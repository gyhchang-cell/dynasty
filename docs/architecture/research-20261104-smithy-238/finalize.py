import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-237';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];grid={tuple(b['pos']):b for b in n['blocks']};checks=[]
def ck(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('8x12x9 DV3465 32palette5BE entities empty',n['size']==[8,12,9]and n['DataVersion']==3465 and len(pal)==32 and sum('nbt'in b for b in n['blocks'])==5 and n['entities']==[])
ck('864declared635stored555nonair80air229omitted',len(grid)==635 and r['nonair']==555 and r['air']==80 and 864-len(grid)==229)
lines=['Original indices; -1=omitted, not air; rows z columns x.']
for y in range(12):
 lines.append(f'y={y}')
 for z in range(9):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([grid.get((x,y,z),{}).get('state',-1)for x in range(8)])))
ck('12layers108RLE864positions exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
ck('6 source-class PNG actually viewed',len(list(P.glob('*.png')))==6)
ck('original normal furnace unlit empty',pal[grid[4,3,4]['state']]['Name']=='minecraft:furnace'and pal[grid[4,3,4]['state']]['Properties']['lit']=='false'and grid[4,3,4]['nbt']['Items']==[])
ck('two full water cauldrons',all(pal[grid[q]['state']]==dict(Name='minecraft:water_cauldron',Properties=dict(level='3'))for q in [(2,3,2),(2,3,6)]))
ck('y0..2 solid saved191 not open stilts',sum(b['pos'][1]<=2 and pal[b['state']]['Name']!='minecraft:air'for b in n['blocks'])==191)
ctx=read(P/'source-context.json');rows=ctx['candidates'][0]['contexts']
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed archive and source NBT hash',bind(r['source_archive'])['sha256']==r['source_archive_sha256']and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ck('5 complete context JSON exact',len(rows)==5 and all(hashlib.sha256(z.read(x['member'])).hexdigest()==x['sha256']and json.loads(z.read(x['member']))==x['json']for x in rows))
 ck('2metadata exact',len(ctx['metadata'])==2 and all(hashlib.sha256(z.read(x['member'])).hexdigest()==x['sha256']and z.read(x['member']).decode()==x['original_text']for x in ctx['metadata']))
seven=dict(layout='一栋8×12×9西单门的单室制革作业屋，室内两口水锅在西北/西南角，偏东中未燃炉上接高墙烟柱，东南箱与北墙双stairs座。无床、内分室、平台环廊或居住层；不是候选说明中设想的架空吊脚作业屋。',proportion='DV3465/32palette/5BE/entities[]；864声明位置中635保存=555nonair80air，229省略非air。12层108RLE864位置全读，6PNG看完。floor2/use3一层，内部高至y7、上y8..11屋盖烟柱不是12层或可达阁楼。',facade='泥219/泥根172/普通红树根106为墙与基盖主体，mudbricks11构地板/烟柱；唯一mangrovedoor1,3/4,4east/right/closed，东墙两个blackpane窗，西门上0,5,4悬灯、0,6,4fence檐挂。分类灰格不当石材，根块名称不代表承托高脚。',roof='南北对称层叠收坡厚根/泥屋盖，从南北z0/8外檐收至y11/z4脊，y10的6spruce底stairs为盖脊构件。中心炉4,3,4上4,y4..8,z4泥砖wall，再4,y9/10,z4砖、y11wall盖帽；没有贯通排烟验证，不能由烟柱构形断言排气安全，亦无可上楼梯。',materials='两watercauldron2,3,2与2,3,6level3，普通炉4,3,4west/unlit且Items[]/BurnCookTotal0/RecipesUsed{}；箱5,3,6west/single/dry用village_tannery候选表、seed-7314582202936891684。无原床、brewingstand、药架、盆栽药草、炼药配方/药蛊物件或材料回执；不因水锅和未燃炉改名成熬药屋。',circulation='西接路jigsaw0,2,4west_up/aligned finalmangrovestairs[facing=east]，上0,3/4,4显式air，内1,2,4实泥支撑门；门内2/3,3/4,4air，炉西3,3/4,4air。两锅东侧3,3/4,2与3,3/4,6air，箱西4,3/4,6和箱上5,4,6air。原source图保留3个jigsaw未final模拟；道路、门、锅/箱范围、悬灯及NPC通行未验。',ground_support='y0..2有191保存非air块、屋下主体连续实泥与泥砖，不是高柱下留空/水下高脚；y-1地形未知，229省略不擅填air。两个室内vines feature口3,3,3与5,3,5finalair只装饰，不当缺失屋翼或村民。两house池均single/rigid，正常31选项本tannery权4/mossify，zombie31选项本源权2/zombify；5完整JSON/2metadata实际读。vines引用configuredfeature、vanilla_tannery代理loot、root/tag/roads/配置未重建或完整读，无Legacy忽略air假设/原生生成证明。')
limits=['完整原源整栋研究1，适用有效参考提议0/正式0：实泥基单室制革作坊不满足NPC06吊脚与熬药用途，作者HOLD0；不把沼泽名、根材、水锅或炉子当有效相关性。','新32palette全Properties/5BE/entities[]、12层108RLE864位与6PNG全读看；635保存与229省略分开，-1非air；不是864参考或12层经营层。','分类图非原材贴图/薄件/灯光/碰撞/路径/地形/性能验收，门与箱盖、锅/炉作用范围和烟柱排气未实机验。','原source3jigsaw在图中未替换；接路finalstairs有Properties，vines2口finalair不等居民或房间。single_pool不得套用旧Iberian Legacy忽略air推理，未生成/执行processor。','5mod完整JSON及2metadata全文实际读：两31选项房池、vines及2processor；普通权4/僵尸权2不能作2栋或实际概率，僵尸规则移门火把/挂网并未运行。','vines configuredfeature、根结构/biometag/roads、vanilla_tannery loot全文未读未验；候选表+seed非实际库存/素材获取/付款/任务或中文指南针回执。无炼药或居民功能。','226已237真实ACK仍待Main最终验收，235pending，236预筛0栋，229/232待审保留；旧firstcarry全0，COD4153/847，NPC累计null，1000未达不制作。','只本地建筑研究，不做生产/贴图/模型/程序/主清单，不运行Java/游戏/联网/UI/声音亮度/唤醒/焦点，不碰实例存档/共享Jar/Git，不删未验任务，不声称全部完成或主动工时。']
put('manual-review.json',dict(batch=238,case='F01_RS_SWAMP_TANNERY1',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_HOLD0_NOT_STILT_OR_ALCHEMY_RELEVANT',new_reference_proposal=0,formal_credit_added=0,native_acceptance=False,actual_reading=dict(new_palette=32,new_BE=5,new_entities=0,new_layers=12,new_RLE_rows=108,new_positions=864,new_PNG_viewed=6,new_full_JSON=5,new_metadata=2,old_PNG_reopened=0),relevance_rejected=True,global_exhaustion_claimed=False))
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current237'];now=bind(b['path']);protected.append(dict(last237_checkpoint=b,current238=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False));ck('8protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks));s=dict(batch=238,status='SWAMP_TANNERY_WHOLE_HOLD0_RELEVANCE',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='238HOLD0 because solidmudbase not stilt and tannery not alchemy;do not repeat prior wrong candidate assumption.226actualACK237awaitfinal,235pending;continue genuinely related different complete source and not generic cauldrons/ordinary housing.')
for f in ['session.json','active-checkpoint.json','latest-independent-admissions.json','carried-forward-pending.json']:put(f,{**s,'previous237_binding':bind(PRE/f),'old_accepted_carries_added':0,'not_master_todo_backup':True})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
