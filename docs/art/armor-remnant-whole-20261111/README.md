# D46：灵钢面罩甲整套原图与调用核查

固定本地Sons of Sins 1.20.1-2.1.6 JAR，原始来源和22个条目哈希见provenance.json。实际查看7张原始PNG：四库存图、两张64×32穿戴图和头盔专用64×64图；whole-native-source.png仅整数放大原图排版，不是Dynasty新稿或游戏截图。胸库存16×48包含三帧，各16tick、插值；三帧不拆设计数。

四个remnant注册请求经bootstrap13–16→lambda$static$1–4→Helmet/Chestplate/Leggings/Boots构造器→ArmorItem.Type，库存JSON指向soul_steel命名图片。此前soul_steel候选是既有sons_of_sins:remnant整套的资源命名，不新增名称族或独立设计。完整面罩/绿芯设计组已有历史读图，复用其适用证据。

**关键穿戴区别**：头盔getArmorTexture直接返回entities/soul_steel_helmet.png。initializeClient扩展通过烘焙Modelsoul_steel_helmet.LAYER_LOCATION取head放进HumanoidModel，其余hat/body/四肢均空。CLIENT/MOD层定义事件以bootstrap5绑定createBodyLayer，模型声明64×64，记录9处texOffs起点。头盔不是标准L1的头部裁片。胸和靴直接返回soul_steel_layer_1，裤返回layer_2；选定这三个类和父类未声明自定义盔甲模型扩展，默认路径上下文复用D44，未验实际运行。

实际学习：面罩用平横顶和多层灰带维持紧凑形状，暗红边不满图碎亮点；短宽胸甲仅绿芯集中识别，短裤与长护胫分开。适用于袖口布/硬片的宽窄分区、强甲集中识别点。只学习材料组织，不复制原图和模型。64×64头部稀疏岛与64×32普通穿戴不能混用；库存动画不证明穿戴会发光。

review.py通过原生JAR/条目哈希、四槽有限注册和消费者、模型层声明、9处UV起点、289条保护哈希。逐面UV、烘焙后的遮挡/姿态、实际事件和实机穿戴五视角仍未验。没有把源图排版当穿戴验收。

累计654名称族、640盔甲名称族、215保守学习组保持不变，独立设计总数未核定，1000门槛未满足。本批新游戏贴图0、游戏启动0、清单删除0；获选和精致旧稿未动，D2袖口/旧L2/材质及PNC遗留待验保持。专业记录仅本地，Main另行独立核收与管理主清单。
