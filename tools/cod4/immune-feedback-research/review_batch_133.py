"""One native independently admitted stare-control and client target-beam family."""
from ledger import B,O,record,attach_auxiliary,verify
import json
r='AlexModGuy/Ice_and_Fire';root=B/'sources'/r.replace('/','__');p='src/main/java/com/github/alexthe666/iceandfire/'
full=['entity/EntityCockatrice.java','entity/ai/CockatriceAIStareAttack.java','entity/ai/CockatriceAIAggroLook.java','entity/ai/CockatriceAITarget.java','client/render/entity/RenderCockatrice.java','client/particle/CockatriceBeamRender.java']
refs=[(p+x,1,len((root/p/x).read_text().splitlines())) for x in full]
refs += [(p+'client/IafClientSetup.java',63,141),(p+'entity/IafEntityRegistry.java',54,55),(p+'entity/IafEntityRegistry.java',90,133),(p+'entity/EntityGorgon.java',55,71),(p+'entity/util/DragonUtils.java',236,247),(p+'event/ServerEvents.java',135,137),(p+'event/ServerEvents.java',155,157)]
k='icefire-cockatrice-native-group-stare-control-admission-versus-client-beam-target-cache'
record(k,r,refs,
 'Cockatrice真实构造AI、注册goals与target选择→AI设TARGET_ENTITY及看向目标→aiStep服务端互相凝视/非失明/非眼罩→shouldMelee最终以距离、target tag、IBlacklistedFromStatues判是否进入凝视效果路径→首tick开STARING，后续按同目标凝视伙伴数/难度施加WITHER/减速/CONFUSION并周期伤害。未驯服玩家还积taming并广播46/45，handleEntityEvent产伤害/爱心粒子。TARGET_ENTITY SynchedData变化清client cached target和攻击计时；client本地凝视+STARING生成沿线粒子；注册RenderCockatrice另按双向凝视/失明绘CockatriceBeamRender，含端点插值、跨端AABB裁剪与全亮beam。',
 '整套实际凝视减速最终准入/独立目标同步与可见beam政策1，不是Gorgon实体替代或仅其黑名单换壳。getFriendsCount只统计同一目标且互相凝视者，expandTowards正向盒而非inflate对称范围；不按伙伴/效果种类/射线面/粒子加数。effects add返回未用，伤害返回亦未用，taming累积及声光不是控制接纳回执。render没有STARING最终条件，视觉只表示当前锚定/凝视，不能当服务端免控判定。getTargetedEntity可复用缓存，TARGET_ENTITY更新才显式失效；TAMING_PLAYER复用同一targetedEntity缓存但其key更新无该回调清理，本类NBT保存运行时taming ID而非UUID，无法据此认定跨重进身份安全。doHurtTarget返回false仅排队动画，aiStep后续真正结算；非Bossimmune。',
 'Boss拒控反馈必须来自最终判定并携带目标；渲染不凭凝视/目标ID即推测灰字。避免复用攻击目标与驯服目标缓存；按身份失效、有限时长与实际事件节流。普通阴阳type9不追加灰字。',
 '完整AI/实体/renderer/beam方法与真实注册已读，vanilla效果准入/同步底层及模型姿态未实机，未宣称失效复现或像素可辨。DragonUtils导航几何仅辅助上下文0；Beam采用entityCutoutNoCull，但引擎深度/遮挡行为未运行核验。目标同步无独立TCP证明。未修改生产功能或资产。','native_final_stare_admission_and_separate_visual_target_policy')
attach_auxiliary('icefire-gorgon-native-gaze-final-admission-replacement-lifetime-type-cache',r,[(p+'CommonProxy.java',125,127),(p+'IceAndFire.java',184,213)],'补闭ServerEvents实例实际注册；注册包装0额外信用。')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch133-native-group-stare-and-beam-not-effect-receipt','credited_chains':[k],'rationale':'Distinct actual status producer gated by group gaze and melee eligibility, independently synchronized native target visual. Whole family1; common Gorgon look/blacklist helpers and vanilla-style beam vertex wrappers0. No extra tame/particle/cache credit.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
