# docs/schema.md — 数据规范与受控词表（v1.0）

> 《战争与和平》拆书地图数据生产的**唯一依据**（人类与 AI 协作者通用）。
> 所有合法值都在这里，写错会被 `scripts/lint_data.js` 拦下。
>
> **铁律第 0 条：不录译文。** 草婴译本（1923–2015）在版权保护期内。
> 全部 `gist` / `summary` / `bio` / `desc` 为本项目**自撰概述**；schema 无 `quote` 字段。
> 字数上限的单一事实源是 `scripts/data_limits.js`（lint 与 merge 同口径）。

---

## 1. data/structure.js — 卷/部/章骨架

底本实测（草婴译，读客经典文库 / 江苏凤凰文艺 2019，ISBN 9787559433602）：

```js
const STRUCTURE = [
  { book:1, parts:[ {part:1, chapters:25}, {part:2, chapters:21}, {part:3, chapters:19} ] },
  { book:2, parts:[ {part:1,chapters:16}, {part:2,chapters:21}, {part:3,chapters:26},
                    {part:4,chapters:13, flag:"verify"},   // 部分公开目录记 12 章
                    {part:5,chapters:22} ] },
  { book:3, parts:[ {part:1,chapters:23}, {part:2,chapters:39}, {part:3,chapters:34} ] },
  { book:4, parts:[ {part:1,chapters:16}, {part:2,chapters:19}, {part:3,chapters:19}, {part:4,chapters:20} ] },
  { book:5, epilogue:true, parts:[ {part:1, chapters:16}, {part:2, chapters:12} ] }
];
// 合计 17 部 361 章（book 5 = 尾声）
```

## 2. data/chapters.js — 全书 361 张章节卡

```js
{ id:"2-3-14",              // 卷-部-章；URL 锚点 #ch-2-3-14
  book:2, part:3, ch:14,
  seq:77,                   // 全书叙述顺序 1..361
  year:1809, month:12,      // 故事内时间；议论/过场章为 null
  tag:"peace",              // 受控：peace | war | essay | transition
  place:"彼得堡",            // places.js 键，可 null
  chars:["pierre","helen"], // characters.js 键，必须可解析
  gist:"…≤60 字自撰概述…",
  flag:null }               // "verify" = 待核对
```

章节与事件是多对多关系，**唯一关联源为 `EVENTS[].ch`**；前端由它建立反向索引。
章节卡不再保存 `event` 字段。详情人物来自本章 `chars` 与 `CHARACTERS[].chapters` 反向索引的并集。

## 3. data/events.js — 完整事件卡（当前 133 张）

```js
{ id:"e-austerlitz",
  title:"奥斯特里茨：仰望天空",
  ch:["1-3-16","1-3-19"],   // 覆盖章节卡 id，必须可解析
  book:1, part:3,           // 冗余便于筛选
  year:1805, month:12, day:2,
  battle:"b-austerlitz",    // 可选：BATTLES.id；仅明确属于该战役时填写，禁止按年份推断
  type:"battle",            // 受控见 §7
  place:"奥斯特里茨",        // places.js 键
  factions:["russian_army","french_army"],   // 受控见 §8，1–3 个
  chars:["andrei","kutuzov","napoleon"],
  rel:[ { a:"andrei", b:"napoleon", kind:"enemy",
          delta:"对「伟人」的崇拜崩塌" } ],   // 关系变动（可空数组）
  theme:["history","death"],  // themes.js 键
  arc:[ { who:"andrei", stage:"幻灭" } ],     // arcs.js stage.label
  summary:"…≤140 字自撰概述…",
  history:null,             // 可选：小说×史实对照（自撰，≤120 字）
  flag:null }
```

`day` 可省略或为 null；填写时须有 `month`，且日期在该年月有效。
事件合并与同步共用 `scripts/jsio.py` 的字段契约；未知字段显式拒绝，未指定字段保留。
`battle` 的有无不由 `type` 自动推导：战场受伤等非 `battle` 类型也可明确关联战役。

## 4. data/characters.js — 人物志（当前 58 详录＋139 简录）

