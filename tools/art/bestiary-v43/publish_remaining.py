"""Publish scoped offline art evidence for two existing registered bosses."""
from pathlib import Path
import hashlib, html, json, re
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];DOC=ROOT/'docs/art/bestiary-v43'
GROUPS={
 'marshal':{'title':'殉节盲帅 · 公孙无妄','ids':['gongsun_wuwang','gongsun_wuwang_foot'],'forms':['骨马负龛','双橇军龛'],
  'details':['mask','skull','support'],'motions':['idle','walk','slash','morph'],
  'description':'原来的4个纯色色岛让骨、旧铁和内龛连成平面。这次重绘盲面、马骨眼窝与颌缘，压低外框和足端，分开哀带、铁壳和誓物。武器保持原色与原结构。',
  'references':'暮色Wraith的浅脸与暗衣、Lich的头胸优先；Alex’s Mobs Froststalker的头颈与支撑分区；灾变Draugr的骨与暗甲对比。只借鉴分区方法，未使用外部像素。',
  'limit':'正前方现有兵器在部分角度仍会遮住盲面；原形体与动作未重做，未以贴图声称消除了几何遮挡。'},
 'taoyan':{'title':'断代凶镬 · 饕宴之尸','ids':['taoyan_zhishi','taoyan_zhishi_phase2'],'forms':['三足凶镬','八足骨镬'],
  'details':['maw','ram','shell'],'motions':['idle','walk','ram','whip','oil','transition'],
  'description':'原先鼎壁、钟体与攻城机构共用一片褐色。现在按完整铸壳组织铜色与接缝，口缘用暗铁、骨齿突出前端，内壁和油面另分层，铜绿只落在下沿接缝。撞击面和传动杆分材质。',
  'references':'暮色PinchBeetle、FireBeetle的口/背壳/暗腹分区；Alex’s Mobs鳄龟与RockyRoller的硬壳与腹下连接；Quark Toretoise的顶壳、浅口和暗底。没有复制壳纹或铜色。',
  'limit':'二阶段前32tick保留一阶段铜色，之后切暖铜；两张图集共用918个UV岛并全部绘制，避免新足错采。未改变切换时刻或热化机制。'}
}
STYLE='body{margin:0;background:#edf0e9;color:#263335;font:16px/1.65 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:32px}a{color:#305f77}h1,h2{line-height:1.25}nav{display:flex;gap:18px;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:18px}.card{background:#f8f8f2;padding:18px;border-radius:12px;margin:24px 0}img{max-width:100%;height:auto;image-rendering:pixelated}figure{margin:12px 0}figcaption{color:#526363;font-size:14px}.scroll{overflow:auto}.atlas{max-width:none;width:1536px}.note{border-left:4px solid #98784b;padding:12px 18px;background:#e4e7de}code{font-size:14px}details{margin:18px 0}summary{cursor:pointer;font-weight:600}section{scroll-margin-top:20px}'
def img(src,caption='',cls=''):
 return f'<figure><a href="{html.escape(src)}"><img loading="lazy" class="{cls}" src="{html.escape(src)}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
def page(title,body):return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+STYLE+'</style><main>'+body+'</main></html>'

