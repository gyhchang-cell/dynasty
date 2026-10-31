"""Native time-bucket anti-reroll control refusal; no sound/prediction runtime claims."""
from ledger import B,O,record,verify
import json
r='Electroblob77/Wizardry';p='src/main/java/electroblob/wizardry/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='wizardry-native-shared-world-time-bucket-casting-refusal-and-client-fail-cue'
record(k,r,[w('spell/ArcaneJammer.java'),w('event/SpellCastEvent.java'),f('item/ItemWand.java',377,545),f('spell/SpellRay.java',160,173),f('spell/SpellRay.java',255,300),f('registry/Spells.java',414,414),f('registry/WizardryPotions.java',125,126)],
 '真实register new ArcaneJammer和arcane_jammer PotionMagicEffect，SpellRay原生cast→shootSpell→onEntityHit服务端对living加持续status。ItemWand原生rightclick→canCast(0) post可取消SpellCastEvent.Pre，HIGHEST ArcaneJammer listener把Random seed设worldTotalTime/15，丢第一次nextInt2后按status amp+2的nextInt>0 cancel。最终canCast见cancel早退，不继续spell.cast或正常cost/cooldown。拒绝WAND/SCROLL时setActiveHand MAIN、请求MISC_SPELL_FAIL声、client眼前+look的5烟粒子。',
 '同15tick时间桶重复尝试不重新随机，时间驱动的拒控准入与回执实际家族1，不按全局Random调用/音色/粒子包装计；seed没有目标UUID或dimension salt，相同world time/amp不同实体可能结果一致，绝非按目标节流。拒绝每次Pre仍请求声音/烟雾，不能称防刷屏已完成。continuous后续只postTick，ArcaneJammer只监听Pre；charged在onUsingTick直接cast，先前许可不会再次Pre检查，源码TODO准确保留。Potion add没有返回接纳检查，初次ray的成功/音效不证明目标被控制。',
 'Boss拒控回执节流与“同一时窗禁止重roll”两种目标不同；不能用确定性概率冒称每目标不刷屏。正式Boss字应跟服务端明确免控决定发送，普通体质不扩展。',
 '全文ArcaneJammer/SpellCastEvent与完整ItemWand关键方法及ray关键方法已观察，实际spell/potion注册核对。Illager反射写spellTicks10的listener已读，但对应原版Evoker AI消费未读，不据此另计或宣称可完全禁原版施法；烟粒子与playSound只有原生调用证据，无运行/像素/两端实测。Forfeit整类另读作支持0，不把每个反噬效果/文本常量算Boss拒控实现。','native_time_bucket_control_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'wizardry-batch94-shared-time-bucket-control-refusal','credited_chains':[k],'rationale':'Actual pre-cast admission uses shared deterministic time buckets to resist spam rerolls; neither a new damage constant nor wrapper over existing body immunity. Repeated sounds not throttled. Illager reflection, Forfeit discovery failures and Clairvoyance navigation outside studied native denial chain zero extra.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
