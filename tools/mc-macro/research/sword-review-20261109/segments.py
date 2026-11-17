import subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[2];py=r/'.build/video-venv/bin/python';extract=r/'research/modern-pvp-20261101/extract.py'
cases=[('user-aim-low','/Users/a15356015027/Desktop/吃屎/录屏2026-11-04 19.08.32.mov',19.7,20.1),('user-close','/Users/a15356015027/Desktop/吃屎/录屏2026-11-05 15.28.14.mov',13.1,13.5),('user-strafe','/Users/a15356015027/Desktop/吃屎/录屏2026-11-06 11.24.19.mov',19.9,20.3),('user-highping','/Users/a15356015027/Desktop/吃屎/录屏2026-11-04 17.01.36.mov',12.6,13.0),('reference-reset',r/'research/modern-pvp-20261101/intel-sword.webm',518,518.4),('reference-hop',r/'research/melee-20261103/G_-FqCxdnAE.mp4',961.7,962.1)]
for name,source,start,end in cases:
 subprocess.run([str(py),str(extract),str(source),str(start),str(end),'--tag','../sword-review-20261109/'+name],check=True)
