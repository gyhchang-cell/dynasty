# D82：Ender IO 黑钢甲完整四槽来源、原图和穿戴消费链

本轮只研究，不制作/覆盖 Dynasty 资源，不启动 Java/游戏，不改共享 Jar、主清单、session 或用户实例。研究对象是 `enderio:dark_steel/default_unpainted_no_faceplate`，四槽整体只作为至多一个待独立审查候选；新正式设计信用0。历史记录不清零，1000有效适用设计总数与精确缺口仍未核定。

## 固定来源和版本

官方仓库 https://github.com/SleepyTrousers/EnderIO-1.5-1.12 ，master固定提交 `9249b7e01fd73c7bc92a2fd60e768c1ef5b39fd3`。旧仓库API重定向到本仓库；一次1.12.2分支查询404，未用失败URL作为固定来源。实际gradle.properties声明Minecraft1.12.2、Forge14.23.5.2847、EnderCore1.12.2-0.5.76、版本5.3.0-alpha。不是当前Dynasty1.20.1依赖兼容结论。

22份选取原文件按Git树blob SHA1和文件SHA256校验。另从官方Forge Maven取得精确声明版本userdev.jar，以同源SHA1校验，并提取LayerArmorBase/LayerBipedArmor补丁和ForgeHooksClient；consumer-provenance记录嵌套归档入口及SHA256。Maven sources.jar查询404后改用实际存在的userdev.jar。未运行上游代码，未生成或加载其Jar。

## 实际查看六张原PNG

四张物品图16×16；两张穿戴图64×32。`native-icons.png` 和 `native-worn-layers.png` 仅为原生像素整数最近邻分析页，已查看，非游戏截图，也非本轮原创贴图。未缩改原始PNG。路径/哈希/透明区在original-image-paths.json。

- 盔图标紧凑、近方桶形，顶部仅一小阶梯；灰额/颊围近黑面区，左右有两点偏冷灰亮块。面区多数是深色实像素，不能把它当成透明面孔开口或白底删除对象。
- 胸图标短宽，两肩保留方阶、领口为深U凹口。上胸两个灰大面汇成V形，下腹横向暗带和一条较亮腰带把硬甲与连接处分开。不是细腰人台；可学宽面明暗，不照抄像素。
- 裤保留横腰、两条平直裤腿和大透明腿间隙；灰膝只占小区域，不铺满高亮线。靴是高筒加向外阶梯脚尖，两脚的透明间隔清楚；四图透明边距均保留。
- 穿戴两图都采用近黑底和灰块分面，但肩臂/胸面会出现密集小灰阶：只学主要灰面与深连接的面积关系，不把密点带入Dynasty粗像素盔甲。两图上左32×16区域外观不同，L1有较密闭横向面片、L2局部透明开口不同；本轮仅记录原始矩形像素差，不在缺少完整ModelBiped/ModelBox源码时宣称准确前/侧/顶/下巴映射。
- 原生亮度整体很低，缩到库存仍可辨灰胸，但穿戴暗处可读性需要真实光照验证；不能凭分析页调亮或判运行缺图。

## 从注册到原图的源码链

1. ModObject297–300将四个枚举绑定到四个createDarkSteel工厂。ModObject构造器调用sanitizeName，CamelCase转为item_dark_steel_*；IModObjectBase.getRegistryName以EnderIO.DOMAIN=`enderio`拼名，apply设置物品RegistryName。ModObjectRegistry的RegisterModObject事件注册枚举，Register<Item>调用其工厂并注册；EnderIO.preInit实际发出PreInit事件。记录的是静态源码路径，事件运行成功仍未验证。
2. 四工厂明确DARK_STEEL与HEAD/CHEST/LEGS/FEET；四模型JSON的layer0逐个指向对应items/item_dark_steel_*原图，parent为item/generated。没有用doc/textures/old旧图或End/stellar素材替代当前黑钢甲。
3. EquipmentData.DARK_STEEL声明texture1/2为dark_steel_layer_1/2；构造器拼enderio:textures/models/armor/，getter加默认空动画后缀与.png。EndSteel的动态帧override不适用所选DARK_STEEL，不另计动画帧设计。
4. ItemDarkSteelArmor.getArmorTexture按实例armorType判断：腿甲恒选texture2；无NightVision且无SoundDetector升级的头盔也选texture2；胸靴和有任一上述升级的头盔选texture1。不能以“头=layer1”的通常规则改写本套引用。hasUpgrade的NBT语义、真正栈和升级获取本轮未闭合。
5. 精确声明Forge2847的LayerArmorBase补丁调用getArmorResource，继而ForgeHooksClient.getArmorTexture调用物品方法并优先使用其非null返回；LayerBipedArmor补丁接入ForgeHooksClient.getArmorModel，物品返回null则保留传入的默认ModelBiped。普通未染绘头盔和其他槽在本物品方法中返回null。
6. 染绘头盔另有分支：PaintUtil.hasPaintSource或DSPAINT子Compound使getArmorModel返回不绘制的no_render；PaintedHelmetLayer读取绘制来源，通过头部postRender、平移/旋转/负缩放以TransformType.HEAD绘制来源物品。此分支已读，但额外升级渲染管理器/事件挂载未闭合，本轮不当成默认黑钢UV，更不另计一套。
7. items.xml四配方都是原生黑钢材料别名的盔/胸/裤/靴网格，输出准确四个ID；只核XML声明，DARK_STEEL别名解释、材料原产与真实合成没有实测。不会以普通铁装备或任意NBT栈冒充原生获取。

## 去重和适用范围

已核旧完整研究的全部29个whole键、1个全九模块重甲配置，以及215个历史学习组名和case注册。complete-old-whole-dedup逐项记录对比；closest旧组的原有观察完整携带在historical-group-comparison。此处复用已落盘观察，不谎称重看全部旧PNG。

最接近的是黑骑士暗甲族（暗铁/黑铁、V胸、灰额、长靴）及机械暗框族（深底金属面板和功能面罩）。黑钢的升级条件和材质路由很有技术参考价值，但代码分支不是新的美术语义。与Eidolon银甲、Tinkers板甲、Betweenlands两种矿物甲也共享紧凑四槽基础语言；与Electrum翼冠/翼靴有结构区别，金黑换色本身不独立。没有往旧学习组硬塞新信用，仅追加一个待审的完整来源配置，正式信用0。

可用于优先范围：黑钢胸宽、腰带连接、直腿和分离靴是普通金属甲的比例/材质阅读参考；不把现代升级功能移入Dynasty，也不依此重画已认可图标。七家族28个目标与70份优先资源仍按旧证据保留；本轮未发现获准可越过门槛制作的理由。

## 仍待验

- 与全部旧whole及历史组的独立适用性/语义验收，1000总数和缺口。
- 精确1.12.2原版ModelBiped/ModelBox完整面UV、slot显隐及最终镜像/接缝；本轮只闭合Forge钩子和物品路径，不套用1.20的面方向裁片冒充本版本验收。
- 真实原生栈、升级NBT与配方加载/材料获取；PaintedHelmet额外渲染分发的实际运行。
- 真实穿戴正面、45度、侧面、背面、灰模/剪影与动作。无图形/游戏启动，分析页不替代这些验收。

289保护文件与70优先文件哈希保持；没有制作快照批次、运行资产改动或提示词删除。
