"""One delayed evasion and one identity-linked damage transfer; both actual native hurt paths."""
from ledger import B,O,record,verify
import json
r='team-abnormals/endergetic';p='src/main/java/com/teamabnormals/endergetic/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
e='common/entity/purpoid/Purpoid.java'
shared=[f(e,86,124),f(e,136,329),f(e,380,417),f(e,570,584),f(e,628,660),f(e,744,783),f(e,853,891),f('core/registry/EEEntityTypes.java',53,53),w('client/renderer/entity/PurpoidRenderer.java')]
k='endergetic-native-delayed-teleport-evasion-success-result-before-relocation'
record(k,r,shared,
 '实际已注册Purpoid native hurt服务器路径：载具本人攻击先下骑并正常super；PURPAZOID其他攻击先wantsToFlee=true及stun=0，间接伤且无动画/不在传送时tryToTeleportRandomly，找到按当前尺寸无碰撞无液体的候选就beginTeleportation并直接return true，不调用super.hurt。普通体型同间接伤路径。实际tick调用controller.tick，到TO/FAST_TO动画10才移动实体或载具、destination清空；onEndimationEnd启动FROM，FROM期间速度0。',
 '计1：原生伤害接纳bool为true但伤害结算被延迟传送规避，区别于立即teleport后检查成功或hurt=false免疫。候选校验发生开始时，10帧动作延迟后没有重验碰撞/维度；若动画未到10先中断，destination可能保留而isTeleporting一直true，onEndimationEnd仅启动FROM，未补传或清destination，不能声称无孤儿。无伤来源不是Living时普通体型尝试传送但仍super。hurt事件真实和传送反馈存在，不证明Boss免控。',
 '不要把原生hurt true/false单独映射Boss灰字；仅显式拒控决定才发免疫语义。异步播放和实体变更要有失效清理，避免已显示免疫但控制仍发生。',
 '关键hurt/controller/候选/完整parent tick以及renderer完整已读，原生注册核对。Blueprint网络/Endimator底层未读，不冒称其S2C序列已全验证；renderer在TO>=10不画连线但super.render先执行，不能推断全部身体不可见；无实际客户端验收。','native_delayed_evasion_outcome_semantics')
k2='endergetic-native-random-child-damage-transfer-with-bidirectional-link-revalidation'
record(k2,r,shared+[f(e,330,378),f(e,528,543),w('common/entity/purpoid/ai/PurpazoidSquirtPurpsGoal.java')],
 '原生finalizeSpawn概率PURPAZOID→setSize把SquirtGoal注册priority0；实际Goal攻击动画>=40每4tick造baby Purp，概率或晚段缺盾时addShielder先存UUID并给child同步mommy整数id，再spawn。parent hurt在避弹未成功后，非bypass且shielders非空随机UUID，当前ServerLevel若查到Purpoid就调用child.hurt并return false，不看其bool。完整tick>=40逐项验证baby/活体/横向64格及双向归属，纠正或移除；UUID列表NBT保存加载。',
 '计1：随机实际子实体承伤及双向链接复验/清理是完整政策，区别Goety活体partner直接拒绝不转移，也区别possession单一被控body重定向。hurt入口不当场再查child alive/baby/归属，依赖tick清理；spawn失败已加入列表，会到tick删除。bypass伤不转移。链接渲染按child同步mommyId找当前worldPurpoid，双方TO>=10时不画线；renderer以双方插值位置绘196顶点，child受伤/死亡染红，mommy stun驱动alpha脉动。单一链接全链1，不把绘制/双方id/生命周期包装拆数。',
 '拒伤可能意味着伤害转到其他实体，而非整体免伤；免疫灰字应只描述此控制被Boss拒绝，不能吞实际转移/伤害事件。按UUID复验真实身份，不只整数id。',
 '完整SquirtGoal、setSize、finalizeSpawn、hurt、parent tick/NBT、renderer方法已读；渲染类型内部深度未读，玩家镜头可见性/alpha合适未实测，只有源码几何与调用证据。普通体质type9不扩展。','native_child_damage_transfer_identity_lifecycle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'endergetic-batch97-delayed-evasion-and-linked-transfer','credited_chains':[k,k2],'rationale':'Two genuinely different final native decisions: return true without damage while delayed teleport queued; child.hurt then return false regardless child result. Shared parent/transport/renderer supplementary, no individual entity reskins or helper credit.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
