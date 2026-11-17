import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from whole_building_candidates import AIR,iso,color

def ld(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
f007=R/'docs/architecture/research-20261101-dungeons-007/manual-review.json';f165=R/'docs/architecture/research-20261104-smithy-165/manual-review.json';f297=R/'docs/architecture/research-20261104-smithy-297/manual-review.json';f301=R/'docs/architecture/research-20261104-smithy-301/manual-review.json'
put('pre-render-family-check.json',dict(batch=304,order='本文件先于本批PNG生成写入。原palette/37BE/15全层索引及下列旧文字已实际阅读；然后才render。',old007F01=dict(binding=bind(f007),observations=next(x for x in ld(f007)['entries']if x['id']=='F01')['observations']),old165F01=dict(binding=bind(f165),observations=ld(f165)['cases'][0]['screening_observations']),other_whole_bindings=[bind(f297),bind(f301)],assessment='不是007F04/301的3×3方室四外柱减少檐层换内装：本体为长矩形公共厅+侧隔间，上两标高各三床，东侧长直阶到中层、转西继续上行。不是297双门小方双层四床，亦不同007F01只有书室无可达阁层。165同三层工住但绕北中央柱多次折转、中间书厅/顶三床；本栋东南长直+西转、两睡层/共六床与底层餐桌/迎客入口组织不同。相同木框白填墙/瓦阶不可单独算独立，但整栋服务/上下分配可进入完整空间研究。',purpose_evidence='原hanging_sign前面写Traveller\'s / Inn / OPEN，背面CLOSED；三粉床在y6、三红床y10；底层多组桌椅/公共空带。不是单凭cherry或big_house文件名授予客栈用途。',qualification='PROVISIONAL_COMPLETE_EAST_ASIAN_INN_SPATIAL_CANDIDATE_PENDING_FULL_IMAGES_AND_ROUTES',limits=['不宣称中国/徽派文化资格；原白旗红圆图样保留为作者原语境，不挪用或改名生产。','指示牌/床只支持原设计旅宿用途，尚未验收实际营业、付款、餐食、中文或NPC。','没有历史hash命中不是语义唯一证明；原范围的独立相关性还需Main判定。'],formal_credit_added=0))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
for name,cut in [('whole',None),('cut-03',3),('cut-07',7),('cut-11',11)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'304 original inn '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
for start in [0,5,10]:
 im=Image.new('RGB',(1200,920),'#edf0f2');dr=ImageDraw.Draw(im);step=20
 for i,y in enumerate(range(start,start+5)):
  ox=40+400*(i%3);oy=45+450*(i//3);dr.text((ox,oy-24),f'y{y} white air / black omitted',fill='black')
  for x in range(size[0]):
   for z in range(size[2]):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
  for x in range(size[0]):dr.text((ox+x*step,oy-12),str(x),fill='black')
  for z in range(size[2]):dr.text((ox-20,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02}.png')
im=Image.new('RGB',(1200,520),'#edf0f2');dr=ImageDraw.Draw(im);step=25
for i,(axis,fixed)in enumerate([('x',8),('z',13)]):
 ox=45+600*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(extent):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=304,status='PRE_FAMILY_CHECK_SAVED_8_IMAGES_GENERATED_NOT_ACTUALLY_VIEWED',images_generated=8,images_actually_viewed=0,new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Actual8PNG including all15plans/2sections,5JSON, exact multi-level routes/headroom and source omissions.'))
print('Saved family precheck, 8 source-category images; not yet actually viewed.')
