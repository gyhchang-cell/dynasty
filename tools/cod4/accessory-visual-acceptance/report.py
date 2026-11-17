"""Audit unchanged production cues, join actual TCP receipts, and index raw screenshots."""
from pathlib import Path
import json,hashlib,re,html,collections
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/accessory-visual-acceptance'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=['jade_cicada','jade_bi_disc','moon_pendant','qilin_horn_charm','silk_pouch','jade_pendant','gold_seal_charm','dragon_scale_charm','phoenix_feather_charm','fox_tail_charm']
notes={
'jade_cicada':'浅青双对蝉翼与中心小体在背部可辨；tick167展开、tick170合拢，绿色回血粒子叠加仍能辨翼形。',
'jade_bi_disc':'肩侧细青圆环及中央菱形可辨；本机正面受肩膀局部遮挡，旁观背面圆环完整。',
'moon_pendant':'肩侧白色缺口弧与两小星可辨；本机肩膀局部遮挡合理，不声称全方向完整可见。',
'qilin_horn_charm':'头两侧淡金分叉角可辨；中间小点被头遮住，没有改为穿透渲染。',
'silk_pouch':'腹前紫色交织线纹与上下收口线可辨；从背部看不到正面图案符合深度遮挡，采用补拍正面图。',
'jade_pendant':'胸前青菱形与两侧折线可辨，原版受击红闪/相机倾斜保留。',
'gold_seal_charm':'胸前金方印与内横竖笔画可辨，首获功名粒子在脚下，未把通用粒子当独立印。',
'dragon_scale_charm':'胸前三片浅青鳞片与上方折线可辨；旁边龙王原生光带/粒子有透明重叠，局部对比减弱，仍可辨本体。',
'phoenix_feather_charm':'后颈五根短橙羽可辨；本机反复触火时火焰颜色重叠明显，旁观清火后较清楚，不宣称火焰内始终清晰。',
'fox_tail_charm':'腰背三条紫色弯曲尾迹可辨，受击红闪与摆动同时保留；是现有有限几何提示，不是新尾巴模型。'}
triggers={'jade_cicada':'原低血量条件→EquipmentBehaviors原生tick一次回血；QA仅装备并把血量置20%。','jade_bi_disc':'原周期tick；白天装备后真实C2S time set night。','moon_pendant':'原周期tick；白天装备后真实C2S time set night。','qilin_horn_charm':'原已装备条件下的周期tick。','silk_pouch':'原已装备条件下的周期tick。','jade_pendant':'原25%低血量，真实Zombie.doHurtTarget→原LivingHurt事件。','gold_seal_charm':'真实ItemEntity玉掉落与玩家拾取→原首次获得功名路径。','dragon_scale_charm':'真实MultiPlayerGameMode.attack原生C2S→真实龙王LivingHurt。','phoenix_feather_charm':'脚下真实火方块→原火伤免疫路径；撤装后火伤恢复。','fox_tail_charm':'真实Zombie.doHurtTarget 50次，原RNG自然成功6次；不改随机、不清伤害无敌帧。'}
source_runs={i:('run-04' if i=='silk_pouch' else 'run-03' if i in ['jade_pendant','gold_seal_charm','dragon_scale_charm'] else 'run-02') for i in items}
# These are actual selected and independently viewable raw frames; fallback selection is explicitly review-needed.
chosen={
'jade_cicada':('jade_cicada-native-f120-t164.png','jade_cicada-native-f61-t167.png'),
'jade_bi_disc':('jade_bi_disc-native-f487-t483.png','jade_bi_disc-native-f446-t483.png'),
'moon_pendant':('moon_pendant-native-f718-t723.png','moon_pendant-native-f724-t723.png'),
'qilin_horn_charm':('qilin_horn_charm-native-f950-t963.png','qilin_horn_charm-native-f1000-t963.png'),
'jade_pendant':('jade_pendant-native-f396-t380.png',None),
'gold_seal_charm':('gold_seal_charm-native-f644-t612.png',None),
'dragon_scale_charm':('dragon_scale_charm-native-f895-t857.png',None),
'phoenix_feather_charm':('phoenix_feather_charm-native-f2319-t2420.png','phoenix_feather_charm-native-f2648-t2424.png'),
'fox_tail_charm':('fox_tail_charm-native-f3211-t3268.png','fox_tail_charm-native-f3549-t3267.png')}
audits=[];runs=[]
for name in ['run-02','run-02-peer','run-03','run-03-peer','run-04','run-04-peer']:
 rd=D/name
 if not (rd/'FINISHED.json').exists():continue
 m=read(rd/'manifest.json');frames=shots=0;stale=[];duplicate=[]
 for p in rd.glob('*-frames.json'):
  seen=set()
  for f in read(p):
   frames+=1
   if f['frameSerial'] in seen:duplicate.append([p.name,f['frameSerial']])
   seen.add(f['frameSerial'])
   if f.get('screenshot'):
    shots+=1;match=re.search(r'-f(\d+)-t(\d+)\.png$',f['screenshot'])
    if not match or tuple(map(int,match.groups()))!=(f['frameSerial'],f['tick']):stale.append(f['screenshot'])
 audits.append({'run':name,'frames':frames,'screenshots':shots,'stale_receipts':stale,'duplicate_world_serial':duplicate})
 runs.append({'run':name,'instance':m['instance'],'jars':m['added_jars'],'mod_jars':m['total_mod_jars'],'exit':(rd/'exit-code.txt').read_text() if (rd/'exit-code.txt').exists() else 'pending'})
