# -*- coding: utf-8 -*-
# 法军与外国人物简录提案（MinorFrench）
# 译名依草婴译本：兰纳／奈伊／贝蒂埃／拉普／萨瓦里／科兰古／迪罗克／裴里亚／波尼亚托夫斯基／奥古斯滕堡
# 缪拉、达武、莫特玛已在详录册，不重复收录；「路易」经查均为路易十四/十六等被提及的历史人物及玛丽·路易丝，非出场角色，未收。
# chapters 均已 grep corpus/ch/ 并读正文核对实际出场；仅被提及者 chapters 留空并标 verify。

MINOR = [
    {"id":"berthier", "name":"贝蒂埃", "aliases":["贝尔蒂埃"],
     "faction":"french_army", "family":None,
     "title":"法军参谋长",
     "bio":"拿破仑的参谋长，把全军师团营的数字记得一清二楚。鲍罗金诺土岗旁替皇帝酌定派哪个师上前，被拿破仑自评「我把小鹅训练成鹰了」。",
     "chapters":["3-1-02","3-1-07","3-2-07","3-2-34"],
     "flag":None},

    {"id":"ney", "name":"奈伊", "aliases":["埃尔欣根公爵"],
     "faction":"french_army", "family":None,
     "title":"法军元帅",
     "bio":"大胆著称的法国元帅。战前会议独敢谏言穿林之险；鲍罗金诺立于拿破仑身边冷笑调近卫军之议；溃退时殿后，扬言「当皇帝当够了，如今要做做将军」。",
     "chapters":["3-2-27","3-2-34","4-3-17"],
     "flag":None},

    {"id":"lannes", "name":"兰纳", "aliases":["拉纳"],
     "faction":"french_army", "family":None,
     "title":"法军元帅",
     "bio":"拿破仑麾下猛将。维也纳桥头拉住欲报信的中士的手臂、替缪拉的骗局打圆场的是他；奥斯特里茨后纵马向皇帝脱帽含笑贺胜。",
     "chapters":["1-3-19"],
     "flag":None},

    {"id":"rapp", "name":"拉普", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"拿破仑副官",
     "bio":"拿破仑的随身副官。鲍罗金诺前夜在帝帐对答：「酒瓶既已打开，就得一饮而尽」；被问近卫军如何，只答「还好，陛下」。",
     "chapters":["3-2-29"],
     "flag":None},

    {"id":"savary", "name":"萨瓦里", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"法军将领、拿破仑特使",
     "bio":"奥斯特里茨前举军使旗求见俄皇的法国军官。名义上传议和与安排两国皇帝会面，实为探听虚实；亚历山大拒会，全营引以为豪。",
     "chapters":["1-3-11"],
     "flag":None},

    {"id":"caulaincourt", "name":"科兰古", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"法军将领、驻俄大使",
     "bio":"拿破仑的近侍将领，曾任驻彼得堡大使。巴拉歇夫出使时与他同席御宴，他识趣地把话头岔到路况；鲍罗金诺时被唤来陪皇帝谈与战争无关的事。",
     "chapters":["3-1-07","3-2-34"],
     "flag":None},

    {"id":"duroc", "name":"迪罗克", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"法军元帅、大宫廷官",
     "bio":"拿破仑帐前司宾的元帅。巴拉歇夫到法营候见，是他传话「皇帝骑马散步前接见」，又替他送来当晚御宴的邀请。",
     "chapters":["3-1-06","3-1-07"],
     "flag":None},

    {"id":"perrega", "name":"裴里亚", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"法军将军",
     "bio":"鲍罗金诺阵前的火性子将军。纵马直冲御前，赌咒说再派一个师俄军就完；拿破仑只回一句「火气大容易犯错，先回去看看再来找我」。",
     "chapters":["3-2-34"],
     "flag":None},

    {"id":"poniatowski", "name":"波尼亚托夫斯基", "aliases":[],
     "faction":"french_army", "family":None,
     "title":"法军元帅（波兰公爵）",
     "bio":"为拿破仑效力的波兰公爵，统领一军。鲍罗金诺奉命包抄俄军左翼，实际只与杜契科夫发生小接触；其军中波兰士官有只身投奔俄军者。",
     "chapters":[],
     "flag":"verify"},

    {"id":"augustenborg", "name":"奥古斯滕堡公爵", "aliases":[],
     "faction":"court", "family":None,
     "title":"奥军陆军中将",
     "bio":"守维也纳泰波桥头堡的奥国将领。被缪拉、兰纳等假意亲昵哄住，反下令拘押报信的中士，桥遂未炸而失。其事经比利平讲述传为笑谈。",
     "chapters":[],
     "flag":"verify"},

    {"id":"wurttemberg", "name":"符腾堡亲王", "aliases":["符腾堡的叶夫盖尼亲王"],
     "faction":"court", "family":None,
     "title":"俄军第一军司令（德籍亲王）",
     "bio":"在俄军供职的德籍亲王。巴格拉基昂负伤后库图佐夫请他接掌第一军，他尚未到位即请增兵；克拉斯诺耶从山上枪击溃退法军，援军仍不至。",
     "chapters":["3-2-35","4-4-04"],
     "flag":None},
]
