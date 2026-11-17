import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-231'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
def st(q):return pal[cells[q]['state']]
ck('newsource exactscreen eligible',read(P/'pre-render-history-screen.json')['rows'][0]['eligible_for_new_source_study'])
ck('16x27x15 DV3120 55palette8BE0entities',n['size']==[16,27,15]and n['DataVersion']==3120 and len(pal)==55 and sum('nbt'in b for b in n['blocks'])==8 and n['entities']==[])
ck('6480stored1056nonair5424air',len(cells)==6480 and r['nonair']==1056 and r['air']==5424)
lines=['Original palette-index RLE; rows z, columns x; all source positions stored.']
for y in range(27):
 lines.append(f'y={y}')
 for z in range(15):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([cells[(x,y,z)]['state']for x in range(16)])))
ck('27layers405RLE exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
ck('10newPNG actually viewed',len(list(P.glob('*.png')))==10)
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed Jar and selected member exact',bind(r['source_archive'])['sha256']==r['source_archive_sha256']and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')['candidates'][0]['contexts'];ck('6 full current modcontexts exact',len(ctx)==6 and all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
v=read(P/'vanilla-fletcher-support.json')
with zipfile.ZipFile(v['archive']['path'])as z:ck('onefullnestedvanillaloot exact',bind(v['archive']['path'])==v['archive']and hashlib.sha256(z.read(v['member'])).hexdigest()==v['sha256'])
ck('worktable and eight thincarpets',st((7,16,5))['Name']=='minecraft:fletching_table'and r['material_counts']['minecraft:cyan_carpet']==8)
ck('chestpair remain single north',all(st((x,16,9))['Name']=='minecraft:chest'and st((x,16,9))['Properties']['type']=='single'and st((x,16,9))['Properties']['facing']=='north'for x in [2,3]))
ck('five original jigsaw 2bridge2villager1deco',r['material_counts']['minecraft:jigsaw']==5)
ck('fence barrier not clear central throughroute',st((7,16,9))['Name']=='minecraft:dark_oak_fence')
rocket=cells[(7,17,13)]['nbt']['Items'];ck('up dispenser nine explicit rockets untriggered',st((7,17,13))['Properties']==dict(triggered='false',facing='up')and len(rocket)==9 and all(x['Slot']==i and x['id']=='minecraft:firework_rocket'and x['Count']==1 for i,x in enumerate(rocket)))
ck('target power0 north facing jackolantern above',st((7,17,12))['Properties']['power']=='0'and st((7,18,12))['Name']=='minecraft:jack_o_lantern')
comparisons=[]
for num in [65,186]:
 f=P.parent/f'research-20261104-smithy-{num:03d}/manual-review.json';o=read(f)
 for c in o['cases']:
  if c.get('member','').startswith('data/skyvillages/'):
   comparisons.append(dict(binding=bind(f),case=c['id'],member=c['member'],complete_saved_seven_dimensions=c['observations'],original_case_status=c.get('status'),original_family_review=c.get('family_review'),old_NBT_or_PNG_reopened=False))
reason='本原fletcher整岛上是八柱单长坡开敞棚：北/西两桥口导入中央制箭台，西南并排双单箱，横向栅栏将后南靶/发射器展示区与前作业区分开。065F01是四向桥口中央岩浆/锻造台环行热棚，065F02是封闭双床/内短梯箱与外L砧磨平台，186F04是南北公共走道分开西生活屋与东切石场。本项可借鉴装备辅助作业/储备/定向测试空间关系，而非仅职业设备/紫色坡盖/浮岛换装；仅最多1相关NPC01辅助武备工棚提案待Main，不能叫铁匠热锻或已验证制箭/测试链。'
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,maximum_proposal=1,formal_credit_added=0,no_exhaustive_semantic_catalogue_claim=True))
seven=dict(layout='单源完整石岛、八quartz柱长盖开敞武备工棚与侧草坡/树；北与西桥口进入前中工作区，中央7,16,5fletching_table与环周8青地毯，西南2/3,16,9并排单箱，y16,z9横栅把南靶/发射器区分出。无床/门/封闭生活室/上楼，不能因岛基、两箱、靶或屋盖拆成多栋。',proportion='16×27×15/DV3120，全6480存1056非air5424air无省略；55palette/8BE/entities[]、27层405RLE和10PNG全读。0..14主要收尖石岛，floor15/use16主要工作地，南侧草台有局部更高层，roof21..25，26全air，不是27层。原五jigsaw仍magenta未final/未实际装配，1056为源nonair非生成成品。',facade='49quartzpillar以x4/10,z2/5/9/12八柱承长盖，外围开敞无玻璃门；西南低栏/两单箱、东侧草坡与树作区分。原quartzbricks25/抛光闪长20/闪长9作白边，在分类图可能棕红，purple30/magenta46原紫彩陶盖图灰，不把分类色当真实纹理。',roof='长南北双坡由两侧y21白材宽边、y22紫陶/倒acaciastair、y23/24收窄紫红陶及去皮acacia横梁，至y25单脊/中央glowstone7,25,7。四对柱承同一盖，八柱不是八间，脊下无楼面梯；东树叶/树干至24是环境不是高经营层。',materials='641stone岛底主材；中央fletchingtable只是原作业点，不凭名称断言玩家可在此打开制箭GUI/执行配方。两north/type single/dry箱有同fletcherloot但不同seed8317039092517924108与-5639013093427397447，嵌套vanillaloot候选emerald/arrow/feather/egg/flint/stick非实存或付款材料。南target7,17,12power0、上7,18,12northjackolantern；后7,17,13updispenser triggeredfalse，原9槽各1rocket已逐项读，但未放入实际世界或触发。无炉/lava/砧/锻造台/磨石，不编热锻或熔炼链。',circulation='原北bridge7,15,0和西0,15,7都finalspruceplanks；内7,16/17,1及1,16/17,7air。中央台7,16,5周北7,16,4/东西6和8,16,5/南7,16,6是cyan_carpet非air，上17air，只静态薄件关系。两箱north前2/3,16/17,8air且箱顶2/3,17,9air。向南7,16,9darkoakfence确实阻开敞直线，7,16/17,10..11air不等前后可连续步行；靶7,17,12下7,16,12bottomsouthdarkstairs、后发射器下7,16,13topnorthstairs，有高低差与围栏/草坡，未证明绕栏路线、射击或触发回路、箱盖/台范围/NPC通过。',ground_support='单NBT含收尖完整石岛与floor15作业铺地，不以省略格补空（全存）。两个roll bridge方向west_up/north_upfinalwood、两个roll村民up_west/up_eastfinalair和东decosocketfinalair，池配置不等居民/装饰实到。houses选中weight50/single_pool_element/rigid，不能套用Legacy忽略air为本源清除规则；本批不重读/运行引擎。houseprocessor原stone→diorite0.2后stone→diamond0.005/emerald0.05和wheat作物替换未执行，不算矿石实产或相加概率。桥/兼容屋/装饰资源及root/tag/实际worldgen未完整重建，不把浮岛当已适配山脚地基。')
limits=['一整座原制箭武备辅助工棚最多提NPC01相关参考1，Main尚未独立相关性/近族验收，本批formal0；不是全套铁匠铺，不按设备/桥口/岛基/截图加数。','当前全55palette/8BE/完整entities[]、27层405RLE6480格、10PNG、6mod+1vanillaloot全文实际读；历史缓存只排exact，不保证全库语义唯一；旧065/186仅完整已写七维复用不重开旧NBT/PNG。','源图分类块非原MC纹理/碰撞，1056源nonair含五jigsaw未替换，不等native世界数；紫陶/石英砖材料与灰棕分类色严格区分。','环台carpet与南横fence均nonair；箱顶/脚头air不证明原生可达/可开；高低草台、靶、发射器及薄阶/栏/台范围/NPC未验，不承诺连续制箭→测试回路。','两箱仅有lootseed候选，原发射器9rocket为源NBT显式物品，不等玩家获取/交易付款；未触发、无音效/实体/游戏；不把工作站名编成玩家配方GUI或任务指南针接入。','实际single/rigid不套Legacy忽略air；houseprocessor与矿石/作物替换未运行，root/tag/桥网/兼容资源/版本升级和浮岛接地未native验，本地固定Jar不证远端最新。','另被动整理203/221/224/225四条既有Main最终+首次carry链，登记增量0/历史subset4非累计数，NPC总仍null；225仅first231、224first228、221first224、203first209以后0，157NPC05不混入。226/229继续pending、228/231HOLD0，COD4153/847及1000未达状态不变。','只建筑本地参考研究与专岗记录，不做程序贴图模型主清单，不运行Java/游戏/联网/UI/声音亮度焦点唤醒，不碰实例原档共享Jar专业资产Git，不删除未验任务，不声称全部完成或工时。']
put('manual-review.json',dict(batch=232,case='F01_SKY_FLETCHER1',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_MAX1_NPC01_EQUIPMENT_SUPPORT_PENDING_MAIN',new_reference_proposal=1,formal_credit_added=0,native_acceptance=False,semantic_judgment=reason,actual_reading=dict(new_palette=55,new_BE=8,new_entities=0,new_layers=27,new_RLE_rows=405,new_positions=6480,new_PNG_viewed=10,current_full_mod_JSON=6,current_full_vanilla_JSON=1,old_PNG_reopened=0)))
reg=read(P/'existing-NPC01-final-firstcarry-register.json');ck('existing register4 unique whole identities not newcredit',len(reg['rows'])==4 and reg['formal_increment']==0 and reg['NPC01_cumulative_total']is None)
f=ROOT/'docs/cod4/audit-20261022/coordinator-architecture225-first231-actual-carry-review-20261111.json';ck('Main first231 passive receipt fixed',bind(f)['sha256']=='0d5ba68e2eac094b93a515ede02afdab7752a521fad730438da99641ddec1a81'and bind(f)['bytes']==1125)
put('Main-first231-carry-review-reused.json',dict(binding=bind(f),entire_object=read(f),increment=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous231_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,accepted225_first231_current232_increment=0,accepted224_first228_current232_increment=0,accepted221_first224_current232_increment=0,accepted203_first209_current232_increment=0,accepted157_first206_current232_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,passive_existing_registry_binding=bind(P/'existing-NPC01-final-firstcarry-register.json'))
 if name.startswith('carried'):o.update(active_pending_including_earlier=['226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1','232F01_SKY_FLETCHER1'],current_batch_new_pending=1,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current231'];now=bind(b['path']);protected.append(dict(last231_checkpoint=b,current232=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('8protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=232,status='NEW_SKY_FLETCHER_WHOLE_MAX1_PENDING_AND_PASSIVE_EXISTING4_REGISTER0',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=1,existing_registered_chain_subset=4,registry_increment=0,active_pending=['226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1','232F01_SKY_FLETCHER1'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue genuinely related complete organization.232 auxiliary gearwork proposal pendingMain;226/229 pending. Existing register subset4 zero newcredit not total;225first231/224first228/221first224/203first209 later0.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
