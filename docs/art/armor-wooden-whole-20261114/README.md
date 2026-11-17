# D101 immersive_armors:wooden 整套参考补证

完整四件图标和七张穿戴/肩片原图已查看：深棕木材大块阴影、红褐胸前交叉绑带、少量灰箍；头盔倒U和裤靴分离清楚。长靴、外伸肩片仅作比例限制例，不照抄。

旧记录只看胸和裤，本轮补足头靴及实际穿戴叠层；仍是wooden_plate同一旧家族，不计新设计。与巨魔皮甲骨角、铁木小铆钉、森格尖牙负空间是不同材料组织。

实际Items注册Set以wooden材质名构造四件ExtendedArmorItem，四工厂分别HEAD/CHEST/LEGS/FEET；注册命名空间immersive_armors，受enabledArmors配置控制，完整平台注册生命周期待验。

不是仅看基础两层即可：ItemsClient.setupPieces572–637给下半身leggings_middle(.5)、leggings_upper(1)，上半身body_middle(.75)、body_upper(1.25)，胸甲另加ShoulderModel。upper会绑定HEAD/CHEST/FEET，lower绑定LEGS；Piece按材质名/片名取实际附加纹理。

ShoulderModel两个1×8×7长方体共用uv0,0、16平方图集，左右姿态不同；基础层64×32上下文不代替1.19.2完整原生网格验收。

已逐片查看原始UV：body_middle胸前80/96、背90/96；body_upper胸前背各60/96；leggings_middle四腿条各32/48，upper四条8/16/8/8。基础layer1胸前82/96、layer2腿各36/48。叠层留白不能当漏贴自动修补。

固定本地Jar、原始文件与Python解析哈希均保存。原图及原始UV矩形已实际查看；矩形裁片不等于最终有符号面/穿戴接缝验收。既有整套家族比较见historic-family-dedup.json，同套新增部位、附加层不计新设计，新增验收信用0。保留既有适用认可证据，总数与缺口仍未核定，1000门槛未成立。

待验：1000适用独立语义参考验收；确定未改且简陋的Dynasty目标授权；1.19.2原生base图层消费与平台/mixin完整生命周期；实际穿戴有符号面及叠层接缝验收。

289已认可与70优先资源哈希不变；未覆盖贴图、共享Jar或主清单；未运行Java或游戏，未操作用户实例、声音、屏幕和亮度。
