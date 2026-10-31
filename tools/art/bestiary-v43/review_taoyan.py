"""Render the actual two-form cauldron actor and its timed texture transition."""
from pathlib import Path
import json
import review_marshal as m
m.OUT=m.ROOT/'docs/art/bestiary-v43/taoyan'
m.base.OUT=m.OUT
m.IDS=('taoyan_zhishi','taoyan_zhishi_phase2')
m.PREFIX='animation.taoyan_zhishi.'
m.MOTIONS=('idle','walk','ram','whip','oil','transition')
m.DETAILS=[('maw',['cauldron_maw','maw_lower_hinge','boiling_oil']),('ram',['siege_']),('shell',['war_cauldron','mourning_bell','bell_yoke','war_relic_crest'])]
def texture_form(ident,clip,tick):
 return m.IDS[0] if ident==m.IDS[1] and clip=='transition' and tick<32 else ident
m.texture_form=texture_form
if __name__=='__main__':
 m.main()
 for tick in (0,24,31.99,32,40,64):
  m.base.label(m.render(m.IDS[1],clip='transition',tick=tick,mode='lit'),f'变身{tick:g}tick · 实际纹理切换 · 离线预览').save(m.OUT/m.IDS[1]/f'transition-{tick:g}.png')
 (m.OUT/'transition-samples.json').write_text(json.dumps([{'tick':t,'model':m.IDS[1],'texture':texture_form(m.IDS[1],'transition',t)+'_body.png'} for t in (0,24,31.99,32,40,64)],indent=2)+'\n')
