# COD4-12 十种全局战斗反馈静态查漏

本次只读核对原请求、当前源码和既有验收记录；未启动游戏、未改正式源码/资产/待办。所有新增文件均在本目录。静态结果不能证明画面可辨识、声音听感、精确动作时长或完整整包观感；本报告不建议据此删除任一整项。

结论：十项均已有部分事件/网络/粒子或独立视觉实现；没有一项可以把**整项剩余**都归为“只是没截图”。逐项存在动作、特定文字/数字或覆盖链缺口，同时有已实现子项只差验收。不得把已有部分抹成“完全未做”，也不得把类型常量、网络队列或几何非空算作精确表现通过。

## 原请求与行号

权威内容使用 `docs/cod4/request.txt:334–351`，十项逐行在339–348。当前磁盘阴气/阳气在270/271；历史消息称272/273，存在版本行号偏移，按行内容归属，不按旧编号机械匹配。`docs/cod4/audit-20261022/cod4-before.txt:109–110,144–153`仅辅助对照后续待办，不代替原请求。

- 阴气：至阳体质免疫、暗雾绕身、服务端权威和视觉同步；阳气：阴体免疫、金辉、同上。**这两项没有灰色“免疫”文字要求。**
- **Boss Immune（request:348）才要求“免疫”灰字、弹开微光、嗡鸣、Boss不受控制和防刷屏。**普通体质type9原生粒子回执可作为已有反馈，不新增普通玩家灰字制作门槛。
- 状态破势（request:277）要求脚下晃影；全局Stagger（345）另要求踉跄、闷哼和后摇。不能把脚下环已实现说成全局动作完成。
- 全局禁止（350–351）：强制镜头转向、大幅持续震屏、全屏纯白；服务端决定类型与目标广播，不改他人Camera。按原文保留，不加“所有方向永远不被遮挡”等门槛。

## 共享生产→网络→客户端链

以下Java路径省略共同前缀 `src/main/java/com/dynasty/`；其他路径相对仓库根。完整编号副本及哈希见 `source-evidence.txt`、`source-manifest.json`。

**CF链**：`expansion/CombatFeedback.java:46–62`监听最终正伤害，排除取消/合成伤害，基于捕获的Dynasty武器/箭矢来源分类普通、蓄满重击和原生暴击；其全局覆盖目前有Dynasty武器过滤（51–52），不能推成所有原版/第三方攻击已自动接入。其他专门生产者见逐项表。`send:28–44`按受击目标位置和维度32格NEAR广播，三tick同/低优先级节流，高优先级可覆盖。`network/CombatFeedbackNetworkRegistration.java:14–16`固定消息16、PLAY_TO_CLIENT、schema2；`CombatFeedback:64–73`编码type+两个位置、校验后客户端主线程转`ExpansionClient.feedback`。

`expansion/ExpansionClient.java:57–90`每客户端世界tick总预算128粒子；普通4、其余通常12粒子，Heavy半径1.3，其余.55。Critical/Perfect使用CRIT，Armor使用ASH，其余这十类落ENCHANTED_HIT默认。声音Block/Perfect=SHIELD_BLOCK（Perfect音高1.5），Heavy=PLAYER_ATTACK_STRONG，其余=PLAYER_ATTACK_CRIT，音量.25。**存在播放调用不等于听感已满足原文；也不能把原版资源复用本身判为失败。**预算提前return会连声音一起略过，三tick节流亦是实际边界，不能承诺每个反馈都播放。包没有目标entityId/动作时钟/材质/伤害数值/普通免疫与Boss免疫语义字段，消费端只粒子和声音，不驱动躯体/文字。未来修复可复用其他原生状态，不意味着必须扩包。

**CV链**：`network/Cod3NetworkRegistration.java:14–16`消息12、PLAY_TO_CLIENT、schema1 → `cod3/Cod3VisualPacket.java:11–22`（维度、实体ID、开始tick、时长、序列、tint）→ 独立命中/甲裂/抬升renderer优先接收，否则`client/Cod3VfxRenderer`。本链不能与CF type编号混淆。

