import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read

def ld(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
D=ld(P/'bounded-header-screen.json');probes=ld(P/'two-heating-columns.json');m=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(m);e=next(e for e in mm['entries']if e['member']=='data/explore_ruins_aether/structures/sky_lake_dock.nbt');a=bind(e['source_archive']);inv=ld(mm['fixed_archive_inventory']['path']);assert a['sha256']==next(v['sha256']for v in inv['archives']if v['path']==a['path'])
with ZipFile(a['path'])as z:raw=z.read(e['member']);d=read(raw)
assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256']
counts=dict(Counter(d['palette'][b['state']]['Name']for b in d['blocks']));BE=[dict(pos=b['pos'],state=d['palette'][b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b]
put('alternative-theme-bounded-screen.json',dict(task_source=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')),task='NPC15黄老汉 大江古渡口：摆渡/夜泊/雨撑篙',source=dict(archive=a,member=e['member'],raw_sha256=e['nbt_sha256'],size=d['size']),materials=counts,BE=BE,entities=d.get('entities'),reading_boundary='仅尺寸/材质频次/全部3BE/entities[]，没有全palette Properties/全层/PNG/整体动线或地形阅读。',decision='NOT_QUALIFIED_AT_THIS_SCREEN',reason='实际主体1696holystone、226aether dirt、187aether grass、285cold aercloud与天根木，加580water/3loot桶。原源异界云湖/小码头不能凭dock名作为中国大江古渡口合格整栋；源entities[]，不能声称船只/摆渡系统或泊位已验。这里只排除当前用途资格，非认定作者无其他价值。',new_complete_whole_studies=0,formal_credit_added=0))
put('bounded-gap.json',dict(batch=300,status='BOUNDED_LOCAL_PASS_NO_NEW_QUALIFIED_SHELTER_AND_WARMING_WHOLE',task_source=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')),task='NPC13巴图 大雪山木屋：居住/夜烤火/雨避',screen=bind(P/'bounded-header-screen.json'),local_heating_probes=bind(P/'two-heating-columns.json'),screened_candidate_files=36,bed_and_heating_sources=2,selected_original_cells_actually_read=29,heating_findings=['山地medium_house_4床在y1，炉4,1,4litfalse/空，y2/3石砖、y4营火四侧顶阶；无居住层可用烤火位证明。','Trek snowy_cartographer床与炉y6，炉litfalse/空，炉上y7/8墙及y9..14实石柱、y15营火四侧竖活板；不把高烟柱顶火当卧室烤火。'],decision='两个候选暂不进入完整空间研究/不计参考；其他34项没有床和所筛炉火同时存在，不因文件名而补足功能。',limits=['36是固定索引经名称/尺寸和历史exact-member初筛后的文件数，不是36个未研究完整建筑，更不是36个有效参考。','可能包含已有局部研究或ID键旧记录；例如299两工作房、旧241的baseplate类组件不能因未命中manual全文就称新整栋。','仅筛原版fire/campfire/furnace/smoker/fireplace及床命名；未覆盖全部无关键词/超尺寸/扩展自定义供暖/其他固定来源，不穷尽本地也不认定真实供暖必须littrue。','未燃炉可以有供暖设计价值，但本批没有证据证明待做NPC夜烤火已完成；烟囱顶部营火不自动满足居住层操作。','保留原始unknown；本批29所选格均STORED，未读取的邻域不填air。','既有适用参考保留，不清零；1000门槛未达，formal0，不制作/不删任务。'],alternative_topic=bind(P/'alternative-theme-bounded-screen.json'),next='在既有建筑范围继续寻找可证明真正相近的完整本地来源；本批记录缺口不把异界码头改名作中国渡口。'))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(dict(check=n,passed=True))
ck('36screened',len(D['entries'])==36)
ck('2bed_and_heating',sum(bool(e['beds']and e['heating'])for e in D['entries'])==2)
ck('29selected_cells',sum(len(v['probes'])for v in probes)==29)
ck('2columns_no_omitted_promoted',all(v['status']=='STORED'for p in probes for v in p['probes']))
ck('two_interior_furnaces_unlit_empty',all(all(f['state']['Properties']['lit']=='false'and f['nbt']['Items']==[]for f in e['features']if f['state']['Name']=='minecraft:furnace')for e in D['entries']if e['beds']and e['heating']))
ck('alternative_no_entities_3BE',d.get('entities')==[] and len(BE)==3)
put('active-checkpoint.json',dict(batch=300,status='BOUNDED_SHELTER_FIRE_GAP_AND_ALTERNATIVE_THEME_EXCLUSION_SEALED',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,last_whole298=bind(R/'docs/architecture/research-20261104-smithy-298/RECEIPT.json'),prior299=bind(R/'docs/architecture/research-20261104-smithy-299/RECEIPT.json'),gap=bind(P/'bounded-gap.json'),next='Main接收bounded缺口。继续原范围真正相关完整来源，不重绘本批组件/工作房/烟柱顶火/异界码头来加数。'))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(batch=300,status='SEALED_BOUNDED_SOURCE_SCREEN_ONLY_NO_QUALIFIED_WHOLE',files=files,data_checks=checks,checks_boundary='数据检查不等整栋/相关性/语义/原生验收。',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False,native_acceptance=False,operations='只本地Python -B/固定来源读、自身300目录写；无Java/游戏/UI/网络/主清单/session/Jar/专业旧资产改动。'))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),gap=bind(P/'bounded-gap.json'),files=len(files),data_checks=len(checks)),ensure_ascii=False))
