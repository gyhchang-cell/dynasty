import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from whole_building_candidates import AIR,iso,color

def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
old249=R/'docs/architecture/research-20261104-smithy-249/manual-review.json';old301=R/'docs/architecture/research-20261104-smithy-301/manual-review.json';Main301=R/'docs/cod4/audit-20261022/coordinator-building301-actual-fivePNG-whole-spatial-HOLD0-review-20261114.json'
put('pre-render-family-check.json',dict(batch=306,order='全原palette/10层110行990格及8BE先读，旧249完整七维、301/297已读旧整栋与Main301判断对比后先写此文件，再生成PNG。',old249=dict(binding=bind(old249),seven_dimensions=ld(old249)['seven_dimensions']),old301=bind(old301),Main301_actual_review=bind(Main301),comparison='本栋矩形单床室配东内壁四格梯，经顶闭活板到roof内top阶/半砖储物平台及西开箱。不同249低单室无梯/隐桶夹梁、301方室四外柱/外菜地无上交通，亦非297内阶双层四床/304三层旅宿。共同小居/白填墙/木框/瓦盖仍有同作者家族风险，不能只凭加梯/换箱加信用；完整床室+低坐台+梯顶闭盖+屋内实平台/高箱的整体组织可进入完整研究待独立判断。',purpose='cod3 NPC03竹林茅屋的居住/夜回屋/雨避空间辅助：真实周缘44bamboo与小床室/屋盖，不仅依据cherry命名。原石阶瓦盖不是茅草盖，无茶棋行为或中国古建资格证明。',decision='PROVISIONAL_BAMBOO_GROVE_DWELLING_AUXILIARY_SOURCE_NOT_STRICT_CHINESE_QUALIFICATION',formal_credit_added=0))
a=ld(P/'source-context.json')['resources'];b=ld(R/'docs/architecture/research-20261104-smithy-304/source-context.json')['resources'];assert a==b
put('context-reuse.json',dict(current=bind(P/'source-context.json'),prior304=bind(R/'docs/architecture/research-20261104-smithy-304/source-context.json'),all5_full_original_JSON_objects_equal=True,prior_full_bodies_actually_read=True,reading='复用同会话304已全文实际读过的5个相同资源正文，不重读/重计新建筑。306实际补读本屋selected entry。',selected=next(v for v in a[1]['json']['elements']if v['element'].get('location')=='trek:village/cherry/houses/cherry_small_house_1'),limits='复用source上下文，不迁304建筑语义/acceptance/信用。'))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
for name,cut in [('whole',None),('cut-02',2),('cut-04',4),('cut-06',6)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'306 original dwelling '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
for start in [0,5]:
 im=Image.new('RGB',(1200,820),'#edf0f2');dr=ImageDraw.Draw(im);step=24
 for i,y in enumerate(range(start,start+5)):
  ox=40+400*(i%3);oy=45+400*(i//3);dr.text((ox,oy-24),f'y{y} white air / black omitted',fill='black')
  for x in range(size[0]):
   for z in range(size[2]):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
  for x in range(size[0]):dr.text((ox+x*step,oy-12),str(x),fill='black')
  for z in range(size[2]):dr.text((ox-20,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02}.png')
im=Image.new('RGB',(1200,520),'#edf0f2');dr=ImageDraw.Draw(im);step=34
for i,(axis,fixed)in enumerate([('x',5),('z',5)]):
 ox=45+600*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(extent):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=306,status='PRE_FAMILY_CHECK_SAVED_7_PNG_GENERATED_NOT_YET_ACTUALLY_VIEWED',images_generated=7,images_actually_viewed=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Actual7PNG/all10plans/2sections; ladder cap/loft floor and high chest reach need exact source probes, not automatic continuous route.'))
print('7images generated after family precheck; not yet actually viewed.')
