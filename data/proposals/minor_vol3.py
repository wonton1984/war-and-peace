# -*- coding: utf-8 -*-
# 第三卷（3-1 ~ 3-3，96 章）简录人物补缺提案
# 口径：本人在场景中有在场行动或对白（含静态在场）才收；转述、书信、旁注不算。
# 查名一律用 python3 scripts/ctx.py <人名> [章id] --present / --chapters 核过。
# 说明：德萨尔 已由 minor_vol4.py 收录（同名冲突，vol3 在场章 3-1-08/3-2-02/3-2-04 已并入其条目）；
#       别洛娃 由 MinorVol4 让入本文件（下方首条，faction 沿用 rostov：她是罗斯托夫家的寄生老小姐）。
MINOR = [
    {"id": "belova", "name": "别洛娃", "aliases": [], "faction": "rostov",
     "family": "rostov", "title": "长住罗斯托夫家的老小姐（亦为奥特拉德诺耶邻居）",
     "bio": "长住罗斯托夫家的老小姐，耳朵背，是客厅里一件少不得的旧摆设。圣彼得节后从奥特拉德诺耶来莫斯科朝圣，拉着病中的娜塔莎斋戒礼拜；晚年陪老伯爵夫人摆牌阵、说闲话。",
     "chapters": ["2-4-08", "3-1-17", "5-1-09", "5-1-12", "5-1-13"], "flag": None},
    # ————— 平民 / 市民 / 农民 —————
    {"id": "ferapontov", "name": "费拉邦托夫", "aliases": [], "faction": "folk",
     "family": None, "title": "斯摩棱斯克的旅店主人（商人）",
     "bio": "斯摩棱斯克开旅店兼面粉铺的商人，阿尔巴端奇常在他家投宿。法军炮击焚城，他把铺子里的面粉丢给士兵，又亲手点火烧掉自家房产。",
     "chapters": ["3-2-04"], "flag": None},

    {"id": "malasha", "name": "玛拉莎", "aliases": [], "faction": "folk",
     "family": None, "title": "菲里村农家的孙女",
     "bio": "菲里村农民家的六岁小孙女。军事会议就在她家正房开，她躲在炕上，把库图佐夫叫作爷爷，看他同别尼生争执，散会后才溜下炕去吃饭。",
     "chapters": ["3-3-04"], "flag": None},

    {"id": "makar", "name": "玛卡尔", "full": "玛卡尔·阿历克赛伊奇", "aliases": [], "faction": "folk",
     "family": None, "title": "巴兹杰耶夫的弟弟（半疯老人）",
     "bio": "巴兹杰耶夫的弟弟，酗酒成癖的半疯老人，独住在亡兄那座封了书房的空宅里。皮埃尔潜居时他抢走手枪乱嚷，次日又举枪瞄准法国人。",
     "chapters": ["3-3-18", "3-3-27", "3-3-28"], "flag": None},

    {"id": "vereshchagin", "name": "魏列夏金", "aliases": [], "faction": "folk",
     "family": None, "title": "莫斯科商人之子",
     "bio": "莫斯科酒店老板的儿子。他自撰并传抄一张文告获罪下狱，拉斯托普庆为平众怒把他交给人群，他死在士兵的刀背与乱拳之下。",
     "chapters": ["3-3-25"], "flag": None},

    {"id": "vereshchagin_sr", "name": "魏列夏金（老商人）", "aliases": [], "faction": "folk",
     "family": None, "title": "莫斯科酒店老板",
     "bio": "莫斯科石桥旁开酒店的商人，白发长眉、脸色红润的小老头。儿子获罪后他四处求情，皮埃尔在卫戍司令的接待室里打量过他。",
     "chapters": ["3-3-10"], "flag": None},

    {"id": "ivan_sidorich", "name": "伊凡·西多雷奇", "aliases": [], "faction": "folk",
     "family": None, "title": "莫斯科商人",
     "bio": "中央商场的瘦商人，名下有三大爿铺子、十万卢布的货。士兵闯进商场抢掠，他反倒说军队一走谁也保不住，任人拿算了。",
     "chapters": ["3-3-21"], "flag": None},

    # ————— 俄军 —————
    {"id": "kaisarov", "name": "凯萨罗夫", "aliases": ["安德烈·凯萨罗夫"], "faction": "russian_army",
     "family": None, "title": "库图佐夫的副官",
     "bio": "库图佐夫的副官。鲍罗金诺战前夜，他把阵地与部署指给皮埃尔看；库图佐夫在土岗上口授明日进攻的命令，执笔者也是他。",
     "chapters": ["3-2-22", "3-2-35", "3-3-04"], "flag": None},

    {"id": "schneider", "name": "施耐德", "aliases": [], "faction": "russian_army",
     "family": None, "title": "库图佐夫的副官",
     "bio": "库图佐夫的副官。菲里会议散后，他深夜来劝总司令休息，被老人用一句吃马肉的狠话顶了回去。",
     "chapters": ["3-3-04"], "flag": None},

    {"id": "sevastyanich", "name": "安德烈·谢瓦斯基扬内奇", "aliases": [], "faction": "russian_army",
     "family": None, "title": "保罗格勒团骑兵大尉",
     "bio": "保罗格勒团的骑兵大尉。奥斯特罗夫诺之役，尼古拉提议冲下山去砍法军龙骑兵，他应声附议；这一冲为尼古拉赢得圣乔治勋章。",
     "chapters": ["3-1-15"], "flag": None},

    # ————— 宫廷 / 社会 —————
    {"id": "asch", "name": "阿舒男爵", "aliases": ["阿舒"], "faction": "court",
     "family": None, "title": "斯摩棱斯克省长",
     "bio": "斯摩棱斯克的省长男爵。阿尔巴端奇奉老公爵之命登门问讯，他只说照上级命令办事，塞下一纸巴克莱的训令便匆匆打发人走。",
     "chapters": ["3-2-04"], "flag": None},

    {"id": "stein", "name": "斯坦因", "aliases": ["斯坦因男爵"], "faction": "court",
     "family": None, "title": "前普鲁士大臣（俄皇顾问）",
     "bio": "被本国驱逐、转而为亚历山大出谋划策的普鲁士前大臣。他在德里萨行辕的随驾之列，御前开议时随伏尔康斯基公爵一同入室。",
     "chapters": ["3-1-09", "3-1-11"], "flag": None},

    {"id": "jobert", "name": "若贝尔先生", "aliases": ["若贝尔"], "faction": "court",
     "family": None, "title": "耶稣会教士",
     "bio": "出入海伦沙龙的耶稣会教士，白发乌眼、风度翩翩。他引海伦改宗天主教，又替她论证她与皮埃尔的婚姻并无约束。",
     "chapters": ["3-3-06"], "flag": None},

    {"id": "glinka", "name": "格林卡", "aliases": [], "faction": "court",
     "family": None, "title": "《俄国信使报》发行人",
     "bio": "《俄国信使报》的发行人、作家。斯洛博达宫的贵族会上他起立发言，主张以恶制恶，人群里有人应和。",
     "chapters": ["3-1-22"], "flag": None},

    # ————— 法军 —————
    {"id": "beausset", "name": "波塞", "aliases": [], "faction": "french_army",
     "family": None, "title": "法国皇宫总监",
     "bio": "拿破仑的皇宫总监。鲍罗金诺前夜他从巴黎带来皇后所赠的罗马王画像，行礼献画；会战当天又斗胆请皇帝进膳，被摇头挡回。",
     "chapters": ["3-2-26", "3-2-29", "3-2-34"], "flag": None},

    {"id": "fabvier", "name": "法布维埃", "aliases": [], "faction": "french_army",
     "family": None, "title": "法军上校",
     "bio": "从西班牙前线赶回的法军上校。鲍罗金诺前夜他到瓦卢耶瓦行营，向拿破仑报告萨拉曼卡一役中部队的忠勇，皇帝只说要在莫斯科挽回。",
     "chapters": ["3-2-26"], "flag": None},

    {"id": "castres", "name": "德·卡斯特", "aliases": [], "faction": "french_army",
     "family": None, "title": "达武的副官",
     "bio": "达武元帅的副官。巴拉歇夫被扣在棚屋里，由他把人领到住处；达武限令这位俄国将军只能同他一个人说话。",
     "chapters": ["3-1-05"], "flag": None},

    {"id": "turenne", "name": "蒂雷纳", "aliases": [], "faction": "french_army",
     "family": None, "title": "拿破仑的侍从",
     "bio": "拿破仑身边的侍从。巴拉歇夫被扣四天后，是他来传话皇帝愿见；他又把人领进挤满将军与波兰贵族的接待室候见。",
     "chapters": ["3-1-05", "3-1-06"], "flag": None},

    {"id": "titville", "name": "蒂特维尔", "aliases": ["雷劳思·蒂特维尔", "雷劳恩·蒂特维尔"],
     "faction": "french_army", "family": None, "title": "拿破仑的译员",
     "bio": "拿破仑身边的译员。拉夫鲁施卡被带来问话，由他把那哥萨克仆役的自夸译给皇帝听；进莫斯科前拿破仑又召他到波克朗山。",
     "chapters": ["3-2-07", "3-3-19"], "flag": None},
]
