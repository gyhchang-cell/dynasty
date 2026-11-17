"""Three independent native companion receipt/settlement policies, no wrapper credits."""
from ledger import B,O,record,verify
import json
r='klikli-dev/occultism';p='src/main/java/com/klikli_dev/occultism/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
base=[f('handlers/FamiliarEventHandler.java',62,63),f('handlers/FamiliarEventHandler.java',292,297),w('util/FamiliarUtil.java'),f('common/capability/FamiliarSettingsData.java',120,122),f('common/entity/familiar/FamiliarEntity.java',285,288),f('common/entity/familiar/FamiliarEntity.java',325,344),f('common/item/familiar/FamiliarCurio.java',46,57),f('common/item/familiar/FamiliarCurio.java',178,221),f('common/item/familiar/FamiliarCurio.java',252,279),f('registry/OccultismEntities.java',326,332),f('registry/OccultismEntities.java',360,366),f('registry/OccultismEntities.java',524,537),f('Occultism.java',105,105)]
fx=[f('Occultism.java',132,132),f('network/Networking.java',37,86),w('network/MessageHandler.java'),w('network/messages/MessageFairySupport.java'),f('common/entity/familiar/FairyFamiliarEntity.java',154,178),f('common/entity/familiar/FairyFamiliarEntity.java',419,421)]
k='occultism-native-fairy-rescue-receipt-precedes-final-victim-cooldown-denial'
record(k,r,base+fx+[f('handlers/FamiliarEventHandler.java',311,344),f('common/entity/familiar/FairyFamiliarEntity.java',349,358)],
 'Forge EventBusSubscriber原生LivingDeath→fairySave：非bypass且IFamiliar、非Guardian/Fairy，owner启用fairy并由FamiliarUtil查equipped优先/本world10格owned alive备选。fairy.saveFamiliar先检查自身saveCooldown和sitting，再置400并tracking该fairy发送两个entityId的Support；随后caller才检查未加入世界的fairy对应victim UNDyingCooldown，命中则return不canceldeath，否则补cooldown、cancel并health2/absorption。实际S2C方向注册→MessageHandler.client→当前level按整数找fairy触发supportAnim20、独立按targetId发30dust。',
 '一个最终拒死前已经消费CD并生成成功样反馈、之后仍可拒绝救援的独立生产顺序位点1；不能把support packet或粒子当最终救活回执。cooldown是fairy单实体global，不是每victim；活体fairy native tick递减，但ring curioTick仅调用familiar.curioTick，所见路径不调用native tick，不能宣称虚拟使魔400tick自动恢复。equipped检索只验证type/pred，不像nearby验证owner/alive；包目标fairy缺失时target仍可独立喷粒子，无pair关系/UUID/维度/age验证。发送tracking的是施救fairy，不保证所有看见victim的人收到；虚拟fairy非world entity时不保证tracking有观察者。',
 'Boss免控回执应在所有资格/节流/最终拒绝条件确定后发送；CD消费和展示回执要绑定同一已确认结果，不能先播成功后在另一个gate失败。目标应包含本维身份和期限，并区分施法者/被拒控制目标。',
 '固定提交，完整native救援、helper检索、ring获取和tick方法、包/consumer/实际注册已读；无游戏、不证明虚拟使魔声音或粒子可见。普通玩家/同伴拒死不是本项目Boss拒控理由；不制作模型，supportAnim实际模型姿态消费者未审不声称动画已通过。','native_rejection_receipt_ordering')
