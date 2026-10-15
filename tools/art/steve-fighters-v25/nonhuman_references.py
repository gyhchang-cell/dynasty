"""Research only: source cuboid reconstruction, never a native game screenshot.

No assets are copied into the game. Java is parsed conservatively, not executed.
Literal boxes, bind-pose transforms and hierarchy only; no animation or UV masks.
Run with the bundled Python (numpy and Pillow). Downloads are pinned official TF
source and cached only inside the research documentation output directory.
"""
from pathlib import Path
import re, json, math, hashlib, urllib.request, subprocess, ast, shutil, html
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/art/steve-fighters-v25/nonhuman-references'
AM = ROOT / 'build/nonhuman-reference/alexsmobs'
CACHE = ROOT / 'build/nonhuman-reference/reconstruction-cache'
TF_SHA = 'e5d776e3b18258548f7fd618adf65315fbc8d053'
TF_MODELS = ['Bunny', 'Penguin', 'DeathTome', 'HarbingerCube',
             'newmodels/NewBoar', 'newmodels/NewDeer', 'newmodels/NewBighorn',
             'newmodels/NewFireBeetle', 'newmodels/NewHelmetCrab',
             'newmodels/NewPinchBeetle', 'newmodels/NewSlimeBeetle',
             'newmodels/NewSquirrel', 'newmodels/NewTinyBird', 'newmodels/NewRaven']
