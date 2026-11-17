"""Hold one raw-record side-pen family candidate without claiming visual study."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-160'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','smoker','stairs','pressure_plate'])}
positions.update((x,y,5)for x in range(9)for y in range(5))
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)];put('critical-original-states.json',{'states':queried,'native_collision_verified':False})
comparisons=[]
for n,ident in [(59,'F02'),(81,'F02')]:
 f=R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json';old=next(x for x in get(f)['cases']if x['id']==ident)
 comparisons.append({'binding':bind(f),'case':ident,'complete_saved_observations_actually_read':old.get('screening_observations',old.get('observations')),'complete_original_comparison_preserved':old.get('saved_written_comparisons',old.get('semantic_family_comparison')),'original_proposal_and_status_preserved':{k:old[k]for k in ['credit_proposal_maximum','formal_credit_added','status']if k in old},'old_images_not_revisited':True,'current_raw_only_comparison':'旧为封闭炉房接通透侧作业棚且有隔门，本源是单小工作室东侧低位无门动物栏，地面高差与屋顶覆草不同；这些区别仍不足在原记录预筛证明独立新整屋空间机制，不认精确复制，也不以换职业/覆草/侧院标签凑参考。当前0只表示保守不提出新增信用，历史结论保留。'})
obs={
'layout':'仅原记录预筛：西侧一间窄长共同室，西单外门、东侧门通同高东露天围场；北石面柜台与南桌椅共室，无内隔或上层。与059F02/081F02封闭共同室接侧围栏作业空间同类，侧场无屋盖/设备更简略仍不足独立新组织，保守0。不称exact复制，也不生成图凑完整参考。',
'proportion':'11×7×11/DV2975，847全存295非air552air零省略；23palette/7全幅原层/3BE/entities[]已读。室内x2..5,z2..8，floor0/use1与东草院floor0/use1同高。y3..6收分木盖空腔无楼板/梯，7高不作7层。',
'facade':'cobble67底墙、oakplanks82、oakstairs74、4柱oaklog；两oakdoor1,1/2,7与6,1/2,3均east/left/closed。东西门虽然同向仍在不同外墙；glasspane7只是原窗。未看PNG，不作建筑质感验收。',
'roof':'逐原索引y3外檐x0/7，y4x1/6，y5x2/5，y6x3/4双脊oakstairs成对长坡；室内北石柜台smoothstoneslabdouble与南桌椅/木压板不是楼梯或上阁楼。露天东院无另盖，不拆成第二栋。',
'materials':'无furnace/smoker/chest/床/水/熔岩/砧/锻台；文件名butcher不能替代加工功能。smoothstoneslab10均double，一孤立fence4,1,7上接未触发plate4,2,7为桌线索；两walltorch不是已验照明/避雨。',
'circulation':'西门前0,1/2,7air，内2,1/2,7air；东门两侧5/7,1/2,3air，东院围栏z1/z7与x10合房东墙围合。院无独立栅栏门，靠东普通门连接房内，不写第三出入口。入口0,0,7west_up最终cobblestairs facingeast/half bottom/straight仅这些原属性；未验台阶碰撞或NPC动物路线。',
'terrain_and_dedup':'四完整JSON实读，classic根size4/max116/start0/surface/beardthin/expansiontrue，houses12项含empty权4，本屋权2legacy/rigid/empty；中心唯一well_top和3optionalbiome不是其他建筑参考。两NPCsocket3,0,4/5 up_west分别finaldouble smoothstoneslab和oakplanks，无动物socket/实体不补牲畜。单Jar缺plainsvillager池非全环境缺；保持旧059/081状态，当前仅原记录不足0/0PNG/0完整视觉信用。'
}
put('raw-family-exclusion.json',{'scope':'raw original record family sufficiency screen only','original_palette_read':23,'original_planes_read':7,'original_BE_read':3,'original_entities':[],'stored_records':847,'omitted_not_air':0,'observations':obs,'comparisons':comparisons,'generated_png':0,'images_actually_viewed':0,'complete_whole_visual_studies':0,'proposal':0,'formal_credit':0})
c=get(P/'source-context.json')['candidates'][0];pool=next(x for x in c['contexts']if x['member'].endswith('/houses.json'));root=c['contexts'][0]['json']
rv={'id':'F01','source_stats':[2975,847,847,295,552,23,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected_pool_member':pool['member'],'selected':[e for e in pool['json']['elements']if e.get('element',{}).get('location')==c['location']],'root_fields':root,'viewed':[],'observations':obs,'written_comparisons':comparisons,'full_study':False,'credit_proposal_maximum':0,'target':'COD3 NPC01 related workshop original-record prefilter','context_reading':'四完整JSON实际读，本屋与center均emptyprocessor；0PNG/0完整视觉研究/0提案。'}
put('review-config.json',{'batch':161,'history_pairs':get(P/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'RAW_ONLY_COMMON_ROOM_AND_CONNECTED_SIDE_YARD_FAMILY_INSUFFICIENT','scope':'COD3 NPC01 original-record family sufficiency prefilter only','cases':[rv],'image_counts':[0,0,0],'raw_family_screen':bind(P/'raw-family-exclusion.json'),'limits':'0新图/0完整视觉参考。原状态共同室和侧院不足新整屋机制，无炉/箱/功能台，不以文件名冒充加工。156NPC05 first159已接纳仅carry0，不推累计；157NPC05/158NPC01待Main各最多1，COD4维持153差847。无Java/游戏/制作/主清单。','next':'继续固定本地用途相关完整建筑的原记录择优，避免单工作间/侧院变体凑数；1000不足不制作。','handoff':'161 classic_butcher1原记录：11×7×11 DV2975，全847=295非air552air，23palette/7原层/3BE/entities[]及4context实际读；共同室两侧门接同高侧院，源无炉/箱/功能台。对059/081完整旧判断保守不足0，非exact复制，0PNG/0完整视觉参考。156 first159仅carry0，157NPC05与158NPC01各max1待审；无Java/游戏/制作/主清单。'})
put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
s=(R/'docs/architecture/research-20261104-smithy-158/seal_screening.py').read_text()
s=s.replace('docs/architecture/research-20261104-smithy-157/latest-independent-admissions.json','docs/architecture/research-20261104-smithy-160/latest-independent-admissions.json')
s=s.replace("check('prior156 and157 pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(156,'F01'),(157,'W01')])", "check('157NPC05 and158NPC01 remain pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(157,'W01'),(158,'F01')])\ncheck('156 resolved first159 exact carry only',carry['156F01_NPC05_resolved_accept1_first159']==get('latest-independent-admissions.json')['newly_notified_NPC05_admission_156_F01'])")
s=s.replace("'source_bodies_visually_screened':len(cases)","'source_bodies_visually_screened':0,'raw_only_source_screens':len(cases)")
s=s.replace("'PASS_COMPLETE_ORIGINAL_SOURCE_READING_INTEGRITY_NOT_SEMANTIC_ADMISSION'","'PASS_RAW_ONLY_SOURCE_FAMILY_SCREEN_INTEGRITY_NO_VISUAL_STUDY'")
s=s.replace("'all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False,'no_projections_generated_or_viewed':True")
s=s.replace('当前158 NPC01最多1待独立判定；153已first156接受仅carry0；156F01与157W01仅NPC05待审各最多1不重送','当前161原记录0；156F01 NPC05已first159接受仅carry0；153已first156接受仅carry0；157W01 NPC05与158F01 NPC01各最多1待审不重送')
(P/'seal_screening.py').write_text(s)
print('Prepared161 raw-only family sufficiency hold0; no PNG, no credit,156 carry0')
