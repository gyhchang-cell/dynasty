"""Primary complete two effect classes; missing actual producer/identity context stays0."""
from ledger import B,O
import json,hashlib,datetime
h=O/'helpers/herschel-immune/batch-050.json';d=json.loads(h.read_text());checked=[]
for row in d['rows']:
 for r in row['source_refs']:
  key,rel=r['source_key'].split('/',1);root=B/'sources'/key;raw=(root/rel).read_bytes();m=json.loads((root/'source.json').read_text());by={x['path']:x['sha256'] for x in m['files']};a,z=r['lines'];assert m['commit']==r['fixed_commit'];assert hashlib.sha256(raw).hexdigest()==by[rel]==r['file_sha256'];assert 1<=a<=z<=len(raw.decode().splitlines());assert r['url']==f'https://github.com/{m["repo"]}/blob/{m["commit"]}/{rel}#L{a}-L{z}';checked.append(r)
out={'helper_file_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'helper_original_credit':0,'main_review_new_effective':0,'main_full_classes_read':['ImmolateEffect128','AirborneEffect40'],'state':'primary_support_only_producer_and_native_consumption_pending','checked_refs':checked,'provenance_boundary':'Fixed commit/archive URL/archive metadata SHA and cached file manifest SHA checked. No cached tree, no blob/tree proof or current archive-byte rehash.','observations':[
'Immolate先EFFECT_CREDIT再addEffect，不检bool且返回新实例；DELAYED_INSTANCES以该实例weakkey记duration，但apply取entity当前实例，确切native merge/identity未展开不能保证匹配。delay守卫是!(storedDuration-staticDuration>4)才returntrue，换算差值>4才继续；singleton duration在shouldApply每次写，amp>=2才tick。无需把共享静态值直接指控运行bug。',
'真正AOE伤害前invulnerableTime0，每目标hurt true且Living才addstack/记delay，新stack准入仍未验证。目标列表来自无排除owner查询并靠friendly/LOS/距离；原afflicted也不显式排除，不能凭burst称其他目标已中。CREDIT remove在循环前，一旦执行即消费；最后不论hurt成果都FX/音且returnfalse。source三层/半径/颜色与其predicate不是独立信用。',
'Airborne全文仅server横向碰撞+水平速*10-1>0才先大坠落声、hurt(flyIntoWall,4+.5*(amp+1))、false；hurt结果忽略，类本身不加上抛速度、不写hit反馈。native effect false如何消费、真正launch producer均缺口，0。'],
'semantic_decision':'两组支持0；真实producer/instance merge/客户端消费者未补齐，不以hurt后副效/声先结果等既有家族换壳计数。已发Herschel继续其原source闭链，本岗不重复抢源。','production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'HERSCHEL-050-REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'main_new_credit':0,'ranges':len(checked)}))
