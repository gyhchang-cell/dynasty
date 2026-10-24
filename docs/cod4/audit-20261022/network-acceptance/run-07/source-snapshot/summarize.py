"""Produce an evidence index; incomplete runs always remain incomplete."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[3]
run=sys.argv[1]
p=R/'docs/cod4/audit-20261022/network-acceptance'/run
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
counts={role:len(list(p.glob(role+'-stage-*.json'))) for role in ['host','peer']}
server=list(p.glob('server-stage-*.json'))
failures={f.name:f.read_text() for f in p.glob('*FAIL*')}
passed=all((p/(role+'-PASS')).exists() for role in ['server','host','peer']) and len(server)==49 and all(n==49 for n in counts.values()) and not failures
network_passed=passed
render_all=all('AFTER_LEVEL' in json.loads(f.read_text()).get('captureEvent','') for role in ['host','peer'] for f in p.glob(role+'-stage-*.json')) and all(n==49 for n in counts.values())
result={'passed':network_passed and render_all,'network_state_passed':network_passed,'world_render_all_stages':render_all,'server_stages':len(server),'client_stages':counts,'failures':failures,'scope':'two automated actual rendered Minecraft clients, host integrated local connection plus remote TCP peer; 4 jars, not full pack','fixtures':'all equipment and initial effects supplied by server QA; stage43 uses native remote-client C2S consumption; not human survival','assertions':['affected client full native effect IDs/amplifiers/durations within100ticks','both tracked entities actual bounded status-aura render queue and packet amplifier','independent armor and Curios equipped-slot ownership','live day/night full-set immunity and removal','stack cap, opposite Qi neutralisation, thunder consumption','native peer pill C2S, exact one consumption, host unaffected'],'not_tested':['all combat source inputs','full pack','two human players'],'evidence_sha256':{f.name:sha(f) for f in sorted(p.iterdir()) if f.is_file() and f.name!='result.json'}}
(p/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},ensure_ascii=False,indent=2))
