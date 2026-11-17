import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from whole_building_candidates import AIR,iso,color

def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
olds={str(n):R/f'docs/architecture/research-20261104-smithy-{n}/manual-review.json' for n in [249,297,301,304,306,307]}
review=R/'docs/cod4/audit-20261022/coordinator-building306-actual-sevenPNG-whole-NPC03-auxiliary-review-20261114.json'
assert bind(review)['sha256']=='c1b43869ad28bfbce45cf335bd8d2f44606f167eb238e336473afbbe98c5626e'
comparisons={n:dict(binding=bind(f),seven_dimensions=ld(f)['seven_dimensions'])for n,f in olds.items()}
comparisons['297']['seven_dimensions']['proportion']=comparisons['297']['seven_dimensions']['proportion'].replace('底层8床块','全屋8床块')
put('pre-render-family-check.json',dict(batch=309,order='全125palette Properties/20BE/13层260行3380源格先实际读，六处旧整栋七维此前实际读且原绑定未变，249/301/307与298/302更正本轮补读，保存本比较后才PNG。',old_whole_comparisons=comparisons,errata=[bind(R/'docs/architecture/research-20261104-smithy-298/prior297-wording-correction.json'),bind(R/'docs/architecture/research-20261104-smithy-302/prior301-wording-correction.json')],Main306=dict(binding=bind(review),status=ld(review)['status'],accepted_bounded_NPC03_auxiliary=1,strict_Chinese_Hui_thatch_credit=0,current_credit_transferred=0,scope_total=None,scope_gap=None,gate_met=False),current_spatial_reading='主屋floor1/use2下厅、floor5 top半砖配y6 bottom半砖/南两床的上居室；东内侧north四阶通楼上。south低附屋floor0/use1有三箱，闭门经主屋south口相连，外west另开门；不同使用层/附屋不拆计。西两cherry闭门x2,z4/7背后实墙/柱，中央z5/6开放进主屋，不能仅门名当实际门洞。',comparison='249/301单方室无内部上交通，297下2床上2床/northwest直阶，306下1床/梯顶储物，307西单门下抬平台和southwest阶上north双床；本屋west双宽开放口、下厅上south双床、eastnorth阶及south低储物附屋为完整组织差别。304是独立英文Inn招牌/下三餐桌/两睡层共6床，不能把本屋双层+附屋强叫新客栈，亦不能只加附屋/箱就自动增加参考。共同木架浅填墙深盖的家族风险保留，由独立整栋审查判断。',purpose='cod2 DUN05废弃民居/窄巷与屋盖空间的广义东亚住宅辅助：实际双层床厅、主附关系、长瓦盖/浅墙框架，不仅cherry目录。无徽派马头墙/中国文化凭据/纸扎人/连通屋顶实测；严格中国Hui0。无外竹林，不转306NPC03资格；无炉，不改称NPC01铁匠铺。',decision='PROVISIONAL_MAIN_DWELLING_LOW_STORAGE_ANNEX_SPATIAL_AUXILIARY_NOT_STRICT_HUI_PENDING_REVIEW',formal_credit_added=0))
a=ld(P/'source-context.json')['resources'];b=ld(R/'docs/architecture/research-20261104-smithy-304/source-context.json')['resources'];assert a==b
put('context-reuse.json',dict(current=bind(P/'source-context.json'),prior304=bind(R/'docs/architecture/research-20261104-smithy-304/source-context.json'),all5_full_original_JSON_objects_equal=True,prior_full_bodies_actually_read=True,reading='复用同会话304已全文实际读过的5个相同资源正文，不重读/重计新建筑。309实际补读本屋selected entry。',selected=next(v for v in a[1]['json']['elements']if v['element'].get('location')=='trek:village/cherry/houses/cherry_medium_house_1'),limits='复用source上下文，不迁304建筑语义/acceptance/信用。'))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
for name,cut in [('whole',None),('cut-03',3),('cut-06',6),('cut-09',9)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'309 original dwelling '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
for start in [0,5,10]:
 im=Image.new('RGB',(1440,1040),'#edf0f2');dr=ImageDraw.Draw(im);step=20
 for i,y in enumerate(range(start,min(start+5,size[1]))):
  ox=40+480*(i%3);oy=45+500*(i//3);dr.text((ox,oy-24),f'y{y} white air / black omitted',fill='black')
  for x in range(size[0]):
   for z in range(size[2]):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
  for x in range(size[0]):dr.text((ox+x*step,oy-12),str(x),fill='black')
  for z in range(size[2]):dr.text((ox-20,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02}.png')
im=Image.new('RGB',(1200,520),'#edf0f2');dr=ImageDraw.Draw(im);step=24
for i,(axis,fixed)in enumerate([('x',8),('z',14)]):
 ox=45+600*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(extent):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=309,status='PRE_FAMILY_CHECK_SAVED_8_PNG_GENERATED_NOT_YET_ACTUALLY_VIEWED',images_generated=8,images_actually_viewed=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Actual8PNG/all13plans/2sections; open west entry vs decorative closed doors, north stairs, lower annex doors/three chests and two beds require exact probes.'))
print('8images generated after family precheck; not yet actually viewed.')
