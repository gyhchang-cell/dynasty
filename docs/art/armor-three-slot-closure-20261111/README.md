# D31：三套候选原生静态槽链补齐

接续D30，固定三个原生注册类（含verbose BootstrapMethods），补齐12条注册名→工厂/构造器→实际槽→原生图标及getArmorTexture选用材质。They Are Watching四个构造器直接注册；Infectum和Poppy八个lambda工厂创建具体槽类。全程仅javap静态反汇编，没有执行模组或游戏。

Infectum四槽均返回entities/armor_layer1_1.png；红色testarmor_layer1/2不被本链选用，不能根据同名文件错接。

三个研究页使用固定Forge1.20.1原版HumanoidArmorModel/ModelPart的标准UV布局，查正面、45度、侧、背和透明孔洞黑剪影。Infectum/Poppy来源是1.19.2，因此明确只是标准布局对照，不称其版本原生运行验证；Armorv源为1.20.1，仍不称实机。研究atlas仅把两层原图叠放供软件分区采样，原图RGBA完全保留，不进入运行资源。

三套分别追加既有暗底紫嵌片、原版轮廓材质变体、链甲族；累计643已读名称/629盔甲名称/213保守学习组。新增独立设计信用0，1000门槛未达。未制作、覆盖、修改身体、删除清单或提交推送。289路径保护核验见verification.json。
