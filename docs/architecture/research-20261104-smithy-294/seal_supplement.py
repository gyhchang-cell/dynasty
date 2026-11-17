"""Seal same-family source supplementation; never production or new credit."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
b=ld(P/'source-binding.json');d=ld(P/'source-original.json');c=ld(P/'source-counts.json')
ck('fixed archive',bind(b['archive']['path'])==b['archive'])
with ZipFile(b['archive']['path'])as z:
 raw=z.read(b['member']);ck('exact original',hashlib.sha256(raw).hexdigest()==b['raw_sha256'] and read(raw)==d)
 for v in ld(P/'source-context.json')['resources']:
  raw=z.read(v['member']);ck('exact context '+v['member'],hashlib.sha256(raw).hexdigest()==v['sha256'] and raw.decode()==v['text'] and json.loads(raw)==v['json'])
 for v in ld(P/'variant-sources.json'):
  raw=z.read(v['member']);ck('exact variant '+v['member'],hashlib.sha256(raw).hexdigest()==v['raw_sha256'] and read(raw)==ld(v['source_json']['path']))
ck('source accounting',c['stored']==198 and c['nonair']==178 and c['air']==20 and c['omitted']==582 and c['stored']+c['omitted']==math.prod(d['size']))
ck('palette and BE',len(d['palette'])==42 and len(ld(P/'all-BE-original.json'))==6 and not d['entities'])
old=R/'docs/architecture/research-20261104-smithy-266/manual-review.json';o=ld(old)
put('prior-full-family-reading.json',dict(binding=bind(old),seven_dimensions=o['seven_dimensions'],limits=o['limits'],status=o['status'],formal_credit_added=o['formal_credit_added'],actual_current_reading='Full seven dimensions and eleven limits actually read; old images not reopened. Same whole camp family despite wood, footprint and coordinate differences.'))
m={tuple(x['pos']):d['palette'][x['state']]for x in d['blocks']}
probes=[dict(pos=[x,y,3],state=m.get((x,y,3),'OMITTED'))for y in range(4)for x in range(7)]
probes.append(dict(pos=[10,0,6],state=m.get((10,0,6),'OMITTED')))
put('actually-read-central-probes.json',dict(cells=probes,count=29,boundary='Only these selected cells individually read, not all saved198 positions.'))
ck('central fence not air',all(m[(x,y,3)]['Name']=='minecraft:oak_fence'for x in (0,6)for y in (1,2,3)))
ck('fire original grass support',m[(10,0,6)]['Name']=='minecraft:grass_block')
ck('four image files',len(list(P.glob('*.png')))==4)
status='SEALED_PRIOR215_PARTIAL_OAK_CAMP_COMPLETED_SAME_266_FAMILY_ZERO_NEW_BUILDING'
review=dict(batch=294,status=status,source=b,new_distinct_whole_buildings=0,new_complete_whole_studies=0,old_whole_family_variant_supplements=1,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,
 actual_reading=dict(images_actually_viewed=4,images=[bind(p)for p in sorted(P.glob('*.png'))],all_plan_layers_actually_viewed=6,full_height_sections_actually_viewed=2,palette_states_actually_read=42,BE_payloads_actually_read=6,context_JSON_actually_read=2,selected_coordinate_cells_actually_read=29,old266_seven_dimensions_and_eleven_limits_read=True,old273_seven_dimensions_read=True,all198_positions_individually_read=False),
 seven_dimensions=dict(
 layout='一完整商旅停驻营地，西x0..6彩毛拱棚内北三桶货储、南卧铺，东侧x8..12外置火圈与座形阶；干草和砂轮在棚外。与旧266深色木同样的货棚北货南卧/外火分区，未新增独立空间组织。棚、桶、床、火圈不拆成多个建筑。',
 proportion='13×6×10，198存储=178nonair+20air，582未存；42palette、6BE、无源实体。主体单层，y5仅屋脊五片活板；比深色木13×6×9多一排占地不构成不同设计。',
 facade='橡木阶16、活板15、栅12、半砖10配蓝16/黄10/白7羊毛；端柱及中线竖板保留，三个east_west rail和floor/west砂轮不能证明这是可驾驶商车。图中分类色与完整方块近似不等原材质和薄件碰撞。',
 roof='有盖横拱货棚，羊毛逐层收窄，y4中脊白羊毛，y5活板压脊；覆盖西货储/卧铺，东火圈露天。没有雨中保护、消防或原生遮雨验收。',
 materials='三桶(2,1,2)/(3,1,2)/(4,1,4)保留原wandering_traders/1、/3、/2及各自seed；红床头(2,1,4)/脚(3,1,4)west。营火(10,1,6)south/littrue/signalfalse，空Items和双四零计时；下(10,0,6)为真实grass_block，与旧266该处省略不同。源loot表本批未读，不称实存商品或完成交易。',
 circulation='中轴z3：x0/6,y1..3均栅栏；x1..3/5,y1是air，x4,y1为top/north/open活板，y2/3中间air。仅内部空气不能证明可从外侧平地进入。床桶前净空、火侧座阶和世界进场未原生验证，不声称NPC通行/开桶/睡觉通过。',
 ground_support='y0混合dirt19/coarse27/rooted18/grass5/path6及部分干草，不完整厚地基；582未存不能当空气/土。root WORLD_SURFACE_WG/beard_thin/start0,size1/max64；pool单一rigid/emptyprocessor。misc/full wandering_trader1..1仅配置，entities[]不保证商人生成或永久存在。'),
 family_dedup='旧215F03/F04只材料/BE预筛，今补读橡木版完整6层；旧266已完整研究深色木同族。木材归一并z偏移-1后198橡木存储格中179状态相符，仅辅助同族判断，非新颖证明。spruce只有机器对照，低匹配不意味着新建筑。旧273两大A架围公共场属另一已研究营地，不再加数。',
 applied_principles=['NPC04百宝金需要有盖货储、停驻卧铺和外火分离；实际入口必须另外验证，不能照抄端栏障碍。','可借鉴货储卧铺分区与紧凑盖宽比例，不直接复制原结构、贴图或模型。','逐层阅读前先排查旧ID键台账及同族空间布局，避免把尺寸、木材或文件差异作新参考。'],
 limits=['新增独立建筑0、合格参考0。未达到1000，不制作或删任务。','4PNG仅源类别图；原42palette/6BE和2JSON已实际阅读，198位置保存不等全部逐格读。两变体机器解析不计实看整栋。','未运行Java、游戏、loot、生成器、中文NPC/指南针或交易任务链，原生验收未通过；名称和配置不证明功能实现。','仅写294目录；旧266/273及sealed293不改，主清单/pending/ownership/session/专业资产/共享Jar不写，无音亮/唤醒/焦点/实例/存档/Git/外网操作。'],NPC_cumulative=None,all_tasks_complete=False)
put('manual-review.json',review)
protected=[]
for row in ld(P/'protected-before.json')['files']:
 before=row['before294'];after=bind(before['path']);protected.append(dict(before=before,after=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Read-only observations; concurrent edits never reverted.'))
ck('shared jar unchanged',all(x['unchanged']for x in protected if x['before']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_actually_viewed=4,new_distinct_building_credit=0,formal_credit_added=0,next='本批是旧266同族补证0；下一处先筛旧ID/全部manual及同族布局，再研究不同完整相关建筑。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,checks=checks,count=len(checks),java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=294,status=status,files=files,checks=len(checks),new_distinct_whole_buildings=0,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected)),ensure_ascii=False))
