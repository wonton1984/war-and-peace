// data/themes.js — 主题线（议论章不污染事件列表，单列 type:"essay"）
// status: open | partial | answered；nodes[].role: 提出 | 推进 | 解答
const THEMES = [
  { id:"history", title:"历史由谁推动", color:"#c9a227", status:"partial",
    question:"拿破仑、亚历山大，还是千万个无名者的偶然行动？",
    nodes:[
      { ch:"1-1-02", role:"提出", note:"沙龙里为拿破仑的「伟大」争辩" },
      { ch:"3-1-01", role:"推进", note:"史论：欧洲民族自西向东推进" },
      { ch:"3-2-01", role:"推进", note:"鲍罗金诺的混沌：命令无法抵达" },
      { ch:"3-3-01", role:"推进", note:"放弃莫斯科：谁都没下过这个命令" },
      { ch:"4-2-01", role:"推进", note:"塔鲁季诺：库图佐夫的「忍耐与时间」" },
      { ch:"5-2-01", role:"解答", note:"尾声第二部：必然性与自由意志" },
    ]},
  { id:"freedom", title:"自由与必然", color:"#6f8f7a", status:"answered",
    question:"人的行为有多少是自己决定的？",
    nodes:[
      { ch:"2-2-01", role:"提出", note:"皮埃尔入共济会：自我完善的许诺" },
      { ch:"2-2-07", role:"推进", note:"日记：努力记录却屡屡失败" },
      { ch:"4-1-12", role:"推进", note:"被俘：失去一切自由反而得安宁" },
      { ch:"4-2-11", role:"推进", note:"普拉东：顺流而下的船" },
      { ch:"5-2-06", role:"解答", note:"自由意识与必然性法则" },
    ]},
  { id:"death", title:"死亡与顿悟", color:"#6e8ca0", status:"answered",
    question:"人在死前能看见什么？",
    nodes:[
      { ch:"1-3-16", role:"提出", note:"奥斯特里茨：仰望天空，荣誉是空的" },
      { ch:"1-1-25", role:"推进", note:"小公爵夫人临产：死亡第一次近身" },
      { ch:"4-1-15", role:"推进", note:"安德烈临终：爱是灵魂的本质" },
      { ch:"4-1-16", role:"解答", note:"死：醒来的一刻" },
    ]},
  { id:"marriage", title:"婚姻与幸福", color:"#b8552e", status:"answered",
    question:"婚姻是交易、牢笼，还是归宿？",
    nodes:[
      { ch:"1-1-06", role:"提出", note:"安德烈论婚姻与女人：别结婚" },
      { ch:"1-3-01", role:"推进", note:"皮埃尔–海伦：一桩被安排的婚事" },
      { ch:"2-3-24", role:"推进", note:"安德烈–娜塔莎：一年之约" },
      { ch:"2-5-16", role:"推进", note:"悔婚：承诺的崩坏" },
      { ch:"5-1-10", role:"解答", note:"娜塔莎的转变：为妻为母的满足" },
    ]},
  { id:"people", title:"贵族与人民", color:"#8a7f6a", status:"partial",
    question:"谁才是这场战争的真正承担者？",
    nodes:[
      { ch:"1-1-22", role:"提出", note:"童山：农奴改革的两难" },
      { ch:"2-2-10", role:"推进", note:"皮埃尔解放农奴：好意与失败" },
      { ch:"3-2-35", role:"推进", note:"鲍罗金诺的士兵：真正在打仗的人" },
      { ch:"4-1-13", role:"推进", note:"普拉东：士兵的整全生命" },
      { ch:"4-3-01", role:"解答", note:"游击战：战争的全民性" },
    ]},
  { id:"vanity", title:"虚荣与真实", color:"#9c8f7a", status:"answered",
    question:"上流社会的体面与人心的真实，哪个更有力量？",
    nodes:[
      { ch:"1-1-01", role:"提出", note:"舍勒沙龙：一场精心编排的表演" },
      { ch:"2-3-14", role:"推进", note:"舞会：娜塔莎的真实对上礼节的空洞" },
      { ch:"3-1-06", role:"推进", note:"海伦改宗：体面下的算计" },
      { ch:"4-2-04", role:"解答", note:"库图佐夫：不表演的人赢了" },
    ]},
];

if (typeof module !== "undefined") module.exports = { THEMES };
