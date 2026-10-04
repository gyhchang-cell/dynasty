"""Single chestplate sample. Native 32px icon, native 64x32 humanoid UV.
Only review-directory files are written. No generators that overwrite global resources.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
D=Path(__file__).resolve().parent;ROOT=D.parents[2];A=D/'candidate/assets/dynasty'
S=ROOT/'src/main/resources/assets/dynasty'
rel=['textures/item/dark_iron_chestplate.png','textures/models/armor/dark_iron_layer_1.png','textures/models/armor/dark_iron_layer_2.png','models/item/dark_iron_chestplate.json']
baseline=[]
for r in rel:
    p=D/'before'/r;p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():shutil.copy2(S/r,p)
    assert p.read_bytes()==(S/r).read_bytes(),r
    baseline.append({'path':str((S/r).relative_to(ROOT)),'backup':str(p.relative_to(D)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
P={'a':'202933','b':'354351','c':'526474','d':'788b94','e':'a5b5b7',
   'f':'574934','g':'896c43','h':'bd9c5e','i':'e0c88b',
   'j':'244e4f','k':'367c79','l':'69b5a4','m':'b5dbc4','n':'182127'}
P={k:'#'+v for k,v in P.items()}
im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
def poly(points,c):d.polygon(points,fill=P[c])
def rect(box,c):d.rectangle(box,fill=P[c])
def line(points,c,width=1):d.line(points,fill=P[c],width=width)
# Frontal equipment silhouette, open collar, distinct shoulders and waist.
poly([(4,4),(9,3),(11,4),(12,7),(14,9),(17,9),(19,7),(20,4),(22,3),(27,4),(29,6),(29,12),(27,15),(24,15),(24,26),(22,29),(9,29),(7,26),(7,15),(4,15),(2,12),(2,6)],'a')
poly([(8,8),(12,9),(19,9),(23,8),(23,25),(21,28),(10,28),(8,25)],'b')
poly([(9,10),(13,11),(18,11),(22,10),(22,22),(20,26),(11,26),(9,22)],'c')
# Raised collar traces the cut-out without filling its transparency.
line([(10,5),(11,8),(14,10),(17,10),(20,8),(21,5)],'g')
line([(11,5),(12,7),(14,9),(17,9),(19,7),(20,5)],'i')
line([(12,9),(14,11),(17,11),(19,9)],'h')
# Two layered shoulder plates; same construction, restrained unequal light.
poly([(4,5),(9,4),(11,6),(11,11),(9,13),(4,12),(3,10),(3,7)],'g')
poly([(4,6),(9,5),(10,6),(10,10),(8,12),(4,11)],'d')
line([(4,6),(8,5),(9,6)],'e');line([(4,7),(4,10)],'c')
line([(3,11),(5,13),(9,14),(10,12)],'h')
poly([(21,6),(22,4),(27,5),(28,7),(28,11),(27,12),(22,13),(20,11)],'g')
poly([(22,6),(23,5),(27,6),(27,10),(25,12),(22,11)],'c')
line([(22,6),(25,5),(27,6)],'d');line([(22,7),(22,10)],'d')
line([(21,12),(22,14),(26,13),(28,11)],'h')
line([(4,14),(7,15)],'b');line([(25,15),(27,14)],'b')
# Two breastplates slope toward the central fastener; no perspective rendering.
poly([(9,12),(13,12),(14,14),(14,17),(12,18),(9,16)],'d')
line([(9,12),(12,12),(13,13)],'e')
poly([(18,12),(22,12),(22,16),(19,18),(17,17),(17,14)],'c')
line([(18,12),(21,12)],'d');line([(21,13),(21,15)],'d')
line([(9,17),(12,19),(15,19),(15,20)],'a')
line([(22,17),(19,19),(16,19),(16,20)],'a')
line([(9,18),(12,20),(14,20)],'h');line([(22,18),(19,20),(17,20)],'g')
# Small jade clasp set in copper; accent is 3px wide, armor remains steel.
poly([(15,11),(17,13),(17,16),(15,18),(13,16),(13,13)],'f')
poly([(15,12),(16,13),(16,16),(15,17),(14,16),(14,13)],'h')
line([(15,13),(15,16)],'k');d.point((15,13),fill=P['m']);d.point((15,14),fill=P['l'])
# Four broad lames separated by short seams, with side buckles instead of noise.
rect((10,21,21,22),'b');line([(11,21),(20,21)],'d');line([(10,23),(21,23)],'a')
line([(11,24),(20,24)],'d');line([(10,25),(21,25)],'b')
line([(8,17),(8,24)],'a');line([(23,17),(23,24)],'a')
for x in (8,22):
    rect((x,19,x+1,20),'f');d.point((x,19),fill=P['h'])
    rect((x,23,x+1,24),'f');d.point((x,23),fill=P['h'])
# A simple belt and two short lower plate panels make a chestplate, not a robe.
line([(9,26),(22,26)],'g');line([(10,26),(21,26)],'h')
rect((14,25,17,27),'f');rect((15,26,16,26),'l')
line([(10,28),(13,28)],'g');line([(18,28),(21,28)],'g');line([(15,28),(16,28)],'b')
im.save(A/'textures/item/dark_iron_chestplate.png')

# Worn texture has its OWN authored patterns. Only body/arm islands of layer1 change.
atlas=Image.open(D/'before/textures/models/armor/dark_iron_layer_1.png').convert('RGBA')
mask=Image.new('1',(64,32));md=ImageDraw.Draw(mask)
def tile(x,y,rows):
    assert len(set(map(len,rows)))==1
    t=Image.new('RGBA',(len(rows[0]),len(rows)))
    t.putdata([tuple(bytes.fromhex(P[c][1:]))+(255,) for row in rows for c in row])
    atlas.paste(t,(x,y));md.rectangle((x,y,x+t.width-1,y+t.height-1),fill=1)
front=['hbaaaabh','bdhbbhcb','cddhhccb','cddklccb','bccmkccb','ahcjjcga',
       'bbchhcbb','cddbbccb','abbbbbba','cddbbccb','ghhllhhg','abbbbbba']
back=['gbbbbbhg','bccddccb','bccccccb','bcccaccb','acccccca','abbbbbba',
      'bccddccb','acccccca','bccccccb','bccccccb','ghhhhhhg','abbbbbba']
side=['gbbh','bccc','bccc','abca','abca','abca','abca','bccc','abca','bccc','ghhg','abba']
tile(20,20,front);tile(32,20,back);tile(16,20,side);tile(28,20,[r[::-1] for r in side])
tile(20,16,['gbbbbbhg','bccccccb','bdcccccb','gbbbbbhg'])
tile(28,16,['abbbbbba','abbbbbba','abbbbbba','abbbbbba'])
armfront=['hiih','gddg','hcdg','gbbg','acca','bccb','abba','bccb','abba','bccb','ghhg','abba']
armback=['ghhg','gccg','hbbg','gbbg','acca','bccb','abba','bccb','abba','bccb','ghhg','abba']
armside=['hiih','gcdg','hccg','gbbg','abca','bcca','abba','bcca','abba','bcca','ghhg','abba']
tile(44,20,armfront);tile(52,20,armback);tile(40,20,armside);tile(48,20,[r[::-1] for r in armside])
tile(44,16,['ghhg','hddh','hdch','ghhg']);tile(48,16,['abba','abba','abba','abba'])
atlas.save(A/'textures/models/armor/dark_iron_layer_1.png')
mask.convert('L').point(lambda v:255 if v else 0).save(D/'qa/edited-uv-mask.png')
old=Image.open(D/'before/textures/models/armor/dark_iron_layer_1.png').convert('RGBA')
changes=[(x,y) for y in range(32) for x in range(64) if atlas.getpixel((x,y))!=old.getpixel((x,y))]
assert all(mask.getpixel(q) for q in changes)
assert {v for _,v in im.getchannel('A').getcolors()}=={0,255}
assert atlas.size==(64,32) and im.size==(32,32)
assert atlas.getchannel('A').getextrema()==(255,255)
for b in baseline:assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256']

F='/System/Library/Fonts/Supplemental/Arial Unicode.ttf';f=ImageFont.truetype(F,22);s=ImageFont.truetype(F,15)
c=Image.new('RGB',(990,555),'#e8e9df');q=ImageDraw.Draw(c)
q.text((24,18),'玄铁重铠 · 胸甲样张',font=f,fill='#263831')
q.text((24,54),'深钢护片 / 铜金收边 / 青玉扣 · 原生32×32平面物品图标',font=s,fill='#657363')
for x,tex,title in [(24,Image.open(D/'before/textures/item/dark_iron_chestplate.png').convert('RGBA'),'项目现图'),(364,im,'新样张')]:
    q.text((x,96),title,font=f,fill='#263831')
    for yy in range(16):
        for xx in range(16):q.rectangle((x+xx*16,136+yy*16,x+xx*16+15,136+yy*16+15),fill=('#d2d9cc','#c0cbb9')[(xx+yy)%2])
    big=tex.resize((256,256),Image.Resampling.NEAREST);c.paste(big,(x,136),big)
    c.paste(tex,(x,420),tex);q.text((x+45,427),'1×原尺寸',font=s,fill='#657363')
q.text((704,96),'物品栏小图',font=f,fill='#263831')
for i,size in enumerate([16,32,64]):
    y=140+i*93;q.rectangle((704,y,781,y+77),fill='#37453f')
    t=im.resize((size,size),Image.Resampling.NEAREST);c.paste(t,(704+(78-size)//2,y+(78-size)//2),t)
    q.text((800,y+29),str(size)+'px 显示',font=s,fill='#657363')
q.line((24,481,966,481),fill='#becab8');q.text((24,501),'清楚的领口、肩甲与腰甲；穿戴贴图单独按人体 UV 绘制。此为候选，未覆盖源文件。',font=s,fill='#657363')
c.save(D/'icon-comparison.png')
sheet=Image.new('RGB',(1050,630),'#e8e9df');q=ImageDraw.Draw(sheet)
q.text((20,16),'穿戴图集 · 64×32 · 仅改胸甲使用的躯干与双臂区域',font=f,fill='#263831')
for y,t,title in [(70,old,'原图：全幅渐变、横纹与随机磨损'),(352,atlas,'新稿：按身体部位组织甲片；头盔、腿部和未使用区域原样保留')]:
    q.text((20,y),title,font=s,fill='#657363');sheet.paste(t.resize((448,224),Image.Resampling.NEAREST),(20,y+32))
q.text((510,100),'双臂共用同一 UV，左臂镜像。',font=s,fill='#657363')
q.text((510,136),'layer_2 不改；不修改模型、注册或数值。',font=s,fill='#657363')
q.text((510,390),'只有胸甲层的 body + arms 贴图区发生变化。',font=s,fill='#657363')
q.text((510,425),'颜色与亮色不等于实现发光。无新增动画。',font=s,fill='#657363')
sheet.save(D/'uv-comparison.png')
manifest={'id':'dynasty:dark_iron_chestplate','name':'玄铁重铠·胸甲','status':'sample_only_waiting_for_user_confirmation',
 'icon':{'path':'candidate/assets/dynasty/textures/item/dark_iron_chestplate.png','dimensions':[32,32],'alpha':[0,255],'visible_colors':len({p[:3] for p in im.getdata() if p[3]})},
 'worn':{'path':'candidate/assets/dynasty/textures/models/armor/dark_iron_layer_1.png','dimensions':[64,32],'alpha':[255],
 'edited_uv_only':'body and shared mirrored arms','changed_pixels':len(changes),'outside_chest_uv_changes':0,'layer2_unchanged':True},
 'reference':{'item_model':'minecraft:item/generated','layer0':'dynasty:item/dark_iron_chestplate','armor_material':'dynasty:dark_iron','worn_layer':'dark_iron_layer_1.png'},
 'baseline':baseline,'installed':False,'game_tested':False,'new_emissive_rendering':False,'animation':False,
 'completion_evidence':'Existing legacy item copied from old xuantian; existing worn layers are dark recolors. Already hooked up, not absent. No dedicated later remaster/approval record found.',
 'protected_completed_armor':['general','jade','sky','bronze','xuantian'],
 'authorization':'v13 copper mirror style approved. User requested one armor sample before bulk work; armor style confirmation remains pending.'}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'icon_colors':manifest['icon']['visible_colors'],'changed_uv_pixels':len(changes),'source_files_preserved':len(baseline),'sample':'one chestplate'},ensure_ascii=False))
