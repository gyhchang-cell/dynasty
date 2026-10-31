"""Render a human-auditable progress report from curated records; grants zero research credit."""
from ledger import O,B,R,verify
import json,hashlib,datetime
verify()
rows=json.loads((O/'reviewed.json').read_text());sources=json.loads((O/'sources.json').read_text())
header='''# Boss Immune / 受击文本：实现研究进度

状态：**研究进行中，未达到1000处，尚未完成本项研究。**

本报告只汇总已经实际读取全文方法及自有调用链的记录。下载项目数、Java文件数、候选方法数、同链包装、平台移植、相同渲染链的颜色/数字/动画变体均不自动计数。机器校验只检查引用哈希和语义键唯一，语义去重仍由逐条人工式源码审阅承担，不能靠键不同自证独立。

原需求依据：本项目 `docs/cod4/request.txt:348` 的 Boss Immune 行要求“免疫”灰字、弹开微光、嗡鸣、不受此次控制影响、不刷屏；`:351` 要求服务端决定类型和目标、客户端播放。`:270–271` 普通阴阳体质免疫没有灰字要求，保留现有 type9 回执边界。不要把“纹丝不动”扩展为冻结Boss正常AI、走路或所有原生动作。

授权边界：仅本研究docs/tools目录；未启动游戏、未运行上游源码、未改正式Java/资产/原清单或待办。本文静态观察不能证明画面可辨识、声音合适或两端实际同步。按最新授权，达到1000有效去重并自检后由本岗负责最小逻辑、S2C与灰字反馈；身体建模/动画交原建模对话，不覆盖其资产；声音优先已有原版合适资源，不强制新录音。

'''
count=f'**有效语义去重：{len(rows)}/1000；缺口：{1000-len(rows)}。** 固定版本已取得完整或选定源码的项目{sum(bool(x.get("commit")) for x in sources)}个，项目数量不计研究数。正式修复仍待1000门槛；到门槛后由本岗落实已授权逻辑/S2C/灰字，编译优先。\n\n'
observations='''## 已获得的具体认识（研究观察，未定案设计）

- 血量差值数字只能看到变化；零伤、抵抗、拒控需有明确语义生产点。Mine and Slash 有明确 nullified 回执，Dummy 则展示“无限血但仍可有实际伤害事件数字”的不同情形。
- `hurt=false` 不能单独等同于Boss免控：共享伤害桶、边界/阶段、方向盾、自源排除各不同；Harbinger与Ignis还能在最终拒绝前生产动作或声音。减到0.1、减半等不应标作完全免疫。
- 动作栏本地化提示不是目标头顶浮字。Leviathan直接攻击者/投射物owner的差别会改变是否得到提示。
- 出生点快照、跟随目标、屏幕投影是不同锚定实现；包里有entityId不等于有维度/代际防护。缺失实体、换世界和实体ID复用仍须逐链核查。
- 粒子总容量、数字横向分槽、累加伤害和按目标节流/事件去重不是一件事。当前样本不能凭总上限宣称“不刷屏”。
- 深度必须看实际提交模式和GL状态。M&S RenderUtils强制GL_ALWAYS，HUD投影链也无世界深度；Damage Engine的注释不能覆盖实际SEE_THROUGH/NORMAL提交分支。
- GUI渲染时钟不能替代独立tick寿命。Simple Combat Indicators使用partialTick差值递增age，静态不足以保证低帧率真实到期时间。
- 已发现死代码/未接活路径，明确0计数；普通玩家体质不因Boss需求而新增灰字门槛。

## 有效记录索引

| 序号 | 语义键 | 项目 / 固定提交 | 首个来源（完整引用见下文） |
|---|---|---|---|
'''
lines=[header,count,observations]
for i,row in enumerate(rows,1):
 ref=row['source_refs'][0]
 lines.append(f'| {i} | `{row["id"]}` | {row["repo"]} / `{row["commit"][:12]}` | [{ref["source_path"]}:{ref["lines"][0]}]({ref["url"]}) |\n')
