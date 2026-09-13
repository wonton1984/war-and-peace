// js/app.js — 主控 / 路由 / 章节卡 / 事件卡 / 搜索 / 人物卡
"use strict";

/* ============ 索引 ============ */
const CHAR_BY_ID = {};
CHARACTERS.forEach(c => { CHAR_BY_ID[c.id] = c; });
const EVENT_BY_ID = {};
EVENTS.forEach(e => { EVENT_BY_ID[e.id] = e; });
const EVENTS_BY_CHAPTER = {};
EVENTS.forEach(e => (e.ch || []).forEach(cid => {
  (EVENTS_BY_CHAPTER[cid] = EVENTS_BY_CHAPTER[cid] || []).push(e);
}));
const CHAPTER_BY_ID = {};
CHAPTERS.forEach(c => { CHAPTER_BY_ID[c.id] = c; });
const THEME_BY_ID = {};
THEMES.forEach(t => { THEME_BY_ID[t.id] = t; });

// 章 -> 人物 的反向索引。
// chapters.chars 只收录详录人物，不能单独用于判断本章全部人物。
// 这里把 characters[].chapters（由语料抽取，详录简录都有）反过来并进索引，
// 使「按人物筛选/搜索」对简录同样生效，且无需在 chapters.js 里重复存储。
const CHAR_BY_CHAPTER = {};
CHAPTERS.forEach(c => { CHAR_BY_CHAPTER[c.id] = new Set(c.chars || []); });
CHARACTERS.forEach(c => (c.chapters || []).forEach(cid => {
  if (CHAR_BY_CHAPTER[cid]) CHAR_BY_CHAPTER[cid].add(c.id);
}));
function charsInChapter(cid) {
  return [...(CHAR_BY_CHAPTER[cid] || new Set())];
}

function charById(id) { return CHAR_BY_ID[id]; }
function charName(id) { const c = CHAR_BY_ID[id]; return c ? c.name : id; }
function factionColor(f) {
  return {
    bezukhov: "#c9a227", rostov: "#b8552e", bolkonsky: "#6e8ca0",
    kuragin: "#8c4a66", druzh: "#7a6f58", russian_army: "#4a6a4a",
    french_army: "#4a5a8c", court: "#9c8f7a", mason: "#6f8f7a", folk: "#8a7f6a",
  }[f] || "#9c8f7a";
}
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ============ 视图路由 ============ */
let currentView = "relations";
function switchView(v) {
  currentView = v;
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t.dataset.view === v));
  document.querySelectorAll(".view").forEach(p => p.classList.toggle("active", p.id === "view" + v[0].toUpperCase() + v.slice(1)));
  document.getElementById("timebar").classList.toggle("hidden", v !== "relations");
  // 注意：这些是顶层 const，不会挂到 window 上，不能用 window.X 判存在。
  // 地图/家族按需初始化：地图容器在视图显示前尺寸为 0，必须先显示再 init。
  if (v === "relations") RelationsView.resize();
  if (v === "map") { MapView.init(); MapView.resize(); }
  if (v === "family") FamilyView.render();
  if (v === "read") renderChapterList();
}

/* ============ 弹层 ============ */
function openModal(html) {
  document.getElementById("modalBody").innerHTML = html;
  document.getElementById("overlay").classList.add("show");
}
function closeModal() { document.getElementById("overlay").classList.remove("show"); }

