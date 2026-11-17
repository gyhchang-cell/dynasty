# D88：三套新来源的 MC 护甲研究

本批继续优先盔甲图标与穿戴 UV，实际研究唤魔长袍（evocation_robes）、佣兵甲（mercenary）、强化锁甲（reinforced_mail），不是再重复旧套装的 UV 路径追踪。三套都保存四个图标、原生穿戴图集、geo 和物品声明，但 **3 个新来源完整四槽案例不等于 3 个已验收语义不同设计**；与旧帽袍、皮革金属护片、锁甲组仍有重叠。本批新增独立验收信用 0，1000 适用独立总量及精确缺口未知，未生产贴图、未删任务。

## 固定来源与实际看图

官方 Infamous-Misadventures/Dungeons-Gear 提交 `9ba0075c5b2f13ef54ec914ad1327a853ecdce6f`，根树 `78bd91fc3217fe58cd2fd5e9ce39e01c48261162`。41 个选定文件的 Git blob SHA-1 与 SHA-256 均验证。源码声明 MC1.19.2 / Forge43.2.8 / 模组5.0.6-beta，依赖 Dungeons Libraries3.0.10-beta、GeckoLib3.1.40。

实际逐页查看三张研究页内的 **12 个原生16²图标＋3张原生穿戴图集＝15张PNG**。唤魔图集160×65，另两套96×64。研究页是他人原图整数最近邻放大，不是 Dynasty 原稿、游戏截图或可交付新美术；原始 PNG 未改尺寸、像素或透明度。没有把15文件、12部位或36盒子计作36个设计。

图标的12份 generated JSON 均完整读过，全部 `minecraft:item/generated`、单 layer0，并逐个核对至实际 PNG。三份 gearconfig 完整读过；长袍为cloth，两套甲为heavy_plate，不能按画面有棕色就编成皮甲。三份 geo 的节点、父级、尺寸、旋转概要人工查看，完整原始声明随源保存；所有 UV 数值机械记录，不宣称人工逐像素检查或实机五视图通过。

## 三套的具体学习与限制

- **唤魔长袍**：蓝帽/棕带/黄扣，蓝底黄衣缘和暗红中襟，蓝直腿、棕靴亮口，整体靠大色区而非雕花辨认。16×1×16帽檐、高帽及折顶是法师专属结构，不能用于普通布皮甲；长襟、亮靴口也不作普通短甲/靴的硬模板。与旧 wizard_hat_robe_variants、immersive_robe_open_front 比较，衣缘原则已存在，不因新名字或配色自动获信用。
- **佣兵甲**：灰盔短鼻梁、单侧钢肩和棕背片、斜胸护片与小腰带让材料主次清楚。胸子骨28度旋转，头/身体仍8×8×8、8×12×4基础；右臂与左臂用不同护片。裤图标仅两个膝片，缺少腰连直腿，是本项目裤甲可辨性反例。与旧 complete_hard_leather_metal_shoulders 对照，结构差异待独立语义核验，不能按棕皮/灰肩另算一套已完成研究信用。
- **强化锁甲**：盔额横条和两侧颊片保留开口；胸深灰锁网、灰纵片和棕下缘分工明确，两块5×4×2护片附属胸主体。裤图标仅棕腰带，靴图标短扁，不适合用户指定完整腿型/短直靴比例。锁网细棋盘只能用于相应材质局部，不能给普通布皮添加噪点。与旧 magistu_chainmail_rust_family 的粗网格/皮边重叠，保留反例和待验候选，零新增信用。

## 四槽绑定与消费者边界

ItemInit 的 `registerArmorSet` 将名称接 `_armor`，显式构造 `geo/armor/{name}_armor.geo.json`、`textures/models/armor/{name}_armor.png`、默认动画，再注册 HEAD/CHEST/LEGS/FEET 四个 ArmorGear。三套入口实际读过。默认分支 animated=false，因此源码引用的是 Libraries 的 `armor_default.animation.json`，不是凭空为每套声称存在独立动画。

为核对后续消费者，另固定 Dungeons-Libraries 提交 `28bd58c43ac1bf18ad421a2dd943eb756e8e0076`，6个文件各有根树blob和SHA验证。完整读过 ArmorGear、ArmorGearModel、ArmorGearRenderer、ClientEventBusSubscriber 和默认 idle JSON。getter传递模型/贴图/动画，CLIENT MOD AddLayers 注册 GeoArmorRenderer，客户端扩展调用 applyEntityStats/setCurrentItem/applySlot；渲染器对cloth的Body做0.93 Z缩放。

**该消费者分支声明 Libraries3.0.12-beta、GeckoLib3.1.39，与 Gear 请求3.0.10-beta/3.1.40不相同。这里只证明分支上下文，不声称请求版本或实际运行二进制一致。** 未下载或启动游戏；未用软件渲染冒充穿戴。完整消费者版本等价性、Gecko骨名/槽位可见性与最终姿态仍待核。

`three-whole-bindings.json` 保留全部源geo、父子结构和每个源盒。11／15／10盒子的父级存在、无循环、图集声明与PNG尺寸一致，常规Bedrock列表UV的名义展开包围范围均在对应图集内。这只是静态范围检查；不等于 signed face、mirror、inflate、pivot、旋转后接缝或最终穿戴验收。

## 保护及待核

289精致保护项及70优先资源哈希在冻结时与当前文件核对，保持不变。旧D54等已保存证据不清零；ledger仅追加三套待验记录与新prior链接，不改任何旧分组或信用。

待核：适用1000独立参考门槛；三套与旧完整视觉案例的独立语义对照；请求消费者版本匹配；实际渲染/五视图/黑剪影/接缝；原生材料、战利品与获取付款。优先目标尚无同时“未重做且简陋”的确证，不借旧穿戴待验重画认可图标。未改主清单、session、共享Jar、身体/骨骼、存档、声音、亮度或焦点。