k2='occultism-native-guardian-life-budget-death-refusal-and-synced-depletion-feedback'
record(k2,r,base+[f('handlers/FamiliarEventHandler.java',365,395),f('common/entity/familiar/GuardianFamiliarEntity.java',62,172),f('common/entity/familiar/GuardianFamiliarEntity.java',214,253)],
 '同一原生LivingDeath分发的独立guardianUltimateSacrifice：只Player非bypass、设置enabled、FamiliarUtil查guardian；虚拟guardian且player有UNDyingCooldown在sacrifice前return。sacrifice读tracked LIVES>0为成功，life1先advancement，再setLives(lives-1)后返回；成功才canceldeath、health1/removeAllEffects/regen+absorption/invulnerableTime30，虚拟guardian按upgrade及扣后剩余life设不同cooldown。实际guardian.tick观察tracked life下降→particleTimer30+GENERIC_HURT，client每tick20原版STONE block粒子；server<=0 kill。life同步字段且NBT显式读写、setLives仅接纳0..5。',
 '一个消耗外部实体有限生命并明确先检victim CD再结算的最终拒死位点1，算法不同于fairy先回执后检查、也不同于持有图腾扣物。life0时sacrifice仍调用setLives(-1)，setter拒绝，返回false不cancel；life1→0成功但使魔下一tick被kill。player.removeAllEffects不含恢复先前beneficial列表，后续额外无敌帧也与取消本次死亡不同。tracked life change才触发损耗声/粒子，未见本法给player直接发送救活灰字；出生首次lives0=-1不播下降。虚拟guardian不native tick，不能推断同样出现实体损耗粒子。没有按life阶段/肢体外观/升级常量加数。',
 '反馈需要区分本次最终拒绝和资源耗尽后续状态；同一Boss免控提示不应误用外部单位死亡或原版受伤声作语义证明。所有final资格先检，再改变资源，再发送有期限回执，避免重复消费。',
 '固定版本完整handler/sacrifice/tick/save/load/lookup关键方法已读；完整ring serializeNBT可写当前familiars但本分支何时把修改后组件回写保存未追完，不声称重进持久化通过。未审模型asset，不把不同生命数身体外观计研究或制作。不运行游戏/编译上游。','native_external_life_budget_refusal')
k3='occultism-native-target-uuid-support-success-gated-receipt-cooldown'
record(k3,r,fx+[f('common/entity/familiar/FairyFamiliarEntity.java',112,123),f('common/entity/familiar/FairyFamiliarEntity.java',429,494),f('common/entity/familiar/HeadlessFamiliarEntity.java',356,364),f('common/entity/familiar/FamiliarEntity.java',285,288)],
 '实际Fairy.registerGoals安装SupportGoal；canUse非sitting且familiar entity非null。goal.tick先递减自身Map<victimUUID,Integer>，每5fairy ticks扫10格同owner的Mob IFamiliar；单victim cooldown0时尝试环境相关fireResistance/waterBreathing/slowFall/speed/resistance，逐个以addEffect实际bool并为gaveSupport；Headless满足fullyRebuilt也可重置死亡状态并heal。只有gaveSupport=true才tracking fairy发同Support包并把该victim设200；实际注册/receiver/target粒子与救援共用，本次不重计。',
 '一个原生按目标UUID且以实际状态接纳结果为门槛的战斗防护反馈节流位点1；与fairy全局saveCooldown以及guardian生命结算不同。200是goal实际tick递减次数，goal停用时不会按世界时间流逝；Map未清离开目标条目，无维度key但每个goal持在world entity实例。一次可给多个effect仍只发一次；失败不占CD，下个每5tick继续尝试。当前查询owner用本world getPlayerByUUID，不保证离线owner；canUse无explicit server检查，具体原生GoalSelector实际侧需平台上下文不宣称client执行。发送按fairy跟踪集，不等于victim跟踪集。',
 'Boss灰字节流可参考真正按目标和已确认结果计数的生产点；世界时间deadline与活跃goal tick冷却不同，不可在暂停/卸载后误判；同一次尝试多个控制分支合并回执，拒绝原因仍须明确。',
 '完整SupportGoal及实际反馈消费者已读；isFullyRebuilt的更上游重建玩法未深入，本条不把Headless复活独立计数。所有效果种类/30颗dust/网络包装均0额外。不作游戏画面结论，不扩普通体质灰字。','native_target_feedback_throttle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'occultism-batch81-companion-final-settlement-and-native-feedback','credited_chains':[k,k2,k3],'rationale':'三个不同实际算法位点：救援先发回执再victim CD；守护者独立外部生命预算且先CD再消费；实际状态接纳bool聚合后的UUID目标反馈限频。共同packet/curio/lookup复用不加数，实体名/升级/生命外观/效果常量0。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
