from pathlib import Path
import json,hashlib,os
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def save(n,d):(D/n).write_bytes(encoded(d))
def digest(p):return sha(p.read_bytes())
assert not (D/'coordinator-delivery.json').exists()
pointer=R/'docs/art/armor-continuation-20261102/progress.json';old=pointer.read_bytes();state=json.loads(old)
assert state['latest_continuation']=='docs/art/armor-current-bindings-20261113/progress.json'
prov=json.loads((D/'provenance.json').read_text());assert digest(Path(prov['archive']))==prov['archive_sha256']
for row in prov['entries']:assert digest(D/row['path'])==row['sha256']
baseline=json.loads((D/'protected-before.json').read_text());end={p:digest(R/p) for p in baseline};assert baseline==end
save('protected-after.json',end)
ack=R/'docs/cod4/audit-20261022/coordinator-armor-D73-head-face-and-original-pixels-static-review-20261113.json'
assert digest(ack)=='8366f53fafcf9fbb89cec2dc6940b4b941434fe3160695ba2b09b9cd0ea0dcac'
save('D73-main-ACK-source.json',{'path':str(ack),'sha256':digest(ack),'scope':'Neutral head face and16 originals limited static review; no worn/live approval or artwork gate waiver'})
java=D/'source/src/main/java/com/teammetallurgy/atum'
gear=(java/'init/AtumItems.java').read_text();color=(java/'client/ClientHandler.java').read_text()
for material,mod in [('iron',10),('gold',20),('diamond',15)]:
 for s,typ in [('helmet','HELMET'),('chest','CHESTPLATE'),('legs','LEGGINGS'),('boots','BOOTS')]:
  assert f'new WandererDyeableArmor(ArmorMaterials.{material.upper()}, "desert_{material}_armor", ArmorItem.Type.{typ}).setDamageModifier({mod}), "desert_{s}_{material}"' in gear
  assert f'AtumItems.DESERT_{s.upper()}_{material.upper()}.get()' in color
assert 'tintIndex > 0 ? -1' in color
assert '14869989' in (java/'items/WandererDyeableArmor.java').read_text()
assert 'slot == EquipmentSlot.LEGS ? 2 : 1' in (java/'items/TexturedArmorItem.java').read_text()
source_reads=[{'path':'source/src/main/java/com/teammetallurgy/atum/items/TexturedArmorItem.java','scope':'full file'},
 {'path':'source/src/main/java/com/teammetallurgy/atum/items/WandererDyeableArmor.java','scope':'full file'},
 {'path':'source/src/main/java/com/teammetallurgy/atum/init/AtumItems.java','scope':'lines177-188 and registration helper267-272'},
 {'path':'source/src/main/java/com/teammetallurgy/atum/Atum.java','scope':'constructor/common/client setup lines58-88 and deferred registration105-113'},
 {'path':'source/src/main/java/com/teammetallurgy/atum/client/ClientHandler.java','scope':'client init/colors including108-109'},
 {'path':'source/gradle.properties','scope':'full file'},
 {'path':'source/build.gradle','scope':'opening plugins/toolchain/runs; not whole file'}]
save('source-read-scope.json',source_reads)
native=[]
for row in prov['entries']:
 p=D/row['path']
 if p.suffix=='.png':
  im=Image.open(p).convert('RGBA');native.append({'path':row['path'],'size':im.size,'rgba_sha256':sha(im.tobytes()),'alpha_bbox':im.getchannel('A').getbbox()})
save('native-png-index-final.json',native)
viewed=[row['path'] for row in prov['entries'] if row['path'].endswith('.png') and ('desert_' in row['path'] or any(row['path'].endswith(f'/wanderer_{s}.png') for s in ['helmet','chest','legs','boots']))]
assert len(viewed)==40
pages=['native-icon-layers.png','native-worn-layers.png','icon-tint-diagnostic.png','prior-native-icons.png','raw-head.png','raw-hat.png','raw-body.png','raw-arm.png','raw-leg.png']
save('actual-visual-review.json',{'native_png_viewed':viewed,'viewed_pages':pages,'not_viewed_this_batch':[x['path'] for x in native if x['path'] not in viewed],
 'limits':['Raw standard context rectangles are not exact source-version geometry.','Tint math and all pages are software diagnostics, not game appearance.','Four raw rectangles for an item are not four independent references.']})
