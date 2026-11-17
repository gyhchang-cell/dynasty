# 武器分期重做 v20

用户已确认 v19 三把武器定稿，随后要求按攻击与获取难度区分基础与高级武器，并继续处理简陋旧资源。本轮选择四把既有武器，精致老图及 v19 三把保持不变。

| ID / 名称 | 实际代码与获取依据 | 本轮处理 |
| --- | --- | --- |
| mu_mao 木矛 | DynastyWeapons：PRIMITIVE，代码标注攻击5；配方2木棍+木板 | 纯木尖、长木杆、三段绑扎，简朴粗像素，无金属宝石 |
| juling_axe 巨灵斧 | DynastyWeapons：攻击2200；WEAPON_BONUS 300；破军斧+龙晶+精钢+图纸 | 大体量钢斧头、宽银刃、厚套筒、龙晶嵌件与缠皮柄 |
| xuantian_axe 玄天钺 | DynastyWeapons：攻击2500；WEAPON_BONUS 300；破军斧+2龙晶+龙帝玉玺 | 宽梯形钺刃、矩形穿孔、玄色金属与古金包边 |
| ziwei_saber 紫微刀 | DynastyWeapons：攻击3200；WEAPON_BONUS 400；龙晶+玄天玉+图纸 | 明确单刃刀形、上扬刀尖、紫黑刀面、银刃与环首 |

数值引用用于美术分期，不是本轮对战伤害实测；没有修改任何数值或获取配方。还查看了 weapon-tier-v11/review.png 中此前认可的原版铁剑/青铜剑/官银剑/玉剑对照，作为基础武器的简单结构与大像素分区参考。用户尚未重发整批愚者武器照片，不声称重新查看了该整批照片。

每件由内置 imagegen 单独生成，完整提示词和生成路径在 selection.json，原稿在 sources/。源画保持原分辨率和 RGBA，不缩16px、不量化；运行图仅裁透明边并补2px。comparison.png 展示运行资源，缩略图为展示用途，非游戏截图。生成与审稿分别核对木矛无高阶装饰、斧/钺轮廓区别、紫微刀单刃与独立刀柄，小图辨识与透明间隙。

统一 install.py 发布，沿用 existing original_item 加载器，由新透明轮廓生成侧边，保留 solid_handheld 左右手第一/第三人称变换。无图形检查和打包记录见 native.log、review.json、DELIVERY.json、installed-readback.json。未启动/重启/关闭游戏，未动声音、亮度、存档；实际世界中的持握、缩放与光影待实机验证。
