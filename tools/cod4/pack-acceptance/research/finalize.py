"""Conservative final site counting; never count candidate lists or string keys."""
from study import *
MANUAL_EXCLUDE={338:'placement/server warning, not display cache',665:'autobuild gameplay notification',1611:'map creation gameplay path',2265:'server cheat-permission notification',913:'texture generation command',90:'static creative tab registration',91:'static creative tab registration',104:'static P2P label registration',748:'static representative recipe item label',749:'static representative recipe item label',750:'static representative recipe item label',1756:'gameplay recipe setter/player message',478:'gameplay useOn message',2174:'server command output'}
def main():
 rows=json.loads((OUT/'analyzed.json').read_text());old={r['candidate'] for r in json.loads((OUT/'review-queue.json').read_text())};seen=set();valid=[];excluded=[]
 for r in rows:
  reason=MANUAL_EXCLUDE.get(r['candidate']);stem=Path(r['path']).stem
  if stem in ['DoubleListEntry','DoubleListListEntry','FloatListEntry','FloatListListEntry','LongListEntry','LongListListEntry','IntegerListListEntry']:reason='numeric type/container variant of same bound-validation text pattern; retain IntegerListEntry only'
  if 'Command' in stem:reason='command pathway, outside chosen live display scope'
  symbol=(r['repo'],stem,r['method'])
  if symbol in seen:reason='same logical class/method across platform copies or overloads; conservatively count once'
  if reason:excluded.append({'candidate':r['candidate'],'reason':reason});continue
  seen.add(symbol);valid.append(r)
 groups=collections.defaultdict(list)
 for r in valid:groups[r['repo']].append(r)
 selected=[]
 while groups and len(selected)<1000:
  for repo in list(groups):
   if len(selected)==1000:break
   selected.append(groups[repo].pop(0))
   if not groups[repo]:del groups[repo]
 for i,r in enumerate(selected,1):r['reference_id']=f'L10N-{i:04d}'
 (OUT/'final-review.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2));(OUT/'manual-exclusions.json').write_text(json.dumps(excluded,indent=2))
 print('Eligible after conservative review',len(valid),'selected',len(selected),'additional review entries:')
 for r in selected:
  if r['candidate'] not in old:print(r['candidate'],Path(r['path']).stem+'.'+r['method'],r['text_calls'][0]['expression'][:110])
 if '--accept' not in sys.argv:return
 assert len(selected)==1000 and len({r['dedup_sha256'] for r in selected})==1000
 for r in selected:assert hashlib.sha256((ROOT/r['source_cache']).read_bytes()).hexdigest()==r['file_sha256'] and r['text_calls'] and r['body']
 payload=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in selected);(OUT/'references-1000.jsonl').write_text(payload)
 summary={'status':'COMPLETE_AST_ASSISTED_STUDY_WITH_SOURCE_REVIEW','valid_implementation_sites':len(selected),'independent_projects':len(set(r['repo'] for r in selected)),'same_defect_fixes_claimed':0,'runtime_executions_claimed':0,'method':'Pinned full-method source + AST localization calls/guards/arguments/text-consumer analysis at every counted site, compact source-context review across the ledger, selected deep lifecycle traces. Not 1000 manually executed mods or 1000 independent algorithms.','excluded_from_count':['translation JSON entries','geometry transforms named translate','datagen/test/model sources','static-only titles and key-only accessors','same code with only literal-key changes','numeric-type copy variants','same logical class/method platform copies and overloads','command-only/gameplay notifications','prior quest1000/bow1000','native JEI seven-site diagnosis chain (retained separately, not added twice)'],'by_project':dict(collections.Counter(r['repo'] for r in selected)),'by_timing':dict(collections.Counter(r['evaluation_timing'] for r in selected)),'eager_i18n_sites':sum(r['eager_i18n'] for r in selected),'getString_sites':sum(r['has_getString'] for r in selected),'line_layout_sites':sum(r['has_line_layout'] for r in selected),'ledger_sha256':hashlib.sha256(payload.encode()).hexdigest(),'unselected_analyzed_sites':len(valid)-len(selected),'repair_gate':'1000 related implementation sites met; user already authorized minimal WorkshopJei repair. No additional coordinator approval.'}
 (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
