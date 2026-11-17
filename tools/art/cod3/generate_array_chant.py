#!/usr/bin/env python3
"""Author an original wordless, quiet synthesized choral tone. Never plays audio."""
import sys,json,hashlib
from pathlib import Path
if len(sys.argv)>1:sys.path.insert(0,sys.argv[1])
import numpy as np
import soundfile as sf
rate=22050;seconds=6;t=np.arange(rate*seconds)/rate
# Three soft vowel-like harmonic voices. No human recording, model voice or borrowed music.
out=np.zeros(t.size);rng=np.random.default_rng(20261018)
for base,offset,gain in [(110,0,.55),(146.8324,.3,.28),(164.8138,.6,.17)]:
 phase=2*np.pi*base*t+.04*np.sin(2*np.pi*.7*t+offset)
 voice=np.zeros(t.size)
 for harmonic in range(1,17):
  f=base*harmonic
  weight=(.7*np.exp(-((f-350)/180)**2)+.28*np.exp(-((f-850)/260)**2)+.08*np.exp(-((f-1800)/350)**2))/harmonic
  voice+=weight*np.sin(harmonic*phase+rng.uniform(-.1,.1))
 breath=.68+.32*np.sin(np.pi*t/3+offset)**2
 out+=gain*voice*breath
edge=np.minimum(np.minimum(t/.8,(seconds-t)/1.1),1).clip(0,1);out*=edge
out*=.24/max(abs(out));target=Path('src/main/resources/assets/dynasty/sounds/scenic/ancient_array.ogg');target.parent.mkdir(exist_ok=True,parents=True)
sf.write(target,out,rate,format='OGG',subtype='VORBIS')
a,sr=sf.read(target);assert sr==rate and a.ndim==1 and len(a)==len(t) and max(abs(a))<.3
report={'sampleRate':sr,'seconds':len(a)/sr,'channels':1,'peak':float(max(abs(a))),'rms':float(np.sqrt(np.mean(a*a))),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'authorship':'Original harmonic synthesis, wordless choir, no recordings or borrowed assets','auditioned':False}
Path('build/cod3-ancient-array-20261018/audio-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
