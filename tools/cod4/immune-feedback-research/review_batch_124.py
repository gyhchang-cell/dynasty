"""Native summoned-instance refusal, not one credit per minion variant."""
from ledger import B,O,record,verify
import json
r='Tslat/Advent-Of-Ascension';p='source/'
def f(s,a,z):return p+s,a,z
k='aoa-native-summoned-minion-player-owner-damage-admission-and-owner-bound-lifetime'
record(k,r,[f('common/registration/entity/AoAMonsters.java',28,30),f('common/registration/entity/AoAMonsters.java',74,75),f('common/registration/AoARegistries.java',117,117),f('common/registration/AoARegistries.java',174,180),f('common/registration/AoARegistries.java',204,222),f('content/entity/boss/king_bambambam/KingBamBamBamEntity.java',112,130),f('content/entity/boss/king_bambambam/KingBamBamBamEntity.java',189,215),f('content/entity/boss/king_bambambam/KingBamBamBamEntity.java',420,620),f('content/entity/boss/king_bambambam/KingBamBamBamEntity.java',699,712),f('util/PlayerUtil.java',311,319)],
 '真实King注册，native getFightTasks装三个SummonMinions variant→Delayed.doDelayedAction→factory构造匿名召唤实例，覆盖isInvulnerableTo/tick/shouldBeSaved/setTarget。最终伤源IS_EXPLOSION或父类已免或有entity且PlayerUtil不能解析玩家/直接玩家owner即拒伤；无entity并不因该归属门拒绝。新增实例绑定当前boss对象，owner不存活或tickCount>12000则discard，不保存；addFreshEntity成功才factory返回实例，上层才扣energy、设攻击memory、生成召唤FX/声。',
 '三种实际召唤类共一个政策计1，不按LittleBam/Piglin/Embrake的实体名、spawn声、资源成本或匿名类副本重复。归属只接受Player、OwnableEntity直接Player owner、Projectile直接Player owner；不递归任意多级主人，不把所有宠物/反射弹等同玩家伤害。setTarget仅允许目标精确PLAYER类型或null，上层还直接写brain ATTACK_TARGET，不能声称setTarget阻断所有AI目标路径。召唤音/火粒子证明实例创建成功分支，非每次拒伤回执；tick的discard与无存档策略也不是文字提示节流。',
 'Boss拒控需分清source direct/owner解析与最终target资格，不能因没有Player来源就泛化拒伤为拒控。提示生命周期不能长于实际目标；召唤成功FX与拒绝反馈需要独立语义。',
 '完整native getFightTasks、SummonMinions factory/handler及PlayerUtil归属函数已读。匿名Piglin最终门不依赖未取得LittleBam/Embrake基类；其super附加政策仅沿用API，不声称已展开三种父类所有免疫。SmartBrainLib延迟调度内部与外部Minecraft最终伤害仲裁未运行，不能称真实两端通过。精英副本未完整审阅不新增数。','native_summoned_instance_damage_admission_and_lifetime')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch124-boss-spawned-instance-policy','credited_chains':[k],'rationale':'One actual factory-installed per-instance final source-admission policy plus owner/tick lifetime; three minion types and every callback wrapper merged. Different from boss-health partner shields, captive-only source checks and multipart gates.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