```js
{ id:"natasha", name:"娜塔莎",
  full:"娜塔莎·罗斯托娃",
  aliases:["娜塔莎·罗斯托娃","别祖霍娃伯爵夫人"],   // 全书唯一，lint 查重
  faction:"rostov",         // 受控见 §8
  family:"rostov",          // families.js 键，可 null
  born:1792, died:null,     // 年份，可 null
  title:"罗斯托娃伯爵小姐 → 别祖霍娃伯爵夫人",
  tier:"core",              // 受控：core（详录）| minor（简录）
  bio:"…≤80 字…",           // tier=core 必填；minor 可空
  arc:"…",                  // 可选：一句弧光
  chapters:["1-1-08"],      // 出场章节索引（corpus 抽取 + 人工校对）
  names:{ cao:"娜塔莎", zhou:"娜塔莎" },   // 多译本，见 names.js
  flag:null }
```

## 5. data/relations.js — 关系边（时间切片的驱动数据）

```js
{ id:"andrei__natasha",
  a:"andrei", b:"natasha",   // characters.js 键，a 字典序 < b
  kind:"courtship",          // 受控见 §9
  from:{ y:1805, m:12 },     // m 可 null
  to:{ y:1812, m:8 },        // null = 直到尾声
  phases:[ { y:1809, m:1, state:"舞会重逢·动心", ev:"e-natasha-first-ball" } ],
  weight:5,                  // 1–5，线宽
  flag:null }
```

**约束：**
- `a` / `b` 不得相同；同一 `(a,b)` 对不得重复出现多条边；
- `phases[].y` 必须落在 `[from.y, to.y]` 内且按年份升序；
- `phases[].ev` 若非 null，必须命中 `events.js` 的 id。

## 6. data/names.js — 多译本人名对照表

```js
{ id:"natasha",
  ru:"Наташа Ростова", en:"Natasha Rostova",
  cao:"娜塔莎·罗斯托娃",                       // 草婴（本项目基准，必填）
  variants:{ zhou:"娜塔莎·罗斯托娃", gao:null, dong:null,
             liu:null, lou:null },              // 未核实留 null + flag
  note:"…",
  flag:"verify" }
```

## 7. events.type 受控词表

| 值 | 含义 | 字形 | | 值 | 含义 | 字形 |
|---|---|---|---|---|---|---|
| `salon` | 沙龙 / 社交场 | 席 | | `wound` | 负伤 / 死亡 | 伤 |
| `family` | 家庭 / 庄园日常 | 家 | | `duel` | 决斗 | 决 |
| `ball` | 舞会 / 宴会 | 舞 | | `business` | 继承 / 债务 / 农政 | 产 |
| `hunt` | 打猎 / 节庆 | 猎 | | `intrigue` | 谋算 / 私奔 / 骗局 | 谋 |
| `battle` | 战役 / 战斗 | 战 | | `spirit` | 精神探索 / 共济会 / 顿悟 | 悟 |
| `march` | 行军 / 撤退 | 行 | | `essay` | 史论 / 议论章 | 论 |

## 8. factions 受控词表

| 值 | 全称 | 色 |
|---|---|---|
| `bezukhov` | 别祖霍夫家 | #c9a227 |
| `rostov` | 罗斯托夫家 | #b8552e |
| `bolkonsky` | 保尔康斯基家 | #6e8ca0 |
| `kuragin` | 库拉金家 | #8c4a66 |
| `druzh` | 德鲁别茨科伊（没落贵族） | #7a6f58 |
| `russian_army` | 俄军 | #4a6a4a |
| `french_army` | 法军 | #4a5a8c |
| `court` | 宫廷 | #9c8f7a |
| `mason` | 共济会 | #6f8f7a |
| `folk` | 农民 / 平民 / 士兵 | #8a7f6a |

## 9. relations.kind 受控词表

| 值 | 含义 | 例 |
|---|---|---|
| `kin` | 血缘 / 家庭 | 安德烈–老公爵、玛丽雅–安德烈 |
| `marriage` | 夫妻（含再婚） | 皮埃尔–娜塔莎、尼古拉–玛丽雅 |
| `courtship` | 恋爱 / 求婚 / 订婚 | 安德烈–娜塔莎、尼古拉–宋尼雅 |
| `affair` | 私情 / 私奔企图 | 阿纳托里–娜塔莎、海伦–陶洛霍夫 |
| `friend` | 挚友 | 安德烈–皮埃尔 |
| `salon` | 社交圈 / 熟人 | 舍勒沙龙、裘丽的圈子 |
| `enemy` | 敌对 / 决斗 / 情敌 | 皮埃尔–陶洛霍夫、陶洛霍夫–尼古拉 |
| `service` | 军中共事 / 上下级 | 库图佐夫–安德烈、杰尼索夫–尼古拉 |
| `patron` | 提携 / 依附 | 华西里公爵–保里斯 |
| `estate` | 经济 / 监护 / 继承 | 卡嘉–皮埃尔、老公爵–布莉恩 |

