"""Package actual assets, evidence and an honest native-mesh review gallery."""
from pathlib import Path
import json,hashlib,zipfile,html
from build_models import ROOT,OUT,ASSETS,IDS,TITLES,SCALES

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    report=json.loads((OUT/'validation.json').read_text());jar=ROOT/'build/libs/dynasty-1.4.0.jar'
    study=json.loads((OUT/'reference-study.json').read_text());assert len(study['items'])==100 and all(v['viewed'] for v in study['items'])
    preserved={}
    for id,row in json.loads((ROOT/'docs/art/bestiary-v41/validation.json').read_text())['assets'].items():
        p=ROOT/row['texture'];assert digest(p)==row['texture_sha256'];preserved[str(p.relative_to(ROOT))]=digest(p)
    for path,sha in json.loads((ROOT/'docs/art/bestiary-v40/DELIVERY.json').read_text())['owned_hashes'].items():
        p=ROOT/path;assert digest(p)==sha;preserved[path]=sha
    with zipfile.ZipFile(jar) as z:
        for id in IDS:
            p=ASSETS/'textures/entity/bestiary'/f'{id}.png';assert z.read('assets/dynasty/textures/entity/bestiary/'+id+'.png')==p.read_bytes()==(OUT/id/'texture.png').read_bytes()
        for cls in ['RealmCreatureLayers','RealmCreatureModel','RealmCreatureRenderer']:assert f'com/dynasty/client/{cls}.class' in z.namelist()
    for log in ['compile.log','jar.log','compile-final.log']:assert 'BUILD SUCCESSFUL' in (ROOT/'build/bestiary-v42'/log).read_text()
    assert '680 animated poses' in (ROOT/'build/bestiary-v42/native-bake.log').read_text()
    events=(ROOT/'src/main/java/com/dynasty/client/DynastyClientEvents.java').read_text()
    bindings={}
    for id in IDS:
        assert 'RealmCreatureLayers::'+id in events and '"'+id+'", ' in events
        bindings[id]=dict(texture='textures/entity/bestiary/'+id+'.png',model='RealmCreatureLayers::'+id,renderer='RealmCreatureRenderer',visual_scale=SCALES[IDS.index(id)])
    (OUT/'runtime-bindings.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n')
    owned=[ASSETS/'textures/entity/bestiary'/f'{id}.png' for id in IDS]
    owned += [ROOT/'src/main/java/com/dynasty/client'/f'{cls}.java' for cls in ['RealmCreatureLayers','RealmCreatureModel','RealmCreatureRenderer']]
    owned += [p for p in (ROOT/'tools/art/bestiary-v42').rglob('*') if p.suffix in ('.py','.java','.gradle')]
    report.update(dict(status='RUNTIME_BOUND_NATIVE_MESH_CHECKED_GAME_PENDING',scope=['dynasty:'+id for id in IDS],
        preview='Offline native Minecraft 1.20.1 LayerDefinition / ModelPart vertices with actual PNGs; not game captures',
        animation_scope='680 sample poses: five mobs idle/walk/normalized vanilla swing; friendly Minister idle/walk only. No claim about server contact ticks.',
        gameplay_changed=False,collision_changed=False,handheld_items_added=False,domains_or_particle_layers_added=False,
        references=dict(count=100,mods=len(study['counts']),model_and_original_atlas_viewed=True,exact_geometry_duplicates_excluded=True,library_reused=True,new_models_after_completed_study=['terracotta_warrior','minister'],details='reference-study.json'),
        jar=dict(path=str(jar.relative_to(ROOT)),sha256=digest(jar),textures_exact=True,classes_present=True),
        owned_hashes={str(p.relative_to(ROOT)):digest(p) for p in owned},approved_batches_preserved=preserved,
        installed_in_live_client=False,live_client_touched=False,prompt_sections_deleted=False,
        self_review=['冥卒首稿双拖布像裤腿，改为错长错位三片悬布。','加深冥卒真实空腔后壁，与框壳区分。','鲛人保留地面步态，不伪造现有AI没有的纯鱼尾游动。','头部近景首稿裁掉盔顶，扩大取景重新输出。','动作标注使用挥击进度，不臆造伤害接触帧。','旧版64UV标尺与256PNG在首稿离线对照中换算错误，按真实PNG尺寸修复并重出对照。','独立怪物研究剔除Dramix/Reyvor两组同构换色，补足100个不同构造。','大臣首稿帽边与头面共面导致闪面，以0.15模型像素外壳厚度修复；保留整数UV与Steve头部尺寸。','友方大臣无攻击AI，移除伪造的攻击展示，只回放真实待机与移动。']))
    (OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    legacy=json.loads((OUT/'references.json').read_text())
    explanations={
      'jade_guard':'旧版装饰层与翼状肩片较密。本轮保留史蒂夫六主体块，改用小幅盔沿、半覆面和薄肩甲；玉色札甲按胸腹连续组织，铜束件与布底分开，维持旧版1.08显示缩放。',
      'soul_soldier':'旧版已有脸部和亡灵身份，肩甲与叠块裙壳较重。本轮用骨面、兜帽、真实留空的躯壳和三片错长悬布表达冥卒；移动由悬布滞后与小幅漂移承接地面导航，近战仍由现有挥击驱动。',
      'thunder_envoy':'旧版巨大翼刃抢过普通怪主体。本轮回到史蒂夫六主体块，露面短须、束发头巾与铜箍形成身份；衣襟和袖褶沿身体组织，小怪不加领域与符文。',
      'merfolk':'旧版长蛇尾与地面近战步态不协调。本轮保留海族与实际行走方式，以史蒂夫双足配鱼肤、浅腹、眼形、侧鳃和贴背短鳍；尾鳍跟随步态，不改导航、碰撞或技能。',
      'terracotta_warrior':'旧贴图有陶俑身份，但布满均匀小点与装甲行。保留史蒂夫六主体，增小发髻、薄肩片和领口；用模制札甲行、克制的面部凹凸明暗与局部裂口表达哑光陶土，身体不再像另一套亮金属装备。',
      'minister':'旧版没有官帽，面部是通用大眼、身体接近整片蓝色。保留友方文官身份、史蒂夫六主体和原玩法；重画灰眉短须的年长面孔，补小官帽、叠襟、腰带与顺向衣褶。帽壳已修复闪面，不给文官套战斗粒子或攻击片段。'}
    applies={**legacy['applied'],
      'terracotta_warrior':'侧重暮色Carminite Golem、Goety Blackguard/Vanguard与Cataclysm构造体的材质分层；只取关节、头胸主次与整面组织，改画原创陶土，不借用它们的武器或纹样。',
      'minister':'侧重暮色Adherent/Redcap、Goety Enchanter/Preacher/Sorcerer的领帽、肤色窗口和衣料分层。重型构造体用来比较并排除过大的肩胸比例，保留普通文官体量。'}
    style='''body{margin:0;background:#182323;color:#e1e7dc;font:17px/1.65 -apple-system,BlinkMacSystemFont,sans-serif}main{max-width:1460px;margin:auto;padding:34px 24px}h1{font-size:34px}h2{margin-top:0}a{color:#c7c48b}nav{display:flex;flex-wrap:wrap;gap:12px;margin:25px 0}nav a{padding:8px 18px;border-radius:18px;background:#334747;text-decoration:none}section{background:#223332;padding:24px;border-radius:18px;margin:28px 0}img{max-width:100%;height:auto;display:block;background:#e8eae2;border-radius:8px}figure{margin:15px 0}summary{cursor:pointer;color:#d2cca6;padding:12px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}.sub{color:#b5c4bc}figcaption{font-size:14px;color:#b5c4bc}p{max-width:1080px}.notice{border-left:4px solid #b7aa72;padding-left:18px}'''
    parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Dynasty · 六个现有生物 V42</title><style>'+style+'</style><main><h1>五只小怪与一位友方NPC · V42</h1><p>玉甲卫、冥卒、雷使、鲛人、兵马俑战士、大臣。实际模型、独立128px像素UV与动作适配；已认可的V40/V41保持原样。</p><p class="notice">以下是实际Minecraft原生模型烘焙顶点与运行PNG的离线预览。编译、打包与680组姿态已检查；实机战斗、多人同步及20只同屏仍待验证。</p><nav>']
    for id,title in zip(IDS,TITLES):parts.append(f'<a href="#{id}">{title}</a>')
    parts.append('</nav><p><a href="reference-study.html">100个独立怪物：模型、原始贴图与逐项观察</a> · <a href="validation.json">验证记录</a> · <a href="realm-creatures-v42.zip">本批资源及生成源</a></p><img src="overview.png" alt="六个生物与原版玩家同尺度总览">')
    for id,title in zip(IDS,TITLES):
        parts.append(f'<section id="{id}"><h2>{title} <small class="sub">dynasty:{id}</small></h2><p>{explanations[id]}</p><figure><img loading="lazy" src="{id}/before-after.png"><figcaption>相同机位、世界比例与基础光照。左：旧绑定/旧PNG；右：本轮实际资源。无额外粒子与发光。</figcaption></figure><details><summary>正、侧、背、45度和玩家比例</summary><img loading="lazy" src="{id}/views.png"><img loading="lazy" src="{id}/checks.png"></details><details><summary>头部 / 胸部近景</summary><div class="grid"><img loading="lazy" src="{id}/close-head.png"><img loading="lazy" src="{id}/close-chest.png"></div></details><details><summary>完整待机、移动'+('' if id=='minister' else '、挥击')+'预览</summary><p class="sub">原生动画函数实际回放。挥击片段扫描原版进度，不宣称服务端伤害接触时序已经实机验证。友方文官只展示已有的待机与移动。</p><div class="grid">')
        clips=[('idle','待机'),('walk','移动')]+([] if id=='minister' else [('attack','挥击进度回放')])
        for clip,label in clips:parts.append(f'<figure><img loading="lazy" src="{id}/{clip}.gif"><figcaption>{label} · 80个离线采样tick</figcaption></figure>')
        parts.append(f'</div><img loading="lazy" src="{id}/motion-strip.png" alt="连续动作阶段检查">')
        if id!='minister':parts.append(f'<img loading="lazy" src="{id}/attack-stages.png">')
        parts.append(f'</details><details><summary>真实PNG / 最近邻放大 / UV方向检查</summary><p><a href="{id}/texture.png">原始128×128 PNG</a> · <a href="{id}/model.json">可重复导出的模型数据</a></p><div class="grid"><img loading="lazy" src="{id}/texture-4x.png"><img loading="lazy" src="{id}/uv-4x.png"><img loading="lazy" src="{id}/uv-direction.png"></div><p class="sub">方向检查图仅供诊断，运行PNG不含棋盘或编号。</p></details><p class="sub">参考落实：{applies[id]}</p></section>')
    parts.append('<section><h2>研究、自检和运行范围</h2><p>实际查看8个模组的100个独立怪物模型源码静态重建及作者原始图集。排除了同构换色，记录了每项版本、渲染绑定与观察；这是一套可复用的同类构造研究库。追加兵马俑与大臣前完成了这100项研究。此前100份人类皮肤/衣层复查保留为补充资料，不计入此100个独立构造。</p><p><a href="reference-study.html">参考画面和逐项观察</a> · <a href="reference-study.json">去重、原始来源、适用范围</a> · <a href="references.json">此前外观与亡灵研究</a></p><p>自检修正：冥卒悬布首稿像双裤腿，改为三片错长；加深空腔后壁；旧图UV换算错误已修复并重出公平对照；头部近景补全盔顶；大臣官帽共面闪烁已用薄壳解决。每个动作都逐帧输出，不用0tick代替完整回放。</p><p>Java编译、JAR打包、六个实际LayerDefinition烘焙、680组姿态、逐面UV越界/重叠/透明缺口、五个人形的Steve六主体尺寸、运行与预览PNG字节一致均通过。原注册ID、AI、伤害、技能、掉落与碰撞保留。新持械道具未擅自制作。</p><p>未启动、关闭或替换现有游戏客户端。实机自然遭遇、战斗和多人负载待验证，待办保留。<a href="runtime-bindings.json">实际绑定</a> · <a href="validation.json">具体哈希与验证范围</a></p></section></main></html>')
    (OUT/'index.html').write_text(''.join(parts))
    from publish_client import publish
    publish()
    with zipfile.ZipFile(OUT/'realm-creatures-v42.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in owned:z.write(p,str(p.relative_to(ROOT)))
        # Include the shared binding file as current integration source, without claiming ownership of its unrelated contents.
        p=ROOT/'src/main/java/com/dynasty/client/DynastyClientEvents.java';z.write(p,str(p.relative_to(ROOT)))
        for id in IDS:z.write(OUT/id/'model.json',id+'/model.json')
        for name in ['validation.json','references.json','reference-study.json','runtime-bindings.json']:z.write(OUT/name,name)
    print('PASS: six live bindings, jar/source/preview PNG identity, V40+V41 preserved, 100 distinct model/atlas studies, gallery and package')
if __name__=='__main__':main()
