# -*- coding: utf-8 -*-
# MinorCourt：宫廷／外交／社交圈 + 少量与沙龙线交叠的军官，次要人物简录提案
# 译名一律依草婴译本；bio 全部自撰概述（不抄底本措辞），每条 ≤80 字。
# chapters 已用 scripts/ctx.py 逐名核对「真出场」；flag 三值：mentioned=仅被提及未正面出场，indexPend=出场属实但该章归属保守，verify=译名/出身待核。
# 核对记录：
#   · 普法尔归 MinorArmy（pfuhl 已在册）；莫特玛子爵(mortemart)、科兰古(caulaincourt)、巴拉歇夫(balashov)
#     已在 characters.js，本提案不重复收录。
#   · 「拉姆」经核对是「瓦格拉姆／卡拉姆辛」的子串，并非人名，未收录。
#   · 玛丽雅·费奥多罗夫娜、伊丽莎白·阿列克谢耶夫娜在底本中作「玛丽雅太后／皇太后」「伊丽莎白皇后」
#     （4-1-01 只叙述其行为，5-2-12 注文明其身份），无正面出场，故 chapters 留空并标 mentioned。
#   · 阿普拉克辛伯爵夫人、鲁勉采夫、斯塔尔夫人同理：只有谈述与史论点名，不见于人前。
#   · 阿普拉克辛在 2-1-03 系被祝酒的赴宴来宾（未直接写其言行），故整条标 indexPend。

