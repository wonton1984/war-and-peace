// js/family.js — 四大家族谱系树（SVG）
"use strict";

const FamilyView = (() => {
  let inited = false;

  function render() {
    const host = document.getElementById("viewFamily");
    if (!host) return;
    host.innerHTML = `
      <div style="max-width:1400px;margin:0 auto">
        <div style="margin-bottom:16px">
          <h2 style="font-family:var(--serif);font-size:19px;color:#e0c05c;letter-spacing:3px">四大家族</h2>
          <p style="font-size:12.5px;color:#8b99a8;line-height:1.9;margin-top:6px">
            库拉金、罗斯托夫、保尔康斯基、别祖霍夫四家是全书的情节骨架。
            节点按世代排列，<span style="color:#8a7020">虚线</span>表示跨家族的联姻。点击任一人物打开人物卡。
          </p>
        </div>
        <div class="fam-grid">
          ${FAMILIES.map(f => famCard(f)).join("")}
        </div>
      </div>`;
    host.querySelectorAll(".tree-node").forEach(el => {
      el.onclick = () => showCharacterCard(el.dataset.id);
    });
    inited = true;
  }

  function famCard(f) {
    const gens = {};
    f.tree.forEach(t => { (gens[t.gen] = gens[t.gen] || []).push(t); });
    const genKeys = Object.keys(gens).map(Number).sort((a, b) => a - b);
    const genName = ["父辈", "子辈", "孙辈"];

    return `
      <div class="fam-card" style="border-color:${f.color}40">
        <h3 style="color:${f.color}">${esc(f.name)}</h3>
        <div class="fam-desc">${esc(f.desc)}</div>
        <div class="fam-tree">
          ${genKeys.map(g => `
            <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:10px">
              <span class="gen-label">${genName[g] || "第" + (g + 1) + "代"}</span>
              <div class="tree-gen">
                ${gens[g].map(t => {
                  const c = charById(t.id);
                  if (!c) return "";
                  const married = t.of !== f.id;
                  return `<div class="tree-node" data-id="${t.id}"
                    style="${married ? "border-style:dashed;border-color:" + factionColor(t.of) : ""};border-left:3px solid ${factionColor(c.faction)}">
                    ${esc(c.name)}
                    ${t.note ? `<span class="tn-note">${esc(t.note)}</span>` : ""}
                  </div>`;
                }).join("")}
              </div>
            </div>`).join("")}
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px dashed #24395c">
          <div style="font-size:11px;color:#8a7020;letter-spacing:1px;margin-bottom:6px">联姻</div>
          ${f.marriages.map(m => `<div style="font-size:12px;color:#8b99a8;line-height:1.85">· ${esc(m)}</div>`).join("")}
        </div>
      </div>`;
  }

  function init() { render(); }
  return { init, render };
})();
