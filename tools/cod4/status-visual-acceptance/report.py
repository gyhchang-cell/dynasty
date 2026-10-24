from pathlib import Path
import json,hashlib,html,re,collections
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/status-visual-acceptance'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected=[('run-02','yin_qi-two-entities-f80-t125.png','阴气：两实体蓝灰绕身带可辨，原生伤害红闪仍在。'),('run-02','yang_qi-two-entities-f397-t386.png','阳气：两实体金色环和竖线可辨，限帧10FPS。'),('run-02','frost_vein-two-entities-f1515-t1345.png','寒脉初始画面，需按实际姿态解读；不概括所有姿态贴合。'),('run-02','stagger-two-entities-f1946-t1797.png','破势：灰色脚下环可辨；没有证明独立踉跄/后摇动作。'),('run-02','yin-immune-day-f2282-t2039.png','至阳免疫：原生type9蓝粒子与玩家免疫状态成立；本行不要求灰字。'),('run-02','yang-immune-night-f2614-t2351.png','阴体免疫：玩家无金辉、目标有金辉，原生type9反馈；本行不要求灰字。'),('run-03','frost-fire-f902-t699.png','火：玩家剩70tick仍有冰纹；牛已先清除；两者燃烧。'),('run-03','frost-fire-f912-t745.png','火：解除后age95，两者寒脉无、速度恢复，实际冰纹消失；不是tick710首帧。'),('run-03','frost-warm-f999-t964.png','温泉：两者已提前清除，均未燃烧；玩家横躺姿态不作为直立整体贴合通过。'),('run-03','frost-cold-f1420-t1292.png','冷水：两者服务端寒脉均剩60tick，冰纹仍在；玩家横躺姿态限制。'),('run-03','frost-cold-f1511-t1332.png','冷水：到期前20tick。')]
# Resolve exact screenshot name for server tick1332 instead of inventing a serial.
fs=read(D/'run-03/frost-cold-frames.json');f=next(f for f in fs if f['tick']==1332 and f.get('screenshot'));selected[-1]=('run-03',f['screenshot'],selected[-1][2])
samples=[];audits=[];runs=[]
for run in ['run-01','run-02','run-03']:
 rd=D/run;manifest=read(rd/'manifest.json');n=0;stale=[];duplicates=[];shots=0
 for p in sorted(rd.glob('*-frames.json')):
  frames=read(p);n+=len(frames);seen=set()
  for i,f in enumerate(frames):
   ser=f['frameSerial']
   if ser in seen:duplicates.append([p.name,i,ser])
   seen.add(ser)
   if f.get('screenshot'):
    shots+=1;match=re.search(r'-f(\d+)-t(\d+)\.png$',f['screenshot'])
    if not match or tuple(map(int,match.groups()))!=(ser,f['tick']):stale.append(f['screenshot'])
 runs.append({'run':run,'jar_hashes':manifest['added_jars'],'total_mod_jars':manifest['total_mod_jars'],'loaded_mod_count':len(read(rd/'loaded-mods.json')),'exit':(rd/'exit-code.txt').read_text(),'frames':n,'screenshots':shots,'frame_files':len(list(rd.glob('*-frames.json')))})
 audits.append({'run':run,'stale_screenshot_receipts':stale,'duplicate_world_serial_rows':duplicates,'accepted_for_precise_final_report':run!='run-01'})
for run,name,note in selected:
 rd=D/run;case=re.sub(r'-f\d+-t\d+\.png$','',name);f=next(f for f in read(rd/(case+'-frames.json')) if f.get('screenshot')==name)
 es=read(rd/(case+'-events.json'));server=next((e['data'] for e in es if e['kind']=='server-tick' and e['data']['tick']==f['tick']),None)
 samples.append({'path':run+'/'+name,'sha256':sha(rd/name),'note':note,'rendered_frame':f,'native_server_same_tick':server,'events_file':run+'/'+case+'-events.json'})
