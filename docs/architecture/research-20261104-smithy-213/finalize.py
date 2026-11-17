import json,hashlib,zipfile,itertools
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-212';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
check('size DV',n['size']==[7,15,7] and n['DataVersion']==3105)
check('counts',len(pal)==41 and len(n['blocks'])==735 and r['nonair']==165 and r['air']==570 and sum('nbt'in b for b in n['blocks'])==7 and n['entities']==[])
check('full stored volume',len(cells)==735)
check('8 actual viewed diagrams',len(list(P.glob('*.png')))==8)
expected=['All original state indices; air12; ?=omitted; rows z; columns x.']
for y in range(15):
 expected.append(f'y={y}')
 for z in range(7):expected.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}' for v,g in itertools.groupby([cells[(x,y,z)]['state'] for x in range(7)])))
check('full RLE exact original 105 rows735 positions', (P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(expected)+'\n')
check('air ladder backing lower two',all(pal[cells[(2,y,3)]['state']]['Name']=='minecraft:air' for y in [1,2]))
check('upper ladder backing thin closed top',pal[cells[(2,3,3)]['state']]['Properties']==dict(half='top',waterlogged='false',powered='false',facing='south',open='false'))
check('bed full pair supported by closed top trapdoors',all(pal[cells[(x,3,2)]['state']]['Properties']['half']=='top' for x in [3,4]))
check('high levels air10to14',all(pal[b['state']]['Name']=='minecraft:air' for b in n['blocks'] if b['pos'][1]>=10))
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:check('source member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
ctx=read(P/'source-context.json');check('three full metadata zero existing context',len(ctx['metadata'])==3 and ctx['candidates'][0]['contexts']==[])
comp=read(P/'saved-complete-family-comparison.json')
for b,c in comp.items():check('full saved judgment '+b,read(c['path'])==c['complete_saved_judgment'] and bind(c['path'])['sha256']==c['sha256'])
seven=dict(
 layout='7×7紧凑整屋：floor0/use1北侧高炉与烟炉、东南工作台，下层中央南北直通；北侧floor3/use4薄活板架承一床一桶，西南内短梯。与205高脚同族基本相同内装下移四格，无新独立工艺线或多栋。',
 proportion='7×15×7/DV3105，735全保存=165非air+570air，0省略；41palette/7BE/entities[]。15层105行735位置全部实际读，y10..14全air。有效实物到y9顶饰，15不是15经营层。',
 facade='spruce/mangrove木底框与绿陶土、混凝土粉、瓜、海绵围合，南北x3都有两格高空气缺口，边缘栅栏与阶檐；没有标准门。不把绿混合块强行解释为处理后建筑材质。',
 roof='y4外圈bottom spruce slab，y5..7混合方块渐收，y8中心east bottom spruce stair，y9中心west open in_wall spruce gate；薄檐与高饰不算可达上层。通风空隙和完整防雨未知，类色图灰色不是石屋顶。',
 materials='高炉(2,1,2)east/烟炉(4,1,2)south均litfalse、Items[]、Cook/Burn/Total0；工作台(4,1,4)。桶(2,4,2)south Items[]，绿床foot(3,4,2)/head(4,4,2)east一对，床下为closed top活板而非202的空气，明确保留差别；无砧/水/熔岩/锻造台，不称完整生产链。',
 circulation='南北x3,z0..6的y1/2均显式air，下方floor0入口边为阶/木框；到炉前中央通道可在静态表达。内梯(2,y1..3,4)south，上方(2,4,4)air；背(2,y1/2,3)air、y3为closed top薄活板，实际梯存留及上床不可证。两相邻jigsaw(6,0,5/6)均finalair，第二个指向缺失minecraft村庄池，不能当两入口两建筑。',
 ground_support='下层设备高炉/烟炉下(2/4,0,2)为stripped spruce log，工作台下(4,0,4)同为木；无205的八柱抬高四格结构。但y-1世界地面未知，入口台阶自然地形接合和保存材料重力更新未验证，不把降层变化直接记新整栋类型。')
limits=[
'实际完整读41palette、7BE、entities[]、15层105RLE/735位置；实际逐一看8PNG，全文读3metadata。未用自动计数替代人工整栋研究，图为全格类别近似，不是实机。',
'当前固定Jar全部JSON字面minecraft:village/jungle/jungle_village_7匹配0；直接引用池缺失。只限当前来源，不推断其它运行包绝无；root/biome/structureset/processor实现未读，0完整contextJSON。',
'两格梯背air、顶格薄活板，实际碰撞/邻居更新/净空/床可达/设备操作未运行；不称作者永不可用，也不冒称本项目原生验收。',
'完整202七维11限制与205七维9限制全文实际读并原样绑定复用；205高脚工作/床平台下移四格、去柱为当前关键差异，同一北设备南内梯上床组织，不够独立空间族；202是一层长室床下air，不把其缺陷偷换当前床支撑。',
'六个新机器候选只有F01完成本批整栋研究，F02..06仅指纹与来源筛查，未读其完整图/层/BE/空间。不把6件、8图、7BE或735格计6/8/7/735建筑。',
'作者HOLD0，0新合格提议/0待主审；旧157first206+1和203first209+1后续本批0，COD4153/847；NPC01/NPC05/NPC06总数未知，无1000达成。',
'无Java/游戏/网络/生产资产/共享Jar/Git/主清单/用户实例存档/声音亮度唤醒焦点改动；不删除任务、不声明全完成或主动工时。']
put('manual-review.json',dict(batch=213,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions=seven,limits=limits,status='HOLD_SAME_PLATFORM_FAMILY_AND_UNRESOLVED_LADDER_POOL_ZERO',complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(palette=41,BE=7,entities=0,layers=15,RLE_rows=105,positions=735,PNG_actual_viewed=8,full_metadata=3,full_context_JSON=0)))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous212_binding']=bind(PRE/name);d['203first209_current213_increment']=0;d['157first206_current213_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['213F01_family_ladder_pool0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current212'];now=bind(old['path']);protected.append(dict(last212_checkpoint=old,current213=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved212 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=213,status='COMPLETE_ORIGINAL_JUNGLE_WORK_HOUSE_STUDY_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Study current screened F02 source whole; preserve purpose and family gates, no production before1000.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
