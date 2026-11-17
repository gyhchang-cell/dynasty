"""Conservative raw-record family exclusion and first whole independent NPC05 carry."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-158'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
f=R/'docs/cod4/audit-20261022/coordinator-smithy156-F01-mill-whole-review-20261110.json'; j=get(f)
assert bind(f)['sha256']=='6762567316c75308d8ca4f8a7338fbba6026667e2671a9597e521d906aefd624' and bind(f)['bytes']==83682
assert len(j['Main_observations'])==12 and len(j['Main_limits'])==10 and len(j['original_author_seven_observations_preserved'])==7
first={'receipt':bind(f),'complete_Main_judgment_object':j,'first_bound_batch':159,'first_carry_related_reference_increment':1,'subsequent_carry_increment':0,'scope':'COD3 NPC05 阿吉 废村磨坊 complete related spatial reference only','COD4_increment':0,'NPC01_increment':0,'cumulative_NPC05_not_inferred':True}
put('first-carry-156-independent-admission.json',first)
a=get(prev/'latest-independent-admissions.json');a['newly_notified_NPC05_admission_156_F01']=first;a['all_other_prior_admissions_carry_only_increment0_159']=True;put('latest-independent-admissions.json',a)
r=get(P/'raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
oldfile=R/'docs/architecture/research-20261104-smithy-128/manual-review.json';old=next(x for x in get(oldfile)['cases']if x['id']=='F02')
comparisons=[{'binding':bind(oldfile),'case':'F02','complete_saved_observations_actually_read':old['screening_observations'],'complete_original_comparison_preserved':old['saved_written_comparisons'],'original_proposal_and_status_preserved':{k:old[k]for k in ['credit_proposal_maximum','formal_credit_added','status']},'old_images_not_revisited':True,'current_raw_only_comparison':'旧128F02已为地面动物院直接位于高加工室之下，外梯上高热工房/西经营带。当前虽西楼梯北向、L形上室和深橡木高斜盖，仍是围动物下院+抬高加工间+外交通；不以转向/高度/木种或加窗开门当新整屋机制，原记录家族0，无新视觉完整研究。'}]
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','water','smoker'])}
positions.update((0,y,z)for y in range(1,7)for z in range(2,8)if (0,y,z)in mp)
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)];put('critical-original-states.json',{'states':queried,'native_collision_verified':False})
obs={
'layout':'仅原记录家族排除：下方大围栏动物院，上方L形烟熏加工室和西短门颈，西外阶入上西门；与128F02下动物院/上热工房/外阶同整体家族，0。原52palette、14全幅原索引层、11BE及entities[]实际读，无PNG生成/查看，不计完整视觉建筑参考。',
'proportion':'8×14×11/DV3337，声明1232，503存=353非air150显式air，729省略非air；下院土水面y1、围栏y2，抬高木/光滑石floor4/use5，上斜盖收分至y9、烟柱到y13。14高不是14层，y8空腔不是阁楼使用层，源无床或梯。',
'facade':'上室darkoakplanks65/log76/strippedlog18，下栏darkoakfence58；sprucedoor1,5/6,3 west/right/closed，地面gate1,2,7east/closed；另十个open gate在上窗/门颈与屋面，不当十个院门。y6上窗木栅门与open spruce活板仅原状态，不做立面质感判断。',
'roof':'逐原索引见主屋两侧z轴木檐/屋架：y7x2/7边、y8x3/6、y9x4/5双脊列，西门颈横木盖另向x0延；烟柱5,6..8,6起，经y10..12偏折到5,13,5bottomcobbleslab。原记录形态而非已看PNG屋面验收，粗木盖不因高斜坡成为不同工作关系。',
'materials':'smoker5,5,6west/unlit，Cook/Burn/Total0、Items[]/RecipesUsed{}；箱4,5,2south/single/dry，butcherloot/seed1472694927139853744。4处水3,1,3/4,1,4/4,1,5/3,1,7非冷却闭环；下动物socket3,1,4与4,1,6最终grass并不已有2牲畜。6个fence柱装配socket均finalair不当6新建筑；实体空。',
'circulation':'西x0上行BOTTOMnorth阶在y1z7/y2z6/y3z5/y4z4，间置TOPsouth承托，y4z3整darkoakplank接上门1,5/6,3；原步进仅静态，入口0,1,5west_up finalstructure_void与低阶关系不据此断定安全接路。下院gate1,2,7eastclosed，院内x2..5y2多air；上房西短颈连接长加工间，非多独立店。未跑碰撞/头顶/动物或NPC寻路。',
'terrain_and_dedup':'六完整context JSON实际读：swamp根size6/max80/start0/WORLD_SURFACE_WG/terrainnone/expansiontrue；27项houses含empty项，本屋weight4single/rigid/house_swamp_vanilla；两中心项，单swamp biome，fence柱list feature池与处理器。processor会按water所在地把dirt/path变plank，TOPdarkoakslab按tag保留否则dirt；未执行，不认原下平台或pillar最终落地。柱池8个featureplacement/递归fallback是组件非8完整建筑，configuredfeature未展开。单Jar缺vanilla动物池/loot不认全环境缺。完整旧128F02七观察原比较/待审状态保留，本例原记录近族0，不修改旧信用。'
}
put('raw-family-exclusion.json',{'scope':'raw original records only; not whole visual study','original_palette_read':52,'original_planes_read':14,'original_BE_read':11,'original_entities':[],'stored_records':503,'omitted_not_air':729,'observations':obs,'comparisons':comparisons,'generated_png':0,'images_actually_viewed':0,'complete_whole_visual_studies':0,'proposal':0,'formal_credit':0})
c=get(P/'source-context.json')['candidates'][0];pool=next(x for x in c['contexts']if x['member'].endswith('/houses.json'));root=c['contexts'][0]['json']
rv={'id':'F01','source_stats':[3337,1232,503,353,150,52,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected_pool_member':pool['member'],'selected':[e for e in pool['json']['elements']if e.get('element',{}).get('location')==c['location']],'root_fields':root,'viewed':[],'observations':obs,'written_comparisons':comparisons,'full_study':False,'credit_proposal_maximum':0,'target':'COD3 NPC01 related workshop original-record prefilter','context_reading':'六完整JSON实际读，configured feature未展开；0图/0完整视觉研究/0提案。'}
put('review-config.json',{'batch':159,'history_pairs':get(P/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'RAW_ONLY_RAISED_HOT_ROOM_OVER_ANIMAL_YARD_FAMILY_EXCLUSION_NO_WHOLE_CREDIT','scope':'COD3 NPC01 original-record family prefilter only','cases':[rv],'image_counts':[0,0,0],'raw_family_screen':bind(P/'raw-family-exclusion.json'),'first156NPC05admission':bind(P/'first-carry-156-independent-admission.json'),'limits':'仅原记录家族排除0，无视觉整屋信用。156 NPC05 Main完整12观察10限制及原七观察整判断首次159携带接纳1，后续carry0；不推累计。157NPC05/158NPC01仍待Main，COD4仍153差847。无Java/游戏/生产/清单删除。','next':'继续固定本地用途相关建筑原记录择优，重复空间家族先排除；1000不足不制作。','handoff':'159 swamp_butcher1原记录预筛：52palette/14原索引层/11BE/entities[]实际读，503存/729省略，院下高热工房加西外梯与128F02同空间家族，0PNG/0视觉完整研究/0提案。156风车Main独立接受1仅NPC05，完整12观察10限制/原七观察及整个判断首次159入admissions/resolved，清掉156待审，以后carry0，不推累计。157NPC05及158NPC01各最多1仍待审，不重送旧例。无Java/游戏/产品或主清单变更。'})
put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
s=(prev/'seal_screening.py').read_text()
s=s.replace("docs/architecture/research-20261104-smithy-157/latest-independent-admissions.json","docs/architecture/research-20261104-smithy-158/latest-independent-admissions.json")
s=s.replace("get('latest-independent-admissions.json')==json.loads", "{k:v for k,v in get('latest-independent-admissions.json').items()if k not in ['newly_notified_NPC05_admission_156_F01','all_other_prior_admissions_carry_only_increment0_159']}==json.loads")
s=s.replace("check('prior156 and157 pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(156,'F01'),(157,'W01')])", "carry['156F01_NPC05_resolved_accept1_first159']=get('first-carry-156-independent-admission.json')\ncarry['carried_unresolved_whole_reference_proposals']=[x for x in carry['carried_unresolved_whole_reference_proposals']if (x['batch'],x['id'])!=(156,'F01')]\ncheck('prior157NPC05 and158NPC01 pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(157,'W01'),(158,'F01')])\nput('carried-forward-pending.json',carry)")
s=s.replace("'source_bodies_visually_screened':len(cases)","'source_bodies_visually_screened':0,'raw_only_source_screens':len(cases)")
s=s.replace("'PASS_COMPLETE_ORIGINAL_SOURCE_READING_INTEGRITY_NOT_SEMANTIC_ADMISSION'","'PASS_RAW_ONLY_SOURCE_FAMILY_SCREEN_INTEGRITY_NO_VISUAL_STUDY'")
s=s.replace("'all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False,'no_projections_generated_or_viewed':True")
s=s.replace("'prior_admissions_current_increment':0", "'prior_admissions_current_increment':1,'first156NPC05independent_carry_increment':1,'all_other_prior_carry_increment':0")
s=s.replace('当前158 NPC01最多1待独立判定；153已first156接受仅carry0；156F01与157W01仅NPC05待审各最多1不重送','当前159原记录0；156F01 NPC05独立接受1首次159携带以后0；153已first156接受仅carry0；157W01 NPC05与158F01 NPC01各最多1待审不重送')
(P/'seal_screening.py').write_text(s)
print('Prepared159 raw family exclusion,0PNG; first156 NPC05 whole judgment carry1; futurecarry0')
