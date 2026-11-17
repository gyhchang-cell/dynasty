from pathlib import Path
import json,hashlib,subprocess,sys,os
D=Path(__file__).resolve().parent;R=D.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
def enc(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def save(p,d):p.write_bytes(enc(d))
def digest(p):return sha(p.read_bytes())
assert not (D/'coordinator-delivery.json').exists()
pointer=R/'docs/art/armor-continuation-20261102/progress.json';old=pointer.read_bytes();state=json.loads(old);assert state['latest_continuation']=='docs/art/armor-desert-whole-20261113/progress.json'
base=json.loads((D/'protected-before.json').read_text());after={p:digest(R/p) for p in base};assert after==base
for pf,folder in [('provenance.json','source'),('dependency-provenance.json','dependency')]:
 p=json.loads((D/pf).read_text())
 for row in p['files']:assert digest(D/folder/row['path'])==row['sha256']
# D75 is a stopped duplicate screening, not a fresh complete-design study.
S=R/'docs/art/armor-faraday-whole-20261114'
subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(S),'--targets',*[f'immersiveengineering:armor_faraday_{s}' for s in ['helmet','chestplate','leggings','boots']],
 '--application','D75仅筛查：当前官方提交与旧engineering-reference-20261111相同，已完整看过；停止重复、不计新参考、不绘图、不修改运行资产。'],check=True)
prior=R/'docs/art/armor-engineering-reference-20261111/provenance.json';pv=json.loads(prior.read_text());cur=json.loads((S/'provenance.json').read_text());assert pv['commit']==cur['commit']
for row in cur['files']:assert digest(S/'source'/row['path'])==row['sha256']
(S/'README.md').write_text('# D75：重复候选筛查，未继续整套研究\n\n法拉第官方固定提交与 docs/art/armor-engineering-reference-20261111 已读整套来源相同。发现重复后停止，不把新下载、26文件或重读构造器计新设计；本批未实图观察，不加新参考信用，不改生产美术。后续实际研究为D76 Thermal防化服。\n')
save(S/'screening-result.json',{'batch':'D75','status':'EXCLUDED_ALREADY_WHOLE_VIEWED_SAME_COMMIT','prior_source':str(prior),'prior_sha256':digest(prior),'commit':cur['commit'],'new_credit':0,'new_visual_review':False,'production_changes':0})
sm={str(p.relative_to(S)):digest(p) for p in sorted(S.rglob('*')) if p.is_file() and '__pycache__' not in p.parts};b=enc({'batch':'D75','files':sm,'new_credit':0,'screening_only':True});h=sha(b);sr=S/f'bounded-receipt-{h}.json';sr.write_bytes(b)
save(D/'D75-screening-receipt.json',{'path':str(sr),'sha256':h})
# Correct the metadata-stage yellow assumption using the actual reviewed red-orange pixels.
dedup=json.loads((D/'dedup-input.json').read_text());dedup['metadata_hypothesis_corrected']='Initial yellow-hazmat category assumption rejected by actual red-orange native source images.';dedup['relation']='Closed protective suit relative to previous yellow and dark-green hazard suits; color alone is not independent design credit.';save(D/'dedup-input.json',dedup)
save(D/'protected-after.json',after)
source=D/'source/src/main/java/cofh/thermal/core';dep=D/'dependency/src/main/java/cofh'
gear=(source/'init/registries/TCoreItems.java').read_text();ids=(D/'source/src/main/java/cofh/thermal/lib/util/ThermalIDs.java').read_text()
for s,typ in [('helmet','HELMET'),('chestplate','CHESTPLATE'),('leggings','LEGGINGS'),('boots','BOOTS')]:
 assert f'ID_HAZMAT_{typ} = "hazmat_{s}"' in ids
 assert f'registerItem(ID_HAZMAT_{typ}, () -> new HazmatArmorItem(HAZMAT, ArmorItem.Type.{typ}, itemProperties()))' in gear
model=(dep/'core/client/renderer/entity/model/ArmorFullSuitModel.java').read_text();haz=(source/'common/item/HazmatArmorItem.java').read_text()
assert 'armorSlot == EquipmentSlot.LEGS || armorSlot == EquipmentSlot.FEET ? _default : ArmorFullSuitModel.INSTANCE.get()' in haz
assert 'scale.extend(0.5F)' in model and 'scale.extend(-0.5F)' in model
assert 'event.registerLayerDefinition(ARMOR_FULL_SUIT_LAYER, ArmorFullSuitModel::createBodyLayer)' in (dep/'core/CoFHCore.java').read_text()
recipes=[]
for p in sorted((D/'source/src/main/generated/data/thermal/recipes').rglob('hazmat_*.json')):
 d=json.loads(p.read_text());recipes.append({'path':str(p.relative_to(D)),'result':d.get('result'),'key':d.get('key'),'conditions':d.get('neoforge:conditions')})
