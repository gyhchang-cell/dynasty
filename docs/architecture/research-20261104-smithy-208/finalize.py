import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-207';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b for b in n['blocks']}
check('size DV',n['size']==[12,11,20] and n['DataVersion']==3953)
check('103palette31BEemptyentities',len(pal)==103 and sum('nbt'in b for b in n['blocks'])==31 and n['entities']==[])
check('storedair omitted',len(g)==1144 and r['air']==248 and r['nonair']==896 and 2640-len(g)==1496)
check('air9 not31',pal[9]['Name']=='minecraft:air' and pal[31]['Name']=='minecraft:oak_slab' and read(P/'original-index-rle.json')['encoding']=='12x11x20=2640; air9; -1 omitted NOT air')
for l in read(P/'original-index-rle.json')['layers']:
 check('20rows y'+str(l['y']),len(l['rows_z0_19'])==20)
 for z,row in enumerate(l['rows_z0_19']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('rawRLE y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)]['state'] if (x,l['y'],z)in g else -1 for x in range(12)])
for row in read(P/'critical-original-states.json'):
 c=tuple(row['pos']);check('critical '+str(c),row['state']==pal[g[c]['state']])
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('original memberhash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')
 for a in ctx['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],b.decode()==a['original_text'] and hashlib.sha256(b).hexdigest()==a['sha256'])
 for a in ctx['candidates'][0]['contexts']+[read(P/'literal-parent-pool.json')]:
  b=z.read(a['member']);check('context '+a['member'],json.loads(b)==a['json'] and hashlib.sha256(b).hexdigest()==a['sha256'])
check('literal parent not current selectedpool',all(e.get('element',{}).get('location')!='trek:village/swamp/houses/swamp_medium_house_1' for e in read(P/'literal-parent-pool.json')['json']['elements']))
check('no ladder no alchemy heatwork',not any(s['Name'] in ['minecraft:ladder','minecraft:brewing_stand','minecraft:cauldron','minecraft:furnace','minecraft:smoker','minecraft:blast_furnace'] for s in pal))
check('7png individually viewed',len(list(P.glob('*.png')))==7)
old=read(P.parent/'research-20261104-smithy-206/manual-review.json')
put('saved-complete-family-comparison.json',dict(binding206=bind(P.parent/'research-20261104-smithy-206/manual-review.json'),full206=old,current_comparison='206低双门储物室接东高双锅平台并有大交接屋盖；当前两间同floor3/use4卧室以弯折外廊连接，两小阁内高箱无楼板/梯，不是206上下工作高差。共同木构沼泽题材只作空间学习，当前无熬药/瓶罐工作区、支柱池未闭合，保留NPC06用途适用性HOLD0，不据两个卧室拆成2参考。',old_NBT_PNG_reopened=False,current_credit=0))
put('manual-review.json',dict(batch=208,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'完整一组双卧室与外廊：northwest木墙屋位x1..7/z1..7，southeast泥砖屋位x4..10/z12..18，均floor3/use4，各两床；外廊从southwest低入口爬至西侧并弯折连接北屋东门。两独立盖仍一个同NBT空间组，不拆两屋/床/高箱。无炼药区，不直接当黑婆现成居所。',
'proportion':'12×11×20 DV3953，2640声明=1144保存(896非air248显式air)+1496省略。103palette/31BE/entities[]；全11层220RLE/2640位和7PNG实际读看。实际居住使用4，高箱在7不是完整二层；11高非11层。',
'facade':'north木板/去皮橡木夹原木框、south泥砖墙，玻璃pane/藤/薄活板/栅门/灯点装饰。north东门7,4/5,3east/left/closed，south西门4,4/5,14west/right/closed；外廊欄不是室内连廊，原空牌不作中文营业说明。',
'roof':'north与south各一组木板/阶/半砖混合偏置屋盖，y8侧出宽檐，y9/10收拢并延长交错脊边。高箱north6,7,6/south5,7,16下方为closed TOP活板，周边无连续完整二层楼板且全palette无梯；不把高箱投影当可经营阁楼或已验可达储层。',
'materials':'两红床head2,4,z2/4与foot3,4,z2/4朝west；两浅蓝床foot8,4,z15/17与head9,4,z15/17朝east，床下保存TOP圆石/苔圆石slab。4箱原swamp_house loot及seed全部保留，两个空木牌、8床BE、17接头合计31BE。无炉/锅/酿药台/梯，不定义熬药工序或供材付款。',
'circulation':'southwest入口3,1,18north底oak阶→3,2,17同向阶→3,3,16同向阶→3,3,15TOPoakslab/上3,4,15air，旁south屋west门4,4/5,14。外廊另弯向north屋east门7,4/5,3，外侧8,3,3TOPoakslab/上8,4,3air；连接区域半砖/活板/栅门状态保留，不能把整廊写全air或已验NPC路径。两处高箱无原源连续梯链，不推自动取物。',
'ground_support':'两屋楼板y3，y0/1大部分省略且只在southwest有少量土/入口。13个向下接头指trek:feature/block_column/oak_log，finalstructure_void，两个居民接头finalTOP圆石/苔圆石slab；原包缺下延柱池，不能把当前类色图虚接地当自然水位/支柱生成已验。实体木框支持局部楼板不等柱底已落自然地基。'},limits=[
'完整103palette/31BE/entities[]、11层220RLE2640位、7PNG实际读看。3metadata绑定与刚实际全文读的207相同，在当前原包逐字/哈希核验复用；不伪称重复新来源。',
'实际完整context为居民池/房loot2JSON。另完整读swamp_vanilla/houses共27候选，因仅名称子串匹配、location不等当前swamp/houses，明确排除当前选择池/处理器闭环，不算27建筑或当前第3依赖。',
'原source root/startpool/biome/structureset没有当前精确命中；缺柱池、居民nitwit/baby/unemployed三个NBT未读，不能宣生成自然地形/水位/村民/黑婆已验。',
'居民池权1/1/10 rigid/empty，仅说明作者生成接口；原entities[]不代表无居民生成，也不把村民当黑婆或任务ID。',
'loot 3..8均匀rolls铁粒/蓝兰/slime/vine/bread/apple/book/lilypad/emerald/seagrass原概率与random_sequence拼写vilage原样保留；未出货付款/拾取/中文任务/指南针验收。',
'地面入口三阶/门状态只是静态布局，薄活板/栏门/床基础slab/屋盖碰撞净空与NPC开门爬行、防坠雨险/当前DV兼容均未运行。',
'与206完整七维/9限制原样保存；当前双卧外廊不能靠水乡题材或两个屋盖获得新合格信用。NPC06熬药用途相关性和支柱依赖仍保留HOLD0，不提新whole待审。',
'157W01仅206首次NPC05+1本208+0，203真实ACK207已交Main但未最终接受仍0。197/190等旧接受后续0，182HOLD/064不追认，COD4153/847不变、NPC01/05/06累计未知，适用1000未达。',
'无Java/游戏/网络/声音亮度唤醒/用户实例原档/专业资产/共享Jar/Git/主清单写入，不删除未验任务或声称全部完成/工时达标。'],actual_reading=dict(palette=103,BE=31,entities=0,layers=11,RLE_rows=220,positions=2640,PNG_actual_viewed=7,metadata_verified_reused_full=3,current_full_context_JSON=2,other_parent_full_JSON_excluded=1),complete_original_spatial_study=True,status='WHOLE_SOURCE_NPC06_APPLICABILITY_SUPPORT_CONTEXT_HOLD_ZERO',new_reference_proposal=0,formal_credit_added=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous207_binding']=bind(PRE/name);d['157W01_first206_current208_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['208F01_NPC06_full_study_HOLD0']=dict(increment=0,new_pending=0)
 put(name,d)
check('203 pending only',[(a['batch'],a['id']) for a in read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']]==[(203,'F02')])
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current207'];now=bind(oldbind['path']);protected.append(dict(last207_checkpoint=oldbind,current208=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved207 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True,local_encoding_header_correction='Initial unsealed RLE generation header said air31 by typo; actual source palette read established air9/oakslab31 and header corrected BEFORE actual RLE reading. All220rows independently checked against original saved states. No source asset change.'))
s=dict(batch=208,status='WHOLE_SWAMP_DOUBLE_DWELLING_HOLD_ZERO',formal_credit_added=0,accepted157_first206_current_increment=0,case203_current_increment=0,active_pending=['203F02'],new_qualifying_reference_proposals=0,new_complete_whole_studies=1,palette=103,BE=31,entities=0,layers=11,RLE_rows=220,positions=2640,PNG_actual_viewed=7,metadata_full_verified_reused=3,current_full_context_JSON=2,other_parent_JSON_full_excluded=1,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Continue fresh related sources F02medium2/F03small5 screened208 but NBT/PNG not inspected; complete structure/semantic study before any credit. 203 final Main decision pending,157first206later0. No production or checklist deletion before gates.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
