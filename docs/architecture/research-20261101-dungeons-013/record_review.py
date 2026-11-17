#!/usr/bin/env python3
"""Record complete forms without treating unresolved design families as extra examples."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '不规则石塔内多小室绕中央空间分布，上缘露天垛台与偏置较高有帽小楼组合，底层数处低棚贴塔边；是整座多小室塔，不拆成塔、亭和囚室。',
  '23×38×23，占用y0..37；中门y10、上门y18，高处小帽与旗继续上升。平台和小室分布不同于旧old_home低双层残屋，最高点不增加楼层。',
  '石墙外侧扶撑/窗洞、木窗与窄小石饰组合，塔身体量较集中但上缘不对称；未凭snowy文件名假定模板有雪坡地形。',
  '露天垛台旁一顶小四坡帽，底部几处更低棚顶；不是用换一个帽顶给旧窄木塔直接增加参考。',
  'cobblestone496、stone_bricks482、stone322、stone_brick_stairs181、cracked_stone_bricks126、dark_oak_slab115、dark_oak_planks103；灰体主材为石，木棚与木室板单独辨认。',
  '底门(10,2,16)，中门4处y10，上门2处y18；x12,z16梯仅y18..22。补看y10/y18及梯侧剖，能见分室与上台，不声称底部至所有房室完整路线已验。',
  '模板含草石地脚，10点为8grunt、1captive_snow及1captain。外接俘虏模板另核原始实体，不是缺失建筑；提案DUN03不规则多小室石守望塔。'],
 'F02':[
  '近方小塔中心竖柱、外围木石框架和两层较紧凑室板叠置，侧面小突出部与底部散柱围护；不同配色或尖顶不能直接视作另一个完整设计。',
  '19×34×19，占用y0..33，约y6/13附近板层，主要上室在约y13以上、尖帽更高；34格不等于所有空间均34格高。',
  '深木横带和灰石角边围较小上室，下部木石混合立面有局部叶苔；分类图不能把全部灰块都看成密实石墙。',
  '上室顶为较尖木坡帽，底部有窄低檐/小坡片；与F03宽平台/较低盖的差别不能只归纳成帽顶一项，家族关系暂不通过。',
  'dark_oak_log198、dark_oak_stairs187、dark_oak_slab172、stone_slab158、dark_oak_planks158、cobblestone122、spruce_fence116；主木种与F03不同不是独立设计证明。',
  '无普通门与梯方块；补看y6/y13与x8/z9，中心柱周边有升高构件，但未认证其原生可通行性或完整楼梯。',
  '草地、散柱和地脚包在模板内，7点为6grunt和1captain。完整小塔可研究，但与F03及既有中心柱单塔的主体家族区分未充分验收，不提案新增信用。'],
 'F03':[
  '四周较开敞木石层架托住宽挑平台，平台中央上室与低坡盖较紧凑，外周围栏比下部塔颈宽；与F02同属中心柱层架塔，独立性先保留。',
  '19×34×19，实际x1..18、y0..33、z1..17，宽木平台约y18，上室约y19以上；底部边缘留白及细旗都不能折算房面积。',
  '竖木柱、石角边和平台外檐向外挑，上段木室四面较紧凑；不能因为相较F02更开敞就未经主体对照自动计另一例。',
  '较低多层坡盖与平台外挑檐配合，旗在中央；旧011-F04虽有尖砖顶，中心柱与分层塔身同类，需比较完整空间而非木顶/砖顶。',
  'oak_log338、spruce_slab292、spruce_stairs222、spruce_trapdoor115、mossy_cobblestone74、spruce_fence74、spruce_planks72；大量木楼层与外檐不是灰分类中的全石层台。',
  '无普通门；x9,z12梯仅y19..22，补看y10/y18及x9/z12，低层开敞框架与上平台可辨，局部短梯不证明地面到上室完整可走。',
  '粗土、草和少量苔石地脚在本体，8点为6grunt、1captain及1minecraft:empty终止点。empty不是额外空房/缺失楼，家族关系待证，当前不提案新增信用。']}
COMPARE=[('research-20261101-dungeons-004','F03-whole.png'),('research-20261101-dungeons-011','F04-whole.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());a=json.loads((OUT/'interface-audit.json').read_text());entries=[];states=[];actors={}
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[i])),
   proposed_target='DUN03不规则多小室石守望塔，23×38×23。' if i=='F01' else '中心柱木石单塔家族研究，独立性暂缓；不增加任何范围信用。',
   independent_design_basis=NOTES[i][0]+' '+NOTES[i][1],status='SCOPED_WHOLE_TOWER_PROPOSAL' if i=='F01' else 'FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],credit_proposal=int(i=='F01'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d['palette'];states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   for pool in next(x for x in a['entries'] if x['id']==i)['outgoing_pools']:
    for comp in pool.get('component_identities_only',[]):
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];actors[comp['member']]=dict(member=comp['member'],sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],
      entity_ids=[e['nbt']['id'] for e in cd['entities']],materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),images_viewed=False,assembled=False,building_credit=0)
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=3,new_images_actually_viewed=12,historical_images_reviewed_again=2,proposals=1,family_holds=2,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],semantic_deduplication=[
   'F01最近旧old_home为低双层塌屋外阶；新为约38高多小室石守望塔，顶部露台与偏置有帽高室、底部低棚，空间关系不同。',
   'F02最近old_home亦不相同，但与F03及旧011-F04中心柱层架单塔的主体独立性尚未充分验收；没有精确hash匹配不代表已证明独立。',
   'F02较紧室板、尖帽与F03较宽平台、较低盖存在差异；本批不直接说它们必为相同设计，也不把门/梯/覆苔和屋顶差异当充分新增依据，双项保留研究。'],
  principles=['完整形态、用途相近与家族独立性分别判断，完整模板也可零信用。',
   '哈希不同不能自动认定新设计；主体层架、室板和平台关系需要语义复核。',
   '露台、偏置高室、底棚和囚室是同一个塔组合，不拆分计算。',
   '普通门、梯、实体接口和empty终止点区别看，empty不代表待建房间。',
   '保存高度包含尖帽和旗杆，短梯不能代替全塔原生通路检查。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Original states only, no native route certification.'))
 dump('actor-component-boundary.json',dict(entries=list(actors.values()),formal_credit_added=0,terminal_pools=['minecraft:empty'],limits='Actor identities only; empty terminal is not an unassembled room.'))
 print('Three studies: one bounded tower proposal, two unresolved family holds, zero formal credit.')
if __name__=='__main__':main()
