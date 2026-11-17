"""Bind actual Requiem reads, but withhold all credit for unresolved release data."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent
B=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-038'
S=B/'sources/Ladysnake__Requiem';sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
mp=B/'source-manifest.json';m=next(x for x in json.loads(mp.read_text()) if x['repo']=='Ladysnake/Requiem')
es={x['path']:x for x in m['files']}
cp=B/'provenance/Ladysnake__Requiem/commit.json';tp=B/'provenance/Ladysnake__Requiem/tree.json'
c=json.loads(cp.read_text());t=json.loads(tp.read_text())
assert c['sha']==m['commit'] and c['tree']['sha']==t['sha']==m['git_tree'] and not t.get('truncated')
ts={x['path']:x for x in t['tree']};refs=[]
specs={
 'requiem-core/src/main/java/ladysnake/requiem/core/remnant/RevivingDeathSuspender.java':None,
 'requiem-api/src/main/java/ladysnake/requiem/api/v1/remnant/DeathSuspender.java':None,
 'src/main/java/ladysnake/requiem/mixin/common/remnant/ServerPlayerEntityMixin.java':None,
 'src/main/java/ladysnake/requiem/common/dialogue/RemnantChoiceDialogueAction.java':None,
 'src/main/java/ladysnake/requiem/mixin/common/remnant/DamageTrackerMixin.java':None,
 'src/main/java/ladysnake/requiem/client/ZaWorldFx.java':None,
 'src/main/java/ladysnake/requiem/mixin/client/remnant/BlabberDialogueScreenMixin.java':None,
 'src/main/java/ladysnake/requiem/mixin/client/remnant/GameRendererMixin.java':None,
 'src/main/java/ladysnake/requiem/mixin/client/remnant/PlayerRendererLayerMixin.java':None,
 'src/main/java/ladysnake/requiem/common/gamerule/StartingRemnantType.java':None,
 'requiem-core/src/main/java/ladysnake/requiem/core/util/serde/DamageSourceSerialization.java':None,
 'src/main/java/ladysnake/requiem/common/advancement/criterion/OnRemnantChoiceCriterion.java':None,
 'src/main/resources/quilt.mod.json':None,
 'src/main/resources/mixins.requiem.common.json':None,
 'src/main/resources/mixins.requiem.client.json':None,
 'src/main/java/ladysnake/requiem/client/RequiemClient.java':[[86,149],[221,229]],
 'src/main/java/ladysnake/requiem/common/RequiemComponents.java':[[85,130]],
 'src/main/java/ladysnake/requiem/Requiem.java':[[80,125]],
 'src/main/java/ladysnake/requiem/common/remnant/RemnantComponentImpl.java':[[35,101]],
 'src/main/java/ladysnake/requiem/common/VanillaRequiemPlugin.java':[[260,274]],
 'src/main/java/ladysnake/requiem/common/advancement/criterion/RequiemCriteria.java':[[35,58]],
 'src/main/java/ladysnake/requiem/common/gamerule/RequiemGamerules.java':[[35,58]],
}
for path,ranges in specs.items():
    e=es.get(path);p=R/e['source'] if e else S/path;b=p.read_bytes();ls=b.decode().splitlines()
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert blob==ts[path]['sha']
    if e:assert sha(b)==e['sourceSha256'] and blob==e['source_blob']
    for a,z in ranges or [[1,len(ls)]]:
        assert 1<=a<=z<=len(ls),(path,a,z,len(ls))
        refs.append({'repo':m['repo'],'commit':m['commit'],'path':str(p.relative_to(R)),
                     'upstream_path':path,'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':blob,
                     'range_text_sha256':sha('\n'.join(ls[a-1:z]).encode()),
                     'binding':'source manifest + fixed commit tree blob' if e else 'existing local resource + fixed commit tree blob; absent from filtered source manifest'})
lp=H.parent/'immune-feedback-research/reviewed.json';rows=json.loads(lp.read_text());idx={x['id']:x for x in rows}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
p53=H/'immune-reference-batch-053.json';o53=json.loads(p53.read_text())
pk='playerrevive-native-helper-membership-pauses-terminal-bleed-clock-and-integrates-authoritative-release-with-asymmetric-helper-feedback-exit'
prior=next(x['complete_semantic_decision_read'] for x in o53['dedup_snapshot']['comparisons'] if x['accepted_id']==pk)
assert all(idx[pk][k]==v for k,v in prior.items())
vk='vampirism-native-down-not-dead-refusal-and-control-state'
comparisons=[
 {'accepted_id':vk,'reading':'Full substantive current decision newly read059','complete_semantic_decision_read':{k:idx[vk][k] for k in fields if k in idx[vk]},
  'comparison':'Generic death denial, protected downed state and clear-before-terminal entry already owned. Requiem potentially differs by first-choice transaction and original death continuation, but missing dialogue/advancement data prevents a qualified complete owner.'},
 {'accepted_id':pk,'reading':'Exact complete053 decision reused unchanged; truncated current output is not claimed full','reused_evidence':ref(p53),'complete_semantic_decision_read':prior,
  'comparison':'Cooperative helper clock/recovery differs conceptually from choice suspension. Generic DBNO supports0, and no novel full candidate is accepted here.'}]
mlp=H.parent/'legacy-migration-acceptance/reviewed.jsonl';mr=next(json.loads(l) for l in mlp.read_text().splitlines() if l.strip() and json.loads(l).get('candidate_id')=='adc8de743cd7133ab85a')
mf=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
covered={}
for x in refs:
    s=covered.setdefault(x['path'],set());a,z=x['lines'];n=set(range(a,z+1));assert not s.intersection(n);s.update(n)
d={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'MOD_OWNED_POLICY_READ_BUT_DIALOGUE_DATA_AND_RELEASE_GUARD_UNCLOSED',
 'research_credit':0,'maximum_proposed_credit':0,'repo':m['repo'],'commit':m['commit'],
 'provenance':{'manifest':ref(mp),'commit_metadata':ref(cp),'tree_metadata':ref(tp),'git_tree':m['git_tree']},
 'source_refs':refs,'source_ranges':len(refs),'unique_files':len(covered),
 'full_files':sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),'cited_lines':sum(map(len,covered.values())),
 'whole_decisions_compared':comparisons,
 'migration_overlap':{'ledger':ref(mlp),'complete_semantic_decision_read':{k:mr[k] for k in mf},
 'decision':'Existing remnant persistence/type/derived abilities/respawn owner retained0. Its support explicitly already includes DeathSuspender NBT/copy/cause/timer caveats; those cannot be counted again.'},
 'bounded_observations':[
 'Declared main common/client mixins and CCA entrypoint present. Registered DeathSuspender uses RevivingDeathSuspender LOSSLESS_ONLY; API AutoSynced+ServerTicking. Native onDeath HEAD checks choice advancement/not-hardcore and CHOOSE gamerule; requests suspend then cancels original death even if suspend returns early for transient state or nonexact ServerPlayer subclass. Force modes become(type,true) without this cancellation. No installed mixin/CCA execution verified.',
 'Suspend requests HP1, Entity invulnerable=true plus PAL INVULNERABLE source grant; stores cause, timer20, transient=true, sync. Server playerTick and DamageTracker.update cancel when flagtrue. Timer predecrement==0 calls external Blabber dialogue exactly once; no callback-success/timeout fallback here. Direct flag and ability-source changes are separate; no universal immunity/prior-flag preservation proof.',
 'Registered choice action handle calls become(chosen,true), then transient-guarded resumeDeath. become invokes MADE_REMNANT_CHOICE criterion before same-type/fakeplayer early returns. Chosen/current comparison controls sound/opus request without change-result check; packet/consumer not expanded. Criterion triggers registered conditions, but advancement JSON and actual dialogue selection wiring unavailable. Cannot prove the_choice becomes done before reentrant death or authenticate a real client response.',
 'Resume unconditionally clears Entity invulnerability and revokes own PAL source, setsHP0, flagfalse, syncs, then calls onDeath(saved or GENERIC). It does not clear saved cause/countdown. Under source read alone it can reenter original advancement gate if unmet; no reproduced loop, guaranteed death, immortal state or reward duplication claim.',
 'NBT saves transient/cause but not timer20. Reader setsflag and only reads deathCause when world.isClient then casts ServerWorld; server does not restore cause. Fresh transient-loaded instance timer0 decrements to-1, so local equality0 dialogue branch is missed; same-object load can retain old timer/cause. Native load/clone/disconnect/CCA semantics unverified; these are already old migration support0.',
 'Bool sync carries onlylifeTransient; apply setsflag, not health/cause/countdown/abilities. Client init creates ZaWorldFx and registers ENDtick/world/shader callbacks. Entry edge requests time-stop sound and radius animation; hasFinishedAnimation=!rendering||ticks>60. Blabber screen mixin cancels render while animation unfinished, not input or server dialogue. Player null/flagfalse clears rendering; nexttrue restarts entry. Presentation is not server-world freeze or final-death receipt.',
 'Client outline suppression and ghost/endportal player layer read transientflag. Native Satin shader/graphics unexpanded. Vanilla plugin helper forbids transient interaction evencreative, but full caller registration not read, so no all-action blockade claim. No screen/audio/game execution.'
 ],
 'missing_for_complete_candidate':[
 'Fixed remnant_choice dialogue data and Blabber actual start/reply/action dispatch; no validated authorization/session binding or selectable path.',
 'Fixed adventure/the_choice advancement JSON/conditions and native award-to-reentrant-death guard. Criterion Java does not substitute actual data.',
 'External PAL/CCA/native lifecycle exact version not expanded; server playerTick cancellation versus CCA component ticking composition unverified.'
 ],
 'local_availability':'Named dialogue/advancement assets and Blabber implementation not found by bounded tools/cod4 source inventory. Existing mixin/mod JSON files were actually read and tree-blob bound directly despite absent filtered manifest entries. Cached tree is not contents of missing assets. No network; other local archives not globally exhausted.',
 'counting':'Every059 field/NBT defect/time constant/renderer/helper counts0. Gaps mean no complete proposed reference; not waiting for semantic acceptance to continue.',
 'validation':'New source/resource SHA/blob/tree/range bindings and exact reused judgment checked once during sealing. No old verifier/master ledger validator rerun.',
 'next_work':'Continue another fixed-local mechanism. Forestry helper/potion/aggressive classes already actually read as initial060 discovery only, not a novel policy or credit.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
out=H/'batch-059-death-suspension-gap-review.json'
with out.open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'review':ref(out),'scope':{k:d[k] for k in ['source_ranges','unique_files','full_files','cited_lines']},'credit':0}))
