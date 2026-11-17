# D43：长袍分层贴图片参考

固定本地 immersive_armors 1.7.2 Forge 1.20.1 JAR。实际查看19张原图，排成3页；16份只读反汇编用于指定方法核对，不是16个设计，也未执行模组。原图只供研究，不复制到Dynasty。四件图标注册请求、四个额外穿戴贴图片及8张底/覆盖图消费者见 static-piece-consumers.json。

区别上一批甲壳专用128图集：长袍附加层用64×32布局与不同扩张参数，在现有HumanoidModel上按槽设置可见部件。两类body片用于HEAD/CHEST/FEET槽列表，两类leggings片用于LEGS列表。不能把upper字面理解为仅胸部。实际可见几何仍由槽遮罩限制。

关键学习：灰白布面染色，金边/腰带独立overlay保持白色乘色；body_middle与leggings_middle图集只有很少像素，leggings_middle底图原生全透明但overlay非空，不能把空底判成无用图片。原图细碎布纹偏多，Dynasty只借分色/分层方法，保留更大像素簇；不照搬图案与几何。

核对范围：Items.registerDyeableSet的四个实际bootstrap/supplier/ArmorItem.Type，注册闭至跨平台Registration.register请求；ItemsClient的ROBE_ARMOR片列表、各片构造器纹理名、Piece.getTexture路径拼接、LayerPiece.render染色与覆盖，以及Mixin遍历实际装备材质getPieces并调用Piece.render。native Minecraft命名空间的4张常规layer图已查看，但原版主层消费者/Forge平台实现与加载生命周期未独立闭合；混入注解的映射签名/refmap匹配仍待核。

未五视角/逐面UV/穿戴或游戏验收。已审654名称族、640甲名称族、215保守学习组保持不变；本轮是既有robe族消费者资料补齐，独立设计信用0，1000门槛仍未满足。289个保护资源哈希未变化；未制作、未改生产资源、未启动游戏、未删清单。Main独立核收后统一处理清单。