**phase.state 受控前缀**（`·` 前的一段）：
`初见` `疏远` `靠近` `求婚` `订婚` `受阻` `悔婚` `决裂` `和解` `结婚` `丧偶` `死别` `反目` `互助`

## 10. 其余数据文件

```js
// families.js
{ id:"rostov", name:"罗斯托夫家", color:"#b8552e", head:"ilya",
  members:["ilya","natasha",...], marriages:["natasha→bezukhov"] }

// places.js
"童山": { lat:54.30, lng:36.30, modern:"俄国图拉省（小说庄园，示意坐标）",
          kind:"estate", ru:"Лысые Горы" }
// kind 受控：estate | city | battlefield | other

// battles.js
{ id:"b-borodino", name:"鲍罗金诺会战", year:1812, month:8, day:26,
  place:"鲍罗金诺", phase:[{name:"舍瓦尔季诺",desc:"…"}],
  russian:"库图佐夫", french:"拿破仑", chars:["andrei","pierre"] }

// routes.js
{ id:"r-french-retreat", kind:"retreat",   // march | retreat | person
  who:null, pts:[{y:1812,m:9,p:"莫斯科"},{y:1812,m:11,p:"别列津纳"}], color:"#4a5a8c" }

// themes.js
{ id:"history", title:"历史由谁推动", question:"…", color:"#c9a227",
  status:"partial",                        // open | partial | answered
  nodes:[{ ch:"1-1-01", role:"提出" }] }   // role 受控：提出 | 推进 | 解答

// arcs.js
{ id:"andrei", who:"andrei",
  stages:[{ label:"荣耀", from:1805, to:1805, ch:["1-2-16"], desc:"…" }] }

// glossary.js
{ id:"hussar", kind:"term", name:"骠骑兵",
  desc:"…≤80 字…", events:["e-nikolai-bridge"] }
// kind 受控：rank（军衔）| title（贵族称谓）| term（术语）| order（团体）
```

## 11. lint 规则摘要（scripts/lint_data.js）

1. **引用完整性**：chapters.chars / events.ch / events.chars / events.place / events.theme /
   events.battle / relations.a,b / relations.phases.ev / characters.family / glossary.events 全部可解析；
2. **词表**：§7–§10 全部受控值越界即报错；
3. **结构调整**：`structure.js` 必须为 17 部 361 章；
4. **章节覆盖**：`chapters.js` 必须覆盖全部 361 个 id（Phase 1 起启用）；
5. **版权门禁**：`gist`>60、`summary`>140、`bio`>80、`history`>120、`desc`>80 报错；
   引号包裹片段 >20 字报错；出现 `quote` 字段直接报错；
6. **别名查重**：`aliases` 跨人物不得重复；
7. **关系约束**：`a`≠`b`；`(a,b)` 唯一；phases 按年升序且落在 from/to 内；
8. **事件日期**：month 为 1–12 的整数；非空 day 必须为有效日数且有 month。粗粒度的同年同月可包含多地活动，不作为冲突判据；
9. **`flag:"verify"` 汇总**输出清单（不算错误）。

## 12. trust_guard 双模式（scripts/trust_guard.js）

- `corpus/ch/` 无文件 → **弱校验**：实际执行 `lint_data.js` 并传递失败状态，明确标注未做语料核查；
- 有文件 → **强校验**：先执行相同的结构门禁，再核对章节人物称名、人物章节索引、事件人物称名、关系边同章共现；
- 匹配使用登记称名，最长词优先；纯泛称及多人物共享称名不计作精确命中。精确称名只表示文本可见，不证明人物身份或在场；
- 结构错误退出非零；歧义、称名缺失和索引缺口列为人工待核，不将它们包装成“准确率 100%”；
- `ctx.py` 的动作线索须绑定查询人物，转述、领属与宾语位置不能直接升级为出场；启发式仍须人工复核；
- `check_gists.py` 的结构缺陷退出 1，称名反查差异为待核；`check_names.py` 的 A/B 类问题退出 1，C 类单独列明。两者无语料均退出 2；
- 语料永不提交（`corpus/` 已 gitignore）；校验报告可入库，但必须区分结构通过、机器线索和人工审定。
