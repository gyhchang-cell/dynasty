import json, hashlib, itertools, zipfile
from pathlib import Path
P=Path(__file__).resolve().parent
PRE=P.parent/'research-20261104-smithy-234'
BASE=P.parent/'research-20261104-smithy-224'
assert not (P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):
 checks.append(dict(check=k,passed=bool(v)))
 assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];c={tuple(b['pos']):b for b in n['blocks']};a=read(P/'derived-assembly.json');d={tuple(b['pos']):b['state']for b in read(P/'derived-source-cells.json')['cells']}
ck('F06 screening selected medium8 actual whole F01',next(x for x in read(P/'pre-render-history-screen.json')['rows']if x['id']=='F06')['eligible_for_new_source_study']and r['member'].endswith('iberian_medium_house_8.nbt'))
ck('11x7x10 DV3578 55palette8BE4entities',n['size']==[11,7,10]and n['DataVersion']==3578 and len(n['palette'])==55 and sum('nbt'in b for b in n['blocks'])==8 and len(n['entities'])==4)
ck('770stored353nonair417air no omissions',len(c)==770 and r['nonair']==353 and r['air']==417)
lines=['Original state indices; rows z columns x; all declared positions stored.']
for y in range(7):
 lines.append(f'y={y}')
 for z in range(10):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[x,y,z]['state']for x in range(11)])))
