import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-233';BASE=P.parent/'research-20261104-smithy-224'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];c={tuple(b['pos']):b for b in n['blocks']};d={tuple(b['pos']):b['state']for b in read(P/'derived-source-cells.json')['cells']};a=read(P/'derived-assembly.json')
ck('selected F04screen medium5 new',next(x for x in read(P/'pre-render-history-screen.json')['rows']if x['id']=='F04')['eligible_for_new_source_study']and r['member'].endswith('iberian_medium_house_5.nbt'))
ck('12x9x11 DV3578 69pal10BE2entity',n['size']==[12,9,11]and n['DataVersion']==3578 and len(n['palette'])==69 and sum('nbt'in b for b in n['blocks'])==10 and len(n['entities'])==2)
ck('1188stored451nonair737air',len(c)==1188 and r['nonair']==451 and r['air']==737)
lines=['Original state indices; rows z columns x; all declared positions stored.']
for y in range(9):
 lines.append(f'y={y}')
 for z in range(11):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(12)])))
ck('9layers99RLE exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
reuse=read(P/'reused-component.json');ck('unique224 child exact',bind(reuse['source_binding']['path'])['sha256']==reuse['source_binding']['sha256']and reuse['component']==read(BASE/'raw-source-audit.json')['candidates'][1]);ck('old2layer6RLE reused exact',(P/'F04-full-layer-index-rle.txt').read_bytes()==(BASE/'F04-full-layer-index-rle.txt').read_bytes())
ck('CW90 module origin9,1,6 inside zerooverlap453nonair',a['module_origin']==[9,1,6]and a['module_box']==[[7,1,6],[9,2,8]]and not a['overlap_nonair']and a['derived_nonair']==453)
ck('chest9,1,6 andanvil9,1,8south smith8,1,6',d[(9,1,6)]['Name']=='minecraft:chest'and d[(9,1,6)]['Properties']['facing']=='south'and d[(9,1,8)]['Name']=='minecraft:chipped_anvil'and d[(9,1,8)]['Properties']['facing']=='south'and d[(8,1,6)]['Name']=='minecraft:smithing_table')
ck('double andesite interface actualProperties',d[(7,0,7)]==dict(Name='minecraft:andesite_slab',Properties=dict(type='double')))
ck('8 PNG viewed',len(list(P.glob('*.png')))==8)
ck('armorstand ironhelmet andclockframe actual original',n['entities'][0]['nbt']['id']=='minecraft:armor_stand'and n['entities'][0]['nbt']['ArmorItems'][3]['id']=='minecraft:iron_helmet'and n['entities'][1]['nbt']['Item']['id']=='minecraft:clock')
ctx=read(P/'source-context.json')['candidates'][0]['contexts'];old={c['member']:c for row in read(BASE/'source-context.json')['candidates']for c in row['contexts']}
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed archive and source member exact',bind(r['source_archive'])['sha256']==r['source_archive_sha256']and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256']);ck('three complete contexts exact reuse',len(ctx)==3 and all(c==old[c['member']]and hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
put('support-context-reuse.json',dict(current_mod_contexts_exact_reused=ctx,bindings=[bind(BASE/f)for f in ['source-context.json','extended-generation-context.json','vanilla-local-support-context.json']],prior_detailed_support_binding=bind(P.parent/'research-20261104-smithy-228/support-context-reuse.json'),new_full_JSON_reads=0,old_NBT_or_PNG_reopened=False))
comparisons=[]
for num in [224,225]:
 f=P.parent/f'research-20261104-smithy-{num}/manual-review.json';o=read(f);comparisons.append(dict(binding=bind(f),seven_dimensions=o['seven_dimensions'],limits=o['limits']))
reason='本屋东南低工具前间经西侧门出同一南前庭，北西主厅沿内折阶到唯一上卧室；没有底床/上第二床室或北上书室。与224低冷作前间→前庭→北厅内折阶上卧室的功能骨架近族，镜向/更小/床数减少/甲架和时钟不能单独证明独立完整建筑原则。与225内竖梯上书室不同不等绕开224近族。作者HOLD0，完整研究保留，不凭原host未见/源hash不同计信用。'
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,old_NBT_or_PNG_reopened=False))
seven=dict(layout='12×9×11原中屋5加唯一原工具模块成一栋工住：东南低工具前间经西门向南西前庭，前庭北门入北西主厅，主厅北内折阶上唯一青床室。主厅下箱与原铁盔甲架是陈设/存储，卧室旁有原时钟框；无底床房/上书室，不拆前间与楼层计数。',proportion='宿主DV3578/69palette/10BE/2entity，全1188格451非air737air无省略；旧模块DV3105/5palette/2BE/18格复用，1206源记录含18重合，独立bbox1188，忽略air/final后453nonair。新9层99RLE1188格及8PNG实际读看，旧2层6RLE只复用；use1/4两层，最高y8檐薄件非9层。',facade='101bricks围护、49andesiteslab含double基铺地、14darkoak板和9TOPslab内floor，17blackpane窗，两个spruce门上下4块为2门。22persistent mangroveleaves外缘植栽非承重柱；甲架和clockframe未在源格图渲染，不因此造新NPC模型或物品图。',roof='51spruceplanks/77spruceslab/1倒stairs与47trapdoors构北高双坡、南东低工作翼盖；y3/4低翼盖接北楼y6/7主盖，y8仅中檐活板。5fencegate多屋盖端窗/栏，非5新地面入口；无第三楼面或上天台梯。',materials='CW90后箱9,1,6south、砧9,1,8south、smith8,1,6；toolsmithloot无seed仅候选。宿主箱3,1,5east用savannahouseloottable无seed；唯一青床4,4,4foot→4,4,5headsouth。原armorstand5.5,1,5.5仅铁盔Damage0/无手持，itemframe4.5,5.5,5.96875仅clock，非居民/新人物建模/已获得材料；无炉/熔岩/热锻链。',circulation='工具西门6,1/2,8west/rightclosed，外5,1/2,8air；内7,1/2,6与8/9,1/2,7air，胸顶9,2,6air。主厅南门4,1/2,6south/rightclosed，内5,1,5原格air但5.5,1,5.5甲架存在，不能忽略实体碰撞。北底阶6,1,3north上6,1,2finalwood平台，再西5,2,2westbottom→4,3,2westbottom，西3,3,2topeaststairs/其上4/5air，接x3..5,y3TOPslab上use4卧室。上3,4,5scaffolding且3,5,5sea_pickle不是上新层路线。南入口7,0,10finalair但内7,1,9brickbottomstairs/7,2,9blackpane，不写成无阻中央门柱；从实际西门/前庭组织理解，不声称街路或NPC通行通过。',ground_support='parentup_west/aligned7,0,7，childdown_south/aligned1,0,2以CW90(-z,y,x)变down_west，origin9,1,6；box7..9/1..2/6..8内含无原nonair覆撞。接口与村民4,0,8finalandesiteslabtype=double保留Properties，其他村民5,0,4/6,1,2finalwood；三村民socket不等三入住。selectedhousesmedium5权2、chance2toolsmith权3/legacyrigid，旧完整上下文精确复用，新全文JSON0；Legacy/Single/Jigsaw/canAttach仅旧限定证据，未跑processor、版本升级、可选biome/根结构/道路地形或实际worldgen。')
limits=['完整新源宿主加唯一原模块研究完成，但与224低前间/前庭/厅内折阶上卧室功能骨架近族，作者HOLD0/提议0，不因尺寸、镜向、床数、实体或不重复hash加信用。','新69palette全Properties/10BE/2entities、9层99RLE1188格与8PNG实际读看；旧5palette/2BE/2层6RLE18格固定证据复用，1206源记录非1206独立world格。','source-class图非MC原纹理/碰撞，2entities不在格图渲染；主厅原air格实际有armorstand占位，不能忽略实体。门/箱盖/砧台范围/内折阶头部/薄件/NPC未验。','selectedmedium5权2/chance2toolsmith权3而非225chance1权1，完整3mod池/processor精确复用；概率未运行，旧支持JSON不算本批新读/新参考。','甲架铁盔与clock框是原实体物件，非新人物/贴图/资产修改；箱loot仅候选，无材料付款/制作交易/目标玩家回执/任务中文指南针验收，无热锻链。','南socketfinalair不等向北可通：stairs和pane保留；y0原air/叶边与Legacy忽略air不等削世界坑或地形已补。原DataVersion兼容、root/tag/townscenter/road及原生生成仍未知。','224first228/225first231/221first224/203first209与157first206不再carry，现formal0；226/229/232仍pending，233partialHOLD0/228/231HOLD0不追认。四既有chain登记只是subset，NPC累计null，COD4153/847，1000未达不制作。','只建筑本地研究和专岗证据，不做程序贴图模型主清单/生产/Jar/Git，不运行Java游戏联网UI/声音亮度焦点唤醒，不碰用户实例原档，不删未验任务，不声称全完成或工时达成。']
put('manual-review.json',dict(batch=234,case='F01_HOST_MEDIUM5_PLUS_REUSED224F04',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_HOLD0_NEAR224_FUNCTIONAL_ORGANIZATION',new_reference_proposal=0,formal_credit_added=0,native_acceptance=False,semantic_hold_reason=reason,actual_reading=dict(new_palette=69,new_BE=10,new_entities=2,new_layers=9,new_RLE_rows=99,new_positions=1188,new_PNG_viewed=8,new_full_JSON=0,old_PNG_reopened=0)))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous233_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,accepted225_first231_current234_increment=0,accepted224_first228_current234_increment=0,accepted221_first224_current234_increment=0,accepted203_first209_current234_increment=0,accepted157_first206_current234_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(active_pending_including_earlier=read(PRE/'session.json')['active_pending'],current_batch_new_pending=0,current234_whole_HOLD0=True,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current233'];now=bind(b['path']);protected.append(dict(last233_checkpoint=b,current234=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('8protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=234,status='NEW_MEDIUM5_WHOLE_HOLD0_NEAR224',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='234wholehold0.Continue previously boundedmedium8 actual originalprofession whole, not swap234hostprofessions;other4mediums no work sockets notclaimed whole.226/229/232pendingMain;no repeat oldcarry.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
