# D111 immersive_armors:divine 整套参考补证

神圣整套八张物品PNG为四底图加四overlay；generated模型明确layer0和layer1，两者合成才是完整图标。底图稀疏不等于缺图。穿戴层的白灰布、金边、绿宝石和链带共同表达仪式护甲。

Items.<clinit>683调用registerDyeableSet，材质默认色0xB02E26。DyeableExtendedArmorItem先查display.color数字标签，缺少则取材质色；ClientMain.postLoad为coloredItems注册染色，lambda仅tintIndex≤0取染色，>0返回-1。因此原白灰底图不是最终默认游戏配色。

setupPieces433–515对下腿、上下躯干及披风使用colored，中间躯干glint；LayerPiece先以RGB渲染基础层，再白色渲染_overlay。Piece拼接固定textures/models/armor/{material}/{piece}{suffix}.png。

原生配方为对应robe部件升级，金锭构边；头盔绿宝石、胸甲不死图腾匹配图形用途。与holy_armor仍保持保守近家族关系，不把不同项目的金白配色直接算成独立新设计。

固定本地Jar、原始文件与Python解析哈希均保存。原图及原始UV矩形已实际查看；矩形裁片不等于最终有符号面/穿戴接缝验收。既有整套家族比较见historic-family-dedup.json，同套新增部位、附加层不计新设计，新增验收信用0。保留既有适用认可证据，总数与缺口仍未核定，1000门槛未成立。

待验：平台postLoad完整调用链；染色后最终整套视觉及面接缝；与holy_armor整套跨项目去重验收；真人实机与1000门槛验收。

289已认可与70优先资源哈希不变；未覆盖贴图、共享Jar或主清单；未运行Java或游戏，未操作用户实例、声音、屏幕和亮度。