**状态链**：原生MobEffect Added/Remove/Expired与StartTracking → `expansion/EffectPresentation.java:20–53`每20tick/dirty刷新、移除包和新追踪回放 → CV的`status_1..8`/`status_clear_*` → `client/Cod3VfxRenderer.java:50–55,208,507–520`实体跟随有限图案。状态7甲裂折线、状态8脚下晃影是现有视觉；不是躯体动作控制器。

## 逐项：已有、真正缺失、仅验收缺失

### 1. Normal Hit — request:339

原文：材质色命中火花；短促命中；目标轻微后仰0.1s。

- 生产/网络：CF `hit:46–62` 默认type0；同一真实最终近战另触发 `cod3/WeaponImpactVisual.java:24–34,57–68`，七把指定武器材质/节奏，不是所有武器通用材质识别。
- 渲染/声音：CF默认4个ENCHANTED_HIT + PLAYER_ATTACK_CRIT；独立材质包经CV → `client/WeaponImpactRenderer.java:29–58` → `WeaponImpactVisual.geometry:72–90`，木/石碎块、铜/铁火花等真实存在。
- **实现/接入缺口**：未见全局type0→目标约2tick后仰的绑定或类型时钟；已有通用受伤动作不能按type0证明精确0.1s。通用材质包没有覆盖全部武器/来源，若按“全局”覆盖须继续界定接入；不把原请求擅自扩成任意第三方模组必须兼容。
- **仅验收/质量缺口**：已支持材质碎片的辨识度、原版粒子遮挡及低帧率观感，既有武器报告12–13已有实机限制；短促音是否合适未听验。已有材质实现不要重做。
- 专业归属：后仰动作交对应人物/生物骨骼动作专门对话；事件类型/时钟接入归正式战斗逻辑；材质几何质量归已有武器VFX专门分工。

### 2. Heavy Hit — request:340

原文：冲击波小环；低沉重击；目标后仰0.2s；不震屏。

- 生产：CF `hit:59–61`捕获蓄满且伤害达阈值；`expansion/ExpansionWeapons.java:121–130`流星锤实际伤害成功/释放；`SecondaryProjectile.java:41`石弹等已有专用生产者。
- 网络/渲染/声音：CF type1 → 12个半径1.3环状ENCHANTED_HIT、PLAYER_ATTACK_STRONG。流星锤另经CV template26冲击环（`ExpansionWeapons:129–130`、`Cod3VfxRenderer:621`），不能泛化给每次Heavy。
- **实现缺口**：全局约4tick目标后仰分型绑定未接；流星锤击退只是物理运动，不能代替全局躯体后仰。
- **仅验收/需定性**：CF环状粒子能否达到“小冲击波环”、现有strong音是否低沉、已有特定武器环的质量须实际判断；原文没要求连续网格环或新增自制音频，不据实现形式直接判缺。
- 专业归属：动作专门对话负责躯体；VFX/声音的必要改进分别归效果/音频与客户端集成，非建筑贴图队列。

### 3. Critical — request:341

原文：金星/星纹+数字放大；脆响；明显后仰；不闪白。

- 生产：CF `hit:54–60`原箭矢暴击/Forge实际暴击；`DynastySchoolCombat.java:130–131`尊重DENY/ALLOW；另有装备暴击生产者，见调用清单。
- 网络/渲染/声音：CF type2 → CRIT粒子环 + PLAYER_ATTACK_CRIT；原版CRIT可能符合星形，不要求新做一套星模型。
- **实现缺口**：本项目该反馈消费链没有伤害数字绘制/放大，包也无数值；不能把外部模组的通用伤害数字自动算作本链已接。未见暴击type驱动明显后仰的绑定。
- **仅验收缺口**：星粒子可辨性、脆响、禁止闪白的实际组合；七星刀专用七次星芒是武器效果，不等于全局暴击数字放大。
- 专业归属：数字交UI/客户端渲染，后仰交人物/生物动作专门对话，逻辑归战斗集成。

### 4. Block — request:342

