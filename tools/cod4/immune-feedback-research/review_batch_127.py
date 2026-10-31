"""Main review of Herschel013-015 candidates; helper original credit remains zero."""
from ledger import B,O,record,verify
import json,hashlib,datetime
r='Electroblob77/Wizardry';p='src/main/java/electroblob/wizardry/'
configs={
'herschel-013-01':('wizardry-native-forcefield-cross-membership-attack-denial-and-global-projectile-exemption',
 '实际Spells注册Forcefield、Entity registry注册EntityForcefield→SpellConstruct.cast/spawnConstruct服务端构造、写caster/lifetime/radius、检查同类AABB不重叠再spawn。EventBusSubscriber原生LivingAttack先判玩家trueSource投射物且ring_defender活动直接return；否则非unblockable、有trueSource、immediateSource非field时，比较两者surrounding forcefield对象，不同即cancel。归属需整个AABB八角严格在球内，20范围候选选最近中心，null/null与同对象不拒。',
 '一个双方空间归属最终伤害拒绝政策1。Defender例外不核验攻击者拥有当前field，不能称只允许射穿自己的盾。实际按trueSource而非弹体位置；身体跨球面是外。ItemArtefact支持event ALLOW或装备/hotbar优先资格，常量戒指/几何/三lookup包装0。LivingAttack本入口无拒伤文字声光/last-send门。',
 'Boss反馈应从明确最终拒控政策产生，来源/目标/空间关系须一致；不能把全局例外或同场允许误作本Boss免疫。',
 '完整field及原生cast/spawn、球筛选、八角、装备资格方法已读。EntityUtils半径筛选首个超半径remove后break，不能声称其余全过球筛选。第三方event重仲裁与原生伤害内部未运行，未证明真实画面。', 'native_spatial_membership_damage_denial'),
'herschel-013-02':('wizardry-native-forcefield-contact-motion-independent-of-damage-and-predicted-visual',
 '同一真实forcefield实例onUpdate→父onUpdate寿命检查→radius+4查询，排XP/self及Defender友方弹，isValidTarget依caster/ally政策；Living预测最近AABB顶点nextDistance<=radius，非Living判穿入穿出。Interdiction先尝试1MAGIC且不查hurt结果；服务端再强制反向*.2+法线速度、地面负Y改.1、setPosition、deflect声，MP发原版velocity包；客户端独立预测FLASH和12DUST。',
 '独立直接位移/接触反馈生产点1，不和前条伤害事件取消合并：没有有效DamageSource也可推离、hurt=false仍会动，且该门不判跨场来源。Living/弹体/两戒指/声粒子合并，不拆变量。tick%5寿命*.99在每接触目标循环内，多目标会多次扣，不是逐目标提示节流。client若内部Player直接return整onUpdate，后续目标也不画；预测不能当服务器拒绝回执。caster失联时Ally函数对非null目标返回true，不保留旧盟友。',
 '免控必须覆盖hurt之外的直接速度与位置控制；灰字微光应消费服务端结果，不能靠客户端独立碰撞预测冒充已拒控。',
 '已完整读field.onUpdate、父类、实际ally主方法、原生cast/spawn。ally深层外部predicate/Baubles插件与vanilla velocity收包内部未展开；client FX生产已读不代表粒子renderer/声音/实际TCP通过。搜索边框4不能保证拦截所有高速弹，super despawn后本方法未return。', 'native_contact_control_and_prediction_semantics'),
'herschel-014-01':('wizardry-native-paralysis-tail-tick-ai-release-versus-critical-hurt-early-removal',
 '真实Paralysis注册→SpellRay.cast/shootSpell实际ray命中→onEntityHit客户端beam/lightning，服务端尝试paralysis效果；SHOCK免疫只挡伤害并发spell.resist，不return，仍可尝试状态。原生LivingUpdate仅EntityLiving且效果仍活动时setNoAI(duration>1)；原生LivingHurt若health-amount<=critical_health就removePotionEffect。注册匿名PotionMagicEffectParticles只覆写spawn粒子，父performEffect空。客户端effect时清移动/跳/潜，聚焦鼠标cancel并yaw/pitch清0。',
 '一个具体AI控制恢复生命周期分叉1：正常尾tick写false，不保存原NoAI；受伤早移除handler未恢复NoAI，后续无effect不再进尾tick门。不能把状态已消失当AI已恢复；不与SlowTime orphan扫描及Possession还原actor策略当同链包装。鼠标/移动/NoAI共一种状态家族不拆3。onEntityHit返回false，SpellRay会走onMiss视觉但可仍cast成功，cast反馈非效果最终接纳。',
 'Boss拒控需要明确阻止真实状态及后续AI接管；解除/到期/受伤解除各路径要恢复以前状态，普通体质免疫不因此新增Boss文字要求。',
 '完整Paralysis、SpellRay native方法、实际Potion注册与父类/输入consumer已读。玩家duration取modifiers.get而非本方法getProperty，其数值配置未深入，不假定实际比例。原生remove/其他listener可能影响最终AI，静态缺口不是王朝实测bug；输入清零不证明服务器所有运动不可突破。', 'native_control_expiry_and_early_release_divergence'),
'herschel-015-01':('wizardry-native-client-local-death-marker-overlay-visibility-and-expiry-boundary',
 '实际Disintegration注册→SpellRay命中→FIRE非免疫先setFire、attackEntityWithoutKnockback（保存motion/hurt/无条件还原），忽略bool，只检查Living健康<=0→spawnEmbers。客户端仅首次写disintegrating=ticksExisted；服务端spawn火星，不发这个标记。postInit→ClientProxy.initialiseLayers→Living renderer表及独立Player skin map安装Disintegrate。layer按key绘模型覆盖，frame clamp到0..18；Pre key时deathTime=0/invisible=true，Post key时invisible=false。',
 '一个实际战斗结果的本地目标状态→模型覆盖→可见性/寿命消费链1，与Ars直接移除绕伤害不同。不按19贴图、renderer map、包装加数。shouldRender仅key，19tick后停在最后帧，本链无清key/超龄门；Pre/Post没有保存原隐身，Post强制false。标记非S2C死亡认证，也不是immune回执。LayerTiledOverlay显式depthMask(true)、保存/还原皮肤wear isHidden，texture matrix归零；不能将这些局部还原说成所有GL状态完整恢复。',
 '免疫反馈需要权威事件、目标关联和清理TTL；视觉状态不能代替机制认证。临时渲染状态应还原旧值，不覆盖其他隐身/外观效果。',
 '完整spell/标记producer、layer注册、绘制及模型选择/隐藏还原已读。死亡原因最终裁决、vanilla取消/异常路径是否Post、实体移除寿命未运行，不说永远残留；仅本链没清标记。不制作/复制模型贴图，未验像素或S2C一致。', 'native_combat_result_overlay_lifecycle')}
