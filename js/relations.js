// js/relations.js — 动态关系图谱 + 年代滑块 + 插值布局
//
// 立身之本：拖动年代滑块 1805→1820，图谱按 relations.js 的 phases 重连。
// 布局稳定性：预计算 3 个年代锚点（1805 / 1812 / 1820）各跑一次力导向并缓存坐标，
// 中间年份线性插值 → 确定性、无抖动、可复现。
// 覆盖完整：每个锚点的坐标表都含全部候选节点（所有关系边的两端）；该年尚未登场者
// 给确定性备用坐标 → 只在中间年份出现的人物（如 1807 的巴兹杰耶夫 / 维拉尔斯基）
// 不会落到 [0,0] 与别人重叠。
"use strict";

const RelationsView = (() => {
  const YEAR_MIN = 1805, YEAR_MAX = 1820;
  const ANCHORS = [1805, 1812, 1820];

  const FACTION_COLOR = {
    bezukhov: "#c9a227", rostov: "#b8552e", bolkonsky: "#6e8ca0",
    kuragin: "#8c4a66", druzh: "#7a6f58", russian_army: "#4a6a4a",
    french_army: "#4a5a8c", court: "#9c8f7a", mason: "#6f8f7a", folk: "#8a7f6a",
  };
  const KIND_COLOR = {
    kin: "#c8d2dc", marriage: "#c9a227", courtship: "#e0a05c", affair: "#b8552e",
    friend: "#6f8f7a", salon: "#5d6b7c", enemy: "#8c4a66", service: "#4a6a4a",
    patron: "#9c8f7a", estate: "#7a6f58",
  };
  const KIND_LABEL = {
    kin: "亲", marriage: "婚", courtship: "恋", affair: "私",
    friend: "友", salon: "交", enemy: "敌", service: "军",
    patron: "提", estate: "产",
  };
  const KIND_WIDTH = {
    kin: 2.6, marriage: 3.4, courtship: 2.4, affair: 2.4, friend: 2.6,
    salon: 1.2, enemy: 2.6, service: 1.8, patron: 1.4, estate: 1.6,
  };

  // 全体可能显示的关系节点：所有关系边的两端（去重 + 排序 → 顺序确定）
  const CANDIDATES = (() => {
    const s = new Set();
    RELATIONS.forEach(r => { s.add(r.a); s.add(r.b); });
    return [...s].sort();
  })();

  // 阵营分扇区用的固定顺序（锚点力导向与备用坐标共用，变动会同时改变两处布局）
  const FAM_ORDER = ["bezukhov", "rostov", "bolkonsky", "kuragin", "druzh",
    "russian_army", "french_army", "court", "mason", "folk"];

  let chart = null;
  let year = YEAR_MIN;
  let playing = false;
  let playTimer = null;
  let anchorCache = {};        // { 1805: {id:[x,y]}, ... }：每个候选节点在每个锚点都有条目
  let anchorActive = {};       // { 1805: Set(id) }：该锚点真正在场的节点
  let currentPairs = new Map(); // "a|b" -> relation（当前年代生效）
  let selectedRel = null;

  /* ---------- 关系在某年是否生效 + 当前状态 ---------- */
  function relActiveAt(r, y) {
    if (r.from && y < r.from.y) return false;
    if (r.to && y > r.to.y) return false;
    return true;
  }

  function relStateAt(r, y) {
    let cur = null;
    for (const p of (r.phases || [])) {
      if (p.y <= y) cur = p;
      else break;
    }
    return cur;
  }

  /* ---------- 节点在某年的活跃度 ---------- */
  function charActiveAt(cid, y) {
    const c = charById(cid);
    if (!c) return 0;
    if (c.born && y < c.born) return 0;
    if (c.died && y > c.died) return 0;
    // 用关系 + 出场章节的年份分布估活跃度
    let score = 0;
    RELATIONS.forEach(r => {
      if (r.a !== cid && r.b !== cid) return;
      const st = relStateAt(r, y);
      if (st) score += 1.2;
      if (relActiveAt(r, y)) score += 0.8;
    });
    CHAPTERS.forEach(ch => {
      if (!ch.chars || ch.chars.indexOf(cid) < 0) return;
      if (ch.year && Math.abs(ch.year - y) <= 2) score += 0.7;
    });
    return score;
  }

  /* ---------- 预计算锚点布局 ---------- */
  // 用确定性伪力导向：同一输入 → 同一输出（不依赖 Math.random 的时序）
  function computeAnchor(y) {
    const ids = new Set();
    const edges = [];
    const degree = {};
    RELATIONS.forEach(r => {
      if (!relActiveAt(r, y)) return;
      const st = relStateAt(r, y);
      if (!st) return;
      ids.add(r.a); ids.add(r.b);
      edges.push({ a: r.a, b: r.b, w: r.weight || 1, kind: r.kind });
      degree[r.a] = (degree[r.a] || 0) + (r.weight || 1);
      degree[r.b] = (degree[r.b] || 0) + (r.weight || 1);
    });

    const list = [...ids];
    const n = list.length || 1;
    const pos = {};

    // 初始：按家族分扇区，扇区内按度数降序铺开（高连接者靠内圈）
    list.sort((a, b) => (degree[b] || 0) - (degree[a] || 0) || (a < b ? -1 : 1));
    const famBuckets = {};
    list.forEach(id => {
      const c = charById(id);
      const f = (c && FAM_ORDER.indexOf(c.faction) >= 0) ? c.faction : "court";
      (famBuckets[f] = famBuckets[f] || []).push(id);
    });
    const presentFams = FAM_ORDER.filter(f => famBuckets[f]);
    const sector = (Math.PI * 2) / Math.max(1, presentFams.length);
    presentFams.forEach((f, fi) => {
      const arr = famBuckets[f];
      arr.forEach((id, i) => {
        const a0 = fi * sector - Math.PI / 2;
        const a1 = a0 + sector;
        const ang = arr.length === 1 ? (a0 + a1) / 2
          : a0 + (sector * (i + 0.5)) / arr.length;
        const ring = Math.floor(i / 4);                 // 每环最多 4 个
        const rad = 260 + ring * 130 + (i % 4) * 22;
        pos[id] = [Math.cos(ang) * rad, Math.sin(ang) * rad];
      });
    });

    // 迭代斥力/引力（固定迭代次数 → 确定性）
    const ITER = 240;
    for (let it = 0; it < ITER; it++) {
      const k = 1 - it / ITER;
      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          const A = pos[list[i]], B = pos[list[j]];
          let dx = A[0] - B[0], dy = A[1] - B[1];
          let d2 = dx * dx + dy * dy;
          if (d2 < 100) { dx = (i - j) * 0.9 + 0.4; dy = 0.6; d2 = 100; }
          const rep = (34000 / d2) * k;
          const d = Math.sqrt(d2);
          A[0] += (dx / d) * rep; A[1] += (dy / d) * rep;
          B[0] -= (dx / d) * rep; B[1] -= (dy / d) * rep;
        }
      }
      edges.forEach(e => {
        const A = pos[e.a], B = pos[e.b];
        if (!A || !B) return;
        const dx = B[0] - A[0], dy = B[1] - A[1];
        const d = Math.sqrt(dx * dx + dy * dy) || 1;
        const target = 190 + (5 - (e.w || 1)) * 34;
        const f = ((d - target) / d) * 0.05 * k * (e.w || 1);
        A[0] += dx * f; A[1] += dy * f;
        B[0] -= dx * f; B[1] -= dy * f;
      });
      // 向心 + 轻微正交配平，避免整体偏向一侧
      list.forEach(id => {
        pos[id][0] *= 0.9975; pos[id][1] *= 0.9975;
        pos[id][0] -= pos[id][0] * 0.0025 * (it / ITER);
        pos[id][1] -= pos[id][1] * 0.0025 * (it / ITER);
      });
    }

    // 归一化到固定视口，保证不同年代布局尺度一致、不溢出
    const xs = list.map(id => pos[id][0]);
    const ys = list.map(id => pos[id][1]);
    const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
    const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
    const half = Math.max(1, Math.max(
      Math.max(...xs) - cx, cx - Math.min(...xs),
      Math.max(...ys) - cy, cy - Math.min(...ys)));
    const SCALE = 560 / half;
    list.forEach(id => {
      pos[id] = [(pos[id][0] - cx) * SCALE, (pos[id][1] - cy) * SCALE];
    });

    // 该年未登场的候选节点补确定性备用坐标：锚点坐标表对全体候选节点完整，
    // 中间年份取坐标时才有值可插值，不会落到 [0,0]。
    placeAbsent(pos, ids);
    anchorActive[y] = ids;
    return pos;
  }

  /* ---------- 备用坐标（某锚点尚未登场的候选节点） ---------- */
  // 阵营射线 + 组内序号半径：同阵营半径必不同，异阵营射线必不同 → 坐标必可区分；
  // 再对照在场节点沿射线外推，直到留出 SEAT_CLEARANCE 间隔（确定性循环，无随机）。
  const SEAT_BASE = 640, SEAT_STEP = 52, SEAT_CLEARANCE = 84;

  function factionIndex(id) {
    const c = charById(id);
    const f = (c && FAM_ORDER.indexOf(c.faction) >= 0) ? c.faction : "court";
    return FAM_ORDER.indexOf(f);
  }

  function placeAbsent(pos, present) {
    const taken = Object.keys(pos).map(id => pos[id]);
    const byFam = {};
    CANDIDATES.forEach(id => {
      if (present.has(id)) return;
      const fi = factionIndex(id);
      (byFam[fi] = byFam[fi] || []).push(id);
    });
    Object.keys(byFam).forEach(fi => {
      const ang = fi * (Math.PI * 2 / FAM_ORDER.length) - Math.PI / 2;
      byFam[fi].forEach((id, k) => {
        const r = SEAT_BASE + k * SEAT_STEP;
        let p = [Math.cos(ang) * r, Math.sin(ang) * r];
        for (let g = 0; g < 64; g++) {
          const clear = taken.every(q => {
            const dx = q[0] - p[0], dy = q[1] - p[1];
            return dx * dx + dy * dy >= SEAT_CLEARANCE * SEAT_CLEARANCE;
          });
          if (clear) break;
          const d = Math.hypot(p[0], p[1]) || 1;
          p = [p[0] + (p[0] / d) * SEAT_STEP, p[1] + (p[1] / d) * SEAT_STEP];
        }
        pos[id] = p;
        taken.push(p);
      });
    });
  }

  function ensureAnchors() {
    ANCHORS.forEach(a => { if (!anchorCache[a]) anchorCache[a] = computeAnchor(a); });
  }

  /* ---------- 线性插值取坐标 ---------- */
  // 任一锚点的坐标表都覆盖全部候选节点，因此这里对所有可能显示的节点都有值。
  function posAt(cid, y) {
    let lo = ANCHORS[0], hi = ANCHORS[ANCHORS.length - 1];
    for (let i = 0; i < ANCHORS.length - 1; i++) {
      if (y >= ANCHORS[i] && y <= ANCHORS[i + 1]) { lo = ANCHORS[i]; hi = ANCHORS[i + 1]; break; }
    }
    const A = anchorCache[lo][cid], B = anchorCache[hi][cid];
    const t = hi === lo ? 0 : (y - lo) / (hi - lo);
    const onA = anchorActive[lo].has(cid), onB = anchorActive[hi].has(cid);
    // 两端都在场 → 线性插值；只在其中一端在场 → 取那一端坐标，不外推到备用位。
    if (onA && onB) return [A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t];
    if (onA) return A;
    if (onB) return B;
    // 两个锚点都未登场（如巴兹杰耶夫 / 维拉尔斯基）：在两端备用坐标之间插值
    return [A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t];
  }

  /* ---------- 渲染 ---------- */
  function buildOption() {
    ensureAnchors();
    const nodes = [], links = [], seen = new Set();
    currentPairs.clear();

    RELATIONS.forEach(r => {
      if (!relActiveAt(r, year)) return;
      const st = relStateAt(r, year);
      if (!st) return;                    // 尚无任何 phase → 关系未开始
      currentPairs.set(r.a + "|" + r.b, { rel: r, state: st });
      [r.a, r.b].forEach(x => { if (!seen.has(x)) { seen.add(x); nodes.push(x); } });
      links.push({
        source: r.a, target: r.b,
        lineStyle: {
          color: KIND_COLOR[r.kind] || "#5d6b7c",
          width: KIND_WIDTH[r.kind] || 1.5,
          opacity: 0.30 + (r.weight || 1) * 0.11,
          curveness: r.kind === "marriage" ? 0.06 : 0.16,
        },
      });
    });

    const data = nodes.map(id => {
      const c = charById(id) || { name: id, faction: "court" };
      // 必有坐标：节点都来自 RELATIONS，锚点坐标表覆盖全部候选节点
      const p = posAt(id, year);
      const act = charActiveAt(id, year);
      const scale = act > 12 ? 26 : act > 7 ? 21 : 16;
      return {
        id, name: c.name,
        x: p[0], y: p[1], symbolSize: scale,
        itemStyle: {
          color: FACTION_COLOR[c.faction] || "#9c8f7a",
          borderColor: "#0d1726", borderWidth: 2,
          opacity: 0.55 + Math.min(0.45, act / 16),
        },
        label: {
          // 只给最活跃的节点常显标签（约 18 个），其余靠悬停/邻接高亮查看。
          // 标签带深色底衬，避免被关系边穿过而降低可读性。
          show: act >= 7,
          color: "#eef3f8", fontSize: 11.5, fontFamily: "Songti SC, serif",
          fontWeight: 600,
          position: "bottom", distance: 8,
          padding: [3, 5],
          backgroundColor: "rgba(10,18,30,.92)",
          borderColor: "rgba(201,162,39,.35)",
          borderWidth: 1,
          borderRadius: 3,
          opacity: 1,
        },
        _act: act,
      };
    });

    return {
      backgroundColor: "transparent",
      animation: true, animationDuration: 420, animationEasing: "cubicOut",
      series: [{
        type: "graph", layout: "none", data, links,
        roam: true, draggable: true,
        zoom: 0.62, center: [0, 0],
        labelLayout: { hideOverlap: true, moveOverlap: 'shiftY' },
        emphasis: {
          focus: "adjacency",
          lineStyle: { width: 4, opacity: 1 },
          label: { fontSize: 13, color: "#e0c05c" },
        },
        lineStyle: { color: "#3a4d68" },
      }],
    };
  }

  /* ---------- 侧栏 ---------- */
  function renderPane() {
    const pane = document.getElementById("relPane");
    const rows = [];
    currentPairs.forEach(({ rel, state }) => {
      const A = charById(rel.a), B = charById(rel.b);
      if (!A || !B) return;
      rows.push({ rel, state, A, B });
    });
    rows.sort((x, y2) => (y2.rel.weight || 0) - (x.rel.weight || 0));

    const active = rows.length;
    const linked = new Set();
    rows.forEach(r => { linked.add(r.rel.a); linked.add(r.rel.b); });
    // 这里数的是“当年有关系或邻近章节线索”的人数（多数人物 born/died 为空，
    // 不足以判断在世），所以如实标注，不写成“人尚在世”。
    const threaded = CHARACTERS.filter(c => charActiveAt(c.id, year) > 0).length;

    pane.innerHTML = `
      <h3>此刻的关系 · ${year} 年</h3>
      <div style="font-size:11.5px;color:#8b99a8;line-height:1.9;margin-bottom:12px">
        ${active} 条关系生效 · ${linked.size} 人在场 · ${threaded} 人有当年线索
      </div>
      ${rows.map(({ rel, state, A, B }, i) => `
        <div class="rel-item" data-i="${i}" style="border-left-color:${KIND_COLOR[rel.kind]}">
          <div class="ri-pair">
            <span style="color:#8a7020;font-size:10.5px">${KIND_LABEL[rel.kind] || ""}</span>
            ${A.name} — ${B.name}
          </div>
          <div class="ri-state">${state.state}</div>
          <div class="ri-year">${rel.from ? rel.from.y : "?"}${rel.to ? "–" + rel.to.y : "–至今"} · ${rel.phases ? rel.phases.length : 0} 个阶段</div>
        </div>`).join("")}
      <div id="eventLog">
        <h3>关系大事记 · ${year} 年</h3>
        ${renderLog()}
      </div>`;

    pane.querySelectorAll(".rel-item").forEach(el => {
      el.onclick = () => {
        const r = rows[+el.dataset.i];
        if (r) showRelationDetail(r.rel);
      };
    });
  }

  function renderLog() {
    const items = [];
    RELATIONS.forEach(r => {
      (r.phases || []).forEach(p => {
        if (p.y === year) {
          const A = charById(r.a), B = charById(r.b);
          if (A && B) items.push({ A, B, p, kind: r.kind });
        }
      });
    });
    if (!items.length) {
      return `<div style="font-size:12px;color:#5d6b7c;padding:6px 0">这一年没有关系发生转折。</div>`;
    }
    return items.map(it => `
      <div class="log-item">
        <span class="li-y">${it.p.y}${it.p.m ? "." + it.p.m : ""}</span>
        <b style="color:#c8d2dc">${it.A.name} — ${it.B.name}</b>
        <span style="color:#8b99a8">：${it.p.state}</span>
      </div>`).join("");
  }

  function showRelationDetail(r) {
    const A = charById(r.a), B = charById(r.b);
    const kindLabel = {
      kin: "血缘 / 家庭", marriage: "夫妻", courtship: "恋爱 / 婚约", affair: "私情",
      friend: "挚友", salon: "社交", enemy: "敌对", service: "军中共事",
      patron: "提携 / 依附", estate: "经济 / 继承",
    }[r.kind] || r.kind;

    openModal(`
      <h2>${A.name} — ${B.name}</h2>
      <p><b>关系性质：</b>${kindLabel}　<b>跨度：</b>${r.from ? r.from.y : "?"}${r.to ? "–" + r.to.y : "–至今"}</p>
      <div class="detail-section">
        <h4>关系变迁</h4>
        <ul>
          ${(r.phases || []).map(p => {
            const ev = p.ev ? EVENTS.find(e => e.id === p.ev) : null;
            const cls = p.y <= year ? "color:#c8d2dc" : "color:#5d6b7c";
            return `<li style="${cls}">
              <b>${p.y}${p.m ? "." + p.m : ""}</b>　${p.state}
              ${ev ? `<div style="font-size:11.5px;color:#8a7020;margin-top:3px">
                <span style="cursor:pointer;border-bottom:1px dotted #8a7020"
                  onclick="showEventCard('${ev.id}')">→ ${esc(ev.title)}</span></div>` : ""}
            </li>`;
          }).join("")}
        </ul>
      </div>
      <div class="modal-actions">
        <button class="btn-ghost" onclick="closeModal()">关闭</button>
      </div>`);
  }

  /* ---------- 交互 ---------- */
  function setYear(y, opts) {
    year = Math.max(YEAR_MIN, Math.min(YEAR_MAX, y));
    const disp = document.getElementById("yearDisplay");
    if (disp) disp.textContent = year + " 年";
    const sl = document.getElementById("yearSlider");
    if (sl && +sl.value !== year) sl.value = year;
    if (chart) chart.setOption(buildOption(), { replaceMerge: ["series"] });
    renderPane();
    if (opts && opts.callback) opts.callback(year);
  }

  function togglePlay() {
    playing = !playing;
    const btn = document.getElementById("playBtn");
    if (btn) btn.textContent = playing ? "⏸ 暂停" : "▶ 播放";
    if (playing) {
      if (year >= YEAR_MAX) setYear(YEAR_MIN);
      playTimer = setInterval(() => {
        if (year >= YEAR_MAX) { togglePlay(); return; }
        setYear(year + 1);
      }, 1100);
    } else {
      clearInterval(playTimer); playTimer = null;
    }
  }

  function init() {
    const el = document.getElementById("graph");
    if (!el || typeof echarts === "undefined") return;
    chart = echarts.init(el, null, { renderer: "canvas" });
    setYear(YEAR_MIN);

    const sl = document.getElementById("yearSlider");
    sl.min = YEAR_MIN; sl.max = YEAR_MAX; sl.value = year; sl.step = 1;
    sl.oninput = () => setYear(+sl.value);
    document.getElementById("playBtn").onclick = togglePlay;

    chart.on("click", p => {
      if (p.dataType === "node") {
        const c = charById(p.data.id);
        if (c) showCharacterCard(c.id);
      }
    });
    window.addEventListener("resize", () => chart && chart.resize());
  }

  function resize() { if (chart) chart.resize(); }

  return { init, setYear, resize, getYear: () => year, KIND_LABEL, KIND_COLOR, FACTION_COLOR, relActiveAt, relStateAt };
})();