pending=['Main independent whole-family semantic dedup against D59 Wanderer and other previously studied armor','Exact MC1.20.4 NeoForge20.4.232 wearing consumer/model and runtime are not closed','Full validated total and exact gap remain null; gate false; no production artwork']
review={'batch':'D74','key':'atum:desert_material_family','source':{'repository':prov['repository'],'commit':prov['commit'],'archive_sha256':prov['archive_sha256']},
 'observations':'README.md','observations_sha256':digest(D/'README.md'),'slots_per_material':4,'material_variants':3,'native_target_png_viewed':36,'prior_actual_icons_viewed':4,'raw_uv_measurements':360,
 'new_validated_independent_credit':0,'pending_complete_source_family_at_most':1,'same_template_materials_not_counted_separately':True,
 'global_applicable_total':None,'exact_gap':None,'gate_met':False,'runtime_accepted':False,'pending':pending}
save('semantic-review.json',review)
prior=R/'docs/art/armor-current-bindings-20261113/combined-semantic-ledger.json';ledger=json.loads(prior.read_text())
assert review['key'] not in ledger['reviewed_pending_whole_keys']
ledger['reviewed_pending_whole_keys'].append(review['key'])
ledger['pending_whole_families'].append({'primary_whole_key':review['key'],'review':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json'),'whole_slots':4,'material_variants':3,'new_validated_credit':0,'new_learning_groups':0,'pending':pending})
ledger.update(current_batch_prior={'path':str(prior),'sha256':digest(prior)},current_batch_additional_D54_carry_credit=0,validated_independent_design_total=None,exact_remaining_gap_to_1000=None,gate_met=False)
save('combined-semantic-ledger.json',ledger)
save('verification.json',{'batch':'D74','source_entries':len(prov['entries']),'native_png_extracted':len(native),'actual_native_png_viewed':40,'actual_target_png_viewed':36,'reviewed_pages':len(pages),'registry_to_type_assertions':12,'item_models':12,
 'raw_uv_rectangles':360,'exact_source_version_geometry_closed':False,'protected289_and_priority70_unchanged':True,'production_changes':0,'java_starts':0,'runtime_acceptance':False,'checklist_deletions':0,'new_validated_credit':0,'gate_met':False})
save('progress.json',{'batch':'D74','status':'DESERT_WHOLE_FAMILY_SOURCE_AND_PIXEL_STUDY_SAVED_PENDING_SEMANTIC_ACCEPTANCE','prior':'docs/art/armor-current-bindings-20261113/progress.json','review':str(D/'semantic-review.json'),'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'production_changes':0,'pending':pending,'next_scope':'Study genuinely unread relevant whole armor families, not more Desert/Wanderer material colors; retain protected originals.'})
manifest={str(p.relative_to(D)):digest(p) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
b=encoded({'batch':'D74','files':manifest,'production_changes':0,'new_credit':0,'gate_met':False,'runtime_accepted':False});h=sha(b);rp=D/f'bounded-receipt-{h}.json';rp.write_bytes(b)
delivery={'batch':'D74','receipt':{'path':str(rp),'sha256':h},'review':{'path':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json')},'verification':{'path':str(D/'verification.json'),'sha256':digest(D/'verification.json')},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending}
save('coordinator-delivery.json',delivery)
assert pointer.read_bytes()==old,'Concurrent specialist pointer change'
state.update(status='D74_DESERT_WHOLE_FAMILY_STUDIED_SEMANTIC_REVIEW_PENDING',latest_continuation=str((D/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((D/'combined-semantic-ledger.json').relative_to(R)),latest_desert_delivery={'path':str(D/'coordinator-delivery.json'),'sha256':digest(D/'coordinator-delivery.json')},latest_reference_gate_met=False)
tmp=pointer.with_name('progress.D74.tmp');tmp.write_bytes(encoded(state));os.replace(tmp,pointer)
assert all(digest(D/p)==h for p,h in manifest.items())
print(json.dumps({'frozen_files':len(manifest),'receipt_sha256':sha(b),'delivery_sha256':digest(D/'coordinator-delivery.json'),'protected_unchanged':True}))
