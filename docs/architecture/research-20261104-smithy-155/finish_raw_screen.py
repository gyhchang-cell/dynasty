"""Reject an unchanged single-room spatial family before generating projections."""
import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
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
put('all-original-planes.json',{'legend':'-1 omitted not air; otherwise original palette index','size':d['size'],'palette':pal,'planes':planes,'original_block_entities':[b for b in d['blocks']if b.get('nbt')],'original_entities':d['entities']})
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','stonecutter','carpet'])}
positions.update((x,y,z)for x in [3,4,5,6]for y in [1,2,3]for z in [3,4,5]if(x,y,z)in mp)
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)];put('critical-original-states.json',{'states':queried,'native_collision_or_reach_verified':False})
comparisons=[]
for n,ident,note in [(85,'F01','旧公共一室已有炉/切石同层组合，无独立冷/热间；本源只是西三炉排与东切石、两相邻南门、共用地毯区。工位数量和两门不形成新整屋分区，原记录预筛0，不冒充看过原PNG。'),(153,'F01','153待判T厅有门颈/北南窄凹臂/东炉不同组织；本源是矩形共同室原状态，无T臂、内隔门、上楼或独立工作翼，0，不占用153待判信用。')]:
 f=OUT.parent/f'research-20261104-smithy-{n:03d}/manual-review.json';c=next(x for x in json.loads(f.read_text())['cases']if x['id']==ident);comparisons.append({'binding':bind(f),'case':ident,'complete_saved_observations_actually_read':c.get('observations',c.get('screening_observations')),'current_raw_only_comparison':note,'old_images_not_revisited':True})
