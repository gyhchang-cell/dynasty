"""Verify D18 frozen inputs, exact references, dedup and unchanged protected resources."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,zipfile
from PIL import Image
D=Path(__file__).resolve().parent; R=D.parents[2]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ctx=read(D/'collection-context.json')
 for k in ['collector','prior_ledger','icon_chart_collector']: assert sha(R/ctx[k])==ctx[k+'_sha256'],k
 prior=read(R/ctx['prior_ledger']); assert (len(prior['groups']),len(prior['case_to_group']),len(prior['reviewed_case_keys']))==(203,518,532)
 for row in prior['source_reviews']: assert sha(R/row['path'])==row['sha256']
 assert sha(D/'candidate-archive-scan.json')==ctx['candidate_scan_sha256']
 baseline=read(D/'source-baseline.json'); assert len(baseline)==289
 changes=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 receipt=read(next(D.glob('texture-requirements-receipt-*.json'))); assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 p=read(D/'provenance.json'); decls=read(D/'resource-declarations.json'); review=read(D/'semantic-review.json')
 cases={c['case_key'] for c in p['cases']}; icons=[a for c in p['cases'] for a in c['icons']]; worn=p['worn_textures']
 assert len(cases)==12 and len(icons)==len(decls)==48 and len(worn)==25 and not read(D/'animation-candidates.json')
 assert cases==set(ctx['selected_case_keys']) and not cases&set(prior['reviewed_case_keys'])
 assert len(review['pages_opened'])==9 and all((D/f).is_file() for f in review['pages_opened'])
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
  for a in p['archives']: assert sha(Path(a['path']))==a['sha256']
  for a in icons+worn+[x['model'] for x in decls]:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   if 'size' in a:
    with Image.open(D/a['local']) as im: assert list(im.size)==a['size']
  for a in icons: assert a['entry']+'.mcmeta' not in jars[a['jar']].namelist()
  for a in decls:
   m=read(D/a['model']['local']); assert m['parent']==a['parent'] and m['textures']['layer0']==a['texture_location']
   ns,t=a['texture_location'].split(':'); assert a['texture']['entry']==f'assets/{ns}/textures/{t}.png'
   assert a['texture'] in next(c['icons'] for c in p['cases'] if c['case_key']==a['case_key'])
  for c in cases: assert {a['part'] for a in decls if a['case_key']==c}=={'helmet','chestplate','leggings','boots'}
 facts=[]
 for a in worn:
  im=Image.open(D/a['local']).convert('RGBA'); alpha=im.getchannel('A'); hist=alpha.histogram(); x={'source':a,'alpha_nonzero':sum(hist[1:]),'alpha_ge_128':sum(hist[128:]),'alpha_extrema':list(alpha.getextrema()),'bbox':im.getbbox(),'standard_uv_assumed':False,'binding_proven':False}; assert not a['binding_proven']
  # Exact named standard-size rectangles: source layout probes only, not semantic/model proof.
  if im.size==(64,32) and ('layer_1.png' in a['entry'] or 'layer_2.png' in a['entry']):
   def count(rect): return sum(alpha.crop(rect).histogram()[1:])
   x['raw_rectangles_only']={'wristcap_48_16_52_20':count((48,16,52,20)),'side_last_rows_x40_44_48_52_y31':[count((xx,31,xx+4,32)) for xx in [40,44,48,52]],'body_strip_x16_40_y20_32':[count((16,y,40,y+1)) for y in range(20,32)]}
  facts.append(x)
 save('native-layer-facts.json',{'layers':facts,'raw_named_64x32_rectangles_probed':sum('raw_rectangles_only' in x for x in facts),'worn_binding_proven':False,'pixels_modified':False,'design_credit_from_layers':0,'warning':'矩形仅记录源图坐标，未证玩家实际选中或标准身体UV适用，不能直接复制至Dynasty。'})
 flat=[c for row in review['observations'] for c in row['cases']]; assert len(flat)==len(set(flat))==12 and set(flat)==cases and not review['excluded_cases']
 groups={g['semantic_group']:g for g in prior['groups']}; new=append=0
 for row in review['observations']:
  k=row['semantic_group']
  if row['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP':
   assert k not in groups; groups[k]={'semantic_group':k,'cases':[],'observations':[]}; new+=1
  else: assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups; append+=1
  groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases'])); groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
 owners={}
 for k,g in groups.items():
  for c in g['cases']: assert c not in owners; owners[c]=k
 reviewed=sorted(set(owners)|{e['case_key'] for e in prior['excluded_cases']}); assert (new,append,len(groups),len(owners),len(reviewed))==(2,6,205,530,544)
 save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':544,'armor_name_families':530,'conservative_learning_groups':205})
 save('reference-gate-accounting.json',{'required_valid_related_independent_designs':1000,'reviewed_name_families':544,'armor_name_families_after_exclusion':530,'excluded_from_full_armor_gate':14,'conservative_learning_groups_in_current_subset':205,'validated_independent_design_total':None,'maximum_credit_under_current_one_per_group_policy':205,'unfilled_minimum_under_current_policy':795,'reference_gate_met':False,'gap_limit':'205学习组含局部、变体和反例，不等于203个已验完整独立设计；795仅为所有组合格时最低缺口。'})
 assert all(review[k]==0 for k in ['new_artwork','production_changes','game_starts']) and not review['gate_met']
 result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changes,'changed_paths':changes,'archive_sources':len(p['archives']),'new_complete_name_families_viewed':12,'native_icon_entries_viewed':48,'distinct_icon_payloads':len({a['sha256'] for a in icons}),'model_json_declarations_checked':48,'native_layer_candidate_entries_viewed':25,'distinct_layer_payloads':len({a['sha256'] for a in worn}),'raw_named_64x32_rectangles_probed':sum('raw_rectangles_only' in x for x in facts),'worn_item_binding_proven':False,'animation_metadata_present':0,'new_learning_groups':2,'append_observations':6,'combined_learning_groups':205,'combined_reviewed_names':544,'validated_independent_design_total':None,'reference_gate_met':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_scripts':{f:sha(D/f) for f in ['collect.py','record_review.py','verify.py']}}
 save('verification.json',result); print(json.dumps(result,ensure_ascii=False)); assert not changes
if __name__=='__main__': main()
