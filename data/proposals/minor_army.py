# -*- coding: utf-8 -*-
# minor_army.py — 俄军（含在俄军/联军司令部任职的外籍出身者）将领与参谋类次要人物（简录，tier=minor）
# 译名一律照草婴译本：陶赫杜罗夫（非「多赫图罗夫」）、柯诺夫尼岑（非「科诺夫尼岑」）、威罗特（非「魏罗特」）、
#   普法尔、保卢奇、阿姆斐尔德、米肖、冯托尔、朗热隆、普尔杰贝歇夫斯基、布克斯赫弗登、奥斯吉尔曼-托尔斯泰伯爵。
# chapters 核对口径：逐条读 corpus/ch/ 正文，只收此人作为行动者出现在场（含被叙写在战场/会上行动）的章节；
#   纯被谈论、名单式点名（如 3-1-09 随驾顾问一串）、史论插叙（3-2-19 除外、3-2-33、4-3-19）、
#   作者注释（3-3-34、5-2-12）一律剔除。每条 chapters 中的章号都含「主名」原串，便于语料反查。
# 核实后不予收录的候选：
#   阿尔巴端奇（已在详录册，童山管家非军官）、巴克莱（已在册）、伏尔佐根（已在册）、斯塔尔（归 MinorCourt，
#     语料中亦只见「斯塔尔夫人」）、马克（12 章 23 次全是他人谈论与史论比喻，无一场面）、
#   斯坦因（被逐的文职政论家，随驾顾问）、符腾堡的叶夫盖尼亲王（仅 4-4-04 一次单点）、
#   威姆普芬／里赫顿斯坦／霍恩洛厄／谢德莫列茨基（均只在点名串里出现，未出场）。
# 「托里」一条已删除：语料中「托里」与「阿纳托里」「巴克莱·德·托里」互为局部串，
#   一旦入册，按人名字串自动抽取章节必然污染（阿纳托里 1—2 卷主场章节全被误挂）。
# flag:"verify" 含义：外籍出身而 faction 就近入 russian_army（奥国／普鲁士／瑞典／撒丁），
#   或军衔、身份细节、同一姓名是否同人尚待再核。

