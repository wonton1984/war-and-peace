# 《战争与和平》人物关系图谱 · 代码审核报告（2026-09-14）

> 处理状态（2026-09-14）：G01–G06 已在本地修复并完成回归；下文保留原审核发现及独立复验，
> 本轮最终决策与验证证据见[第七节](#七修复执行记录2026-09-14)。本报告记录提交前验证，发布状态以 Git 提交记录及 GitHub Pages 部署结果为准。

- 审核日期：2026-09-14
- **受审快照：`main` @ `539283a`**（工作区 clean 时的状态）
- 范围：`index.html`、`css/style.css`、`js/` 五个前端模块、`data/` 全部数据文件、`scripts/` 门禁与管线、README / docs/schema.md 契约。
- 方法：静态阅读；在 Node 沙箱中装载全部数据并断言不变量；真实 Chrome（`--headless=new`）装载全站并逐个跑通各视图渲染函数；执行项目全部门禁与回归；另派一个独立审查 agent 做交叉验证。
- **审核期间工作区发生了并发修改**（非本次审核所做）：G01–G06 与部分交叉验证发现被修复。本报告分两阶段呈现——第二节是对 `539283a` 的发现，第三节是对修复后工作区的独立复验。

---

## 一、结论

**`539283a` 快照未发现 P1 级问题，上一轮报告（2026-09-13）的 F01–F16 已核实闭环。** 项目当时处于可交付状态：门禁全部退出 0、4 套回归全绿、真实浏览器 11 项渲染全部通过且 `window.onerror` 为空。

当时新发现 **6 项问题，最高 P2**，共同形状是**门禁覆盖面小于其宣称范围**，而不是功能坏掉。

**在审核期间，工作区出现了并发修复，G01–G06 全部被处理**，并附带新增了针对性的回归测试。第三节对修复结果做了独立复验：全部门禁与回归在修复后仍全绿，且新增测试确实能捕获它们声称要捕获的缺陷。其中 G03 的修复尤为关键——新增的转义回归测试**在我捕获到的一次中间态运行中是红的**，实证了数据可被执行的问题真实存在（见 §2.3 证据）。

### 问题总表（针对 `539283a`）

| 编号 | 级别 | 问题 | 主要位置 | 状态 |
|---|---|---|---|---|
| G01 | P2 | `data/background.js` 不在任何门禁覆盖内，前端无字段兜底 | `scripts/lint_data.js:27-29,32-34`、`scripts/smoke_data.js:12-18`、`js/app.js:495,506,521` | ✅ 已修 |
| G02 | P3 | 版权／字数门禁实际覆盖面窄于 schema 表述；`✓` 文案夸大已证范围 | `scripts/lint_data.js:76-83,109-111,167-168,204-206,253,267-276`、`docs/schema.md:207` | ✅ 已修 |
| G03 | P3→**P2** | `esc()` 不转义单引号，数据被拼进内联 `onclick` 的 JS 字符串 | `js/app.js:40-44` 及 12 处使用点、`js/map.js:227` | ✅ 已修 |
| G04 | P3 | `#rel-` 分享链接：注释描述了未实现的功能 | `js/app.js:416` | ✅ 已修 |
| G05 | P3 | `js/map.js` 同一处连续两条互相矛盾的注释 | `js/map.js:52-55` | ✅ 已修 |
| G06 | P3 | `threaded` 计数只可能覆盖详录人物，文案未限定范围 | `js/relations.js:337-339` | ✅ 已修 |

**G03 的级别在原稿中被低估。** 我最初按「当前 0 命中」定为 P3；并发修复附带的回归测试（`scripts/test_frontend.js` 注入 id `e-');globalThis.auditInjected=true;//`）证明该模式是**可执行的**，而非仅潜在。按最终证据回填为 P2。

---

## 二、详细发现（针对 `539283a`）

### G01 · P2：新增数据文件 `data/background.js` 落在全部门禁之外

**位置**

- `scripts/lint_data.js:27-29`（`files` 数组）、`:32-34`（`exportNames` 数组）
- `scripts/smoke_data.js:4`（自述「按 index.html 的顺序装载」）、`:12-13`（`ORDER`）、`:16-18`（`names`）
- `js/app.js:495`、`:506`、`:521`（直接 `.map()` 三个数组）

**根因与影响**

`index.html:120` 已引入 `data/background.js`，但两道数据门禁的装载清单都没有跟着更新：

```
$ node scripts/lint_data.js
  已载入数据文件 13 个：…（不含 background.js）
$ node scripts/smoke_data.js
  （输出中没有 ERA_BACKGROUND 行）
```

三层后果：

1. **版权门禁不扫它。** 这是项目中散文密度最高的数据文件之一（展示文本约 1.2k 字）。`lint_data.js` 的版权小节只遍历 `CHARACTERS / CHAPTERS / EVENTS / THEMES / ARCS / BATTLES / GLOSSARY / NAMES`。项目「零原文」的版权立场正建立在门禁之上。
2. **没有 schema／引用校验。** `topics[].title/text/reading`、`timeline[].year/title/text`、`sources[].title/url` 均无必填校验；`timeline[].year` 不校验是否落在 `1805–1820`。
3. **前端无兜底。** `js/app.js` 对 `period`/`intro`/`framing`/`perspective` 走 `esc()`（`undefined` → 空串，安全），但对 `topics`/`timeline`/`sources` 直接 `.map()`。字段缺失即抛 `TypeError`，且没有门禁会在发布前拦下它。

`scripts/smoke_data.js:4` 的自述「按 index.html 的顺序装载全部 data/*.js」在 `539283a` 后也不再成立——`index.html` 顺序已插入 `background.js`，`ORDER` 未同步。

**当时未造成故障**：真实浏览器实测 `ERA_BACKGROUND` 正常装载，`showBackground()` 渲染出 4302 字弹层。这是覆盖缺口，不是现存缺陷。

### G02 · P3：版权／字数门禁的实际覆盖面窄于 schema 表述

**位置**：`scripts/lint_data.js:109-111`（bio）、`:167-168`（gist）、`:204-206`（summary、history）、`:253`（glossary.desc）、`:267-276`（版权门禁小节与成功文案）、`docs/schema.md:207`

`docs/schema.md:207` 的表述读起来是全局规则：

> 5. **版权门禁**：`gist`>60、`summary`>140、`bio`>80、`history`>120、`desc`>80 报错；引号包裹片段 >20 字报错；出现 `quote` 字段直接报错；

但 `539283a` 的实现中：

- **`LIMITS.desc` 只作用于名物**（`:253`）。`battles.desc`、`battles.phase[].desc`、`routes.desc`、`families.desc`、`themes.question`、`arcs.stages[].desc`、`relations.phases[].state` 都没有长度检查。
- **引文门禁只扫 3 个字段**。对全部展示文本逐字段统计：

| 字段 | 条数 | 总字数 | 引文门禁 |
|---|---:|---:|---|
| `chapters.gist` | 361 | 18543 | ✔ 已扫 |
| `events.summary` | 133 | 11338 | ✔ 已扫 |
| `characters.bio` | 197 | 10390 | ✔ 已扫 |
| `relations.phases.state` | 140 | 1303 | ✘ 未扫 |
| `chapters.place` | 340 | 1182 | ✘ 未扫 |
| `glossary.desc` | 28 | 869 | ✘ 未扫 |
| **`events.history`** | 12 | **825** | ✘ 未扫 |
| `arcs.stages.desc` | 37 | 518 | ✘ 未扫 |
| `background.*`（全部） | 22 | ~1220 | ✘ 未扫 |
| 其余（`battles.phase.desc` / `routes.desc` / `families.*` / `themes.*` 等） | ~63 | ~1450 | ✘ 未扫 |

| 口径 | 结果 |
|---|---|
| 展示文本总字数 | 47824 |
| 引文门禁覆盖 | 40271 |
| **覆盖率** | **84.2%** |

最大的一块未覆盖字段是 `events.history`：它在 `:205` 有长度检查，但没有引文检查。

**`✓` 文案也夸大了已证范围。** `:276` 的 `if (!violations) ok("无 quote 字段、无超长引文")` 中，`violations` 只统计 `quote` 字段。长度与引文超限走的是 `bad()` → `problems`，与这条文案无关。因此该行 ✓ 实际只证明了「没有 `quote` 字段」。

**当时无违规**：所有字段的超 20 字引文命中数均为 0，字数上限无一超出。这是防线缺口，不是现存违规——但意味着新加入的文本不受约束。

### G03 · P3→P2：`esc()` 不转义单引号，数据被拼进内联 `onclick` 的 JS 字符串

**位置**：`js/app.js:40-44`（`esc` 定义）及约 12 处使用点；`js/map.js:227`

`esc()` 转义 `& < > "` 四种字符，但**不转义 `'`**。而当时的模式是：

```js
onclick="MapView.focus('${esc(k)}')"          // js/map.js:227
onclick="showEventCard('${e.id}')"            // js/app.js:259 等
```

`"` 已被转义，所以无法逃出 HTML 属性；但内容若含 `'`，就会提前闭合 JS 字符串字面量。由于浏览器**先做 HTML 实体解码、再编译内联处理器**，注入的 `');<语句>;//` 会被当作 JavaScript 执行。

**当时全量扫描为 0 命中**（人名/地点/id 都不含引号），因此我最初定为 P3。

**级别回填为 P2 的直接证据**：并发修复附带的转义回归测试——

```js
const unsafeId = "e-');globalThis.auditInjected=true;//";
assert.equal(run("globalThis.auditInjected"), false, "data executed as JavaScript");
```

**在我捕获到的一次中间态运行中（测试已加入、`js/app.js` 尚未改），该断言失败：`true !== false`。** 数据确实被执行了。这证明该模式不是理论风险。

放大器是 G01：`ERA_BACKGROUND.timeline[].year` 当时既无 schema 校验、又被原样插进 `aria-label="查看${t.year}年人物关系"` 与 `RelationsView.setYear(${t.year})`。两个缺陷叠加构成一条完整的注入路径。

### G04 · P3：`#rel-` 分享链接——注释描述了未实现的功能

`js/app.js:416` 的注释写着 `#ch-2-3-14 / #e-austerlitz / #rel-a-b`，但 `:417-427` 只有 `#ch-` / `#e-` / `#y` 三个分支。`showRelationFrom(a, b)` 函数本身存在且可达，但 `#rel-` 哈希形式从未实现：带 `#rel-andrei-natasha` 打开会静默落到默认视图。README 第 56 行只列了三种，所以**对外文档没有说谎**，问题局限在这行漂移的注释。

### G05 · P3：`js/map.js` 同一处连续两条互相矛盾的注释

```js
      // 常显地名只给庄园与五大会战；其余地点用悬停/弹层查看，
      // 否则中欧一带 20 个常显标注会互相压叠。
      // 常显标注只留互不贴近的四个关键地标（两座庄园 + 两大会战），
      // 其余地点靠悬停查看：常显过多会在中欧一带堆叠成一团。
      const MAJOR = ["鲍罗金诺", "奥斯特里茨", "别列津纳", "童山"];
```

第一条是修改前的陈述残留，第二条才是当前行为。代码正确，注释误导。

### G06 · P3：`threaded` 计数只可能覆盖详录人物，文案未限定范围

侧栏输出「`${threaded} 人有当年线索`」。`charActiveAt` 的打分来源是 `RELATIONS` 端点与 `CHAPTERS[].chars`；实测 `chapters[].chars` 只覆盖 **57** 位人物且**全部为详录**（`tier === "minor"` 命中 **0**）。因此 139 位简录人物除个别关系边端点外恒为 0 分，`threaded` 实质是「有当年线索的详录人物数」，而文案读起来覆盖全部 197 位。

---

## 三、修复后的独立复验（工作区并发修改）

### 修复内容（我只做复验，未参与修改）

| 发现 | 修复方式 |
|---|---|
| G01 | `lint_data.js` 的 `files`/`exportNames` 加入 `background.js`/`ERA_BACKGROUND`；并**从 `index.html` 反向解析脚本清单**，任何网页数据文件未纳入门禁即报错。`smoke_data.js` 同步，并在 `ORDER` 与 `index.html` 不一致时抛错。新增 `[时代背景 background.js]` 小节：必填非空字符串、长度上限、`timeline[].year` 必须为 1805–1820 整数且严格递增、`sources[].url` 必须为有效 HTTPS。 |
| G02 | 版权门禁从逐字段硬编码改为**递归遍历全部已装载数据**（对象、数组、乃至对象键），按字段名套用 `LIMITS`，并统计实际扫描量。成功文案改为「已递归检查 N 个字符串」。 |
| G03 | 新增 `jsArg(v) = esc(JSON.stringify(v))`，替换全部 18 处内联插值（app.js 15 / map.js 2 / relations.js 1）。 |
| G04 | 注释改为 `#ch-2-3-14 / #e-austerlitz / #y1812`。 |
| G05 | 两条矛盾注释合并为一条正确的。 |
| G06 | `threaded` 增加 `c.tier === "core"` 过滤，文案改为「详录人物中 N 人有当年线索」。 |

### 复验结果

**全部门禁与回归（修复后工作区）：**

```
node scripts/lint_data.js          退出=0
node scripts/trust_guard.js        退出=0
node scripts/smoke_data.js         退出=0
node scripts/test_notes.js         退出=0   （63 passed）
node scripts/test_frontend.js      退出=0
python3 scripts/test_pipeline.py   退出=0
python3 scripts/test_guards.py     退出=0   （8 tests，原 5）
python3 scripts/check_gists.py     退出=0
python3 scripts/check_names.py     退出=0
```

**门禁输出对比：**

| | 修复前 | 修复后 |
|---|---|---|
| lint 装载数据文件 | 13 个（无 background） | **14 个**（含 background） |
| smoke 校验符号 | 无 `ERA_BACKGROUND` | `✓ ERA_BACKGROUND 7` |
| 版权门禁覆盖 | 3 个字段，约 84.2% 字数 | **递归扫描 26822 个字符串** |

**新增回归测试覆盖了新风险：**

- `test_guards.py::test_background_missing_or_invalid_is_rejected`：7 种变异（删 `topics`、`timeline` 改对象、`sources=[null]`、空 `reading`、`year=1804`、`year='1805'`、`url='javascript:alert(1)'`）逐一必须被拒；文件整体缺失时 lint 与 smoke 都必须非零退出。
- `test_guards.py::test_nested_copyright_and_description_limits_are_enforced`：5 种嵌套变异（`background.topics[].text`、`events[].history`、`relations[].phases[].quote`、`battles[].phase[].desc`、`places[].note`）必须被拒，且不得再输出「无 quote 字段、无超长引文」。
- `test_guards.py::test_copyright_boundary_counts_unicode_characters`：引文长度按**码点**计数（`😀`×20 通过、×21 拒绝），而非 UTF-16 码元。
- `test_frontend.js`：新增 HTML 实体解码 + 逐按钮点击穿透导航；以及上文 G03 的转义回归断言。

**真实浏览器复验（Chrome `--headless=new`，修复后）：**

```
PASS ERA_BACKGROUND 载入 :: object topics=5 timeline=4 sources=4
PASS showBackground() :: modalBody 4302 字, details=6, 外链=4
PASS showCharacterCard(pierre) :: 28829 字
PASS showEventCard(e-sherer-saloon) :: 3562 字
PASS showChapter(4-1-03) :: 1244 字
PASS showCharacterIndex() :: 47141 字
PASS showThemesIndex() :: 1820 字
PASS FamilyView.render() :: 10230 字
PASS RelationsView 16 年 setYear :: ok
PASS MapView.init() :: ok
PASS renderChapterList() :: 319905 字
onerror: 无
```

**残留的两处未收口（供参考，不构成缺陷）：**

1. `js/app.js` 的 `showBackground()` 中 `${t.year}` 仍原样插入 `aria-label` 与 `RelationsView.setYear()`，未走 `jsArg()`。当前安全，因为新增的 schema 校验已强制 `timeline[].year` 为 1805–1820 整数——即**数据层已堵死**，只是编码习惯不统一。
2. `esc()` 本身仍不转义 `'`。`jsArg()` 通过 `JSON.stringify` 产生双引号字面量从而绕开了该问题，但任何未来直接使用 `esc()` 拼内联字符串的代码会重新踩中。

### 本次审核自身的方法学更正

我在发现 G03 时据「当前 0 命中」定为 P3，这是**低估**。正确的判据不是「今天的数据是否干净」，而是「这个模式在数据被污染时是否可执行」——后者由并发修复的回归测试证伪了我的定级。教训记录在此，供后续审核参考。

---

## 四、交叉验证（独立审查 agent）

审核期间另派一个独立 agent 做交叉验证，返回 4 条。**逐条复验后采纳 1 条、驳回 3 条**，记录如下以免重复讨论：

| # | 主张 | 复验结论 |
|---|---|---|
| 1 | `js/app.js:425` 的 `#y1812` 分支不切视图、不关弹层，从家族/地图视图深链会静默改年份 | **驳回**。哈希只在 `DOMContentLoaded` 时读取一次，没有 `hashchange` 监听；加载时 `switchView("relations")` 刚执行完且无弹层。所述复现（加载后改 URL）根本不触发任何代码。`:508` 那处需要 `closeModal()+switchView()` 是因为它从打开的弹层里调用，差异是必要的而非遗漏。 |
| 2 | `switchView()` 不关弹层，开着弹层点标签页会留下孤儿遮罩 | **驳回**。`#overlay` 是 `position:fixed; inset:0; z-index:200`（`css/style.css:345-350`），`#viewTabs` 为 `z-index:55`。弹层打开时标签页被完全遮住，无法点击，所述复现不成立。（无键盘焦点陷阱是另一回事，属无障碍打磨项，未达报告门槛。） |
| 3 | `js/relations.js:339` 每个滑块 tick 做约 5 万次迭代，拖动可见卡顿 | **驳回**。实测 50 次采样：`threaded` 一项 **0.709 ms/次**，`setYear` 全部纯计算合计 **0.685 ms/次**。亚毫秒级，不构成卡顿；真实开销在 ECharts `setOption` 与 `innerHTML` 重建，不在此处。 |
| 4 | `js/app.js:507` 的 `timeline[].year` 未转义即插入 `aria-label` 与内联 `onclick` | **采纳**。已并入 §2.3 作为 G03 的具体实例与放大器（当时 `background.js` 无任何 schema 校验）。修复后由数据层校验堵死，见 §3 残留项 1。 |

---

## 五、`539283a` 上已核实健康的部分

**数据不变量（Node 沙箱装载全部 14 个数据文件后断言）：**

| 断言 | 结果 |
|---|---|
| 关系边缺 `from.y`（`js/app.js:110` 直接解引用 `r.from.y`） | **0** |
| 关系边悬空 `phases[].ev` | **0** |
| 关系边无 `phases` | **0** |
| `phases[].y` 非单调递增 | **0** |
| `to.y` 与末阶段 `y` 不一致 | **0** |
| `born` / `died` 的类型（`charActiveAt` 的数值比较依赖） | 仅 `number` 或 `null`，**无字符串** |
| 人物/章节/事件 id 违反笔记键正则 `^(char\|event\|ch):[A-Za-z0-9._-]+$` | **0** |
| id 与 `__proto__` / `constructor` / `prototype` 冲突 | **0** |
| 地点名 / 人物名 / 人物 id 含 `'` `"` `\` `<`（G03 触发条件） | **0** |
| 锚点缺席导致的坐标跳变（1805、1820 在场而 1812 缺席） | **0** 例 |

**仓库卫生：** `js/` 与 `index.html` 中 `console.` / `debugger` / `TODO` / `FIXME` 残留 **0**；`index.html` 24 处资源版本标记全部为 `?v=21`；运行时网络请求（`fetch`/`XHR`/`serviceWorker`）**0**，唯一外部 URL 是用户主动点击的 4 条资料来源；`.gitignore` 正确排除 `corpus/`、`.env*`、`*.epub`、`*.pem`、`*.key`、`/AGENTS.md`、`/PLAN.md`，`git ls-files` 中无凭据、无 epub、无逐章语料。

**上一轮报告修复项抽样复核：**

- **F01（生成器覆盖人工数据）**：`scripts/jsio.py:274-289` 的 `atomic_write` 在 `create=True` 时用 `os.link` 原子创建（预检查后被他人抢先写入也不会覆盖），否则 `os.replace`；`refuse_existing`（`:305`）在 `build_chapters.py:146` 生效。
- **F03 / F15（同步丢字段）**：`test_pipeline.py` 与 `test_guards.py` 全通过，含 `day` 字段保真与非法日期不落盘。
- **F05–F07（笔记可靠性）**：`test_notes.js` 63 条断言覆盖异常导入、禁用存储、迁移、删除墓碑、多页冲突与导出。

---

## 六、明确没有覆盖的范围

- **未做第三方依赖审计**：`assets/vendor/leaflet.js`、`echarts.min.js`、`leaflet.css` 未核版本号、已知 CVE 或许可证。本地化离线运行降低了但不消除这项风险。
- **未在 Safari / Firefox / 真实移动设备上验证**：本次只用 Chrome headless。
- **未验证线上部署**：只对本地快照负责，未核对 GitHub Pages 当前发布内容。
- **未审文学内容准确性**：`trust_guard` 的 77 组歧义称名、114 条索引无精确称名、36 组事件称名、2 条 `names.cao`、15 条 gist 反查线索全部**未逐条判定**，与上一轮报告口径一致。
- **未独立复算 Python 管线全部路径**：`merge_events.py` / `merge_minor.py` / `sync_*.py` 依赖项目自带回归（已通过）间接认定，未逐行重审。
- **未做无障碍与对比度审计**：`aria-label`、`tabindex="-1"` 的存在已注意到，但未做系统性 WCAG 检查。

**§3 的复验结论针对的是审核期间的工作区状态（未提交）。** 该状态若被提交，本报告 §3 即刻对其生效；若被回退，则以 §2 的 `539283a` 发现为准。

## 七、修复执行记录（2026-09-14）

本轮只修正报告涉及的门禁、交互参数与说明，不增加新的阅读功能，不改写正式文学数据。

### 逐项处理

| 编号 | 决策与实际修改 |
|---|---|
| G01 | `lint_data.js` / `smoke_data.js` 登记 `background.js` 与 `ERA_BACKGROUND`。lint 校验必填文本、非空对象数组、1805–1820 整数递增年表及 HTTPS 来源；缺文件或缺全局符号不能通过。额外核对网页数据依赖清单，后续新增未登记数据文件会被拒绝，smoke 还核对装载顺序。 |
| G02 | 递归检查全部已登记数据的字符串值和对象键；嵌套 `quote` 字段也报错。`gist` / `summary` / `bio` / `history` / `desc` 的既有上限对所有同名字段生效，不擅自把 `question` / `state` 等字段当作 `desc`。去掉引文匹配的200字符截断，按 Unicode 码点计长；版权小节只有自身无错误才输出成功。时代背景的文本上限与检查边界已补入 schema。 |
| G03 | 未采纳单独增加 `&#39;` 的建议：HTML 属性解析会还原该实体，仍会破坏 JS 字符串。新增 `jsArg()`，先 `JSON.stringify` 再 HTML 转义；人物、章节、事件、主题、关系、笔记按钮及地图地点的动态字符串参数统一使用它。没有宣称这等同于整站 XSS 安全认证。 |
| G04 | 注释改为实际支持的 `#ch-` / `#e-` / `#y1812`；不增加未要求的关系分享路由。 |
| G05 | 两条旧注释均替换：第二条“两座庄园＋两大会战”也与名单不符。现仅说明以下四处常显，不改变标注名单或地图行为。 |
| G06 | `threaded` 显式限定 `tier === "core"`，文案改为“详录人物中 N 人有当年线索”。不把简录人物的保守索引混入活跃度算法，不声称这是全体人物的在世或出场人数。 |

G01 选择发布前拦截：数组缺字段会在 `openModal()` 的模板参数求值时抛错。
不以空数组兜底隐藏错误，也不把该故障描述为必然先打开空白弹层。

### 验证证据

第三节保留审核方当时的中间态复验；此后补入数据依赖清单回归，最终为下述9项门禁测试。

- 新增门禁回归先在旧实现上失败：非法背景字段、缺文件、嵌套禁用字段、
  事件史实段落引文、战役阶段描述超长、201字符引文及 Unicode 边界均暴露覆盖缺口。
- `test_guards.py` 现为 **9 项测试，全通过**，含网页新增未登记数据依赖及缺少
  `ERA_BACKGROUND` 符号的拒绝场景；20个扩展区汉字允许、21个被引号包裹时拒绝。
- `test_frontend.js` 不再只匹配内联脚本源码：执行生成的按钮动作，验证跳转后的内容。
  合成事件 ID 在旧实现中会执行夹带脚本；修复后只打开目标事件，不执行数据中的代码。
- 五道检查全部退出0：`lint_data.js`、`trust_guard.js`、`smoke_data.js`、
  `check_gists.py`、`check_names.py`。
- 四套回归全部通过：笔记 **63** 条、前端导航与参数隔离、数据管线 **23** 项、
  门禁 **9** 项。正式数据仍有人工待核项，未将其标成已审定。
- 真实 Chromium `file://`：带单引号的测试地点，修复前点击后地图中心不变；
  修复后实际中心到达指定坐标 `[12.34, 45.67]`，缩放为8。测试地点只存在于页面内存。
- 浏览器验证章节→事件→人物、主题→章节、人物关系年份→侧栏详情→事件、
  人物志、家族、地图重复进入、全部16个年份及时代背景跳转；未捕获应用运行时错误。
- 详录人数边界：1805年计数34；临时把皮埃尔设为简录后为33，恢复后回到34。
  桌面1440px、手机390px肉眼检查通过，手机无横向溢出。
- 页面资源版本统一升至 `?v=22`。未新建常驻服务、未上传语料、未更改用户笔记。

### 保留边界

HTTPS 来源仅做语法校验；文本门禁不是原文相似度检测，不能替代人工版权判断。
原报告列出的文学内容待核、第三方依赖、Safari / Firefox、真实移动设备与完整安全审计范围不变。
本节记录提交前的本地验证结果；后续发布状态以 Git 提交记录及 GitHub Pages 部署结果为准。