GOETY_SHA = '02adbe7491767210f63857fa763a6f1de1262cbd'
GOETY_MODELS = ['Snapper', 'CarrionMaggot', 'Leapleaf']
# Observations from visual inspection of all ten corrected sheets. The final
# field is a shape/interaction focus, not a verified gameplay attack claim.
VISUAL_NOTES = '''
低扁叠壳与前伸头|四条外展短足|前颚
细长躯干与超长尾|四条直足|尖吻与细舌
折叠侧翼与高头|双腿宽爪|钩喙
低长分段躯干|腹面滑行，无腿|前端触角
高肩厚胸与低头|粗四足|前吻与侧角
厚头短鱼身|腹鳍侧鳍尾板|前口
小头横身与直尾|短腿与贴身双翼|短喙
宽头长耳与竖躯干|后足宽底|前口与短前肢
超长水平鲸身|胸鳍与水平尾叶|大前头
低长吻与长尾|外展短四足|前吻
小头横身与抬升尾|四条细长足|手部与前吻
厚头长鱼身与尾板|侧鳍腹鳍|前口须
低腹与背翼覆片|三对平面足|前触角
上下叠合胶体|无实体足，水中漂浮|纹理细节缺失，器官不可判定
长身与下折前嘴|腹部短附肢与侧翼|双段长颚
窄身与高背鳍|腹侧鳍与尾叶|小前口
小虫胸与巨大侧面片|细足与背翼|长刺吻
长吻厚躯干与长尾|短四足|分段前颚
斜躯干与折侧翼|双足|前喙
紧凑鱼身与大尾板|背鳍侧鳍|小口
圆厚头与块状横身|短粗四足|宽前吻
高头大耳与横身|粗四足|长鼻与象牙
高长颈与短尾|长双腿宽脚|短喙
梯级头与分节横身|多对短足|前吻
方头细杆与放射底部|细长放射附肢，无常规足|底部接触附肢
箱状腹与上展花瓣|底部短附肢，漂浮形态|花瓣与中央头
方腹与交叉薄翼|薄腿面片|前端头部
窄长鱼身与展侧鳍|背鳍侧鳍尾叶|前口
细长鱼身与低颚|多处鳍片|前颚
窄高躯干与长尾|双腿宽足|长吻与头顶突起
细身长颈与双直角|细长四足|额角
厚前头与上扬长尾|短四足|前口
垂直细长鱿鱼默认姿态|下垂腕与两根超长触腕|腕端；默认姿态非游动姿态
厚胸与小后躯|长前臂短后足|前臂与前口
厚背与下伸前头|粗四足|前吻
上下叠块与中部缩腰|无实体腿，悬浮|整团形态；灰模无旋风透明效果
长鱼身与横宽头|多鳍与竖尾叶|横锤头与前口
小直立身与长细喙|微小足与折翼|长喙
小前身与大后躯|大后足小前肢|前吻与耳
高前胸与水平粗尾|大后腿，尾作平衡|前肢与前吻
长低躯干与折尾|短四足|长吻与舌
超长前颈与宽低背|侧面大鳍片|前端颚
三段虫身与上举叶片|多条细足|前头；携带叶片非身体
低长壳与扇尾|薄足片与前钳|双前钳
高腿横躯与长耳|四条细长足|前吻
厚分节腹与高眼柄|前附肢与腹下足片|折叠前击肢
低头囊与放射腕|八条折腕|腕端
重叠立方外壳|无可见腿|纹理决定的五官未重建
长腿大身与宽额部|四条长足|额部角结构
低鱼身与凸眼|胸鳍与尾叶|前口
高方身与头顶片|双短足|前面细长突起
长鱼身与高背鳍|胸鳍与水平尾叶|宽前吻
低横身与扁尾|四片低足|宽扁前喙
竖头身与短喙|双短腿与贴身翼|前口
低横身与直长尾|短四足|前吻与前爪
扁宽头与凸双眼|外展后足与小前足|宽前口
低长渐细蛇身|无足，腹面|前口与尾端
厚胸低头与翘角|粗四足|鼻角
前倾头颈与上翘尾|双腿与侧翼|尖喙
壳状分层背部|短四足|前头；灰面片无法显示甲片边缘
高厚熊躯与背鳍|四足与尾板|前吻
中高头与横身|短双足与侧翼|粗喙
低长身与分叉尾端|胸鳍与后鳍|宽前口
高头斜身与大嘴|长双腿，折侧翼|宽厚喙
窄骨架鱼身与长刺吻|薄鳍与尾板|前刺
大头与细长前肢|双足与长前肢|前肢；直立默认姿态
低长身与上竖大尾|短四足|尾部轮廓与前吻
低身与上卷长尾|粗四足|前吻与爪
前伸颈与上折翼|双足与大双翼|钩喙
扁平长身与尾片|宽薄漂浮面片|头部纹理器官不可判定
宽上身与两根高立柱|短双腿|上部结构；投射机制未研究
宽头短身与长尾板|侧鳍与尾片|前口
低小躯干与扁膜|四肢与滑翔膜|前吻
细身巨大展开翼|双翼，足细小|前喙
分节虫身与平面大翼|多足与双翼|前口与尾刺候选
紧凑横身与短尾|短四足|厚前吻
低扁壳与前方头|四条短足|前口
高横身与下垂尾|粗四足|前吻与爪
大长喙与斜身|双足与贴侧翼|长厚喙
扁盾背与双尾丝|腹侧足面片|前触角与尾丝
高肩厚躯与低头|粗四足|翘牙
高虫胸与放射附片|长足与侧翼|尖吻与前附肢
厚宽蛙头与凸眼|外展粗后足与短前足|宽口
小身大头与双长耳|短四足|前口
方头竖身与侧翼|双扁足|小喙
中央书体与分离薄页|无腿，悬浮|书页；默认姿态未施加纸页风暴动画
大立方体与底足|四短足|整块体，纹理五官不可判定
粗横身与低前头|短粗四足|前吻
小横身高颈与宽角片|四条细长足|额角；灰片未应用透明镂空
横身厚头与卷角|四足|弯曲额角
厚腹小前头与长触须|三对外展腿|前口与触角
低蟹身与倾斜头盔|四条外展腿|双钳；角片透明轮廓缺失
厚腹与双巨钳|三对外展腿|宽大前钳
低虫身与高举尾囊|三对外展腿|尾囊与前口
小身与折升大尾|短四足|前口；尾轮廓可借鉴鼠类
小方头横身与尖尾片|微小双足与侧翼|小喙
斜横鸟身与侧折翼|双足，采用源码落地Y=21|前喙
厚鱼身与斜分层颚|侧鳍背鳍尾叶|大前颚
低矮四段蛆身|无实体足，腹面|小前头
前倾植物躯干与放射花瓣|四个块状接地点|花冠与大前附肢
'''.strip().splitlines()
# Explicit identity exclusions: equipment, particles, variants, humanoids, and
# incomplete multipart rigs. Those need separate entity assembly, not overlay.
EXCLUDE = set('Anaconda AncientDart BisonBaby BlobfishDepressurized BoneSerpentBody BoneSerpentHead BoneSerpentTail CatfishMedium CatfishSmall CaveCentipede EndPirateAnchor EndPirateAnchorChain EndPirateAnchorWinch EndPirateDoor EndPirateFlag EndPirateShipWheel Fart FlutterPotted LeafcutterAntQueen MurmurBody MurmurHead MurmurNeck MysteriousWorm PollenBall RockyChestplateRolling ShieldOfTheDeep SquidGrapple Straddleboard TarantulaHawkBaby TendonClaw TransmutationTable UnderminerDwarf VoidWorm VoidWormBeak VoidWormBody VoidWormShot VoidWormTail WanderingVillagerRider Farseer'.split())
NUM = re.compile(r'^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?[fFdD]?$')

