"""Fixed-source split-priority paid death protection; one whole candidate only."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_text())
p50=H/'immune-reference-batch-050.json';p49=H/'immune-reference-batch-049-screen.json';p45=H/'immune-reference-batch-045.json'
assert ref(p50)['sha256']=='59958fbe55e28774eee1642642401e7da4539601b103d37b8bafa8450051ef6e'
d50=load(p50);d45=load(p45)
v=d50['provenances'][0];mr=(R/v['manifest_path']).read_bytes();assert sha(mr)==v['manifest_sha256']
m=next(x for x in json.loads(mr) if x['repo']==v['repo']);es={x['path']:x for x in m['files']}
prefix='src/main/java/hellfirepvp/astralsorcery/'
refs=[]
def source(n,a=1,z=None,context='actual_read051'):
 e=es[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines();z=z or len(lines)
 assert sha(b)==e['sourceSha256']
 refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
  'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),'reading_context':context})
full=['common/perk/node/key/KeyCheatDeath.java','common/effect/EffectCheatDeath.java','common/effect/EffectCustomTexture.java',
 'common/perk/PerkCooldownHelper.java','common/perk/CooldownPerk.java','common/util/tick/TimeoutListContainer.java',
 'common/perk/node/KeyPerk.java','common/perk/node/MajorPerk.java','common/perk/PerkTree.java','common/perk/data/PerkTypeHandler.java',
 'common/util/CacheEventBus.java','common/perk/data/PerkTreeData.java','common/perk/data/PerkTreeLoader.java',
 'common/perk/data/LoadedPerkData.java','common/perk/data/PreparedPerkTreeData.java','common/registry/RegistryEffects.java',
 'common/util/NameUtil.java','common/util/SidedReference.java','common/lib/EffectsAS.java']
for n in full:source(n)
for n,a,z in [('common/util/entity/EntityUtils.java',1,87),('common/registry/internal/PrimerEventHandler.java',164,167),
 ('common/CommonProxy.java',375,392),('common/perk/AbstractPerk.java',281,281),('common/perk/AbstractPerk.java',143,145),('common/lib/ColorsAS.java',70,70),
 ('common/data/research/PlayerPerkData.java',103,129),('common/data/research/PlayerPerkData.java',182,191),
 ('common/data/research/PlayerPerkData.java',413,438)]:source(n,a,z)
reuse={
 'common/auxiliary/charge/AlignmentChargeHandler.java','common/perk/PerkEffectHelper.java','common/perk/source/ModifierManager.java',
 'common/perk/AbstractPerk.java','common/perk/modifier/AttributeModifierPerk.java','common/data/research/ResearchHelper.java',
 'common/data/research/PlayerPerkData.java','common/data/research/ResearchManager.java','common/registry/RegistryPerks.java',
 'common/registry/internal/PrimerEventHandler.java','common/registry/internal/InternalRegistryPrimer.java',
 'common/network/play/server/PktSyncCharge.java','client/event/AlignmentChargeRenderer.java',
 'common/network/play/server/PktSyncPerkActivity.java','common/network/play/server/PktSyncModifierSource.java',
 'common/event/handler/EventHandlerCache.java','AstralSorcery.java','common/CommonProxy.java',
 'common/network/PacketChannel.java','common/network/base/ASPacket.java','common/network/channel/SimpleSendChannel.java',
 'common/network/channel/BufferedReplyChannel.java'}
for x in d50['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if x['repo']=='HellFirePvP/ObserverLib' or n in reuse:
  if n=='common/registry/internal/PrimerEventHandler.java' and x['lines']==[195,197]:continue
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  refs.append(dict(x,reading_context='exact050_shared_support_reused0'))
for x in d45['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if n=='common/util/tick/TimeoutList.java' or (n=='common/util/MiscUtils.java' and x['lines']==[219,228]):
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  refs.append(dict(x,reading_context='exact045_timeout_support_reused0'))

ledger=A/'immune-feedback-research/reviewed.json';lb=ledger.read_bytes();rows=json.loads(lb);idx={r['id']:r for r in rows}
policy='astralsorcery-native-priority-separated-prepaid-death-token-with-independent-consumption-and-uuid-cooldown-teardown'
assert policy not in {r['semantic_dedup_key'] for r in rows}
dist={
 'tf-lifecharm-native-final-death-cancel-priority':'LifeCharm chooses/consumes an item and directly cancels in one HIGHEST handler, with explicit self packet. Astral HIGHEST only pays/writes cooldown/attempts effect; a distinct LOW effect listener owns cancel/consume for any living holder. The intervening admission/event boundary and independent token lifetime are proposed as a whole, not event priority alone.',
 'ars-player-totem-death-cancel-resource-and-rearm':'Ars directly cancels and deactivates a persistent equipment perk, rearmed by sleep. Astral producer application cooldown is UUID/perk runtime state, distinct from independently consumable timed potion; cooldown expiry, source removal and potion use do not form one active flag.',
 'relics-native-lethal-escape-grants-followup-incoming-immunity':'Relics immediately cancels death then grants follow-up flight/immunity with per-stack cooldown. Astral first pays to attempt a token but does not cancel; later effect listener removes token then restores health and submits nearby fire/knockback, with no blanket subsequent invulnerability. Independent temporary protection owner is essential, not another potion constant.',
 'draconic-native-undying-invulnerability-window-target-activation-receipt':'Draconic immediate charged-module consumption establishes explicit damage immunity window and target activation receipt. Astral producer and final refusal are separated within the same event dispatch; it grants no explicit invulnerability window and its intended dedicated particles are only commented code. No second credit for absence of FX.',
 'occultism-native-guardian-life-budget-death-refusal-and-synced-depletion-feedback':'Guardian consumes external entity lives and successful sacrifice directly gates cancellation. Astral charge payment gates attempted token creation, not later token admission/consumption/cancellation. The final consumer does not verify payer or current cooldown/perk. Neither resource identity nor actor species alone is the difference.',
 'bumblezone-native-terminal-refusal-deferred-current-item-payment-and-cross-world-receipt-queue':'Bumblezone commits refusal before queued teleport/current-offhand payment and delayed cue. Astral commits payment/cooldown before effect admission and later LOW refusal, with a surviving native timed token possible if the consumer is skipped. No async queue/teleport; opposite settlement ownership and distinct token/cooldown expiry form the proposed whole policy.'}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
cmps=[{'accepted_id':k,'complete_semantic_decision_read':{f:idx[k][f] for f in fields},'distinction':val} for k,val in dist.items()]
mig=d50['migration_overlap_screen'];mb=(R/mig['path']).read_bytes();mi={r['candidate_id']:r for r in map(json.loads,mb.decode().splitlines())}
mc=[]
for c in mig['comparisons']:
 assert all(mi[c['accepted_id']][k]==val for k,val in c['complete_semantic_decision_read'].items())
 mc.append({'accepted_id':c['accepted_id'],'complete_semantic_decision_read':c['complete_semantic_decision_read'],
  'distinction':'Existing Astral persistent player research/allocation/clone owner remains accepted. Perk loader/source methods here establish runtime listener/eligibility teardown only; no second migration credit. This new proposed owner is prepaid token creation versus later death cancellation and cooldown lifecycle.'})
progress_path=A/'immune-feedback-research/progress.json';progress=load(progress_path);assert len(rows)==progress['reviewed_effective_semantic_dedup']
observations=[
 'Actual startup CommonProxy initializes PerkTypeHandler, attaches reload listener and server lifecycle setup. PerkTreeLoader loads perk_class through registered KEY_CHEATDEATH constructor, builds Loaded/Prepared tree. Server tree setup/update validates each concrete perk; AbstractPerk.validate dispatches KeyCheatDeath.attachListeners through CacheEventBus to Forge HIGHEST LivingDeath. Tree invalidation unregisters cached listeners and clears this CooldownPerk key. RegistryEffects separately creates/names cheat_death, registers its LOW LivingDeath handler and primes the actual effect. Actual installed tree JSON is not present in this research scope; native dispatch wiring is established, not current-save unlock availability.',
 'Producer is server PlayerEntity with progress.hasPerkEffect(this). Concrete PlayerPerkData query requires map allocation and !isSealed; isSealed checks presence of sealed key, not its boolean payload. It then requires no cooldown and drainCharge(...,false). Default charge350, application cooldown600, token duration500/amplifier0 are config declarations only. Unlike050 there is no chance roll or damage-stage cancellation; producer onDeath never setsCanceled or health.',
 'After successful shared charge drain, producer writes UUID/perk application cooldown BEFORE attempting addPotionEffect(cheat_death,duration,amp,true,false,true). No effect admission result, preexisting-token check, successful later cancellation receipt or refund is inspected. A preexisting token does not suppress the purchase attempt when perk cooldown is absent. Modifier persistence/source helpers and shared charge arithmetic/sync belong to existing050 support; no duplicated credit for them.',
 'Independent LOW listener accepts any server LivingEntity with active cheat_death, even without player type, perk, current charge or cooldown. It first cancels death, immediately removes the active effect and uses returned amplifier, then setHealth(min(maxHealth,4+2*amp)), attempts regeneration200/amplifier2 and fire resistance500/amplifier1. Returned admission results ignored; no deathTime reset, dedicated invulnerability window or clear-all-effects call in this consumer. No source/bypass/void/team/FakePlayer exclusion in the shown gates. Actual final survival/engine arbitration unexecuted.',
 'The two listeners intentionally bridge effect admission within one death event. If producer succeeds but effect is rejected, charge/cooldown remain and that path supplies no token to LOW. If an intervening listener cancels and event dispatch skips LOW, a successfully admitted token may remain until another death or native expiry. Both registrations use the overload without explicitly requesting receiveCancelled; native Forge dispatch details and external listener ordering were not expanded, so these are conditional boundaries, not a demonstrated failure/exploit. If LOW is reached with an independently preexisting token, it can refuse death despite producer cooldown or insufficient charge. No rollback protocol connects the two owners.',
 'After cancellation/health/effect changes, consumer queries alive other LivingEntity in victim AABB.grow(3), then independently setFire(10) and applyKnockback(2,otherX-victimX,otherZ-victimZ). No ally/Boss check or accepted-control result; not a sphere-distance/LOS gate. Exact vector arguments recorded without assuming native knockback direction or guaranteed movement. Refusal of knockback need not undo earlier ignition. These aftermath variants are one consumer policy0 extra, not Boss immunity.',
 'getCurativeItems returns a new empty list: the effect advertises no normal curative items, not universal immunity to commands/other removal. The token has native duration and is removed on successful LOW consumption; it is not explicitly revoked when the granting perk is sealed/removed. Native duration decrement, save/load, merge/reapplication, death rollback and effect synchronization are MC/Forge boundaries. No claim that configured500 tick token survives a particular native death path or that the original item/cast source is retained.',
 'Application cooldown owner is TimeoutListContainer<UUID,ResourceLocation>, separate SERVER and CLIENT containers. Key path writes server only. setOrAddTimeout resets an existing entry or adds one; the consumer does not inspect or remove cooldown. SERVER END ticks each UUID list even if player is offline, predecrements entries and removes on<=0 after callback; outer container removes empty UUID lists. Default600 is remaining ticks, not world timestamp, offline playtime or persisted NBT. Historical Observer TickManager exact support forwards SERVER/CLIENT END calls; no runtime elapsed-time claim.',
 'Cooldown callback resolves current player by UUID and side, then current perk tree key, invokes onCooldownTimeout if still CooldownPerk. KeyCheatDeath callback is empty. Thus timeout emits neither a ready/refund packet nor a revival cue. Removing all cooldowns checks hasList then removes the whole UUID list with callbacks; perk invalidation removes its key across UUIDs. Direct container removeList has no null-ret guard internally, but these helper/clear callers guard existing keys; no caller-triggered crash asserted.',
 'Server logout removes modifier sources through PerkEffectHelper/ModifierManager but does not call removeAllCooldowns for this player; remaining cooldown continues in global SERVER ticker. Clone removes original/reapplies new perks then removes all original-UUID cooldowns; shared charge owner does not clear with that operation. Server stop clears perk tree (unregister/invalidate keys) and cooldown container. Client disconnect clears tree/cooldowns; ordinary source removal is not tree invalidation. No token removal/refund tied to these cooldown clears. Native entity potion transfer on clone is unexpanded.',
 'Synchronization is not an explicit death receipt. Shared charge depletion remains050 regeneration-only PktSyncCharge max/current self state; no key/attack/paid-token/result metadata. The death consumer dedicated PHOENIX_PROC packet lines are commented TODO, therefore neither packet nor particles exist on that shown path. EffectCustomTexture implements actual18px inventory/HUD icon draw calls through sprite query; that depicts active effect only, not final resurrection. Token could be created/consumed in same event, so a visible intermediate icon is not guaranteed. No custom revive sound in either producer/consumer. Native potion/health sync/asset rendering not validated.',
 'Source/perk activity packets and native entry/source-removal methods from050 are reused unchanged. They synchronize eligibility/source changes, not this runtime cooldown or a successful death refusal. No KeyCheatDeath-specific cooldown network write appears in complete producer/helper; generic client cooldown map presence is not proof of server reconciliation. Retained charge after disconnect is already050 and remains0 additional credit.',
 'Compared six complete accepted death/resource policies, entire050 policy and held049 overlap decision. Proposed difference is prepayment→attempted timed token→independent lower-priority death refusal, with nonidentical actor eligibility, cooldown/token/charge lifetimes and no success-specific cue. Not just a second charge consumer or event priority number. All480 saved records screened for candidate concepts, not480 source chains reread; shared methods, registrations, helper bugs, variants and render wrappers0. One whole mechanism max1, pending coordinator decision.'
]
doc={'schema_version':1,'owner':'program-feedback-review-051','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_PREPAID_DEATH_TOKEN_POLICY_PENDING_INDEPENDENT_REVIEW','research_credit':0,'maximum_proposed_credit':1,
 'repo':m['repo'],'commit':m['commit'],'semantic_dedup_key':policy,'provenances':d50['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':[ref(p50),ref(p45)],'scope':'Nineteen newly cited whole files and selected complete methods/declarations actually read051. TimeoutList202 reread but retained045 support. Shared050 source/runtime/charge/transport and Observer tick bindings reused unchanged. Historical migration owner may already have read some loader sources; no first-ever-reading claim. EventHelperInvulnerability81 was explored but its sole producer is attunement, so excluded0. Partial exploratory tails of unrelated methods not cited.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),'comparisons':cmps,
  'scope':'Six full nearest saved semantic decisions read; broad480 keyword/ID screen not counted as480 source reads.'},
 'existing_work_overlap':[{'evidence':ref(p50),'distinction':'050 owns chance/attribute-qualified direct LivingDamage refusal with retained shared charge/regeneration HUD.051 does not re-award charge; its split death producer/token consumer/cooldown state ownership is distinct, subject to review.'},
  {'evidence':ref(p49),'distinction':'049 held reactive true-source relocation/state FX0.051 is prepaid delayed-in-dispatch death cancellation, not new reactive movement; nearby fire/knockback remains aftermath0.'}],
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mb),'comparisons':mc,'scope':'Exact complete prior Astral player-progress judgment reused; unchanged fields checked. No disk IO/allocation-format re-audit.'},
 'whole_chain_observation':observations,
 'application':'原程序应把付费成功、效果接纳和最终拒绝结果分开记录；冷却清除与保护效果清除不能互相冒充。Boss拒控反馈必须锚定最终拒控理由，不能使用救死、点燃/击退或持续图标代替。普通阴阳体质不新增灰字。只研究，不引入复活玩法。',
 'critical_boundaries':['Fixed historical Astral1.16-indev and separately fixed Observer1.5.2 support, no installed Dynasty binary/runtime equivalence.',
 'Current loaded perk-tree JSON, engine effect admission/merge/expiry/sync, canceled-event dispatch defaults/other listeners and final health/death rollback are not executed or fully expanded. Conditional analysis only; no guaranteed lost purchase or actual rescue proof.',
 'Native potion synchronization is an external boundary; dedicated Phoenix packet is commented out and gets zero implementation credit.18px icon draw input is not a visual acceptance.',
 'One entire policy0/max1; main may merge/hold. Shared050 charge/cleanup and045 timeout helpers, repeated definitions, loader framework and native buffers add no credit.',
 'No network/upstream execution/game/Java/Gradle or production/test/art/background/sharedJar/instance/main ledger/checklist edit. No hours claimed.'],
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'runtime_credit':0},
 'next_work':'Coordinator independently reviews051; continue a different original-program fixed-local owner, not a paid charge helper or death-effect parameter variant.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered={}
for x in refs:
 a,z=x['lines'];new=set(range(a,z+1));old=covered.setdefault(x['path'],set());assert not old.intersection(new);old.update(new)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-051.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0,'maximum_pending':1}))
