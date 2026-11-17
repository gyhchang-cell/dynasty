"""Completed whole source study, with conservative pending whole proposal."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get('raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']};planes=[]
for y in range(d['size'][1]):
 rows=[[-1]*d['size'][0]for _ in range(d['size'][2])]
 for b in d['blocks']:
  if b['pos'][1]==y:rows[b['pos'][2]][b['pos'][0]]=b['state']
 planes.append({'y':y,'rows_z_ascending_x_ascending':rows})
assert {(x,p['y'],z):s for p in planes for z,row in enumerate(p['rows_z_ascending_x_ascending'])for x,s in enumerate(row)if s!=-1}=={tuple(b['pos']):b['state']for b in d['blocks']}
put('all-original-planes.json',{'legend':'-1 omitted, not explicit air; other cells original palette index','size':d['size'],'palette':pal,'planes':planes,'original_block_entities':[b for b in d['blocks']if b.get('nbt')],'original_entities':d['entities']})
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','stairs','stonecutter','lantern'])}
positions.update((x,y,z)for x in [3,4,5]for y in [0,1,2]for z in [2,3,4,5,6]if(x,y,z)in mp)
positions.update([(4,1,1),(5,1,4),(6,2,4),(6,3,4),(6,4,4),(6,8,4),(6,9,4)])
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)]
put('critical-original-states.json',{'states':queried,'omitted_not_air':[[0,0,0],[8,0,8],[4,9,4]],'native_collision_or_reach_verified':False})
ctx=get('source-context.json')['candidates'][0];oldpath=OUT.parent/'research-20261104-smithy-090/source-context.json';old=json.loads(oldpath.read_text())['candidates'][0];by={c['member']:c for c in old['contexts']};reused=[c['member']for c in ctx['contexts']if c==by.get(c['member'])];assert len(reused)==5
collection=get('biome-collection-context.json')
with ZipFile(r['source_archive'])as z:
 b=z.read(collection['member']);assert hashlib.sha256(b).hexdigest()==collection['sha256']and json.loads(b)==collection['json']
put('source-context-reuse.json',{'previous_complete_context_binding':bind(oldpath),'same_value_hash_reused_members':reused,'current_selected_actually_read':'weight2 legacy_single_pool_element rigid giant_taiga/mossify','new_biome_tag_and_collection_actually_read':True,'collection_duplicate':'wythers:old_growth_taiga_swamp appears twice, not two biomes/buildings','no_context_or_component_reference_credit':True})
obs={
 'layout':'同一单层T形作坊：西短门颈接中央共用厅，北窄凹臂放切石台/低阶陈设，南相对窄凹臂放低阶陈设，东端炉与独立石烟构。不是矩形一室只换职业/木色的直接变体，也不是分门四室或工住楼。最多1整屋空间提案依据入口颈—中央分流—南北窄臂/东热端关系；与085同室炉+切石家族仍有交集，可由Main判0。全部8图/20palette/10原层/2BE/entities[]已读，未自加正式信用。',
 'proportion':'9×10×9/DV3465，810声明406存333非air73显式air，404省略不能补air。地板y0/use1；中央厅x3..5,z3..5，窄北/南臂x4/5,z2/6是同高开口，原连续中央高空腔直至y6，无楼板/梯，y7..8坡盖和y9烟顶不是十层或可用阁楼。原索引完整重建406状态；8PNG全实际看完。',
 'facade':'stone71围T形低墙、diorite24构东炉后壁/烟构，spruceplanks154作宽坡盖和少量地板，非全石屋。西门2,1/2,4 east/right/closed，位置西不称东门；仅一扇上下状态，没有北南独立客门。源无玻璃/箱/床/NPC实体或招牌，不能推定中文任务/营业状态。',
 'roof':'高东西长主坡盖覆南北窄臂，西突出门颈有较低短盖；154 spruceplanks全块与54 spruce slab（含double和bottom）构阶状长坡，不能写成154楼梯或分类灰石瓦。中央灯4,6,4悬挂，原roof腔无地板；东6,z4烟构从炉上diortewall y2/3接double dioriteslab y4/5/6、diorite y7、double slab y8、wall y9，不称已验空心排烟或登楼。',
 'materials':'北4,1,2 stonecutter north，北前4,1,1是stone非air，南侧4,1,3 air为可读接近空间，不因facingnorth写北侧可站。东6,1,4 furnace west/litfalse、Items[]/CookBurnTotal0/RecipesUsed{}，前5,1/2,4 air但原生操作/路径未验。南4/5,1,6 bottom diorite stairs south、北5,1,2 bottom north是同高低陈设不通楼。灯共5：0,3,3/5及4,6,4、8,6,4 hangingtrue，6,2,5 hangingfalse。无水/熔岩/砧/床/梯/箱，切石+炉不等完整打铁产出。',
 'circulation':'西socket0,0,4 west_up/aligned/empty/final spruce_stairs[facing=east]仅原显式facing，不补写half/shape；旁0,0,3/5原cobble底阶。经2,1/2,4门入3..5,y1/2,z3..5连续air中央厅，北4/5,y1/2,z3接北凹位，南4/5,y1/2,z5接低阶前；东到5,1/2,4炉前。门颈与窄臂形成T分流但共享地面，无独立封闭冷热室/南北穿出门。灯、低阶、烟构不冒充额外房间；未验门碰撞、切石作业与炉交互/NPC寻路。',
 'terrain_and_dedup':'单NBT存T形原基础/墙/屋盖，不缺必需房翼，唯一empty入口无补柱/村民socket。root gianttaiga WORLD_SURFACE_WG/beardthin/size6/start0/terrainradius2/allowedrange22是生成语境，不证明山脚承托。5主JSON与090完整已读同hash逐值复用，当前屋权2legacy/rigid/mossify，中心path_randomizer不挂本屋；新biometag/collection全文读，2原版+optional列表含重复old_growth_taiga_swamp不加计。对060F03室内外三侧工区、084F02连续L高低翼、085F01矩形同室炉/切石/箱、090F01矩形长坡单炉箱逐项保留完整比较；T形凹臂/分流整体最多1待独立判定，不按两工位/三臂/8图/高盖/材料或archive-member数凑1000。'
}
notes=['旧060室外北热台/东砂轮经两门绕屋，当前单西门中央分流到室内北凹臂/东炉；本件无户外绕屋工线，整体关系不同，非换热源职业本身计数。','旧084 L连续高南箱室/低北smith翼单门同层，本件T中央厅及南北相对窄凹臂/东炉端；没有L的主箱室/独立低翼，也没有内隔门。','旧085矩形共同室西北炉/高箱、中东切石、后箱；本件无箱及双北门，单西门颈接中央T分流、切石退北窄臂/东端炉，是否仅同室多工位变体由Main严格判定，可判0，不靠职业或无exact保证通过。','旧090矩形长坡单炉/西南箱无其他翼，本件无箱且原T地板及南北窄臂占用组织不同；共同高坡屋盖/闪长岩烟构单独0。']
comparisons=[{**c,'current_complete_comparison':n}for c,n in zip(get('pre-render-spatial-comparison.json')['comparisons'],notes)]
put('complete-study-review.json',{'case':'F01','observations':obs,'comparisons':comparisons,'credit_proposal_maximum':1,'formal_credit_added':0,'independent_admission':False,'actual_images_viewed':['whole','cutaway','y0','y2','y4','y6','y8','vertical']})
put('complete-reading-integrity.json',{'original_planes':bind(OUT/'all-original-planes.json'),'palette_entries_actually_read':20,'original_planes_actually_read':10,'lossless_original_index_reconstruction':True,'original_stored_positions':406,'omitted_positions_not_air':404,'original_block_entities_actually_read':2,'original_entities':d['entities'],'current_generated_png':8,'current_png_actually_viewed':8,'unviewed_current_png':0,'critical_states':bind(OUT/'critical-original-states.json'),'context_reuse':bind(OUT/'source-context-reuse.json'),'new_collection_verified':bind(OUT/'biome-collection-context.json'),'native_acceptance':False})
pool=next(c['json']for c in ctx['contexts']if c['member'].endswith('/houses.json'));root=next(c['json']for c in ctx['contexts']if '/worldgen/structure/'in c['member'])
rv={'id':'F01','source_stats':[3465,810,406,333,73,20,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_absent_positions':[[0,0,0],[8,0,8],[4,9,4]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected':[e for e in pool['elements']if e.get('element',{}).get('location')==ctx['location']],'root_fields':root,'viewed':['whole','cutaway','y0','y2','y4','y6','y8','vertical'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':1,'context_reading':'五主JSON与090已完整读同hash逐值复用；当前selected及root/centers实读，新biometag及gianttaigas集合全文读，不补查已通过旧语义范围；mossify不是中心道路processor，源无柱/箱loot。'}
put('review-config.json',{'batch':153,'history_pairs':get('pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'ONE_COMPLETE_RELATED_T_PLAN_WORKSHOP_PENDING_MAXIMUM_ONE','scope':'COD3 NPC01 related complete cutting/firing workshop spatial research; no production','cases':[rv],'image_counts':[8,8,0],'pre_render_spatial_comparison':bind(OUT/'pre-render-spatial-comparison.json'),'complete_study':bind(OUT/'complete-study-review.json'),'complete_reading':bind(OUT/'complete-reading-integrity.json'),'limits':'完整8PNG/20palette/10原层/2BE/entities[]，406存404省略；T形共用单层未编二层/独立多室。085同室炉+切石有家族交集，最多1请独判，可0。初始root路径误套Trek层级已更正到Jar实际village_giant_taiga.json，先前singleJar缺失不当真实缺；context已重存原值。150已first152接受仅carry0，最新Main first152 review复用不重验旧源。无Java/游戏/生产/主清单。','next':'继续154固定本地用途相关完整作坊，使用本次冻结历史指纹缓存只补新源delta，不重读旧已判范围；1000不足不制作。','handoff':'153 RSgianttaiga masons_house2完整8PNG/20palette/十原层/2BE/entities[]；9×10×9 DV3465 810声明406存333非air73air/404省略。西门颈→中央共用T厅→北切石凹臂/南低阶凹臂/东炉及烟构，单层无上楼/箱床。对060F03/084F02/085F01/090F01完整旧观察比较，整组最多1待Main独判，不以同室双职业/高顶保证新家族，可判0。五context复用090，新tag/collection实际读。150first152已Main逐值通过，仅carry0不再重验旧147148151152。没有Java/游戏/制作/声音亮度/主清单操作。'})
ad=json.loads((OUT.parent/'research-20261104-smithy-152/latest-independent-admissions.json').read_text());ad['all_prior_acceptances_carry_only_no_current_increment_153']=True
reviewpath=ROOT/'docs/cod4/audit-20261022/coordinator-smithy150-first152-carry-review-20261110.json';ad['150first152_Main_carry_review']=bind(reviewpath);put('latest-independent-admissions.json',ad)
s=(OUT.parent/'research-20261104-smithy-151/seal_screening.py').read_text()
s=s.replace("bindings(get('latest-independent-admissions.json'));bindings(cfg)","check('prior admitted complete judgment reused unchanged',get('latest-independent-admissions.json')['newly_notified_admission_150_F01']==json.loads((ROOT/'docs/architecture/research-20261104-smithy-152/latest-independent-admissions.json').read_text())['newly_notified_admission_150_F01']);bindings(cfg)")
s=s.replace("put('carried-forward-pending.json',carry);bindings(carry)","check('150 accepted first152 carry no repeated credit',carry['150F01_resolved_accept1_first152']==get('latest-independent-admissions.json')['newly_notified_admission_150_F01']);put('carried-forward-pending.json',carry)")
s=s.replace('当前151提案0，150仅max1待独立判定','当前153最多1待独立判定，150已first152接受且仅carry0')
(OUT/'seal_screening.py').write_text(s)
print(json.dumps({'queried_positions':len(queried),'full_reading':True,'proposal_maximum':1,'formal_credit':0,'prior150_credit_current':0},ensure_ascii=False))
