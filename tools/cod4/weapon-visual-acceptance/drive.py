"""Case driver for the helper's native client interaction path. No injected VFX."""
from pathlib import Path
import json,time,sys
R=Path(__file__).resolve().parents[3]
O=R/'docs/cod4/audit-20261022/weapon-visual-acceptance'/sys.argv[1]
group=sys.argv[2] if len(sys.argv)>2 else 'smoke'
def wait(p,timeout=240):
 end=time.time()+timeout
 while time.time()<end:
  if p.exists():return json.loads(p.read_text())
  fails=list(O.glob('*-FAIL.json'))
  if fails:raise RuntimeError(fails[-1].read_text())
  if (O/'exit-code.txt').exists():raise RuntimeError('client exited')
  time.sleep(.3)
 raise TimeoutError(str(p))
def case(i,item,**kw):return dict(id=i,item=item,**kw)
cases=[]
if group=='smoke':
 cases=[case('s01-tie-first','tie_jian'),case('s02-seven-third','seven_star_saber',camera='THIRD_PERSON_BACK'),case('s03-bow-third','lie_gong',kind='bow',camera='THIRD_PERSON_BACK',duration=90),case('s04-flute-third','yu_di',kind='use',camera='THIRD_PERSON_BACK',targets=3)]
elif group=='materials':
 for w in ['mu_mao','shi_ge','tong_dao','tie_jian','qinggang_sword','gilded_mace','yitian_sword']:
  for label,opts in [('day-first',{}),('night-third',dict(light='night',camera='THIRD_PERSON_BACK')),('glass-10fps',dict(scene='glass',fps=10,camera='THIRD_PERSON_BACK')),('wall-third',dict(scene='occlusion',camera='THIRD_PERSON_BACK'))]:
   cases.append(case(w+'-'+label,w,**opts))
elif group=='sequence':
 for w in ['seven_star_saber','halberd_fangtian','yu_di']:
  for label,opts in [('day-first',{}),('day-third',dict(camera='THIRD_PERSON_BACK')),('night-glass',dict(scene='glass',light='night',camera='THIRD_PERSON_BACK')),('wall-10fps',dict(scene='occlusion',fps=10,camera='THIRD_PERSON_BACK'))]:
   cases.append(case(w+'-'+label,w,kind='use' if w=='yu_di' else 'attack',targets=3,**opts))
elif group=='bows':
 for w in ['lie_gong','chang_gong','shenbi_bow','luoyan_bow','tianlang_bow','dragon_bow','zhuxing_bow','fengling_bow']:
  for label,opts in [('day-first',{}),('third-10fps',dict(camera='THIRD_PERSON_BACK',fps=10))]:cases.append(case(w+'-'+label,w,kind='bow',duration=90,**opts))
elif group=='visible':
 for w in ['mu_mao','shi_ge','tong_dao','tie_jian','qinggang_sword','gilded_mace','yitian_sword','seven_star_saber','halberd_fangtian','yu_di']:
  for label,opts in [('side-day',{}),('side-night-10fps',dict(light='night',fps=10,scene='glass'))]:
   cases.append(case(w+'-'+label,w,kind='use' if w=='yu_di' else 'attack',camera='THIRD_PERSON_BACK',viewYaw=25,pixels=True,targets=3 if w in ['halberd_fangtian','yu_di'] else 1,**opts))
elif group=='advanced':
 for w in ['huan_shou_dao','juque_sword','mu_mao','chang_qiang','dragon_spear','bawang_spear','thunder_spear','beichen_spear','baihu_glaive']:
  for label,opts in [('stone',{}),('sand-wall',dict(ground='sand',scene='occlusion',fps=10))]:
   cases.append(case(w+'-mobile-'+label,w,mobile=True,camera='THIRD_PERSON_BACK',viewYaw=25,pixels=True,**opts))
 cases.append(case('juque-ceiling','juque_sword',mobile=True,scene='ceiling',pixels=True))
 for w in ['pojun_axe','xuantian_axe']:
  for label,opts in [('first',{}),('third-glass',dict(camera='THIRD_PERSON_BACK',viewYaw=25,scene='glass')),('wall-10fps',dict(camera='THIRD_PERSON_BACK',viewYaw=25,scene='occlusion',fps=10))]:
   cases.append(case(w+'-'+label,w,target='dynasty:royal_guard',pixels=True,**opts))
 for label,opts in [('third-move',dict(move=True)),('first-turn',dict(move=True,camera='FIRST_PERSON')),('swim',dict(scene='water',move=True)),('effect-clear',dict(removeSpeed=True))]:
  opts.setdefault('camera','THIRD_PERSON_BACK');cases.append(case('tang-'+label,'tang_dao',pixels=True,duration=90,**opts))
 for target in ['dragon_king','dragon_emperor']:
  for label,opts in [('first',{}),('third-glass',dict(camera='THIRD_PERSON_BACK',viewYaw=25,scene='glass')),('reload',dict(reload=True))]:cases.append(case(target+'-'+label,'dragon_slayer',target='dynasty:'+target,pixels=True,duration=90,**opts))
