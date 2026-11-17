# D54：木条/林地整套甲的材质与专用UV研究

接续D53银甲，不停在单一候选。本批只读Roots旧版原稿与固定源码，未制作或覆盖Dynasty资源。两套各有原生四槽，共8个物品ID；为保守去重仅作为一个待验的枝木/浅片材学习族，不把两套、10张PNG、113个长方体或28种取样区域当作独立设计数。新增已验收设计信用0。适用1000门槛未达，实际已验适用总数与确切缺口未知；历史有效依据不清零。

官方来源 https://github.com/MysticMods/Roots ，固定提交 `27dc32ecf4dfffbc67790bc69ed0b405137dee2f`，分支1.12.2，原版信息3.1.9.1。此旧版本用于美术/布局参考，不能直接作为当前Forge1.20.1运行证据。固定ZIP、29个原条目哈希、许可证与三份依赖上下文源码保存；没有执行外部项目。

## 实际看图与可借鉴处

已实际查看 `native-source-images.png` 的四件wildwood、四件sylvan和两张64×64穿戴图；以及 `wildwood-raw-net-patches.png` 的15种和 `sylvan-raw-net-patches.png` 的13种原始方块取样区域。分析页只整数最近邻放大原图，非新作、非游戏、非最终朝向面/穿戴效果。

wildwood头件用两侧上挑枝节和中央长木鼻片，眼口留暗/透明开口；胸件是左右成对木板、中央宽竖木片及分离的肩节点。裤件两条膝护有粗木横节，不画成人体裤腿；靴件小木枝伸出筒口，底部仍保留两只方脚。主体用橙褐木节和黄褐木板区分，深褐集中于间隙、底端；长木条以连续竖向浅带表示年纹，不靠密细木纹。可用于学习竹/木类的材料身份与窄接缝，不能把17个头部枝块和60块几何复杂度当作目标。

逐块取样进一步区分了相同UV起点下不同尺寸的取样：48,16的2×8/6/4木条共享竖向木纹，而0,16的枝节取样更橙；胸板16,16用分叉浅边与较暗正面，末端帽与木块16,32采用环周明暗。不把同一图集上的不同尺寸取样错误归成同一有效UV岛，更不把这些小块当作15个设计。只学习方向明确的粗纹和材料分区，不复制纹样。

sylvan主体为浅灰米色护片，绿色衬料主要在护额、裤/靴口，木枝褐色仍作为固定件。胸前花饰是少量蓝白、红黄、紫绿像素簇形成三处焦点；图标没有把全身涂成发光虹彩。腿部浅片长而直，与两侧木固定件分开；靴筒口绿色和深色底边承接全套材料。原64×64图集的浅片材存在细密交错明暗/棋盘式纹理，这部分不适合直接作为Dynasty成稿标准，应该学习面积关系而避免照搬噪点。大的头侧枝角、袖口细枝与多片外翻也不适合普通盔甲比例。

两套四图均以原生16像素簇组织，仅作为参考尺寸。Dynasty获选原稿依旧保留原始分辨率，绝不据此缩成16px或强制减色。

## 原生注册、图标与穿戴链

RegistryManager的RegisterContentEvent回调调用ModItems.registerItems，八条event.addItem分别构造ItemWildwoodArmor或ItemSylvanArmor，并传入真实HEAD/CHEST/LEGS/FEET。构造器设置 `Roots.MODID + name` 注册名。四件物品模型各自generated，layer0为 `roots:items/<id>`，与当前1.20.1常见的item单数路径不同，不能猜路径。

两类物品的initModel均调用ModelLoader.setCustomModelResourceLocation(id, "handler")；getArmorTexture返回各自专用64×64纹理，四槽共用一图而不是普通layer_1/layer_2。getArmorModel回调传入真实armorSlot，模型getInstance按ARMOR槽位验证并逐槽缓存。子类分别构造60和53个长方体，归head/chest/armR/armL/legR/legL/bootR/bootL八根。原始构造参数、parent关系、旋转和取样范围保存在box-texture-correspondence.json。

Wildwood胸子件Y再减1，双腿/靴子件Y再减12、根初始Y为-12；Sylvan头子件Y再加1，腿靴同样修正。最终父类还按姿态重新设置根位置，不能把初始偏移当最终世界位置。armorScale分别1.2/1.1，因此“模型只是原版大小”也不是成立的说法。

## 依赖上下文与不能宣称的部分

固定MysticalLib上游提交 `71f61b7ac70d0a4c607319cbf82960354a1cd79e` 的RegisterContentEvent.addItem实际append列表；LibRegistry.initAll发事件、registerItems把列表注册进实际物品注册表，ModelRegistryEvent遍历IModeledObject.initModel；ModelArmorBase构造器在子类addBox前设置64×64，render先更新姿态再按槽位控制八根showModel并实际render。三份固定源的URL/SHA已记录。

Roots只声明MysticalLib最低1.13，未固定实际加载版本；因此这三份源码是有界依赖上下文，不是实际客户端加载证明。未运行"handler"模型变体解析。源码每个ModelRenderer都在addBox之后才写mirror=true；最终字段不能自动当作已烘焙方块镜像状态。未验证那个精确版本ModelBox构造时机，所以本批仅保留mirror赋值顺序，不生成伪造的世界面镜像验收。取样页是原纹理范围，不宣称当前1.20.1箱UV或最终面朝向。

五视角穿戴、接缝、镜像、姿态与旧依赖实际版本均待验；原始像素/程序链完整不代表全部正式验收。

## 去重、当前目标与保护

已对照历史木板甲、铁木铆接、钢叶、植物头饰、巨魔皮革、骨羽肩带等学习族的具体记录。两新套不是简单像素换色，但木/叶/骨材料语言与旧族有交叠，故保持一待验族，未新增独立信用。对照原记录在dedup-comparison.json；不声称重新看完全部旧图片。

当前Dynasty目标延用D52的七个历史静态问题家族及28个真实ID（current-dynasty-targets.json），图标已改不等于wearUV已改，静态问题也不自动许可重画。精致老稿和已认可图标继续保护。289个保护文件逐项与基线一致，未改身体/骨骼/程序/任务/主清单，未碰游戏、共享Jar、原存档、声音、亮度或屏幕状态。
