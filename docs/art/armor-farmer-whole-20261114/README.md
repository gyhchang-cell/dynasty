# D94 农夫整套参考：四部位及分层穿戴消费

本轮仅参考研究，未制作/覆盖贴图。当前仍无新确认的“未做过且简陋”重画授权目标；保护289已认可资源与70优先路径，前后哈希一致。没有游戏、屏幕、声音、实例、共享Jar或主清单操作。

固定本地 Kaleidoscope Cookery 1.2.1 Forge/MC1.20.1 二进制，来源与SHA见provenance.json。已实际查看5张16×16图标、2张64×64草帽图和两张64×32农夫穿戴图；来源原稿保持原像素。进度 farmer_set 与 farmer_armor/straw_hat 标签明确支持草帽＋农夫胸/腿/靴完整搭配，不是临时拼头盔。

注册bootstrap26–30→工厂16–20→三件直接ArmorItem和独立StrawHatItem。材质名cookery_farmer无命名空间，复用已固定Forge47.1.0源码上下文可解析minecraft:…layer_2（腿）/layer_1（胸、靴）；帽子明确覆盖纹理/模型，自己的64平方图集，注册层bootstrap4接StrawHatModel.createBodyLayer。上下文版本符合模组声明47+，不等于该整合包真实加载版本或运行验收。

原图腿UV相对条负控：L1各20/48不透明为棕靴片，L2各32/48为蓝裤片；胸前背候选矩形L1各88/96与86/96，L2只40/96腰区。草帽3个Cuboid/平面、15宽檐、负UV和1.275缩放是职业衣装反例，不照搬为原版紧凑U形头盔。矩形研究仍不等于方向/镜像/接缝或实机穿戴通过。

完整重看历史同族两版本6个图标记录＋4个穿戴记录（两穿戴在版本间相同），逐文件和原Jar哈希核对。4张草帽相关新增证据补齐同旧家族；花带、版本、部位、配方均不新增独立设计数。新信用0，保留已有适用认可记录；总有效设计数、距1000缺口仍null，gate=false。

未删除提示词。详见four-slot-binary-bindings.json、semantic-review.json、historic-family-dedup.json、raw-uv-strip-facts.json和actual-review-scope.json。