原文：盾牌/武器火星+盾牌纹；金属格挡；举盾定格。

- 生产：`expansion/EquipmentBehaviors.java:258–278`原生ShieldBlockEvent，正格挡后type3/4；`333`双钺主动格挡；`256`竹甲真实反射亦type3。后者并非举盾，不可拿它替代举盾正例。
- 网络/渲染/声音：CF type3 → 默认ENCHANTED_HIT + SHIELD_BLOCK。原生使用物品举盾及盾面纹理存在；双钺另有`equipment_weapon_duck_guard` → `Cod3VfxRenderer:390–395`双斧局部几何。
- **实现/覆盖缺口**：type3不承载/驱动专门举盾定格，未见全局反馈时钟绑定；独立盾牌纹/贴盾反馈未由该CF分支生产。原生盾本身的纹理能否满足“盾牌纹”需按实际图确认，不能在没有图的情况下新增必须做decal门槛。
- **仅验收缺口**：已有原生举盾、SHIELD_BLOCK金属音及粒子是否表现为盾/武器火星，专门双钺视觉归属。举盾动画存在不等于所有type3生产者都有该姿态。
- 专业归属：举盾定格动作交对应人物/玩家动作分工；盾纹若确需新增才交盾/武器模型贴图分工；不能一律要求新资产。

### 5. Perfect Block — request:343

原文：金环+时停感0.1s；清脆“铛”；完美格挡后反击前摇；不锁镜头。

- 生产：`EquipmentBehaviors:258–283`原生5≤useTick<11判定、清除破势、type4；`288–299`原反击资源窗口；`DynastySchoolCombat:134–147,167–175`武器格挡后原反击伤害路径。另有混元/护盾type4复用，并非每个type4都是真完美格挡（`EquipmentBehaviors:217–221,325,329`）。
- 网络/渲染/声音：CF type4 → 环状12个CRIT、SHIELD_BLOCK音高1.5；这些是已有“金色环状粒子/清脆音”候选表现，未实际定性，不能仅因无连续金环网格就判完全未实现。
- **实现缺口**：没有type4驱动约2tick“时停感”的表现链，也没有通用完美格挡→反击前摇动作绑定。资源窗口、提示文字及伤害倍率不是动作前摇。“时停感”不等于要求真停服务器时间，不新增全局冻结机制。
- **仅验收缺口**：现有金色粒子环、调高音高的铛声、原生完美格挡解除与归属的画面/听感。已有机制无需重造。
- 专业归属：前摇/视觉停顿交动作专门分工，客户端表现集成；不允许用锁镜头制造时停感。

### 6. Armor Break — request:344

原文：甲碎裂纹decal+碎片；碎裂；目标踉跄0.2s。

- 生产/网络：`EquipmentBehaviors.java:431`原BREAK+type5；通用裂甲原生MobEffect走状态CV；另`cod3/ArmorCrack.java:30–56`实际士气韧性减半→同DamageSource正最终伤害，仅破军/玄天斧，CV专用甲裂包。
- 渲染：状态7折线（`Cod3VfxRenderer:519`）；`ArmorCrack.java:72–84`裂纹分离+四片漂移；`client/ArmorCrackRenderer.java:27–55`锚于受击者55%身体高度、实体跟随/深度遮挡。**不能把该两把斧的真实减半触发和所有armor_break状态混成完全同一机制。**
- 声音：CF type5用ASH+PLAYER_ATTACK_CRIT；专用甲裂renderer不播放声音。
- **实现缺口**：踉跄约4tick的躯体绑定未接；当前反馈链无明确碎裂音分支（可考虑复用合适原版声，不强制新录音）。带碎片decal只覆盖两把斧，通用状态折线无同等碎片路径。
- **仅验收/质量缺口**：两把斧已有原生甲裂/碎片可见，局部身体/心粒子遮挡；见旧武器报告24–25、50–51，不将nonzero改写成完整优质，也不要求所有角度无遮挡。
- 专业归属：甲裂VFX复用既有armor-crack专门分工；踉跄交人物/生物动作；声音与触发覆盖归代码/音频集成。