cases=[];samples=[]
for item in items:
 run=source_runs[item];n=item+'-native';rd=D/run;pd=D/(run+'-peer')
 if not all((x/(n+'-result.json')).exists() for x in [rd,pd]):continue
 events=read(rd/(n+'-events.json'));pe=read(pd/(n+'-events.json'));seq='equipment_accessory_'+item
 hw=[e['data'] for e in events if e['kind']=='actual-s2c-handle' and e['data']['sequence']==seq];pw=[e['data'] for e in pe if e['kind']=='actual-s2c-handle' and e['data']['sequence']==seq]
 hf=read(rd/(n+'-frames.json'));pf=read(pd/(n+'-frames.json'));hostid=hf[0]['player']['id'];peerid=pf[-1]['selfId']
 assert hostid!=peerid and hw==pw and hw and all(w['entity']==hostid for w in hw)
 record={'item':item,'run':run,'native_trigger':triggers[item],'visual_review':notes[item],'host_entity_id':hostid,'peer_self_id':peerid,'native_cue_packets_identical_both_clients':True,'native_packets':hw,'events_counts':dict(collections.Counter(e['kind'] for e in events)),'sides':{}}
 for side,folder,frames in [('host',run,hf),('peer',run+'-peer',pf)]:
  geom=[f for f in frames if 'Accessory:'+item in f['geometry']]
  assert geom and all(any(w['start']<=f['tick']<w['start']+w['duration'] for w in hw) for f in geom)
  assert not frames[-1]['geometry']
  shots=[f for f in geom if f.get('screenshot') and f['nativePixelDelta'].get('Cod3Vfx',{}).get('changedPixels',0)>0]
  selection=chosen.get(item,(None,None))[side=='peer']; f=next((f for f in shots if f['screenshot']==selection),None)
  if f is None and shots:f=shots[min(2,len(shots)-1)]
  record['sides'][side]={'frames':len(frames),'visual_frames':len(geom),'visible_pixel_screenshots':len(shots),'actual_visible_window':[min(f['tick'] for f in geom),max(f['tick'] for f in geom)],'no_accessory_geometry_at_end':frames[-1]['tick'],'selected':f['screenshot'] if f else None,'rendered_pixels_range':[min([f['nativePixelDelta']['Cod3Vfx']['changedPixels'] for f in geom if 'Cod3Vfx' in f['nativePixelDelta']],default=0),max([f['nativePixelDelta']['Cod3Vfx']['changedPixels'] for f in geom if 'Cod3Vfx' in f['nativePixelDelta']],default=0)]}
  if f:
   path=folder+'/'+f['screenshot'];native=next((e['data'] for e in events if e['kind']=='server-tick' and e['data']['tick']==f['tick']),None)
   samples.append({'item':item,'side':side,'path':path,'sha256':sha(D/path),'note':notes[item],'frame':f,'native_server_same_tick':native})
 record['both_views_have_actual_visible_screenshots']=all(s['visible_pixel_screenshots'] for s in record['sides'].values());cases.append(record)
