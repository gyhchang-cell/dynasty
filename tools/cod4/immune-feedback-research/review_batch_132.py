"""Native gaze final admission, replacement lifetime and renderer identity policy; one family."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/Ice_and_Fire';root=B/'sources'/r.replace('/','__');p='src/main/java/com/github/alexthe666/iceandfire/'
full=['entity/EntityGorgon.java','entity/EntityStoneStatue.java','entity/ai/GorgonAIStareAttack.java','entity/util/IBlacklistedFromStatues.java','client/render/entity/RenderStoneStatue.java','misc/IafDamageRegistry.java','client/ClientProxy.java']
refs=[(p+x,1,len((root/p/x).read_text().splitlines())) for x in full]
refs += [(p+'IceAndFire.java',89,133),(p+'IceAndFire.java',215,217),(p+'client/IafClientSetup.java',63,141),(p+'entity/IafEntityRegistry.java',46,47),(p+'entity/IafEntityRegistry.java',90,133),(p+'entity/util/DragonUtils.java',351,356),(p+'event/ServerEvents.java',135,137),(p+'event/ServerEvents.java',163,165),(p+'event/ServerEvents.java',331,383)]
k='icefire-gorgon-native-gaze-final-admission-replacement-lifetime-type-cache'
record(k,r,refs,
 '注册Gorgon/StoneStatue及clientInit真实RenderStoneStatue；Gorgon目标AI→互相凝视且非雕像/可见→aiStep再检眼罩、双方失明和IBlacklistedFromStatues→scare动画>10且server共享cooldown0→buildStatueEntity复制非玩家NBT和体型→addFreshEntity→玩家hurt(MAX_VALUE)或非玩家remove(KILLED)→共享cooldown40/clearTarget。SynchedEntityData承载被困类型/NBT/尺寸/裂纹；渲染器按被困类型建model与hollow entity缓存，使用雕像yaw/坐姿/幼体、石材render type和裂纹层。AttackEntity原生事件十次合格镐击后移除并掉雕像或圆石。',
 '一处最终石化准入及实体替代生命周期家族1，与既账hydra致命floor、dragon骑乘/尸体、myrmex成长窗口不同。setTarget切近战仅是初筛，aiStep仍最终复核；Mob look控制可能先于最终黑名单检验执行，不能宣称拒控者纹丝不动。预备攻击音先于最终结算；spawn返回值及玩家hurt返回值均忽略，非玩家绕过hurt直接移除，不能用hurt=false推导拒控或成功。40tick是Gorgon共享成功路径cooldown，不是每目标免疫提示节流。雕像hurt仅return source==OUT_OF_WORLD而不super/改HP，true同样不能代表扣血。renderer hollow缓存按类型而非UUID，首个putIfAbsent返回null、后续同类型沿用首个NBT且类内无world-clear，不能把视觉代理当目标身份；合并整链，不拆镐声、裂纹层、各缓存/维度常量。',
 'Boss拒控灰字必须在明确最终控制拒绝点发出，不能复用预备音、伤害bool或生成调用作为成功/拒绝语义。目标锚定需实体身份与生命周期，拒绝节流需按真实目标；普通阴阳继续type9且无灰字新要求。',
 '固定commit源码静态全文与注册闭链；原版SynchedEntityData/Forge事件派发、Citadel动画网络底层、具体blind实体tag成员和RenderType深度实现未展开，不证明TCP到达、像素、原版粒子寿命或跨世界清理故障已复现。镐击实体移除不等于原生目标复活，未借用模型资产。未改生产、未运行游戏。','native_final_control_admission_and_target_proxy_lifecycle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch132-gorgon-gaze-replacement-target-proxy','credited_chains':[k],'rationale':'Final reciprocal-gaze admission plus replacement/stone proxy lifecycle one policy. Do not split whitelist, blindness, statue fields, render caches, sound wrappers or crack steps. Existing IceFire hydra/dragon/myrmex families have distinct final producers.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