obs={'layout':'原状态预筛：同一个矩形共同工间，西三普通炉，东单切石台，两相邻南门入同室，中央红蓝地毯。原索引所有内格可确认无分墙/独立翼/上使用层；不因三炉或两门说成双作坊。明确重复单室家族0，未生成PNG/未做视觉整屋研究。','proportion':'10×8×9/DV3465，720声明340存287非air53显式air，380省略。floor1/use2，y5内高空腔，y6木帽/y7压力板，不说8层或上室；17palette与八原层/4BE/entities[]实际读，0原图。','facade':'木坡与石墙外表，仅相邻南门4,2/3,6east/right/open与5,2/3,6north/right/closed，facing不同不当一内隔门一外门；二者都在同一南墙且共同室北连。未做原PNG立面观察。','roof':'原spruceplanks109与63stonepressureplate分布外皮，原plate poweredfalse。mossify对plate顺序.01button/.01bottom cobbleslab/.99air只是处理规则，不当实际63触发机关或63建筑。没有梯或上楼地板，不看图也不编屋顶形态验收。','materials':'三个炉2,2,z3/4/5east且unlit/Items[]/CookBurnTotal0/RecipesUsed{}，切石6,2,4north，中央blue/red carpet各3非air。无箱床水熔岩砧磨，无实际产出/交易。两灯3/6,4,4 hangingtrue，原实体空。','circulation':'南socket4,0,8 south_up/empty/aligned/finalspruce_stairs[facing=north]只有facing原属性；5,0,8北向底石阶以及4/5,1,7北向底石阶接南门，但未运行半块步进。门内x3,y2,z3..5air为炉前，x4/5,y2,z3..5地毯非air，上y3air；共享同室而非三炉各分房。无寻路/门/台交互实测。','terrain_and_dedup':'六主context与153同hash值复用，当前selected权2legacy/rigid/mossify，中心path_randomizer不挂本屋；pressureplate可替换石按钮/半块/air不是矿石已产出。源floor0内部有显式air但floor1木板，不能省略等air或虚拟地下室。对085矩形同室双工位家族保守原记录排除0；不凭非exact/三炉/两门/压力板数生成无用图凑数。'}
put('raw-family-exclusion.json',{'scope':'original-record family screen only, not whole visual study','original_records_read':340,'original_palette_read':17,'original_planes_read':8,'original_BE_read':4,'original_entities':[],'generated_png':0,'images_actually_viewed':0,'complete_whole_visual_studies':0,'observations':obs,'comparisons':comparisons,'proposal':0,'formal_credit':0})
ctx=get('source-context.json')['candidates'][0];oldfile=OUT.parent/'research-20261104-smithy-153/source-context.json';old=json.loads(oldfile.read_text())['candidates'][0];by={c['member']:c for c in old['contexts']};assert all(c==by[c['member']]for c in ctx['contexts'])
pool=next(c['json']for c in ctx['contexts']if c['member'].endswith('/houses.json'));selected=[e for e in pool['elements']if e.get('element',{}).get('location')==ctx['location']]
root=next(c['json']for c in ctx['contexts']if '/worldgen/structure/'in c['member'])
rv={'id':'F01','source_stats':[3465,720,340,287,53,17,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_absent_positions':[[0,0,0],[9,7,8]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected':selected,'root_fields':root,'viewed':[],'observations':obs,'written_comparisons':comparisons,'full_study':False,'credit_proposal_maximum':0,'context_reading':'六JSON与153原hash/值相同复用，当前selected和mossify全文实读；原记录同公共室排除，未生成或查看PNG，不算完整视觉建筑参考。'}
put('review-config.json',{'batch':155,'history_pairs':get('pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'RAW_ONLY_SINGLE_COMMON_ROOM_FAMILY_EXCLUSION_NO_PNG_NO_WHOLE_CREDIT','scope':'COD3 NPC01 original-record family prefilter only','cases':[rv],'image_counts':[0,0,0],'raw_screen':bind(OUT/'raw-family-exclusion.json'),'context_reuse':bind(oldfile),'limits':'17palette/八原索引/4BE/entities[]全原状态读，340存380省略；清楚仅单公共室三炉/切石/相邻南门，提前0排除。0PNG生成/查看、0视觉整屋研究、0提案信用；不把原索引扫描计1000。既有153max1只carry待Main，150first152只carry0。无Java/游戏/制作/主清单。','next':'156继续用途相关完整作坊原记录择优，原单室换职业先排除，不生图/信用；1000不足不制作。','handoff':'155原记录预筛RSgianttaiga masons_house1：17palette/八层/4BE/entities[]、340存380省略，西三炉与东切石在同一个矩形共同室，两相邻南门通一室，源无内隔/翼/上使用层。对085同室炉切石家族0，明确提前排除；0PNG生成/查看、0完整视觉整屋研究、0提案/正式。六context同153复用，plate63的mossify替换未运行不称红石机关；153max1仅carry待Main。未运行Java/游戏或改生产/主清单。'})
ad=json.loads((OUT.parent/'research-20261104-smithy-154/latest-independent-admissions.json').read_text());ad['all_prior_acceptances_carry_only_no_current_increment_155']=True;put('latest-independent-admissions.json',ad)
s=(OUT.parent/'research-20261104-smithy-154/seal_screening.py').read_text()
s=s.replace("'source_bodies_visually_screened':len(cases)","'source_bodies_visually_screened':0,'raw_only_source_screens':len(cases)")
s=s.replace("'PASS_COMPLETE_ORIGINAL_SOURCE_READING_INTEGRITY_NOT_SEMANTIC_ADMISSION'","'PASS_RAW_ONLY_SOURCE_FAMILY_SCREEN_INTEGRITY_NO_VISUAL_STUDY'")
s=s.replace("'all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False,'no_projections_generated_or_viewed':True")
s=s.replace('当前154提案0，继承153最多1待独立判定','当前155原记录预筛提案0，继承153最多1待独立判定')
(OUT/'seal_screening.py').write_text(s)
print(json.dumps({'critical_positions':len(queried),'PNG':0,'whole_visual_studies':0,'proposal':0,'formal_credit':0},ensure_ascii=False))
