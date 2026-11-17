"""Close a bounded Feathered Knife screen with no proposed semantic credit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty')
H=Path(__file__).resolve().parent
S=R/'tools/cod4/immune-feedback-research/sources/WayofTime__BloodMagic'
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):
    return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}

meta=json.loads((S/'source.json').read_text())
tree=json.loads((S/'tree.json').read_text())
assert meta['commit']==tree['sha']=='35f0188665e648d981095b6933cc75b0ca96eca5'
assert not tree.get('truncated')
files={x['path']:x for x in meta['files']}
trees={x['path']:x for x in tree['tree']}
prior=H/'immune-reference-batch-056-screen.json'
assert sha(prior.read_bytes())=='9640d5819a2267465d9816eba75383a50580ecf39bd7b58c9143edd1a6ce8783'
old=json.loads(prior.read_text())
refs=[]
for name,ranges,context in [
    ('ritual/types/RitualFeatheredKnife.java',None,'Actual whole class read during056 discovery; unchanged read reused0, now fixed cache binding added. Not reread this turn.'),
    ('network/SetClientHealthPacket.java',None,'New whole class read057: float codec, enqueued client health write.'),
    ('network/BloodMagicPacketHandler.java',None,'New whole class read057: concrete PLAY_TO_CLIENT registration.'),
    ('network/BasePacketHandler.java',None,'New whole class read057: channel direction, protocol and send helpers. Native transport unexpanded.'),
    ('common/tile/TileMasterRitualStone.java',[[61,91],[232,275]],'New complete onUpdate/performRitual/stopRitual methods read057; no full activation/save/helper/ticker chain claim.'),
    ('BloodMagic.java',[[88,243],[295,310]],'New bounded class/field/constructor/setup context read057. Full constructor/setup contained; onLoadComplete only fragment, not a complete initialization audit.'),
]:
    path='src/main/java/wayoftime/bloodmagic/'+name
    p=S/path;b=p.read_bytes();lines=b.decode().splitlines();e=files[path]
    assert sha(b)==e['sha256']
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert blob==e['git_blob_sha1']==trees[path]['sha']
    for a,z in ranges or [[1,len(lines)]]:
        refs.append({'repo':meta['repo'],'commit':meta['commit'],'path':str(p.relative_to(R)),
                     'upstream_path':path,'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':blob,
                     'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),'reading_context':context})
ritual=refs[0]
oldritual=next(x for x in old['discovery_only'] if x['path']==ritual['path'])
assert oldritual['sha256']==ritual['file_sha256'] and oldritual['actual_lines_read']==ritual['lines']

lp=H.parent/'immune-feedback-research/reviewed.json'
rows=json.loads(lp.read_text());index={x['id']:x for x in rows}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation',
        'concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
comparisons={
 'bloodmagic-native-post-hit-execution-eligibility-and-altar-credit-before-final-damage':
  'Same project accepted whole owner already covers explicit special eligibility, direct health mutation outside ordinary damage admission and altar credit not proving final target outcome. FeatheredKnife starts from ritual cadence and player ratio rather than accepted melee hit, and calls altar after health request, but this bounded read does not establish a distinct full immunity/refusal-result lifecycle. Do not split threshold, incense, will pools or numeric packet into credits.',
 'bumblezone-native-crusher-contact-control-versus-stopped-impact-direct-health-settlement':
  'Existing full owner already distinguishes hurt admission from direct setHealth and nonlethal request floors. FeatheredKnife direct health threshold/payment is different gameplay context but no new final control-refusal decision or outcome acknowledgment has been demonstrated. Static health request and client value write remain support0.',
}
covered={}
for x in refs:
    s=covered.setdefault(x['path'],set());a,z=x['lines'];new=set(range(a,z+1));assert not s.intersection(new);s.update(new)
doc={
 'schema_version':1,'owner':'program-feedback-review-057','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'BOUNDED_SCREEN_CLOSED_HELD_ZERO_NO_NEW_WHOLE_REFUSAL_OWNER',
 'research_credit':0,'maximum_proposed_credit':0,'repo':meta['repo'],'commit':meta['commit'],
 'provenance':{'source_manifest':ref(S/'source.json'),'cached_tree':ref(S/'tree.json'),
               'commit_label':meta['commit'],'tree_response_sha':tree['sha'],'cached_tree_url':tree['url'],
               'scope':'Existing local source manifest and cached fixed-commit tree labels/blob entries, not a newly fetched commit object or verified installed binary. No invented separate git-tree root hash.'},
 'source_refs':refs,'prior_read_reuse':{'evidence':ref(prior),'range':ritual,'credit':0},
 'baseline':{'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'ledger':ref(lp)},
 'dedup_snapshot':{**ref(lp),'comparisons':[
   {'accepted_id':k,'complete_semantic_decision_read':{f:index[k][f] for f in fields if f in index[k]},'comparison':v}
   for k,v in comparisons.items()]},
 'bounded_observations':[
  {'stage':'server caller and cancellation boundaries','observation':
   'Tile onUpdate returns client-side, handles redstone stop/restart, and invokes performRitual at activeTime%currentRefreshTime==0 before increment. performRitual requires server/current/enabled, valid structure and uncanceled RitualRunEvent, repairs ranges then calls concrete ritual; invalid structure invokes stop. stop posts cancelable stop event, calls ritual stop and clears ritual/active/time for nonredstone break only. onUpdate sets active=false before calling redstone stop, so cancellation does not itself undo that assignment. Activation method, base ticker registration, event definitions, helper validation and ritual stop implementation are unexpanded: no complete natural activation/cleanup claim.'},
  {'stage':'concrete eligible health extraction','observation':
   'FeatheredKnife concrete method checks owner currentEssence>=20 else causeNausea and return, reads permitted will pools, sets refreshTime10 or20, and computes maxEffects=currentEssence/20. It locates/caches a relative altar or scans configured range; getEntitiesOfClass(Player) in configured box has no explicit Boss/fake/creative/alive filter in this method. Ratio gate is >0.3 normally, >0.7 with steadfast threshold, or >0.1 for nonowner with vengeful threshold. Ordinary sacrificedHealth stays1, so ratio is a precheck, not an exact final health floor. With corrosive incense mode, SOUL_FRAY veto applies and requested health equals health-maxHP*ratio.'},
  {'stage':'settlement order and no new immunity policy','observation':
   'Incense mode consumes incense and attempts SOUL_FRAY without checking effect acceptance; destructive will modifies LP then local balance/drain accumulates, full living armor optionally grants experience. Next direct player.setHealth(requestedValue), then SetClientHealthPacket(requestedValue) to cast ServerPlayer, then altar.sacrificialDaggerCall(int LP,false), then totalEffects increment/budget break. No hurt call/result or final health readback in this sequence. At end owner network syphon uses totalEffects; raw will drain only when effects>0 and faster cadence. No whole transaction/rollback/actual LP capacity acknowledgment established. Altar and network implementations are not newly expanded; accepted comparator provides only its quoted prior boundary.'},
  {'stage':'will pool mismatch supporting0','observation':
   'The local variable accumulated from destructiveWill is passed to WorldDemonWillHandler.drainWill with STEADFAST, not DESTRUCTIVE. This is an exact source enum/variable mismatch, not verified installed depletion or exploit; downstream handler not expanded, no production fix and no extra reference credit.'},
  {'stage':'actual client value receiver','observation':
   'Concrete packet carries one float health; encode/decode have no actor UUID, dimension, sequence, recipe identity or finite-value guard. handle enqueues updateClientHealth and marks handled. Client update writes Minecraft.getInstance().player.setHealth(health) without local null/current-session guard. It is a value replication request for the current client player, not an acknowledgment of altar fill, resource charge, final server HP, hurt refusal or Boss immunity. No late-packet failure or desync was reproduced.'},
  {'stage':'registered direction and dispatch limits','observation':
   'BloodMagic owns one handler; setup calls initialize. Handler initialize registers SetClientHealthPacket as server-to-client; BasePacketHandler specifies PLAY_TO_CLIENT and sends via target ServerPlayer.connection. Protocol compares string1. Constructor contains two addListener(this::setup) calls and handler numeric index increments on registrations, but native bus duplicate behavior and channel registration semantics are unexpanded, so no double initialization/network failure claimed. onLoadComplete only fragment read, not complete ritual discovery proof. Generic channel and packet class are supporting0.'}
 ],
 'decision':'Close this bounded candidate screen at0/max0. Known direct-health/altar settlement families already cover the observed refusal boundary; no separate complete policy established. Missing activation/native context is disclosed rather than counted. Do not count packet omissions, will-enum mismatch, two listeners, ratio changes or effect names separately. This is not an assertion that every BloodMagic ritual is exhausted or semantically equivalent.',
 'application':'Keep final authoritative health/control decision separate from local numeric replication and resource/altar settlement. Feedback should report the actual refusal reason and target identity, not infer success from a float packet. Research only; background and existing UI preserved.',
 'limits':['No game/Java/Gradle/network/native packet or display/audio execution.',
           'Base ticker, real ritual activation/discovery, full altar/network/will/effect/living armor implementation and Forge/Minecraft setter/transport remain unexpanded.',
           '056 whole ritual read reused unchanged0;057 newly reads five files in seven ranges. Four full files overall does not mean all file call chains are complete.',
           'Fixed local cache metadata does not prove exact installed build. Source SHA/blob/range validation is not semantic acceptance.',
           'No production/tests/assets/Jar/instance/master/pending/checklist writes; no task deletion/hours claim.'],
 'source_ranges':len(refs),'unique_files':len(covered),
 'full_files':sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),
 'cited_lines':sum(map(len,covered.values())),
 'new_ranges':len(refs)-1,'reused_ranges':1,
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0,
 'next_work':'Next different fixed-local original-program whole mechanism, excluding Mace/FeatheredKnife numeric motion/payment/direct-health wrappers.053 and055 accepted; do not rerun. No automatic formal credit.'
}
out=H/'immune-reference-batch-057-screen.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'scope':{k:doc[k] for k in ['source_ranges','unique_files','full_files','cited_lines']},'credit':0}))
