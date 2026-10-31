"""Main semantic review of Herschel034/035; three game policies, zero automatic helper credit."""
from ledger import B,O,record,verify
import json,hashlib
repo='Momo-Softworks/Cold-Sweat';root=B/'sources/Momo-Softworks__Cold-Sweat';p='src/main/java/com/momosoftworks/coldsweat/'
extra=[]
for f in ['src/main/resources/cold_sweat.mixin.json','src/main/resources/data/cold_sweat/cold_sweat/entity/temp_effects/default_player.json','src/main/resources/data/cold_sweat/cold_sweat/entity/temp_effects/default_entity.json',p+'mixin_plugin/ColdSweatMixinPlugin.java',p+'api/temperature/effect/TempEffect.java',p+'common/event/HandleTempEffects.java']:
 extra.append((f,1,len((root/f).read_text().splitlines())))
extra.extend([(p+'api/util/Temperature.java',88,90),(p+'common/capability/temperature/AbstractTempCap.java',70,83),(p+'common/capability/handler/EntityTempManager.java',765,767),(p+'common/capability/handler/EntityTempManager.java',824,829),(p+'util/math/CSMath.java',214,222)])
def helper_refs(batch,row):
 d=json.loads((O/f'helpers/herschel-immune/batch-{batch:03}.json').read_text());r=d['rows'][row];refs=[]
 for v in r['source_refs']:
  prefix='Momo-Softworks__Cold-Sweat/';assert v['source_key'].startswith(prefix)
  rel=v['source_key'][len(prefix):];a,z=v['lines'];assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==v['file_sha256'];refs.append((rel,a,z))
 return refs+extra
limits='主岗完整复读helper列出包含方法及原生注册/生命周期，额外固定默认数据和mixin清单/plugin已读；默认player启用冷效且普通entity effects空，不宣称自定义整包也如此。冷range原始min=-50/max=-100由betweenInclusive和blend正确处理反序，非未核实失效。Temperature.get→启用cap的BODY=CORE+BASE，resistance同cap trait；上游所有气候/装备/同步数值生产者、第三方全局listener次序及Forge内部派发未穷尽。动态注册的效果对象无cap所有者过滤字段，按事件实体做test；不据静态结构宣称跨实体实际叠乘或运行bug。无真实客户端/移动物理/网络/像素/声音验收，无正式修改或编译。'
k1='coldsweat-native-thermal-qualified-voluntary-input-vector-replacement'
record(k1,repo,helper_refs(34,0),
 '实际ColdSweat constructor注册TempEffectInit，配置loader分类型列表、LivingTick每20tick按首匹配配置向cap新增效果与总线listener。SERVER FreezeMoveSpeed读实际EntityMoveEvent内Living温度资格及抗性→非零penalty修改当前speed并cancel。已列mixin在原生Entity.moveRelative写motion前post事件，取消时以修改后direction/speed/currentYaw重新getInputVector，并add到既有deltaMovement。',
 '最终实际控制输入替代生产点1，与已有冻伤source取消/热源quota不同。cancel是选择新输入而非停止所有运动；existing速度/外部击退不在这条链归零。冲刺腾空penalty*1.5，上界min1；免温factor0或reduction0不取消、不改输入。控制抗性归移动实体自身；不是hurt=false/灰字或原生药水准入。每cap/type只首次注册，换bounds同type不换对象，effectsData缺失提前return而不清旧effect；remove/leave明确unregister。这些共享lifecycle不再拆数。',
 'Boss纹丝不动必须证明拒绝相应控制输出，不能拿event canceled等同无位移；自主输入、残余速度和攻击击退应明确区分。拒控回执仍需服务端理由，普通阴阳不加文字。',limits,'native_control_input_substitution')
