"""Integrate manually reviewed helper suggestions; explicit decisions, no proposal auto-credit."""
from review_batch import accepted,record,O
from pathlib import Path
import json,hashlib
source=O/'helpers/halley-migration/batch-001.json'
a=json.loads(source.read_text());rs={int(r['id'].split('-')[-1]):r for r in a['records']}
# Chosen only after reading complete provided reader/writer/consumers and master family comparisons.
choices={
1:'Deferred attachment slot restoration is distinct from Curios or Aether file import; one actual accessories owner chain. Master additionally read full AccessoriesContainerImpl.write. Invalid-stack queue drained without success acknowledgement; old keys overwrite modern keys, shrink starts size-1.',
2:'Actual manual quest completion list on disk + toggle + completion consumer, not generic JSON infrastructure. One client-local book progress owner; not server rewards or Clone. Whole-file parse failure overwrites defaults, history omitted from serialize.',
3:'Camo load validates current content factory after codec, removes invalid formerly paid material. Concrete gameplay state recovery negative example; double-camo and flags together1. Native/codec internals untraced, no safe alias recipe claim.',
5:'Owned displayed stack restored then actually returned, map marker cleanup before return; unlike generic 27slot wrapper, complete owner-specific consumer read. Rotation/scheduling not permanent progression. give helper untraced so no lossless return guarantee.',
9:'Concrete planted flower uses registry ID and actual item drop consumer, distinct owned registry-backed state. Invalid ID has no opaque preservation; apply-if-nonempty may retain stale reused flower. No proof null Identifier accepted safely.',
10:'Player-configured physical block shape restored and consumed by collision shape cache; concrete game state, no asset production. Packed disk vs component representation; raw offsets not validated and low bits only decoded. Whole family1.',
11:'Paid roller source resources converted to overlay+count then recoverable physical source item; disk count bounded but stream VAR_INT unbounded. Missing overlay discards count, zero-count overlay retained, extract ignores SlotAccess.set result. One codec+consumer chain1.',
12:'Carrier ownership transaction independently guards clear on successful addFreshEntity, beyond previously credited dragon-owned gear/growth reader. DragonBase support already counted0extra. Unknown entity id retains carrier; null type.create unguarded; no explicit server release guard.',
13:'UUID recall references existing world entity, not serialized horn payload. Actual index persistence+summon consumer distinct owner; wide contains Dragon key match and clear-all after any success risk partial receipt loss. Binding writer not supplied so do not claim whole capture path.',
16:'Actual earned taming accumulation paired with persistent integer session entityId, consumer getEntity not stable UUID; master read server mutual-gaze progression branch including final tame. Specific identity-loss counterexample distinct inventory/egg/colony. No runtime proof of wrong-player assignment.',
17:'Saved mounted taming work has actual consumer: master read progression/reset/tame branches. No rider resets work immediately despite persistence, different lifetime from cooldown/flying; neither all timers permanent nor saved means resumable. Full unrelated combat tick not read, not claimed.',
21:'Concrete world encounter generation spacing history, not generic SavedData infrastructure; full load/save/check/get read. Static global map not cleared across loads and loop overwrites distance result; no world generation/game launch. Not a building design reference.',
24:'Historical shulkerBoxContents vs storageContents outer UUID owner + actual placement consumes saved receipt, distinct existing stack capacity promotion and canonical wrapper serializer. Same normalizeInventory helper0, missing UUID fatal, remove-before-capacity-init no rollback.',
25:'Actual orphaned double-chest overflow recovery consumer distinct generic inventory serializer. Source clears before deferred TickTask drops; no server means clear without return; linked owner excluded. All overflow slots1.',
26:'Actual live storage tier snapshot replacement independent from canonical disk reader: new BE imports before old removed, beingUpgraded suppresses orphan salvage. Linked capacity failure after removal and dual conversion non-atomic. One all-tier owner conversion.',
27:'Actual vanilla Container interface-to-new owner transfer selective items/name, different from mod BE whole snapshot. Destination grows before installing slot references; arbitrary source metadata omitted. Shared capacity wrappers0. Partial double chest lacks rollback.',
29:'Actual item crafting tier conversion preserves original full components then resets slot limits; primary endpoint guard present and server manager validation in matches. Shared canonical wrapper0, shaped/shapeless/double one family; broad components inappropriate for whitelist player Clone.',
30:'Actual vanilla item capability-to-new item storage conversion, distinct world BE importer and full component copy recipe. Ignores insertion remainder, loses name/other components, missing capability still yields crafted item. Slot copying entire owner1.'
}
indexfile=O/'candidates.jsonl';index={r['candidate_id']:r for r in map(json.loads,indexfile.read_text().splitlines())};added=[]
for n in list(choices)+[6]:
 for e in rs[n]['evidence']:
  raw=Path(e['private_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['file_sha256'];assert hashlib.sha256(e['context'].encode()).hexdigest()==e['method_sha256']
  if e['candidate_id'] not in index and 'supporting field declaration' not in e['method']:
   q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};index[q['candidate_id']]=q;added.append(q)
with indexfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[];files=set()
for n,review in choices.items():
 r=rs[n];support=[e['candidate_id'] for e in r['evidence'][1:] if e['candidate_id'] in index]
 row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master semantic review: '+review,r['limits']+' Master scope: static full supplied contexts; source/hash checked, no upstream execution or native GUI.',support)
 row['helper_provenance']={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'id':r['id'],'helper_credit_before_master':0}
 rows.append(row);files.update(e['private_file'] for e in r['evidence'])
# Existing pending owner gains a traced real permission consumer. Rewrite master-owned original decision, not helper/coordinator file.
r=rs[6];batch=O/'reviews/batch-058.json';old=json.loads(batch.read_text());new=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master read isOwnedBy: disabled policy true, UUID.equals(null) false; invalid/missing owner denies enabled window permission.',r['limits']+' Traced actual consumer promotes prior pending; same window ownership counted once.',[e['candidate_id'] for e in r['evidence'][1:]])
for i,x in enumerate(old):
 if x['candidate_id']==r['candidate_id']:assert x['status']=='pending';old[i]=new
batch.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
# Save persistent source regeneration override for original manually authored batch.
script=Path('tools/cod4/legacy-migration-acceptance/record_batch058.py')
s=script.read_text();anchor='record(58,'
if 'halley001-ownable-upgrade.json' not in s:
 pos=s.index(anchor);s=s[:pos]+"import json\nfrom review_batch import O\nupgrade=json.loads((O/'halley001-ownable-upgrade.json').read_text())\nrows=[upgrade if x['candidate_id']==upgrade['candidate_id'] else x for x in rows]\n"+s[pos:];script.write_text(s)
(O/'halley001-ownable-upgrade.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
for n,why in {14:'OldUsersConverter ownership reader shares already credited egg/hive identity chain; extra Dread consumer context retained0, not key rename extra.',22:'Exact unlocked Pages owner+Enum methods already credited batch063 lectern/bestiary chain.'}.items():
 r=rs[n];rows.append(dict(candidate_id=r['candidate_id'],status='duplicate',reason=why,supporting_candidates=[e['candidate_id'] for e in r['evidence'][1:] if e['candidate_id'] in index]));files.update(e['private_file'] for e in r['evidence'])
r=rs[28];rows.append(dict(candidate_id=r['candidate_id'],status='pending',reason='Full helper load+setFixedSettings read. Policy repair compares cardinality only; actual no-sort gameplay consumers not supplied/deep read, so no count just category setter.',supporting_candidates=[]));files.update(e['private_file'] for e in r['evidence'])
# Pending must be indexed although not accepted.
for n in [28]:
 e=rs[n]['evidence'][0]
 if e['candidate_id'] not in index:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')}
  with indexfile.open('a') as f:f.write(json.dumps(q,ensure_ascii=False)+'\n')
record(68,rows,files|{e['private_file'] for e in rs[6]['evidence']})
decisions={n:('accepted' if n in choices or n==6 else 'pending' if n==28 else 'merged-existing-zero') for n in rs}
(O/'halley001-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),verified_unique_context_hashes=143,new_accepted=len(choices),promoted_pending=1,decisions=decisions,master_review_notes=choices,existing_rejected_retained={4:'27slot native handler wrapper, no separate custom restoration semantics beyond same parent; actual return support enriches but does not compel count',19:'Native loot/container delegation already master rejected, no distinct migration algorithm/owner-consumer recovery beyond generic container family'},existing_accepted_merged=[7,8,15,18,20,23],new_duplicate=[14,22],pending=[28],extra_scope='Cockatrice/Amphithere progression branches read additionally, not entire unrelated combat tick; helper originals unchanged; no production or GUI.'),ensure_ascii=False,indent=2)+'\n')
