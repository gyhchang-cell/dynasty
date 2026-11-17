# D48：完整兽皮骨边甲原图与专用穿戴消费者

固定本地Radiation Zone Reborn 1.3.2.1 Forge 1.20.1 JAR。22条原生文件、13份只读反汇编与JAR哈希见provenance.json；实际查看四个16×16库存原图及一张128×64穿戴原图。whole-native-source.png只是整数放大原图排版，不是Dynasty成品或游戏截图，未复制进运行资源。

注册tyrant_skin_armor四槽分别经bootstrap121–124直接REF_newInvokeSpecial至TyrantSkinArmorItem$Helmet/Chestplate/Leggings/Boots构造器，再指向ArmorItem.Type对应部位；本套不是lambda$static供应器形式。库存模型使用tyrant_skin_helmet等短资源名。四槽getArmorTexture均直接返回entities/tyrant_skin_armor_layer.png，没有普通layer_1/layer_2拆分。

四个initializeClient扩展实际把专用层烘焙部件放入HumanoidModel：头head←Head；胸body←Body、left_arm←LeftArm、right_arm←RightArm；裤left_leg←LeftLeg、right_leg←RightLeg、body←Body2；靴left_leg←LeftLeg2、right_leg←RightLeg2。不能把裤腰Body2当胸Body，或把靴与裤腿当同一岛。CLIENT/MOD层定义事件bootstrap46绑定createBodyLayer，层声明128×64；保存19处原生texOffs起点及对应声明子件，不宣称已逐面/姿态核验。

实际材质观察：大片暗苔绿软皮承托白牙骨，白边集中于头口、V形胸沿、肩部和靴口；中间少量黄绿主面，避免骨白铺成栅栏。库存短宽胸与直腿仍接近MC轮廓，但骨缘阶梯比普通布皮更强。128×64原图中胸与裤腰、腿与靴的多个岛相互独立，不是两张64×32拼接。部分灰绿小块较散，不照搬为普通皮甲噪点。对待修皮/布袖口与织锦，借软硬材料面积和结束位置；不复制图像、专用几何或给人物身体加骨片。

去重：radiation_zone_reborn:tyrant_skin_armor及creature_hide_shell_vests组已存在，此轮把候选资源与四部位消费者补实，不增加名称、组或有效独立设计信用。累计654名称族/640甲名称族/215保守学习组不变；有效独立设计总数未核定，适用1000门槛未满足。

review.py验证固定原生条目/反汇编、四槽直接构造器与纹理/模型部件、层定义声明、19UV起点及289保护路径。实际事件/模型烘焙运行、逐面UV、遮挡、缝线和穿戴五视角仍待验；此轮仅作者阶段有限静态证据。新稿0、游戏启动0、清单删除0。原认可和精致旧稿未动，D2与PNC遗留范围继续保留，Main独立核收与主清单管理不由本专岗替代。
