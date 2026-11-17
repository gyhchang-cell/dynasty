import json,hashlib
from pathlib import Path
from zipfile import ZipFile
R=Path('/Users/a15356015027/Desktop/dynasty');ROOT=R/'docs/architecture';meta=ROOT/'research-20261101-dungeons-026/all-structure-metadata.json';inventory=Path(json.loads(meta.read_text())['fixed_archive_inventory']['path'])
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(p,n,d):(p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
allrows=[];archive_checks={};previous=ROOT/'research-20261104-smithy-283'
for batch,begin,end in [(284,0,60),(285,60,180),(286,180,413)]:
 p=ROOT/f'research-20261104-smithy-{batch}';assert not(p/'RECEIPT.json').exists();d=json.loads((p/'bounded-anonymous-functional-screen.json').read_text());rows=d['rows'];allrows.extend(rows)
 (p/'screen_anonymous.py').write_text(Path(f'/tmp/dynasty-research{batch}-screen.py').read_text())
 d['selection']='fixed metadata order positions '+str(begin)+'..'+str(end-1)+'; not present in selected historical archive/member index, /houses, nonzombie, exclude specified occupational names, horizontal>=5, volume<=4500; not global semantic exhaustion'
 d['history_caveat']='Absence in this selected record index does not prove source was never bounded before; no new semantic/full-whole credit claimed.'
 put(p,'bounded-anonymous-functional-screen.json',d)
 checks={}
 for row in rows:
  jar=row['source']['source_archive']
  if jar not in archive_checks:archive_checks[jar]=bind(jar)['sha256']
  assert archive_checks[jar]==row['archive_sha256']
  with ZipFile(jar)as z:assert hashlib.sha256(z.read(row['source']['member'])).hexdigest()==row['source']['nbt_sha256']
 checks['source_archive_and_member_SHA_exact']=True;checks['slice_count_exact']=len(rows)==end-begin;checks['machine_signature_candidates0']=d['potential_count']==0 and not any(row['potential_smith_devices_not_qualification']for row in rows)
 put(p,'scope-and-reading.json',{'batch':batch,'status':'BOUNDED_DEVICE_PREFILTER_ONLY_ZERO','metadata_binding':bind(meta),'fixed_inventory_binding':bind(inventory),'source_range':[begin,end],'rows':len(rows),'actual_semantic_whole_studies':0,'actual_PNG_viewed':0,'palette_BE_entities_full_manual_read':False,'devices_rule':'anvil substring OR blast_furnace OR smithing_table OR vanilla grindstone; only prefilter, not sole architectural-purpose test','scope_limits':['No newly eligible device-signature candidates in this slice, not proof all worlds/buildings lack forges.','Ordinary furnace, cauldron, brewing or generic crafting block does not establish a smithy; no purpose upgraded.','Does not examine roofs/paths/all layers or whole relatedness, and does not count sources/components/hash matches as buildings.','Selected historical index may miss earlier bounded material-only captures; repeats of bounded signatures get no credit.','Metadata size cap and name exclusions omit larger buildings, combination structures and custom mechanisms; no all-local exhaustion claim.'],'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0})
 protected=[]
 oldrows=json.loads((previous/'protected-inputs-current.json').read_text())['files']
 for row in oldrows:
  old=row[f'current{batch-1}'];now=bind(old['path']);protected.append({f'previous{batch-1}':old,f'current{batch}':now,'unchanged':old==now,'this_chat_wrote_file':False})
 put(p,'protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0});checks['protected8_unchanged']=all(v['unchanged']for v in protected);checks['previous_receipt_files_unchanged']=all(bind(v['path'])==v for v in json.loads((previous/'RECEIPT.json').read_text())['files']);checks['no_session_or_png_written']=not(p/'session.json').exists()and not list(p.glob('*.png'))
 assert all(checks.values()),checks
 put(p,'active-checkpoint.json',{'batch':batch,'status':'BOUNDED_DEVICE_PREFILTER_ONLY_ZERO','previous_receipt':bind(previous/'RECEIPT.json'),'scope':bind(p/'scope-and-reading.json'),'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'273_275_pending':True,'tasks_deleted':0,'all_tasks_complete':False,'next':'继续选择固定本地其他直接适用完整建筑；这仅是设备预筛，不推整体1000研究完成，不重计旧221宿主。'})
 put(p,'verification.json',{'checks':checks,'all_passed':True,'qualification':'fixed archive/member reproducibility only; not independent architecture/game acceptance'})
 # Save exact sealing code as audit aid, not a command to rerun sealed batches.
 (p/'seal_functional.py').write_text(Path('/tmp/dynasty-seal-functional284-286.py').read_text())
 put(p,'RECEIPT.json',{'batch':batch,'status':'BOUNDED_DEVICE_PREFILTER_ONLY_ZERO','files':[bind(f)for f in sorted(p.iterdir())if f.is_file()and f.name!='RECEIPT.json'],'checks':checks,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
 assert all(bind(v['path'])==v for v in json.loads((p/'RECEIPT.json').read_text())['files']);print(bind(p/'RECEIPT.json'));previous=p
assert len(allrows)==413 and len({(r['source']['source_archive'],r['source']['member'])for r in allrows})==413
print('413 distinct archive/member rows; semantic or whole credit0')