raw=Path('/Users/a15356015027/Desktop/code x提示词/cod4.txt').read_text();rows=[x for x in raw.splitlines() if x.startswith('[ ] jade_pendant /') or x.startswith('[ ] jade_cicada ')]
# Report only facts; finalized review file is a separate explicit manual receipt.
reviewed=D/'visual-review.json';manual=read(reviewed) if reviewed.exists() else {}
all_good=len(cases)==10 and all(c['both_views_have_actual_visible_screenshots'] for c in cases)
fullrows=[x for x in rows if ('jade_cicada 玉蝉' in x and manual.get('cicada_pass')) or ('jade_pendant /' in x and all_good and manual.get('nine_patterns_pass'))]
limits=['两套真实生产整包Java客户端+TCP LAN、离线QA身份；不是两名真人，非真实公网延迟认证。','本机host为佩戴者，peer为空装旁观者；本矩阵验原生反馈entityId归属和两端可见，不覆盖同时多佩戴者/死亡重生/32边界/多人AOE。相关机制由协调其他验收保留。','装备/血量/掉落/敌对目标由QA夹具设置；Curios GUI拖放、自然获取、正常生存难度不在范围。','本机生命5000且抗击退用于稳定镜头；OverflowingBars在位，未删除模组、HUD、原始粒子或资产。','截图含原生伤害数字、火焰、龙王光带、聊天和提示窗；所有方向都清楚不作保证。像素读回增加负载，30FPS为上限，非性能认证。','run02 peer离线UUID采用错误命名空间算法产生FTB Teams已知玩家警告；host entity1实际广播与两端入镜/归属成立，不能借此宣称FTB通过。run03/04私有launcher改为原生OfflinePlayer名称MD5 UUID，未动正式FTB内容。','run02四个正面本机视角被旁观者站在相机处遮住，零像素，保留负例；run03旁观者侧移，三件已清楚。丝囊原生周期在相机转背后触发，run04保持正面补该项。','run01 peer17字昵称被原生login编码拒绝，未执行案例；失败保留。']
result={'scope':'COD4-3现有10饰品视觉与双客户端归属，只读原资产与正式代码','runs':runs,'cases':cases,'fully_closable_exact_rows':fullrows,'manual_visual_review':manual,'limitations':limits,'samples':samples,'production_changed':False,'todo_changed':False}
(D/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(D/'capture-quality-audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2))
lines=['10饰品原生双客户端验收','实际生产Jar固定0e1fbac34942714cd90a18ec1b404303b5d4d5bf96ce7c96277e16e561fe5c27','可整条清理精确原文（本对话未修改TODO）：']+fullrows+['','逐项：']
for c in cases:lines += [c['item']+'：'+c['native_trigger']+' '+c['visual_review']+' 原生两端包相同，owner='+str(c['host_entity_id'])+'，peer='+str(c['peer_self_id'])+'。', '  '+', '.join(k+': '+str(v['selected']) for k,v in c['sides'].items())]
lines+=['','玉蝉run02原生tick161 health1000/5000，LivingHeal amount400=8%，cooldown cicada=3761（+3600tick=180秒），只一次触发；原有限16tick cue161–176后清空。未等180秒重触发，长期冷却机制沿用协调已通过记录。','狐尾run02原生50次实际Zombie攻击，6次原随机触发，反馈均归属佩戴者；不是手动发包。','凤凰羽run02佩戴时火伤被原机制拦截，撤装后2497/2507/2517/2527火伤恢复；本机火焰遮住部分短羽，旁观图可辨五羽。','','边界：']+limits+['','每张原始PNG与同帧实体、原生队列、几何、实际像素差、文件hash见acceptance.json。浏览gallery.html；蝉翼滑条只切换原始PNG，不插帧/修图。']
(D/'REPORT.txt').write_text('\n'.join(lines))
body=['<!doctype html><meta charset="utf-8"><title>10饰品原生双客户端证据</title><style>body{background:#111827;color:#eee;font:16px sans-serif;max-width:1400px;margin:auto}img{max-width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}section{margin:35px 0}a{color:#9df}pre{white-space:pre-wrap}</style><h1>10饰品原生双客户端证据</h1><p><a href="REPORT.txt">报告与真实边界</a> · <a href="acceptance.json">同帧原始回执</a></p>']
for c in cases:
 body.append('<section><h2>'+c['item']+'</h2><p>'+html.escape(c['visual_review'])+'</p><div class="pair">')
 for x in samples:
  if x['item']==c['item']:body.append('<div><p>'+html.escape(x['side']+' '+x['path'])+'</p><img loading="lazy" src="'+x['path']+'"></div>')
 body.append('</div></section>')
cicada=read(D/'run-02-peer/jade_cicada-native-frames.json');slides=[{'src':'run-02-peer/'+f['screenshot'],'tick':f['tick'],'serial':f['frameSerial']} for f in cicada if f.get('screenshot') and 'Accessory:jade_cicada' in f['geometry']]
body+=['<section><h2>蝉翼原始帧滑条</h2><input id="s" type="range" min="0" max="'+str(len(slides)-1)+'" value="0" step="1"><p id="label"></p><img id="wing"></section>','<script>const slides='+json.dumps(slides)+';const s=document.getElementById("s");function show(){let f=slides[Number(s.value)];document.getElementById("wing").src=f.src;document.getElementById("label").textContent=f.src+" tick="+f.tick+" serial="+f.serial;}s.addEventListener("input",show);show();</script>']
(D/'gallery.html').write_text('\n'.join(body));print('cases',len(cases),'paired actual images',len(samples),'closure rows',len(fullrows));print('selected',[(x['item'],x['side'],x['path']) for x in samples if 'run-04' in x['path'] or (x['side']=='peer' and 'run-03' in x['path'])])
