import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from whole_building_candidates import AIR,iso,color

def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
olds={str(n):R/f'docs/architecture/research-20261104-smithy-{n}/manual-review.json' for n in [249,297,304,306]}
review=R/'docs/cod4/audit-20261022/coordinator-building306-actual-sevenPNG-whole-NPC03-auxiliary-review-20261114.json'
assert bind(review)['sha256']=='c1b43869ad28bfbce45cf335bd8d2f44606f167eb238e336473afbbe98c5626e'
put('Main306-bounded-qualification-carry.json',dict(binding=bind(review),status=ld(review)['status'],judgments=ld(review)['Main_independent_judgments'],accepted_auxiliary_instances=1,strict_Chinese_or_Hui_or_thatch_credit=0,scope_total=None,scope_shortfall=None,gate_met=False,credit_transferred_to307=0))
put('pre-render-family-check.json',dict(batch=307,order='全81palette及Properties/14BE/10层130行1690原格先读，旧249/297/304/306整栋七维实际读后保存此判断，再生成PNG。',old_whole_comparisons={n:dict(binding=bind(f),seven_dimensions=ld(f)['seven_dimensions']) for n,f in olds.items()},errata={'298':'297比例中底层8床块应是全屋8床块；下2床/上2床，共4床。','302':'301无同9×9主基资格；实际主房x2..6/z2..6，外柱x1/7/z1/7，roofx1..7/z0..8。'},current_spatial_reading='west门入下层西低通道，东x6..9底oak半砖抬平台配两对向座阶，西南三烛/四烛与珊瑚扇陈设。南后部x8→7→6→5沿west逐级上，至y4北向接上层半砖睡区。北两张粉床，南屋内开口与中间坐台。单栋双层住居，非两栋或营业客栈。',comparison='与297同为两使用层但其下层两床/上两床、north中段直阶；本源下层无床而有整体抬高休坐区，上层两床，south边阶及局部楼面敞口。与306单床室+墙梯屋内储藏平台、249单室无梯隐桶及304公共三桌+三床两睡层的分配不同。白填墙木架黑深盖同族风险保留，不能只凭楼梯/床数/尺寸视为独立。',purpose='cod2 DUN05废弃民居/屋盖内竖向交通的广义东亚双层居住空间辅助：真实两床/框架白墙/深砖双坡盖/室内阶，而非仅cherry目录名。无徽派马头墙/中式文化证明/屋顶相连巷道/纸扎人，严格用途资格0。无外竹林证据，不挪用306的NPC03林居资格。',decision='PROVISIONAL_TWO_LEVEL_DWELLING_SPATIAL_AUXILIARY_PENDING_INDEPENDENT_REVIEW_NOT_STRICT_HUI',formal_credit_added=0))
a=ld(P/'source-context.json')['resources'];b=ld(R/'docs/architecture/research-20261104-smithy-304/source-context.json')['resources'];assert a==b
put('context-reuse.json',dict(current=bind(P/'source-context.json'),prior304=bind(R/'docs/architecture/research-20261104-smithy-304/source-context.json'),all5_full_original_JSON_objects_equal=True,prior_full_bodies_actually_read=True,reading='复用同会话304已全文实际读过的5个相同资源正文，不重读/重计新建筑。307实际补读本屋selected entry。',selected=next(v for v in a[1]['json']['elements']if v['element'].get('location')=='trek:village/cherry/houses/cherry_medium_house_2'),limits='复用source上下文，不迁304建筑语义/acceptance/信用。'))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
for name,cut in [('whole',None),('cut-02',2),('cut-04',4),('cut-06',6)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'307 original dwelling '+name,cut),(760*i,0))
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
for i,(axis,fixed)in enumerate([('x',6),('z',6)]):
 ox=45+600*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(extent):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=307,status='PRE_FAMILY_CHECK_SAVED_7_PNG_GENERATED_NOT_YET_ACTUALLY_VIEWED',images_generated=7,images_actually_viewed=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Actual7PNG/all10plans/2sections; raised platform, west stairs/landing and beds/chest headroom require exact probes; not native collision.'))
print('7images generated after family precheck; not yet actually viewed.')
