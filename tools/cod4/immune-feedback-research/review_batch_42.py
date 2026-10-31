# HISTORICAL ONLY: Cat Revenant credit retracted in DEDUP-CORRECTION-20261027.json. Do not rerun.
"""Manually reviewed actual shield loss and combat sound/effect lifecycle sites."""
from ledger import B,O,record,verify
import json
keys=[]
def w(r,f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,r,refs,c,o,l):
 for f,a,z in refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
 record(k,r,refs,c,o,l,'固定版本本地Git tree/blob校验+SHA，完整关键方法/实际game生产调用观察；仅静态，不证明原生渲染/音效/真实TCP。正式源码资产TODO不动、不启动游戏。模型只读，不把制作交给本岗。普通阴阳type9没有灰字要求。','native_rejection_receipt_lifecycle');keys.append(k)
r='lender544/new1.20.1';p='src/main/java/com/github/L_Ender/cataclysm/';e=p+'entity/AnimationMonster/BossMonsters/Ignited_Revenant_Entity.java'
add('cat-revenant-native-critical-axe-shield-loss-and-rejection-receipt',r,[(p+'init/ModEntities.java',187,190),(e,61,92),(e,126,210),(e,212,257),(e,310,349),(p+'ClientProxy.java',147,147),w(r,p+'client/render/entity/Ignited_Revenant_Renderer.java'),(p+'client/model/entity/Ignited_Revenant_Model.java',386,429)],
 '真实注册IgnitedRevenant goal start/stop/施法goal设置ANGER；native hurt server anger+directLiving主手Axe且damage>=1.5*(Axe base+1)、durability<4→WITHER_BREAK_BLOCK+durability++并直接false；否则source方向盾canBlock判定→shield bookkeeping/近战反推+ANVIL_PLACE→false；synced durability被真实model setupAnim控制4盾showModel。',
 '一个带真实盾资源损耗/不同拒绝回执的native家族1，不按4面盾/阈值/动画拆数。critical axe先于BYPASSES_SHIELD/方向门，破最后盾的当前击仍false；原hurt false不表示未改变盾、未发声或无任何受击后果。四盾基于累计数隐藏，但未取得Revenant_Layer全文/实际像素不声称全方向看清或资产质量。普通方向盾允许穿刺arrow、BYPASSES_SHIELD例外；无target-local免疫灰字或提示节流。synced字段默认0且此类NBT方法只super，没有自己保存耐久，不能假定重开仍破盾。该方向盾内部与既有RoyalDraugr方向算法同构部分0新增，本条新增依据明确斧击先消耗4盾并拒伤的独立生产裁决。伤害阈值不是读取玩家真实crit状态。',
 'Boss拒控可拒绝本次控制而触发明确微光嗡声；不能以false声称目标完全无反应。节流应覆盖同一次语义，不从斧击damage猜游戏状态。')
r='ochotonida/artifacts';p='common/src/main/java/artifacts/';q='neoforge/src/main/java/artifacts/'
base=[w(r,p+'component/ComponentType.java'),w(r,p+'component/ComponentQuery.java'),w(r,p+'equipment/EquipmentSlotManager.java'),w(r,p+'equipment/EquipmentSlotAccess.java')]
add('artifacts-native-equipped-hurt-sound-additive-target-receipt',r,base+[w(r,p+'mixin/ability/hurtsound/LivingEntityMixin.java'),w(r,p+'mixin/ability/hurtsound/client/LivingEntityMixin.java'),w(r,p+'component/HurtSound.java'),(p+'registry/ModDataComponents.java',59,61),(p+'registry/ModItems.java',573,606),(p+'event/ArtifactHooks.java',180,185)],
 '真实BunnyHoppers/KittySlippers物品配置HurtSound原版兔/猫资源→native LivingEntity.playHurtSound HEAD与client handleDamageEvent HEAD→onPlaySoundAtEntity查询真实装备HURT_SOUND.includeInactive+enabled→每个匹配组件entity.playSound(volume,pitch)。',
 '独立原生受击声音回执策略1；server/client入口、猫兔两常量及codec合并，不把声音wrapper多算。HEAD注入不cancel原生声，是附加而非替换；includeInactive排除cooldown/disabled过滤，不排component.enabled false，声音可在装备能力停用时仍按独立设置播。按每个组件iterate，不按entity/event限流，多个槽可能叠音；同一实际事件两端如何消费原生声音未实机，不能宣称已重复播bug。query仍是已注册slot provider范围，不能概括所有装饰slot都支持。实际Mixin JSON raw缓存未补齐，Java注入位点/物品有据但未证明该pin装载。纯受伤音不能称Boss拒控嗡声；不制作/录制新音。',
 '优先复用原版声音但由拒控语义播一次，明确音源目标与去重；不要在原版hurt声回调里对所有免疫/伤害再附加。')
add('artifacts-native-antidote-finite-status-cap-with-shared-item-cooldown',r,base+[w(r,q+'neoforge/event/ArtifactHooksNeoForge.java'),(p+'event/ArtifactHooks.java',53,68),(p+'event/ArtifactHooks.java',85,149),w(r,p+'component/ability/CureEffects.java'),(p+'registry/ModDataComponents.java',152,153),(p+'registry/ModDataComponents.java',210,217),(p+'registry/ModItems.java',385,395),w(r,q+'neoforge/data/tags/MobEffectTags.java')],
 '补齐真实NeoForge tag datagen完整addTags：blindness/nausea/mining fatigue/hunger/levitation/slowness/poison/weakness/wither；真实ANTIDOTE_VESSEL启用CureEffects+Ticker注册→原生EntityTick.Post livingUpdate→能力tick按实际slot冷却/disabled→收集tag内有限期且剩余>上限的效果→removeNoUpdate再可选按上限重加，非空集合才扣耐久和40tick物品cooldown。',
 '从之前CureEffects候选补齐实际tag定义后晋级1，九种效果常量不拆9。不是拒绝初始控制/免疫；无限期明确跳过，duration<=cap不动，cap<=0移除且不重加。新MobEffectInstance保留amplifier/ambient/visible/icon但不复制hiddenEffect链，不能假设隐藏层完全保留。native tick既client/server，无server-only门；伤耐久仅ServerLevel，addCooldown仅Player，非玩家没有同样40tick门，冷却也非每target每effect独立。组件的tag raw生成JSON未取得，不称启动已载入或客户端同步观感通过；datagen明确native状态类别，控制实际缩短策略相关。没有世界灰字/拒控sound。',
 'Boss拒控与事后状态缩短必须分开；提示寿命、隐藏/续期状态、按目标限频不能借物品CD当已满足。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'cat-artifacts-batch42','credited_chains':keys,'rationale':'Revenant斧击消耗盾且拒当前击1，普通方向盾同既有家族0；装备原生附加hurt声1；解毒瓶有限期控制状态上限1(补实际tag datagen)。所有wrapper/资源名/效果常量0。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