def numbers(s):
    s=re.sub(r'(?:Maths\.rad|MathHelper\.modelDegrees)\(([-+\d.fF]+)\)',lambda m:str(math.radians(float(m[1].rstrip('fF')))),s)
    for k,v in [('Mth.HALF_PI',math.pi/2),('Mth.PI',math.pi),('Math.PI',math.pi)]:s=s.replace(k,str(v))
    vals = s.split(',')
    def evaluate(x):
        x=re.sub(r'(\d)[fFdD]\b',r'\1',x).strip()
        tree=ast.parse(x,mode='eval')
        def ev(n):
            if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):return n.value
            if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):return ev(n.operand)*(1 if isinstance(n.op,ast.UAdd) else -1)
            if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div)):
                a,b=ev(n.left),ev(n.right)
                return a+b if isinstance(n.op,ast.Add) else a-b if isinstance(n.op,ast.Sub) else a*b if isinstance(n.op,ast.Mult) else a/b
            raise ValueError(x)
        return float(ev(tree.body))
    try:return [evaluate(x) for x in vals]
    except (SyntaxError,TypeError):raise ValueError(s)

def strip_comments(s):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', s, flags=re.S)

def block(s, pos):
    start=s.index('{', pos); depth=1; end=start+1
    while depth:
        depth += (s[end]=='{')-(s[end]=='}'); end+=1
    return s[start+1:end-1]

def part():
    return dict(pos=[0,0,0], rot=[0,0,0], parent=None, boxes=[])

def boxes(s, p, rejected):
    for m in re.finditer(r'\.addBox\(([^;]*?)\)', s):
        args=m[1].split(',')
        try:
            v=numbers(','.join(args[:6]))
            if len(v)!=6: raise ValueError()
            inflate=0
            if len(args)>6 and NUM.fullmatch(args[6].strip()): inflate=numbers(args[6])[0]
            elif len(args)>6:
                d=re.search(r'CubeDeformation\(([-\d.fF]+)',args[6])
                if d: inflate=numbers(d[1])[0]
            p['boxes'].append(dict(origin=[x-inflate for x in v[:3]], size=[x+2*inflate for x in v[3:]]))
        except ValueError: rejected.append(m[0])

def parse_am(source, name):
    s=strip_comments(source); m=re.search(r'public\s+Model'+name+r'\s*\(',s)
    if not m: return {}, ['missing constructor']
    s=block(s,m.end()); parts={}; rejected=[]
    # Refuse procedural/conditional constructor assembly instead of flattening it.
    if re.search(r'\b(switch|for|while)\s*\(',s): return {}, ['procedural constructor']
    for statement in s.split(';'):
        for m in re.finditer(r'(\w+)\s*=\s*new AdvancedModelBox\(',statement): parts[m[1]]=part()
        m=re.search(r'(\w+)\.(?:setPos|setRotationPoint)\(([^)]+)\)',statement)
        if m and m[1] in parts:
            try: parts[m[1]]['pos']=numbers(m[2])
            except ValueError: rejected.append(m[0])
        m=re.search(r'(\w+)\.addChild\((\w+)\)',statement)
        if m and m[2] in parts: parts[m[2]]['parent']=m[1]
        m=re.search(r'setRotationAngle\((\w+),(.*)\)\s*$',statement.strip(),re.S)
        if m and m[1] in parts:
            try: parts[m[1]]['rot']=numbers(m[2])
            except ValueError: rejected.append(m[0])
        m=re.search(r'(\w+)\.(?:setTextureOffset\([^)]*\)\.)?addBox\(',statement)
        if m and m[1] in parts: boxes(statement,parts[m[1]],rejected)
    return parts,rejected

