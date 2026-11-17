"""Record the uniquely authorized269 NPC06 auxiliary reference carry; no production."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
main=ROOT/'docs/cod4/audit-20261022/coordinator-architecture269-actual-author23ACK-final-acceptance-20261112.json';mb=main.read_bytes();m=json.loads(mb)
assert bind(main)['sha256']=='8431bbc788948db155915a4740264e287d4db70935ac16e38a4845e201f810a5'
assert m['decision']=='ACCEPT_ONE_WHOLE_AUXILIARY_NPC06_SPATIAL_REFERENCE_ONLY' and m['accepted_related_whole']==1
grant=m['first_formal_carry_authorized_once'];assert grant=={'reference_batch':269,'scope':'NPC06 auxiliary complete spatial reference','maximum_increment':1,'COD4_increment':0,'current_firstcarry_observed':False,'no_repeat_later':True}
seen=[]
for p in sorted((ROOT/'docs/architecture').glob('research-*/session.json')):
 if p.parent==OUT:continue
 d=json.loads(p.read_text())
 if d.get('269_first_carry_batch')is not None or d.get('first_carry269_added',0)>0 or d.get('old269_carry_added',0)>0:seen.append(str(p))
assert not seen,seen
for k in ['Main_actual_whole_preACK','author23_specific_ACK','author_ACK_receipt','complete_prior239_family_preserved_reference']:assert bind(m[k]['path'])==m[k]
ack=json.loads(Path(m['author23_specific_ACK']['path']).read_text())
assert m['all_actual_author23_responses']==ack['finding_responses']+ack['limit_responses']
assert len(m['complete_Main_seven_dimensions'])==len(m['complete_original_seven_dimensions'])==7
assert len(m['complete_Main12_findings'])==12 and len(m['complete_Main11_limits'])==11 and len(m['complete_original11limits'])==11
family_path=Path(m['complete_prior239_family_preserved_reference']['path']);family_bytes=family_path.read_bytes();family=json.loads(family_bytes)
assert family['effective239_firstcarry']==243 and family['old_double_entry_withdrawn']is True
(OUT/'Main269-final-original.json').write_bytes(mb)
(OUT/'prior239-complete-family-preserved.json').write_bytes(family_bytes)
record={'batch':277,'source_batch':269,'Main_final_binding':bind(main),'Main_final_complete_original':m,
 'complete_prior239_binding':bind(family_path),'complete_prior239_original_preserved':family,
 'actual_reading':'Main final29210B completely displayed in two bounded sections: allMain7/12/11, original7/11, all23specificresponses plus everydecision/scope/binding field. Prior239 full70713B preserved exact as previously reviewed comparison, not claiming all nested historical material freshly reread; no oldNBT/PNG reopened.',
 'first_carry':{'source_batch':269,'first_carry_batch':277,'scope':'NPC06 auxiliary complete spatial reference','increment':1,'COD4_increment':0,'NPC_cumulative':None,'later_reuse_increment':0},
 'new_whole_studies':0,'formal_credit_added':0,'native_acceptance':False,
 'no_blackgranny_alchemy_or_NPC_task_acceptance':True,'production_changes':0,'tasks_deleted':0,
 'prior239_first243_only':True,'prior259_first263_only':True,'prior260_first267_only':True,
 '273_275_pending_unchanged':True,'274_alias_correction_credit':0,'all_tasks_complete':False}
put('269-first-carry-acceptance.json',record)
prev=ROOT/'docs/architecture/research-20261104-smithy-276';s=json.loads((prev/'session.json').read_text());prior_pending=list(s['active_pending'])
target='269F03_SWAMP_STILT_HOUSE_BODY_NPC06_AUXILIARY_SPACE';assert prior_pending.count(target)==1
s['active_pending'].remove(target)
assert '273F01_ATI_WHOLE_NOMADIC_CAMP_NPC04_AUXILIARY_SPACE'in s['active_pending']and '275F02_SNOWY_LIBRARY_RESIDENTIAL_NPC13_AUXILIARY_SPACE'in s['active_pending']
s.update({'batch':277,'status':'269_ACCEPTED_NPC06_AUXILIARY_FIRST_CARRY277_ONLY','new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':1,'old269_carry_added':1,'269_first_carry_batch':277,'269_first_carry_executed':True,'author269_Main_final':bind(main),'first_carry269_record':bind(OUT/'269-first-carry-acceptance.json'),'previous276_receipt':bind(prev/'RECEIPT.json'),'next':'269 first277 only1, all future reuse0. Continue next distinct related whole local source.273/275 remain pending;274 correction0; COD4153/847 and NPC totalsnull.'})
put('session.json',s)
protected=[]
for r in json.loads((prev/'protected-inputs-current.json').read_text())['files']:
 before=r['current276'];now=bind(before['path']);protected.append({'previous276':before,'current277':now,'unchanged':before==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':0,'cod5_missing_not_invented':True})
sealed_checks=[]
for batch in [269,276]:
 p=ROOT/f'docs/architecture/research-20261104-smithy-{batch}/RECEIPT.json';d=json.loads(p.read_text())
 for f in d['files']:assert bind(f['path'])==f
 sealed_checks.append({'batch':batch,'receipt':bind(p),'all_original_file_bindings_unchanged':True})
put('active-checkpoint.json',{'batch':277,'status':s['status'],'session':bind(OUT/'session.json'),'first_carry269':bind(OUT/'269-first-carry-acceptance.json'),'new_whole_studies':0,'NPC06_auxiliary_carry_increment':1,'COD4_increment':0,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'formal_credit_added':0,'native_acceptance':False,'tasks_deleted':0,'all_tasks_complete':False})
checks={'Main_current_final_exact_sha':bind(main)==record['Main_final_binding'],'prior269_firstcarry_absent':not seen,'complete_Main7_12_11_original7_11_retained':True,'all23_ACK_exact_retained':len(m['all_actual_author23_responses'])==23,'complete239_exact_bytes_preserved':(OUT/'prior239-complete-family-preserved.json').read_bytes()==family_bytes,'Main_final_exact_bytes_preserved':(OUT/'Main269-final-original.json').read_bytes()==mb,'sealed269_276_all_unchanged':len(sealed_checks)==2,'private_pending_only269_removed':s['active_pending']==[x for x in prior_pending if x!=target],'protected8_unchanged':len(protected)==8 and all(r['unchanged']for r in protected),'no_cumulative_NPC_inferred':s['NPC06_total']is None,'no_new_study_or_task_acceptance':True}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'passed':True,'sealed_originals':sealed_checks,'new_source_reading_credit':0})
put('RECEIPT.json',{'batch':277,'status':s['status'],'files':[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'],'checks':checks,'new_whole_studies':0,'NPC06_auxiliary_first_carry269':1,'269_first_carry_batch':277,'later269_reuse_increment':0,'COD4_increment':0,'formal_credit_added':0,'native_acceptance':False,'tasks_deleted':0,'all_tasks_complete':False})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'carry':bind(OUT/'269-first-carry-acceptance.json')},ensure_ascii=False))