ck('7layers70RLE770source positions exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
reuse=read(P/'reused-component.json');ck('unique old224 module exact reuse',bind(reuse['source_binding']['path'])['sha256']==reuse['source_binding']['sha256']and reuse['component']==read(BASE/'raw-source-audit.json')['candidates'][1]);ck('old module 2layers6RLE18positions exact',(P/'F04-full-layer-index-rle.txt').read_bytes()==(BASE/'F04-full-layer-index-rle.txt').read_bytes())
ck('unrotated origin3,1,4 box inside zerooverlap356',a['module_origin']==[3,1,4]and a['module_box']==[[3,1,4],[5,2,6]]and a['all_inside_parent']and not a['overlap_nonair']and a['derived_nonair']==356 and a['derivation']=='No rotation; (4,0,6)+(0,1,0)-(1,0,2)=(3,1,4)')
ck('chest3,1,4east anvil5,1,4east smith3,1,5',d[3,1,4]['Name']=='minecraft:chest'and d[3,1,4]['Properties']['facing']=='east'and d[5,1,4]['Name']=='minecraft:chipped_anvil'and d[5,1,4]['Properties']['facing']=='east'and d[3,1,5]['Name']=='minecraft:smithing_table')
ck('three closed doors not six doors',sum(n['palette'][b['state']]['Name']=='minecraft:spruce_door' for b in n['blocks'])==6 and all(d[q]['Name']=='minecraft:spruce_door'and d[q]['Properties']['open']=='false'for q in [(5,1,7),(5,2,7),(6,1,2),(6,2,2),(8,1,6),(8,2,6)]))
ck('south bedroom outside wall sign nonair',d[8,1,7]['Name']=='minecraft:jungle_wall_sign'and d[8,2,7]['Name']=='minecraft:air')
ck('bedroom has one ground-level bed pair',d[7,1,4]['Properties']['part']=='foot'and d[7,1,5]['Properties']['part']=='head'and d[7,1,5]['Properties']['facing']=='south')
ck('four original empty itemframes no displayed equipment',all(e['nbt']['id']=='minecraft:item_frame'and 'Item'not in e['nbt']for e in n['entities']))
ck('village socket double andesite retains type',d[8,0,8]==dict(Name='minecraft:andesite_slab',Properties=dict(type='double')))
ck('7 actual source-class PNG viewed',len(list(P.glob('*.png')))==7)
ctx=read(P/'source-context.json')['candidates'][0]['contexts'];old={c['member']:c for row in read(BASE/'source-context.json')['candidates']for c in row['contexts']}
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed archive and original member hashes',bind(r['source_archive'])['sha256']==r['source_archive_sha256']and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ck('3full contexts exact old reuse',len(ctx)==3 and all(c==old[c['member']]and hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
ck('selected medium8 weight2 toolsmith chance1 weight1',any(e['weight']==2 and e['element']['location'].endswith('iberian_medium_house_8')for e in ctx[0]['json']['elements'])and any(e['weight']==1 and e['element']['location'].endswith('iberian_toolsmith_1')for e in ctx[1]['json']['elements']))
put('support-context-reuse.json',dict(current_contexts_exact_reused=ctx,bindings=[bind(BASE/f)for f in ['source-context.json','extended-generation-context.json','vanilla-local-support-context.json']],prior_detailed_support_binding=bind(P.parent/'research-20261104-smithy-228/support-context-reuse.json'),new_full_JSON_reads=0,old_NBT_or_PNG_reopened=False))
comparisons=[]
for num in [224,225,234]:
 f=P.parent/f'research-20261104-smithy-{num}/manual-review.json';o=read(f);comparisons.append(dict(binding=bind(f),seven_dimensions=o['seven_dimensions'],limits=o['limits']))
for num,case in [(65,'F02'),(186,'F04')]:
 f=P.parent/f'research-20261104-smithy-{num:03}/manual-review.json';o=next(v for v in read(f)['cases']if v['id']==case)
 comparisons.append(dict(binding=bind(f),case=case,seven_dimensions=o['observations'],family_review=o.get('family_review'),whole_boundary=o.get('whole_boundary'),new_old_admission_claim=False,old_NBT_or_PNG_reopened=False))
reason='新屋是同一地面上两间完整封闭并列工住室：西低工具室只有南门通外前坪，东高卧室既有南门又有西北门通北外侧餐座小坪；两室之间x6砖墙不开室内直通，东南门外有原墙牌薄件，不能声称通行已验。区别于065F02封闭卧房+室外L冷作平台/室内上储短阶、186F04南北公共贯通通路旁西私室与东露天切石、224/234前间经庭再入主厅内阶上卧室，以及225下工住上书室。差异在同层两间独立围护、分门外绕与卧室额外后出入口的完整组织，不据镜向、屋脊高低、床数或同一模块新算。至多1相关NPC01工住分区参考待Main独立判断；无热锻链，不保证全历史语义唯一，正式0。'
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,old_NBT_or_PNG_reopened=False,global_semantic_novelty_proven=False))
seven=dict(layout='11×7×10原中屋8加唯一原toolsmith模块作为一栋参考。西低工具室x3..5/z4..6由南5,1/2,7门向外前坪，东卧室x7..8/z2..5有南8,1/2,6门及西北6,1/2,2门；中x6砖墙将两室隔开，没有直接室内联通。北外侧有台座/压力板小餐角与四空物品框，非第二作坊。两室同use1，非上下楼。',proportion='DV3578/55palette/8BE/4entities，全770存格353nonair417air、无省略；旧模块DV3105/5palette/2BE/18存格固定复用。源记录788但独立bbox770，final/忽略air后356nonair。新7层70RLE770位置及7PNG实际读看；旧2层6RLE18位置复用不算新读。屋脊到y6不等7楼，内部无梯/上层可用楼板。',facade='72bricks独立围护，44andesiteslab主要double铺基，15darkoakplanks为工住地板；10blackpane窗配44sprucetrapdoor窗饰檐饰。6sprucedoor块是3个完整闭门且皆left。15persistent mangroveleaves为外缘植栽非承重墙；空itemframe不当工具展示或新模型。',roof='西工具室较低窄南北山墙坡盖，东卧室较高南北双坡；32spruceplanks/61spruceslab/16sprucestairs加trapdoor构高低并列双盖，西2fencegate在4,3,2与4,3,8是盖端构件非新增地面门。y5/6属上盖，既无梯也无连续可用上层证明；分类灰色不等石瓦原材。',materials='原工具模块不旋转：箱3,1,4east/single、chippedanvil5,1,4east、smith3,1,5，箱旧toolsmithloot不等已获得材料。卧室craft8,1,2上8,2,2有三支littrue白烛；床7,1,4foot→7,1,5headsouth仅1对。无原furnace/blast/lava/炉料/水冷/机械锤，不由candleslittrue编热锻链。4itemframes均无Item，原NBT绝对坐标和UUID保留、不改写或导入。',circulation='工间南门5,1/2,7south/leftclosed，外5,1/2,8air；室内5,1/2,5/6与4,1/2,4/5、3,1/2,6air，箱顶3,2,4air。卧室南门8,1/2,6south/leftclosed，外8,1,7是east墙牌而头8,2,7air，不能写全air门前；8,1/2,8air。卧室西门6,1/2,2west/leftclosed，西5,1/2,2及东7,1/2,2air，北侧4,1,1fence+4,2,1pressureplate台、4,1,2jungle底阶餐座不是上楼梯。南入口5,0,9finalandesite上5,1,9open trapdoor非air，门/薄件/绕屋/NPC寻路均未验。',ground_support='parent4,0,6up_south/aligned与child1,0,2down_south/aligned无需旋转，origin=(4,0,6)+(0,1,0)-(1,0,2)=(3,1,4)；3..5/y1..2/z4..6模块完全在宿主内、原nonair覆撞0。接口finaldarkoakplanks，8,0,8村民口finalandesiteslab type=double保留；另5,0,0finalandesite/7,0,3finaldarkoakplanks，3村民socket非3NPC。housesmedium8权2/chance1toolsmith权1，3mod完整上下文及root/tag/worldset/vanilla支持精确复用，不新增JSON阅读；Legacy忽略air不是地形填补，processor、版本转换、根道路/世界地形/自然生成未执行。')
limits=['本批至多1完整相关NPC01工住分区参考待Main独立审查，formal0，非1个游戏成品或COD4参考；不凭文件、模块、床、框、镜向计多例。全历史语义唯一未知，主审可因近族/相关性判0。','新55palette全Properties/8BE/4entities、7层70RLE770位置与7PNG实际读看；旧模块5palette/2BE/2层6RLE18位置原证据复用，788源记录非788独立世界格。','分类图非原纹理与细几何碰撞，4原空itemframes不在格图渲染；门开合、箱盖、砧锻造台侧向操作、工作净空、床位/薄件/NPC路线/防雨火险未实机验证。','东南卧室门外8,1,7墙牌非air、入口5,1,9open trapdoor非air；北餐角fence/pressureplate与椅stairs非连续上楼梯，两个不同屋盖不代表二层。','只有冷作砧/锻造台/箱加住宅craft，没有炉/熔炼/机械锤与NPC生产；箱loot是候选而非玩家原生材料、付款/制作/交易/领取/中文任务指南针验收。','3mod池/processor和root/tag/vanilla等固定旧证据复用，新完整JSON阅读0；池权重非实测生成概率，3村民socket不等3居民。原DV兼容、地形道路、实体坐标转换与原生生成未知。','221first224/224first228/225first231/203first209/157first206后续carry全0；226/229/232仍pending，234HOLD0不追认。COD4153/gap847，NPC01/05/06累计null，1000门槛未达不制作。','仅本地建筑研究/专岗落盘，不改程序贴图模型、主任务清单或共享Jar，不运行Java游戏/联网UI声音亮度唤醒，不碰用户实例原档，不推送Git，不删未验任务，不声称全完成或工时达成。']
put('manual-review.json',dict(batch=235,case='F01_HOST_MEDIUM8_PLUS_REUSED224F04',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_PENDING_INDEPENDENT_REVIEW',new_reference_proposal_maximum=1,formal_credit_added=0,native_acceptance=False,semantic_comparison=reason,actual_reading=dict(new_palette=55,new_BE=8,new_entities=4,new_layers=7,new_RLE_rows=70,new_positions=770,new_PNG_viewed=7,new_full_JSON=0,old_PNG_reopened=0)))
qs=[(3,1,4),(3,2,4),(5,1,4),(3,1,5),(3,1,6),(3,2,6),(4,1,4),(4,2,4),(4,1,5),(4,2,5),(5,1,5),(5,2,5),(5,1,6),(5,2,6),(5,1,8),(5,2,8),(8,1,7),(8,2,7),(8,1,8),(8,2,8),(6,1,2),(6,2,2),(5,1,2),(5,2,2),(7,1,2),(7,2,2),(5,1,9),(5,2,9)]
put('key-derived-route-cells.json',dict(cells=[dict(pos=q,state=d[q])for q in qs],actual_read=True,not_native_collision_or_path_acceptance=True))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous234_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,old_accepted_firstcarry_not_repeated=True,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(active_pending_including_earlier=read(PRE/'session.json')['active_pending']+['235F01_HOST_MEDIUM8_PLUS_REUSED224F04'],current_batch_new_pending_maximum=1,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current234'];now=bind(b['path']);protected.append(dict(last234_checkpoint=b,current235=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('8protected unchanged',len(protected)==8 and all(x['unchanged']for x in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=235,status='NEW_MEDIUM8_WHOLE_MAX1_PENDING_MAIN',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals_maximum=1,active_pending=read(PRE/'session.json')['active_pending']+['235F01_HOST_MEDIUM8_PLUS_REUSED224F04'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue genuinely related source research;235 max1 pending Main,226/229/232 pending unchanged. No repeat oldcarry; no new construction before accepted1000; no unrelated ordinary-house candidates credited.')
put('session.json',s);put('active-checkpoint.json',s)
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
