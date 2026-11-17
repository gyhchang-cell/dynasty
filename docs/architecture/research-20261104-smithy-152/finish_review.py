"""One whole source study and first carry of the independently accepted150."""
import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
mainpath=ROOT/'docs/cod4/audit-20261022/coordinator-smithy150-F01-whole-review-20261110.json';main=json.loads(mainpath.read_text());mainbinding=bind(mainpath)
assert mainbinding['sha256']=='f9816c117453a001ec45416b5de84b0142d796c1476a27f73fc367c441e1d70b'
assert main['accepted_related_whole_reference']==1 and main['COD4_credit']==0 and len(main['independent_findings'])==8 and len(main['mandatory_limits'])==6 and len(main['complete_five_saved_observations_and_comparisons_read'])==5
entry={'receipt':mainbinding,'complete_Main_judgment_object':main,'first_bound_batch':152,'accepted_related_COD3_increment_once':1,'COD4_increment':0,'native_acceptance':False,'game_task_completion':False}
put('first-carry-150-independent-admission.json',entry)
r=get('raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']};planes=[]
for y in range(d['size'][1]):
 rows=[[-1]*d['size'][0]for _ in range(d['size'][2])]
 for b in d['blocks']:
  if b['pos'][1]==y:rows[b['pos'][2]][b['pos'][0]]=b['state']
 planes.append({'y':y,'rows_z_ascending_x_ascending':rows})
