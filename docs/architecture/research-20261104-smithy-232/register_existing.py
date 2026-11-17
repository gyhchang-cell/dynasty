import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def exact(b):assert bind(b['path'])==b;return read(b['path'])
rows=[]
for num,batch,name in [(203,209,'203-final-acceptance-first-carry.json'),(221,224,'first-carry-221.json'),(224,228,'first-carry-224.json'),(225,231,'first-carry-225.json')]:
 folder=P.parent/f'research-20261104-smithy-{batch}';carrypath=folder/name;c=read(carrypath);receipt=read(folder/'RECEIPT.json');assert bind(carrypath)in receipt['files']
 if num==203:
  fb=c['Main_final_binding'];f=exact(fb);assert f==c['full_Main_final_judgment_preserved_exact']and c['first_author_carry_batch']==batch and c['current_increment']==1 and c['all_later_increment']==0
  ab=f['actual_author_ACK'];exact(ab);orig=f['full_original_judgment'];assert f['accepted_whole_reference_increment']==1;whole=f['whole_case'];s=orig['source'];source=dict(source_archive=s['source_archive'],source_archive_sha256=s['source_archive_sha256'],member=s['member'],nbt_sha256=s['nbt_sha256']);origbinding=bind(P.parent/'research-20261104-smithy-203/manual-review.json');seven=orig['seven_dimensions'];limits=orig['limits']
 else:
  fb=c['final_acceptance_binding'];f=exact(fb);assert f==c['final_acceptance_entire_object']and c['first_bound_batch']==batch and c['increment']==1
  ab=c['actual_author_ACK_binding'];a=exact(ab);assert a==c.get('original_ACK_entire_object',c.get('actual_author_ACK_entire_object'))
  origbinding=c['original_whole_manual_binding'];orig=exact(origbinding);exact(c['original_whole_receipt_binding']);exact(c['actual_author_receipt_binding']);seven=orig['seven_dimensions'];limits=orig['limits'];whole=c['case'];s=read(P.parent/f'research-20261104-smithy-{num}/sources.json')['candidates'][0];source={k:s[k]for k in ['source_archive','source_archive_sha256','member','nbt_sha256']}
  if num==221:assert f['accepted_related_complete_NPC01_reference'] and f['original_seven_dimensions_preserved']==seven and f['original_eight_limits_preserved']==limits
  else:assert f['current_accepted_NPC01_whole_maximum']==1 and f['original_seven_dimensions']==seven and f['original_eight_limits']==limits
 assert len(seven)==7 and len(limits)>=8
 maincarry=ROOT/f'docs/cod4/audit-20261022/coordinator-architecture{num}-first{batch}-actual-carry-review-20261111.json'
 rows.append(dict(whole_case=whole,original_batch=num,first_carry_batch=batch,primary_whole_source=source,original_manual_binding=origbinding,original_seven_dimensions=seven,original_limits=limits,original_limit_count=len(limits),Main_final_binding=fb,actual_author_ACK_binding=ab,first_carry_binding=bind(carrypath),first_carry_receipt_binding=bind(folder/'RECEIPT.json'),Main_first_carry_review_binding=bind(maincarry)if maincarry.exists()else None,historical_accepted_unit=1,increment_this_registration=0,all_later_carry_increment=0,registration_scope='Passive existing final+firstcarry chain; no new semantic/native acceptance'))
keys=[(r['primary_whole_source']['source_archive_sha256'],r['primary_whole_source']['member'],r['primary_whole_source']['nbt_sha256'])for r in rows];assert len(set(keys))==len(rows)
o=dict(schema='dynasty.architecture.existing-final-firstcarry-subset.v1',batch=232,rows=rows,verified_existing_chain_subset_size=len(rows),subset_size_is_not_new_reference_credit=True,semantic_dedup_basis='Four distinct original wholecase/primary whole source identities with already Main final-accepted original spatial judgments; reused modules not separate rows. No claim of newly exhaustive semantic dedup.',NPC01_cumulative_total=None,COD4_accepted=153,COD4_gap=847,formal_increment=0,full_historical_registry_complete=False,excluded_pending=['226','229','232'],excluded_author_HOLD0=['228','231'],NPC05_or_NPC06_reclassified=False,old_NBT_or_PNG_reopened=False,all_tasks_complete=False)
(P/'existing-NPC01-final-firstcarry-register.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');print('Registered existing verified subset',len(rows),'newcredit0/cumulative null')
