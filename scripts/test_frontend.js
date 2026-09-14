#!/usr/bin/env node
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ROOT = path.join(__dirname, "..");
const modal = { innerHTML: "" };
const context = vm.createContext({
  document: {
    addEventListener() {},
    getElementById(id) {
      if (id === "modalBody") return modal;
      if (id === "overlay") return { classList: { add() {}, remove() {} } };
      return null;
    },
  },
  loadNote() {},
  RelationsView: { KIND_LABEL: {} },
});
for (const f of ["structure", "places", "characters", "families", "relations", "themes",
  "arcs", "battles", "routes", "glossary", "names", "chapters", "events"]) {
  vm.runInContext(fs.readFileSync(path.join(ROOT, "data", f + ".js"), "utf8"), context);
}
vm.runInContext(fs.readFileSync(path.join(ROOT, "js", "app.js"), "utf8"), context);
const run = code => vm.runInContext(code, context);
const decodeHTML = text => text.replace(/&(?:#(\d+)|#x([0-9a-f]+)|(amp|quot|apos|lt|gt));/gi,
  (_, decimal, hex, named) => decimal ? String.fromCodePoint(+decimal) :
    hex ? String.fromCodePoint(parseInt(hex, 16)) :
      ({ amp: "&", quot: '"', apos: "'", lt: "<", gt: ">" })[named.toLowerCase()]);
const buttons = () => [...modal.innerHTML.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)]
  .map(([, attrs, body]) => ({
    text: decodeHTML(body.replace(/<[^>]*>/g, "")).trim(),
    click: decodeHTML((attrs.match(/\bonclick="([^"]*)"/) || [])[1] || ""),
  }));
const title = () => decodeHTML((modal.innerHTML.match(/<h2[^>]*>(.*?)<\/h2>/s) || [])[1] || "");
function clickButton(text) {
  const button = buttons().find(b => b.text === text);
  assert.ok(button, `missing visible button: ${text}`);
  assert.ok(button.click, `button has no action: ${text}`);
  run(button.click);
}

// One chapter can lead to multiple events, and every event leads back to all its chapters.
const chapter = run("Object.keys(EVENTS_BY_CHAPTER).find(id => EVENTS_BY_CHAPTER[id].length > 1)");
assert.ok(chapter, "fixture must exercise one chapter with multiple events");
for (const eid of run(`EVENTS_BY_CHAPTER[${JSON.stringify(chapter)}].map(e => e.id)`)) {
  const expectedTitle = run(`EVENT_BY_ID[${JSON.stringify(eid)}].title`);
  run(`showChapter(${JSON.stringify(chapter)})`);
  clickButton(expectedTitle + " →");
  assert.equal(title(), expectedTitle);
}
for (const eid of run("EVENTS.map(e => e.id)")) {
  for (const cid of run(`EVENT_BY_ID[${JSON.stringify(eid)}].ch`)) {
    run(`showEventCard(${JSON.stringify(eid)})`);
    clickButton(cid + " →");
    assert.ok(title().includes(cid), `wrong destination: ${eid}/${cid}`);
  }
}

// Sharing a year and a character must not attach a battle to a salon.
run("showEventCard('e-sherer-saloon')");
assert.ok(!modal.innerHTML.includes("战役阶段"));
run("showEventCard('e-austerlitz')");
assert.ok(modal.innerHTML.includes("战役阶段 · 奥斯特里茨（三皇会战）"));
run("showEventCard('e-andrei-wound')");
assert.ok(modal.innerHTML.includes("战役阶段 · 鲍罗金诺会战"));

// A chapter with an empty original chars list must still expose its reverse-indexed people.
run("showChapter('4-1-03')");
assert.ok(modal.innerHTML.includes("本章人物"));
assert.ok(modal.innerHTML.includes("米肖"));

// The browser decodes HTML entities before compiling an inline JavaScript handler.
const unsafeId = "e-');globalThis.auditInjected=true;//";
run(`globalThis.auditInjected=false;
  EVENT_BY_ID[${JSON.stringify(unsafeId)}]={...EVENTS[0],id:${JSON.stringify(unsafeId)},title:"转义回归事件"};
  EVENTS_BY_CHAPTER[${JSON.stringify(chapter)}].push(EVENT_BY_ID[${JSON.stringify(unsafeId)}]);`);
run(`showChapter(${JSON.stringify(chapter)})`);
clickButton("转义回归事件 →");
assert.equal(run("globalThis.auditInjected"), false, "data executed as JavaScript");
assert.equal(title(), "转义回归事件");
console.log("前端回归通过：多事件导航、全部事件回链、战役归属、反向人物索引");
