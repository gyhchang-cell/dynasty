import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
old301=R/'docs/architecture/research-20261104-smithy-301/whole-comparison.json'
err302=R/'docs/architecture/research-20261104-smithy-302/RECEIPT.json'
decisions=dict(
 cartographer=dict(original_space='9×8×7完整504格无省略。floor0/use1单层室内x2..6/z2..4约5×3，西1,1/2,3闭门；东6,1,4制图台和6,1,2西开箱，中央红白3×3地毯。2普通灯：5,3,3悬灯和4,5,2standing高盖内灯。y4北南/侧墙上birch平顶板，y5..7长x向坡盖，无梯/床/独立上层使用空间。',purpose='制图台与原village_cartographer loot箱只证小型制图作业房。不能变成NPC01铁匠铺或NPC04百宝金叫卖摊；未有锻造设备、营业界面、相应商品/店招或具体原任务职业证据。浅墙深盖和Japanese目录不能单独认中国/徽派市场资格。',family='与301的3×3方卧室/外菜地及007F04图书方室不同，当前5×3长室及长横坡确有比例/布置差别，不能武断当精确同族重复。尚未完成整栋七维/PNG审查，不提出独立参考；无指纹命中并非新设计结论。',decision='HOLD0_PURPOSE_NOT_ESTABLISHED_BEFORE_PNG_NOT_A_PROVEN_DUPLICATE'),
 fletcher=dict(original_space='9×7×9完整567格无省略。floor0/use1主房边x2..6/z2..6、净3×3，西2,1/2,4闭门，东5,1,3制箭台/5,1,5西开箱；外四墙柱x1/7,z1/7，y3宽薄檐、y4..6逐收深砖双坡盖。5悬灯=四外角y3与内4,4,4。无内梯/床/第二使用层。',purpose='真实制箭台与fletcher loot箱，不是铁匠炉或叫卖/交易库存。原任务目前没有可直接映射此制箭作业房的具体建筑要求；DUN05泛称古代商铺不足以免去中式/徽派整体资格，木墙/薄檐本身不够。',family='和301/007F04净3×3单方室、西口/东物件/四外柱有近族风险；本源全木墙、y0低基、双坡盖与301浅墙四向盖不同，不能只凭共同方室断言已经证明重复。未完成整栋七维与PNG，不给新实例信用。',decision='HOLD0_PURPOSE_NOT_ESTABLISHED_AND_FAMILY_UNRESOLVED_BEFORE_PNG'))
checks=[]
for key in ['cartographer','fletcher']:
 d=ld(P/(key+'-original.json'));pre=ld(P/(key+'-precheck.json'));pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells=0
 for layer in pre['all_layers']:
  for z,row in enumerate(layer['rows_z']):
   for x,s in enumerate(row.split()):
    b=bs.get((x,layer['y'],z));assert s==(str(b['state'])if b else'_');cells+=1
 assert pre['all_palette']==pal
 assert pre['all_BE']==[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in bs.values()if'nbt'in b]
 assert cells==pre['counts']['declared']==pre['counts']['stored'] and pre['counts']['unknown']==0
 decisions[key]['source']=pre['source'];decisions[key]['original_counts']=pre['counts']
 decisions[key]['actual_reading']=dict(full_palette_and_properties=len(pal),all_BE=3,plans=len(pre['all_layers']),rows=sum(len(v['rows_z'])for v in pre['all_layers']),all_declared_cells_or_unknown=cells,PNGs=0,complete_whole_studies=0)
 checks.append(dict(source=key,all_original_layers_states_palette_BE_match=True,declared_cells=cells,boundary='Data consistency, not semantic credit.'))
put('purpose-family-prequalification.json',dict(batch=308,decisions=decisions,old_family_reading=dict(binding=bind(old301),prior007F04_seven_dimensions=ld(old301)['prior007F04']['seven_dimensions_actually_read'],correction302=bind(err302),correction='301不是同9×9主基：主房x2..6/z2..6、柱x1/7,z1/7；旧F04外轮廓不得转成301主基尺寸。'),original_task_scope='cod2 DUN05中式徽派鬼市商铺/民宅；cod3 NPC01山脚铁匠铺、NPC04遗迹口十字路卖货摊。分别核用途，不能把任意职业台认成铁匠或卖货摊。',task_bindings=[bind(Path('/Users/a15356015027/Desktop/code x提示词')/n)for n in ['cod2.txt','cod3.txt']],limits=['两来源原数据预筛，不是两完整建筑人工研究，更不是2合格参考。','不把未证明相同称作已去重成功，也不凭namespace或工位名称强加原任务资格。','未排尽本地资料；可以待有更直接用途证据再审，当前不先画PNG补图数。','Main306已接纳有界林居空间辅助实例，信用不迁入本批；304/307独立审查状态未知，旧153/847不变，各主题累计unknown。','仅自身308写，无Java/Gradle/游戏/网络/UI/声音亮度/唤醒/焦点/用户实例/存档/Jar/专业资产/主清单/session/Git/自动化。'],PNGs=0,new_complete_whole_studies=0,formal_credit_added=0,applicable_gate_met=False,tasks_deleted=0))
put('validation.json',dict(checks=checks,new_reference_credit=0))
put('active-checkpoint.json',dict(batch=308,status='PURPOSE_UNESTABLISHED_HOLD0_BEFORE_PNG',actual_source_prechecks=2,actual_source_state_cells_read=1071,actual_palette_states_read=79,actual_BE_read=6,PNGs=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='继续找有实际用途/题材支持的完整源；先完整旧族比较，不用任意职业台凑中式建筑数。保留306 bounded接纳，307待独立审查，不重复旧图。'))
files=[bind(f)for f in sorted(P.iterdir())if f.is_file() and f.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=308,status='SEALED_TWO_ORIGINAL_SOURCE_PREQUALIFICATION_HOLD0_BEFORE_PNG',files=files,source_prechecks=2,PNGs=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,applicable_gate_met=False,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),prequalification=bind(P/'purpose-family-prequalification.json'),files=len(files),actual_full_source_prechecks=2,PNGs=0,whole_studies=0,credit=0),ensure_ascii=False))
