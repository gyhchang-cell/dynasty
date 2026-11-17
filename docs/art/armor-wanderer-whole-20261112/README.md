# D59 流浪者布甲：完整四槽来源研究

固定官方 TeamMetallurgy/Atum2，master 的 877292afe7e704d42d1cfb726cbc9955be0ef409。仅解压字节，不编译/执行上游代码。gradle.properties 实读 MC1.20.4、NeoForge20.4.232、Atum2.3.0，不称 Dynasty Forge1.20.1 可直接加载。

原生 atum:wanderer_helmet / wanderer_chest / wanderer_legs / wanderer_boots。AtumItems173–176 四 Supplier分别 HELMET/CHESTPLATE/LEGGINGS/BOOTS；registerItemWithTab267–272 进入 ITEM_DEFERRED，再由Atum构造器及registerDeferredRegistries105–108绑定modBus。WandererDyeableArmor继承TexturedArmorItem，默认颜色14869989，display.color覆盖。AtumArmorMaterials完整实读，WANDERER修理材料是LINEN_CLOTH，不能因为金色边就说金属重甲。

四个完整item JSON只声明 item/generated 和layer0=atum:item/wanderer_<槽名>。已实际查看4个16x16原生引用图：白灰罩帽、金色额带及棕黑面孔空区；白短宽胸衣、金袖口，头胸略圆弧但大块像素；白直腿配金腰，棕色短L靴。不能将另8个wanderer_armor_*图自动当实际图标：本批解压保存但未目视它们，不给引用/查看信用。

TexturedArmorItem完整实读：hasRender默认false，这4注册未setHasRender；非LEGS选 wanderer_armor_1，LEGS选2，type非null追加_overlay；不存在自定义穿戴模型override。四幅实际图集均64x32，已逐页查看：底层白布大面、短斜灰簇，L1帽口留黑/透明间隙、躯干和袖；L2主要直腿与腰。固定覆盖层是棕头带/鞋底与棕腰，而图标是金腰/额带，**图标与穿戴配色不一致**，仅作身份一致性反例，不照搬。L1底层脚几乎空，鞋色由覆盖层承担，不能误认为缺失鞋图后随意填白。

ClientHandler57–112：MOD CLIENT订阅类，init内注册 tintIndex>0白、0读getColor；Atum.setupClient85–88直接调用init。当前4模型只有一层，所以不能假称它们已使用layer1免染金边。初始化线程/精确NeoForge消费者是否有效未运行验证。

已查看 active-native-01/02、4张context-uv页。标准矩形来自既有Mortem raw-standard-uv.json逐字引用并记录哈希；仅作head/hat/body/arm/leg原始矩形对应，1.20.4实际Vanilla/NeoForge选槽、染色覆盖及ModelPart几何源码未完整读到。尝试官方20.4.232标签patch返回404，未绕过TLS；不据此判模组错误，不声称完整运行消费者闭合。不对未见左右镜像/接缝/穿戴五视作验收。

应用于 cloth / sea_silk 的材料学习：布主面大、窄边少、图标保持短宽胸/双直腿/短靴；避免细棋格布纹与图标/穿戴异色。复用已读保存的开襟袍、毛领皮衣、青边长袍完整文字观察，非重新读旧像素，未全215组排重。Atum新命名空间不证明新独立设计；仅1完整候选族，独立适用/去重待Main验收，新增正式信用0。

D54已验1族首次承接在上一份新的 armor-material-three-20261112/combined-semantic-ledger.json；此处继承只计0追加，完整Main11/8及作者ACK不裁窄。全局total/gap null，gate false。无生产资产变更、无游戏、无清单删除。
