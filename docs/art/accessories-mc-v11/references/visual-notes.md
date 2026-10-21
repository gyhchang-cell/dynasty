# 1000件模组物品参考复查

实际查看study-01至study-10，100件一页，共1000件去重物品，包含饰品与普通物品；来源18个本地整合包目录、400个模组命名空间，从8940个候选中按命名空间轮选，扫描2523个不同文件名JAR。sources.json记录ID、JAR、原资源路径与SHA256。该计数不是1000个整合包；参考中也有不适合项目的GUI符号、模组占位图和高细节反例，未把它们全部当作合格风格。

- 第1—3页：Artifacts药瓶、Cataclysm腰带、Twilight Forest挂符、项链的识别来自大片轮廓与小数目的高光。亦有过亮光团、纯色GUI标记等反例。
- 第4—6页：Relics与Jewelry的首饰保留负空间；HerbalBrews杯口、Supplementaries墨水瓶和Quark算盘在几格明暗内建立材质。细节不是细碎写实纹理。
- 第7—10页：比对Malum腰带、饰品环、兽爪与角等，区分主体形状和附属线。食物、袋、材料也靠不规则粗阶梯与主色块识别，不能统统做成圆宝石或精致徽章。

风格板只选8个清晰示例：artifacts:antidote_vessel、relics:bastion_ring、cataclysm:belt_of_beginner、jewelry:citrine_necklace、herbalbrews:coffee、naturalist:antler、supplementaries:antique_ink、quark:abacus_0。参考像素从未写入Dynasty运行资源。imagegen参考图仅用于大像素和克制明暗，所有12件按各自真实名称原创。

作者仓库入口核对：[Relics](https://github.com/Octo-Studios/relics)、[Botania](https://github.com/VazkiiMods/Botania)。本轮实际视觉依据是本地安装版本中的PNG，不以README代替看图。

## 对原先作品的复查结论

v10八件：茶盏多余釉裂、官徽细羽毛与边纹、星盘刻度与额外星点、铃铛雕纹、皮革缝线均使32px预览产生碎噪，全部返修。v9的朱砂囊织物噪点、逆鳞密纹、海螺细肋与碎高光、战鼓密集绳索亦有相同问题，补做4件。其他精致老图及未选作品不作批量简化。

检查comparison.png与inventory-size-review.png：后者所有新旧主体均适配同样32px预览槽位，再整数放大方便阅读；运行PNG保留生成原稿主体像素，未通过事后缩图、量化或Pillow绘制来伪造新资产。资源预览不等于游戏实测。