elif group=='bow-visible':
 for w in ['lie_gong','chang_gong','shenbi_bow','luoyan_bow','tianlang_bow','dragon_bow','zhuxing_bow','fengling_bow']:
  for label,opts in [('first',{}),('third-10fps',dict(camera='THIRD_PERSON_BACK',viewYaw=25,viewAt=26,fps=10))]:cases.append(case(w+'-visible-'+label,w,kind='bow',duration=90,pixels=True,**opts))
elif group=='closing':
 for w in ['huan_shou_dao','juque_sword','mu_mao','chang_qiang','dragon_spear','bawang_spear','thunder_spear','beichen_spear','baihu_glaive']:
  cases.append(case(w+'-clear-wall-sand',w,mobile=True,camera='THIRD_PERSON_BACK',viewYaw=25,pixels=True,scene='occlusion',ground='sand',fps=10))
  cases.append(case(w+'-first-mobile',w,mobile=True,pixels=True))
 for w in ['mu_mao','shi_ge','tong_dao','tie_jian','qinggang_sword','gilded_mace','yitian_sword','seven_star_saber','halberd_fangtian','yu_di']:
  for label,opts in [('first',{}),('glass-third-10fps',dict(camera='THIRD_PERSON_BACK',viewYaw=25,fps=10,scene='glass'))]:
   cases.append(case(w+'-guard-'+label,w,target='dynasty:royal_guard',pixels=True,kind='use' if w=='yu_di' else 'attack',targets=3 if w in ['halberd_fangtian','yu_di'] else 1,**opts))
 for w in ['pojun_axe','xuantian_axe']:
  cases.append(case(w+'-clear-wall',w,target='dynasty:royal_guard',pixels=True,camera='THIRD_PERSON_BACK',viewYaw=25,scene='occlusion',fps=10))
 cases += [case('sweep-invulnerable-negative','halberd_fangtian',noDamage=True,pixels=True),case('seven-invulnerable-negative','seven_star_saber',noDamage=True,pixels=True),case('flute-offhand-first','yu_di',kind='use',offhand=True,pixels=True,targets=3),case('dragon-part-flight','dragon_slayer',target='minecraft:ender_dragon',pixels=True,camera='THIRD_PERSON_BACK',viewYaw=25,duration=90)]
 cases += [case('juque-tight-ceiling','juque_sword',mobile=True,scene='tight-ceiling',pixels=True,pitch=30),case('tang-swim-flags','tang_dao',scene='water',move=True,pixels=True,camera='THIRD_PERSON_BACK',duration=90),case('tang-clear-flags','tang_dao',removeSpeed=True,pixels=True,camera='THIRD_PERSON_BACK',duration=90)]
else:raise ValueError(group)
wait(O/'READY.json',600)
if len(sys.argv)>3:wait(O/(sys.argv[3]+'-DRIVER-COMPLETE.json'),600)
for c in cases:
 if (O/(c['id']+'-result.json')).exists():continue
 tmp=O/'command.tmp';tmp.write_text(json.dumps(c));tmp.replace(O/'command.json')
 r=wait(O/(c['id']+'-result.json'))
 ev=json.loads((O/(c['id']+'-events.json')).read_text());fr=json.loads((O/(c['id']+'-frames.json')).read_text())
 print(c['id'],'frames',len(fr),'geometry',sorted({k for f in fr for k in f['geometry']}),'wire',sorted({e['data']['sequence'] for e in ev if e['kind']=='actual-s2c-handle'}),flush=True)
(O/(group+'-DRIVER-COMPLETE.json')).write_text(json.dumps(cases,indent=2))
