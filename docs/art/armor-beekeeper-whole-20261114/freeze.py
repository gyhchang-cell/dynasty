from pathlib import Path
import json,hashlib,os
D=Path(__file__).resolve().parent;R=D.parents[2];P=D.parent/'armor-hazmat-whole-20261114'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def save(n,d):(D/n).write_bytes(enc(d))
assert not (D/'coordinator-delivery.json').exists()
pointer=R/'docs/art/armor-continuation-20261102/progress.json';old=pointer.read_bytes();state=json.loads(old);assert state['latest_continuation']=='docs/art/armor-hazmat-whole-20261114/progress.json'
prov=json.loads((D/'provenance.json').read_text());assert digest(Path(prov['tree_provenance']))==prov['tree_sha256']
for r in prov['files']:assert digest(D/'source'/r['path'])==r['sha256']
for r in json.loads((D/'reused-consumer-context.json').read_text())['inputs']:assert digest(Path(r['path']))==r['sha256']
before=json.loads((D/'protected-before.json').read_text());after={p:digest(R/p) for p in before};assert after==before;save('protected-after.json',after)
gear=(P/'source/src/main/java/cofh/thermal/core/init/registries/TCoreItems.java').read_text();ids=(P/'source/src/main/java/cofh/thermal/lib/util/ThermalIDs.java').read_text()
for s,t in [('helmet','HELMET'),('chestplate','CHESTPLATE'),('leggings','LEGGINGS'),('boots','BOOTS')]:
 assert f'ID_BEEKEEPER_{t} = "beekeeper_{s}"' in ids
 assert f'registerItem(ID_BEEKEEPER_{t}, () -> new BeekeeperArmorItem(BEEKEEPER, ArmorItem.Type.{t}, itemProperties()))' in gear
clazz=(D/'source/src/main/java/cofh/thermal/core/common/item/BeekeeperArmorItem.java').read_text();assert 'armorSlot == EquipmentSlot.LEGS || armorSlot == EquipmentSlot.FEET ? _default : ArmorFullSuitModel.INSTANCE.get()' in clazz
recipes=[]
for p in sorted((D/'source/src/main/generated/data/thermal/recipes').rglob('beekeeper_*.json')):
 d=json.loads(p.read_text());recipes.append({'path':str(p.relative_to(D)),'key':d.get('key'),'result':d.get('result'),'conditions':d.get('neoforge:conditions')})
save('actual-recipe-observations.json',recipes)
save('actual-review-scope.json',{'new_native_png_viewed':6,'prior_icons_reopened':4,'actual_viewed_pages':['native-icons.png','native-atlases.png','raw-uv-context.png','prior-whole-comparison.png'],'new_full_class_read':'BeekeeperArmorItem.java','context_reuse':'D76 fixed model/material/helpers, no repeated implementation credit','not_claimed':['all downloaded translations read','fabric PNG viewed','exact consumer/game appearance']})
pending=['Main semantic dedup versus D76 and previous protective-suit family; shared model earns no new credit','Exact1.20.4 native consumer/dependency binary and wearing seams/five views unverified','Applicable independent design total/gap null; no artwork before1000 gate']
review={'batch':'D77','key':'thermal:beekeeper','source_commit':prov['commit'],'observations':str(D/'README.md'),'sha256':digest(D/'README.md'),'whole_slots':4,'native_png_viewed':6,'new_validated_credit':0,'pending_whole_family_at_most':1,'gate_met':False,'validated_total':None,'exact_gap':None,'runtime_accepted':False,'pending':pending}
save('semantic-review.json',review)
prior=P/'combined-semantic-ledger.json';ledger=json.loads(prior.read_text());assert 'thermal:beekeeper' not in ledger['reviewed_pending_whole_keys'];ledger['reviewed_pending_whole_keys'].append('thermal:beekeeper')
ledger['pending_whole_families'].append({'primary_whole_key':'thermal:beekeeper','review':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json'),'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':pending})
ledger.update(current_batch_prior={'path':str(prior),'sha256':digest(prior)},current_batch_additional_D54_carry_credit=0,validated_independent_design_total=None,exact_remaining_gap_to_1000=None,gate_met=False);save('combined-semantic-ledger.json',ledger)
save('verification.json',{'batch':'D77','new_native_png_viewed':6,'pages_viewed':4,'slot_assertions':4,'shared_model_not_new_credit':True,'head_face_transparent_pixels':16,'head_face_opaque_pixels':48,'protected289_priority70_unchanged':True,'production_changes':0,'java_starts':0,'checklist_deletions':0,'new_credit':0,'gate_met':False,'runtime_accepted':False})
save('progress.json',{'batch':'D77','status':'BEEKEEPER_WHOLE_SOURCE_PIXEL_STUDY_SAVED_PENDING_SEMANTIC_ACCEPTANCE','prior':'docs/art/armor-hazmat-whole-20261114/progress.json','review':str(D/'semantic-review.json'),'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'production_changes':0,'pending':pending,'next_scope':'Continue genuinely unread relevant whole armor designs; exclude variants/repeated templates; preserve approved artwork.'})
manifest={str(p.relative_to(D)):digest(p) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts};b=enc({'batch':'D77','files':manifest,'new_credit':0,'gate_met':False,'production_changes':0,'runtime_accepted':False});h=hashlib.sha256(b).hexdigest();rp=D/f'bounded-receipt-{h}.json';rp.write_bytes(b)
save('coordinator-delivery.json',{'batch':'D77','receipt':{'path':str(rp),'sha256':h},'review':{'path':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json')},'verification':{'path':str(D/'verification.json'),'sha256':digest(D/'verification.json')},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
assert pointer.read_bytes()==old,'Concurrent specialist pointer update'
state.update(status='D77_BEEKEEPER_WHOLE_REFERENCE_STUDIED_PENDING_ACCEPTANCE',latest_continuation=str((D/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((D/'combined-semantic-ledger.json').relative_to(R)),latest_beekeeper_delivery={'path':str(D/'coordinator-delivery.json'),'sha256':digest(D/'coordinator-delivery.json')},latest_reference_gate_met=False)
tmp=pointer.with_name('progress.D77.tmp');tmp.write_bytes(enc(state));os.replace(tmp,pointer)
assert all(digest(D/p)==v for p,v in manifest.items())
print(json.dumps({'frozen_files':len(manifest),'receipt_sha256':h,'delivery_sha256':digest(D/'coordinator-delivery.json'),'protected_unchanged':True}))
