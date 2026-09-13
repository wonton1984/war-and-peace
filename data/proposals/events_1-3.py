# -*- coding: utf-8 -*-
# 事件卡提案：第一卷·第三部（1-3-01 … 1-3-19 中未被覆盖的 01-13；14-19 已有 e-austerlitz / e-nikolai-wound）
# 依据草婴译本 corpus/ch/1-3-01..13 逐章核对 chars 出场；summary 全部自撰。
EVENTS_PROPOSAL = [
    # ── 1. 皮埃尔–海伦：被安排的婚姻（01-02，彼得堡）──
    {
        "id": "e-pierre-helen-wedding",
        "title": "被安排的婚姻",
        "ch": ["1-3-01", "1-3-02"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "family", "place": "彼得堡",
        "factions": ["bezukhov", "kuragin"],
        "chars": ["pierre", "helen", "vasily", "anna_sherer", "kuragina"],
        "rel": [
            {"a": "vasily", "b": "pierre", "kind": "estate", "delta": "从图谋遗嘱变成张罗婚事，把继承人牢牢留在自己家里"},
            {"a": "pierre", "b": "helen", "kind": "marriage", "delta": "命名日家宴上求婚定局，一个半月后成婚"},
        ],
        "theme": ["marriage", "vanity"],
        "arc": [
            {"who": "pierre", "stage": "牢笼"},
            {"who": "helen", "stage": "交易"},
        ],
        "summary": "皮埃尔成了巨产继承人，被华西里公爵带到彼得堡，安插进自己的家门。舍勒的晚会上他一转头看清了海伦肉体的魅力，从此退不回从前的看法。命名日家宴上满座人都等着那句话，求婚终于说出口；一个半月后婚礼办完，他住进装修一新的邸宅，成了社交界公认最走运的新婚人。",
        "history": None, "flag": None,
    },

    # ── 2. 童山求婚与拒婚（03-05，童山）──
    {
        "id": "e-marya-refuses-anatole",
        "title": "童山的求婚",
        "ch": ["1-3-03", "1-3-04", "1-3-05"],
        "book": 1, "part": 3,
        "year": 1805, "month": 12, "day": None,
        "type": "intrigue", "place": "童山",
        "factions": ["bolkonsky", "kuragin"],
        "chars": ["vasily", "anatole", "marya", "old_prince", "liza", "bourienne"],
        "rel": [
            {"a": "anatole", "b": "marya", "kind": "courtship", "delta": "为财产而来的求婚，当面殷勤背后嫌丑"},
            {"a": "anatole", "b": "bourienne", "kind": "affair", "delta": "借住的花房里搂腰低语，被玛丽雅撞破"},
            {"a": "old_prince", "b": "marya", "kind": "kin", "delta": "当众羞辱女儿的装扮，内心更不肯放她出嫁"},
        ],
        "theme": ["marriage"],
        "arc": [{"who": "marya", "stage": "受难"}],
        "summary": "一八〇五年十二月，华西里公爵带着阿纳托里到童山，替儿子向玛丽雅公爵小姐提亲。老公爵一边当众奚落女儿的穿戴，一边私下应下求婚，说要当面考察女婿。阿纳托里眼里只有布莉恩小姐，二人在花房幽会被玛丽雅撞破。老公爵假意给女儿择婿自由，她当场说了不愿意，回房反倒安慰布莉恩，要成全这对情人。",
        "history": None, "flag": None,
    },

    # ── 3. 罗斯托夫家读信（06，莫斯科）──
    {
        "id": "e-nikolai-letter",
        "title": "尼古拉的家书",
        "ch": ["1-3-06"],
        "book": 1, "part": 3,
        "year": None, "month": None, "day": None,
        "type": "family", "place": "莫斯科",
        "factions": ["rostov", "druzh"],
        "chars": ["ilya", "countess_r", "anna_mikh", "natasha", "sophia", "petya", "vera"],
        "rel": [
            {"a": "natasha", "b": "sophia", "kind": "kin", "delta": "分担秘密与眼泪，宋尼雅说出终身不改的爱"},
        ],
        "theme": ["marriage"],
        "arc": [{"who": "sophia", "stage": "定情"}],
        "summary": "仲冬，罗斯托夫家盼到尼古拉的第一封亲笔信：他负了伤，也升了军官。老伯爵关在书房里对着信又哭又笑；德鲁别茨卡雅公爵夫人像做手术一样，把消息一层一层透给伯爵夫人。娜塔莎抢先抱住宋尼雅报信，两人对哭，宋尼雅说她一辈子都爱他。全家联名回信写了一周，附上六千卢布托近卫军的门路寄去。",
        "history": None, "flag": None,
    },

    # ── 4. 奥洛莫乌茨重逢与大检阅（07-08）──
    {
        "id": "e-olomouc-review",
        "title": "奥尔米茨大检阅",
        "ch": ["1-3-07", "1-3-08"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "march", "place": "奥尔米茨",
        "factions": ["russian_army", "court"],
        "chars": ["nikolai", "boris", "berg", "andrei", "alexander", "franz"],
        "rel": [
            {"a": "nikolai", "b": "andrei", "kind": "enemy", "delta": "参谋部的嘲讽刺痛骠骑兵，挑战的念头被检阅冲散"},
            {"a": "nikolai", "b": "boris", "kind": "friend", "delta": "半年重逢，两种从军路子的互相打量"},
        ],
        "theme": ["history", "vanity"],
        "arc": [{"who": "nikolai", "stage": "少年"}],
        "summary": "尼古拉到奥洛莫乌茨的近卫军营地找保里斯取钱收家信，把申格拉本的经历吹得与事实全不符；来访的安德烈出言调侃，两人不欢而散，决斗与否一路上缠着他。次日两位皇帝检阅八万联军，尼古拉在御前如醉如痴，纵马从皇帝面前驰过，只恨不能为沙皇赴死。全军对胜利的信心比打了胜仗还强。",
        "history": None, "flag": None,
    },

    # ── 5. 保里斯在司令部（09）──
    {
        "id": "e-boris-headquarters",
        "title": "不成文的从属关系",
        "ch": ["1-3-09"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "intrigue", "place": "奥尔米茨",
        "factions": ["russian_army", "court"],
        "chars": ["boris", "andrei", "nesvitsky"],
        "rel": [
            {"a": "boris", "b": "andrei", "kind": "patron", "delta": "一次引荐让准尉站进将军都要候见的门里"},
        ],
        "theme": ["vanity", "history"],
        "arc": [],
        "summary": "保里斯到行营找安德烈谋副官差事，看见挂满勋章的老将军对小副官踮脚侍立，明白了军中除条令之外还有一套不成文的从属关系。安德烈带他去行宫见侍从武官长，正遇御前军事会议散会：少壮派压倒两位老将，决定立刻同拿破仑决战。拿破仑的来信被当作心虚的证据，司令部里人人相信胜利已成定局。",
        "history": None, "flag": None,
    },

    # ── 6. 维绍小捷与皇帝亲临（10）──
    {
        "id": "e-wischau-affair",
        "title": "维绍：小胜与大捷",
        "ch": ["1-3-10"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": 16,
        "type": "battle", "place": None,
        "factions": ["russian_army", "french_army"],
        "chars": ["nikolai", "denisov", "alexander"],
        "rel": [
            {"a": "nikolai", "b": "alexander", "kind": "patron", "delta": "对沙皇的崇拜烧到顶点，只求死在御前"},
        ],
        "theme": ["history", "vanity"],
        "arc": [{"who": "nikolai", "stage": "少年"}],
        "summary": "维绍城下只俘虏了法军一个骑兵连，却被传成辉煌大捷。当后备队的尼古拉懊丧无事可干，花钱从哥萨克手里买下落马龙骑兵的好马。皇帝忍不住亲临前线，在垂死伤兵前肩膀发颤、眼中含泪，说战争真是可怕。当晚军官们围着篝火砸碎酒杯为沙皇祝酒，会战前夕全军都爱上了他们的皇帝。",
        "history": None, "flag": "verify",
    },

    # ── 7. 钟表机器开拔（11，史论章）──
    {
        "id": "e-clockwork-march",
        "battle": "b-austerlitz",
        "title": "像钟表一样开拔",
        "ch": ["1-3-11"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "essay", "place": "奥斯特里茨",
        "factions": ["russian_army", "court"],
        "chars": ["andrei", "kutuzov", "bilbin"],
        "rel": [
            {"a": "kutuzov", "b": "andrei", "kind": "service", "delta": "老帅私下交底：明天这一仗要打败仗"},
        ],
        "theme": ["history"],
        "arc": [{"who": "andrei", "stage": "荣耀"}],
        "summary": "和谈使节来往，皇帝在维绍停留，兴奋的中心却从行辕扩散到全军各部。十九日入夜，八万联军离开宿营地，像钟表被上紧发条：一个轮子咬住另一个轮子越转越快，没有任何人能使其停住，结果只是报出奥斯特里茨会战的时辰。安德烈寸步不离总司令，库图佐夫只对他说：我看这一仗要败。",
        "history": None, "flag": None,
    },


    # ── 8. 会战前夜军事会议（12）──
    {
        "id": "e-council-weyroter",
        "battle": "b-austerlitz",
        "title": "会战前夜的军事会议",
        "ch": ["1-3-12"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "march", "place": "奥斯特里茨",
        "factions": ["russian_army", "court"],
        "chars": ["kutuzov", "andrei", "miloradovich", "dokhturov"],
        "rel": [
            {"a": "kutuzov", "b": "andrei", "kind": "service", "delta": "准许他列席会议，却不容任何计划改动"},
        ],
        "theme": ["history"],
        "arc": [{"who": "andrei", "stage": "荣耀"}],
        "summary": "会战前夜，威罗特在库图佐夫行辕宣读近一个钟头复杂如地理课的作战部署。巴格拉基昂拒绝出席；朗热隆当面挖苦，米洛拉多维奇盯脸不语，陶赫杜罗夫记下难懂的村名；总司令在安乐椅上真的睡着了，醒来只说计划不能再改，最要紧的是睡觉。散会后安德烈在雾夜里憧憬：明天或许就是属于他的土伦。",
        "history": None, "flag": None,
    },

    # ── 9. 雾夜侦察与拿破仑训令（13）──
    {
        "id": "e-fog-patrol",
        "battle": "b-austerlitz",
        "title": "雾夜侦察",
        "ch": ["1-3-13"],
        "book": 1, "part": 3,
        "year": 1805, "month": 11, "day": None,
        "type": "march", "place": "奥斯特里茨",
        "factions": ["russian_army", "french_army"],
        "chars": ["nikolai", "bagration", "napoleon"],
        "rel": [
            {"a": "nikolai", "b": "bagration", "kind": "service", "delta": "枪声里自请侦察得偿，被留作传令官"},
        ],
        "theme": ["history"],
        "arc": [{"who": "nikolai", "stage": "少年"}],
        "summary": "雾夜侧防线上，尼古拉困得栽向马鬃，忽然法军阵地火把连成一线、万人高呼万岁。他不顾巴格拉基昂叫其勿过小河的告诫，带三名骠骑兵摸黑冲下山，在子弹的啸声里坐实敌哨未撤，趁势讨上火线的机会，被留在将军身边当传令官。山那边，拿破仑正骑马巡视营地、宣读训令，士兵们相信阵地坚不可摧。",
        "history": None, "flag": None,
    },
]