save(D/'recipe-source-observations.json',recipes)
save(D/'source-read-scope.json',{'full_files':['HazmatArmorItem.java','ArmorItemCoFH.java','ArmorMaterialCoFH.java','ArmorFullSuitModel.java','gradle.properties of both repositories'],
 'selected_ranges':['TCoreItems register/registerArmor/HAZMAT declaration','ThermalIDs260-263','RegistrationHelper113-119','ThermalCore registration121-140','CoFHCore event listener and layer registration','4 actual model JSON and5 recipe JSON, English native guide'],
 'not_claimed':['Full huge registry/event source reading','Exact published dependency binary identity','All downloaded language guides or fabric PNG visually viewed']})
pending=['Main whole-design semantic dedup versus existing protective-suit group and applicability to old Dynasty cloth/leather','Exact1.20.4 native geometry/consumer and resolved dependency binary identity remain unverified','Five-view wearing seams, gameplay acquisition and real game appearance not tested','Applicable validated whole-design total/gap remain null; gate false']
review={'batch':'D76','key':'thermal:hazmat','source':json.loads((D/'provenance.json').read_text())['commit'],'dependency':json.loads((D/'dependency-provenance.json').read_text())['commit'],
 'observations':str(D/'README.md'),'sha256':digest(D/'README.md'),'whole_slots':4,'actual_native_png_viewed':6,'analysis_pages_viewed':3,'raw_context_rectangles':60,
 'new_validated_credit':0,'pending_whole_family_at_most':1,'validated_total':None,'exact_gap':None,'gate_met':False,'runtime_accepted':False,'pending':pending}
save(D/'semantic-review.json',review)
prior=R/'docs/art/armor-desert-whole-20261113/combined-semantic-ledger.json';ledger=json.loads(prior.read_text());assert 'thermal:hazmat' not in ledger['reviewed_pending_whole_keys']
ledger['reviewed_pending_whole_keys'].append('thermal:hazmat');ledger['pending_whole_families'].append({'primary_whole_key':'thermal:hazmat','review':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json'),'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':pending})
ledger.update(current_batch_prior={'path':str(prior),'sha256':digest(prior)},current_batch_additional_D54_carry_credit=0,validated_independent_design_total=None,exact_remaining_gap_to_1000=None,gate_met=False)
save(D/'combined-semantic-ledger.json',ledger)
save(D/'verification.json',{'batch':'D76','protected289_priority70_unchanged':after==base,'native_png_actually_viewed':6,'pages_actually_viewed':3,'slot_assertions':4,'custom_head_chest_model_read':True,'exact_runtime_closed':False,'production_changes':0,'java_starts':0,'checklist_deletions':0,'new_credit':0,'gate_met':False})
save(D/'progress.json',{'batch':'D76','status':'NATIVE_HAZMAT_WHOLE_DESIGN_AND_CUSTOM_UV_SOURCE_STUDIED_PENDING_INDEPENDENT_ACCEPTANCE','prior':'docs/art/armor-desert-whole-20261113/progress.json','screened_repeat':'D75','review':str(D/'semantic-review.json'),'production_changes':0,'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'pending':pending,'next_scope':'Continue genuinely unread related complete armor designs; avoid Faraday/Desert repeats and material variants; protect all approved original artwork.'})
manifest={str(p.relative_to(D)):digest(p) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts};b=enc({'batch':'D76','files':manifest,'new_credit':0,'gate_met':False,'production_changes':0,'runtime_accepted':False});h=sha(b);rp=D/f'bounded-receipt-{h}.json';rp.write_bytes(b)
save(D/'coordinator-delivery.json',{'batch':'D76','receipt':{'path':str(rp),'sha256':h},'review':{'path':str(D/'semantic-review.json'),'sha256':digest(D/'semantic-review.json')},'verification':{'path':str(D/'verification.json'),'sha256':digest(D/'verification.json')},'screened_duplicate_D75':{'path':str(sr),'sha256':digest(sr)},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
assert pointer.read_bytes()==old,'Concurrent specialist pointer update'
state.update(status='D76_HAZMAT_WHOLE_REFERENCE_STUDIED_PENDING_ACCEPTANCE',latest_continuation=str((D/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((D/'combined-semantic-ledger.json').relative_to(R)),latest_hazmat_delivery={'path':str(D/'coordinator-delivery.json'),'sha256':digest(D/'coordinator-delivery.json')},latest_reference_gate_met=False)
tmp=pointer.with_name('progress.D76.tmp');tmp.write_bytes(enc(state));os.replace(tmp,pointer)
assert all(digest(D/p)==v for p,v in manifest.items());assert all(digest(S/p)==v for p,v in sm.items())
print(json.dumps({'D75_screened_repeat':digest(sr),'D76_frozen_files':len(manifest),'D76_receipt_sha256':h,'D76_delivery_sha256':digest(D/'coordinator-delivery.json'),'project_artwork_unchanged':True}))
