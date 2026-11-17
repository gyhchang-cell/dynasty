"""Bounded local source preassessment, not a whole lighthouse/workshop study."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];PREV=P.parent/'research-20261104-smithy-178'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'preassessment-original-sources.json')['rows'][0];d=r['original'];pal=d['palette'];c={tuple(b['pos']):b for b in d['blocks']}
ys=(2,3,4,7,8,9,10)
positions={(x,y,z) for y in ys for z in range(6,15) for x in range(7,17)}
used=sorted({c[p]['state'] for p in positions})
localBE=[b for b in d['blocks'] if tuple(b['pos']) in positions and 'nbt'in b]
functional=[{**b,'state_original':pal[b['state']]} for b in d['blocks'] if any(k in pal[b['state']]['Name'] for k in ['grindstone','smithing','furnace','anvil','jigsaw','bed'])]
boundary={'id':'F01','original_local_index_grids_actually_read':[{'y':y,'x_range':[7,16],'z_rows':[{'z':z,'x7to16states':[c[(x,y,z)]['state'] for x in range(7,17)]} for z in range(6,15)]} for y in ys],'actual_original_local_indices_read':630,'actual_complete_used_palette_entries':{str(i):pal[i] for i in used},'complete_local_BE_actually_read':localBE,'additional_functional_original_records_actually_read':functional,'selected_pool_snippets_only':r['selected_pool_snippets'],'full_palette155_BE42_or_all25375states_read':False,'full_context_or_metadata_read':False,'actual_images_viewed':0,'whole_study':False}
put('actual-reading-boundary.json',boundary)
note='25×35×29/DV3120源完整25375声明格均有原记录（机器完整性，非整栋语义验收），机器分类1321非air/24054air。只实际检查x7..16/z6..14的y2/3/4/7/8/9/10共630原索引。下部砂轮(12,3,8)floor/east、下方stone，西邻air及西北满水锅(11,2,8)level3，近cartography/craft/green_carpet、阶式家具与普通barrels；上部smithing_table(14,8,10)南接两去皮横木，西北/西侧两床、两plains_house箱和书架同层，未见由局部可证的专用工作间/工艺流。不能据砂轮、锻造台、灯塔题材或高度认定独立作坊；不排除更全研究可能，但当前相关性不足，保守0。10jigsaw原池/朝向/final已读，其中side house/cross/outdoor_shack是真实非empty池；不声称它们是三整栋、也不判本源必缺翼。selected towncenter weight1/legacy/rigid/empty processor仅片段，其他pool/loot/root/metadata未读。'
put('sources.json',{'candidates':[{k:r[k] for k in ('id','source_archive','member')}],'metadata_not_reference_credit':True})
put('manual-review.json',{'cases':[{'id':'F01','source_archive':r['source_archive'],'member':r['member'],'status':'BOUNDED_LIGHTHOUSE_LOCAL_WORK_MARKERS_RELEVANCE_UNPROVEN_ZERO','observations_bounded_not_whole_building_seven_dimensions':note,'credit_proposal_maximum':0,'formal_credit_added':0,'images_actually_viewed':[],'native_acceptance':False}],'complete_whole_reference_studies':0,'pending_maximum':0,'formal_credit_added':0})
mp=R/'docs/cod4/audit-20261022/coordinator-smithy174-first177-admission-carry-review-20261110.json';main=get(mp)
assert bind(mp)['sha256']=='871a7990682503e395f3b8b9633f7973384c8f3d9aeefa49bc843d4a3e303c42' and bind(mp)['bytes']==6940
integrity={'receipt':bind(mp),'complete_Main_verification_object_actually_read':main,'current_semantic_increment':0,'current_old_admission_increment':0,'no_old_source_images_or_chains_reopened':True}
put('Main177-carry-integrity-only.json',integrity)
ad=get(PREV/'latest-independent-admissions.json');ad['174first177_Main_carry_integrity_only']=integrity;put('latest-independent-admissions.json',ad)
carry=get(PREV/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
assert [(p['batch'],p['id']) for p in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
put('carried-forward-pending.json',carry);put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('dense25375_sizeDV',d['size']==[25,35,29] and d['DataVersion']==3120 and len(d['blocks'])==len(c)==25375)
ck('155palette42BE0entities',len(pal)==155 and sum('nbt'in b for b in d['blocks'])==42 and d.get('entities',[])==[])
ck('air24054',r['material_counts']['minecraft:air']==24054)
ck('630_local_indices11_localBE',len(positions)==630 and len(localBE)==11)
ck('grindstone12_3_8',pal[c[(12,3,8)]['state']]=={'Name':'minecraft:grindstone','Properties':{'facing':'east','face':'floor'}})
ck('smith14_8_10',pal[c[(14,8,10)]['state']]['Name']=='minecraft:smithing_table')
ck('actual_full_water_cauldron',pal[c[(11,2,8)]['state']]=={'Name':'minecraft:water_cauldron','Properties':{'level':'3'}})
ck('two_bed_pairs',sum(pal[c[p]['state']]['Name']=='minecraft:red_bed' for p in positions)==4)
ck('10_jigsaws',sum(pal[b['state']]['Name']=='minecraft:jigsaw' for b in d['blocks'])==10)
ck('no_furnace_anvil_lava_palette',not any(any(k in s['Name'] for k in ['furnace','anvil','lava']) for s in pal))
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
ck('zero_png',not list(P.glob('*.png')))
ck('Main_complete_integrity_object_exact',get(P/'Main177-carry-integrity-only.json')['complete_Main_verification_object_actually_read']==get(mp))
put('verification.json',{'status':'PASS_BOUNDED_PREASSESSMENT_AND_COMPLETE_MAIN177_INTEGRITY_CONTEXT','checks':checks,'check_count':len(checks),'machine_assertions_not_reference_credit':True,'java_run':False,'native_acceptance':False})
s={'batch':179,'status':'LIGHTHOUSE_LOCAL_WORK_MARKERS_RELEVANCE_UNPROVEN_ZERO_WITH_MAIN177_CARRY_CONTEXT','complete_whole_reference_studies':0,'raw_original_sources_bounded_screened':1,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'174first177_later_carry_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'180 continue fixed-local truly related whole-building candidates;157W01 only pending.1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':180})
(P/'HANDOFF.md').write_text('179海滨灯塔towncenter有界相关性预判0：只读7个局部层630原索引、对应使用palette完整条目/11局部BE及额外全部砂轮/锻造台/床/10jigsaw原记录、1selectedpool片段；非155palette/42BE/25375states全部语义读，0PNG/0全context/0完整整栋研究。局部是下杂项家具/锅砂轮与上双床普通箱/书架邻锻造台，专用工作空间未证，保守0不提议。未声称不存在任何工作可能或全栋完整性已语义验。Main177完整6940B核验全文实际阅读并原样双表示保存，仅carry0；174接受仍首次177+1随后0，157保留待审。无Java/游戏/资产/清单更改。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'used_palette_entries':len(used),'checks':len(checks)},ensure_ascii=False))