def main():
 cover=Image.new('RGB',(1800,1280),'#e8e9e4');d=ImageDraw.Draw(cover);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26)
 entries=[]
 for group,g in GROUPS.items():
  out=DOC/group
  native=json.loads((out/'native-bake-check.json').read_text());checks=json.loads((out/'resource-verification.json').read_text());assert native['status']==checks['status']=='PASS'
  ref=json.loads((DOC/f'{group}-reference-review.json').read_text());assert ref['accepted_for_target']==100
  body=f'<h1>{g["title"]} · 像素材质补完</h1><nav><a href="../continuation-20261028.html">本轮总览</a><a href="../{group}-reference.html">逐项参考与排除记录</a><a href="material-export.json">实际资源记录</a><a href="resource-verification.json">资源检查</a><a href="native-bake-check.json">GeckoLib原生解析</a></nav><p>{g["description"]}</p><p>{g["references"]}</p><p class="note">全部画面为实际PNG逐面采样的软件预览；含原色与基础漫反射，没有粒子/发光。不是游戏截图。已验证原生资源解析与隔离重新导出；整包构建、实际客户端加载和战斗待验证。{g["limit"]}</p>'
  for ident,label in zip(g['ids'],g['forms']):
   body+=f'<section class="card" id="{ident}"><h2>{label}</h2><code>dynasty:{ident}</code><p>同机位、同尺度；旁置玩家1.8m与一格石砖/木材参照。尺寸、骨架、攻击时间轴保持原样。</p>'
   body+=img(f'{ident}/comparison-45.png','左：修改前；右：本轮。点图看原尺寸。')
   body+='<details><summary>正面、侧面、背面对照</summary>'+''.join(img(f'{ident}/comparison-{view}.png',view+' · 同条件前后') for view in ['front','side','back'])+'</details>'
   body+='<details open><summary>原色、基础光照与近景</summary><div class="grid">'+''.join(img(f'{ident}/{view}.png',view+' · 实际PNG') for view in ['45-unlit','45-lit','front-lit','back-lit'])+'</div><div class="grid">'
   for detail in g['details']:
    if (out/ident/f'{detail}-detail.png').exists():body+=img(f'{ident}/{detail}-detail.png',detail+' · 仅隔离现有骨骼查看，不是新增部件')
   body+='</div></details><details><summary>PNG原尺寸、整数倍放大、逐面UV</summary>'
   body+=img(f'{ident}/texture.png','原始512×512图集。有效面按模型单位绘制，并非放大旧图。')+'<div class="scroll">'+img(f'{ident}/texture-3x.png','3倍最近邻 · 可横向滚动','atlas')+'</div><div class="grid">'+img(f'{ident}/uv-overlay-2x.png','UV岛叠加检查')+img(f'{ident}/uv-direction.png','临时方向/编号检查纹理，仅预览使用，运行PNG已恢复正式图')+'</div></details>'
   body+='<details><summary>灰度、暗处与玩家观察距离</summary><div class="grid">'+''.join(img(f'{ident}/{x}.png',x+' · 软件等效检查，非游戏光照截图') for x in ['gray','dim','distance-10m','distance-18m','distance-28m'])+'</div></details>'
   body+='<details open><summary>完整代表动作 · 固定相机</summary><p>每条覆盖开始到恢复，共24帧。原动作不改时序；离线解释器不能代替游戏动画和服务器接触验证。</p><div class="grid">'
   for motion in g['motions']:
    body+=img(f'{ident}/{motion}.webp',motion+' · 完整原动作')+f'<p><a href="{ident}/{motion}-frames.png">{motion}逐帧检查图</a></p>'
   body+='</div></details>'
   if ident=='taoyan_zhishi_phase2':body+='<details><summary>贴图切换边界</summary><div class="grid">'+''.join(img(f'{ident}/transition-{t}.png',t+'tick · 保留原切换时刻') for t in ['24','31.99','32','40'])+'</div></details>'
   body+='</section>'
   i=len(entries);preview=Image.open(out/ident/'45-lit.png').convert('RGB').resize((900,570),Image.Resampling.NEAREST);x=(i%2)*900;y=(i//2)*640
   cover.paste(preview,(x,y+60));d.text((x+24,y+16),g['title']+' / '+label,font=font,fill='#263335')
   entries.append({'entity':g['ids'][0],'form':ident,'gallery':f'{group}/index.html#{ident}','new_entity':False})
  (out/'index.html').write_text(page(g['title'],body))
 cover.save(DOC/'continuation-overview.png')
 body='<h1>剩余生物材质补完 · 2026-10-28</h1><p>本轮补完两个既有注册Boss的四种现有形态。已认可批次保留；没有新增实体，也没有重新设计身体。</p>'+img('continuation-overview.png','四种形态 · 同一软件预览管线，含玩家与方块参照')
 for group,g in GROUPS.items():body+=f'<section class="card"><h2><a href="{group}/index.html">{g["title"]} · 完整对照与动作</a></h2><p>{g["description"]}</p><p>{g["references"]}</p></section>'
 body+='<p class="note">每个目标已完成100项相关模型/原图集研究，分别查看110与131候选；排除10与31。并非100种独立骨架或100个整合包，也不将软件构造视图称为作者游戏截图。48条现有动作经GeckoLib4.8.4解析；四种形态2622面完成原生烘焙。PNG/UV/保护资源及隔离重新导出检查通过。整包构建、实机加载、战斗观感仍待验证。</p>'
 (DOC/'continuation-20261028.html').write_text(page('两Boss四形态 · 真实PNG材质补完',body))
 report={'status':'MATERIAL_UV_NATIVE_DONE_GAME_PENDING','registered_bosses':2,'existing_forms':entries,'new_entities':0,'body_geometry_changed':False,'timelines_or_gameplay_changed':False,'native_geckolib':'4.8.4','native_quads':2622,'parsed_existing_clips':48,'actual_game':'PENDING','full_gradle_build':'NOT_RUN','sound_brightness_user_world':'UNTOUCHED','pushed':False,'prompts_deleted':False}
 runtime=[]
 for group,g in GROUPS.items():
  for id in g['ids']:
   runtime += [f'src/main/resources/assets/dynasty/geo/blueprint/boss/{id}.geo.json',f'src/main/resources/assets/dynasty/textures/entity/blueprint/boss/{id}_body.png']
 runtime+=['src/main/java/com/dynasty/blueprint/boss/client/BlindMarshalRenderer.java','src/main/java/com/dynasty/blueprint/boss/client/TaoyanCauldronRenderer.java']
 report['runtime_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in runtime}
 # Restrict link checks to these new galleries; the shared project has unrelated work.
 checked=0
 for p in [DOC/'continuation-20261028.html',DOC/'marshal/index.html',DOC/'taoyan/index.html']:
  for link in re.findall(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"',p.read_text()):
   if not link.startswith(('https:','http:')):assert (p.parent/link).exists(),(p,link);checked+=1
 report['local_gallery_links_checked']=checked
 (DOC/'continuation-20261028.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(f'Published two bosses / four existing forms; {checked} local gallery links present.')
if __name__=='__main__':main()
