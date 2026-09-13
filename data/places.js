// data/places.js — 庄园 / 城市 / 战场
// kind: estate | city | battlefield | other
// 坐标为示意性地理定位（历史地名取今地近似经纬度），非精确测绘。
const PLACES = {
  // ————— 庄园 —————
  "童山":            { lat:54.30, lng:36.30, modern:"俄国图拉省（小说庄园，示意坐标）", kind:"estate", ru:"Лысые Горы" },
  "奥特拉德诺耶":     { lat:55.55, lng:37.20, modern:"莫斯科近郊（罗斯托夫家庄园，示意坐标）", kind:"estate" },
  "保古察罗伏":       { lat:55.20, lng:35.80, modern:"斯摩棱斯克省（安德烈庄园，示意坐标）", kind:"estate" },
  "尼科尔斯科耶":     { lat:54.10, lng:39.60, modern:"梁赞省（尼古拉庄园，示意坐标）", kind:"estate" },
  "梅基希":          { lat:55.40, lng:36.10, modern:"莫斯科西南近郊小镇", kind:"other" },


  // ————— 城市 —————
  "彼得堡":          { lat:59.94, lng:30.31, modern:"俄罗斯圣彼得堡", kind:"city", ru:"Петербург" },
  "莫斯科":          { lat:55.75, lng:37.62, modern:"俄罗斯莫斯科", kind:"city", ru:"Москва" },
  "维也纳":          { lat:48.21, lng:16.37, modern:"奥地利维也纳", kind:"city" },
  "布劳瑙":          { lat:48.22, lng:13.05, modern:"奥地利布劳瑙", kind:"city" },
  "布尔诺":          { lat:49.20, lng:16.61, modern:"捷克布尔诺", kind:"city" },
  "奥尔米茨":        { lat:49.59, lng:17.25, modern:"捷克奥洛穆茨", kind:"city" },
  "维尔诺":          { lat:54.69, lng:25.28, modern:"立陶宛维尔纽斯", kind:"city" },
  "斯摩棱斯克":      { lat:54.78, lng:32.05, modern:"俄罗斯斯摩棱斯克", kind:"city" },
  "沃罗涅日":        { lat:51.67, lng:39.21, modern:"俄罗斯沃罗涅日", kind:"city" },
  "雅罗斯拉夫尔":     { lat:57.63, lng:39.87, modern:"俄罗斯雅罗斯拉夫尔", kind:"city" },
  "奥廖尔":          { lat:52.97, lng:36.06, modern:"俄罗斯奥廖尔", kind:"city" },
  "梁赞":            { lat:54.63, lng:39.69, modern:"俄罗斯梁赞", kind:"city" },
  "卡卢加":          { lat:54.51, lng:36.26, modern:"俄罗斯卡卢加", kind:"city" },
  "图拉":            { lat:54.20, lng:37.62, modern:"俄罗斯图拉", kind:"city" },
  "蒂尔西特":        { lat:55.08, lng:21.90, modern:"俄罗斯加里宁格勒州苏维埃茨克", kind:"city" },
  "埃尔富特":        { lat:50.98, lng:11.03, modern:"德国埃尔福特", kind:"city" },
  "德累斯顿":        { lat:51.05, lng:13.74, modern:"德国德累斯顿", kind:"city" },
  "柏林":            { lat:52.52, lng:13.40, modern:"德国柏林", kind:"city" },
  "华沙":            { lat:52.23, lng:21.01, modern:"波兰华沙", kind:"city" },

  // ————— 战场 —————
  "维绍":            { lat:49.28, lng:17.00, modern:"捷克维什科夫（1805 前卫小捷）", kind:"battlefield" },
  "申格拉本":        { lat:49.30, lng:16.90, modern:"捷克布尔诺东北（1805 战场）", kind:"battlefield" },
  "奥斯特里茨":      { lat:49.15, lng:16.88, modern:"捷克斯拉夫科夫（三皇会战）", kind:"battlefield", ru:"Аустерлиц" },
  "霍拉勃隆":        { lat:48.93, lng:16.75, modern:"捷克霍拉布伦（1805 后卫战）", kind:"battlefield" },
  "恩斯河":          { lat:48.28, lng:14.30, modern:"奥地利恩斯河一线", kind:"battlefield" },
  "克雷姆斯":        { lat:48.41, lng:15.61, modern:"奥地利克雷姆斯", kind:"battlefield" },
  "普尔土斯克":      { lat:52.70, lng:21.10, modern:"波兰普乌图斯克（1806 战场）", kind:"battlefield" },
  "埃劳":            { lat:54.38, lng:20.65, modern:"俄罗斯巴格拉季奥诺夫斯克（1807 战场）", kind:"battlefield" },
  "弗里德兰":        { lat:54.48, lng:21.02, modern:"俄罗斯普拉夫金斯克（1807 战场）", kind:"battlefield" },
  "奥斯特罗夫诺":     { lat:55.30, lng:30.20, modern:"白俄罗斯奥斯特罗夫诺（1812 战斗）", kind:"battlefield" },
  "鲍罗金诺":        { lat:55.52, lng:35.82, modern:"俄罗斯莫扎伊斯克以西（1812 会战）", kind:"battlefield", ru:"Бородино" },
  "舍瓦尔季诺":      { lat:55.51, lng:35.68, modern:"鲍罗金诺会战前哨", kind:"battlefield" },
  "塔鲁季诺":        { lat:55.20, lng:36.60, modern:"俄罗斯塔鲁季诺（1812 侧翼进军）", kind:"battlefield" },
  "小雅罗斯拉韦茨":   { lat:55.01, lng:36.47, modern:"俄罗斯小雅罗斯拉韦茨（1812 血战）", kind:"battlefield" },
  "克拉斯诺耶":      { lat:54.57, lng:31.43, modern:"俄罗斯克拉斯内（1812 追歼）", kind:"battlefield" },
  "别列津纳":        { lat:54.30, lng:28.35, modern:"白俄罗斯别列津纳河（1812 渡河）", kind:"battlefield" },
  "维亚兹马":        { lat:55.21, lng:34.30, modern:"俄罗斯维亚济马", kind:"battlefield" },

  // ————— 其他 —————
  "德里萨":          { lat:55.80, lng:27.90, modern:"白俄罗斯德里萨（1812 营地）", kind:"other" },
  "波克朗山":        { lat:55.73, lng:37.55, modern:"莫斯科西南（库图佐夫指挥部）", kind:"other" },
  "菲里":            { lat:55.74, lng:37.50, modern:"莫斯科菲里村（1812 军事会议）", kind:"other" },
  "克拉斯纳亚帕赫拉":  { lat:55.44, lng:37.28, modern:"莫斯科近郊（库图佐夫指挥部）", kind:"other" },
  "察廖夫扎伊米歇":    { lat:55.60, lng:35.60, modern:"斯摩棱斯克省（库图佐夫指挥部）", kind:"other" },
  "阿尔巴特街":       { lat:55.75, lng:37.59, modern:"莫斯科阿尔巴特街", kind:"other" },
  "巴兹杰耶夫宅":     { lat:55.76, lng:37.61, modern:"莫斯科（皮埃尔藏身处）", kind:"other" },
};

if (typeof module !== "undefined") module.exports = { PLACES };