/* ============ 人物卡 ============ */
function showCharacterCard(cid) {
  const c = charById(cid);
  if (!c) return;
  const rels = RELATIONS.filter(r => r.a === cid || r.b === cid);
  const evs = EVENTS.filter(e => (e.chars || []).indexOf(cid) >= 0);
  const arc = ARCS.find(a => a.who === cid);
  const color = factionColor(c.faction);
  const chs = c.chapters || [];

  openModal(`
    <div class="pc-head">
      <div class="pc-badge" style="background:${color}">${esc(c.name[0])}</div>
      <div>
        <div class="pc-name">${esc(c.name)}</div>
        ${c.full ? `<div class="pc-full">${esc(c.full)}</div>` : ""}
        ${c.title ? `<div class="pc-title">${esc(c.title)}</div>` : ""}
        <div style="margin-top:6px">
          ${c.tier === "minor" ? '<span class="pill">简录</span>' : '<span class="pill char">详录</span>'}
          ${c.flag === "verify" ? '<span class="pill verify">待核</span>' : ""}
          ${c.flag === "mentioned" ? '<span class="pill">仅被提及，未正面出场</span>' : ""}
          ${c.flag === "indexPend" ? '<span class="pill">索引待扩</span>' : ""}
          ${c.flag !== "mentioned" && !(c.chapters || []).length ? '<span class="pill">未正面出场</span>' : ""}
        </div>
      </div>
    </div>
    ${c.born || c.died ? `<p style="font-size:12px;color:#8a7020;margin-bottom:10px">
      ${c.born ? c.born : "?"} — ${c.died ? c.died : "?"}</p>` : ""}
    ${c.bio ? `<div class="detail-section"><h4>小传</h4><p>${esc(c.bio)}</p></div>`
      : '<div class="detail-section"><h4>小传</h4><p style="color:#5d6b7c">（简录，暂无小传）</p></div>'}
    ${c.tier === "minor" ? '<p style="font-size:11.5px;color:#8a7020">简录人物：仅收录身份定位与出场章节索引，未建关系边。</p>' : ""}
    ${c.arc ? `<div class="detail-section"><h4>弧光</h4><p>${esc(c.arc)}</p></div>` : ""}
    ${arc ? `<div class="detail-section"><h4>阶段</h4><ul>
      ${arc.stages.map(s => `<li><b>${esc(s.label)}</b>　<span style="color:#8a7020">${s.from}–${s.to}</span>
        <div style="font-size:11.5px;margin-top:3px">${esc(s.desc)}</div></li>`).join("")}
    </ul></div>` : ""}
    ${rels.length ? `<div class="detail-section"><h4>关系（${rels.length}）</h4>
      ${rels.map(r => {
        const other = r.a === cid ? r.b : r.a;
        const st = (r.phases || [])[0];
        return `<span class="rel-chip" onclick="showRelationFrom('${r.a}','${r.b}')">
          <span class="rc-kind">${(RelationsView.KIND_LABEL[r.kind] || "")}</span>${esc(charName(other))}
          <span style="color:#5d6b7c;font-size:10.5px">　${st ? r.from.y + "起" : ""}</span>
        </span>`;
      }).join("")}
    </div>` : ""}
    ${evs.length ? `<div class="detail-section"><h4>关联事件（${evs.length}）</h4><ul>
      ${evs.map(e => `<li><button class="btn-ghost" onclick="showEventCard('${e.id}')">${esc(e.title)} →</button>
        <span style="color:#8a7020;font-size:11px">　${e.year || ""}</span>
        <div style="font-size:11.5px;margin-top:3px">${esc(e.summary)}</div></li>`).join("")}
    </ul></div>` : ""}
    <div class="detail-section"><h4>出场（${chs.length} 章）</h4>
      <div style="font-size:11.5px;color:#8b99a8;line-height:1.9">
        ${chs.map(id => `<button class="btn-ghost" onclick="showChapter('${id}')">${esc(id)}</button>`).join(" ")}
      </div>
    </div>
    <div class="notes">
      <h4>拆书笔记 · ${esc(c.name)}</h4>
      <textarea id="noteArea" placeholder="记下你的想法…（自动保存在本机浏览器）"></textarea>
      <div class="note-status" id="noteStatus"></div>
      <div class="note-actions">
        <button class="btn-gold" onclick="saveNote('char:${cid}')">保存笔记</button>
        <button class="btn-ghost" onclick="exportNotes()">导出全部</button>
      </div>
    </div>
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
  loadNote('char:' + cid);
}

function showRelationFrom(a, b) {
  closeModal();
  switchView("relations");
  const r = RELATIONS.find(x => (x.a === a && x.b === b) || (x.a === b && x.b === a));
  if (r) RelationsView.setYear(r.from ? r.from.y : 1805);
}

/* ============ 事件卡 ============ */
function showEventCard(eid) {
  const e = EVENT_BY_ID[eid];
  if (!e) return;
  const battle = e.battle ? BATTLES.find(b => b.id === e.battle) : null;
  const linked = (e.ch || []).map(cid => CHAPTER_BY_ID[cid]).filter(Boolean);

  openModal(`
    <h2>${esc(e.title)}</h2>
    <p style="font-size:12px;color:#8a7020">
      ${e.year ? e.year + " 年" + (e.month ? " " + e.month + " 月" : "") + (e.day ? " " + e.day + " 日" : "") : "时间未定"}
      ${e.place ? "　·　" + esc(e.place) : ""}
      　·　${esc(e.type)}
      　·　${(e.ch || []).join(", ")}
    </p>
    <div class="detail-section"><h4>概述</h4><p>${esc(e.summary)}</p></div>

    ${(e.chars || []).length ? `<div class="detail-section"><h4>出场人物</h4>
      ${e.chars.map(c => `<span class="rel-chip" onclick="closeModal();showCharacterCard('${c}')">
        <span style="color:${factionColor((charById(c) || {}).faction)}">●</span> ${esc(charName(c))}</span>`).join("")}
    </div>` : ""}

    ${(e.rel || []).length ? `<div class="detail-section"><h4>关系变动</h4><ul>
      ${e.rel.map(r => `<li><b>${esc(charName(r.a))} — ${esc(charName(r.b))}</b>
        <span style="color:#8a7020;font-size:11px">　${esc(r.kind)}</span>
        <div style="font-size:11.5px;margin-top:3px">${esc(r.delta)}</div></li>`).join("")}
    </ul></div>` : ""}

    ${(e.theme || []).length ? `<div class="detail-section"><h4>主题线</h4>
      ${e.theme.map(t => {
        const th = THEME_BY_ID[t];
        return th ? `<span class="rel-chip" onclick="showTheme('${t}')">${esc(th.title)}</span>` : "";
      }).join("")}
    </div>` : ""}

    ${(e.arc || []).length ? `<div class="detail-section"><h4>人物阶段</h4><ul>
      ${e.arc.map(a => `<li><b>${esc(charName(a.who))}</b>　<span style="color:#8a7020">${esc(a.stage)}</span></li>`).join("")}
    </ul></div>` : ""}

    ${battle ? `<div class="detail-section"><h4>战役阶段 · ${esc(battle.name)}</h4><ul>
      ${battle.phase.map(p => `<li><b>${esc(p.name)}</b>
        <div style="font-size:11.5px;margin-top:3px">${esc(p.desc)}</div></li>`).join("")}
    </ul></div>` : ""}

    ${e.history ? `<div class="detail-section"><h4>小说 × 史实</h4><p>${esc(e.history)}</p></div>` : ""}

    ${linked.length ? `<div class="detail-section"><h4>对应章节</h4><ul>
      ${linked.map(c => `<li><button class="btn-ghost" onclick="showChapter('${c.id}')">${esc(c.id)} →</button>　<span style="color:#8b99a8">${esc(c.gist || "")}</span></li>`).join("")}
    </ul></div>` : ""}

    <div class="notes">
      <h4>拆书笔记 · ${esc(e.title)}</h4>
      <textarea id="noteArea" placeholder="记下你的想法…（自动保存在本机浏览器）"></textarea>
      <div class="note-status" id="noteStatus"></div>
      <div class="note-actions">
        <button class="btn-gold" onclick="saveNote('event:${eid}')">保存笔记</button>
        <button class="btn-ghost" onclick="exportNotes()">导出全部</button>
      </div>
    </div>
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
  loadNote('event:' + eid);
}

function showTheme(tid) {
  const t = THEME_BY_ID[tid];
  if (!t) return;
  const roleColor = { 提出: "#c9a227", 推进: "#6f8f7a", 解答: "#b8552e" };
  openModal(`
    <h2>${esc(t.title)}</h2>
    <p style="color:#8b99a8">${esc(t.question)}</p>
    <div class="detail-section"><h4>线索</h4><ul>
      ${t.nodes.map(n => {
        const ch = CHAPTER_BY_ID[n.ch];
        return `<li style="cursor:pointer" onclick="closeModal();showChapter('${n.ch}')">
          <b style="color:${roleColor[n.role] || "#c8d2dc"}">${esc(n.role)}</b>
          <span style="color:#8a7020;font-size:11px">　${n.ch}</span>
          <div style="font-size:11.5px;margin-top:3px">${esc(n.note || (ch ? ch.gist : ""))}</div>
        </li>`;
      }).join("")}
    </ul></div>
    <p style="font-size:12px;color:#8a7020">状态：${esc(t.status === "answered" ? "书中已作答" : t.status === "partial" ? "部分作答" : "开放")}</p>
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
}

/* ============ 章节卡 ============ */
function showChapter(cid) {
  const c = CHAPTER_BY_ID[cid];
  if (!c) return;
  const events = EVENTS_BY_CHAPTER[cid] || [];
  const characters = charsInChapter(cid);
  const anchoredHere = p => events.some(e => e.id === p.ev);
  const relHere = RELATIONS.filter(r => (r.phases || []).some(anchoredHere));

  openModal(`
    <h2>${cid}</h2>
    <p style="font-size:12px;color:#8a7020">
      ${c.book === 5 ? "尾声" : "第 " + c.book + " 卷"} · 第 ${c.part} 部 · 第 ${c.ch} 章
      　·　全书第 ${c.seq} 章
      ${c.year ? "　·　" + c.year + (c.month ? " 年 " + c.month + " 月" : " 年") : ""}
      ${c.place ? "　·　" + esc(c.place) : ""}
    </p>
    <div class="detail-section"><h4>概述</h4>
      <p>${c.gist ? esc(c.gist) : '<span style="color:#b8552e">概述待补（flag: verify）</span>'}</p></div>
    ${characters.length ? `<div class="detail-section"><h4>本章人物</h4>
      ${characters.map(x => `<span class="rel-chip" onclick="closeModal();showCharacterCard('${x}')">
        <span style="color:${factionColor((charById(x) || {}).faction)}">●</span> ${esc(charName(x))}</span>`).join("")}
    </div>` : ""}
    ${relHere.length ? `<div class="detail-section"><h4>本章的关系变动</h4><ul>
      ${relHere.map(r => {
        const p = r.phases.find(anchoredHere);
        return `<li><b>${esc(charName(r.a))} — ${esc(charName(r.b))}</b>
          <div style="font-size:11.5px;margin-top:3px">${esc(p.state)}</div></li>`;
      }).join("")}
    </ul></div>` : ""}
    ${events.length ? `<div class="detail-section"><h4>关联事件（${events.length}）</h4>
      ${events.map(e => `<p><button class="btn-ghost" onclick="showEventCard('${e.id}')">${esc(e.title)} →</button></p>`).join("")}</div>` : ""}
    <div class="notes">
      <h4>拆书笔记 · ${cid}</h4>
      <textarea id="noteArea" placeholder="记下你的想法…"></textarea>
      <div class="note-status" id="noteStatus"></div>
      <div class="note-actions">
        <button class="btn-gold" onclick="saveNote('ch:${cid}')">保存笔记</button>
        <button class="btn-ghost" onclick="exportNotes()">导出全部</button>
      </div>
    </div>
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
  loadNote('ch:' + cid);
}

/* ============ 阅读视图 ============ */
let readFilter = { book: "", tag: "", char: "", q: "" };

function renderChapterList() {
  const list = document.getElementById("chapterList");
  if (!list) return;
  let rows = CHAPTERS.slice();

  if (readFilter.book) {
    const [b, p] = readFilter.book.split("-");
    rows = rows.filter(c => c.book === +b && (!p || c.part === +p));
  }
  if (readFilter.tag) rows = rows.filter(c => c.tag === readFilter.tag);
  if (readFilter.char) rows = rows.filter(c => charsInChapter(c.id).indexOf(readFilter.char) >= 0);
  if (readFilter.q) {
    const q = readFilter.q.toLowerCase();
    const hitChars = new Set(CHARACTERS.filter(c =>
      c.name.toLowerCase().includes(q) || (c.full || "").toLowerCase().includes(q) ||
      (c.aliases || []).some(a => a.toLowerCase().includes(q))).map(c => c.id));
    rows = rows.filter(c =>
      (c.gist || "").toLowerCase().includes(q) ||
      c.id.includes(q) ||
      (c.place || "").toLowerCase().includes(q) ||
      charsInChapter(c.id).some(x => hitChars.has(x)) ||
      (EVENTS_BY_CHAPTER[c.id] || []).some(e =>
        e.title.toLowerCase().includes(q) || (e.summary || "").toLowerCase().includes(q)));
  }

  const cnt = document.getElementById("chapterCount");
  if (cnt) cnt.textContent = `${rows.length} / ${CHAPTERS.length} 章`;

  const tagLabel = { peace: "和", war: "战", essay: "论", transition: "过" };
  list.innerHTML = rows.map(c => `
    <div class="ch-card ${(EVENTS_BY_CHAPTER[c.id] || []).length ? "is-event" : ""}" data-id="${c.id}">
      <div class="cc-head">
        <span class="cc-id">${c.id}</span>
        <span class="cc-title">${c.book === 5 ? "尾声" : "第" + c.book + "卷"}·${c.part}部·${c.ch}章</span>
        ${c.tag ? `<span class="pill ${c.tag}">${tagLabel[c.tag] || c.tag}</span>` : ""}
        ${c.flag === "verify" ? `<span class="pill verify">待核</span>` : ""}
      </div>
      <div class="cc-gist">${c.gist ? esc(c.gist) : '<span style="color:#b8552e">概述待补</span>'}</div>
      <div class="cc-meta">
        ${c.year ? `<span class="pill">${c.year}${c.month ? "." + c.month : ""}</span>` : ""}
        ${c.place ? `<span class="pill">${esc(c.place)}</span>` : ""}
        ${charsInChapter(c.id).slice(0, 8).map(x =>
          `<span class="pill char"><span style="color:${factionColor((charById(x) || {}).faction)}">●</span> ${esc(charName(x))}${(charById(x) || {}).tier === "minor" ? '<span style="opacity:.6;font-size:9px">简</span>' : ""}</span>`).join("")}
        ${charsInChapter(c.id).length > 8 ? `<span class="pill">+${charsInChapter(c.id).length - 8}</span>` : ""}
      </div>
    </div>`).join("");

  list.querySelectorAll(".ch-card").forEach(el => {
    el.onclick = () => showChapter(el.dataset.id);
  });
}

function initReadToolbar() {
  const selBook = document.getElementById("filterBook");
  selBook.innerHTML = `<option value="">全部卷部</option>` +
    STRUCTURE.map(b => `<optgroup label="${b.title}">` +
      b.parts.map(p => {
        const key = b.book + "-" + p.part;
        return `<option value="${key}">${PART_TITLES[key] || (b.title + " 第" + p.part + "部")}（${p.chapters}章）</option>`;
      }).join("") + `</optgroup>`).join("");

  const selChar = document.getElementById("filterChar");
  const named = CHARACTERS.filter(c => (c.chapters || []).length > 0)
    .sort((a, b) => (b.chapters || []).length - (a.chapters || []).length);
  selChar.innerHTML = `<option value="">全部人物</option>` +
    named.map(c => `<option value="${c.id}">${esc(c.name)}（${c.chapters.length}章）</option>`).join("");

  selBook.onchange = () => { readFilter.book = selBook.value; renderChapterList(); };
  selChar.onchange = () => { readFilter.char = selChar.value; renderChapterList(); };
  document.getElementById("filterTag").onchange = e => { readFilter.tag = e.target.value; renderChapterList(); };
  document.getElementById("filterQ").oninput = e => { readFilter.q = e.target.value.trim(); renderChapterList(); };
}

/* ============ 全局搜索 ============ */
function globalSearch(q) {
  q = (q || "").trim();
  if (!q) return;
  switchView("read");
  document.getElementById("filterQ").value = q;
  readFilter.q = q;
  renderChapterList();
}

/* ============ 引导 ============ */
const GUIDE_STEPS = [
  { t: "关系随时间变化", d: "这是本站的核心。底部<b>年代滑块</b>从 1805 拖到 1820，图谱会按当年的关系实时重连——安德烈与娜塔莎之间会依次经历初见、重逢、订婚、悔婚、和解死别。" },
  { t: "读「此刻的关系」", d: "右侧面板列出当前年份生效的每条关系与它的<b>状态</b>。点开任一条，可以看到这段关系的完整变迁时间表。" },
  { t: "四种视图", d: "<b>关系</b>是主视图；<b>家族</b>看四大家族谱系与联姻；<b>地图</b>看 1805/1812 的行军与撤退；<b>阅读</b>是全书 361 章的拆解卡片，可按卷部、人物、类型筛选。" },
  { t: "人物志与主题线", d: "顶栏的<b>人物志</b>按家族/阵营列出全部人物（详录 + 简录）；<b>主题线</b>把托尔斯泰的议论按「历史由谁推动」「自由与必然」等六个问题归拢。" },
  { t: "记下你的想法", d: "任何一张卡片底下都有<b>拆书笔记</b>，自动存在本机浏览器，支持导出 Markdown 与 JSON。点人物名可以顺着关系一路走下去。" },
];
let guideStep = 0;
function showGuide(step) {
  guideStep = Math.max(0, Math.min(GUIDE_STEPS.length - 1, step));
  const s = GUIDE_STEPS[guideStep];
  document.getElementById("guideBody").innerHTML = `
    <h2>${s.t}</h2>
    <p><span class="gd-step">${guideStep + 1}/${GUIDE_STEPS.length}</span>${s.d}</p>
    <div class="gd-dots">${GUIDE_STEPS.map((_, i) => `<span class="gd-dot ${i === guideStep ? "on" : ""}"></span>`).join("")}</div>
    <div class="guide-actions">
      ${guideStep > 0 ? `<button class="btn-ghost" onclick="showGuide(${guideStep - 1})">上一步</button>` : ""}
      ${guideStep < GUIDE_STEPS.length - 1
        ? `<button class="btn-gold" onclick="showGuide(${guideStep + 1})">下一步</button>`
        : `<button class="btn-gold" onclick="closeGuide()">开始重演</button>`}
      <button class="btn-ghost" onclick="closeGuide()">跳过</button>
    </div>`;
  document.getElementById("guide").classList.add("show");
}
function closeGuide() {
  document.getElementById("guide").classList.remove("show");
  try { localStorage.setItem("wp_guide_done", "1"); } catch (e) {}
}

/* ============ 启动 ============ */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab").forEach(t => {
    t.onclick = () => switchView(t.dataset.view);
  });
  document.getElementById("overlay").onclick = e => {
    if (e.target.id === "overlay") closeModal();
  };
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { closeModal(); closeGuide(); }
    if (e.key === "/" && document.activeElement.tagName !== "INPUT" &&
        document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault(); document.getElementById("searchBox").focus();
    }
  });
  document.getElementById("searchBox").onkeydown = e => {
    if (e.key === "Enter") globalSearch(e.target.value);
  };
  document.getElementById("btnGuide").onclick = () => showGuide(0);
  document.getElementById("btnThemes").onclick = showThemesIndex;
  document.getElementById("btnChars").onclick = showCharacterIndex;
  document.getElementById("btnBackground").onclick = showBackground;

  initReadToolbar();
  RelationsView.init();
  switchView("relations");

  // 分享链接：#ch-2-3-14 / #e-austerlitz / #rel-a-b
  const h = location.hash;
  if (h.startsWith("#ch-")) {
    switchView("read");
    const id = h.slice(4);
    if (CHAPTER_BY_ID[id]) setTimeout(() => showChapter(id), 200);
  } else if (h.startsWith("#e-")) {
    const id = h.slice(1);
    if (EVENT_BY_ID[id]) setTimeout(() => showEventCard(id), 200);
  } else if (h.startsWith("#y")) {
    RelationsView.setYear(+h.slice(2) || 1812);
  }

  let done = false;
  try { done = localStorage.getItem("wp_guide_done") === "1"; } catch (e) {}
  if (!done) setTimeout(() => showGuide(0), 500);
});

