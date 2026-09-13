# -*- coding: utf-8 -*-
# 事件卡提案：第二卷·第一部（1806，16 章）
# 现有 events.js 在本部只有两张卡（e-pierre-dolokhov-duel 覆盖 04/06/11/12，
# e-nikolai-dolokhov-cards 覆盖 13/14/15）。以下 9 张补齐本部其余章节：
# 01、02-03、05、07、08-09、10-11、12、16（拆成父子还债与杰尼索夫求爱两张）。
# 所有 summary 为自撰概述，未使用底本措辞。
EVENTS_PROPOSAL = [
    {
        "id": "e-nikolai-home-leave",
        "title": "尼古拉休假归家",
        "ch": ["2-1-01"],
        "book": 2, "part": 1, "year": 1806, "month": None,
        "type": "family", "place": "莫斯科",
        "factions": ["rostov", "russian_army"],
        "chars": ["nikolai", "denisov", "natasha", "sophia", "ilya", "countess_r", "petya"],
        "rel": [
            {"a": "nikolai", "b": "denisov", "kind": "service",
             "delta": "把醉睡的朋友一路带回自己家，全家把他当贵客接待"},
            {"a": "nikolai", "b": "sophia", "kind": "courtship",
             "delta": "少年之约被当面挑明：她宁可放手，也不要他勉强守约"},
            {"a": "natasha", "b": "denisov", "kind": "salon",
             "delta": "初次见面就扑上去拥抱亲吻，弄得满屋人尴尬"}
        ],
        "theme": ["marriage", "freedom"],
        "arc": [
            {"who": "nikolai", "stage": "少年"},
            {"who": "natasha", "stage": "少女"},
            {"who": "sophia", "stage": "定情"}
        ],
        "summary": "一八〇六年初，尼古拉休假回到莫斯科，顺手把醉得不省人事的杰尼索夫也带回自己家。"
                   "屋里一片拥抱与哭声，唯独母亲最后才出来。次日娜塔莎摊牌：宋尼雅愿意爱他，却不愿用旧约捆住他；"
                   "她自己立志一辈子不嫁人，要当舞蹈家。",
        "history": None, "flag": None,
    },
    {
        "id": "e-bagration-banquet",
        "title": "英国俱乐部的接风宴",
        "ch": ["2-1-02", "2-1-03"],
        "book": 2, "part": 1, "year": 1806, "month": 3,
        "type": "ball", "place": "莫斯科",
        "factions": ["rostov", "russian_army", "bezukhov"],
        "chars": ["ilya", "bagration", "nikolai", "denisov", "dolokhov", "pierre", "nesvitsky", "anna_mikh"],
        "rel": [
            {"a": "ilya", "b": "bagration", "kind": "salon",
             "delta": "倾囊作东，从颂诗到摔杯一路张罗，最后为自己干杯落泪"},
            {"a": "pierre", "b": "dolokhov", "kind": "enemy",
             "delta": "同席而坐，一句祝酒词挑出早已传开的猜忌"},
            {"a": "anna_mikh", "b": "pierre", "kind": "patron",
             "delta": "主动替他张罗、传话请他到场，顺手攀上人情"}
        ],
        "theme": ["history", "vanity"],
        "arc": [{"who": "pierre", "stage": "牢笼"}],
        "summary": "奥斯特里茨败讯传到莫斯科，先是一片缄默，随后由俱乐部里的头面人物定调：错在奥国人和统帅，"
                   "只有士兵是英雄，被捧出来的英雄是巴格拉基昂。老伯爵倾囊设下三百人的接风宴，"
                   "颂诗、大鲟鱼、香槟与摔杯一轮接一轮，轮到给他自己干杯时他捂脸哭出声。皮埃尔闷坐对面，心事无人过问。",
        "history": "一八〇五年末俄军在奥斯特里茨惨败，国内舆论难以接受，便把不丢面子的战功集中到一位"
                   "不涉党争的将军身上；这正是托尔斯泰讽刺的集体造神。",
        "flag": None,
    },
    {
        "id": "e-dolokhov-fires-wide",
        "title": "第二枪故意打偏",
        "ch": ["2-1-05"],
        "book": 2, "part": 1, "year": 1806, "month": 3,
        "type": "duel", "place": "莫斯科",
        "factions": ["bezukhov", "russian_army"],
        "chars": ["dolokhov", "pierre", "nikolai", "denisov", "nesvitsky"],
        "rel": [
            {"a": "pierre", "b": "dolokhov", "kind": "enemy",
             "delta": "一枪见血，真正的杀意却被陶洛霍夫自己咽了回去"},
            {"a": "dolokhov", "b": "nikolai", "kind": "friend",
             "delta": "负伤后把向母亲报信的差事交给他"}
        ],
        "theme": ["vanity", "death"],
        "arc": [{"who": "dolokhov", "stage": "赌局"}],
        "summary": "融雪的林间空地上起雾，四十步外看不清人脸。皮埃尔伸手就开枪，打中了陶洛霍夫的腰。"
                   "对方伏在雪里咬一口雪，撑起身体举枪瞄准，对着挺胸站立的皮埃尔回敬一枪偏弹，又倒回雪地。"
                   "被抬进城时他只抓住尼古拉：先去看我母亲，别让她受惊。",
        "history": None, "flag": None,
    },
    {
        "id": "e-bolkonsky-obituary",
        "title": "童山的讣闻",
        "ch": ["2-1-07"],
        "book": 2, "part": 1, "year": None, "month": None,
        "type": "family", "place": "童山",
        "factions": ["bolkonsky"],
        "chars": ["old_prince", "marya", "liza"],
        "rel": [
            {"a": "old_prince", "b": "marya", "kind": "kin",
             "delta": "第一次在女儿面前失控抽噎，两人共守一个秘密"},
            {"a": "marya", "b": "liza", "kind": "kin",
             "delta": "跪在嫂子膝上擦泪，宁可哭也不说出死讯"}
        ],
        "theme": ["death"],
        "arc": [{"who": "marya", "stage": "受难"}],
        "summary": "童山得到奥斯特里茨的消息已经两个月，尸首与俘虏名单里都没有安德烈。库图佐夫的信说他的手举军旗、"
                   "冲在全团之前。老公爵把悲痛全化成愤怒，命人定好墓碑，逢人便说儿子阵亡；"
                   "玛丽雅仍旧天天盼他回来。两人商定：先瞒住快临产的丽莎。",
        "history": None, "flag": None,
    },
    {
        "id": "e-liza-death",
        "title": "难产之夜",
        "ch": ["2-1-08", "2-1-09"],
        "book": 2, "part": 1, "year": None, "month": 3,
        "type": "wound", "place": "童山",
        "factions": ["bolkonsky"],
        "chars": ["andrei", "liza", "marya", "old_prince", "nikolushka"],
        "rel": [
            {"a": "andrei", "b": "liza", "kind": "marriage",
             "delta": "归来当夜妻子死于难产，他自觉犯下无法补救的罪"},
            {"a": "old_prince", "b": "andrei", "kind": "kin",
             "delta": "父子在门口无言相抱，老头儿哭得像孩子"}
        ],
        "theme": ["death"],
        "arc": [
            {"who": "andrei", "stage": "沉寂"},
            {"who": "marya", "stage": "受难"}
        ],
        "summary": "三月十九日夜里突然临产，风雪吹灭蜡烛，全家打灯笼在大路上等莫斯科请来的产科医生。"
                   "走上楼梯的却是被认定阵亡的安德烈——他与医生在最后一站同车赶到。孩子活了，产妇死了，"
                   "那张脸到闭眼时还像在问为什么。三日后下葬，五日后施洗，老公爵颤巍巍抱着婴儿当教父。",
        "history": None, "flag": None,
    },
    {
        "id": "e-dolokhov-proposal",
        "title": "向没有陪嫁的孤女求婚",
        "ch": ["2-1-10", "2-1-11"],
        "book": 2, "part": 1, "year": 1806, "month": 12,
        "type": "family", "place": "莫斯科",
        "factions": ["rostov", "russian_army"],
        "chars": ["nikolai", "dolokhov", "sophia", "natasha", "countess_r", "denisov"],
        "rel": [
            {"a": "dolokhov", "b": "sophia", "kind": "courtship",
             "delta": "常来做客的亡命徒开口求婚，被一口回绝"},
            {"a": "nikolai", "b": "sophia", "kind": "courtship",
             "delta": "他劝她接受这门合适的亲事，她只要像妹妹那样永远爱他"},
            {"a": "dolokhov", "b": "natasha", "kind": "enemy",
             "delta": "全家只剩她咬定陶洛霍夫心肠坏、决斗中皮埃尔才有理"}
        ],
        "theme": ["marriage", "vanity"],
        "arc": [
            {"who": "sophia", "stage": "定情"},
            {"who": "dolokhov", "stage": "算计"}
        ],
        "summary": "决斗经老伯爵奔走暗中了结，尼古拉反倒当上总督副官，整个夏天没离开莫斯科。养好伤的陶洛霍夫天天来"
                   "罗斯托夫家吃饭，看上了没有陪嫁的宋尼雅。圣诞饯行宴上家里人才知道：他求了婚，被她当场拒绝。"
                   "尼古拉劝她重新考虑，她只说愿像爱哥哥一样永远爱他。",
        "history": None, "flag": None,
    },
    {
        "id": "e-natasha-yugler-ball",
        "title": "约盖尔舞会上的玛祖卡",
        "ch": ["2-1-12"],
        "book": 2, "part": 1, "year": 1806, "month": 12,
        "type": "ball", "place": "莫斯科",
        "factions": ["rostov", "russian_army"],
        "chars": ["natasha", "denisov", "nikolai", "sophia"],
        "rel": [
            {"a": "denisov", "b": "natasha", "kind": "courtship",
             "delta": "被她亲口劝下场跳玛祖卡，一整晚再没离开她身旁"}
        ],
        "theme": ["vanity"],
        "arc": [{"who": "natasha", "stage": "少女"}],
        "summary": "约盖尔借来皮埃尔家的大厅办舞会，没有主人，只收入场券，人人跳得像初次穿长舞裙的少女。"
                   "娜塔莎第一次正式赴会，一进场就爱上所有看见的人。她独自穿过舞厅去请坐着不肯下场的杰尼索夫；"
                   "马刺一响全场惊叹，连老人都谈起波兰和旧日时光。",
        "history": None, "flag": None,
    },
    {
        "id": "e-ilya-pays-debt",
        "title": "父亲替儿子还清赌账",
        "ch": ["2-1-16"],
        "book": 2, "part": 1, "year": None, "month": None,
        "type": "business", "place": "莫斯科",
        "factions": ["rostov"],
        "chars": ["nikolai", "ilya", "sophia", "countess_r"],
        "rel": [
            {"a": "ilya", "b": "nikolai", "kind": "kin",
             "delta": "勉强筹足四万三千卢布替儿子还债，宽容比责骂更难当"},
            {"a": "nikolai", "b": "sophia", "kind": "courtship",
             "delta": "她越发体贴，他自认已经不配"}
        ],
        "theme": ["vanity", "marriage"],
        "arc": [{"who": "nikolai", "stage": "失足"}],
        "summary": "父亲从俱乐部回来，尼古拉迎上去，用连自己都厌恶的平静口气说出那个数目。老伯爵红到后颈，"
                   "颓然倒进沙发，只反复说谁都会遇到这样的事。儿子追上去吻他的手，放声大哭。"
                   "此后两星期尼古拉足不出户，等父亲好不容易把这笔钱筹足，再送去取收据。",
        "history": None,
        "flag": "verify",
    },
    {
        "id": "e-denisov-proposal-rejected",
        "title": "杰尼索夫求爱被拒",
        "ch": ["2-1-16"],
        "book": 2, "part": 1, "year": None, "month": None,
        "type": "family", "place": "莫斯科",
        "factions": ["rostov", "russian_army"],
        "chars": ["natasha", "denisov", "countess_r", "nikolai"],
        "rel": [
            {"a": "denisov", "b": "natasha", "kind": "courtship",
             "delta": "一次没有回应的求爱：她敬爱他、可怜他，却不嫁他"},
            {"a": "countess_r", "b": "denisov", "kind": "salon",
             "delta": "板着脸教训他该先向家长开口，把这门亲事挡在门外"}
        ],
        "theme": ["marriage"],
        "arc": [{"who": "natasha", "stage": "少女"}],
        "summary": "就在父子谈心的同一晚，杰尼索夫守在钢琴边说命运握在她手里。娜塔莎先去找母亲讨主意，"
                   "又自己跑回大厅见他：她敬爱他，也可怜他，只是不嫁。伯爵夫人板着脸说女儿还小，"
                   "他该先同家长开口。第二天尼古拉送朋友上雪橇，他在莫斯科连一天也不愿多留。",
        "history": None, "flag": None,
    },
]
