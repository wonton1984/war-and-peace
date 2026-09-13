// scripts/data_limits.js — 字数上限的单一事实源
// lint_data.js、merge_proposals.js 与 Python 管线 jsio.py 共用；改上限只改这里。
"use strict";

module.exports = {
  gist: 60,      // 章节卡概述
  summary: 140,  // 事件卡概述
  bio: 80,       // 人物小传
  history: 120,  // 小说×史实对照
  desc: 80,      // 名物/战役/主题 描述
  quoteSpan: 20, // 引号内片段上限（版权门禁）
};