def parse_tf(source):
    s=strip_comments(source)
    method=re.search(r'public static LayerDefinition (?:create|createBodyLayer)\(',s)
    if method:s=block(s,method.end())
    parts={'root':part()}; aliases={}; rejected=[]
    for m in re.finditer(r'(\w+)\s*=\s*\w+\.getRoot\(\)',s): aliases[m[1]]='root'
    # Statements retain the chained builder and final PartPose as one unit.
    for statement in s.split(';'):
        m=re.search(r'(\w+)\.addOrReplaceChild\("([^"]+)"',statement)
        if not m: continue
        parent=aliases.get(m[1]); name=m[2]
        if parent is None: rejected.append('unresolved parent: '+m[1]); continue
        p=part();p['parent']=parent; boxes(statement,p,rejected)
        pose=re.search(r'PartPose\.(offsetAndRotation|offset|rotation)\(([^)]*)\)',statement)
        if pose:
            try:
                v=numbers(pose[2]); p['pos']=v[:3] if pose[1]!='rotation' else [0,0,0]
                p['rot']=v[3:] if pose[1]=='offsetAndRotation' else v if pose[1]=='rotation' else [0,0,0]
            except ValueError: rejected.append('nonliteral pose '+pose[0])
        parts[name]=p
        alias=re.search(r'(\w+)\s*=\s*'+re.escape(m[1])+r'\.addOrReplaceChild',statement)
        if alias: aliases[alias[1]]=name
    if re.search(r'\b(for|while)\s*\(',s[:s.find('@Override') if '@Override' in s else len(s)]):
        rejected.append('procedural pieces omitted')
    return parts,rejected

def rotation(v):
    x,y,z=v;cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]) @ np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]) @ np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])

FACES=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
CORNERS=np.array([[x,y,z] for x in [0,1] for y in [0,1] for z in [0,1]])

def geometry(parts):
    cache={}
    def transform(n):
        if n in cache:return cache[n]
        p=parts[n];t=np.eye(4);t[:3,:3]=rotation(p['rot']);t[:3,3]=p['pos']
        if p['parent'] in parts:t=transform(p['parent'])@t
        cache[n]=t;return t
    faces=[]; points=[]
    for n,p in parts.items():
        t=transform(n)
        for b in p['boxes']:
            v=CORNERS*np.array(b['size'])+b['origin'];v=v@t[:3,:3].T+t[:3,3];v[:,1]*=-1
            points.extend(v)
            for f in FACES:
                q=v[f];normal=np.cross(q[1]-q[0],q[2]-q[0]);ln=np.linalg.norm(normal)
                if ln>1e-8:faces.append((q,normal/ln,n))
    return faces,np.array(points)

def render(faces,points,yaw,size=(320,260)):
    w,h=size;a=math.radians(yaw);e=math.radians(20)
    right=np.array([math.cos(a),0,math.sin(a)]);toward=np.array([math.sin(a)*math.cos(e),math.sin(e),-math.cos(a)*math.cos(e)]);up=-np.cross(toward,right)
    basis=np.array([right,up,toward]);pr=points@basis.T;lo=pr.min(0);hi=pr.max(0);mid=(lo+hi)/2;scale=min((w-35)/max(1,hi[0]-lo[0]),(h-35)/max(1,hi[1]-lo[1]))
    rgb=np.full((h,w,3),238,dtype=np.uint8);depth=np.full((h,w),-np.inf)
    light=np.array([-.4,.8,-.5]);light/=np.linalg.norm(light)
    for q,n,name in faces:
        p=(q@basis.T-mid)*[scale,-scale,1]+[w/2,h/2,0]
        col=int(105+95*abs(n@light))
        for idx in [(0,1,2),(0,2,3)]:
            tri=p[list(idx)];x0=max(0,int(np.floor(tri[:,0].min())));x1=min(w-1,int(np.ceil(tri[:,0].max())));y0=max(0,int(np.floor(tri[:,1].min())));y1=min(h-1,int(np.ceil(tri[:,1].max())))
            if x0>x1 or y0>y1:continue
            xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8:continue
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;ww=1-u-v;z=u*a[2]+v*b[2]+ww*c[2];old=depth[y0:y1+1,x0:x1+1];mask=(u>=0)&(v>=0)&(ww>=0)&(z>old)
            rgb[y0:y1+1,x0:x1+1][mask]=col;old[mask]=z[mask]
    return Image.fromarray(rgb)