### 7. Stagger — request:345（另参277状态视觉）

原文：脚下晃影+踉跄；闷哼；破势后摇；不强制转向。

- 生产：`ExpansionEffects.java:22,46–63`原STAGGER减速/免疫/施加；`EffectPresentation:32–53`状态8的原生生命周期；`SecondaryProjectile:33`种子命中另发CF type6。**不是所有STAGGER Added都自动发type6**，但状态8视觉不依赖它。
- 渲染/声音：CV `status_8` → `Cod3VfxRenderer:520`三条摆动地线+弧环；CF type6若发送则ENCHANTED_HIT+PLAYER_ATTACK_CRIT。状态8本身不发闷哼。
- **实现缺口**：减速属性不是踉跄/后摇；未见状态8→对应躯体动作时钟及专门闷哼路径。不能把“未录声音”作为唯一剩余，消费分支本来就不是闷哼选择。
- **仅验收缺口**：脚下环已有实际图及减速记录，保留既有通过子项；全范围同步观感不是静态能补。状态行与全局动作行不得重复生产两套状态。
- 专业归属：踉跄和后摇交专业人物/生物骨骼动作对话；脚下环属于既有效果，不因动作未完重做贴图。

### 8. Knockdown — request:346

原文：倒地尘土+目标倒地；重摔；倒地→起身；不震屏。

- 生产：`ExpansionWeapons.java:97–101`真实绳镖/飞爪命中，Boss转IMMUNE；非Boss拉拽速度(y=.18)+STAGGER+CF type7。
- 网络/渲染/声音：type7走默认ENCHANTED_HIT+PLAYER_ATTACK_CRIT；没有该type专用尘土/重摔消费。非Boss拉拽+减速是已有机制，不能称完全没做，也不能称倒地动作。
- **实现缺口**：完整倒地/起身动作及其受击目标生命周期绑定；该分支的倒地尘土和重摔音。死亡侧倒或水中横躺图不能替代活体倒地→起身。
- **仅验收缺口**：原拉拽命中/墙体边界等已有原生结果可复用；不能通过新增截图弥补实际未接动作。
- 专业归属：倒地/起身交对应骨骼动画专门对话；战斗逻辑负责权威状态/取消/同步，VFX/音频负责有限尘土与重摔，不归建筑。

### 9. Launch — request:347

原文：上扬尘土+目标浮空；破空；浮空0.4s落地；不强制抬头。

- 生产：`cod3/WeaponLift.java:60–109`捕获真实攻击/正最终伤害、实际新增向上速度≥.18及可上升空间，4tick内真实离地≥.02后发type8；指定长柄/环首/巨阙再发CV；`SecondaryCombatActions.java:89`石虫自身出土亦type8，这不是受击目标浮空正例。
- 渲染：`WeaponLift:113–141`8tick有限弧光，真实支撑地块材质、四个地面小块；`client/WeaponLiftRenderer.java:26–50`跟随真实插值脚部和实际onGround。这个观察器不新增冲量、不伪造浮空。
- 声音：CF type8仍PLAYER_ATTACK_CRIT，抬升renderer无破空分支。
- **实现/规格差距**：8tick VFX时长不等于每个目标真实浮空8tick；当前没有通用0.4s浮空落地动作/时长绑定。不能以此擅自修改物理机制；需协调比较原有自然飞行时序。无专门破空音路径。
- **仅验收/质量缺口**：已有真实抬升/落地/地材尘土正例与顶棚负例；旧武器报告16–17、28–29、40–43记录弧光被主体/原版效果遮挡。已实现尘土不是缺资产，完整浮空/落地时长须复用原生时序再核对。
- 专业归属：现有weapon-lift VFX分工；若需要浮空/落地躯体动作交人物/生物动作；0.4s语义和物理边界归主协调战斗逻辑，QA不改。

### 10. Boss Immune — request:348

原文：“免疫”灰字+弹开微光；嗡鸣；Boss纹丝不动；不刷屏。