review={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'master_before':374,'helper_credit_transferred':0,'production_changes':False,'game_started':False,'batches':[],'main_review_scope':'Four proposed chains independently read in main fixed source cache; 12 support/duplicate/missing-chain units remain zero and not all reread fully by main.'}
keys=[]
for n in [13,14,15]:
 path=O/f'helpers/herschel-immune/batch-{n:03}.json';raw=path.read_bytes();d=json.loads(raw);dec=[]
 for row in d['rows']:
  if row['id'] not in configs:
   dec.append({'helper_id':row['id'],'decision':'support_or_excluded_0','credit':0,'main_full_reread_claimed':False});continue
  cfg=configs[row['id']];key=cfg[0];refs=[]
  for ref in row['source_refs']:
   rel=ref['source_key'].split('/',1)[1];src=B/'sources/Electroblob77__Wizardry'/rel
   assert hashlib.sha256(src.read_bytes()).hexdigest()==ref['file_sha256']
   assert ''.join(src.read_text().splitlines(keepends=True)[ref['lines'][0]-1:ref['lines'][1]])==ref['excerpt'] if 'excerpt' in ref else True
   refs.append((rel,*ref['lines']))
  if row['id']=='herschel-014-01':
   for rel in ['potion/PotionMagicEffect.java','potion/PotionMagicEffectParticles.java']:
    refs.append((p+rel,1,len((B/'sources/Electroblob77__Wizardry'/p/rel).read_text().splitlines())))
  if row['id']=='herschel-015-01':refs.append((p+'client/renderer/entity/layers/LayerTiledOverlay.java',65,94))
  record(key,r,refs,*cfg[1:]);keys.append(key);dec.append({'helper_id':row['id'],'decision':'promoted_after_native_chain_and_semantic_review','credit':1,'master_key':key})
 review['batches'].append({'batch':n,'helper_file_sha256':hashlib.sha256(raw).hexdigest(),'decisions':dec})
review['added_effective']=len(keys);review['master_after']=374+len(keys);(O/'HERSCHEL-013-015-REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch127-herschel013-015-main-reviewed-native-chains','credited_chains':keys,'rationale':'Spatial attack boundary and independently executing contact-position control are two different actual production sites. Paralysis early vs tail release and local-death overlay cleanup are independent lifecycle consumers; shared ray, status names, registry, models and codecs receive zero extra. 12 helper support units stay zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