MINOR = [
    {"id":"konovnitsyn", "name":"柯诺夫尼岑", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"库图佐夫司令部值班将军",
     "bio":"总司令身边的值班将军，脸面刚毅俊美，菲里会上还敢向小姑娘挤挤眼。他从不制订作战计划，却总在战况最吃紧处指挥。",
     "chapters":["3-2-15","3-3-04","4-2-05","4-2-16","4-2-17","4-2-19","4-4-10","4-4-11"],
     "flag":None},

    {"id":"dokhturov", "name":"陶赫杜罗夫", "aliases":["陶霍杜罗夫"],
     "faction":"russian_army", "family":None,
     "title":"俄军将领（军指挥官）",
     "bio":"个儿矮小、最不引人注目的将领，公认见识不多。从奥斯特里茨的堤坝到斯摩棱斯克的街口，哪里局势最紧，他就在哪里收拢部队。",
     "chapters":["1-3-12","3-2-35","4-2-15","4-2-16","4-2-18"],
     "flag":None},

    {"id":"yermolov", "name":"叶尔莫洛夫", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"第一集团军参谋长",
     "bio":"主战派少壮将领的代表。鲍罗金诺他把功绩记在自己名下，又把勋章抛给先登土岗的士兵；塔鲁季诺他当众顶撞总司令，回头又催进攻。",
     "chapters":["3-2-32","3-2-35","3-3-03","3-3-04","3-3-21","4-2-04","4-2-07","4-2-15","4-2-19"],
     "flag":None},

    {"id":"miloradovich", "name":"米洛拉多维奇", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"奥斯特里茨第四纵队长、前卫将领",
     "bio":"脸色红润、留上翘小胡子的将领，在御前纵马勒缰、用法语表忠心。他自称无所畏惧，一心要截击溃退的法军，连报告信封里只装一张白纸。",
     "chapters":["1-3-12","1-3-15","4-2-07","4-2-19","4-4-04"],
     "flag":None},

    {"id":"rayevsky", "name":"拉耶夫斯基", "aliases":["拉耶夫斯基将军"],
     "faction":"russian_army", "family":None,
     "title":"俄军将领（鲍罗金诺中央阵地主官）",
     "bio":"魁伟的黑头发将军，鲍罗金诺全天守在后来以他命名的那个土岗上。菲里会上他主张死战，塔鲁季诺日又站在叶尔莫洛夫旁边听总司令取笑。",
     "chapters":["3-2-35","3-3-04","4-2-07"],
     "flag":None},

    {"id":"platov", "name":"普拉托夫", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"哥萨克统领",
     "bio":"带哥萨克独立行动的老统领，侦察、截辎、追败兵样样靠前。战争后期他与叶尔莫洛夫等人按捺不住要切断法军，逼得总司令处处收着。",
     "chapters":["2-2-16","4-2-19"],
     "flag":None},

    {"id":"tol", "name":"冯托尔", "aliases":["冯托尔大尉"],
     "faction":"russian_army", "family":None,
     "title":"侍从武官（大尉）",
     "bio":"奥斯特里茨败退时恰好路过的侍从大尉，扶皇帝跨过壕沟，又在苹果树旁说了半日话；尼古拉远远瞧着，悔得心里发疼。",
     "chapters":["1-3-18"],
     "flag":"verify"},

    {"id":"pfuhl", "name":"普法尔", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"普鲁士军事理论家、亚历山大一世的顾问",
     "bio":"设计德里萨阵地的普鲁士理论家，穿一身做工很差的俄国将军服。谁反对他的计划他就跟自己人吵，被托尔斯泰看作德国空想军人的标本。",
     "chapters":["3-1-10","3-1-11"],
     "flag":"verify"},

    {"id":"paulucci", "name":"保卢奇", "aliases":["保卢奇侯爵"],
     "faction":"russian_army", "family":None,
     "title":"侍从武官长",
     "bio":"说话大胆果断的流亡侍从武官长，随皇帝视察工事，又在御前当着皇上痛斥筑阵的建议、主张进攻；不懂德语，只好用法语同伏尔佐根理论。",
     "chapters":["3-1-10","3-1-11"],
     "flag":"verify"},

    {"id":"tschernyschew", "name":"契尔内歇夫", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"皇帝侍从武官",
     "bio":"德里萨行辕里当值的皇帝侍从武官。安德烈公爵前来报到，由他接待；他闲坐着看书，随口说出皇上已经疑心那座工事无用。",
     "chapters":["3-1-10","3-1-11"],
     "flag":None},

    {"id":"armfeld", "name":"阿姆斐尔德", "aliases":["阿姆斐尔德将军"],
     "faction":"russian_army", "family":None,
     "title":"随驾顾问将领（瑞典出身）",
     "bio":"御前会上第一个发言的外籍顾问：主张另择一处新阵地，理由却说不出来，只为表明自己也有主张。拿破仑把他归进「阴谋家」一栏。",
     "chapters":["3-1-11"],
     "flag":"verify"},

    {"id":"michaud", "name":"米肖", "aliases":["米肖上校"],
     "faction":"russian_army", "family":None,
     "title":"军事工程师、上校",
     "bio":"陪皇帝巡视德里萨工事并替它辩护的撒丁出身上校；莫斯科弃守后，库图佐夫派他专程去报信。他不懂俄语，却自称外国人而有俄国心。",
     "chapters":["3-1-10","3-1-11","4-1-03"],
     "flag":None},

    {"id":"dolgorukov", "name":"陶尔戈鲁科夫", "aliases":["陶尔戈鲁科夫公爵","陶尔戈鲁基公爵"],
     "faction":"russian_army", "family":None,
     "title":"侍从武官长",
     "bio":"奥洛莫乌茨的侍从武官长，安德烈带保里斯去他那里谋差事。奥斯特里茨前夜他力主决战，又陪法国军使去敌营，还嘱尼古拉向皇上呈报军情。",
     "chapters":["1-3-09","1-3-10","1-3-11","1-3-13","1-3-17"],
     "flag":"verify"},

    {"id":"langeron", "name":"朗热隆", "aliases":["朗热隆将军","朗热隆伯爵"],
     "faction":"russian_army", "family":None,
     "title":"法裔俄军将领（纵队长）",
     "bio":"奥斯特里茨军事会议上挂着微妙笑容、只管转鼻烟壶的将领，私下把那套部署叫作「一堂地理课」。会战后他的残部挤在奥格斯特的堤坝上。",
     "chapters":["1-3-12","1-3-15","1-3-18"],
     "flag":"verify"},

    {"id":"przybyszewski", "name":"普尔杰贝歇夫斯基", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"俄军将领（纵队长）",
     "bio":"不亢不卑的纵队长，会上用手罩着耳朵听威罗特宣读部署。奥斯特里茨一役他同自己那个军一起放下了武器，莫斯科便传他背信弃义。",
     "chapters":["1-3-12","1-3-15","1-3-18"],
     "flag":"verify"},

    {"id":"weyroter", "name":"威罗特", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"奥国将军（联军作战计划起草人）",
     "bio":"前来接替阵亡的施密特的奥国将军，奥斯特里茨那套烦琐部署出自他手：半夜在库图佐夫行辕宣读，把几个纵队派往互相矛盾的方向。",
     "chapters":["1-2-13","1-3-12"],
     "flag":"verify"},

    {"id":"schmidt", "name":"施密特", "aliases":["施密特将军"],
     "faction":"russian_army", "family":None,
     "title":"奥国将军",
     "bio":"克雷姆斯城下这一战，安德烈公爵跟在他身边：坐骑受伤、手臂擦伤。捷报送进奥国宫廷，朝廷却只怪俄军听凭这位受人爱戴的将军战死。",
     "chapters":["1-2-09"],
     "flag":"verify"},

    {"id":"buxhowden", "name":"布克斯赫弗登", "aliases":["布克斯赫弗登伯爵"],
     "faction":"russian_army", "family":None,
     "title":"奥国将领",
     "bio":"淡黄头发的高个奥国将领，奥斯特里茨军事会议上背靠墙盯着蜡烛，一副并没有在听的神态；会前他还是俄军引为靠山的会师对象。",
     "chapters":["1-3-12"],
     "flag":"verify"},

    {"id":"uvarov", "name":"乌瓦罗夫", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"俄军骑兵将领",
     "bio":"鲍罗金诺日奉命迂击法军右翼的骑兵主官，那场佯攻与中心战场几乎无关；菲里会上他坐在发烧的巴克莱旁边，打着手势低声报告前线情形。",
     "chapters":["3-2-35","3-3-04"],
     "flag":"verify"},

    {"id":"ostermann", "name":"奥斯吉尔曼-托尔斯泰伯爵", "aliases":["奥斯吉尔曼托尔斯泰伯爵"],
     "faction":"russian_army", "family":None,
     "title":"俄军师长",
     "bio":"维捷布斯克方向的上级：先派副官送来急令，自己又带随从来到骑兵连后面与团长谈几句。尼古拉未等命令就冲锋，反被召去受谢并许以勋章。",
     "chapters":["3-1-14","3-1-15"],
     "flag":"verify"},

    {"id":"porkhovitinov", "name":"波尔霍维季诺夫", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"总司令部传令军官",
     "bio":"前线派出的干练军官，雨夜里换了两回马跑了三十俄里赶到列塔舍夫卡，午夜把法军已占福明斯科耶的报告当面交给值班将军。",
     "chapters":["4-2-15","4-2-16","4-2-17"],
     "flag":None},

    {"id":"shcherbinin", "name":"谢尔比宁", "aliases":[],
     "faction":"russian_army", "family":None,
     "title":"司令部副官",
     "bio":"司令部的年轻副官：鲍罗金诺日他从左翼飞马回报，库图佐夫看他的脸色便知消息不好；塔鲁季诺夜里又是他摸黑点烛接了前线的报告。",
     "chapters":["3-2-35","4-2-16"],
     "flag":"verify"},

    {"id":"orlov", "name":"奥尔洛夫", "aliases":["奥尔洛夫伯爵"],
     "faction":"russian_army", "family":None,
     "title":"塔鲁季诺前线分队长",
     "bio":"塔鲁季诺夜唯一准时到位的分队长。他信了一名波兰士官的话，放两团哥萨克去劫缪拉；扑空后独自进攻，倒是真缴到大炮与上千俘虏。",
     "chapters":["4-2-06","4-2-07"],
     "flag":"verify"},

    {"id":"grekov", "name":"格列科夫", "aliases":["格列科夫少将"],
     "faction":"russian_army", "family":None,
     "title":"哥萨克少将",
     "bio":"奉奥尔洛夫伯爵之命带两团哥萨克，随那名波兰士官去劫法军统帅的行辕，白跑一场；塔鲁季诺这一仗真正出力的只有他们这一队人。",
     "chapters":["4-2-06"],
     "flag":None},

    {"id":"baghout", "name":"巴戈乌特", "aliases":["巴戈乌特将军"],
     "faction":"russian_army", "family":None,
     "title":"俄军军长",
     "bio":"塔鲁季诺会战中被托里在树林里找到的老将：照命令他早该与奥尔洛夫的哥萨克会合，天大亮却仍停在林里，因此被当面痛斥。",
     "chapters":["4-2-06"],
     "flag":"verify"},

    {"id":"constantine", "name":"康斯坦丁亲王", "aliases":["康斯坦丁·巴夫洛维奇亲王"],
     "faction":"court", "family":None,
     "title":"皇弟、近卫军指挥官",
     "bio":"皇帝的胞弟，军中靠他转信也算一条门路。1812年末他跟到维尔诺，又通知库图佐夫：皇上对我军战绩微小、行动迟缓深为不满。",
     "chapters":["4-4-10"],
     "flag":None},

    {"id":"volkonsky", "name":"伏尔康斯基公爵", "aliases":[],
     "faction":"court", "family":None,
     "title":"皇帝行辕长官",
     "bio":"随御营主持行辕的公爵：德里萨的御前会上他跟在皇帝身后入室听议；莫斯科弃守的正式文书，也是他在圣诞祈祷中被叫出教堂接下的。",
     "chapters":["3-1-11","4-1-02","4-4-10"],
     "flag":None},
]