- 生产：`ExpansionEffects.java:43–50`识别Boss并拒SHA/STAGGER；`ExpansionWeapons:100–101`Boss拒拉拽；CF type9。同type也用于`QiConstitution.java:18–32`普通玩家体质免疫，**不要把两者要求互相套用**。
- 网络/渲染/声音：CF type9 → 默认ENCHANTED_HIT+PLAYER_ATTACK_CRIT；包无entityId/Boss语义，客户端无灰字绘制分支。`send:38–44`已有三tick节流、IMMUNE优先级5。
- **确定实现缺口**：Boss灰色“免疫”文字链缺失；当前声音选择是攻击暴击声，未接明确嗡鸣分支。未来最小修复应能区分Boss与普通体质，不能让所有type9普通玩家都被强加灰字。
- **仅验收/覆盖缺口**：已有默认微光是否构成“弹开”尚无合格Boss画面；已有拒控分支和节流不能代替全部Boss/所有控制来源都纹丝不动、防刷屏的实机结论。拒绝控制也不等于冻结Boss正常AI/走动，不添加“Boss永远不动”机制。原生普通体质type9图不是Boss灰字/音频通过证据。
- 专业归属：灰字属于客户端文字/战斗UI与语义集成；微光属于效果，嗡鸣属于音频/资源选择；拒控归战斗逻辑。**无需把灰字缺失送往人物模型或阴阳状态贴图队列。**

## 已有动作不应抹除，但不能越界算作十类动作已接

`client/character/DynastyCharacterModel.java:269,276,350`有真实hurtTime驱动的腹胸头短动作；`client/BossCuboidRenderer.java:108–125`及`BossFormsRenderer`有hurtTime→hurt clip。其他精英亦有各自hurt/stunned动作。故“整个项目完全没有受伤动画”是错误说法；然而这些消费的是hurtTime/个体技能，不是CF十类和精确2/4/8tick反馈时钟，不能证明Normal/Heavy/Critical强度区分、Stagger后摇或Knockdown倒地起身。状态减速、物理击退、反击资源窗口亦不能自动代替专业动作。

专业分工按现有对应人物/生物/玩家动作对话处理必要骨骼动画；本报告仅明确职责，不虚构已指派到某个姓名/已接单。现有无贴图POSITION_COLOR材质火花、armor-crack、weapon-lift应沿用其已有VFX专业成果；不因缺动作就重建模型。未来任何正式新增机制/资源仍须相应1000处相关实现研究，本次静态检索658个Java文件是审计范围，**不计作1000研究**。

## 复用证据与边界

- `../network-acceptance/report.json:16–42`：旧ce9259、四Jar、49stage真实TCP机制和状态队列，可复用apply/refresh/remove/体质/换装事实；旧草地图/心形HUD遮挡不能当可辨视觉通过。不是当前完整整包精确美术或十类全部触发验收。
- `../status-visual-acceptance/REPORT.txt:2–15,35–37`：0e1完整整包本地两实体，阴阳光效/免疫type9、脚下灰环、寒脉环境；声音QA静音未听验。四状态整项尚有边界，普通阴阳不要求灰字的纠正已在原报告。
- `../weapon-visual-acceptance/REPORT.txt:12–29,40–51`：材质火花、甲裂与真实抬升已有原生事件/实际截图，保留遮挡/辨识度限制；不能把武器专项几何等价为全局十类动作或声音。这里只复用该报告结论，未重新观测PNG、未宣称新视觉通过。
- 本次当前工作树源码带哈希；不声称与旧实测0e1每个class逐字相同。source-manifest锁定本次读取版本，旧运行仍按各自Jar哈希记账。
- CF和CV包均无Camera转向命令，所查消费链无锁镜头/全屏闪白/震屏操作；这只证明所查链没有该操作，不证明所有安装模组组合都无镜头变化。

本次可整行清理：**0**。可收窄：已有事件、两个S2C链、材质火花、状态裂纹/脚下环、两斧decal碎片、真实抬升/地材尘土、原生格挡/完美格挡机制及节流。真正待制作/接入与仅待验收子项应分开保留，Boss灰字明确仍是实现缺口。
