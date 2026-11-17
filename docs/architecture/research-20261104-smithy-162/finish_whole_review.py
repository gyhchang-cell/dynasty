"""Actual full single-room study, conservative family hold0, no production."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-161'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','stonecutter','candle'])}
positions.update((x,y,z)for y in [1,2,3,4,5,6]for x,z in [(2,2),(2,3),(2,4),(2,5),(2,6),(3,5),(4,5),(5,5),(6,5),(7,5),(3,3),(3,4)])
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)];put('critical-original-states.json',{'states':queried,'native_collision_verified':False})
comparisons=[]
notes={60:'旧060F03小室外北热台/东砂轮与二门绕屋关系，本源唯一东门进单冷石工间，外侧仅窄前台，删热端/改设备/砖顶不是新分区机制。',84:'旧084F02 L形南宽高室→北窄低工作翼，当前矩形同室没有同层第二翼，不把小前檐/几张柜台当独立工作房。',155:'旧155F01已是共同矩形室炉/切石，原记录近族0保留；当前一个切石台/角高箱/低陈设依同室墙边排布，无内隔、冷热独立翼、上住层或新交通，保守0，不借材质或炉数差异加数。'}
for n,ident in [(60,'F03'),(84,'F02'),(155,'F01')]:
 f=R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json';old=next(x for x in get(f)['cases']if x['id']==ident)
 comparisons.append({'binding':bind(f),'case':ident,'complete_saved_observations_actually_read':old.get('screening_observations',old.get('observations')),'complete_original_comparison_preserved':old.get('saved_written_comparisons',old.get('semantic_family_comparison')),'original_proposal_and_status_preserved':{k:old[k]for k in ['credit_proposal_maximum','formal_credit_added','new_formal_credit','status']if k in old},'old_images_not_revisited':True,'current_complete_comparison':notes[n]})
obs={
'layout':'完整Tudor小石匠工屋，一间矩形共用冷加工室，东单门接窄栏边前台，西切石台、北高箱/柜台、东低陈设环墙排布。全部7PNG/56palette/8原索引层/3BE/entities[]实际读看，整栋而非散件研究。无内分墙、独立热端、卧室或第二使用层；对既有单共同工间家族保守0，不提出Main新增参考。',
'proportion':'8×8×10/DV3578，640位置全存=272非air368显式air、零省略。主体外x1..5/z1..7、内3×5，floor1/use2；窄东前台同floor1。屋顶主脊y6、孤立brickwall帽y7，8高不等8层。低家具局部占室内净空，不认为全部15内格都可站/NPC通行。',
'facade':'calcite42白墙配strippedsprucelog18木框，混stonebrick54/tuff21/mossystonebrick10基层，原红brick17/brickstairs52为屋盖。唯一sprucedoor5,2/3,5east/left/closed；whitepane5在西/东/南北壁。侧花箱/灯/3烛littrue原状态不等游戏照明或功能验收，未生成中文招牌或NPC。',
'roof':'红砖主高双坡叠两侧局部伸出檐，y5原TOP spruce stairs在x2/4,z2..6、TOP slab x3,z2..6为封顶，y6其上同区紧接砖屋面，未留使用头高；无梯/楼口，不能称可住阁楼/二层。y7brickwall4,7,2只是孤立帽，不是熏炉烟囱，源无炉。分类全方块图只能研究体量，半块/楼梯真实轮廓与贴图未验。',
'materials':'stonecutter2,2,5south，下2,1,5mossystonebrick，正南2,2,6clay实块非air，东3,2/3,5air可作接近线索，不写南面可直接站。箱2,3,2south/single/dry原masonlootseed-2161309898419228005，下2,2,2brick上2,4,2air、南2,3,3air，开盖/触达仍未运行。brickstairs2,2,3north与mossy石阶4,2,4east/4,3,2north是低陈设，不接高层。无炉/砧/床/水/熔岩/机器产出证据。',
'circulation':'街socket7,1,5east_up/empty/aligned最终mossy石砖阶west/bottom/straight/dry，接6,1,5mossystonebrick、门5,2/3,5，东前6/7,2/3,5air；室内4/3,2/3,5air。东窄台z3/6有栏，z4仅x7栏不当完整四面安全护栏。内NPCsocket3,1,5up_east/plainsvillagers/finaltuff为装配意图，原实体0不认已生成NPC。源未跑门/阶/台与高箱交互或寻路，未完成付款/获取/中文指南针。',
'terrain_and_dedup':'五完整JSON实际读：Tudor root size5/max116/start0/surface/beardthin/expansiontrue；houses16项含empty权6，本屋权1legacy/rigid/emptyprocessor。中心唯一权1挂street_tudor，其tuff水变spruce/.1grass/grass水变water/.4mossy四规则非本屋processor，未执行不得用其改写本屋混地板。biome7原条含wythers temperate_island重复一次，保留不称7不同建筑。单Jar缺plainsvillager池/masonloot非全环境缺。060F03/084F02完整旧七观察与原比较、155F01完整原记录七观察及比较已读，旧图/源未重跑；当前单室/角柜/切石/东前台不足新整屋机制0，不据exact fingerprint未匹配自加。'
}
put('whole-family-comparison.json',{'cases':comparisons,'current_full_visual_study_complete':True,'family_distinctness_sufficient':False,'proposal':0,'formal_credit_added':0})
c=get(P/'source-context.json')['candidates'][0];pool=next(x for x in c['contexts']if x['member'].endswith('/houses.json'));root=c['contexts'][0]['json']
rv={'id':'F01','source_stats':[3578,640,640,272,368,56,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected_pool_member':pool['member'],'selected':[e for e in pool['json']['elements']if e.get('element',{}).get('location')==c['location']],'root_fields':root,'viewed':['whole','cutaway','vertical','y0','y2','y4','y6'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':0,'target':'COD3 NPC01 related workshop whole study, family insufficient0','context_reading':'五完整JSON实际读；本屋empty与center streetprocessor区分，biome重复保留，0原实体/3BE。'}
f=R/'docs/cod4/audit-20261022/coordinator-smithy156-first159-carry-review-20261110.json';j=get(f);assert bind(f)['sha256']=='51e3f9f99fbd16f11299edfce80b4d2bb985a08f76000f9f003e3cc0b7cb7446' and j['new_Main_reference_increment']==0
put('156-first159-carry-review-reuse.json',{'receipt':bind(f),'complete_Main_carry_review_preserved':j,'new_reference_increment':0,'does_not_accept159_or160_as_visual_whole_studies':True,'pending157_158_unchanged':True})
put('review-config.json',{'batch':162,'history_pairs':get(P/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'COMPLETE_SINGLE_COLD_WORKROOM_WHOLE_STUDY_HELD0_FAMILY_INSUFFICIENT','scope':'COD3 NPC01 whole workshop spatial study, conservative family hold0','cases':[rv],'image_counts':[7,7,0],'whole_family_comparison':bind(P/'whole-family-comparison.json'),'carry_review_reuse':bind(P/'156-first159-carry-review-reuse.json'),'limits':'7PNG全看/56palette/8原层/3BE/entities[]全读，只完整研究不计新参考。156 first159 whole judgment carry复核0，本批不重计；157NPC05/158NPC01各max1待Main不重送，COD4仍153差847。无Java/游戏/制作/主清单。','next':'继续固定本地相关整屋研究，优先真实整体布局差异，不凭屋面/材料/陈设/文件数凑1000；门槛不足不制作。','handoff':'162完整Tudor mason1整屋研究：8×8×10 DV3578，640全存272非air368air，56palette/8原状态层/3BE/entities[]/7PNG与5context实际读。东门单冷加工间/西切石/北高箱/小东前台，木封顶上紧接砖屋面非可用阁楼；对060F03/084F02/155F01全文旧判断保守家族不足0，不增独立待审。新156 first159 carry复核整个判断保留0，157NPC05和158NPC01仍待Main不重送。无Java/游戏/生产/主清单。'})
put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
s=(R/'docs/architecture/research-20261104-smithy-160/seal_screening.py').read_text()
s=s.replace('docs/architecture/research-20261104-smithy-159/latest-independent-admissions.json','docs/architecture/research-20261104-smithy-161/latest-independent-admissions.json')
s=s.replace("held=len(cfg['cases'])-complete","held=sum(x.get('credit_proposal_maximum',0)==0 for x in cfg['cases'])")
s=s.replace("'source_bodies_visually_screened':0,'raw_only_source_screens':len(cases)","'source_bodies_visually_screened':len(cases),'raw_only_source_screens':0")
s=s.replace("'PASS_RAW_ONLY_SOURCE_FAMILY_SCREEN_INTEGRITY_NO_VISUAL_STUDY'","'PASS_COMPLETE_WHOLE_SOURCE_STUDY_INTEGRITY_FAMILY_HELD0'")
s=s.replace("'all_generated_projections_actually_viewed':False,'no_projections_generated_or_viewed':True","'all_generated_projections_actually_viewed':True")
s=s.replace(";bindings(cfg)","\nfor key in ['whole_family_comparison','carry_review_reuse']:bindings(cfg[key])\nfor rv in cfg['cases']:\n for comparison in rv['written_comparisons']:bindings(comparison['binding'])")
s=s.replace('当前160原记录0','当前162完整整屋研究家族不足0')
(P/'seal_screening.py').write_text(s)
print('Prepared162 complete7 views, family hold0; carry verification0 retained without new credit')
