// js/map.js — 战局地图 + 路线动画 + 人物行踪
"use strict";

const MapView = (() => {
  let map = null;
  let layers = {};
  let routeLines = {}, routeMarkers = {};
  let animTimer = null;
  let playIdx = 0;
  let playGhost = null;        // 播放中的移动标记，stopPlay 必须回收

  const CAMP = {
    russian: "#4a6a4a", french: "#4a5a8c",
    battlefield: "#8c4a66", estate: "#c9a227", city: "#8b99a8", other: "#5d6b7c",
  };

  function init() {
    if (typeof L === "undefined") return;
    const el = document.getElementById("map");
    if (!el) { setTimeout(init, 300); return; }
    // 幂等：同一容器只建一次地图；再次进入只调整尺寸，
    // 否则重复 L.map("map") 会抛 “Map container is already initialized.”
    if (map) { resize(); return; }
    // 视图隐藏时容器尺寸为 0，此时建图只会得到 0×0 画布；
    // switchView 每次进入地图视图都会再调用 init()，那时容器已经可见。
    if (!el.clientWidth || !el.clientHeight) return;

    map = L.map("map", {
      center: [53.2, 24.5], zoom: 4, zoomControl: true,
      attributionControl: false, preferCanvas: true,
    });

    // 底图：自绘欧洲国界（离线，无需瓦片）
    L.geoJSON(EUROPE_GEOJSON, {
      style: {
        color: "#3f5c85", weight: 1.1, fillColor: "#16273f",
        fillOpacity: 1,
      },
    }).addTo(map);

    layers.places = L.layerGroup().addTo(map);
    layers.routes = L.layerGroup().addTo(map);

    renderPlaces();
    renderMapPane();
  }

  function renderPlaces() {
    layers.places.clearLayers();
    Object.entries(PLACES).forEach(([name, p]) => {
      const color = CAMP[p.kind] || CAMP.other;
      // 仅让以下四处地标常显；其余地点靠悬停查看，避免中欧标注堆叠。
      const MAJOR = ["鲍罗金诺", "奥斯特里茨", "别列津纳", "童山"];
      const big = MAJOR.indexOf(name) >= 0;
      const m = L.circleMarker([p.lat, p.lng], {
        radius: big ? 6 : 4,
        color, weight: big ? 2 : 1.4,
        fillColor: color, fillOpacity: big ? 0.55 : 0.3,
      });
      const evs = EVENTS.filter(e => e.place === name);
      const battles = BATTLES.filter(b => b.place === name);
      m.bindPopup(`
        <b>${esc(name)}</b><br>
        <span style="color:#8b99a8;font-size:11.5px">${esc(p.modern || "")}</span>
        ${p.ru ? `<br><span style="color:#5d6b7c;font-size:11px">${esc(p.ru)}</span>` : ""}
        ${battles.length ? `<hr style="border:none;border-top:1px solid #24395c;margin:7px 0">
          ${battles.map(b => `<div style="margin-bottom:5px">
            <b style="color:#c9a227">${esc(b.name)}</b>
            <span style="color:#8a7020;font-size:11px">　${b.year}.${b.month}</span>
            <div style="font-size:11.5px;margin-top:2px">${esc(b.desc)}</div></div>`).join("")}` : ""}
        ${evs.length ? `<hr style="border:none;border-top:1px solid #24395c;margin:7px 0">
          ${evs.slice(0, 6).map(e => `<div style="font-size:11.5px;margin-bottom:3px">
            <span style="color:#8a7020">${e.year || ""}</span> ${esc(e.title)}</div>`).join("")}` : ""}
      `, { maxWidth: 300 });
      m.addTo(layers.places);
      if (big) {
        m.bindTooltip(name, {
          permanent: true, direction: "bottom", offset: [0, 6],
          className: "wp-tip",
        });
      }
    });
  }

  /* ---------- 路线 ---------- */
  function routeLatLngs(pts) {
    return pts.map(p => {
      const pl = PLACES[p.p];
      return pl ? [pl.lat, pl.lng] : null;
    }).filter(Boolean);
  }

  function toggleRoute(id, on) {
    const r = ROUTES.find(x => x.id === id);
    if (!r) return;
    if (!on) {
      if (routeLines[id]) { layers.routes.removeLayer(routeLines[id]); delete routeLines[id]; }
      (routeMarkers[id] || []).forEach(m => layers.routes.removeLayer(m));
      delete routeMarkers[id];
      return;
    }
    if (routeLines[id]) return;

    const ll = routeLatLngs(r.pts);
    if (ll.length < 2) return;

    routeLines[id] = L.polyline(ll, {
      color: r.color, weight: 2.6, opacity: 0.85,
      dashArray: r.kind === "retreat" ? "7,6" : null,
    }).addTo(layers.routes);

    // 途经点：起讫两端加编号徽标，中间用小圆点 → 方向可读
    routeMarkers[id] = r.pts.map((p, i) => {
      const pl = PLACES[p.p];
      if (!pl) return null;
      const isEnd = i === 0 || i === r.pts.length - 1;
      if (isEnd) {
        const label = i === 0 ? "起" : "讫";
        const m = L.marker([pl.lat, pl.lng], {
          icon: L.divIcon({
            className: "wp-route-end",
            html: `<span style="display:inline-flex;align-items:center;justify-content:center;
              width:20px;height:20px;border-radius:50%;background:${r.color};
              color:#0d1726;font:700 11px/1 sans-serif;border:2px solid #0d1726;
              box-shadow:0 0 8px rgba(0,0,0,.6)">${label}</span>`,
            iconSize: [20, 20], iconAnchor: [10, 10],
          }),
        });
        m.bindTooltip(
          `<b>${esc(p.p)}</b>${p.y ? `<br><span style="color:#8a7020">${p.y}${p.m ? "." + p.m : ""}</span>` : ""}` +
          `<br><span style="font-size:11px;color:#8b99a8">${i === 0 ? "起点" : "终点"}</span>`,
          { direction: "top" });
        return m.addTo(layers.routes);
      }
      return L.circleMarker([pl.lat, pl.lng], {
        radius: 3.5, color: r.color, weight: 2,
        fillColor: "#0d1726", fillOpacity: 1,
      }).bindTooltip(
        `<b>${esc(p.p)}</b>${p.y ? `<br><span style="color:#8a7020">${p.y}${p.m ? "." + p.m : ""}</span>` : ""}`,
        { direction: "top" }
      ).addTo(layers.routes);
    }).filter(Boolean);

    routeLines[id].bindPopup(`<b>${esc(r.label)}</b><br>
      <span style="font-size:11.5px;color:#8b99a8">${esc(r.desc)}</span>`);

    // 自动缩放到整条路线，避免线段被视口裁掉
    map.fitBounds(routeLines[id].getBounds(), { padding: [40, 40] });
  }

  /* ---------- 播放撤退 ---------- */
  function playRoute(id) {
    const r = ROUTES.find(x => x.id === id);
    if (!r) return;
    stopPlay();                       // 先回收上一次播放的标记与定时器
    if (!routeLines[id]) toggleRoute(id, true);
    const pts = routeLatLngs(r.pts);
    if (pts.length < 2) return;

    playGhost = L.circleMarker(pts[0], {
      radius: 7, color: "#e0c05c", weight: 3,
      fillColor: "#c9a227", fillOpacity: 0.9,
    }).addTo(map);

    playIdx = 0;
    const step = () => {
      if (playIdx >= pts.length) { stopPlay(); return; }
      playGhost.setLatLng(pts[playIdx]);
      const p = r.pts[playIdx];
      const evs = EVENTS.filter(e => e.place === p.p);
      playGhost.unbindTooltip();
      playGhost.bindTooltip(
        `<b>${esc(p.p)}</b>${p.y ? `<br>${p.y}${p.m ? "." + p.m : ""}` : ""}` +
        (evs.length ? `<br><span style="font-size:11px;color:#8a7020">${esc(evs[0].title)}</span>` : ""),
        { direction: "top", permanent: true }
      ).openTooltip();
      playIdx++;
      animTimer = setTimeout(step, 1150);
    };
    step();
    const btn = document.getElementById("playRouteBtn");
    if (btn) btn.textContent = "⏹ 停止";
  }

  // 停止播放：清定时器、摘掉移动标记与其提示、复位按钮。
  // 一切出口都走这里，重复播放/中途停止都不会留下 ghost。
  function stopPlay() {
    if (animTimer) { clearTimeout(animTimer); animTimer = null; }
    if (playGhost) {
      playGhost.unbindTooltip();
      if (map) map.removeLayer(playGhost);
      playGhost = null;
    }
    const btn = document.getElementById("playRouteBtn");
    if (btn) btn.textContent = "▶ 播放撤退路线";
  }

  /* ---------- 侧栏 ---------- */
  function renderMapPane() {
    const pane = document.getElementById("mapPane");
    pane.innerHTML = `
      <h3>战役</h3>
      ${BATTLES.map(b => `
        <div class="battle-item" data-id="${b.id}">
          <div class="bi-name">${esc(b.name)}</div>
          <div class="bi-meta">${b.year}.${b.month}${b.day ? "." + b.day : ""} · ${esc(b.place)}</div>
          <div class="bi-desc">${esc(b.desc)}</div>
        </div>`).join("")}

      <h3 style="margin-top:18px">路线</h3>
      ${ROUTES.map(r => `
        <label class="route-toggle">
          <input type="checkbox" data-route="${r.id}">
          <span style="color:${r.color}">━</span>
          <span>${esc(r.label)}</span>
        </label>`).join("")}
      <div style="margin-top:10px">
        <button class="btn-gold" id="playRouteBtn" style="width:100%">▶ 播放撤退路线</button>
      </div>

      <h3 style="margin-top:18px">地点（${Object.keys(PLACES).length}）</h3>
      <div style="font-size:11.5px;color:#8b99a8;line-height:2">
        ${Object.entries(PLACES).map(([k, v]) =>
          `<div style="cursor:pointer" onclick="MapView.focus(${jsArg(k)})">
            <span style="color:${CAMP[v.kind] || CAMP.other}">●</span> ${esc(k)}
            <span style="color:#5d6b7c;font-size:10.5px">　${esc((v.modern || "").slice(0, 18))}</span>
          </div>`).join("")}
      </div>`;

    pane.querySelectorAll(".battle-item").forEach(el => {
      el.onclick = () => {
        const b = BATTLES.find(x => x.id === el.dataset.id);
        if (!b) return;
        const pl = PLACES[b.place];
        if (pl) map.setView([pl.lat, pl.lng], 7, { animate: true });
        showBattle(b.id);
      };
    });
    pane.querySelectorAll("[data-route]").forEach(cb => {
      cb.onchange = () => toggleRoute(cb.dataset.route, cb.checked);
    });
    document.getElementById("playRouteBtn").onclick = () => {
      // stopPlay 自己会复位按钮文案
      if (animTimer) stopPlay();
      else playRoute("r-1812-retreat");
    };
  }

  function showBattle(bid) {
    const b = BATTLES.find(x => x.id === bid);
    if (!b) return;
    openModal(`
      <h2>${esc(b.name)}</h2>
      <p style="font-size:12px;color:#8a7020">
        ${b.year} 年 ${b.month} 月${b.day ? " " + b.day + " 日" : ""}　·　${esc(b.place)}
        　·　俄军 ${esc(b.russian)}　对　法军 ${esc(b.french)}
      </p>
      <div class="detail-section"><h4>概述</h4><p>${esc(b.desc)}</p></div>
      <div class="detail-section"><h4>阶段</h4><ul>
        ${b.phase.map(p => `<li><b>${esc(p.name)}</b>
          <div style="font-size:11.5px;margin-top:3px">${esc(p.desc)}</div></li>`).join("")}
      </ul></div>
      <div class="detail-section"><h4>出场人物</h4>
        ${(b.chars || []).map(c => `<span class="rel-chip" onclick="closeModal();showCharacterCard(${jsArg(c)})">
          <span style="color:${factionColor((charById(c) || {}).faction)}">●</span> ${esc(charName(c))}</span>`).join("")}
      </div>
      <div class="modal-actions"><button class="btn-ghost" onclick="closeModal()">关闭</button></div>`);
  }

  function focus(name) {
    const p = PLACES[name];
    if (p && map) map.setView([p.lat, p.lng], 8, { animate: true });
  }

  function resize() { if (map) setTimeout(() => map.invalidateSize(), 80); }

  return { init, resize, focus, showBattle, playRoute };
})();
