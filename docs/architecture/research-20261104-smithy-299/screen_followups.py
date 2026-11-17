import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read

def ld(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(m);inv=ld(mm['fixed_archive_inventory']['path'])
ns=['data/kaisyn/structures/village/snowy_taiga_viking/houses/snowy_taiga_butcher_1.nbt','data/kaisyn/structures/village/snowy_taiga_viking/houses/snowy_taiga_shepherd_1.nbt']
entries=[]
for n in ns:
 e=next(e for e in mm['entries']if e['member']==n);a=bind(e['source_archive']);assert a['sha256']==next(x['sha256']for x in inv['archives']if x['path']==a['path'])
 with ZipFile(a['path'])as z:raw=z.read(n);d=read(raw)
 assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256']
 pal=d['palette'];materials=dict(Counter(pal[b['state']]['Name']for b in d['blocks']));BE=[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b]
 entries.append(dict(source=dict(archive=a,member=n,raw_sha256=e['nbt_sha256']),size=d['size'],materials=materials,BE=BE,actual_reading='本批只读尺寸/材质频次/全部BE；没有全palette Properties、全层空间或PNG阅读。',new_complete_whole_studies=0,formal_credit_added=0,assessment='带smoker但litfalse/Items空/计时0，无床；屠夫工作房/动物口不能自动完成猎户夜烤火/居住。暂不重绘草顶同族。'if'butcher'in n else'loom与羊口，无炉无床；牧羊工作房不能作为猎户木屋近似参考补数。'))
old=R/'docs/architecture/research-20261101-dungeons-005/manual-review.json';e=next(x for x in ld(old)['entries']if x['id']=='F03');assert e['member']=='data/trek/structures/overworld/medium/snow_cottage.nbt'
put('bounded-followup-screen.json',dict(batch=299,task_binding=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')),task='NPC13巴图：大雪山木屋/白天猎/夜烤火/雨避',metadata=bind(m),prior298=bind(R/'docs/architecture/research-20261104-smithy-298/RECEIPT.json'),old_cottage_exclusion=dict(review=bind(old),old_complete_seven_observations_actually_read=e['observations'],old_credit=e['formal_credit_added'],further_family_record=bind(R/'docs/architecture/research-20261104-smithy-057/manual-review.json'),decision='已完整研究且旋转覆雪同族0，不重做PNG/不增加参考。'),partial_source_screens=entries,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,limits=['完整读BE不等完整建筑空间研究；上述两源不增加1000参考计数。','未穷尽固定索引全部无关键词建筑，不能称本地无更多合格来源。','不因smoker名称或litfalse状态声称夜烤火/烹饪已完成；动物口不等实际养殖/猎获材料。','只写本批研究目录，无制作/Java/游戏/网络/主清单删除。'],next='保留298作者HOLD0等待独立实际空间/相关性判定；继续优先查找不同完整组织的山地居住/猎户参考，避免小室换顶与工作房用途错配。'))
put('active-checkpoint.json',dict(batch=299,status='BOUNDED_FOLLOWUP_EXCLUSIONS_SAVED_NO_NEW_WHOLE',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,last_whole298=bind(R/'docs/architecture/research-20261104-smithy-298/RECEIPT.json'),next='继续不同且真正相近的完整山屋来源；本批3个排除项不重算。1000未达，不生产。'))
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()];put('RECEIPT.json',dict(batch=299,status='SEALED_BOUNDED_SCREEN_ONLY',files=files,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),new_whole_studies=0,formal_credit_added=0),ensure_ascii=False))