lines.append('\n## 逐项观察与边界\n\n')
for i,row in enumerate(rows,1):
 lines.append(f'### {i}. {row["id"]}\n\n')
 for label,key in [('全文调用链','full_chain_observation'),('实际观察','concrete_observation'),('与本任务的关系','application_to_boss_immune'),('覆盖边界','limitations')]:lines.append(f'**{label}：** {row[key]}\n\n')
 lines.append('固定来源：\n\n')
 for ref in row['source_refs']:
  a,b=ref['lines'];lines.append(f'- [{ref["source_path"]}:{a}–{b}]({ref["url"]})；SHA256 `{ref["file_sha256"]}`。\n')
 for ref in row.get('auxiliary_refs',[]):lines.append(f'- 辅助（0计数）：[{ref["repo"]}/{ref["source_path"]}]({ref["url"]})；{ref["note"]}\n')
 lines.append('\n')
lines.append('''## 继续研究入口

`reviewed.json` 为有效台账；`candidate-index.json` 为词法筛选线索，全部0计数，不能将其总量当已研读；`candidates.json` 记录实际读过但未满足完整/相关/独立门槛的候选与排除原因。`semantic-dedup.json` 记录合并依据。`sources.json` 保存固定版本及逐文件SHA；源码全文位于对应tools/sources目录。

Halley batch-001已由主岗复核80个证据范围/52文件，全部0新增有效，处理结论见HALLEY-001-REVIEW.json；逐字/哈希核验不能代替完整交互链或语义独立性。Wizardry新增1条原生Boss控制拒绝/施法回放链；Epicfight的旧partial文件保留当时0计数事实；2026-10-27已补齐原生NeoForge入口、Hurtable、具体Boss、动画S2C与消费，新增仅2个独立家族，见EPICFIGHT-COMPLETED-20261027.json和有效台账，不将旧0账重复晋级。

近期主岗已补Tinkers实际盾反/Enderference/effect immunity，Artifacts真实装备拒伤及附加受击声/有限期状态上限，PNC原生压力火伤门/摔落/弹源/传送拒绝，Mekanism事务吸收结算，RedstoneArsenal护盾资源/HUD与实际命中门，Goety Vizier与SkullLord活体partner免疫。CureEffects此前tag未读候选已补实际NeoForge tag datagen，晋级仅一次，原始生成JSON未得仍明确边界。已继续补ColdSweat实际热源/冻伤拒绝、载肩代理与目标一次性灵魂反馈，Enigmatic临时效果/装备来源清单/闪避，BloodMagic黑曜石披风（Bounce并Ars既有家族0），IceFire多头保护/龙骑乘尸体/成长窗口，以及luavixen物理浮字和Goety Wight隐藏/Minister伤害预算回执。Revenant新一条经交叉复核撤回，合并既有TF盾家族0，见DEDUP-CORRECTION-20261027.json；同样不会因补得模型源码而为同链重复加数。已继续补Tetra控制声光未检查effect接纳、Assorted来源记忆/健康差值配对、Goety风袍目标风生命周期与原生受击声跨维度消费边界、AoA实际注册的光环/场地恢复/全身穿透箭去重、Aether拒弹预测HUD与三个Boss拒伤政策，以及Malum比例ward与Incoming Aegis最终拒绝（实际转换数据/收取charge/dirty同步/HUD合并不按包装拆数）。MPA占位伤害类仍0。Arcanus已补完整stun原生启用及服务器组件消费者、危险感知一次性拒伤和实体屏障临近到期碰撞门共3；IE盾已补真实注册/native Pre事件/方向/升级及能量恢复链，电装备聚合拒绝另计1，具体每条以有效账边界为准。后续优先补明确的Boss拒控/拒伤回执、已有世界文字组件的世界切换/实体销毁处理、逐目标或逐事件节流实现。Goety monolith已补Heresiarch原生续期、实体与渲染注册，拒绝→原生entity event→shieldTime→渲染整链计1；拒晕链另计1，明确拒晕不等于无伤或不受击退。Halley已转迁移，不继续占有本项选源。Herschel负责Iron’s Spells、Ars Nouveau、SpellEngine候选，每批最多30，主岗逐条审查；其001为18条晋级，002为14条新实现及3条补齐001待定，003为6条新实现及2条补齐002待定；004为7条晋级（08/09缺实际启用producer仍0），005为7条晋级（弹历史并既有家族0），006为7条晋级（隐身清仇恨不属拒控/受击回执范围0，本地重影模板0）；007主审晋级6条，4条为调度/模板/AI转移支持材料0；辅助线程随后外部Provider证书502，已保留完整交付及错误，不重启循环重试。Java固定来源已校验，注册资源保留既有web全文观察/显示转录，明确raw资源TLS失败后未再请求，不能冒称原始blob已核验。守卫研究不自动转入。主岗继续Relics、Reliquary、Cyclic、Draconic Evolution、Goety、Wizardry、Mowzies、Enigmatic Legacy、Vampirism、Botania等，避开助手认领来源。不会用纯图形/基础网络库或同链包装补足1000。

主岗继续批70–76补齐Bewitchment真实金符/血池，Arcanus实际输入→能力/组件/实体链，IE原生盾/电装备，以及Simply Swords限时同stack弹反、支付ion cube触发租期、状态observer维度UUID/世界时缓存、蓄力存被击次数拒伤、Gloam跨owner目标免再抓取。Goety Arca锚点资格拒死链只计1，普通图腾并已有家族0；AlexsMobs原生分体Boss受击计时广播与目标对消费边界另计1，空damageType及全服广播/无UUID维度限制明确保留，不声称回放已通过。新取得源码及读取方法不自动入账，Forbidden Arcanus虚拟火抗消费者仍待补、骷髅wear入口为TODO；7条实际排除/待定观察见uncredited-observations-20261027b.json，均0。无需启动游戏，不给普通阴阳体质追加灰字需求。

主岗批77–89已继续补Mowzie crane teleport最终资格，Embers整次爆炸吸收/mercy窗口、完整盔甲socket聚合拒伤、当前攻击者工具缓存power拒绝与延迟bool耗能，Goety ender ground最终传送拒绝，Occultism救援消息先于冷却拒绝、guardian有限命数拒死、UUID目标支援成功回执与golem武器/姿态接纳。Waxweaver先前0候选现已补完整809行manager、原生世界tick/能力入口/隐藏body与渲染主方法，晋级仅1；目标缺失时continue先于expiry的孤儿状态、addEffect失败仍物理锁定的边界保留，旧uncredited-b仅为历史状态不再重复入账。EpicFight补原生guard资源破盾仍拒绝、ImpactGuard嵌套部分伤害后外层取消、dodge代理首碰关联、Endurance建防控盾闪光，以及攻击phase tried/shouldCount/dealtDamage三态目标预算，明确启动闪光/代理受击/声音粒子不能自证最终Boss拒控。新Ars Elemental补原生伤害泡结算、负面状态接纳付款拒绝、无投射物声波拒绝后独立反击3处；普通反弹和效果/注册包装0。Psi实际portal/capability控制准入→IMMUNE_TARGET异常→caster红字/网格位置包整链仅1，blink/motion/mass包装及调试聊天0。

补充13条明确0/待定观察见uncredited-observations-20261027c.json；Time Lock整段注释、Time Slow替换SpellData却原生消费者仍用原payload等反例保留，不为够数抹除失败。Ars Elemental及Psi为主岗新选源，不进入Herschel保留3项目；Herschel本地仍仅001–007交付，不重试既有Provider证书502。RECENT-PROVENANCE-20261027.json逐文件复核近期记录的固定tree Git blob/SHA256/范围/URL，验证器不判定语义独立、不给credit。1000仍未达到，不作正式逻辑或资产修改，不给普通阴阳体质加灰字门槛。

主岗批90–102已补：Scylla原生招架窗口（该parry particle render为空，不能称闪光已实现）；EnderIO SoulVial按序目标资格（动作栏失败提示不等于目标浮字，ERROR_BOSS声明未使用）；AlexsCaves sonic拒伤反击、spear灵体消耗、Watcher锁定租期与PrimitiveClub接纳后stun回执；Undergarden首次击打唤醒、和平Boss拒伤及slingshot命中效果短路；Wizardry世界时桶随机拒施法（非回执节流，拒绝仍重复声光）。Botania补Diva延迟末tick脑洗重验、Thunder链中途目标缺失会break余链。Lycanites补成功馈入伤害预算与次tick整HP回滚、Fear最终搬运资格/释放、Lifeleak取消攻击转治疗、坐骑投射免疫的事后净化、一次近战临时击退属性失败恢复缺口，以及instability最终Boss排除/双包不同随机冲量。Endergetic补身体箭拒绝与卵囊直接super通道、延迟传送规避返回true却不super伤害、父伤害转给宝宝并false、实际HP损失落地解抓与目标全局重抓冷却。每条完整链只计一次，不按注册/Goal/packet包装拆数。

Illage新增吟唱零伤预算打断治疗及终态成败声光，另补原生战斗声音随实体/动作冻结锚定与生命周期（不是Boss免控语义）；Invoker新增当前来伤来源在parent hurt前切换持续护盾、同次准入受影响，完整gameplay→同步字段→实际层注册已核。Necromancer半伤/普通守卫有限盾次数/幻象类等只做支持，不因新mob名加数。Fuzss main仅元数据树0，改读已有固定1.20.1游戏快照且保留原main证据，没有追随HEAD。

另外14组实际0信用/待定/合并观察已保存于uncredited-observations-20261027d.json：不将注释类、缺实际获取/消费者的技能、泛用代理、部分减伤及音效/图形包装自动晋级。AoA Tyrosaur灰色护甲数字仍缺与现TES不同API版本的匹配链，不拼凑完整链；Betweenlands固定tree超时结果保留，不循环重试。本文仍是研究进度，1000未满足，正式逻辑/S2C/灰字未实施。

主岗批103–106新增8处：Squall原生地面攻击被拒击退后仍独立上抛；Leapleaf两连通冲击区域共享命中尝试而非伤害成功历史；Thrasher父伤害前概率脱困预算；MoCreatures修复石空间准入和鳄鱼乘客身份拒伤/先释放；Create纸板取消伤害仍下马击退与目标收包、马铃薯失败只回滚预处理后的火时长、紫颂传送取消布尔值与弹药回收契约。均沿实际注册/原生调用方法读完整链，包装及常量变体0。另8组0计数观察见uncredited-observations-20261027e.json。340/1000尚未满足正式门槛；Quark固定tree超时已保留，不循环请求。

主岗批107–112净新增8处，当前348/1000：Goety bubble共享碰撞预算与来伤解爆准入；Naga成功受击且特定攻击阶段打断→坠落→地面锁定→起身动作消费；Domestication首次攻击尝试开未来拒伤窗、致命原伤序列化救援容器、来源限定破泡与下马拒绝，以及按目标UUID反射/本地接触回执租约独立于持续推力；PNC原生刷怪来源标记在最终捕获再验，白名单不越过实例免捕；Goety区域Transpose取消只break当前cell目标循环、其他cells继续，后续药瓶爆裂仍独立发声光。每条整链计1，粒子/模型/注册/网络包装均0。守卫缓存仅复用固定源码，未转旧账信用。

107复读Cyclic Laser发现与既有原生render-produced-laser记录相同，已撤回重复1并保存DEDUP-CORRECTION-107.json；当前348已扣重复，不能将旧临时计数再加回。新增11组0/待定/合并材料见uncredited-observations-20261027f.json。Spectrum本地固定缓存虽已观察关键完整方法，其独立Git tree请求25秒超时并保留4366639bytes部分结果；不重试、不导入有效来源、不计数。Domestication Blazing真实global key与资源filename不匹配，原生获取链未闭合，保留0；不为通过研究改资源。Forbidden QuantumCatcher只作捕获准入/成本提示对比0，未将普通目标提示当Boss灰字。

当前正式门槛仍差652，不实施正式逻辑/S2C/灰字，不称1000完成，也不将静态几何/声音调用当像素验收。Herschel保留Iron's Spells/Ars Nouveau/SpellEngine来源；主岗避免新选这些来源，本地新交付仍默认credit0，模型资产继续归原建模对话。全部操作限本研究目录，未启动游戏、未改总待办/资产/原档。


批113继续新增1处原生冶炼伤害准入/结算：火免疫目标改走magic source仍显式拒火抗/创造能力/对应source免伤，预资格在共享燃料检查前，实际hurt接纳才产物；原生controller每20tick的tick12调用已追齐，非按多个damage常量/配方拆数。当前349/1000、差651；生成伤害data固定blob已校，材料burning字段不等于IS_FIRE标签，未启动游戏或修改正式内容。



批114–117已实际新增6处，349→355：Occultism真实familiar最终效果拒绝、mummy随机拒伤及条件进度、Beholder先于伤害的眼束/租期；AlexsCaves多部件client拒绝/服务端generic relay；Goety master-fang闭合反馈先于实际资格结算；Aether BossEvent UUID→实体ID显示/移除生命周期与原版替换资格。包装、常量/模型绘制不拆计。

批118–120新增8处，355→363，仍差637：Herschel008主岗复核盾接触回执、敌对VELOCITY在reset前抗性门、DAMAGE忽略原生结果仍成功反馈、Turtle威胁入壳/拒伤概率翻倒，之后补008-15 MPS火伤转热/过热源退出循环1；009实际伤害接纳才目标冲量而发射费用/反冲/声独立1。另主岗Boof触发与最终push资格/源寿命、坐骑伤害规则在骑手LivingHurt投射各1。008和009来源文件/方法数均不加数，已晋级记录再次交付不重计。支持/待定见HERSCHEL-008-REVIEW-PARTIAL.json与HERSCHEL-009-REVIEW.json；MPS原生armor归一化/API/整合端未读边界保留，不声称四甲实测全免。

本轮再读Retro移植家族Forge1.20.1与NeoForge1.21.1完整浮字生产/消费文件，仍0credit：每tick血差与明确拒控不同，GL深度恢复/flush先后、classic未消费onTop、按帧缩放及整数ID换世界边界保留于uncredited-observations-20261028a.json。未用大量平台分支或样式凑数。Herschel新增Werewolves/RedstoneArsenal保留选源，主岗避免重复。

用户明确考试结束，禁编译/禁测试已解除；本岗仍只研究、静态证据检查，没有启动游戏/服务器/GameTest、图形程序或解锁唤醒屏幕，没有编译正式代码。游戏/真实TCP由主协调集中安排。1000尚未满足，正式逻辑/S2C/灰字/资产/总待办仍未改，普通阴阳体质不追加灰字要求。此前所有研究计数均是各阶段历史值，最新以progress.json及本报告首部为准。


批121–126新增11处（363→374）：本地完整链补齐团队/其他主岗缓存中的原生最终拒绝与反馈生产；121–124具体逐项见有效账，既有信用不移交、不重算。125补AlexsMobs藤索真实绑定/释放与owner查找/绳渲染，以及沙漠鹰对带sting节肢伤源拒绝和客户端sting重建；126补Vampirism不可移动Boss脆弱代理到母体fight状态的原生转交。藤索dirty key仅检查contains而未移除、消息无UUID维度重验等静态边界保留，不称实机网络或像素已通过。

批127主岗独立核查Herschel013–015的4项候选，晋级4（374→378）：Forcefield跨内外攻击拒绝与碰撞运动两个不同最终点、Paralysis末tick恢复与提前移除生命周期、原生死亡消散标记到实际layer启用/过期边界。其它12项仍0；不称12支持均由主岗全量复读，也不按来源文件数计。见HERSCHEL-013-015-REVIEW.json。

批128/129新增2处（378→380）：Domestication库存式拒伤/反控/末次受击重置恢复；Reliquary拒敌资格缓存与独立击杀耗耐久回执到HUD生命期。HealthSiphon全链与既有转伤语义重复0。Reliquary包slot=-1导致同键覆盖，拒敌本身不发耐久提示；世界HUD图标不是目标浮字，不冒充Boss免疫回执。logout只清另一系统，charm面板未显式清；具体维度隔离、外部handlers与底层派发仍有明确边界。

批130主审Herschel016/017新增2（380→382，缺618）：DungeonsMobs共享盾血保留负溢出与后续tick级联/逐盾恢复；Orb原生AABB独立入口及hurt失败后rootVehicle整组下乘。Goety已有Wildfire逐次重置盾HP的完整方法已交叉复读，只有真正不同的累积结算点加1，不以项目移植加数。Squall休眠相位拒伤、通用冲击副作用、常量拒伤/反射仍0；主岗纠正helper Squall tick引用207–215仅片段，已读完整206–246包含raid唤醒与timeout。Wildfire渲染注册未查得，模型非空不称可见。见HERSCHEL-016-017-REVIEW.json。Herschel继续Aether，主岗预留避免重复新选。

当前382为真实语义去重研究数；未达到1000，未实施正式逻辑、S2C、文字、资产或TODO修改。普通阴阳体质不追加Boss灰字要求。以下校验只核证据完整性，不等于游戏验收。

批131主岗完成Herschel019全链主审，新增1（382→383，缺617）：注册世界生成原生core→持续围困生产、无owner token的中心覆盖、逐轴边界纠正与自然到期/孤tag清理、conquer/regenerate注释空撤销、64格本维XYZ成功包与本地场渲染。只计控制生命周期整链，不将世界生成/结构/六面/8纹理/codec计建筑或额外功能信用；原生地形辅助仅上下文0。raw entity NBT跨端中心一致性未闭合，成功声光不当作已解除；未运行或宣称实机故障。见HERSCHEL-019-REVIEW.json。018全支持0，主岗只做既有全文阅读记录/017家族的语义核对，未冒称本轮全量重读其20文件。

额外4组实际阅读支持0见uncredited-observations-20261028c.json：Mowzie Boss背景音乐是相邻辅助而非受击/免控回执；Botania骑乘落地/火项链是已有来源保护家族，Relics AntiHeal只读到简单取消；Recruits静态方法是否经实例EventBus注册启用尚未闭合，不将其swinging字段当真实已运行拒控token，守卫旧账未移入。本轮无新网络获取或服务重试。

主协调独立收据coordinator-integrity-3e75456d84cd.json对应382快照，3853 source_refs/1649文件SHA、commit URL及key核对无误，研究加数0。当时383已由本岗另跑完整性核验；两者范围不同，均不证明语义独立或像素/音效/TCP验收。


批132–140实际主审新增13，主账396/1000，缺604；仍未达到制作门槛，10小时要求亦未声称达成。132–136为IceFire实际凝视/环境释放/关系控制五批六处；137主审Herschel021两处；138Basher有限挡击换武器/stun一处；139主审022–024三处；140Goety神像活体成员/同主人/魂预算/WOUNDED再生排除最终拒死一处。全部合并共同包装、模型层、端口、常量与实体名变体。原普通阴阳不要求灰字，Boss明确灰字/微光/嗡声与控制拒绝/限频范围不变。

Herschel020、重复Decoy、025助手RockyRoller不自动加信用；本岗未声称025全链复读。022主手库存控制与旧位移门不同，023Mob首非空槽无论掉落概率均清槽，024永久改owner且同owner拒绝，与临时控心不同；各只计实际最终生产点1。主岗逐项全文复读方法和原生上下文，原helper文件/credit0不改。新的完整性4192ref、近期122条741文件1577ranges固定Gitblob匹配仍只证明来源，不证明语义或实机。

Goety140外层死亡取消不接收startRevival结果，当前Raider另有同维条件；20tick普通字段不等专门可见动作；35通用原版回执不等Boss免疫。神像UUID→活体表有tick阶段，Cage魂查询/扣费非单来源事务。囚犯、通用图腾和同事件其他常量分支未拆数。继续研究，总任务仍进行中；未启动游戏、编译或制作正式代码/资产/TODO。


批141再新增1至397/1000，缺603：捕获者模式与异主囚犯身份触发LivingDeath改归属/治疗/取消，是独立最终拒死生产点，与神像预算复活和PNC计时驯服区分；初次村民转换未同处cancel、解缚声先于转换结果，不能混淆收据。具体来源见reviewed.json最后项。uncredited-20261028e两组21来源只支持0，候选/补下载不计。当前来源完整性4203refs、近期123条742文件1588范围固定Gitblob匹配，不证明实机或自动语义。

收到主协调整包基线0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba及53条状态，本岗未改Jar/正式代码/资产/TODO，不自开游戏。1000与10小时均未达成，总任务继续，全部未完成范围保持。

批142主审Herschel026新增1至398/1000，缺602。原生亡灵邻域20tick占据采样产生半伤，和前述翻盾/破盾/固定partner拒绝/随机转伤不同；非免疫，不用强化粒子或护盾层冒充最终准入或实机观感。helper025/027仅收到支持0，028继续。最新完整性4211ref、近期124条745文件1596range固定Gitblob通过；不加语义信用。全部阶段记录保留为接续，1000与10小时仍未达，总范围不变、尚未正式修复。

批143全文主审Herschel028再新增1至399/1000，缺601，仍未到制作门槛。原生驯服/保存/解除→非空owner用户名拒异主Player最终hurt（动物/水生合并），不含getIsTamed门，伤前HP包不是免疫收据。旧Crocodile captive门credit1不变，父owner先前仅未计上下文，本次补全生产/撤销/最终门后独立晋级，旧行添加互引说明。最新完整性4236ref、近期125条748文件1621range固定Gitblob通过。Herschel继续WerewolfTooth候选0，正式修改/编译/游戏/资产/待办均未进行；1000与10小时未达，全部任务范围保留。

批144–145补充完整语义审核至402/1000，缺598：Herschel029库存救死与旧生命符政策重复0，030环境光实际AI拒敌1；GuardianHeart注视选敌/群体互改目标及primary-only排除1；032己方宠物直接Player非shift拒伤1。固定坐标声光不是最终AI接纳回执，shift放行不证明HP成功。方法/粒子/适配分支均不拆计。4308引用哈希及范围、近期128条761文件1668固定Gitblob范围通过，仅来源完整性。Herschel生态03已因旧观察/新hash混列SUPERSEDED，04替代；本岗无源复核、编译或运行，不晋级任何生态或免疫实机项。1000与10小时未满足，正式修复未开始，总任务不结束。

批146–153主审推进到413/1000，缺587，未足正式制作门槛。146传送抑制presence lease、147双钩owner原生拒友伤、148部署mountUUID多贡献减伤、149静止/视角短期免伤lease各1；150owner-qualified幻象引爆拒绝与独立电链leader+每tick目标尝试去重两项；151可配置友伤选敌策略完整生产/验证/存储/原生消费1；152伤害合格声望跨档文字与报复准入政策1；153Herschel034两个不同控制输出位点+035治疗预算与心形显示整链共3。共同注册、常量、包装和视觉函数不拆计，候选数不转信用。

Herschel033缺Order自然获取/匹配消费保持0；036热摇镜/冷颤/blur助手支持0，主岗收到未全源主审不晋级。主岗补固定默认JSON：player启用cold effects、普通entity effects空；反序范围由betweenInclusive/blend处理，不编造配置失效。冷击退读victim.lastHurtByMob，并非victim免疫；cancel move事件重算输入非停住；冻心client与server预算同式不证明同步。

最新来源检查4543引用SHA/range匹配、近期139条847文件1903范围固定Gitblob匹配，只完整性，不自动证明语义/视觉/TCP/声音。uncredited20261028f新增8source refs只支持0，其中astryxion原固定archive fileSHA而无cached tree，不称该项目Gitblob已核。无正式源码/资产/Jar/总TODO修改，不自开游戏、不编译测试、不唤醒解锁。普通阴阳无灰字要求，Boss348/351原范围保持。1000/10小时尚未达到，全部剩余scope保留，本报告不是总任务完成。


154–156及helper036/039最新主审：416/1000，缺584。037真实预结算状态消耗/目标锚定战斗提示整链1（不是免疫成功）；038单次knockback lease与Goety已有stamp重复0。Tigerseye实际永久AI改写→改变才声光/扣mana→持久标记/重载静默恢复1；Heisei共享既账brainwash0。Vinculotus消费时live BE/world身份重验与原传送目的地资格重定向1，付款不是实际传送成功；Medumone通用addEffect尝试0。

036本地主角热晃/冷颤及blur消费者全文主审后保留0支持；留表不能推实际持续process，Boss反馈不动他人camera。039完整native Djinn拒火预算/替代目标生命周期与通用注册已读；缺具体Djinn JSON class映射字节，候选0；helper TLS失败保留，主岗不重复联网请求/关证书。CreatureInfo.enabled=false仅log非return，不能擅判不注册。

最新完整性4613引用SHA/range、近期142条878文件1961范围固定tree Gitblob核验；Iron新支持只archive fileSHA不假称tree。详情CURRENT-CONTINUATION.md、HERSCHEL-036..039-REVIEW.json和uncredited-observations-20261029g.json。仍无正式改动/编译/测试/游戏/屏幕操作/Jar覆盖/资产/总待办变更，普通阴阳无灰字追加要求。1000/十小时未达，全部剩余scope保持，任务未完成。


157–160与040/041主审已完成：当前420/1000、缺580。Draconic真实按目标免疫例外伤源分类、Tetra实际攻击来源回执/共享owner-bucket寿命/准星HUD、Vampirism武器攻击明确资格原因拒绝、AoA精英跨血线保护与普通耗能共享姿态四整链各1。四等级/包装/物种/三个reason不拆数。040三组11完整方法支持0；041完整866行和父结算/同步setter核对后仅主岗整链1，外部HeldBehaviour未展开，不能声称严格480/160到期或读档永久卡无敌。主账4689引用SHA/range、近期146条916文件2037范围fixedtree/blob/URL核过；不是自动语义证明或实机验收。来源及边界见CURRENT-CONTINUATION与主账，所有未完成要求继续保留。未改正式源码/资产/待办/Jar、未启动游戏/图形/编译/测试。


主批161/Herschel042已主审：当前421/1000、差579。实际Mekanism native beam预查无敌截断与hurtfalse/折射继续传播为一整链1；四甲/盾/codec/粒子/renderer包装不拆。主岗全文BasicLaser与本粒子consumer、补真实item capability注册及module enabled读取，source固定d4df9b354c209c85713bdc8a017bfe54aa044e40；4752引用hash/range、近期147条945文件2100范围tree/blob/URL核过。无目标/reason字段，实际投递/像素/声音/TCP未验，事务不保证火/实体/方块一起回滚。详HERSCHEL-042-REVIEW与接续。未满1000，未正式修改/游戏/编译，不缩剩余范围。


主批162–164新增3，当前424/1000、差576；Herschel043完整审为支持0，044条件body拒绝后head全伤回退整链1，163PNC native kick actor限频/服务器选目标/伤害独立位移回执整链1，164Ragno拒伤预算/格挡反馈10tick限频/眩晕脆弱窗口整链1。包装、声/粒子和动画consumer不拆数。完整方法/固定tree/blob来源已核，静态不证明pixel/声音/真实TCP。下一来源Bumblezone固定tree仅0，继续全文观察；不缩1000和10小时要求。未动正式功能、Jar、资产、待办/备份，未启动游戏/GUI/编译。


主批165–169新增6，当前430/1000、差570。Twilight观察者触发临时不可移动actor生命周期1；Bumblezone战斗撤销pacify1、实际Paralysis add/remove同步及render懒到期1、接触施力末端准入与按目标方向tick去重1、Rootmin controller puzzle准伤/血条/护盾整链1；PoiseCluster第三次target skip消费交互并销毁绕hurt整链1。Herschel045/047/049支持0，046/048各主审1，不按文件/方法/几何变体加数。049Java ^高于&&，纠正helper盟友绕过误读，JLS基础辅助不计；048已与Thrasher预hurt计数比较并限定独立语义。固定tree/blob与archive manifest明确分界，静态不证明pixel/声音/TCP。1000及十小时未满，所有scope保留；未改正式功能/Jar/资产/TODO或备份，未启动游戏/GUI/编译。


主批170–174新增5，当前435/1000、缺565。native Wrath移除后按当前policy请求重建1；Continuity native拒死先承诺、双层队列延迟当前装备付款/FX1；HiveLifeline现场最近非绑定替身+首armor CD拒伤整链1（只确认NeoForge EVENT_HIGH，不能泛称Fabric）；Herschel051 Gust直接位移先于状态接纳、未来墙碰撞伤/声/请求结束1；Sentry collision先推再禁伤与stop撞击独立setHealth请求1。050、05102 Immmolate后链仍支持0；049错误已获独立纠正/原SHA不变。所有完整方法/固定来源和去重边界写明，native tick/收包/真实画面不冒称通过。1000和至少10小时未完、scope不缩，未正式制作/编译/测试/游戏或触屏，未改Jar/资产/待办/备份。


主批175–177新增3，当前438/1000缺562。Herschel052归因先于effect admission/可变effect-key延迟/同步消费整体1；053实际contact接纳与几何fallback冲刺终止、Burning失败仍改iframe合并1；Bumblezone White聚合HP与event clock动态盾准入/源state客户端层整体1。四个装备/毒包装全文筛除0；054只metadata支持0不冒称全文主审。完整观察/固定SHA/语义比较与平台边界见接续和HERSCHEL-052/053-REVIEW。未生产制作/编译/测试/游戏/GUI/资产/Jar/TODO写入，无备份。1000和至少10小时仍未满足，总任务未完/scope不缩。


主178–179新增2，当前440/1000缺560，本轮175–179共5。055实际callee禁用拒绝voidreturn后caller仍绿overlay/CD，补supplier/已学持久化/书lookup静态条件1；056固定生成ender_slime配方和manager/native碰撞扣液/实际returning生命周期补闭，部分MAX尺度消费保留与最终传送拒绝分离1。旧门/包装0，054/057仅metadata支持0，BloodMagic bounce部分0留源/range不充数。全部局限写明，未正式制作/编译/测试/游戏/触屏/资产/Jar/TODO/备份。1000和至少10小时仍未达，不缩全部scope。


''')
(O/'REPORT.md').write_text(''.join(lines))
print(json.dumps({'report':str(O/'REPORT.md'),'effective':len(rows),'formal_gate':False},ensure_ascii=False))
