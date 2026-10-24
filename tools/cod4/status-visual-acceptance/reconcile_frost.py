"""Join existing native server tick records to actual rendered screenshot receipts."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3]; D=R/'docs/cod4/audit-20261022/status-visual-acceptance'; run=D/'run-03'
def load(n):return json.loads((run/n).read_text())
rows=[]
for case,ticks in {'frost-fire':[699,745],'frost-warm':[954,964],'frost-cold':[1262,1292,1332,1347,1352]}.items():
 events=load(case+'-events.json');frames=load(case+'-frames.json')
 server={e['data']['tick']:e['data'] for e in events if e['kind']=='server-tick'}
 env=[e for e in events if e['kind']=='native-environment-fixture']
 for tick in ticks:
  frame=next(f for f in frames if f['tick']==tick and f.get('screenshot'))
  assert frame['screenshot'].endswith(f"-f{frame['frameSerial']}-t{tick}.png")
  rows.append({'case':case,'server_tick':tick,'environment':env,'native_server_state':server[tick], 'rendered_frame':frame,'screenshot_sha256':hashlib.sha256((run/frame['screenshot']).read_bytes()).hexdigest()})
result={'jar':load('manifest.json')['added_jars']['dynasty-1.4.0.jar'],'method':'服务端END原生effects.duration与渲染回执按gameTime联结。不同线程同tick并非严格因果屏障，不据此承诺0帧延迟；不使用client age120结论。',
 'cold_evidence':'环境tick1257；同帧tick1262/1292/1347的服务端两实体均inWater=true/onFire=false，寒脉分别剩90/60/5tick，速度.082/.164；PNG保留冰纹。该原生记录支持未到期冷水保留。',
 'expiry_boundary':'tick1352服务端两实体effects=[]，速度恢复.1/.2；客户端同帧effects=[]但速度仍.082/.164。run03在此终止，未观测后续客户端属性同步，不能据此认定永久残留或通过属性同步。',
 'target_effect_list':'同一run内客户端Cow的effects列表从施加后一直为空，而服务端原生effect、属性以及原生Status6广播/实际渲染存在。客户端远端实体effects[]不能替代服务端剩余时间。',
 'warm_cleanliness':'run03 fixture在重新施加前clearFire；warm tick926/950/954/961/964两实体均onFire=false。warm→cold fixture删除上轮blocks（包含magma），重铺-61石地；native记录无早期解除。原run03未保存全块体/BFS快照，因此清理证据为冻结QA源码加原生效果时间线；不为正常自然到期重跑。',
 'source_rule':'GeothermalWater.warm：ServerLevel、feet真实水，连通水水平±4、竖向±3、最多128cells，只检测水下真实magma。scenic_21不是判定条件，报告不引用它为暖源。',
 'closure':'冷水未到期保留、正常自然到期成立；末帧不是错误解除。客户端属性后续传播不在该run观测时间内，不据此新增故障或重测。', 'samples':rows}
(D/'frost-native-reconciliation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('saved',len(rows),'exact screenshot/server tick pairs')
