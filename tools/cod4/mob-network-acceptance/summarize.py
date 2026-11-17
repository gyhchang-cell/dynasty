from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];base=R/'docs/cod4/audit-20261022/mob-network-acceptance';run=sys.argv[1];out=base/run
results=[json.loads(p.read_text()) for p in sorted(out.glob('result-*.json'))]
matrix=json.loads((base/'applicability.json').read_text())
rows=[]
for r in matrix['matrix']:
 cases=[x for x in results if x['index']<240 and x['name'].startswith(r['id']+'/')]
 rows.append(dict(id=r['id'],name=r['name'],neutral=r['neutral'],expected_cases=8,recorded=len(cases),status='未覆盖' if len(cases)!=8 else 'pass' if all(c['pass'] for c in cases) else 'fail',failures=[{'case':c['name'],'checks':c['checks']} for c in cases if not c['pass']]))
failures=[dict(index=x['index'],name=x['name'],checks=x['checks']) for x in results if not x['pass']]
report={'run':run,'completed':(out/'server-COMPLETE').exists() and all((out/(r+'-COMPLETE')).exists() for r in ['host','peer']),'identity':'两个自动控制的真实Minecraft客户端；集成LAN主机本地连接+独立UUID的真实TCP peer；不是两名真人；没有FakePlayer','artifact_sha256':'ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b','scope':'仅固定生产Jar+GeckoLib+Curios+私有QA四Jar，非完整整合包/生存获取；实体原料位置与高血量由服务端夹具提供；行为输入通过原生MultiPlayerGameMode，经C2S到服务端','case_count':len(results),'pass_cases':sum(x['pass'] for x in results),'fail_cases':len(failures),'failures':failures,'species':rows,'screenshots':len(list(out.glob('*-view-*.png'))),'original_pending':'[ ] 两名真实玩家验证仇恨、中立受击、喂食、交易、偷窃物返还和击杀掉落不重复；不要把 FakePlayer 测试等同于真实联机验收。','can_close_original':False,'closure_reason':'两个自动控制的真实客户端已获用户认可，可作为真实联机机制验收；闭项仅按30类适用机制、玩家隔离、掉落守恒和真实缺口判定，不以缺少真人为门槛。详见最终综合回执。','uncovered':['两名真人操作及主观观感/音效','完整整合包兼容性与生存获取流程','自然世界生态生成（本任务使用实体夹具）','不同机器或互联网延迟场景']}
(out/'run-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['completed','case_count','pass_cases','fail_cases','failures','screenshots']},ensure_ascii=False,indent=2))
