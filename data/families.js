// data/families.js — 四大家族 + 谱系 + 联姻
// tree: {gen, of} 谱系层级；marriages: 跨家族联姻（画跨树连线）
const FAMILIES = [
  {
    id:"bezukhov", name:"别祖霍夫家", color:"#c9a227", head:"kirill",
    desc:"叶卡德琳娜朝的巨富之家。老伯爵的遗嘱把家产与爵位给了私生子，从此财富成了这个家唯一的话题。",
    members:["kirill","pierre","katya","helen","natasha"],
    tree:[
      { id:"kirill", gen:0, of:"bezukhov" },
      { id:"katya",  gen:1, of:"bezukhov", note:"表姐" },
      { id:"pierre", gen:1, of:"bezukhov" },
      { id:"helen",  gen:1, of:"kuragin", note:"嫁入" },
      { id:"natasha",gen:1, of:"rostov",  note:"再嫁入" },
    ],
    marriages:["helen→pierre","natasha→pierre"],
  },
  {
    id:"rostov", name:"罗斯托夫家", color:"#b8552e", head:"ilya",
    desc:"莫斯科的乐善好施之家。伯爵的慷慨与管家的手脚一起掏空了家业，最后靠儿子的劳作把日子重新撑起来。",
    members:["ilya","countess_r","vera","nikolai","natasha","petya","sophia"],
    tree:[
      { id:"ilya",       gen:0, of:"rostov" },
      { id:"countess_r", gen:0, of:"rostov" },
      { id:"vera",       gen:1, of:"rostov" },
      { id:"nikolai",    gen:1, of:"rostov" },
      { id:"natasha",    gen:1, of:"rostov" },
      { id:"petya",      gen:1, of:"rostov" },
      { id:"sophia",     gen:1, of:"rostov", note:"外甥女" },
      { id:"marya",      gen:1, of:"bolkonsky", note:"嫁入" },
    ],
    marriages:["marya→nikolai"],
  },
  {
    id:"bolkonsky", name:"保尔康斯基家", color:"#6e8ca0", head:"old_prince",
    desc:"童山的军人世家。老公爵的才智与暴政一起统治着庄园，儿女在压抑中长成了两种不同的人。",
    members:["old_prince","andrei","liza","marya","nikolushka"],
    tree:[
      { id:"old_prince", gen:0, of:"bolkonsky" },
      { id:"andrei",     gen:1, of:"bolkonsky" },
      { id:"liza",       gen:1, of:"bolkonsky", note:"长媳" },
      { id:"marya",      gen:1, of:"bolkonsky" },
      { id:"nikolushka", gen:2, of:"bolkonsky" },
    ],
    marriages:["liza→andrei","natasha→andrei(未成)"],
  },
  {
    id:"kuragin", name:"库拉金家", color:"#8c4a66", head:"vasily",
    desc:"把人际当棋局的宫廷之家。父亲铺路，儿女收网：美人、蠢货、浪荡子，各有各的不体面。",
    members:["vasily","kuragina","hippolyte","helen","anatole"],
    tree:[
      { id:"vasily",   gen:0, of:"kuragin" },
      { id:"kuragina", gen:0, of:"kuragin" },
      { id:"hippolyte",gen:1, of:"kuragin" },
      { id:"helen",    gen:1, of:"kuragin" },
      { id:"anatole",  gen:1, of:"kuragin" },
    ],
    marriages:["helen→pierre"],
  },
  {
    id:"druzh", name:"德鲁别茨科伊家", color:"#7a6f58", head:"anna_mikh",
    desc:"没落贵族。母亲用一切体面与不体面的办法替儿子敲门，儿子自己也很清楚该往哪扇门里走。",
    members:["anna_mikh","boris"],
    tree:[
      { id:"anna_mikh", gen:0, of:"druzh" },
      { id:"boris",     gen:1, of:"druzh" },
      { id:"julie",     gen:1, of:"rostov", note:"嫁入" },
    ],
    marriages:["julie→boris"],
  },
];

if (typeof module !== "undefined") module.exports = { FAMILIES };
