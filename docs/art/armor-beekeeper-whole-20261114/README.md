# D77：养蜂服完整四槽图标与穿戴UV研究

实际研究 `thermal:beekeeper_helmet/chestplate/leggings/boots`。来源沿用官方CoFH/ThermalCore固定提交 `cc7c230146a71d177767a8f9d6b26f0a52e9aeed`，29个原生文件经Git blob/SHA-256核对。新实际查看四张16×16图标、两张64×32穿戴图，以及原图、原始UV矩形和与D76的整套对照页。材料图、翻译及其他下载文件不虚报目视数量。

## 四槽与实际消费者

BeekeeperArmorItem全文实读：继承ArmorItemCoFH，构造时按槽注册抗蜇属性。TCoreItems202–205分别构造HELMET/CHESTPLATE/LEGGINGS/BOOTS，ThermalIDs250–253给出四个原生字符串；BEEKEEPER材料名thermal:beekeeper，修理物beekeeper_fabric。四份模型JSON均minecraft:item/generated、单层layer0，实际引用各自图标。

该类客户端扩展与防化服相同：头/胸选ArmorFullSuitModel，腿/脚保留传入默认模型。复用D76已实际读取、固定哈希的CoFHCore `dcd7bd6703418ee2e8eb2185957de83925fa89fe`：头/hat变形outer.extend(0.5)，双袖outer.extend(-0.5)，左袖mirror，图集64×32；层注册、材料getName和主注册helper也复用原证据，不把共享模型重读算新实现。

版本MC1.20.4、NeoForge20.4.237、ThermalCore11.0.7/CoFHCore11.0.2；不宣称Dynasty1.20.1可直接加载。默认层推导腿用layer2、其他用layer1；精确该版本消费者、最终变形常量、发布二进制与接缝仍未验。

五份配方实际读取：布料由蜂脾和forge:string制作，四槽以该布料制作、靴另用forge:leather；均有thermal:beekeeper_armor flag条件。原生指南描述整套防刺且消耗耐久，不把配方或说明当实际获取/功能验收。

## 实图观察

1. 罩帽是宽扁的围网结构，上下浅布边框住网区，脸部没有普通金属盔眼鼻板。网格说明用途，不靠发光或雕花。
2. 胸衣以宽V领/肩接缝、中央竖衣襟、短袖端组织浅青灰大面，区别于前套胸前黑接口，不只是换色。
3. 裤子以宽腰连接双直腿；黑色短靴用方头、短筒和浅布筒口形成材料交界，无圆鼓鞋和巨大装饰。
4. 穿戴head正面矩形[8,8,16,16]中48像素完全不透明、16像素完全透明。图集其他区域还存在alpha188，已记录坐标，不能将全图强制二值化。透孔是PNG事实，不宣称游戏中透明排序或脸部显露已验。
5. 胸前领口/衣襟、背部浅布面、袖口网纹在图集保持身份连续性；不把hat空白或layer2头袖空白误报缺件。layer2主要负责腰腿，layer1腿区主要负责靴。
6. 60个原始UV矩形实际查看，只作材质区域对照，不冒充精确方向、左右镜像、五视穿戴或接缝验收。
7. 对Dynasty旧cloth/sea_silk可借鉴领口、衣襟和袖口的大块分区，皮甲可借鉴布/靴的材料交界；养蜂网罩不直接套成古代盔甲，不复制为原创，也不重画已认可图标。

## 完整设计去重

实际查看了D76防化服四件与本案四件的同页原图。网罩/V领衣襟与前套面罩/接口有结构差别；四件图标alpha均不同，layer1 alpha也不同，但layer2 alpha完全相同。RGBA或alpha不同不能直接证明语义独立。

两套共用头胸模型和功能服体系，先按至多1个完整待审族记录，交主协调比较是否并入同一保守族。四件、六PNG、孔洞、60矩形及重复模型不拆计参考。正式新增信用0；有效总数/精确缺口继续null，gate=false。

`provenance.json`、`reused-consumer-context.json`固定来源及复用哈希；`static-bindings.json`、`raw-uv-context.json`、`prior-hazmat-comparison.json`保存引用、矩形和透明度测量。页面是诊断图，不是游戏截图。用户要求全文与批次说明已保存；289保护/70优先资源前后不变。不开Java/游戏，不碰实例、原存档、共享Jar、声音亮度焦点，不写主清单、不删提示词。继续其他真正未读的完整相关设计，避免本案换色凑数。
