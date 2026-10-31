"""Audit two distinct R sessions, not a single uninterrupted bridge run."""
from pathlib import Path
import json,sys

root=Path(__file__).resolve().parents[2]
for label in sys.argv[1:]:
    path=root/'.build/state-live'/f'xiaocai190-app-diag192-{label}.log'
    lines=path.read_text().splitlines()
    interruptions=[i for i,l in enumerate(lines) if ' INPUT_FINISH ' in l]
    finishes=[(i,json.loads(l.split(' FINISH ',1)[1])) for i,l in enumerate(lines) if ' FINISH ' in l]
    starts=[i for i,l in enumerate(lines) if ' STATE 正在读取角色状态' in l]
    manual=[l for l in lines if ' MANUAL_FINISH ' in l]
    blocked_restart=(len(finishes)==2 and len(starts)==2 and
                     starts[0]<interruptions[0]<finishes[0][0]<starts[1]<finishes[1][0]) if interruptions else False
    report={'label':label,'manual_requests':manual,'starts':len(starts),
            'finishes':[v for _,v in finishes],
            'all_finishes_grounded_aligned_released':bool(finishes) and all(v['safe_aligned_finish'] for _,v in finishes),
            'no_restart_until_fresh_r':blocked_restart,
            'passed':len(interruptions)==1 and blocked_restart and all(v['safe_aligned_finish'] for _,v in finishes),
            'scope':'Intentional manual takeover, then one fresh R run. Not continuous-run speed evidence.'}
    Path(__file__).with_name(label+'-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