assert {(x,p['y'],z):s for p in planes for z,row in enumerate(p['rows_z_ascending_x_ascending'])for x,s in enumerate(row)if s!=-1}=={tuple(b['pos']):b['state']for b in d['blocks']}
put('all-original-planes.json',{'legend':'-1 omitted, not explicit air; other cells original palette index','size':d['size'],'palette':pal,'planes':planes,'original_block_entities':[b for b in d['blocks']if b.get('nbt')],'original_entities':d['entities']})
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','stonecutter','lantern'])}
positions.update((x,y,z)for x,y,z in [(2,2,3),(2,3,3),(3,2,3),(3,3,3),(4,2,3),(4,3,3),(2,2,4),(2,3,4),(3,2,4),(3,3,4),(4,2,4),(4,3,4),(5,2,4),(5,3,4),(5,2,3),(5,3,3),(6,2,3),(6,3,3),(1,1,3),(2,1,3),(2,1,2),(1,2,6),(3,5,3),(3,0,3)]if(x,y,z)in mp)
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)]
put('critical-original-states.json',{'states':queried,'omitted_not_air':[[0,0,0],[3,6,3],[3,7,3]],'native_collision_or_reach_verified':False})
obs={
 'layout':'单一小石作室，西单门入紧凑中央/南侧绕行空腔，西北stonecutter朝南；中部泥/黏土与落地魂灯占位，不能称全空通堂。单室没有储箱、床、第二工位分区、外工作翼或第二层。黏土/粗泥不规则小丘外壳是材质/轮廓变化，不足以新增完整单室作坊家族；7原图/26palette/8原层/5BE/entities[]完整研究1，提案0/正式0。',
 'proportion':'8×8×7/DV3337，448声明194存161非air33显式air，254省略。原y6和y7全省略非显式air，最高原实体y5不是8层。使用floor1/use2，y0 TOP木半块承盘+四柱socket；没有梯或上使用地板，壳内空腔不是阁楼。全部7图实际看完，无生成未看图冒充观察。',
 'facade':'西spruce单门1,2/3,3 facingwest/right/closed，两上下状态一个入口。粗泥46/podzol18/黏土25/terracotta7/普通土3拼不规则壳；不是灰图所示全石屋，也不是自然洞窟/已贴山坡地形。四darkoakplanks在2/5,1,1/5局部框位，不编造完整木框地形承重。',
 'roof':'y5粗泥/灰化土/黏土不规则全块帽，y4壳围低空腔；低边25 darkoakstairs全部TOP不同朝向角形作盘沿支托，不是25登楼台阶。22 darkoakslab全部原TOP在y0；houseprocessor可改TOPslab为泥但尚未执行，不能将原木承盘渲染当最终泥土屋实景。无屋顶梯、第二层或烟囱。',
 'materials':'单stonecutter2,2,2 facingsouth，前2,2,3air、上2,3,3air；无配方/产物/交易或任务获取实测。魂灯1,2,6、3,3,3、5,3,2均hangingfalse落地；3,3,3灯下面3,2,3clay，4,3,3terracotta，不能说中轴连续air。无箱桶/水/熔岩/炉高炉/砂轮/锻台/砧/床/梯，泥壳石作室不等完整热工作坊。',
 'circulation':'西入口socket0,1,3 west_up/aligned/empty最终darkoakstairs[east,bottom,straight,dry]不是finalair；接1,1,3 coarse_dirt下方地面，西门lower1,2,3→2,2/3,3air。直东3,2,3clay/3,3,3落地灯挡住，不称从门直通后壁。可读南绕2/3/4/5,y2/3,z4air再到5/6,y2/3,z3air，仍仅原状态，不宣称NPC转弯、灯碰撞、切石台互动和危险躲避实测。',
 'terrain_and_dedup':'4柱socket2/5,0,1/5 up_west/rollable/feature darkoakfence/finalstructure_void，非4NPC或4栋。原补柱feature向下及水浸updater/tag复用150已读证据，不证明实时落地。六context与150逐值同hash复用，当前实选house权2 single/rigid/house_swamp_vanilla，区别150tannery实际streetprocessor；house规则TOP木slab按replaceable/location保留或变dirt，BOTTOM规则仅匹配BOTTOM，不自行把原TOP改完当结果。root swamponly/terrainNONE/size6/WORLD_SURFACE_WG只是语境。对148单公共炉室热源/台改为切石及泥壳不新增多区机制；075敞棚不同但本件仍单室职业变体，保守0；不以不同occupation、壳造型、hash或五接头凑1000。'
}
notes=['旧敞前水/热源小棚尚无干储或住翼，本件封闭泥壳单室有切石台，原整体界限较完整但不单凭封闭壳或职业变化增加新家族，0。','旧公共小炉室西双门/折角台/南炉，本件西单门/单切石台及中部占位皆同单室紧凑作业；泥壳轮廓/无烟构不自行形成独立空间组织，0。']
comparisons=[{**c,'current_complete_comparison':n}for c,n in zip(get('pre-render-spatial-comparison.json')['comparisons'],notes)]
put('complete-study-review.json',{'case':'F01','observations':obs,'comparisons':comparisons,'credit_proposal_maximum':0,'formal_credit_added':0,'independent_admission':False,'actual_images_viewed':['whole','cutaway','y0','y2','y4','y6','vertical']})
ctx=get('source-context.json')['candidates'][0];oldctx=json.loads((OUT.parent/'research-20261104-smithy-150/source-context.json').read_text())['candidates'][0];oldby={c['member']:c for c in oldctx['contexts']}
assert all(c==oldby[c['member']]for c in ctx['contexts'])
put('source-context-reuse.json',{'previous_full_context':bind(OUT.parent/'research-20261104-smithy-150/source-context.json'),'six_contexts_same_hash_and_value':True,'column_feature_tag_previous_reading':bind(OUT.parent/'research-20261104-smithy-150/column-feature-context.json'),'current_selected_house_processor':'trek:village/house_swamp_vanilla','no_new_reference_credit_from_reuse':True})
put('complete-reading-integrity.json',{'original_planes':bind(OUT/'all-original-planes.json'),'palette_entries_actually_read':26,'original_planes_actually_read':8,'lossless_original_index_reconstruction':True,'original_stored_positions':194,'omitted_positions_not_air':254,'original_block_entities_actually_read':5,'original_entities':d['entities'],'current_generated_png':7,'current_png_actually_viewed':7,'unviewed_current_png':0,'critical_states':bind(OUT/'critical-original-states.json'),'context_reuse':bind(OUT/'source-context-reuse.json'),'native_acceptance':False})
pool=next(c['json']for c in ctx['contexts']if c['member'].endswith('/houses.json'));root=next(c['json']for c in ctx['contexts']if '/worldgen/structure/'in c['member'])
rv={'id':'F01','source_stats':[3337,448,194,161,33,26,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_absent_positions':[[0,0,0],[3,6,3],[3,7,3]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected':[e for e in pool['elements']if e.get('element',{}).get('location')==ctx['location']],'root_fields':root,'viewed':['whole','cutaway','y0','y2','y4','y6','vertical'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':0,'context_reading':'六主JSON与150已完整读范围逐值同hash复用；当前selected实际读权2single/rigid/house_swamp_vanilla，四column使用150down feature/updater/tag复用，不新生成/新增语义信用；当前single Jar无missing不意味环境已验。'}
put('review-config.json',{'batch':152,'history_pairs':get('pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'ONE_COMPLETE_RELATED_MASON_STUDY_HOLD_ZERO_FIRST_CARRY_ACCEPTED150','scope':'COD3 NPC01 related whole workshop research; no production','cases':[rv],'image_counts':[7,7,0],'pre_render_spatial_comparison':bind(OUT/'pre-render-spatial-comparison.json'),'complete_study':bind(OUT/'complete-study-review.json'),'complete_reading':bind(OUT/'complete-reading-integrity.json'),'first_carry150':bind(OUT/'first-carry-150-independent-admission.json'),'limits':'7PNG/26palette/8层/5BE/entities[]全部实际读；194存254省略，y6/7全省略非air。六context同150复用，house processor不能套street，柱未执行。本源单室职业变体0；150Main accepted1首次绑定152仅COD3相关，非任务完成/COD4/1000。初次联合摘要命令有一处Python字典推导少空格SyntaxError，未执行读取/写入，已更正单独完整读，无截断补计。无Java/游戏/生产/主清单。','next':'继续153固定本地相关完整作坊，复用150已接受完整判断只carry0，不重复重哈希；1000不足不制作。','handoff':'152完整7PNG/26palette/8层/5BE/entities[]，8×8×7/DV3337，448声明194存161非air33air/254省略；泥壳小切石单室完整研究1但同单室家族提案0。六context同150复用，当前house实际houseprocessor而非150street。首次carry Main150完整8判断6限制和五旧比较，解150pending，仅COD3相关+1，当前152新提案0/正式0；141142first144等仅carry0，无游戏任务完成或1000达标。未运行Java/游戏、未制作/改主清单。'})
ad=json.loads((OUT.parent/'research-20261104-smithy-151/latest-independent-admissions.json').read_text());ad['newly_notified_admission_150_F01']=entry;ad['all_other_acceptances_carry_only_no_current_increment_152']=True;put('latest-independent-admissions.json',ad)
s=(OUT.parent/'research-20261104-smithy-151/seal_screening.py').read_text()
s=s.replace("put('carried-forward-pending.json',carry);bindings(carry)","carry['carried_unresolved_whole_reference_proposals']=[v for v in carry['carried_unresolved_whole_reference_proposals']if not(v.get('batch')==150 and v.get('id')=='F01')]\ncarry['150F01_resolved_accept1_first152']=get('first-carry-150-independent-admission.json')\ncheck('150 accepted once first152 complete Main retained',carry['150F01_resolved_accept1_first152']==get('latest-independent-admissions.json')['newly_notified_admission_150_F01']and not carry['carried_unresolved_whole_reference_proposals'])\nput('carried-forward-pending.json',carry);bindings(carry)")
s=s.replace("'prior_admissions_current_increment':0","'prior_admissions_current_increment':1,'first_carry_150_related_COD3_increment':1,'COD4_increment':0")
s=s.replace('当前151提案0，150仅max1待独立判定','当前152提案0，150Main accepted1仅COD3相关首次绑定152关闭pending')
(OUT/'seal_screening.py').write_text(s)
print(json.dumps({'queried_positions':len(queried),'full_reading':True,'new_proposal':0,'first_prior150_COD3_accepted_increment':1,'COD4_increment':0},ensure_ascii=False))
