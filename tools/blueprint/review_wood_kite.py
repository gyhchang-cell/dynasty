#!/usr/bin/env python3
"""Same-scale actual asset software previews; no JVM."""
from pathlib import Path
import ast,json,numpy as np
R=Path(__file__).resolve().parents[2];p=R/'tools/blueprint/review_taoyan_cauldrons.py';ns={'__file__':str(p)};exec(p.read_text().split('\nreport={}\n',1)[0],ns)
D=R/'docs/blueprint-cod1/evidence/wood-kite-v1';D.mkdir(parents=True,exist_ok=True);ns.update(D=D,ID='luban_yisha');ns['sheet'].__globals__['D']=D
for ident in ('luban_yisha','luban_yisha_metal'):
 ns['ident']=ident;render=ns['render'];ns['sheet']([render(yaw=y,mode=m) for y,m in ((0,'lit'),(180,'lit'),(90,'lit'),(-90,'lit'),(45,'lit'),(45,'shape_gray'),(45,'silhouette'))],['正面','背面','右侧','左侧','45度','灰模','剪影'],ident+' / 原创9m翼展、5.5m长度 / 固定世界5.5px每单位 / 1.8m人物及1m石块参照 / 软件图',ident+'-views.png',cols=3)
 ns['sheet']([render(c,t) for c,t in [('fly',10),('intro',160),('wing_cut',36),('bombs',32),('claws',36),('wind',40),('overheat',40),('lightning',48),('meteor',60),('stun',20)]],[f'{c} {t}t' for c,t in [('fly',10),('intro',160),('wing_cut',36),('bombs',32),('claws',36),('wind',40),('overheat',40),('lightning',48),('meteor',60),('stun',20)]],ident+' / 各技能和真实折叠关节源姿态 / 飞行高度由实体承载 / 软件图',ident+'-poses.png',cols=3)
print('Actual wood and metal aircraft view sheets rendered; software only, no JVM')