raw=Path('/Users/a15356015027/Desktop/code x提示词/cod4.txt').read_text();rows=[line for line in raw.splitlines() if line.startswith('| ') and any(line.startswith('| '+k) for k in ['yin_qi ','yang_qi ','frost_vein ','stagger '])]
result={'scope':'原资产只读；隔离生产整包，原生C2S /effect 与实际火/水/magma，原生服务端事件/原生S2C/实际渲染同帧PNG。非手工调用render、非fake feedback。','runs':runs,'exact_remaining_rows':rows,'fully_closable_rows':[],
 'findings':{'yin_qi':'绕身视觉、天罡白天清除/夜间允许、脱帽和再装备正确；原生IMMUNE type9粒子存在，普通体质免疫不要求灰字。待补两TCP实际可见同步，不能因Boss灰字缺口锁此行。','yang_qi':'金辉与地煞夜间清除（包括属性）、白天允许/换装正确；原生type9反馈成立，普通体质免疫不要求灰字。待补两TCP实际可见同步。','frost_vein':'原冰纹出现；真实火及magma连通水在6秒时限前解除并有消失图；冷水只在正常截止tick1352自然到期。当前新画面为单客户端+两实体，并未完成第二TCP客户端的环境前后同帧可见验收。可收窄本地画面与服务端一致部分，保留双客户端视觉部分。','stagger':'脚下灰环可辨、减速同步；独立踉跄/后摇动作未证明，声音未录制（QA静音），不能整行关闭。'},
 'frost_reconciliation':'frost-native-reconciliation.json',
 'pose_boundary':{'observed':'warm/cold玩家呈水平姿态；alive=true、onFire=false、inWater=true、underWater=false、swimming=false、sprinting=false；原夹具没有getPose/动画控制器回执，不能反推具体动画来源。','loaded':'run03实际96mod中有notenoughanimations1.12.4、cameraoverhaul2.1.1，没有ParCool；QA没有设置Pose/绘制模型。','judgement':'水中图仅验冰纹有无及原生状态一致；不当作直立冰纹整体观感或所有姿态贴合通过。未确认产品姿态bug，不修改正式代码。'},
 'warm_environment':'run03每次fixture先clearFire/removeAllEffects，清除上轮记录blocks（含magma），重铺石底；warm原生全程未燃烧。GeothermalWater只读连通水±4水平/±3竖向/128cells下magma，与scenic_21无关。',
 'limitations':['run01失焦重复worldSerial/陈旧tick保留但不进入最终精确证据。','run02温泉继承上一轮燃烧，不作为干净温泉正例；采用run03。','run03火在tick699后到745之间没有中间世界渲染PNG；原生server-tick覆盖清除710，不宣称截图710首帧。','run03冷水末帧1352客户端属性尚旧而服务端已恢复，观测在此结束；正常自然到期，不能推断持久不同步。无需重测。','旧network49stage、ce9259基线只复用原生网络/机制：不采用旧空草地PNG证明状态视觉，不等于两名真人。','截图和native前后像素读回增加负载；10FPS是上限，非最低FPS/性能保证。'],
 'samples':samples,'production_changed':False,'todo_changed':False}
(D/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(D/'capture-quality-audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2))
lines=['四状态实际画面阶段验收（原资产只读）','生产Jar：'+runs[-1]['jar_hashes']['dynasty-1.4.0.jar'],'当前可整条关闭：0。可收窄本地阴阳绕身/换装昼夜、寒脉环境画面、破势脚下环部分。','']
for k,v in result['findings'].items():lines += [k+'：'+v]
lines += ['','寒脉：服务端tick650施加119→玩家710/牛690提前解除；warm926施加119→玩家961/牛954提前解除；cold1233施加119，1257加冷水，1292双方仍60tick，1332双方20tick，1351双方1tick，1352正常到期。','fire截图f912/t745/age95证明解除后双方速度.1/.2及冰纹消失；并非710首帧。','warm clearFire后原生全程无火，清理上轮magma并重铺石底；warm查询不依赖scenic21。',result['pose_boundary']['observed'],result['pose_boundary']['loaded'],result['pose_boundary']['judgement'],'','精确原文（保留）：']+rows+['','边界：']+result['limitations']+['','逐图：']+[x['path']+' — '+x['note'] for x in samples]+['','完整渲染回执、同tick原生记录、文件hash见acceptance.json。寒脉9对专表见frost-native-reconciliation.json。','各run manifest含实际helper/生产jarhash，run02/run03全量精确帧审计见capture-quality-audit.json。未改原清单/资产/正式Java。']
(D/'REPORT.txt').write_text('\n'.join(lines))
body=['<!doctype html><meta charset="utf-8"><title>四状态原生画面核对</title><style>body{background:#10151d;color:#eee;font:16px sans-serif;max-width:1300px;margin:auto}img{max-width:100%}section{margin:32px 0}pre{white-space:pre-wrap}a{color:#9de}</style><h1>四状态原生画面核对</h1><p>保留真实姿态、遮挡、GUI和粒子；不是几何非空即通过。详情 <a href="REPORT.txt">REPORT</a></p>']
for x in samples:body.append('<section><h2>'+html.escape(x['note'])+'</h2><p>'+html.escape(x['path'])+'</p><img loading="lazy" src="'+x['path']+'"><pre>'+html.escape(json.dumps({k:x['rendered_frame'][k] for k in ['tick','age','frameSerial','screen','geometry','nativePixelDelta']},ensure_ascii=False,indent=2))+'</pre></section>')
(D/'gallery.html').write_text('\n'.join(body));print('report written; precise final samples',len(samples));print([(a['run'],len(a['stale_screenshot_receipts']),len(a['duplicate_world_serial_rows'])) for a in audits])
