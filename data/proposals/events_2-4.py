# -*- coding: utf-8 -*-
# 事件卡提案：第二卷·第四部（1810 年秋—12 月，奥特拉德诺耶）
# 现有事件：e-otradnoe-hunt(01,03-07)、e-andrei-oak(02)、e-countess-vs-sonya(12-13)
# 本提案补齐 08-12，并把 10-11 的节庆化装游猎拆成独立事件（place 借用奥特拉德诺耶，梅留科夫庄未在 places.js 立键，flag=verify）
EVENTS_PROPOSAL = [
    {
        "id": "e-julie-matchmaking", "title": "母亲的算盘：求娶裘丽",
        "ch": ["2-4-08"], "book": 2, "part": 4,
        "year": 1810, "month": None, "type": "family", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["countess_r", "nikolai"],
        "rel": [
            {"a": "countess_r", "b": "julie", "kind": "salon", "delta": "写信到卡拉金家为子求亲，得口头允意"},
            {"a": "nikolai", "b": "sophia", "kind": "courtship", "delta": "拒绝为挽救家产娶无感情的富家女"}],
        "theme": ["marriage"], "arc": [{"who": "nikolai", "stage": "成长"}],
        "summary": "伯爵负债日深，暗中变卖祖宅与郊外庄园。伯爵夫人把挽救家计的全部希望押在尼古拉娶有钱的裘丽上，先写信到莫斯科探口风，再含泪相劝。尼古拉顶回去，宁可牺牲一切也不背弃宋尼雅；谈不拢，家里笼着愁云。安德烈从罗马寄来第四封信，婚期又推。",
        "history": None, "flag": None,
    },
    {
        "id": "e-natasha-christmas-wait", "title": "娜塔莎的圣诞苦等",
        "ch": ["2-4-09"], "book": 2, "part": 4,
        "year": 1810, "month": 12, "type": "family", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["natasha", "sophia", "countess_r", "nikolai", "ilya", "petya"],
        "rel": [{"a": "andrei", "b": "natasha", "kind": "courtship", "delta": "婚期悬置，等待从甜蜜变成恐慌"}],
        "theme": ["marriage"], "arc": [{"who": "natasha", "stage": "热恋"}],
        "summary": "圣诞假期第三天，娜塔莎坐立不宁：打发仆人捉公鸡、拿燕麦、取粉笔，要彼嘉背她下楼，躲到柜子后面在吉他上弹出与安德烈听过的那段歌剧旋律。她把自己最可贵的年华算作白白虚度，茶桌上忽然向母亲喊着要把他讨回来，说哭就哭。",
        "history": None, "flag": None,
    },
    {
        "id": "e-harp-night-song", "title": "竖琴与歌",
        "ch": ["2-4-10"], "book": 2, "part": 4,
        "year": 1810, "month": 12, "type": "family", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["natasha", "nikolai", "sophia", "countess_r", "ilya", "petya"],
        "rel": [], "theme": ["marriage"], "arc": [{"who": "natasha", "stage": "热恋"}],
        "summary": "月夜暗室里，兄妹三人围着竖琴追忆童年的黑人幻影，争辩人是否做过天使。娜塔莎起身唱得前所未有地好：伯爵在书房听住了，宋尼雅自愧不如，伯爵夫人含泪听出女儿身上那种过剩的东西。彼嘉跑来报告家奴化装队到了，歌声戛然而止，娜塔莎放声大哭。",
        "history": None, "flag": None,
    },
    {
        "id": "e-masquerade-sleigh-ride", "title": "化装雪橇闯梅留科夫",
        "ch": ["2-4-10", "2-4-11"], "book": 2, "part": 4,
        "year": 1810, "month": 12, "type": "hunt", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["nikolai", "natasha", "sophia", "petya"],
        "rel": [{"a": "nikolai", "b": "sophia", "kind": "courtship", "delta": "月夜雪橇上第一次真正看见她"}],
        "theme": ["people"], "arc": [{"who": "sophia", "stage": "定情"}],
        "summary": "尼古拉扮老太婆驾三驾雪橇，载着骠骑兵娜塔莎、契尔克斯人宋尼雅冲入月色雪原，与父亲的车夫并辔争驰，闯进四俄里外的梅留科夫庄。主客跳舞、玩指环与绳子，肥胖的夫人在乱脸谱里含笑认人。宋尼雅异常兴奋，觉得自己的命运今夜就要定下。",
        "history": None, "flag": "verify",
    },
    {
        "id": "e-barn-woodpile", "title": "谷仓算命与柴堆一吻",
        "ch": ["2-4-11"], "book": 2, "part": 4,
        "year": 1810, "month": 12, "type": "family", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["nikolai", "sophia", "natasha"],
        "rel": [{"a": "nikolai", "b": "sophia", "kind": "courtship", "delta": "月光柴堆后接吻定情"}],
        "theme": ["marriage"], "arc": [{"who": "sophia", "stage": "定情"}, {"who": "nikolai", "stage": "成长"}],
        "summary": "饭桌上老姑娘讲起在谷仓捉鸡占卜、军官现身同席的怪谈，宋尼雅偏要独自去听声。尼古拉绕到后门小径的柴堆后等候——他今夜才认识这个又快活又坚决的姑娘。两人撞个正着，隔着软木焦味接吻，只喊出对方的名字，便分头从原路回去。",
        "history": None, "flag": "verify",
    },
    {
        "id": "e-mirror-divination", "title": "两面镜子前",
        "ch": ["2-4-12"], "book": 2, "part": 4,
        "year": 1810, "month": 12, "type": "family", "place": "奥特拉德诺耶",
        "factions": ["rostov"], "chars": ["natasha", "sophia", "nikolai"],
        "rel": [
            {"a": "nikolai", "b": "sophia", "kind": "courtship", "delta": "归途雪橇上决心与她永不分离"},
            {"a": "natasha", "b": "sophia", "kind": "kin", "delta": "一句含混的占卜话叫娜塔莎又欢喜又不安"}],
        "theme": ["marriage", "death"], "arc": [{"who": "natasha", "stage": "热恋"}],
        "summary": "回程雪橇上，娜塔莎刻意把座位排开，让哥哥与宋尼雅同乘；尼古拉在月光里下了永不分离的决心，又跳上妹妹的雪橇报喜。夜里双镜点烛，娜塔莎盯了许久什么也不见；宋尼雅被催得慌了神，失口说看见未婚夫躺着、容光焕发。烛熄之后，娜塔莎睁眼望着结冰窗缝里的冷月光。",
        "history": None, "flag": None,
    },
]
