# D87：蜜蜂盔甲完整四部位新来源研究

本批只做参考研究，未改 Dynasty 运行贴图、物品、人物模型或任何存档。已保护的 289 项及 70 项优先资产将按现值复核。没有删提示词、覆盖共享 Jar、启动 Java、操作屏幕或声音。

固定官方来源：TelepathicGrunt/Bumblezone，提交 `727844606bf41de151af9ae71e82caeaa72d04ce`，实际根树 `67afb61216ffb3a3563acdbad929273d3668b25a`。48 个下载文件逐个以根树 Git blob SHA-1 和本地 SHA-256 核对；下载不等于全部阅读。源码声明 MC 1.20.6、NeoForge 20.6.82-beta、Bumblezone 7.5.3；不是 Dynasty 的 Forge 1.20.1 运行验收。

## 实际看图与阅读

实际看过正常 variant1 四个原生 16² 图标、裤/靴两个原生覆盖图、两张 128² 穿戴图集，共 8 张。`upstream-source-study.png` 与 `upstream-overlays-study.png` 是他人原图的整数最近邻放大研究页，非新作品、非 Dynasty 资源、非游戏截图。原始 PNG 未改动。其余下载的 variant2/trans 图标未宣称看过或完成研究。

完整阅读 BeeArmorModel、BeeArmorModelProvider、ArmorModelProvider、ForgeArmorProviders、BzArmorMixin、RegisterArmorProviderEvent、BeeArmor、BzArmor、BzArmorMaterials；BumblezoneClient 只读事件/四槽 provider/layer supplier/pollen 属性相关段，BzItems 只读四槽与配色注册段，四个具体物品类只读构造与本研究涉及状态接口，不宣称通读玩法。四个 variant1 item JSON 和两种花粉子模型完整阅读。

## 可应用观察与限制

头盔仍有紧凑倒 U 开口，深颊收束亮黄额；胸以横向黄棕大区及白翼区别于普通金属胸甲；裤保留黑色直腿、金腰带和少量边点；靴以暗筒和小扣区分，不画圆鞋头。黄色原图含细碎蜂毛纹理，这部分不作为 Dynasty 普通布皮模仿目标。学材料主次和状态清晰，不能复制触角、翼片或图案。

关键绑定已从源码确认：`bee_material_layer_1/2.png` 的数字取自物品的 `variant`，不是原版 LEGS 与其他槽的 L2/L1 选择。正常 variant1 四槽共用第一张 128² 图集；trans 另走配色路径。每个注册物品新建 provider，getModel 缓存槽位模型并设置 variant；texture getter 使用缓存的 variant。NeoForge 的实际调用先后与 Mixin 生效仍待运行验证，不把静态路径当客户端成功。

花粉裤：pollen 属性 0 选择 base-only，1 选择 base+overlay；穿戴代码按状态显示两侧花粉袋。靴 base+overlay 有两个小金扣。胸翼按飞行组件改变旋转，未测运动。renderToBuffer 是每槽单独渲染子树：头、身体或腿；不能只看 visible=true 就声称 inherited hat/arms 实际渲染。

记录两种源码模型的明确声明：variant1 37 个盒/平面声明，其中 19 个零厚度；variant2 35 个，其中 19 个零厚度。18 个是两侧阶梯翼片，另一个是身体后方刺片。`explicit-model-declarations.json` 保留各声明 UV 原点、尺寸、deformation 与 PartPose。它不含继承的 HumanoidModel 网格，也不是 MC1.20.6 实际面投影、最终 UV 朝向/接缝或穿戴验收；没有把盒数、平面数当设计数。

## 语义去重与下一步

此前 ledger 没有 the_bumblezone 来源；已有 `terra_equipment:bee` 只有保守归入普通材料模板的黄棕蜂甲记录，本批读过其原观察。新套的触角、独立阶梯翼、真腿/靴节点和花粉状态构成一个完整四槽候选，尚待独立语义比较与适用性验收。variant2、trans 换色、花粉状态与四个部位均不额外计数。

这次保存 **1 个新的候选完整设计，新增已验收信用 0**。全球适用 1000 项的独立总数与缺口仍未知，gate=false；D54 等历史有效收据原样保留，不清零、不虚增。70 个优先资源中仍没有目标被证明同时“未重做且简陋”，不能为凑制作量重画精致稿。

待核：完整启动/Mixin 配置与实际渲染调用顺序；MC1.20.6 继承网格和最终 UV；四槽实穿五视角/黑剪影；实际获取与付款/修补来源；旧蜂甲及防蜂服完整视觉语义对照；独立信用验收。所有待验任务继续保留。
