"""Seal fixed-local Forestry source-side equipment protection overlap, credit0."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent
B=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-015'
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
mp=B/'source-manifest.json';m=next(x for x in json.loads(mp.read_text()) if x['repo']=='ForestryMC/ForestryMC')
cp=B/'provenance/ForestryMC__ForestryMC/commit.json';tp=B/'provenance/ForestryMC__ForestryMC/tree.json'
c=json.loads(cp.read_text());t=json.loads(tp.read_text());assert c['sha']==m['commit'] and c['tree']['sha']==t['sha']==m['git_tree'] and not t.get('truncated')
es={x['path']:x for x in m['files']};ts={x['path']:x for x in t['tree']};refs=[]
specs={
 'apiculture/ArmorApiaristHelper.java':None,
 'apiculture/genetics/alleles/AlleleEffectPotion.java':None,
 'apiculture/genetics/alleles/AlleleEffectAggressive.java':None,
 'apiculture/capabilities/ArmorApiarist.java':None,
 'apiculture/items/ItemArmorApiarist.java':None,
 'apiculture/genetics/alleles/AlleleEffectThrottled.java':None,
 'apiculture/genetics/alleles/AlleleEffect.java':None,
 'apiculture/genetics/alleles/AlleleEffects.java':None,
 'api/apiculture/IArmorApiarist.java':None,
 'apiculture/BeekeepingLogic.java':[[160,320],[495,525]],
 'apiculture/genetics/Bee.java':[[156,217]],
 'apiculture/ModuleApiculture.java':[[202,232],[919,936]],
 'apiculture/items/ItemRegistryApiculture.java':[[90,103]],
 'apiculture/tiles/TileBeeHousingBase.java':[[138,184]],
 'apiculture/genetics/BeeDefinition.java':[[304,345]],
 'apiculture/genetics/BeeBranchDefinition.java':[[25,51]],
}
for short,ranges in specs.items():
    path='src/main/java/forestry/'+short;e=es[path];p=R/e['source'];b=p.read_bytes();ls=b.decode().splitlines()
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert sha(b)==e['sourceSha256'] and blob==e['source_blob']==ts[path]['sha']
    for a,z in ranges or [[1,len(ls)]]:
        assert 1<=a<=z<=len(ls),(path,a,z,len(ls))
        refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':path,
          'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':blob,
          'range_text_sha256':sha('\n'.join(ls[a-1:z]).encode()),
          'reading_context':'Actual060 source read; initial three whole classes read during059 exploration in same work interval. All other methods/ranges read before sealing. No native whole-file claim for bounded context.'})
lp=H.parent/'immune-feedback-research/reviewed.json';rows=json.loads(lp.read_text());idx={x['id']:x for x in rows}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
ks={
 'occultism-native-equipped-or-owned-upgraded-familiar-final-effect-rejection':'Already owns live equipment/qualified capability source controlling effect denial. Forestry counts matching equipment returns before its own addPotionEffect/hurt call; producer-local placement and slot quantity alone do not establish another whole immunity policy. No owner/pet upgrade lifecycle here; ordinary qualification/count variants held0.',
 'mekanism-native-purification-paid-effect-duration-advance-and-hidden-rollover':'Existing owner distinguishes accepted effect duration processing from final refusal. Forestry changes requested duration before admission, not an active hidden-effect queue; this is a useful boundary but not new accepted state-lifecycle evidence. No post-admission cleansing claim.',
}
comps=[{'accepted_id':k,'reading':'Complete substantive decision newly read060','complete_semantic_decision_read':{f:idx[k][f] for f in fields if f in idx[k]},'comparison':v} for k,v in ks.items()]
p56=H/'immune-reference-batch-056-screen.json';prior=json.loads(p56.read_text());pk='pnc-native-fall-resource-budget-total-refusal-versus-partial-mitigation'
pc=next(x['complete_semantic_decision_read'] for x in prior['dedup_snapshot']['comparisons'] if x['accepted_id']==pk)
assert all(idx[pk][k]==v for k,v in pc.items())
comps.append({'accepted_id':pk,'reading':'Exact056 complete decision reused unchanged0','reused_evidence':ref(p56),'complete_semantic_decision_read':pc,
 'comparison':'Existing whole partial-versus-total mitigation and non-result cues owner. Forestry integer equipment count and duration/damage scale variants add0. Default armor protection consumes no resource, unlike PNC, so no paid mitigation claim.'})
covered={}
for x in refs:
    s=covered.setdefault(x['path'],set());a,z=x['lines'];new=set(range(a,z+1));assert not s.intersection(new);s.update(new)
d={'created_utc':datetime.now(timezone.utc).isoformat(),'owner':'program-feedback-review-060',
 'status':'BOUNDED_SOURCE_POLICY_SCREEN_COMPLETE_HELD_ZERO_OVERLAP','research_credit':0,'maximum_proposed_credit':0,
 'repo':m['repo'],'commit':m['commit'],
 'provenance':{'manifest':ref(mp),'commit_metadata':ref(cp),'tree_metadata':ref(tp),'git_tree':m['git_tree']},
 'source_refs':refs,'source_ranges':len(refs),'unique_files':len(covered),
 'full_files':sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),'cited_lines':sum(map(len,covered.values())),
 'baseline':{'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'ledger':ref(lp)},
 'dedup_snapshot':{**ref(lp),'comparisons':comps},
 'bounded_chain':[
 {'stage':'registered concrete source and protection implementation','observation':'Actual module context installs ArmorApiaristHelper and registers capability default ArmorApiarist.INSTANCE; item registry constructs four equipment-slot armor items. Item capability returns default implementation; protectEntity unconditionallytrue, ignoring cause/doProtect and doing no durability/energy payment. Helper supports legacy item-interface or capability, skips empty stacks, queries cause=effect UID and doProtect=true. It counts entity.getEquipmentAndArmor(), not a hardcoded four armor-slot scan. Native iterable/third-party capabilities unexpanded, no universal item count/inventory exploit assertion.'},
 {'stage':'concrete gameplay dispatch','observation':'AlleleEffects constructs Aggressive and harmful potion effects, then registerAlleles registers EFFECT chromosome. Read SINISTER/FIENDISH setAlleles selects aggressive; TROPICAL branch selects miasmic. These are actual source template methods, not proof whole breeding/natural acquisition. TileBeeHousingBase.updateServerSide calls canWork then doWork. canWork computes queen/error/flower state and synchronizes active state; doWork chooses princess breeding or queenWorkTick. Nonnull queenWorkTick calls queen.doEffect before production throttle. Source bootstrap/tile ticker factory/module enablement and complete world setup remain external to bounded screen.'},
 {'stage':'effect selection and throttle','observation':'Bee.doEffect validates storage then runs active effect; inactive effect only if both combinable. Both studied effects are noncombinable, so no second independent effect credit. Throttled implementation reuses any EffectData instance or creates one integer slot, skips increment if requiresWorkingQueen and housing errors, otherwise increments and resets on configured threshold. Aggressive threshold40/no working flag, potion threshold configured/requiresWorking=true; current housing work gate still applies at caller. These are call counts, not independently proven wall-clock ticks or full save/load policy.'},
 {'stage':'target eligibility and source-side partial/full rejection','observation':'Actual AABB derives genome territory times housing modifier with scaled offset; getBounding does not call clamped getModifiedArea. Enumerates EntityLivingBase, no explicit target owner/Boss/alive/line-of-sight predicate in these methods. Aggressive starts damage4, subtracts protective count, skips attack when <=0, else requests attackEntityFrom without checking result. Potion first random chance, then for harmful effect count>=4 skips; counts3/2/1 shorten newly requested duration to1/4,1/2,3/4. Beneficial potion skips IMob and never queries armor. addPotionEffect result/final native admission unexpanded. Full protection prevents these producer calls, not all sources/effects on the target.'},
 {'stage':'presentation and exit boundaries','observation':'Client tile checks canDoBeeFX and interval4; canDoBeeFX tests local not-paused and active, doBeeFX calls current queen.doFX. Bee FX selection is independent of target protection/chance/result. Potion FX randomly delegates to generic bee FX or requests colored potion particles at housing position; no target success/refusal list. Base effect requests hive FX using flowers. These source activity cues are not target immunity receipts. No custom lasting target immunity state is established: every eligible source pulse rechecks equipment. Removing gear does not remove previously admitted native potion; ordinary duration/hidden-state cleanup belongs engine and is unexpanded.'}
 ],
 'decision':'Conservative whole screen held0/max0 after nearest whole decisions. Live capability qualification, numeric partial/full source suppression and independent hive FX do not establish another counted immunity/control/feedback lifecycle. Do not count each armor piece, bee species, potion, slot/counter/helper or renderer as a reference.',
 'limits':['Historical mc-1.12 fixed Forestry source, not Dynasty API/runtime.',
 'Bounded full effect/helper/armor classes and containing dispatcher methods read; entire large module/BeeDefinition/housing bootstrap classes not claimed full. Source breeding/actual installed templates, native iterable/hurt/potion arbitration, capability storage and source FX packet/particle renderer lifetime unexpanded.',
 'No attempted execution of upstream source, game, audio, display, Gradle/Java or network. No target feedback request, actual successful hurt/status, delivered particles or runtime fault claimed.',
 'New source bindings are provenance checks, not acceptance. All implementation notes/support and reused comparisons0. No task deletion or hours claim.'],
 'application':'Reject control at the actual source/target policy boundary and report a final reason. Keep partial duration/amount reduction separate from full denial; activity particles cannot supply an immunity acknowledgment. Research only.',
 'next_work':'Next different whole mechanism; exclude generic equipment-count and effect/damage variants.058/059 remain explicit missing-link studies0, not submitted complete candidates.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
out=H/'immune-reference-batch-060-screen.json'
with out.open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'scope':{k:d[k] for k in ['source_ranges','unique_files','full_files','cited_lines']},'credit':0}))
