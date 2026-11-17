"""Two manually read target-status policies; all library dispatch is auxiliary0."""
from ledger import B,O,record,attach_auxiliary,verify
import json
r='SammySemicolon/Malum-Mod';p='src/main/java/com/sammy/malum/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='malum-native-gluttony-status-denial-plus-retrospective-hunger-cleanse'
record(k,r,[w('MalumMod.java'),f('registry/common/MalumContent.java',180,208),f('registry/common/MalumContent.java',330,330),f('registry/common/MalumContent.java',704,705),w('registry/common/MalumMobEffects.java'),w('registry/common/item/MalumFoodProperties.java'),w('common/events/RuntimeEventHandler.java'),w('common/effect/gluttony/GluttonyEffect.java'),w('common/item/IMalumEventResponder.java'),w('common/item/curiosities/weapons/scythe/RavenousScytheItem.java')],
 '真实@Mod注册MobEffects与Gear/Materials。RuntimeEventHandler原生Applicable→GluttonyEffect.canApplyPotion，只对HUNGER且目标已有GLUTTONY/TRIAL_OF_FAITH/DESPERATE_NEED写DO_NOT_APPLY；Added→removeExistingHunger对任意刚加入效果事件重查目标当前三态，有则移除既有HUNGER。RottingEssence注册食品原生95%施HUNGER600tick；RavenousScythe服务端合格原生伤害Pre响应applyGluttony，通过可修改properties事件后addEffect/放大既有实例。',
 '计1：当前互斥状态同时覆盖新效果最终拒绝与旧效果事后清除的双阶段一致性政策；三种状态名、两个事件回调及属性构造不拆数。不是按装备multiset等级和放大阈值拒绝，也不是定时cap缩短。Added没有限定新效果就是gluttony，任意Added都重查；是否新状态已出现在entity.hasEffect取决于NeoForge插入时序，静态不假定必当场清旧。保留Gluttony每tick仍causeFoodExhaustion，免Hunger不等于免所有饥饿耗费。属性事件允许替换effectType，不把任意替换都推成有免疫资格。',
 'Boss控制拒绝应在适用性最终门产生明确原因；已有状态清除和新请求拒绝要分别覆盖，不能只用客户端当前效果列表猜拒绝。普通阴阳不新增灰字要求。',
 '上述所引关键类/完整方法全文已读。Lodestone两个固定源码文件已补读仅作分发支持0，未验证Malum构建锁定所用Lodestone版本相同，也未展开外部charged attack判定，不能声称实装此物品必定触发。直接Applicable拒绝链独立成立；无Boss灰字/音效/实机同步结论。','native_mutually_exclusive_status_applicability_and_retrospective_cleanup')
a='LodestarMC/Lodestone';q='src/main/java/team/lodestar/lodestone/'
attach_auxiliary(k,a,[(q+'handlers/ItemEventHandler.java',1,len((B/'sources'/a.replace('/','__')/(q+'handlers/ItemEventHandler.java')).read_text().splitlines())),(q+'events/GameEvents.java',1,len((B/'sources'/a.replace('/','__')/(q+'events/GameEvents.java')).read_text().splitlines()))],'完整泛型分发：真实Pre事件按目标/攻击者主手与护甲lookup调用接口；基础分发不是独立游戏实现，且未验证依赖版本锁定。')
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
k2='goety-native-stored-effect-type-denial-before-independent-prehit-effect-theft'
record(k2,r,[f('Goety.java',132,205),f('common/items/ModItems.java',41,47),f('common/items/ModItems.java',124,124),f('common/entities/ModEntityType.java',621,624),w('common/items/WartlingEggItem.java'),w('common/entities/neutral/Wartling.java'),f('common/entities/ally/spider/AbstractSpiderServant.java',203,236)],
 '原生WartfulEgg.use→服务端新Wartling，把玩家首个可治愈HARMFUL实例存为StoredEffect并立即从玩家移除，然后才尝试addFreshEntity。Wartling最终canBeAffected对当前StoredEffect相同类型返回false，其余委托父类。Mega原生近战在super.doHurtTarget之前对目标施存储非beneficial效果，或存储并移除目标首个可治愈beneficial效果、播bite声。存储经NBT写读；server tick发送该效果颜色粒子。',
 '计1：实体当前被携带的效果类型作为动态最终免疫资格，并在原生施/夺效果流程中更新；各药水种类/egg与近战存储来源合并，不按名称拆。区别静态Boss全拒绝/标签类目门或按装备等级阈值。effect是直接实例引用，不是copy；NBT读取也可改变资格，effect本身不是SynchedEntityData，不假定客户端拥有同样值。夺效/施效发生在父hurt之前，即使最终hurt=false也已可能改变效果和播声，不能把此声当HP成功或拒控回执。egg去除玩家状态在spawn结果前，不是成功spawn事务。',
 'Boss灰字依据明确最终控制拒绝，不能由普通hurt返回或尝试音效推断。动态资格需要生命周期和权威端一致性；状态剥夺与伤害结算应分清，失败时副作用需明确。',
 'Wartling/Egg全文、父类完整doHurtTarget与实际注册已读；父类更深基类effect门沿用外部Minecraft契约，不声称已跑通。直接push拒绝仅支持不另算；死亡云/归主声/粒子不是拒绝时专属反馈。未运行或改资产。','native_dynamic_carried_status_type_final_rejection')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch121-two-distinct-native-status-policies','credited_chains':[k,k2],'rationale':'Two independently observed game policies: paired prospective/retrospective incompatible-state exclusion; mutable carried-effect identity final denial with pre-hurt theft. Source callback wrappers, effect names, dependency dispatch, positive knockback scaling and angle quantization0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
