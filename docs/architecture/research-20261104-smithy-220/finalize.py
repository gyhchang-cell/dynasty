import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-219';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];c={tuple(b['pos']):b for b in n['blocks']}
ck('8 exact fresh leads no semantic credit',len(read(P/'pre-render-history-screen.json')['rows'])==8)
ck('F08 full component size DV',r['id']=='F08'and n['size']==[5,12,5]and n['DataVersion']==3105)
ck('31 palette 300 stored 200air100nonair',len(pal)==31 and len(c)==300 and r['air']==200 and r['nonair']==100)
ck('three BE zero source entities',sum('nbt'in b for b in n['blocks'])==3 and not n['entities'])
ck('7 actual viewed diagrams',len(list(P.glob('*.png')))==7)
ck('full60 RLE rows',sum(a.startswith('z')for a in(P/'F08-full-layer-index-rle.txt').read_text().splitlines())==60)
ck('no continuous independently grounded roof support',all(pal[c[(3,y,2)]['state']]['Name']in ['minecraft:chain','minecraft:stone_brick_wall','minecraft:grindstone']for y in range(4,8)) and pal[c[(3,3,2)]['state']]['Name']=='minecraft:air')
with zipfile.ZipFile(r['source_archive'])as z:ck('original archive and member fixed',bind(r['source_archive'])['sha256']==r['source_archive_sha256']and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
put('manual-review.json',dict(batch=220,status='COMPLETE_COMPONENT_READING_NOT_COMPLETE_BUILDING_ZERO',complete_original_spatial_study=False,full_component_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(full_component_palette=31,full_BE=3,full_entities=0,full_component_layers=12,RLE_rows=60,component_positions=300,PNG_viewed=7,full_direct_JSON=1,new_full_metadata=0),component_observations=dict(layout='5×12×5职业插入件：底木板/andesite台，west箱(1,1,1)，west两组andesite阶装饰，east封闭lava坑(3,2,2)；无独立出入口墙/床/原料间。',proportion='300全stored=100非air+200air、31palette、3BE、0entity；有效最高非air8，9..11全air，12高不是12层。',facade='底平台木+andesite/stonebrickwall炉台，开放周边，north/south细墙断柱不构成整栋围护。',roof='y7双砖檐/顶slab带，y8砖/双graniteslab脊；middle2行chain从高盖垂下，一列终lanterny4，另一列终ceilinggrindstoney4并接wall5，后者y3air无落地柱。不能把悬挂设备误认完整亭的结构。',materials='lava(3,2,2)level0，grindstone(3,4,2)east/ceiling在(3,5,2)wall下；west箱1,1,1有原vanilla weaponsmithlootseed6224733400003303762，来源是候选不是取得回执。',circulation='西x0,y1/2,z1显式air通箱west，x0,y1/2,z2/3air靠装饰台；y3原villagerjigsaw(2,3,3)finalair未实际放置，服务站位需主建筑约束；高grindstone未验交互距离/熔岩安全。',ground='下接口(2,0,2)down_west/name&targetminecraft:bottom/empty/finalandesite表示可被主房接口引用；上villagers池缺失。独立全图不能证明落地屋盖，必须取原始宿主整栋关系。'),limits=['前4大候选仅机器设备抽取及有界阅读；初次长设备输出被截断，不声称其631palette/331BE/全实体或全图已读。F01/02巨大cottage53×62×62含众敌与两药台，当前只读指定2smith/caldron/2brew条；不是整栋完成。', 'F03 generic5三炉+food箱偏生活厨房，F04 genericbig1双炉+generic箱，缺明确锻造/炼药/磨坊证据，未展开全栋不加数。', 'F05..07 Iberian各3×2×3是职业设备片，不是三完整建筑；仅尺寸/设备名机器摘要，未声称全BE/图已读。', 'F08原misc池12职业各weight1/legacy_single/rigid/emptyprocessor，自fallback；仅该池全文读。vanilla weaponsmithloot与villagerspool两依赖当前jar缺，不当完整生成链。', 'F08完整31palette/3BE/12层60RLE/7PNG实际读看，但只是组件0，不提议独立整栋；新发现同源未读host rustic_barn_professions_1为11×14×10，下一批先原接口闭合再谈整栋。', 'COD4153/847，NPC01/05/06总数未知；157first206及203first209本批0。无Java/游戏/网络/生产/Jar/清单/声音亮度焦点变动，不删任务。']))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous219_binding']=bind(PRE/name);d['203first209_current220_increment']=0;d['157first206_current220_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[]
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current219'];now=bind(old['path']);protected.append(dict(last219_checkpoint=old,current220=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved219 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True));put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=220,status='COMPLETE_RUSTIC_WEAPON_COMPONENT_STUDY_ZERO_NOT_WHOLE',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged']for a in protected),next='Resolve original unstudied rustic_barn_professions_1 host and F08 connector/pool into one allowed whole; reuse exact component observations, never count component alone or add variants as separate buildings.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
