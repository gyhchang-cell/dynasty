# D40 PneumaticCraft 两套新完整参考

官方 https://github.com/TeamPneumatic/pnc-repressurized ，分支1.20.1固定提交 `2639a983eb9e3352517aed6dc03994a50e84883f`。39份原生源码/JSON/PNG以Git blob与SHA256固定。缓存tree顶sha不作为额外rootTree证明。

实际看过两张原生分层页，共14张16px库存层与9张64x32穿戴图集，八个部位注册/物品JSON/主穿戴纹理静态核对通过。原图只整数放大展示；未合成默认染色，不是新稿或游戏截图。压缩铁甲克制灰阶、原版紧凑轮廓；气动甲以面罩、窄眼片、环扣、胸灯表达装置用途。材质与用途可学，不复制具体像素。染色、零散覆盖层和四部位不增加设计数。

PneumaticArmorItem默认底色/副色/眼片分别0x969696/0xc0c0c0/0x00aa00；layer2只有头盔染眼片，其余如胸灯白乘数。ColorHandlers自动注册ITintableItem。PumpkinOverlay只覆盖第一人称头盔遮罩，不能据此断言排除所有外部穿戴渲染。额外translucent/eyepiece图集虽已看，其调用链未闭合，原生完整穿戴另验。

两套名称加入既有原版材质和机械暗框学习组：累计654名称、640盔甲名称、215保守组，新增有效独立设计信用0，适用1000门槛仍未满足，待独立图审。不提前生产。289保护路径无变化，没有开游戏/Java、修改共享Jar或删除清单。

本轮前置D39 Ars默认namespace工厂和骨层级源码边界已单独固定在 armor-ars-factory-closure-20261111；反射/第三方/运行时及Geo实体仍不宣称排除。下一步继续不同完整盔甲实际原图阅读，复用有效证据，不再扩展旧helper。
