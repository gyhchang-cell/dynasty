# D76：Thermal防化服完整设计研究

本轮继续未读的完整相关设计，四槽为 `thermal:hazmat_helmet/chestplate/leggings/boots`。固定官方CoFH/ThermalCore提交 `cc7c230146a71d177767a8f9d6b26f0a52e9aeed`，补读官方CoFH/CoFHCore提交 `dcd7bd6703418ee2e8eb2185957de83925fa89fe`。所有下载文件校验Git blob SHA-1及SHA-256，来源见provenance。没有执行上游代码或将参考资产装入Dynasty。

## 来源和实际消费者

最初筛查ThermalFoundation的 `069620a664e07e6ac72bbef0fed33ecbfe1846e5` 完整tree，未见hazmat资源；实际来源在ThermalCore，保留两份完整tree及commit响应，不把仓库名称猜测当来源。ThermalCore版本实读为MC1.20.4、NeoForge20.4.237、11.0.7；同分支CoFHCore版本11.0.2与声明依赖名一致，但尚未证明与解析到的发布二进制完全相同。

已读TCoreItems四个构造注册、ThermalIDs原生字符串、RegistrationHelper的ITEMS.register和ThermalCore的TCoreItems.register/ITEMS.register入口。四件均为HazmatArmorItem，HELMET/CHESTPLATE/LEGGINGS/BOOTS，材料HAZMAT名称 `thermal:hazmat`；材料类getName返回该名，修理物为hazmat_fabric。四份实际图标模型均 `minecraft:item/generated`、单层layer0，引用当前四张16×16原图，不从名称臆造纹理路径。

HazmatArmorItem、ArmorItemCoFH、ArmorMaterialCoFH、ArmorFullSuitModel全文实读。客户端扩展明确：LEGS/FEET沿用传入默认模型，HEAD/CHEST改用ArmorFullSuitModel。该类从HumanoidModel.createMesh继承主体，替换头/hat为8³盒、变形outer.extend(0.5)，双臂4×12×4、变形outer.extend(-0.5)，左臂mirror；图集64×32。CoFHCore构造器监听entityLayerSetup，其registerLayerDefinition挂同一模型层。INSTANCE实际是烘焙该层的HumanoidModel，不因类名就推断另一套动画。

两张穿戴原图均64×32；材料默认层选择可推导护腿layer2、其他layer1，但当前批未完整固定精确1.20.4 Vanilla/NeoForge消费者、最终常量与渲染路径，所以这里只作受限来源绑定，不冒充该版本穿戴/接缝运行验收。ArmorItemCoFH的另一个getArmorModel方法不等于已证明覆盖了客户端扩展选择；具体默认分支与外部注入仍待验。

四份配方以hazmat_fabric为主要材料；fabric配方是cured_rubber与forge:string。配方带 `cofh_core:flag_set / thermal:hazmat_armor` 条件，不能把JSON存在当所有安装配置都能获取。原生指南用途是防环境危害、需要整套达到完整保护；本批未运行验证数值或获取。

## 实际看过的像素与应用观察

已逐页实际查看4张原生图标、2张穿戴图，及60个原始UV矩形的诊断页。页面为原生PNG整数倍最近邻放大或原始矩形展示，不是游戏截图、五视穿戴或精确模型重建。

1. 本固定版本是红橙主体，不是黄色防化衣。面罩是浅灰粗阶梯近圆外轮廓、低位深灰呼吸区和下方黑领；身份靠大块结构表达，而非装饰花纹。
2. 胸衣保持短宽双袖、黑色短领和腰端，胸口一个大黑矩形接口。暗红外缘与橙亮面分成少数大块，缩小后主要部位仍能识别。
3. 裤子以红腰连接两条直腿，黑暗内缝建立负空间；靴子使用黑色短筒和方鞋头，小红筒口连回衣裤，不画圆鼓鞋或巨大肩甲。
4. 图集头部正面矩形有大浅灰面罩，周围黑色罩体；背侧用深黑蓝棋格簇表示柔性材料，不能照抄成Dynasty布衣的细密噪点。
5. 胸部正背均有黑色方接口，周围红橙大面，袖端和下摆由黑色区域收束；图标中的胸前黑块在UV也有对应，有助于保持名称/用途/穿戴身份一致。
6. layer2腰与腿继续红橙材质，layer1腿区域主要提供黑靴；不能把头/手臂在layer2为空、hat区域为空直接当成缺图。
7. 专用头部与袖部变形说明“相同64×32布局”不等于穿戴体积相同。迁移纹理之前必须核实实际模型消费者，不能把参考的大面罩比例强塞到现有Dynasty默认头盔。
8. 对cloth/leather/sea_silk可借鉴少量大材质区、袖端/腰线和部位连续性；竹甲/织锦/朱砂可借鉴图标与穿戴标志对应。防化面罩、红橡胶身份不适合直接套成古代盔甲；不因此重画已认可原稿或修改身体模型。

## 去重与保留的条件

旧账本已有alexscaves:hazmat和radiation_zone_reborn:protective，分别保存黄色防护衣和暗绿面罩束带的观察。先前名称筛查将本案暂归黄色防护服的假设，已被本轮红橙原图推翻；保留更正，不靠颜色差异授予新信用。旧两套只复用已保存观察，未假称重新查看其原生图。需要主协调比较材料、面罩结构、接口和全套设计后再决定是否独立、是否适用于当前旧盔甲。

本案最多1个待审完整族；四件、6PNG、60矩形、头胸专用分支和来源行数都不拆算设计。新增正式信用0，全局有效总数和精确缺口仍null，gate=false。

本轮另查重法拉第，发现来源提交与旧工程护甲研究完全相同，停止重复；D75只保存排除记录，不算新完整参考。Hexerei Orc/Druid的四槽注册是注释，未将候选PNG当有效四槽设计。这些筛查不替代本案实际像素研究。

289保护及70优先资源哈希前后不变。保存用户要求全文及批次说明，不启动Java/游戏，不碰用户实例、存档、共享Jar、声音/亮度/焦点，不删提示词或改主清单。下一步继续其他未读完整相关设计；不研究本案换色来凑数。
