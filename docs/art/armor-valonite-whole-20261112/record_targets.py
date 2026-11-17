"""Read-only qualification: historical work is not an unmodified/crude asset."""
from pathlib import Path
from PIL import Image
import hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[2]
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text());base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
notes={
'bamboo':('千像素竹片/绑带原稿，已有制作证据，保护图标。','L1/L2竹条绑带与头顶旧静态风险尚待当前消费者/穿戴核验。',['armor-wildwood-whole-20261112']),
'brocade':('千像素紫织物、金边交领/腰饰原稿，不改成普通材料甲。','旧材质优先与头顶静态风险仍待验。',['armor-material-three-20261112','armor-ra-atem-whole-20261112']),
'cloth':('32px灰布、斜系带、褶线裤和绑腿，历史稿保留；朴素不等于简陋。','旧肩块、窄高靴比例意见及头顶静态风险，未实机验收。',['armor-material-three-20261112','armor-mummy-whole-20261112']),
'leather':('32px棕皮、肩带和腰带明确，不因低阶简单重画。','旧长靴/小脚掌意见与头顶风险待核，图标不代表穿戴通过。',['armor-inventor-whole-20261112']),
'sea_silk':('32px浅蓝交领与裙片已有改稿，不换成蓝金属甲。','旧肩突出/长靴比例意见与头顶风险待验，仅限有依据微调候选。',['armor-material-three-20261112','armor-ra-atem-whole-20261112']),
'hongmeng':('千像素白金主甲、紫内衬、冠和胸V形原稿，保留认可设计。','材料分区疑点属于穿戴待验，不授权改原稿或加大冠肩。',['armor-ra-atem-whole-20261112','armor-arcane-fortress-whole-20261112']),
'cinnabar':('千像素朱红/米白符片、交领与直腿原稿，不换紫色晶体身份。','旧穿戴材质分区待验；Valonite只借亮面比例/袖口透明分工，不借其颜色。',['armor-arcane-fortress-whole-20261112','armor-valonite-whole-20261112'])}
rows=[]
for t in targets['targets']:
 fam=t['family'];icon,uv,refs=notes[fam];assets=[]
 for rel,expected in t['files'].items():
  p=R/rel;assert h(p)==expected
  im=Image.open(p) if p.suffix=='.png' else None
  assets.append({'path':str(p),'sha256':h(p),'original_dimensions':im.size if im else None,'scope':'worn_atlas' if '/textures/models/' in rel else 'inventory_icon' if im else 'inventory_model'})
 refs2=[]
 for ref in refs:
  folder=R/'docs/art'/ref;p=next((folder/n for n in ['semantic-review.json','progress.json','README.md','geometry-uv-context.json'] if (folder/n).exists()),None);assert p
  refs2.append({'path':str(p),'sha256':h(p),'status':'D54 whole-family acceptance retained; scope-specific reuse required' if 'wildwood' in ref else 'saved study; independent applicability/dedup pending, zero new credit','use_limit':'Panel/cloth/edge/UV method only. No palette copying, art release, file/component counting. Material-three progress covers Wanderer and related consumers; not accepted as a new design here.'})
 rows.append({'family':fam,'native_ids':t['native_ids'],'icon_state':'HISTORICALLY_REWORKED_PRESERVE','icon_observation':icon,'worn_state':'STATIC_FINDING_PENDING_WORN_ACCEPTANCE','worn_observation':uv,'confirmed_unmodified_crude':False,'redraw_eligible_now':False,'static_cap_risk':t['static_cap_risk'],'material_priority':t['material_priority'],'assets':assets,'reusable_reference_state':refs2})
for rel,expected in base.items():assert h(R/rel)==expected
inventory=sorted({Path(rel).stem.rsplit('_',1)[0] for rel in base if '/models/item/' in rel and Path(rel).stem.endswith(('_helmet','_chestplate','_leggings','_boots'))})
history=R/'docs/art/armor-continuation-20261102/visual-review.json'
out={'batch':'D72','scope':'289 protected files /70 priority files, actual seven-family 28-ID qualification','protected_baseline':str(R/'docs/art/armor-ars-reference-20261111/source-baseline.json'),'protected_baseline_sha256':h(R/'docs/art/armor-ars-reference-20261111/source-baseline.json'),'protected_files_unchanged':len(base),'protected_armor_families':inventory,'other_protected_family_state':'Retain protection. This seven-family page is not a new visual judgment of all protected files.','priority_files_unchanged':sum(len(x['assets']) for x in rows),'priority_IDs':28,'confirmed_old_crude_redraw_IDs':[],'qualification':'No ID in this protected priority scope currently substantiated as both unmodified/old and crude. Static risk or simple low-tier design does not prove redraw eligibility.','history':{'path':str(history),'sha256':h(history)},'actual_page_viewed':'current-target-readonly.png','thumbnail_scope':'Diagnostic sheet only: large original PNGs reduced with nearest sampling. Source/runtime byte-identical; no16px production conversion or quantization.','targets':rows,'production_changes':0,'gate_met':False}
(B/'current-target-status.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Saved seven families /28 exact IDs /70 hashes; no invented redraw qualification.')
