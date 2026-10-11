"""Extract the golem's own right hammer; no unrelated projectile or copied texture."""
import json,copy,shutil
from build import A
id='juchui_jinjia_lishi';g=json.loads((A/'geo/boss_forms'/f'{id}.geo.json').read_text());geo=g['minecraft:geometry'][0];bone=next(b for b in geo['bones'] if b['name']=='hammer_1');cubes=copy.deepcopy(bone['cubes']);offset=[43,13,-18]
for c in cubes:
 c['origin']=[c['origin'][j]-offset[j] for j in range(3)]
 if 'pivot' in c:c['pivot']=[c['pivot'][j]-offset[j] for j in range(3)]
geo['description'].update(identifier='geometry.hammer_chain',visible_bounds_width=4,visible_bounds_height=4,visible_bounds_offset=[0,0,0]);geo['bones']=[{'name':'root','pivot':[0,0,0],'cubes':cubes}]
(A/'geo/boss_forms/hammer_chain.geo.json').write_text(json.dumps(g,indent=2)+'\n')
a={'format_version':'1.8.0','animations':{'animation.hammer_chain.spin':{'loop':True,'animation_length':.6,'bones':{'root':{'rotation':{'0':[0,0,0],'.6':[360,0,0]}}}}}}
(A/'animations/boss_forms/hammer_chain.animation.json').write_text(json.dumps(a,indent=2)+'\n');shutil.copy2(A/'textures/entity/boss_forms'/f'{id}.png',A/'textures/entity/boss_forms/hammer_chain.png')