k2='coldsweat-native-last-attacker-thermal-qualified-knockback-output-weakening'
record(k2,repo,helper_refs(34,1),
 '同一真实配置/lifecycle注册独立SERVER FreezeKnockback。原生LivingKnockBackEvent callback从受害者.getLastHurtByMob取攻击者，按该实体creative/spectator、BODY范围、GRACE/和平/抗性资格，强度乘blend(1,1-reduction,factor)。remove/leave卸载listener。',
 '一个不同最终原生击退强度生产位点1，和voluntary input替代不互相调用；非同事件换常量/实体名模板。资格来源是victim记忆的上次攻击者，不是victim自身温度，也无当前DamageSource核对；不是目标Boss免控。null旧攻击者不改强度；攻击者免温factor0恢复原强度，受害者免温不由此门判断。没有event.cancel、伤害成功判断或强度非负guard；这里只能说写入事件输出，不保证最终实体移动。',
 '免疫提示不能把攻击者虚弱或旧攻击者记忆当作受害者Boss免疫。每次回执必须绑定实际来源和最终拒控因果，不能凭击退弱就发灰字。',limits+'LivingKnockBackEvent框架生产/lastHurtByMob赋值精确时机和后续抗击退消费未独立全文展开，相关引擎依赖支持0；不宣称该stored attacker就是本次冲量源。','native_attacker_qualified_control_output')
k3='coldsweat-native-frozen-health-healing-budget-and-independent-heart-overlay'
record(k3,repo,helper_refs(35,0),
 '真实SERVER FreezeHealing在LivingHeal按frozen=round(blend(0,maxHealth*percentage,factor))预算，把heal amount限制0..max(0,unfrozen-currentHealth)。已列MixinLimitFoodRegen在原生FoodData.tick HEAD捕获player，再redirect自然回血gamerule，只现有效果map+非零percentage且当前HP达unfrozen上限则false。CLIENT FreezeHearts独立注册，真实Gui.renderHeart TAIL发RenderHeartEvent后按同公式draw冻结半/全/极限心overlay，RenderTick START重置heartIndex。',
 '一个冻伤治疗上限实际拒绝/数量截断与反馈消费者整链1，不拆heal/native food path/heart painter三份，与AntiHeal简单status一律cancel和一次濒死leaf预算不同。不直接扣已有超上限HP；factor0解冻预算而不超原maxHealth。food redirect不重新调用test，默认map曾注册不等本次range合格；static STORED_PLAYER未finally清除，主tick关联只源码可见，不外推重入问题。HeartIndex仅container递增，overlay是原版画完后叠加，无取消原心绘制。client/server两个type与独立条件，数值同式不等跨端最终显示一致。',
 '可见反馈应表示实际预算/拒控语义，不能拿HUD冻结心替代Boss头顶拒控灰字；服务端最终裁决与独立本地重算必须分别记录并验收。',limits+'食物回执和GUI仅真实原生注入源静态证据，未检查GUI/HUD冲突、Forge healing最终settlement或TCP一致性；并不计不相关通用GUI图形库。','native_healing_refusal_budget_and_feedback')
for n,keys in [(34,[k1,k2]),(35,[k3])]:
 file=O/f'helpers/herschel-immune/batch-{n:03}.json';d={'helper_batch':n,'helper_file_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'helper_original_credit':0,'main_review_new_effective':len(keys),'promoted_keys':keys,'main_review':'Primary read full listed methods/native chain, fixed immutable source hashes and semantic difference. Default JSON+mixin/plugin supplemented; no method/file/template count inflation. Shared bounds, immunity factor, registration and lifecycle0.','limits':limits}
 (O/f'HERSCHEL-{n:03}-REVIEW.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch153-thermal-input-knockback-healing-three-native-sites','credited_chains':[k1,k2,k3],'rationale':'Three distinct final game policies: voluntary movement-input replacement, last-attacker-qualified knockback strength, and frozen-health healing budget with heart overlay. Not hot/cold or species constants; registration/config/temperature factor/side/lifecycle/render helper wrappers and heat camera context0. Existing temperature damage and source immunity rows unchanged.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
verify()
