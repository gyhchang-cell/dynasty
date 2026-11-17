from pathlib import Path
import os,signal,subprocess,time
root=Path(__file__).resolve().parents[2];p=root/'.build/anchor-singleplayer'
try:os.kill(int((p/'app.pid').read_text()),signal.SIGTERM)
except ProcessLookupError:pass
time.sleep(.4)
f=(p/'app.log').open('a');env={**os.environ,'MC_MACRO_TRACE':'1','MC_MACRO_BACKGROUND':'1','MC_ANCHOR_DIAGNOSTIC_PATH':str(p/'state.json')}
a=subprocess.Popen([str(root/'.build/candidates/anchor-197/mcPvPmax.app/Contents/MacOS/MCMacro')],env=env,stdout=f,stderr=f,start_new_session=True);(p/'app.pid').write_text(str(a.pid));print('candidate',a.pid)