MINOR = [
    # ── 彼得堡·莫斯科沙龙与宫廷 ────────────────────────────────
    {"id": "morio", "name": "莫里奥神父", "aliases": ["莫里奥"],
     "faction": "court", "family": None,
     "title": "流亡的意大利神父",
     "bio": "舍勒沙龙里的红人，热心而单纯；同皮埃尔大谈欧洲均势与俄国的使命，被安娜·舍勒急忙隔开。",
     "chapters": ["1-1-02", "1-1-03"], "flag": None},

    {"id": "lorand", "name": "劳兰", "aliases": ["劳兰医生"],
     "faction": "court", "family": None,
     "title": "彼得堡名医",
     "bio": "被请来诊视垂危的老别祖霍夫伯爵；仪态讲究，连一句拉丁成语也要拿法语腔道出，出入病家如赴宴。",
     "chapters": ["1-1-12", "1-1-18", "1-1-19", "1-1-20", "1-1-21"], "flag": None},

    {"id": "apraksin", "name": "阿普拉克辛", "aliases": [],
     "faction": "court", "family": None,
     "title": "俱乐部旧贵族、牌手",
     "bio": "皮埃尔在莫斯科俱乐部的老相识、波斯顿牌友；一八一二换了制服，在贵族会上抢着呵斥不同的声音。",
     "chapters": ["2-1-03", "3-1-22"], "flag": "indexPend"},

    {"id": "apraksina", "name": "阿普拉克辛伯爵夫人", "aliases": [],
     "faction": "court", "family": None,
     "title": "彼得堡社交界的寡妇",
     "bio": "莫斯科命名日宴会上太太们口中的名字；新近丧夫，据说哭坏了眼睛，本人始终不在人前出现。",
     "chapters": [], "flag": "mentioned"},

    {"id": "peronskaya", "name": "彼隆斯卡雅", "aliases": ["宫中女官彼隆斯卡雅"],
     "faction": "court", "family": None,
     "title": "前朝女官",
     "bio": "又黄又瘦的前朝旧人；罗斯托夫家在彼得堡全靠她引路，舞会上不停向伯爵夫人报出大臣与公使的名字。",
     "chapters": ["2-3-14", "2-3-15", "2-3-16"], "flag": None},

    {"id": "naryshkina", "name": "纳雷施金娜", "aliases": [],
     "faction": "court", "family": None,
     "title": "彼得堡社交界公认的美人",
     "bio": "太太们拿她作标尺，量每一个初次亮相的姑娘；宫廷波兰舞曲的行列里，她走在男主人身后。",
     "chapters": ["2-3-15", "2-3-16"], "flag": None},

    {"id": "valuev", "name": "华鲁耶夫", "aliases": [],
     "faction": "court", "family": None,
     "title": "御前要人",
     "bio": "俱乐部里被人围住听他讲古的朝臣；一八一二年在御前用餐时望望窗外，提醒皇帝民众还想见他。",
     "chapters": ["2-1-03", "3-1-21"], "flag": None},

    {"id": "shishin", "name": "申兴", "aliases": ["申兴舅舅"],
     "faction": "court", "family": None,
     "title": "莫斯科社交界的“毒舌头”",
     "bio": "罗斯托夫伯爵夫人的堂兄，老单身汉；斜衔琥珀烟管，逢人便把俏皮话与丧气话一并递上。",
     "chapters": ["1-1-15", "1-1-16", "1-1-17", "2-1-02", "2-1-03",
                  "2-1-15", "2-5-08", "2-5-09", "3-1-20"], "flag": None},

    {"id": "rumyantsev", "name": "鲁勉采夫", "aliases": ["鲁勉采夫伯爵"],
     "faction": "court", "family": None,
     "title": "亲法一派的首领",
     "bio": "朝中重臣，彼得堡亲法圈子的旗帜；海伦的客厅为他留着位置，战火烧进来仍替拿破仑说好话。",
     "chapters": [], "flag": "mentioned"},

    {"id": "george", "name": "乔紫小姐", "aliases": ["乔紫"],
     "faction": "court", "family": None,
     "title": "法国悲剧名伶",
     "bio": "拿破仑的旧人，俄国土太们争睹的角色；在莫斯科海伦的客厅里披上红披巾朗诵悲剧诗，四围全是青年。",
     "chapters": ["2-5-13"], "flag": None},

    {"id": "merlukova", "name": "梅留科夫夫人", "aliases": [],
     "faction": "court", "family": None,
     "title": "罗斯托夫家的寡妇邻居",
     "bio": "戴眼镜、体胖而爱笑；圣诞化装舞会就在她家开，她忍笑在人群里走来走去，认不出自己的女儿。",
     "chapters": ["2-4-11"], "flag": None},

    {"id": "schoss", "name": "肖斯夫人", "aliases": [],
     "faction": "court", "family": None,
     "title": "依附罗斯托夫家的外国女伴",
     "bio": "随伯爵一家撤离莫斯科；她的箱子被卸下腾给伤员，厢房让给重伤的安德烈公爵，为此生了气。",
     "chapters": ["3-3-14", "3-3-17", "3-3-31"], "flag": None},

    {"id": "schoss_mlle", "name": "肖斯小姐", "aliases": [],
     "faction": "court", "family": None,
     "title": "罗斯托夫家小姐们的同伴",
     "bio": "爱攒小瓶小盒；化装舞会那一夜，是她带着姑娘们坐雪橇去梅留科夫家的庄园。",
     "chapters": ["2-4-09", "2-4-10", "2-4-11", "2-4-12"], "flag": None},

    {"id": "maria_feodorovna", "name": "玛丽雅太后", "aliases": ["皇太后"],
     "faction": "court", "family": None,
     "title": "先帝遗孀",
     "bio": "老公爵记得她初次赐见时的笑；一八一二年在彼得堡只顾迁走她庇护的机关，于是有了她的一派。",
     "chapters": [], "flag": "mentioned"},

    {"id": "elizabeth_alexeyevna", "name": "伊丽莎白皇后", "aliases": [],
     "faction": "court", "family": None,
     "title": "皇后",
     "bio": "别人向她请示时，她答称机关之事乃皇上的分内；至于她自己，要走也最后一个离开彼得堡。",
     "chapters": [], "flag": "mentioned"},

    {"id": "stael", "name": "斯塔尔夫人", "aliases": ["斯塔尔"],
     "faction": "court", "family": None,
     "title": "法国女作家",
     "bio": "托尔斯泰在史论里把她列入受史家裁判的名人；叙事中又说库图佐夫从塔鲁季诺给她写信、读小说。",
     "chapters": [], "flag": "mentioned"},

    # ── 与沙龙／传闻线交叠的军官 ────────────────────────────────
    {"id": "zhertkov", "name": "热尔科夫", "aliases": [],
     "faction": "russian_army", "family": None,
     "title": "骠骑兵少尉、副官",
     "bio": "爱开玩笑的副官，把盟军覆没当段子讲给奥国将军听；真要他冒弹雨去传令，他半路便调转马头。",
     "chapters": ["1-2-02", "1-2-03", "1-2-05", "1-2-08", "1-2-17", "1-2-19", "1-2-21"],
     "flag": None},

    {"id": "kimzhin", "name": "基莫兴", "aliases": [],
     "faction": "russian_army", "family": None,
     "title": "红鼻子大尉→营长",
     "bio": "因一件蓝大衣挨过团长训斥的红鼻子连长，检阅时听总司令问话便挺得僵直；一八一二年升营长，"
          "鲍罗金诺负伤后与安德烈公爵同在一间农舍。",
     "chapters": ["1-2-02", "1-2-20", "3-2-05", "3-2-24", "3-2-25", "3-2-36", "3-3-31", "3-3-32"], "flag": None},

    {"id": "bogdanovich", "name": "波格丹内奇", "aliases": [],
     "faction": "russian_army", "family": None,
     "title": "骑兵团团长（上校）",
     "bio": "保罗格勒团的老上校，为吉梁宁的事与尼古拉结下疙瘩；退却时故意不看他，仿佛这军官并不存在。",
     "chapters": ["1-2-08"], "flag": "indexPend"},

    {"id": "gierston", "name": "吉尔斯顿", "aliases": [],
     "faction": "russian_army", "family": None,
     "title": "骑兵大尉",
     "bio": "两次因决斗被降为兵、两次官复原职的老骠骑兵；拿一团的名誉劝尼古拉去向团长低头认错。",
     "chapters": ["1-2-05", "1-2-08", "1-3-10"], "flag": None},

    {"id": "bekleshev", "name": "别克列沙夫", "aliases": [],
     "faction": "russian_army", "family": None,
     "title": "赴宴的来宾",
     "bio": "陪巴格拉基昂进莫斯科英国俱乐部赴宴的来宾，在门口止步让主客先行；因名字与皇帝相同，被排在主宾身旁。",
     "chapters": ["2-1-03"], "flag": None},
]
