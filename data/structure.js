// data/structure.js — 卷/部/章骨架
// 底本实测：草婴译《战争与和平》（读客经典文库 / 江苏凤凰文艺 2019，ISBN 9787559433602）
// 全书 17 部 361 章（book 5 = 尾声）
const STRUCTURE = [
  { book:1, title:"第一卷", parts:[
    { part:1, chapters:25 },
    { part:2, chapters:21 },
    { part:3, chapters:19 },
  ]},
  { book:2, title:"第二卷", parts:[
    { part:1, chapters:16 },
    { part:2, chapters:21 },
    { part:3, chapters:26 },
    { part:4, chapters:13, flag:"verify" },   // 部分公开目录记 12 章
    { part:5, chapters:22 },
  ]},
  { book:3, title:"第三卷", parts:[
    { part:1, chapters:23 },
    { part:2, chapters:39 },
    { part:3, chapters:34 },
  ]},
  { book:4, title:"第四卷", parts:[
    { part:1, chapters:16 },
    { part:2, chapters:19 },
    { part:3, chapters:19 },
    { part:4, chapters:20 },
  ]},
  { book:5, title:"尾声", epilogue:true, parts:[
    { part:1, chapters:16 },
    { part:2, chapters:12, flag:"verify" },   // 史论部
  ]},
];

// 部标题（用于界面展示）
const PART_TITLES = {
  "1-1":"舍勒沙龙与童山", "1-2":"申格拉本", "1-3":"奥斯特里茨",
  "2-1":"尼古拉回乡与赌局", "2-2":"共济会与乡村", "2-3":"彼得堡·舞会与求婚",
  "2-4":"猎归夜谈", "2-5":"悔婚与决裂",
  "3-1":"1812 入侵", "3-2":"鲍罗金诺", "3-3":"莫斯科大火",
  "4-1":"彼得堡与被俘", "4-2":"普拉东·卡拉塔耶夫", "4-3":"法军撤退", "4-4":"彼嘉之死与别列津纳",
  "5-1":"婚后生活", "5-2":"历史哲学",
};

// 展开为扁平章节表（供 lint 与引擎用）
const ALL_CHAPTERS = (() => {
  const out = [];
  let seq = 0;
  STRUCTURE.forEach(b => b.parts.forEach(p => {
    for (let c = 1; c <= p.chapters; c++) {
      out.push({ id:`${b.book}-${p.part}-${String(c).padStart(2, "0")}`,
                 book:b.book, part:p.part, ch:c,
                 epilogue:!!b.epilogue, flag:p.flag || null, seq:++seq });
    }
  }));
  return out;
})();

const TOTAL_CHAPTERS = ALL_CHAPTERS.length;   // 361

if (typeof module !== "undefined") module.exports = { STRUCTURE, PART_TITLES, ALL_CHAPTERS, TOTAL_CHAPTERS };