def font(n):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',n)

def run():
    OUT.mkdir(parents=True,exist_ok=True);(CACHE/'sources').mkdir(parents=True,exist_ok=True);(CACHE/'geometry').mkdir(exist_ok=True)
    # Migrate this script's earlier source cache into the ignored research tree.
    if (OUT/'sources').exists():
        for file in (OUT/'sources').glob('*.java'):shutil.move(str(file),str(CACHE/'sources'/file.name))
        (OUT/'sources').rmdir()
    for file in OUT.glob('[0-9][0-9][0-9]-*.json'):shutil.move(str(file),str(CACHE/'geometry'/file.name))
    sha=subprocess.check_output(['git','-C',str(AM),'rev-parse','HEAD'],text=True).strip()
    records=[];excluded=[]
    for path in sorted((AM/'src/main/java/com/github/alexthe666/alexsmobs/client/model').glob('Model*.java')):
        name=path.stem[5:]
        if name in EXCLUDE:excluded.append({'name':name,'reason':'variant/item/humanoid or multipart exclusion'});continue
        src=path.read_text();parts,warnings=parse_am(src,name)
        records.append((name,'AlexsMobs',sha,'https://github.com/AlexModGuy/AlexsMobs/blob/'+sha+'/'+str(path.relative_to(AM)),src,parts,warnings))
    for name in TF_MODELS:
        relative='src/main/java/twilightforest/client/model/entity/'+name+'Model.java'
        url='https://raw.githubusercontent.com/TeamTwilight/twilightforest/'+TF_SHA+'/'+relative
        cache=CACHE/'sources'/(name.split('/')[-1]+'Model.java')
        if not cache.exists():cache.write_bytes(urllib.request.urlopen(url,timeout=20).read())
        src=cache.read_text();parts,warnings=parse_tf(src)
        if name.endswith('NewRaven'):
            for leg in ['right_leg','left_leg']:parts[leg]['pos'][1]=21.0
            warnings.append('Raven feet use source setupAnim isBirdLanded Y=21, not initial layer Y=0; all other transforms are bind pose.')
        records.append((name.split('/')[-1].removeprefix('New'),'TwilightForest',TF_SHA,'https://github.com/TeamTwilight/twilightforest/blob/'+TF_SHA+'/'+relative,src,parts,warnings))
    for name in GOETY_MODELS:
        relative='src/main/java/com/Polarice3/Goety/client/render/model/'+name+'Model.java'
        cache=CACHE/'sources'/(name+'Model.java')
        if not cache.exists():cache.write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/Polarice3/Goety-2/'+GOETY_SHA+'/'+relative,timeout=20).read())
        src=cache.read_text();parts,warnings=parse_tf(src)
        records.append((name,'Goety',GOETY_SHA,'https://github.com/Polarice3/Goety-2/blob/'+GOETY_SHA+'/'+relative,src,parts,warnings))
    ledger=[];cards=[]
    for name,mod,commit,url,src,parts,warnings in records:
        faces,pts=geometry(parts)
        if len(faces)<6 or len(pts)<8:excluded.append({'name':name,'reason':'no usable literal geometry','warnings':warnings});continue
        idx=len(ledger)+1;key=f'{idx:03d}-{mod.lower()}-{name.lower()}'
        # Persist the exact interpreted data for independent audit.
        (CACHE/'geometry'/(key+'.json')).write_text(json.dumps(parts,indent=2))
        card=Image.new('RGB',(640,355),'white');d=ImageDraw.Draw(card)
        d.text((12,8),f'{idx:03d}  {name}  / {mod}',font=font(20),fill='#202020')
        card.paste(render(faces,pts,40),(0,40));card.paste(render(faces,pts,100),(320,40))
        ext=np.ptp(pts,axis=0);bcount=sum(len(p['boxes']) for p in parts.values())
        d.text((12,300),f'{bcount} cuboids | W/H/L {ext[0]:.1f}/{ext[1]:.1f}/{ext[2]:.1f} model px',font=font(14),fill='#333333')
        d.text((12,324),'SOURCE GRAY RECONSTRUCTION | no texture / animation / renderer scale',font=font(12),fill='#555555')
        card.save(OUT/(key+'.png'));cards.append(card)
        organ=[n for n in parts if re.search(r'jaw|fang|claw|horn|beak|mouth|mandible|snout',n,re.I)]
        support=[n for n in parts if re.search(r'leg|foot|feet|wing|fin|flipper|tentacle|tail',n,re.I)]
        observation=VISUAL_NOTES[idx-1].split('|')
        ledger.append(dict(index=idx,identity=name,mod=mod,commit=commit,source=url,sha256=hashlib.sha256(src.encode()).hexdigest(),image=key+'.png',geometry_local_ignored=str((CACHE/'geometry'/(key+'.json')).relative_to(ROOT)),cuboids=bcount,model_bounds_px=ext.round(3).tolist(),layout=observation[0],support_observation=observation[1],attack_or_interaction_shape=observation[2],support_parts=support,attack_or_interaction_candidates=organ,limitations=warnings+['Literal bind pose only (Raven source landed feet excepted); zero-thickness planes are opaque gray, ignoring alpha masks.','No animations, runtime scales, inherited cuboids, renderer layers or attack semantics reconstructed.'],visually_reviewed=True))
    for start in range(0,len(cards),10):
        sheet=Image.new('RGB',(1280,1820),(224,224,224));d=ImageDraw.Draw(sheet);d.text((14,8),f'Nonhuman source study {start+1:03d}-{min(start+10,len(cards)):03d} | two views / identity',font=font(20),fill='#222222')
        for j,card in enumerate(cards[start:start+10]):sheet.paste(card,((j%2)*640,45+(j//2)*355))
        sheet.save(OUT/f'sheet-{start//10+1:02d}.png')
    (OUT/'ledger.json').write_text(json.dumps(ledger,indent=2));(OUT/'excluded.json').write_text(json.dumps(excluded,indent=2))
    active={r['image'] for r in ledger}
    for file in OUT.iterdir():
        if re.fullmatch(r'\d{3}-[a-z]+-[a-z]+\.(png|json)',file.name) and file.name not in active:file.unlink()
    header='''# Nonhuman source visual study: 100 identities\n\n100 distinct mob identities, not 100 class names: 83 AlexsMobs, 14 TwilightForest, 3 Goety. All ten corrected sheets inspected visually. Two gray software views per identity. Java Y-down is converted to world Y-up and camera up is positive world Y. Raven additionally uses the explicit landed foot Y=21 from its own setupAnim; initial source Y=0 would detach the feet.\n\nScope caveat: this is **100 nonhuman mobs of mixed sizes**, not evidence that all 100 are small. Whale, elephant, Laviathan, giant squid, Sunbird and other large species are retained as anatomy references, not small-unit scale references. Independently auto-framed cards must not be used to compare in-game sizes. No native screenshots, texture/alpha reconstruction, full animation/rig study, or gameplay attack verification is claimed. Flat alpha-masked legs/wings/antlers appear as opaque rectangles. GiantSquid is an elongated vertical bind pose; DeathTome pages use the unanimated layer layout.\n\nPrimary source commits:\n- AlexModGuy/AlexsMobs: `'''+sha+'''` (local official checkout).\n- TeamTwilight/twilightforest 1.20.x: `'''+TF_SHA+'''` (official pinned source; not claimed identical to the local 4.3.2508 jar).\n- Polarice3/Goety-2 1.20: `'''+GOETY_SHA+'''` (official pinned source; not claimed identical to the local 2.5.51.0 jar).\n\nNo local jar textures copied. No production edits, installs, build, sound, UI or commit. Source cache and interpreted geometry are research artifacts only. `ledger.json` contains every per-source URL, SHA-256, geometry path, cuboid count, per-visual layout/support/interaction observation, and limitations. Items, skins, babies, multipart heads/tails, humanoids and incomplete procedural assemblies do not add identities. IceCrystal and QuestRam are deliberately omitted from the final set.\n\nRelevant design observations: carp_spirit can draw on CosmicCod (16), DevilsHolePupfish (20), Mudskipper (50) and Snapper (98): axial torso, separate tail pivot, thin independent fins, and an explicit jaw rather than a humanoid torso. tree_spirit can draw on Flutter (26) and Leapleaf (100): central plant body, radial canopy/flower parts and low stable contacts; these are plant references rather than literal trees. clockwork_rat can draw on Jerboa (39), Raccoon (55), Skunk (67), SugarGlider (73), Squirrel (95): separate head/ears, four contacts, articulated tail and a horizontally biased small body. These are interpretation notes, not copied assets.\n\n'''
    header+='\n'.join(f'- [Sheet {i:02d}: {(i-1)*10+1:03d}-{i*10:03d}](sheet-{i:02d}.png)' for i in range(1,11))+'\n\n| # | Identity | Layout | Support | Interaction shape (not verified attack) | Primary source |\n|---|---|---|---|---|---|\n'
    header+='\n'.join(f"| {r['index']:03d} | [{r['identity']}]({r['image']}) | {r['layout']} | {r['support_observation']} | {r['attack_or_interaction_shape']} | [{r['mod']}]({r['source']}) |" for r in ledger)+'\n'
    (OUT/'README.md').write_text(header)
    e=html.escape
    intro='100 distinct nonhuman identities · 83 Alex’s Mobs / 14 Twilight Forest / 3 Goety. Mixed sizes; not 100 small species. Source gray reconstructions, two views each. Corrected positive-Y camera. No native screenshots or full animation study.'
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>100 nonhuman source references</title><style>body{font:16px system-ui;margin:30px auto;max-width:1400px;background:#eee;color:#222;padding:0 20px}h1{font-size:28px}nav{display:flex;gap:14px;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:20px}article{background:white;padding:14px;border:1px solid #ccc}img{width:100%;height:auto}p{line-height:1.5}small{color:#555}a{color:#235ba2}.notes{background:#fff;padding:15px;margin:20px 0}</style><h1>100 个非人形 Minecraft 生物：源码视觉研究</h1><p>'+e(intro)+'</p><nav><a href="README.md">研究说明与全部笔记</a><a href="ledger.json">来源台账 JSON</a>'+''.join(f'<a href="sheet-{i:02d}.png">图板 {i:02d}</a>' for i in range(1,11))+'</nav><div class="notes"><b>范围与来源</b><p>不同卡片独立缩放，不能比较游戏尺寸。透明贴图面片会显示为实心灰色长方片；动画、渲染缩放、皮肤和额外渲染层未重建。Raven 双足采用同一源码 setupAnim 明确的落地 Y=21。第三方完整 Java 和转换模型 JSON 仅存于忽略的 build 目录。</p><p>鲤鱼精：16 / 20 / 50 / 98 的轴向鱼身、独立尾鳍和颚。树精：26 / 100 的中央植物躯干、放射花冠与低稳支撑。机关鼠：39 / 55 / 67 / 73 / 95 的独立耳、四足、水平躯干与分节尾。</p></div><div class="grid">'
    for r in ledger:
        page+=f'<article id="ref-{r["index"]:03d}"><h2>{r["index"]:03d} {e(r["identity"])}</h2><a href="{r["image"]}"><img loading="lazy" src="{r["image"]}" alt="{e(r["identity"])} 两视角灰模"></a><p><b>布局：</b>{e(r["layout"])}<br><b>支撑：</b>{e(r["support_observation"])}<br><b>交互形状：</b>{e(r["attack_or_interaction_shape"])}</p><a href="{e(r["source"])}">{e(r["mod"])} 官方源码 · {r["commit"][:12]}</a><p><small>{r["cuboids"]} cuboids · '+e(' '.join(r['limitations']))+'</small></p></article>'
    (OUT/'index.html').write_text(page+'</div></html>')
    print(json.dumps({'usable_identities':len(ledger),'by_mod':{m:sum(r['mod']==m for r in ledger) for m in ['AlexsMobs','TwilightForest','Goety']},'output':str(OUT)},indent=2))

if __name__=='__main__':run()
