# D112 immersive_armors:prismarine 整套参考补证

海晶整套四图标蓝绿装甲块与橙色刺有对应关系。六张穿戴图含8×8橙色刺图，不能把小图当整套低规格缺陷；主体来自64×32中上躯干与中层裤腿图。

setupPieces516–571添加MiddleLeggingsLayerPiece、MiddleBodyLayerPiece、UpperBodyLayerPiece和full ModelPiece(PrismarineModel).texture(prismarine)。

PrismarineModel按五组构造2×5×2长方体刺，起点(-1,-1,-1)，8×8图集；四根头刺、左右臂各三根、左右腿各一根。copyFromModel先全隐藏，再HEAD选组0、CHEST选组1/2、LEGS选组3/4；FEET不启用刺，不能把全套图标上的装饰不加区分复制到四槽。

四配方结果与四槽一致，以海晶碎片/海晶砂粒构件，胸甲额外海洋之心；图案呈离散海晶块质感，橙刺采用专用几何并保留主体标准护甲结构。

固定本地Jar、原始文件与Python解析哈希均保存。原图及原始UV矩形已实际查看；矩形裁片不等于最终有符号面/穿戴接缝验收。既有整套家族比较见historic-family-dedup.json，同套新增部位、附加层不计新设计，新增验收信用0。保留既有适用认可证据，总数与缺口仍未核定，1000门槛未成立。

待验：有符号面方向及刺体UV具体面核查；完整穿戴动态接缝；原生1.19.2与Dynasty1.20.1兼容不可推断；整套独立去重验收及真人实机。

289已认可与70优先资源哈希不变；未覆盖贴图、共享Jar或主清单；未运行Java或游戏，未操作用户实例、声音、屏幕和亮度。
