# -*- coding: utf-8 -*-
"""简录人物提案 · 第一卷 / 第四卷 / 尾声（MinorVol4）

范围：1-1 ~ 1-3、4-1 ~ 4-4、5-1 ~ 5-2 中未收录的次要人物。
收录标准：「出场」= 本人在该场景中有在场行动或对白（含静态在场）；
转述旧话、书信问候、他人谈论、地名与人名归属、注脚点名，均不计。
全部 chapters 经 `python3 scripts/ctx.py <名> [章]` 核对。
"""

MINOR = [
    # ————— 第一卷 第一部 —————
    {"id": "stevens", "name": "斯蒂文思", "aliases": [], "faction": "court",
     "family": None, "title": "英国海军军官",
     "bio": "阿纳托里家酒宴上的英国海军军官，同陶洛霍夫打赌：坐在三楼窗台、两脚悬空，一口气喝完一瓶朗姆酒。赌局当晚就开场。",
     "chapters": ["1-1-06"], "flag": None},

    {"id": "karagina", "name": "卡拉金娜伯爵夫人", "aliases": ["卡拉金娜"],
     "faction": "court", "family": None, "title": "莫斯科贵妇（裘丽之母）",
     "bio": "裘丽的母亲。罗斯托夫家命名日那天她带着女儿登门，跟班在客厅门口高声通报了她和小姐的到来。",
     "chapters": ["1-1-07"], "flag": "verify"},

    # ————— 第一卷 第二部 —————
    {"id": "mack", "name": "马克将军", "aliases": [], "faction": "russian_army",
     "family": None, "title": "奥国将军（乌尔姆投降的奥军统帅）",
     "bio": "奥军副总司令，乌尔姆城下全军覆没后只身逃回。在布尔诺司令部走廊里被热尔科夫当作笑料祝贺，他却带来俄军已输掉一半的实情。",
     "chapters": ["1-2-03"], "flag": None},

    {"id": "ekonomov", "name": "埃科诺莫夫", "aliases": ["埃科诺莫夫少校"],
     "faction": "russian_army", "family": None, "title": "步兵团少校",
     "bio": "保罗格勒步兵团少校。后卫撤退时同团长并马守在桥边，放一个个连队过桥，队列里士兵的歌声引来了团长的注意。",
     "chapters": ["1-2-20"], "flag": None},

    {"id": "ivan_lukich", "name": "伊凡·鲁基奇", "aliases": [], "faction": "russian_army",
     "family": None, "title": "步兵连长",
     "bio": "陶洛霍夫所在连的连长，听不懂法国话，却弓着身子一句不漏地听士兵同法国掷弹兵争论，还一路催他讲下去。",
     "chapters": ["1-2-15"], "flag": None},

    {"id": "sidorov", "name": "西多罗夫", "aliases": [], "faction": "folk",
     "family": None, "title": "俄军士兵",
     "bio": "散兵线上的士兵，被同伴推出来同法国兵斗嘴。他挤挤眼，说出一串谁也听不懂的假法国话，两军阵前笑成一片。",
     "chapters": ["1-2-15"], "flag": None},

    # ————— 第一卷 第三部 —————
    {"id": "chartoryzhsky", "name": "查多利日斯基", "aliases": ["查多利日斯基公爵"],
     "faction": "court", "family": None, "title": "外交大臣（御前随从）",
     "bio": "亚历山大皇帝身边的外交大臣。维绍城外皇帝看着垂死的伤兵落泪，转身用法语对他叹战争可怕；奥斯特里茨前线也在随行之列。",
     "chapters": ["1-3-10", "1-3-15"], "flag": None},

    {"id": "novosiltsev", "name": "诺伏西尔采夫", "aliases": [], "faction": "court",
     "family": None, "title": "御前侍从",
     "bio": "皇帝随从里那些衣饰华丽的年轻人之一，随亚历山大驰上奥斯特里茨前线，一时把青春和活力带进库图佐夫沉闷的司令部。",
     "chapters": ["1-3-15"], "flag": None},

    {"id": "repnin", "name": "雷普宁", "aliases": ["雷普宁公爵"],
     "faction": "russian_army", "family": None, "title": "近卫骑兵上校（负伤被俘）",
     "bio": "近卫骑兵上校，奥斯特里茨负伤被俘。拿破仑问他带的什么兵，他答只带一个骑兵连；皇帝夸他团里尽职，他以军人的客气话回敬。",
     "chapters": ["1-3-19"], "flag": None},

    {"id": "sukhtelen", "name": "苏赫吉仑", "aliases": ["苏赫吉仑中尉"],
     "faction": "russian_army", "family": None, "title": "近卫骑兵中尉（负伤被俘）",
     "bio": "十九岁的近卫骑兵中尉，同雷普宁一起被俘。拿破仑笑他太年轻就来打仗，他断断续续顶了一句：年轻不妨碍勇敢。",
     "chapters": ["1-3-19"], "flag": None},

    # ————— 第四卷 第一部 —————
    {"id": "katerina_petrovna", "name": "卡吉琳娜·彼得罗夫娜", "aliases": [],
     "faction": "court", "family": None, "title": "沃罗涅日晚会上的琴手",
     "bio": "沃罗涅日省长家的座上客。她一起手弹华尔兹和苏格兰舞曲，满场立刻明白今晚要跳舞，太太小姐们都按舞会打扮起来。",
     "chapters": ["4-1-04"], "flag": None},

    {"id": "nikita_ivanovich", "name": "尼基塔·伊凡内奇", "aliases": [],
     "faction": "court", "family": None, "title": "沃罗涅日的文官",
     "bio": "沃罗涅日省里一位文官。晚会上妻子同尼古拉谈笑风生，他板着脸走过来问在谈什么，脸色随妻子的兴奋一点点发白。",
     "chapters": ["4-1-05"], "flag": None},

    # ————— 第四卷 第二部 —————
    {"id": "yakovlev", "name": "雅科武列夫", "aliases": ["雅科武列夫上尉"],
     "faction": "court", "family": None, "title": "俄军上尉（奉拿破仑之命出使）",
     "bio": "莫斯科陷落后被拿破仑召见的上尉，奉命带信去彼得堡见亚历山大皇帝。他关心的只是弄到一件军大衣和一辆大车。",
     "chapters": ["4-2-09", "4-2-10"], "flag": None},

    {"id": "tutolmin", "name": "图托尔明", "aliases": [], "faction": "court",
     "family": None, "title": "莫斯科孤儿院院长（退役少将）",
     "bio": "莫斯科孤儿院的退役少将，拿破仑巡视孤儿院时同他谈话，又派他去彼得堡谈判；亚历山大皇帝没有接见这位使者。",
     "chapters": ["4-2-09", "4-2-10"], "flag": None},

    # ————— 第四卷 第三部 —————
    {"id": "vincent_bosse", "name": "樊尚·博斯", "aliases": ["樊尚", "博斯"],
     "faction": "french_army", "family": None, "title": "被俘的法国小鼓手",
     "bio": "游击队里被俘的法国小鼓手，光着脚踩泥浆，饿得半死。彼嘉央杰尼索夫把他叫进屋，塞给他吃的，却不知怎样待他才好。",
     "chapters": ["4-3-07"], "flag": None},

    {"id": "likhachev", "name": "利哈乔夫", "aliases": [], "faction": "folk",
     "family": None, "title": "杰尼索夫游击队的哥萨克",
     "bio": "游击队里的哥萨克，夜里坐在大车底下替彼嘉磨马刀。彼嘉阵亡前那个半睡半醒的夜里，正是他的声音把彼嘉唤醒。",
     "chapters": ["4-3-10"], "flag": None},

    # ————— 第四卷 第四部 —————
    {"id": "savelich", "name": "萨维里奇", "aliases": [], "faction": "bezukhov",
     "family": None, "title": "皮埃尔的老仆",
     "bio": "皮埃尔的老仆，从莫斯科赶到奥廖尔回报房产情形。皮埃尔问他为何不要自由，他答跟着这样的东家日子好过。",
     "chapters": ["4-4-13", "4-4-18"], "flag": None},

    {"id": "desalles", "name": "德萨尔", "aliases": ["德萨尔先生"],
     "faction": "bolkonsky", "family": None, "title": "小尼古拉的家庭教师（瑞士人）",
     "bio": "安德烈从瑞士请来的家庭教师，穿俄式礼服，说生硬的俄语。他随玛丽雅一行离开童山，又在尾声里守着长大的小尼古拉。",
     "chapters": ["2-5-21", "3-1-08", "3-2-02", "3-2-04", "3-2-08", "4-1-14", "4-4-01", "4-4-15", "4-4-16", "5-1-12", "5-1-14", "5-1-16"], "flag": None},

    # ————— 尾声 —————

    {"id": "anna_makarovna", "name": "安娜·玛卡罗夫娜", "aliases": ["安那·玛卡罗夫娜"],
     "faction": "folk", "family": None, "title": "童山家里照看孩子的人",
     "bio": "童山家里同孩子们在一起的人。她有一手绝活：用一副针织出两只袜子，织完当着孩子们的面从一只里抽出另一只。",
     "chapters": ["5-1-13"], "flag": "verify"},
]
