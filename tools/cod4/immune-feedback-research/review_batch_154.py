"""Main review037/038: actual single-use pre-settlement cue1, equivalent knockback lease0."""
from ledger import B,O,record,verify
import json,hashlib
repo='Moriyashiine/bewitchment';root=B/'sources'/repo.replace('/','__');p='src/main/java/moriyashiine/bewitchment/'
refs=[(p+'mixin/brew/LivingEntityMixin.java',92,121),(p+'client/packet/SpawnExplosionParticlesPacket.java',1,47),(p+'client/BewitchmentClient.java',90,239),(p+'common/block/WitchCauldronBlock.java',96,163),(p+'common/block/entity/WitchCauldronBlockEntity.java',133,167),(p+'common/block/entity/WitchCauldronBlockEntity.java',248,384)]
for f in [p+'common/registry/BWStatusEffects.java',p+'common/statuseffect/EmptyStatusEffect.java','src/main/resources/data/bewitchment/recipes/cauldron_brewing/volatility.json',p+'common/recipe/CauldronBrewingRecipe.java',p+'common/BWMixinPlugin.java','src/main/resources/fabric.mod.json','src/main/resources/bewitchment.mixins.json']:
 refs.append((f,1,len((root/f).read_text().splitlines())))
# Validate all paths and ranges before mutating the master.
for f,a,z in refs: assert (root/f).exists() and z<=len((root/f).read_text().splitlines()),(f,z)
k='bewitchment-native-volatility-consumed-pre-settlement-target-anchored-combat-cue'
record(k,repo,refs,
 '固定volatility酿造配方fire_charge→Cauldron原生tick投料/RecipeType列表→getPotion写CustomPotionEffects→Block.onUse玻璃瓶实际魔力支付/交付。原生LivingEntity.damage HEAD在server、正amount且hurtTime0、已有VOLATILITY且非爆炸来源时，对附近存活非自身实体尝试爆炸伤害→播放原版爆炸声→tracking+self发送实体ID粒子包→移除VOLATILITY。实际Client初始化注册receiver→主线程查当前world中ID→8个原版爆炸粒子。',
 '一个实际受击触发、消耗状态并独立发送目标锚定战斗提示的完整实现1。计数范围是实际游戏反馈生产/消费，不是假称免疫拒绝。与已账shadowward伤害分配、Botania cloak减伤/共享反伤、Arcanus随机消耗防护、Relics owner主动引爆不同：本链不拒原始来伤，真实status在预结算入口一次消费并提供受击目标而非投射物的tracking/self声光。AOE、状态消费、包与两个recipient分支不拆份。DEFLECTION箭分支优先returnfalse则本链不执行；邻居AABB.expand3不是球。各邻居damage结果忽略，原命中未最终settle，提示后消耗不随结果回滚；没有友军/owner过滤。爆炸tag抑制本链同类递归，非全局递归安全。包仅integerID，异步执行时查当前world，缺失丢弃，无UUID/维度/sequence/TTL，不能证明重用ID安全或目标已伤。',
 'Boss灰字必须来自最终明确拒控结果；预命中声光只说明分支执行。可参考有限状态消费、tracking+self收件人、目标锚定和缺失丢弃，但需补真实身份/生命周期及反馈节流；普通阴阳type9不新增灰字。',
 '主岗完整复读所列包含方法，含巨大client初始化90–239和原生瓶装支付96–163，固定配方文件及已有brew链补证；helper原稿0。原版PotionItem.finishUsing内部及引擎damage最终结算、Fabric网络底层/粒子原生绘制未全文展开；天然获取交付静态可见，不宣称实际喝下/客户端可见/声音可听/网络通过。原来的共用酿造、注册、包装不再计数。无生产改动/游戏/编译。','native_consumable_combat_feedback_producer_consumer')
for n,new,reason,keys in [(37,1,'完整实际战斗提示生产至消费链独立1；不是拒控成功回执。',[k]),(38,0,'与已账Goety单次目标时间戳击退取消语义等价；map与NBT、机会清理10tick属于支持差异，不为结构换壳另计。Earthquake显式Y运动已属DungeonsMobs既研取消作用域/独立Y控制支持。',[])]:
 f=O/f'helpers/herschel-immune/batch-{n:03}.json';d=json.loads(f.read_text())
 (O/f'HERSCHEL-{n:03}-REVIEW.json').write_text(json.dumps({'helper_batch':n,'helper_file_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'helper_original_credit':0,'main_review_new_effective':new,'promoted_keys':keys,'main_review':reason,'main_full_containing_method_review':True,'production_changes':False,'game_started':False,'limits':'静态语义研究；不代表运行验收。037新增完整client初始化、配方、cauldron取得链；038全文DamageSources/AoeEntity/EarthquakeAoe/EarthquakeSpell和原生注册上下文，NeoForge引擎具体派发未展开。'},ensure_ascii=False,indent=2)+'\n')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch154-volatility-native-consumable-cue-and-knockback-lease-equivalence','credited_chains':[k],'rationale':'037 actual consumable pre-settlement combat cue complete producer→target-bound consumer1; not immunity. 038 UUID lease equivalent to goety-no-knockback-single-use-native-event-stamp0; manual direct Y control equivalent to existing dungeonsmobs control cancellation scope0. No credit for wrappers/constant/payload fields.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
