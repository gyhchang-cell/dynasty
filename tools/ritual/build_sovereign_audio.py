"""Original synthesized ritual voice and 32-second battle loop. No sampled recordings."""
from pathlib import Path
import numpy as np
import soundfile as sf
rate=22050
out=Path('src/main/resources/assets/dynasty/sounds/ritual');out.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(721)
t=np.arange(rate*4)/rate
phase=2*np.pi*(52*t-3*t*t)
voice=(np.sin(phase)+.32*np.sin(phase*2.01)+.17*np.sin(phase*3.03))
voice*=np.minimum(1,t*4)*np.maximum(0,1-t/4)**.7
voice+=rng.normal(0,.035,len(t))*np.sin(np.pi*t/4)**2
sf.write(out/'awakening.ogg',np.tanh(voice)*.65,rate,format='OGG',subtype='VORBIS')
t=np.arange(rate*32)/rate
track=np.zeros_like(t)
# Pentatonic low brass, deep hand-drum pulse, sparse high bell response.
notes=[55,65.406,73.416,82.407,55,49,65.406,55]
for i,f in enumerate(notes):
    local=t-i*4;env=np.where((local>=0)&(local<4),np.minimum(1,np.maximum(0,local)*3)*np.maximum(0,1-local/4),0)
    track+=env*(np.sin(2*np.pi*f*t)*.18+np.sin(2*np.pi*f*1.5*t)*.055+np.sin(2*np.pi*f*2*t)*.06)
for beat in range(64):
    local=t-beat*.5;env=np.where((local>=0)&(local<.45),np.exp(-np.maximum(0,local)*13),0)
    track+=env*np.sin(2*np.pi*(72*local-40*local*local))*(.36 if beat%4==0 else .13)
    if beat%8==6:track+=env*np.sin(2*np.pi*440*local)*.11
fade=np.minimum(1,t/.03)*np.minimum(1,(32-t)/.08)
sf.write(out/'battle.ogg',np.tanh(track)*fade*.8,rate,format='OGG',subtype='VORBIS')
for file in out.glob('*.ogg'):
    info=sf.info(file);assert info.samplerate==rate and info.frames>0
    print(file,info.duration)
