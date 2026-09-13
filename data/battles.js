// data/battles.js — 战役（含阶段拆分）
const BATTLES = [
  { id:"b-schongraben", name:"申格拉本", year:1805, month:11, day:16,
    place:"申格拉本",
    desc:"巴格拉基昂以四千人挡住法军主力，替库图佐夫争得撤退时间。",
    phase:[
      { name:"霍拉勃隆停战", desc:"缪拉误判兵力，提议停战，拿破仑撕毁协定" },
      { name:"土申的炮台", desc:"四门炮顶住主攻，土申事后反被责问" },
      { name:"尼古拉冲击", desc:"骑兵连首战，尼古拉负伤坠马" },
    ],
    russian:"巴格拉基昂", french:"缪拉", chars:["bagration","tushin","nikolai","andrei","murat"] },
  { id:"b-austerlitz", name:"奥斯特里茨（三皇会战）", year:1805, month:12, day:2,
    place:"奥斯特里茨",
    desc:"俄奥联军按计划进攻却落入拿破仑的陷阱，库图佐夫负伤，安德烈扛旗倒地。",
    phase:[
      { name:"军事会议", desc:"魏罗特的部署，库图佐夫在会上一言不发" },
      { name:"晨雾中的混乱", desc:"联军纵队脱节，法军抢占普拉岑高地" },
      { name:"安德烈倒下", desc:"扛旗冲锋，仰面看见高远的天空" },
      { name:"拿破仑巡视战场", desc:"对着安德烈说「这才是光荣的死」，安德烈听见的是空话" },
    ],
    russian:"库图佐夫", french:"拿破仑", chars:["andrei","kutuzov","napoleon","nikolai"] },
  { id:"b-borodino", name:"鲍罗金诺会战", year:1812, month:8, day:26,
    place:"鲍罗金诺",
    desc:"俄法两军六万余人伤亡的正面血战。没有胜者，但法军的锐气在这里被磨尽。",
    phase:[
      { name:"舍瓦尔季诺前哨", desc:"会战前两日的失守，托尔斯泰借此讽刺「阵地」的虚构" },
      { name:"巴格拉基昂凸角", desc:"反复易手的绞肉机，巴格拉基昂重伤" },
      { name:"拉耶夫斯基炮垒", desc:"皮埃尔以平民之身在场，目睹炮垒被夺又被夺回" },
      { name:"安德烈重伤", desc:"一颗霰弹在身边爆炸；邻床是刚被锯掉腿的阿纳托里" },
      { name:"库图佐夫的判断", desc:"向皇帝报告胜利，尽管俄军退却" },
    ],
    russian:"库图佐夫", french:"拿破仑", chars:["andrei","pierre","kutuzov","napoleon","bagration","dolokhov","anatole","denisov"] },
  { id:"b-tarutino", name:"塔鲁季诺与侧翼进军", year:1812, month:10,
    place:"塔鲁季诺",
    desc:"库图佐夫放弃莫斯科后南下截断法军退路，把战争拖进俄国人熟悉的节奏。",
    phase:[
      { name:"侧翼进军", desc:"孤注一掷的战略机动，托尔斯泰认为其意义被史家夸大" },
      { name:"塔鲁季诺会战", desc:"错过俘虏缪拉的机会，但打开反攻局面" },
    ],
    russian:"库图佐夫", french:"缪拉", chars:["kutuzov","murat","bennigsen"] },
  { id:"b-beresina", name:"别列津纳渡河", year:1812, month:11,
    place:"别列津纳",
    desc:"法军撤退途中的最后一场崩坏。冰河、残兵与被丢弃的辎重。",
    phase:[
      { name:"克拉斯诺耶追歼", desc:"俄军追及法军，库图佐夫与将领们意见相左" },
      { name:"渡河", desc:"混乱中强渡，落伍者被俘" },
    ],
    russian:"库图佐夫", french:"拿破仑", chars:["kutuzov","napoleon","pierre"] },
];

if (typeof module !== "undefined") module.exports = { BATTLES };
