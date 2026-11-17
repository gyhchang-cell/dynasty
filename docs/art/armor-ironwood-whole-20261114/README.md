# D102 twilightforest:ironwood 整套参考补证

实际查看四张16平方图标和两张64×32穿戴原图；灰褐大面以少量浅绿铆钉/扣点区分，短宽胸部、倒U盔、直裤和独立靴都保留基础MC轮廓。亮色小点服务材质识别，不扩成密集雕花。

对照既有ironwood_metal_rivets整套，旧四图标和两层可用原图逐字节核查；与本轮木板甲的红绑带/独立厚肩、森格毛皮尖牙下摆有不同组织，但不是新发现设计。

TFItems实际namespace twilightforest；四注册bootstrap42..45分别指工厂21..24，创建IronwoodArmorItem、ARMOR_IRONWOOD与四正确Type。该类只有ctor与getArmorTexture，不含自身initializeClient模型覆盖；全包/外部覆盖仍未实测。

getArmorTexture实际只在LEGS选twilightforest:textures/armor/ironwood_2.png，其他选ironwood_1.png，不能按materialname猜默认minecraft路径。原生材质静态段确有ironwood名称。

四个generated图标模型各含10种trim_type覆盖，原图基础layer0一致。四配方用forge:ingots/ironwood，结果minecraft:item_nbt并带附魔：头aqua_affinity、胸腿protection、靴feather_falling，均I级。普通ID不能代替带NBT的实际配方产物。

原始UV胸前76/96、背74/96，第一层四鞋条各24/48；第二层腰部前背40/96，四腿条各36/48。已看裁片，铆钉处在离散局部、背面整块留干净；标准网格上下文矩形不等于最终有符号面或实际接缝验收。

固定本地Jar、原始文件与Python解析哈希均保存。原图及原始UV矩形已实际查看；矩形裁片不等于最终有符号面/穿戴接缝验收。既有整套家族比较见historic-family-dedup.json，同套新增部位、附加层不计新设计，新增验收信用0。保留既有适用认可证据，总数与缺口仍未核定，1000门槛未成立。

待验：1000适用独立参考验收；确定未改且简陋Dynasty目标；完整纹饰覆盖/运行继承网格与有符号面接缝；实际穿戴验收。

289已认可与70优先资源哈希不变；未覆盖贴图、共享Jar或主清单；未运行Java或游戏，未操作用户实例、声音、屏幕和亮度。
