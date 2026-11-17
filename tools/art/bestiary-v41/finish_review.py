"""Verify this batch's production files and publish its native-mesh review."""
import json,gzip,hashlib,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import review as r
from build_models import face_rects

R=r.ROOT;D=r.OUT
meshes=json.loads(gzip.decompress((R/'build/bestiary-v41/native-mesh.json.gz').read_bytes()))
report={'scope':['dynasty:nine_tailed_fox','dynasty:phoenix'],
        'format':'existing native Java ModelPart renderer; Forge 1.20.1 unchanged',
        'preview':'Offline actual Minecraft ModelPart vertices + actual runtime PNG, not game screenshots',
        'game_validation':'pending; no world/client launched or closed',
        'references':'102 quadruped model/coat studies, 57 families; 106 bird studies, 22 families. Not 208 independent rigs. 1000-independent-creature request remains incomplete.',
        'assets':{}}

for name in meshes:
    folder=D/name;data=json.loads((folder/'model.json').read_text());runtime=R/data['texture']
    assert runtime.read_bytes()==(folder/'texture.png').read_bytes()
    atlas=Image.open(runtime).convert('RGBA');assert list(atlas.size)==data['texture_size']==[128,128]
    occupied=np.zeros((128,128),bool);names=set();cubes=0;checked=0
    test=Image.new('RGBA',(128,128));draw=ImageDraw.Draw(test)
    colors=['#da6651','#7ead59','#68a8cb','#a887ca','#d0af4b','#7d9689']
    for bone in data['bones']:
        assert bone['parent'] is None or bone['parent'] in names
        names.add(bone['name'])
        for c in bone['cubes']:
            cubes+=1
            for i,(face,(u,v,w,h)) in enumerate(face_rects(c).items()):
                u,v,w,h=map(int,(u,v,w,h));assert u>=0 and v>=0 and u+w<=128 and v+h<=128
                region=occupied[v:v+h,u:u+w];assert not region.any();region[:]=True
                assert np.array(atlas)[v:v+h,u:u+w,3].min()==255
                draw.rectangle((u,v,u+w-1,v+h-1),fill=colors[i])
                for yy in range(v,v+h):
                    for xx in range(u,u+w):
                        if ((xx-u)//2+(yy-v)//2)%2:draw.point((xx,yy),fill='#cfd4d0')
                # A dark origin and bright +U/+V edges make mirroring/direction visible.
                draw.line((u,v,u+w-1,v),fill='#f4edd6');draw.line((u,v,u,v+h-1),fill='#28323c')
                checked+=1
    for state,vertices in meshes[name].items():
        arr=np.array(vertices);assert arr.shape==(cubes*24,5) and np.isfinite(arr).all()
        assert arr[:,3:].min()>=0 and arr[:,3:].max()<=128
    if name=='nine_tailed_fox':assert len([n for n in names if n.startswith('tail') and not n.endswith('_tip')])==9
    test.save(R/'build/bestiary-v41'/f'{name}-direction-check.png')
    views=[r.raster(r.geometry(data),test,a,size=(650,480),scale=11,mode='unlit') for a in (0,45,90,180)]
    r.card(views,['正面：白边 +U，黑边原点','45度','侧面','背面'],folder/'uv-direction-check.png',name+' / 临时方向纹理检查；未写入游戏PNG')
    for state in (('idle','walk','attack') if name=='nine_tailed_fox' else ('idle','walk','fly')):
        times=[0,10,20,30,40,50,60,70]
        r.card([r.raster(r.geometry(data,t,state),atlas,40,size=(600,430),scale=9) for t in times],
               [str(t)+' tick' for t in times],folder/(state+'-contact.png'),name+' / '+state+' 原生完整回放取样',cols=4)
    for view,label in [('front','正面面部'),('45','45度头部与身体')]:
        im=Image.open(folder/(view+'.png'));im.crop((200,100,700,510)).resize((1000,820),Image.Resampling.NEAREST).save(folder/(view+'-close.png'))
    report['assets'][name]={'texture':str(runtime.relative_to(R)),'texture_sha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),
        'bones':len(names),'cubes':cubes,'nonoverlapping_opaque_UV_faces':checked,'native_poses':len(meshes[name]),'runtime_and_preview_identical':True}

jar=R/'build/libs/dynasty-0.1.0.jar'
if not jar.exists():
    jars=[p for p in (R/'build/libs').glob('dynasty-*.jar') if 'sources' not in p.name];jar=max(jars,key=lambda p:p.stat().st_mtime)
with zipfile.ZipFile(jar) as z:
    for name,item in report['assets'].items():
        entry='assets/dynasty/textures/entity/bestiary/'+name+'.png'
        assert hashlib.sha256(z.read(entry)).hexdigest()==item['texture_sha256']
    for cls in ('BestiarySpiritLayers','BestiarySpiritModel','BestiarySpiritRenderer'):
        assert 'com/dynasty/client/'+cls+'.class' in z.namelist()
report['jar']={'file':str(jar.relative_to(R)),'sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'textures_match':True,'classes_present':True}
report['build']='classes and reobfJar successful; see build/bestiary-v41/full-build.log and jar-build.log'
(D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

css='body{margin:0;background:#e8eae2;color:#263936;font:17px/1.7 system-ui}main{max-width:1500px;margin:auto;padding:28px}img{max-width:100%;height:auto;image-rendering:pixelated}figure{margin:20px 0}h2{margin-top:50px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}a{color:#12637a}.notice{padding:18px;background:#dbe3d8}details{margin:20px 0}code{word-break:break-all}'
parts=['<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>凤凰与基础九尾狐 · V41</title><style>'+css+'</style><main><h1>凤凰与基础九尾狐 · 模型、像素UV与专用动作</h1><p class="notice">本轮只处理未精修的基础九尾狐和凤凰，已认可的白面狐仙姑、麒麟、年兽及其他批次不动。这里全部是原生ModelPart离线预览，不是实机截图。两只的注册、碰撞、技能和伤害不改。</p><img src="overview.png"><nav><a href="#nine_tailed_fox">九尾狐</a> · <a href="#phoenix">凤凰</a> · <a href="references/index.html">实际查看的参考</a> · <a href="validation.json">验证记录</a></nav>']
notes={
 'nine_tailed_fox':('基础九尾狐','参考Alex’s Mobs鬃狼的躯干／足端分区、暮色森林兔与松鼠的简洁大色块、Critters and Companions雪貂的长身与口鼻衔接。改成连贯狐吻、腹下负形、四足和九根有父子关系的尾部；暖棕背毛、浅腹、深足和尾尖保持身份。九尾摆动不再独立漂浮，迈步分对角，攻击前压集中在颈部。','attack'),
 'phoenix':('凤凰','参考Frikinzi’s Fauna金雕、红鸢与鱼鹰的翼根／前翼／飞羽连接，以及虹雉和雉鸡的冠、颈胸与长尾色区。凤凰保持原赤金主题，重画胸腹与飞羽方向；翼段继承运动，飞羽延迟跟随，落地向后收翼；修复第一版落地翼尖穿地和重叠闪面。','fly')}
for name,(title,note,action) in notes.items():
    parts+=['<section id="'+name+'"><h2>'+title+'</h2><p>'+note+'</p>']
    for file,caption in [('before-after.png','修改前后：同机位、同尺度、同基础光照'),('views.png','正面、45度、侧面、背面'),('checks.png','原色、灰模、剪影、玩家比例')]:
        parts.append('<figure><a href="'+name+'/'+file+'"><img loading="lazy" src="'+name+'/'+file+'"></a><figcaption>'+caption+'</figcaption></figure>')
    parts.append('<h3>完整原生骨骼回放</h3><p>每种状态0–78 tick、40帧。显示实际PNG和原生顶点；自然战斗与客户端光照仍待实机复核。</p><div class="grid">')
    for state in ('idle','walk',action):parts.append('<figure><img loading="lazy" src="'+name+'/'+state+'.gif"><figcaption>'+state+' · 无声循环</figcaption><a href="'+name+'/'+state+'-contact.png">动作阶段取样图</a></figure>')
    parts.append('</div><details><summary>原始PNG、4倍最近邻、UV与方向检查、近景</summary><p><a href="'+name+'/texture.png">实际128×128 PNG</a> · <a href="'+name+'/model.json">生成源模型数据</a></p><div class="grid">')
    for file in ('texture-4x.png','uv-4x.png','front-close.png','45-close.png'):parts.append('<img loading="lazy" src="'+name+'/'+file+'">')
    parts.append('</div><img loading="lazy" src="'+name+'/uv-direction-check.png"><p>方向检查图只用于离线验证，正式PNG没有测试棋盘。</p></details></section>')
parts.append('<h2>检查与交付边界</h2><p>两套模型和贴图的权威生成源可重复导出相同结果；474个UV面无越界、无重叠且已绘制；240个原生姿态全部烘焙并输出。classes与reobfJar通过，JAR内纹理哈希与源文件一致。没有启动或关闭现有客户端，没有操作声音和亮度。实机加载、自然战斗和多人表现仍待验证。</p><p>参考记录为四足102条／57模型族、鸟类106条／22模型族，包含同骨架物种与毛色变体。它们不是208套独立模型；此前1000套独立生物的研究要求仍未完成，未据此删除提示词。</p></main></html>')
(D/'index.html').write_text(''.join(parts))
print(json.dumps(report,ensure_ascii=False,indent=2))
