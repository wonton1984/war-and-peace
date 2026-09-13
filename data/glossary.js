// data/glossary.js — 名物：军衔 / 贵族称谓 / 术语 / 团体
// kind: rank | title | term | order
const GLOSSARY = [
  // ————— 军衔 rank —————
  { id:"g-yunker", kind:"rank", name:"士官生", desc:"贵族子弟入伍的起点军衔，尼古拉以此身份进入保罗格勒骠骑兵团。" },
  { id:"g-poruchik", kind:"rank", name:"中尉", desc:"骑兵连一级的下级军官，安德烈在申格拉本以中尉衔随巴格拉基昂行动。" },
  { id:"g-shtabs", kind:"rank", name:"上尉", desc:"连长一级，土申即以炮兵上尉统带四门炮。" },
  { id:"g-polkovnik", kind:"rank", name:"上校", desc:"团长军衔，安德烈在鲍罗金诺以前任团长的身份带一个团。" },
  { id:"g-general", kind:"rank", name:"将军", desc:"巴格拉基昂、别尼生等人的军衔，是宫廷与军队之间的接点。" },
  { id:"g-feldmarshal", kind:"rank", name:"元帅", desc:"库图佐夫的军衔，1812 年他以此统率全部俄军。" },

  // ————— 贵族称谓 title —————
  { id:"g-knyaz", kind:"title", name:"公爵", desc:"俄语「князь」，在俄国是古老世家的标志，未必富有；保尔康斯基、库拉金两家的头衔。" },
  { id:"g-graf", kind:"title", name:"伯爵", desc:"俄语「граф」，别祖霍夫、罗斯托夫两家的头衔。老别祖霍夫的巨额财产即随此爵位传承。" },
  { id:"g-knyazhna", kind:"title", name:"公爵小姐", desc:"公爵之女的称谓，玛丽雅与海伦均以此身份出场。" },
  { id:"g-grafinya", kind:"title", name:"伯爵夫人", desc:"伯爵夫人，罗斯托夫伯爵夫人与海伦婚后均用此称。" },
  { id:"g-ober", kind:"title", name:"宫廷女官", desc:"皇后的侍从女官，安娜·舍勒以此身份立足彼得堡社交界。" },
  { id:"g-kamer", kind:"title", name:"侍从官", desc:"宫廷荣誉职衔，阿纳托里等贵族子弟常挂此空衔。" },

  // ————— 术语 term —————
  { id:"g-hussar", kind:"term", name:"骠骑兵", desc:"轻骑兵，以华丽制服与放肆作风著称。尼古拉与杰尼索夫服役的兵种。" },
  { id:"g-cossack", kind:"term", name:"哥萨克", desc:"边疆骑兵，1812 年游击战的主力，季洪与拉夫鲁施卡一类人物的来处。" },
  { id:"g-adiutant", kind:"term", name:"副官", desc:"将军身边的侍从军官，安德烈与聂斯维茨基都曾任此职——离权力最近的位置。" },
  { id:"g-flank", kind:"term", name:"侧翼进军", desc:"库图佐夫放弃莫斯科后隐蔽南下的战略机动，托尔斯泰认为史家高估了它的谋略性。" },
  { id:"g-guerrilla", kind:"term", name:"游击战", desc:"1812 年由正规军小队与农民自发组成的袭扰战，托尔斯泰视之为「全民战争」的证据。" },
  { id:"g-furlough", kind:"term", name:"休假", desc:"军官的短期返乡，尼古拉两次休假分别引出了赌局与打猎两条重要支线。" },
  { id:"g-duel", kind:"term", name:"决斗", desc:"贵族以荣誉为名的私斗，皮埃尔与陶洛霍夫一战是他一生的转折点。" },
  { id:"g-obrok", kind:"term", name:"代役租", desc:"农奴向地主缴纳的货币地租，皮埃尔在基辅庄园的改革即试图减轻此项负担。" },
  { id:"g-manifesto", kind:"term", name:"告示", desc:"拉斯托普庆在莫斯科张贴的法语禁令与传单，是战时狂热的产物。" },
  { id:"g-revelation", kind:"term", name:"《启示录》", desc:"皮埃尔用来推算拿破仑数字之谜的书，一度让他相信自己负有使命。" },
  { id:"g-masonry", kind:"term", name:"共济会", desc:"以自我完善与博爱为纲领的秘密团体，皮埃尔在托尔若克受其感召而加入。" },
  { id:"g-holy", kind:"term", name:"神亲", desc:"拜访童山的朝圣者，玛丽雅从他们身上获得宗教的慰藉。" },

  // ————— 团体 order —————
  { id:"g-salon", kind:"order", name:"舍勒沙龙", desc:"彼得堡最著名的政治沙龙。发言有固定流程，客人有固定座次，一切都被女主人安排好。" },
  { id:"g-paul", kind:"order", name:"保罗格勒团", desc:"尼古拉与杰尼索夫服役的骠骑兵团，1812 年随军东撤并在奥斯特罗夫诺作战。" },
  { id:"g-guards", kind:"order", name:"近卫军", desc:"皇帝身边的精锐部队，调入近卫军是安娜·米哈伊洛夫娜替儿子奔走的第一目标。" },
  { id:"g-nobility", kind:"order", name:"贵族代表", desc:"选出的地方贵族职务，伊利亚·罗斯托夫以此身份参与莫斯科的事务。" },
];

if (typeof module !== "undefined") module.exports = { GLOSSARY };
