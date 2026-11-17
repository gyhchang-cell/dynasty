"""User-authorized removal of eight redundant school blueprint preparation nodes.
No remaining quest, detector or reward ID is renumbered.
"""
REMOVED_BLUEPRINT_PREPS={'10d333a04d5f58da','10d309dbd5e4932b','10d3531c75e191e2','10d3563864764554','10d30cb4d566fd86','10d3422734972408','10d34ee6243d0e1f','10d3510627cfe2b5'}
CINNABAR='朱砂没有矿。主世界用探险者指南针搜索“山麓采矿庄园”或“天工山城”，寻找宝箱，有概率取得。神庙、法阵遗迹属于小型地物，指南针无法直接搜索。'
SKY='天将令：进入九霄天界，用自然指南针搜索“九霄仙岛”，在岛上探索并击败九霄天将，每次必掉1枚。首次不用天将令召唤；已有令牌可在法阵·祭坛复战。'
def apply(chapters):
 byid={q['id']:q for c in chapters for q in c['quests']}
 def expand(dep):
  if dep not in REMOVED_BLUEPRINT_PREPS:return [dep]
  return [v for p in byid[dep]['deps'] for v in expand(p)]
 for c in chapters:
  c['quests']=[q for q in c['quests'] if q['id'] not in REMOVED_BLUEPRINT_PREPS]
  for q in c['quests']:
   q['deps']=list(dict.fromkeys(v for d in q['deps'] for v in expand(d)))
   for field in ['title','display_title','subtitle','how','purpose']:
    if q['target']=='dynasty:tie_jian' and isinstance(q.get(field),str):q[field]=q[field].replace('铁剑','锻铁长剑') if '锻铁长剑' not in q[field] else q[field]
   if q['target']=='dynasty:cinnabar' and q['role']=='main':q['description']=[CINNABAR]+q['description'][1:]
   if q['target']=='dynasty:sky_token':q['description'].append(SKY)
   q['description']=[s.replace('主世界神庙、法阵遗迹或帝陵宝箱有概率出朱砂；没有朱砂矿。',CINNABAR) for s in q['description']]
   if q.get('journey_distant_dependencies'):q.pop('journey_distant_dependencies')
