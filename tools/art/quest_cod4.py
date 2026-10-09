"""Optional COD4 nodes in existing chapters, preserving every existing save identity."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def add_cod4(chapters):
    nodes=json.loads((ROOT/'docs/cod4/quest-nodes.json').read_text())
    for node in nodes:
        chapter=next(c for c in chapters if c['file']==node['chapter'])
        occupied=[(q['x'],q['y']) for q in chapter['quests']]+[(q['x'],q['y']) for q in chapter.get('quest_links',[])]
        candidates=[(x*1.8,y*1.8) for y in range(-5,6) for x in range(-5,6)]
        candidates.sort(key=lambda p:(abs(p[1])+abs(p[0])*.2,p[1],p[0]))
        position=next((p for p in candidates if all(math.dist(p,q)>=1.55 for q in occupied)),None)
        assert position is not None,'No free position in '+chapter['file']
        chapter['quests'].append(dict(id=node['id'],title='拓展 · '+node['title'],icon='{ id: "dynasty:'+node['item']+'" }',kind='advancement',target='dynasty:'+node['advancement'],count=1,
            tasks='[{ id: "'+node['task']+'", type: "advancement", advancement: "dynasty:'+node['advancement']+'" }]',rewards='[]',purpose=node['title'],how=node['description'][0],deps=[],role='build',route='cod4',x=position[0],y=position[1],shape='square',subtitle='可选 · 装备与行旅',description=node['description']))