/* ============ 人物志索引 ============ */
const FACTION_LABEL = {
  bezukhov: "别祖霍夫家", rostov: "罗斯托夫家", bolkonsky: "保尔康斯基家",
  kuragin: "库拉金家", druzh: "德鲁别茨科伊家", russian_army: "俄军",
  french_army: "法军", court: "宫廷", mason: "共济会", folk: "平民 / 仆役",
};

function showCharacterIndex() {
  const byFac = {};
  CHARACTERS.forEach(c => (byFac[c.faction] = byFac[c.faction] || []).push(c));
  const order = ["bezukhov", "rostov", "bolkonsky", "kuragin", "druzh",
    "russian_army", "french_army", "court", "mason", "folk"];
  const core = CHARACTERS.filter(c => c.tier === "core").length;
  const minor = CHARACTERS.length - core;

  openModal(`
    <h2>人物志</h2>
    <p style="color:#8b99a8">共 <b>${CHARACTERS.length}</b> 位：详录 <b>${core}</b> 位（有关系边与弧光），
       简录 <b>${minor}</b> 位。点任一条打开人物卡。</p>
    ${order.filter(f => byFac[f]).map(f => `
      <div class="detail-section">
        <h4><span style="color:${factionColor(f)}">●</span> ${esc(FACTION_LABEL[f])}（${byFac[f].length}）</h4>
        <div>
          ${byFac[f].sort((a, b) => (b.chapters || []).length - (a.chapters || []).length)
            .map(c => `<span class="rel-chip" onclick="closeModal();showCharacterCard('${c.id}')">
              ${esc(c.name)}${c.tier === "core" ? "" : '<span style="color:#5d6b7c;font-size:10px">·简</span>'}
              <span style="color:#5d6b7c;font-size:10px">　${(c.chapters || []).length}章</span>
            </span>`).join("")}
        </div>
      </div>`).join("")}
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
}

/* ============ 主题索引 ============ */
function showThemesIndex() {
  openModal(`
    <h2>主题线</h2>
    <p style="color:#8b99a8">托尔斯泰的议论不按情节走，而按问题走。六条线各自贯穿全书。</p>
    <div class="detail-section"><ul>
      ${THEMES.map(t => `<li style="cursor:pointer" onclick="showTheme('${t.id}')">
        <b style="color:${t.color}">${esc(t.title)}</b>
        <span style="color:#8a7020;font-size:11px">　${t.nodes.length} 个节点</span>
        <div style="font-size:11.5px;margin-top:3px">${esc(t.question)}</div>
      </li>`).join("")}
    </ul></div>
    <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
}

/* ============ 时代背景 ============ */
function showBackground() {
  openModal(`
    <article class="era-background" aria-labelledby="eraTitle">
      <div class="era-heading">
        <h2 id="eraTitle" tabindex="-1">时代背景</h2>
        <button class="btn-ghost" onclick="closeModal()" aria-label="关闭时代背景">关闭</button>
      </div>
      <p class="era-period">${esc(ERA_BACKGROUND.period)}</p>
      <p>${esc(ERA_BACKGROUND.intro)}</p>
      <p class="era-reading">${esc(ERA_BACKGROUND.framing)}</p>
      <section class="detail-section era-topics">
        <h3>五个阅读前的小问题 · 点击展开</h3>
        ${ERA_BACKGROUND.topics.map((t, i) => `
          <details${i === 0 ? " open" : ""}>
            <summary>${esc(t.title)}</summary>
            <p>${esc(t.text)}</p>
            <p class="era-reading"><b>阅读提示：</b>${esc(t.reading)}</p>
          </details>`).join("")}
      </section>
      <section class="detail-section">
        <h3>一条简短年表</h3>
        <p>点击年份，可回到关系图查看这一年的小说人物关系。</p>
        <ul class="era-years">
          ${ERA_BACKGROUND.timeline.map(t => `<li>
            <button class="btn-ghost" aria-label="查看${t.year}年人物关系"
              onclick="closeModal();switchView('relations');RelationsView.setYear(${t.year})">${t.year}</button>
            <b>${esc(t.title)}</b>
            <p>${esc(t.text)}</p>
          </li>`).join("")}
        </ul>
      </section>
      <section class="detail-section">
        <h3>小说的视角，不是历史定论</h3>
        <p>${esc(ERA_BACKGROUND.perspective)}</p>
      </section>
      <details class="detail-section">
        <summary>资料来源 · 外部页面可能包含剧透</summary>
        <ul class="era-sources">
          ${ERA_BACKGROUND.sources.map(s => `<li><a href="${esc(s.url)}"
            target="_blank" rel="noopener noreferrer">${esc(s.title)}</a></li>`).join("")}
        </ul>
      </details>
      <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>
    </article>`);
  document.getElementById("modalBody").scrollTop = 0;
  document.getElementById("eraTitle").focus();
}
