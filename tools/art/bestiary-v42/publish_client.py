"""Publish genuine isolated-client captures, separately from offline model renders."""
from pathlib import Path
import hashlib,json,html
from PIL import Image,ImageDraw,ImageFont
from build_models import ROOT,OUT,IDS,TITLES

def publish():
    directory=OUT/'client/run01';source=directory/'result.json'
    if not source.exists():return
    result=json.loads(source.read_text())
    assert result['status']=='PASS' and result['resource_reload'] and len(result['stages'])==35
    expected=json.loads((directory/'expected-textures.json').read_text())
    for id in IDS:
        p=ROOT/'src/main/resources/assets/dynasty/textures/entity/bestiary'/f'{id}.png'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==expected[id],id
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',23)
    overview=Image.new('RGB',(1440,1380),'#e8eae2');d=ImageDraw.Draw(overview)
    d.text((15,12),'独立Forge客户端实拍 · 原版日光 / 真实玩家 / 石砖参照',font=font,fill='#283936')
    sections=[];manifest={}
    for i,(id,title) in enumerate(zip(IDS,TITLES)):
        folder=directory/id
        raw=Image.open(folder/'45.png').convert('RGB')
        # Review contact-sheet crop only; every original framebuffer PNG remains untouched.
        shot=raw.crop((160,230,1820,1310));shot.thumbnail((710,380),Image.Resampling.NEAREST)
        x=i%2*720;y=55+i//2*440;overview.paste(shot,(x+(710-shot.width)//2,y))
        d.text((x+12,y+390),title,font=font,fill='#283936')
        pieces=[f'<section id="{id}"><h2>{title}</h2><div class="grid">']
        for view,title_view in [('front','正面'),('45','45度'),('side','侧面'),('back','背面')]:
            assert (folder/(view+'.png')).exists()
            pieces.append(f'<figure><a href="{id}/{view}.png"><img loading="lazy" src="{id}/{view}.png"></a><figcaption>{title_view} · 原始帧缓冲截图</figcaption></figure>')
        pieces.append('</div>')
        for action in ['walk']+([] if id=='minister' else ['swing']):
            frames=sorted(folder.glob(action+'-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
            assert len(frames)>=5,(id,action)
            images=[Image.open(p).convert('RGB') for p in frames]
            # Native screen capture sequence, not the offline animation renderer.
            small=[]
            for im in images:
                im=im.crop((160,230,1820,1310));im.thumbnail((830,540),Image.Resampling.NEAREST);small.append(im)
            small[0].save(folder/(action+'.gif'),save_all=True,append_images=small[1:],duration=200,loop=0)
            pieces.append(f'<figure><img loading="lazy" src="{id}/{action}.gif"><figcaption>'+('受控地面移动，客户端实际行走动画' if action=='walk' else '服务端原版挥击广播，客户端实际动作；不代表自然AI伤害验收')+'</figcaption></figure>')
        pieces.append('</section>');sections+=pieces
        manifest[id]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.png')}
    overview.save(directory/'overview.png')
    (directory/'capture-hashes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    style='body{background:#e8eae2;color:#283936;max-width:1500px;margin:auto;padding:24px;font:18px/1.6 sans-serif}img{max-width:100%;height:auto}section{border-top:1px solid #9ea9a1;margin-top:35px;padding-top:20px}figure{margin:10px 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}a{color:#245b6e}'
    page='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>V42 · 实际客户端验收</title><style>'+style+'</style><h1>六个角色 · 真正Forge客户端验收</h1><p>独立新存档，Minecraft 1.20.1 / Forge 47.4.10，原版日光、真实玩家与石砖/木板比例参照，无资源包和额外光影。实际注册Renderer、六张资源PNG的SHA-256及重载通过。35个场景取得123张原始截图；静音测试实例已自行退出，原客户端与存档未动。</p><p>移动和挥击由验收夹具控制，服务端广播通过真实集成连接到客户端；不是自然AI战斗、伤害时序、双人联机或20只同屏负载验收。玩家使用离线默认皮肤。</p><p><a href="../../index.html">返回模型及贴图对照</a> · <a href="result.json">原始运行结果</a> · <a href="capture-hashes.json">截图校验</a></p><img src="overview.png">'+''.join(sections)
    (directory/'index.html').write_text(page)
    validation=json.loads((OUT/'validation.json').read_text())
    validation.update(status='CLIENT_LOAD_RELOAD_AND_CONTROLLED_MOTION_CHECKED_NATURAL_COMBAT_PENDING',isolated_client_launched=True,existing_client_touched=False,
        client_checks=dict(result='client/run01/result.json',screenshots=result['screenshots'],stages=35,resource_reload=True,png_hashes_exact=True,actual_registered_renderer=True,controlled_movement=True,vanilla_swing_packets=True,natural_combat=False,multiplayer=False,load20=False))
    (OUT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    p=OUT/'index.html';text=p.read_text()
    marker='<section id="jade_guard">'
    if 'id="actual-client"' not in text:
        text=text.replace(marker,'<section id="actual-client"><h2>实际Forge客户端验收</h2><p>六只已在独立静音客户端加载、重载并检查受控移动与原版挥击广播。35场景 / 123张真实截图；自然AI战斗、多人和负载继续待验证。</p><p><a href="client/run01/index.html">打开实机各角度与动作</a></p><img loading="lazy" src="client/run01/overview.png"></section>'+marker,1)
    text=text.replace('实机战斗、多人同步及20只同屏仍待验证。','实机自然战斗、多人同步及20只同屏仍待验证；独立客户端的实际载入、重载与受控动作已补验。')
    p.write_text(text)
    publish_natural()
    print('PASS: 123 genuine framebuffer captures, 35 scenes, six runtime textures, reload, controlled walking and vanilla swing broadcasts')

def publish_natural():
    # natural02 fixes the scene-boundary screenshot label; retain natural01 as raw history.
    directory=OUT/'client/natural02';source=directory/'result.json'
    if not source.exists():return
    result=json.loads(source.read_text())
    assert result['status']=='PASS' and len(result['scenarios'])==6
    sections=[];manifest={}
    for row,title in zip(result['scenarios'],TITLES):
        id=row['id'];folder=directory/id
        frames=sorted(folder.glob('ai-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
        assert len(frames)>=10,(id,len(frames))
        images=[]
        for p in frames:
            im=Image.open(p).convert('RGB');im.thumbnail((1120,800),Image.Resampling.NEAREST);images.append(im)
        images[0].save(folder/'ai.gif',save_all=True,append_images=images[1:],duration=500,loop=0)
        manifest[id]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in frames}
        sections.append(f'<section><h2>{title}</h2><p>自行选中玩家 {row["natural_target_ticks"]} tick；寻路 {row["navigation_path_ticks"]} tick；距出生点最大位移 {row["distance_from_spawn"]:.2f} 格；直接伤害事件 {row["accepted_direct_damage_events"]} 次。</p><img loading="lazy" src="{id}/ai.gif"><details><summary>原始截图</summary>'+''.join(f'<a href="{id}/{p.name}">{p.stem}</a> ' for p in frames)+'</details></section>')
    (directory/'capture-hashes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (directory/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>V42 · 生产AI近战</title><style>body{max-width:1200px;margin:auto;padding:24px;background:#e8eae2;color:#283936;font:18px/1.6 sans-serif}img{max-width:100%}section{margin:30px 0;border-top:1px solid #aaa}a{color:#245b6e}</style><h1>生产AI近战 · 实际Forge客户端</h1><p>测试脚本只放置生物与生存玩家，不调用 setTarget、move、swing 或 hurt；目标选择、寻路与攻击均由现有AI完成。玩家接受抗性与每tick治疗，避免现有高伤害中断观察；未改生物数值或资源。</p><p>这是测试场中的生产AI，不是自然生成或野外遭遇。未验证死亡、水下遭遇、多人或20只同屏；大臣只检查正常活动且不攻击。</p><p><a href="result.json">原始事件统计</a> · <a href="capture-hashes.json">截图哈希</a> · <a href="../../index.html">返回美术对照</a></p>'+''.join(sections))
    validation=json.loads((OUT/'validation.json').read_text())
    validation['status']='CLIENT_LOAD_RELOAD_CONTROLLED_MOTION_AND_PRODUCTION_AI_MELEE_CHECKED'
    validation['production_ai_fixture']={'result':'client/natural02/result.json','scenarios':6,'screenshots':result['screenshots'],'target_navigation_melee':True,'friendly_minister_nonattack':True,'player_protection':'Resistance IV (amplifier 3) and post-damage healing; no invulnerability','natural_spawning':False,'death':False,'aquatic_encounter':False,'multiplayer':False,'load20':False}
    validation['pending']=['自然生成与野外遭遇','死亡过程','水下遭遇','多人同步与20只同屏负载']
    (OUT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    p=OUT/'index.html';text=p.read_text()
    if 'id="production-ai"' not in text:
        marker='<section id="jade_guard">'
        text=text.replace(marker,'<section id="production-ai"><h2>生产AI近战补验</h2><p>五只小怪自行索敌、寻路、近战命中；客户端实际移动与挥击通过。友方大臣保持不攻击。玩家仅加抗性和治疗保障观察，生物资源与数值未改。</p><p>自然生成、死亡、水下遭遇、多人和负载仍待验。</p><a href="client/natural02/index.html">查看完整实机AI动作与事件记录</a></section>'+marker,1)
    p.write_text(text)
    print('PASS: production AI target/navigation/melee and friendly minister nonattack, with explicit fixture limits')

if __name__=='__main__':publish()
