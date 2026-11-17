"""Seal one completely read source, held zero for conservative family dedup."""
import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get('raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
planes=[]
for y in range(d['size'][1]):
 rows=[[-1]*d['size'][0]for _ in range(d['size'][2])]
 for b in d['blocks']:
  if b['pos'][1]==y:rows[b['pos'][2]][b['pos'][0]]=b['state']
 planes.append({'y':y,'rows_z_ascending_x_ascending':rows})
rebuild={(x,p['y'],z):state for p in planes for z,row in enumerate(p['rows_z_ascending_x_ascending']) for x,state in enumerate(row)if state!=-1}
assert rebuild=={tuple(b['pos']):b['state']for b in d['blocks']}
put('all-original-planes.json',{'legend':'-1 omitted, not explicit air; other cells original palette index','size':d['size'],'palette':pal,'planes':planes,'original_block_entities':[b for b in d['blocks']if b.get('nbt')],'original_entities':d['entities']})
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['stairs','trapdoor','cauldron','lantern','fence'])}
positions.update([(4,5,1),(4,5,2),(3,4,1),(3,4,2),(2,1,7),(4,1,7),(3,2,4),(3,3,4),(3,4,4),(3,5,4),(3,2,5),(3,2,6),(3,2,7),(3,2,8),(3,4,8),(3,5,5),(3,6,4)])
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)]
put('critical-original-states.json',{'states':queried,'omitted_not_air':[[0,7,0],[3,7,3],[6,0,9]],'native_collision_or_reach_verified':False})
assert all(tuple(p)not in mp for p in [[0,7,0],[3,7,3],[6,0,9]])
obs={
 'layout':'单一窄长干工/储物敞口北段，向南直接连两水缸带盖栏棚。西侧三格并列低入口台阶先入北段，内部沿南北直通湿棚，无隔门、住翼、内梯或上层使用地板。整屋仍属干作业屋附带盖湿区的既有关系，虽从侧附/L凹位改为长轴延伸，保守不据此增加家族信用；完整研究1/提案0/正式0，不以制革职业名或城垛屋盖凑数。',
 'proportion':'7×8×10/DV3953，560声明291存220非air71显式air，269省略。原8层索引全读并精确重建291状态；最高非省略y6，y7全省略不是显式air。主要floor1/use2；y4两箱和y5半块屋盖不是可上二层，源无梯。7张当前图全实际看完，无未看图冒充观察。',
 'facade':'砂岩及切制砂岩69/31、terracotta18围北段三侧；西入口x1,z1..3开敞无门。南段y2侧/后丛林木栏，y4侧/后TOP闭trapdoor形成上带，不能叫两层封闭走廊或多扇门。六棕墙旗位南外z9三面/东外x6三面，原NBT仅banner id，无人物或已验活动招牌。0,4,4北向jungle_wall_hanging_sign双面原Tannery与装饰符文，非中文化已完成。',
 'roof':'北段y5 smooth_sandstone外圈/18砂岩slab含TOP铺盖及两TOP反向砂岩阶檐，y6八BOTTOM砂岩slab作间隔屋沿装饰；无屋顶交通梯。南湿棚y5为20个BOTTOM birch_slab，分类灰图不代表石盖。屋顶装饰和半块屋面不证明完整避雨或新增一层，不把南棚另算一栋。',
 'materials':'湿缸2,2,7和4,2,7均water_cauldron level3/下sandstone1，北储4,4,z1/2是west/right与west/left双箱，原两个独立tannerylootseed -2035829315196625911和1207068590726367160；一组双箱不是两店/两份项目奖励。箱下4,3,z1/2是TOP closed spruce_trapdoor，箱上4,5,z1/2为TOP砂岩slab而非air；箱前3,4,z1/2显式air，未验原生箱盖/高位够取。北台2/3,2,1 TOP spruce_trapdoor，上盆栽2,3,1及落地lantern3,3,1；无炉/高炉/锻台/砂轮/砧/床，不称完整热工作坊。',
 'circulation':'西socket0,1,2 west_up/rollable/empty/finalstructure_void并带原placement_priority/selection_priority0，非finalair。三个BOTTOM sandstone east阶在1,1,z1/2/3为同高并排，不是三步上楼；入北段后中轴x3,y2,z2..7原air，南端3,2,8被jungle_fence拦住，不说贯通南出口。北/南交界3,2/3/4,4 air、3,5,4 smoothsandstone；内部同层连接，无门碰撞/寻路运行。南侧高closedtrapdoor/墙旗均为原非air物件，未验实际间隙通行。',
 'terrain_and_dedup':'原两层砂岩台基和西入口包含在单模板，仅一个empty入口，不要求外接第二屋，entities[]/无NPCsocket。house实选权2single_pool_element/rigid/minecraft:empty；root minecraft:jigsaw,size6/start0/WORLD_SURFACE_WG/beard_thin/expansionhacktrue/max80。centers三正常98/98/49和三僵尸2/2/1，zombie_desert仅僵尸中心语境，不能套正常house。原版tanneryloot/biometag/zombieprocessor仅本Jar missing，不断言环境缺。对120F01 L形工屋/低湿凹位（外缸use1、内use2，不误说全部同高），121F02石长居/work室+侧湿盖+高箱，保守仍既有干工附湿棚家族；150外阶低湿/高干微室是另一个待判案，本件不占用或推定150已通过。'
}
notes=['旧L干工围低use1三缸凹位，内use2；本件无L翼、直连南湿棚，均干工附湿位，不凭沿长轴展开或砂岩盖认定新家族，0。','旧北西门入狭长工住、侧低盖三缸、屋内高箱但无梯；本件没有床和门、南同层湿棚，保守不因删住翼/高箱计新机制，0。','150低use1湿坪与上use4微干储间由外直阶连接，max1尚未独立通过；本件use2长向干湿同层与高位箱无登楼，不能当150第二例或推定150已通过。']
comparisons=[]
for c,n in zip(get('pre-render-spatial-comparison.json')['comparisons'],notes):comparisons.append({**c,'current_complete_comparison':n})
put('complete-study-review.json',{'case':'F01','observations':obs,'comparisons':comparisons,'credit_proposal_maximum':0,'formal_credit_added':0,'independent_admission':False,'actual_images_viewed':['whole','cutaway','y0','y2','y4','y6','vertical']})
put('complete-reading-integrity.json',{'original_planes':bind(OUT/'all-original-planes.json'),'palette_entries_actually_read':30,'original_planes_actually_read':8,'lossless_original_index_reconstruction':True,'original_stored_positions':291,'omitted_positions_not_air':269,'original_block_entities_actually_read':10,'original_entities':d['entities'],'current_generated_png':7,'current_png_actually_viewed':7,'unviewed_current_png':0,'critical_states':bind(OUT/'critical-original-states.json'),'native_acceptance':False})
ctx=get('source-context.json')['candidates'][0];pool=next(x['json']for x in ctx['contexts']if x['member'].endswith('/houses.json'));root=next(x['json']for x in ctx['contexts']if '/worldgen/structure/'in x['member'])
rv={'id':'F01','source_stats':[3953,560,291,220,71,30,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_absent_positions':[[0,7,0],[3,7,3],[6,0,9]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected':[e for e in pool['elements']if e.get('element',{}).get('location')==ctx['location']],'root_fields':root,'viewed':['whole','cutaway','y0','y2','y4','y6','vertical'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':0,'context_reading':'三个原JSON全文实际读：desert root/houses/centers，正常house权2single/rigid/empty；中心僵尸权2/2/1 processor仅语境，缺三原版文件仅单Jar。Trek元数据与150同固定archive复用，无新语义信用。'}
put('review-config.json',{'batch':151,'history_pairs':get('pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'ONE_COMPLETE_RELATED_TANNERY_STUDY_HOLD_ZERO_EXISTING_FAMILY','scope':'COD3 NPC01 related complete wet-work/dry-storage building research; no production','cases':[rv],'image_counts':[7,7,0],'pre_render_spatial_comparison':bind(OUT/'pre-render-spatial-comparison.json'),'complete_study':bind(OUT/'complete-study-review.json'),'complete_reading':bind(OUT/'complete-reading-integrity.json'),'limits':'7PNG全读/30palette/8原层/10BE/entities[]，291原存/269省略；高箱下TOP闭trapdoor、箱上TOP石slab，不说二层/可达。三context实际读。对已有干工附湿作棚保守同族0，150max1尚待Main。无Java/游戏/制作/主清单。','next':'继续152固定本地用途相关完整作坊；复用已读证据，先判家族再全图全层，1000不足不制作。','handoff':'151 Trek desert_tannery1完整研究1但提案0/正式0。7PNG/30palette/八原层/10BE/entities[]全部实际读；7×8×10 DV3953 560声明291存220非air71air/269省略，use2干工北段直连南双满水缸棚，无门梯上使用层，y4双箱不当第二层。三context原读，selected权2single/rigid/empty，僵尸processor不挂正常house。对120F01/121F02既有干工附湿作棚保守同族0；150max1仅carry待判。没有Java/游戏/声音亮度/生产/主清单操作。'})
ad=json.loads((OUT.parent/'research-20261104-smithy-150/latest-independent-admissions.json').read_text());ad['all_prior_acceptances_carry_only_no_current_increment_151']=True;put('latest-independent-admissions.json',ad)
s=(OUT.parent/'research-20261104-smithy-150/seal_screening.py').read_text().replace('当前150仅max1待独立判定','当前151提案0，150仅max1待独立判定')
(OUT/'seal_screening.py').write_text(s)
print(json.dumps({'queried_positions':len(queried),'all_images_read':7,'complete':1,'proposal':0,'formal_credit':0},ensure_ascii=False))
