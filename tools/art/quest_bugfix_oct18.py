"""Remove duplicated school inventory milestones and repeated boilerplate."""
import json
from pathlib import Path
REMOVED=set(json.loads(Path(__file__).with_name('quest_removed_oct18.json').read_text()))
def apply(chapters):
 byid={q['id']:q for c in chapters for q in c['quests']}
 def expand(d):
  return [v for p in byid[d]['deps'] for v in expand(p)] if d in REMOVED else [d]
 for c in chapters:
  c['quests']=[q for q in c['quests'] if q['id'] not in REMOVED]
  for q in c['quests']:
   q['deps']=list(dict.fromkeys(v for d in q['deps'] for v in expand(d)))
   lines=[]
   for s in q['description']:
    s=s.replace('#minecraft:planks','任意木板').replace('，背包持有即可','').replace('背包持有即可；','').replace('背包持有即可。','')
    if s and s not in lines:lines.append(s)
   if q.get('evolution_recipe'):
    # Recipe UI is authoritative; don't append a second, stale smithing ingredient list.
    lines=[s for s in lines if not ('兵器图纸' in s and ('+' in s or '＋' in s or '→' in s))]
    lines.insert(1,'在锻造台按配方升级；保留原武器等级、历练与附魔。按 R 查看配方。')
   if q['target']=='dynasty:cinnabar':
    lines=[s for s in lines if not any(t in s for t in ['朱砂没有矿','没有朱砂矿','指南针无法','无法直接用指南针'])]
    lines.insert(1,'没有朱砂矿。用探险者指南针搜索神庙、法阵遗迹、山麓采矿庄园或天工山城，开宝箱有概率取得朱砂。新加入定位的建筑需前往尚未探索的区域搜索。')
   q['description']=list(dict.fromkeys(lines))
   if '持有一份即可' in q.get('subtitle',''):q['subtitle']='备料'
