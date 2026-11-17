import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-228'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
def st(q):return pal[cells[q]['state']]
ck('14x10x14 DV3465 61palette10BE0entity',n['size']==[14,10,14] and n['DataVersion']==3465 and len(pal)==61 and sum('nbt'in b for b in n['blocks'])==10 and n['entities']==[])
ck('all1960positions482nonair1478air',len(cells)==1960 and r['nonair']==482 and r['air']==1478)
lines=['Original palette-index RLE; rows z, columns x; all source positions stored.']
for y in range(10):
 lines.append(f'y={y}')
 for z in range(14):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([cells[(x,y,z)]['state']for x in range(14)])))
ck('10layers140RLE exact',(P/'F50-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
ck('seven actual PNG complete',len(list(P.glob('*.png')))==7)
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed archive member binding',bind(r['source_archive'])['sha256']==r['source_archive_sha256'] and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')['candidates'][0]['contexts'];ext=read(P/'extended-generation-context.json')['contexts']
 ck('six full new JSON bindings',len(ctx)==4 and len(ext)==2 and all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256'] for c in ctx+ext))
ck('jigsaw final air',cells[(7,1,13)]['nbt']['final_state']=='minecraft:air')
ck('south entrance inner clear head and blackTC support',all(st((7,y,z))['Name']=='minecraft:air'for z in range(9,13)for y in [1,2]) and all(st((7,0,z))['Name']=='minecraft:black_terracotta'for z in range(9,14)))
ck('central south chest retained',st((7,2,6))['Name']=='minecraft:chest' and st((7,2,6))['Properties']['facing']=='south')
ck('chest service trapdoor not air',st((7,1,7))['Name']=='minecraft:spruce_trapdoor' and st((7,1,7))['Properties']['open']=='true')
ck('south craft and lava cauldron not forge',st((9,1,10))['Name']=='minecraft:crafting_table' and st((8,1,10))['Name']=='minecraft:lava_cauldron' and not any(p['Name'] in ['minecraft:anvil','minecraft:furnace','minecraft:smithing_table','minecraft:grindstone']for p in pal))
comparisons=[]
for num in [221,222]:
 f=P.parent/f'research-20261104-smithy-{num}/manual-review.json';o=read(f);comparisons.append(dict(binding=bind(f),seven_dimensions=o['seven_dimensions'],limits=o['limits'],reading='222 seven dimensions read in229;221 saved full judgments reused, no old NBT/PNG reopened'))
reason='候选229是完整中央抬高储箱、两翼多桶分储、南侧工作台与热液锅的开放工料亭。222是八柱小屋内围单中心工作位的冷工具桌亭，且作者HOLD0；221是封闭高木框仓内中央抬高热液平台与顶磨石，已first224。229的中央核心为储物取放而非热液/工具操作，环行服务边与两侧分储不同。仅提NPC01材料储存及制作辅助建筑最多1，是否足够相关独立仍待Main；不等完整铁匠铺，不拆桶/旗/箱计数，不断言全库穷尽。'
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,maximum_proposal=1,formal_credit_added=0))
seven=dict(layout='14×10×14整体开放多边形储藏工料亭，中央剥皮橡木抬台载南向箱，两翼5桶分区取物，南侧工作台和熔岩炼药锅相邻，西北外侧营火。整体只有一层主要活动面；抬台顶局部use2不是上层居室。无门床梯，不当居民房或完整锻坊。',proportion='DV3465，61palette/10BE/0entities，全部1960格482非air1478air无省略。10层140RLE与7PNG实际阅读；源jigsaw仍magenta，若只应用入口finalair会481非air，但未执行原生放置或派生装配，482源非air不当最终成屋。',facade='橡木柱与67栅栏形成开敞下缘，白羊毛26、红羊毛36、橙陶18与骨块18构成多边形彩色带。无玻璃门窗的围合住房；彩带与骨块可借鉴储藏亭识别和分段节奏，分类图不等实际纹理。',roof='105 spruce slab为宽阶式低冠，配4sprucestairs与13trapdoors；顶细立杆/铁栏和红旗，不是可用屋顶楼层。y9切片仅顶端薄件和旗，y10无储存格；不以十层bbox称十层楼。',materials='黑陶82作局部铺地，剥皮橡木54作中央与边构件，干草5/南瓜2/骨块18是布置不等材料供应证明。五桶均piglin_barrel表、中央箱house_piglin表无seed，所有loot候选不等实际库存。西北2,2,1营火lit=true/east/signal_fire=true但Items空/CookingTimes全0；旗7,3,10无Patterns、顶8,9,6黑pig纹。熔岩锅非炉、无砧/炉/磨石/锻造台，不编完整热锻流程。',circulation='南7,1,13jigsaw最终air，head7,2,13air、floor7,0,13黑陶；向北z12..9的x7,use1/head2均air/黑陶支撑，转东8/9,1/2,9可到南工作位前。西桶front4,1/2,8及5,1/2,7、东桶front10,1/2,4与5为空且底黑陶。中央箱7,2,6前7,1,7是top/open/south云杉活板非air，use2/3为空；不能据此声称可跳上、箱盖可开或NPC通路已验。',ground_support='外围多处y0原air不是完整垫层，选中house legacy/rigid，Legacy忽略air的固定源码证据复用，不能把源air当削世界坑或假定地形已填。houses选中storage权3，14选项中mine是single，不能全称legacy。street processor含water位置黑陶→oakplank、四个0.2随机黑陶替换及最终gravel，不执行不叠加成实测比例。root size2/start0/WORLD_SURFACE_WG/beardthin/maxdistance80与可选wythers群系仅注册配置；piglin6..8/weight6及brute2..3/weight1是spawn override，entities空不等已刷。townsset旧221固定对象复用，街路接合/原生坡地未验。')
limits=['新完整相关工料储藏亭研究完成，最多提NPC01辅助材料/制作建筑1，Main尚未独立验收，当前formal0；不是完整铁匠铺，不用桶/抬台/截图凑数。','61palette全Properties、10BE、完整entities[]、10层140RLE1960格、7PNG实际读看；57机器接口候选和11关键词候选不当完整参考，旧源不重开。','所有图为原源分类格而非碰撞/纹理验收，入口jigsaw未替换、482源非air非最终世界数。中央箱前非air活板、箱盖/跳跃/NPC/营火交互未原生验。','4上下文与2root/tag JSON全文读；houses不同element_type保留，loot随机候选不等实际材料/付款/原生获取，processor顺序与概率不外推。','源地面有air/洞，Legacy忽略air不等世界支撑；群系可选、spawn override非实体、街路和坡地落地未验。','222原作者HOLD0与221原接受first224状态完整保留，新的布局比较不证明全库唯一；固定本地Jar不证明远端最新或跨DV原生兼容。','224仅first228已carry1，229不重复；221first224、157first206、203first209后续均0。225/226仍待Main，COD4153/gap847、NPC01/05/06累计未知，1000未达不制作。','只本地只读源研究/写专岗证据，不运行Java/游戏/联网/UI/声音亮度/焦点，不碰实例原档共享Jar专业资产主清单Git，不删除未验提示词，不声称所有任务完成或工时达成。']
put('manual-review.json',dict(batch=229,case='F50_PIGLIN_STORAGE1',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_MAX1_NPC01_SUPPORT_PENDING_MAIN',new_reference_proposal=1,formal_credit_added=0,native_acceptance=False,semantic_judgment=reason,actual_reading=dict(new_palette=61,new_BE=10,new_entities=0,new_layers=10,new_RLE_rows=140,new_positions=1960,new_PNG_viewed=7,new_full_JSON=6,old_PNG_reopened=0)))
put('key-source-route-cells.json',dict(cells=[dict(pos=q,state=st(q),nbt=b.get('nbt'))for q,b in sorted(cells.items())if q[1]<=3 and ((q[0]in[7,8,9] and q[2]>=6)or q[0]in[3,4,5,10,11])],static_not_native=True))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous228_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,accepted224_first228_current229_increment=0,accepted221_first224_current229_increment=0,accepted157_first206_current229_increment=0,accepted203_first209_current229_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(active_pending_including_earlier=['225F01_HOST_PLUS_REUSED224F04','226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1'],current_batch_new_pending=1,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current228'];now=bind(b['path']);protected.append(dict(last228_checkpoint=b,current229=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('eight protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=229,status='NEW_STORAGE_WHOLE_MAX1_PENDING_MAIN',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=1,active_pending=['225F01_HOST_PLUS_REUSED224F04','226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Read entire Main225 new review business object and actual indexed12+8 author ACK; no automatic acceptance/carry.229 pendingMain.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
