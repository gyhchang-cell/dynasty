"""Publish real resources and labelled offline evidence; preserve earlier galleries."""
from pathlib import Path
import hashlib, html, json, re, zipfile

ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/art/bestiary-v43'
OUT=DOC/'wood-kite'
ASSET=ROOT/'src/main/resources/assets/dynasty'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
esc=html.escape
STYLE='''body{margin:0;background:#1d2929;color:#e6e8dc;font:17px/1.65 -apple-system,BlinkMacSystemFont,sans-serif}main{max-width:1500px;margin:auto;padding:28px 24px}h1{font-size:32px}h2{font-size:25px}a{color:#d1c489}nav{display:flex;gap:15px;flex-wrap:wrap}section,article{background:#2a3a39;padding:24px;margin:25px 0;border-radius:16px}img{max-width:100%;height:auto;display:block;background:#e8e9e4}figure{margin:16px 0}figcaption,small,.sub{font-size:14px;color:#c3cebd}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.three{grid-template-columns:repeat(3,minmax(0,1fr))}details{margin:18px 0;border-top:1px solid #5d6b5e;padding-top:12px}summary{cursor:pointer;font-weight:600}code{font-size:14px}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #526456}.texture{image-rendering:pixelated;max-height:840px;width:auto}button{border:0;border-radius:20px;padding:10px 18px;font:inherit;background:#c4b881;color:#182b27;cursor:pointer}.ref img{max-height:450px;width:auto}.tag{font-size:13px;padding:3px 8px;background:#465945;border-radius:10px}@media(max-width:720px){.grid,.three{grid-template-columns:1fr}main{padding:15px}section{padding:16px}}'''
def page(title,body):
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+STYLE+'</style><main>'+body+'</main></html>'
def picture(src,caption):
 return f'<figure><a href="{src}"><img loading="lazy" src="{src}" alt="{esc(caption)}"></a><figcaption>{esc(caption)} · 点击查看原尺寸</figcaption></figure>'

def main():
 study=json.loads((DOC/'wing-reference-review.json').read_text())
 assert sum(r['accepted_for_luban_yisha'] and r['viewed'] for r in study['references'])==100
 exported=json.loads((OUT/'material-export.json').read_text())
 native=json.loads((OUT/'native-bake-check.json').read_text());assert native['status']=='PASS'
 assert all(r['parsedAnimationClips']==12 for r in native['forms'].values())
 static=json.loads((OUT/'validated-source.json').read_text());assert static['staticChecks']=='PASS_SOURCE_SOFTWARE_ONLY'
 preserved={}
 for row in json.loads((ROOT/'docs/art/bestiary-v41/validation.json').read_text())['assets'].values():preserved[row['texture']]=row['texture_sha256']
 for batch in ('bestiary-v40/DELIVERY.json','bestiary-v42/validation.json'):
  report=json.loads((ROOT/'docs/art'/batch).read_text())
  for p,sha in report['owned_hashes'].items():
   if p.startswith('src/') and p.endswith(('.png','.java','.json')):preserved[p]=sha
 for name,sha in preserved.items():assert digest(ROOT/name)==sha,('Approved batch changed elsewhere; investigate without overwriting',name)
 write(OUT/'approved-preservation.json',dict(status='PASS',count=len(preserved),sha256=preserved))
 # A small optional Minecraft1.20.1 resource override. Does not replace a mod
 # JAR, install anything in a live instance or include external study assets.
 pack=OUT/'wood-kite-materials-v43.zip';entries={}
 with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('pack.mcmeta',json.dumps(dict(pack=dict(pack_format=15,description='Dynasty V43 · 鲁班一杀双形态像素材质')),ensure_ascii=False))
  for id in exported:
   for folder,suffix in [('geo','.geo.json'),('textures/entity','.png')]:
    p=ASSET/folder/'blueprint/boss'/(id+suffix);name=str(p.relative_to(ASSET.parent));z.write(p,name);entries[name]=digest(p)
 with zipfile.ZipFile(pack) as z:
  for name,sha in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
 body='''<h1>鲁班一杀：双形态像素材质</h1><p>原机关鸟形体与动作保留；重画木、铜、铁、合金刃口和紫晶观察口。两张512×512图集按实际逐面UV分配，不是把旧16×16放大。</p><nav><a href="#wood">木羽形态</a><a href="#metal">金属形态</a><a href="../wing-reference.html">100项参考与逐项观察</a><a href="wood-kite-materials-v43.zip">仅本批4个资源的覆盖包</a></nav><p class="sub">以下全部是实际PNG逐面采样的软件预览，不是游戏截图。玩家参照高1.8米，石砖与木块各1米；同一角度前后机位、比例、光照一致。无额外发光、粒子或材质乘色。</p>'''
 explanations={
  'luban_yisha':'木羽：暖红木沿构件长轴组织纹理；深铁用于抓足、齿轮与投弹舱；铜梁保留干净承重面，观察口和剪喙形成主要对比。',
  'luban_yisha_metal':'金属：沿用原来的铜质外壳主题，抹去木纹；区分外壳折面、暗铁连接、滑轨与浅色工作刃，动力与观察口继续使用克制紫晶色。'}
 for id,label,anchor in [('luban_yisha','木羽形态','wood'),('luban_yisha_metal','金属形态','metal')]:
  row=exported[id]
  body+=f'<section id="{anchor}"><h2>{label} <code>{id}</code></h2><p>{explanations[id]}</p>'
  body+=picture(id+'/comparison-45.png','左：原运行贴图 / 右：本轮贴图；模型形体相同')
  body+='<details><summary>正面、侧面、背面：同条件前后对照</summary>'
  for view,label_ in [('front','正面'),('side','侧面'),('back','背面')]:body+=picture(id+'/comparison-'+view+'.png',label_+'前后对照')
  body+='</details><details><summary>原色与普通基础光照</summary><div class="grid">'
  for view in ('front','45','side','back'):
   for mode,word in [('unlit','原色'),('lit','中性漫反射')]:body+=picture(f'{id}/{view}-{mode}.png',view+' / '+word)
  body+='</div><div class="grid">'+picture(id+'/gray.png','灰度层级')+picture(id+'/dim.png','较暗基础光照，无额外发光')+'</div></details>'
  body+='<details><summary>头部、翼面与动力连接近景</summary><div class="grid three">'
  for part,word in [('head','头部'),('wing','翼面'),('motor','动力连接')]:body+=picture(id+'/'+part+'-detail.png',word+'实际表面')
  body+='</div></details><details><summary>完整原动作：飞行 / 翼斩 / 抓取 / 投弹</summary><p class="sub">每条完整时间轴24帧固定机位回放；不编辑伤害接触帧，不伪称服务端或实机验收。</p><div class="grid">'
  for clip,word in [('fly','飞行'),('wing_cut','翼斩'),('claws','抓取'),('bombs','投弹')]:
   body+=f'<figure><img loading="lazy" src="{id}/{clip}-frames.png" alt="{word}全时段检查"><figcaption>{word} · <a href="{id}/{clip}.webp">打开完整动画</a></figcaption></figure>'
  body+='</div></details><details><summary>原始PNG、最近邻放大、UV叠加与方向检查</summary>'
  body+=f'<p><a href="{id}/texture.png">原始512×512 PNG</a> · <a href="{id}/texture-3x.png">整数3倍放大</a> · <a href="{id}/uv-islands.json">逐面UV清单</a></p><div class="grid">'
  body+=picture(id+'/texture-3x.png','正式运行图集 / 最近邻3倍')+picture(id+'/uv-overlay-2x.png','正式图集叠加UV边界')+picture(id+'/uv-direction.png','编号与方向检查 / 诊断纹理')+picture(id+'/uv-direction-side.png','侧面方向检查')
  body+=f'</div><p class="sub">方向棋盘仅存在于检查图，未写入运行PNG。{row["face_islands"]}个独立面岛；{row["nonconstant_faces"]}个面已有非纯色材质组织；小连接件保留简洁色块。</p></details></section>'
 body+='''<section><h2>实际验证与剩余项</h2><p>运行资源、预览图集、覆盖包PNG一致；原73骨骼、体型、动作、技能与碰撞保持。UV标尺、边界、隔离边与像素密度检查通过；在临时目录从权威源重新生成，9个资源逐字节一致。</p><p>使用当前GeckoLib4.8.4真实解析器与Builtin模型工厂，两种形态共1848面烘焙通过，原有24条动画可解析；离线另含炸弹2条动作，共26条×81阶段几何检查。未运行整项目Gradle构建，未打开或替换游戏客户端。本轮实际资源重载、游戏光照、技能实战与多人验证待完成。</p><p>自检修改：修正软件预览共面深度的浮点斑点；动画取景改为整条固定尺度，避免逐帧缩放造成假变化。这两项都是预览修复，不宣称修复了原有模型共面结构或完成了游戏GL验证。</p><p>已认可批次的资源哈希保持；未改公孙无望和饕餮之食的四个后续形态。它们各自的100项相近参考尚未补齐，未把本机关鸟的研究直接当成它们的门槛。</p><p class="sub"><a href="native-bake-check.json">GeckoLib烘焙</a> · <a href="validated-source.json">源资源与动作检查</a> · <a href="reexport-check.json">隔离重导出</a> · <a href="approved-preservation.json">已认可资源保护</a> · <a href="delivery.json">交付范围</a></p></section>'''
 (OUT/'index.html').write_text(page('鲁班一杀双形态 · 真实材质对照',body))
 refs='<h1>鲁班一杀：实际查看的模型与贴图参考</h1><p>共查看101项，100项用于这只机关鸟的鸟体、翼面、头部和材质组织；Enderiophage相似性不足，排除。58张作者模型贴图展示，43项源码形体与原始PNG图集研究；不声称100套独立骨架或100只机关鸟，未复用原作者资产。</p><p><a href="wood-kite/index.html">返回本轮成品</a> · <a href="wing-reference-review.json">版本、哈希、去重依据与观察记录</a></p>'
 for row in study['references']:
  links=[(row.get('source') or row.get('model_source'),'作者页 / 模型源'),(row.get('texture_source') or row.get('image_source'),'原贴图 / 展示来源')]
  refs+=f'<article class="ref"><h2>{row["number"]}. {esc(row["identity"])}</h2><span class="tag">'+('采用' if row['accepted_for_luban_yisha'] else '排除，不计数')+'</span><p>'+esc(row['observation'])+'</p>'
  refs+='<p>'+' · '.join(f'<a href="{esc(url,quote=True)}">{label}</a>' for url,label in links if url)+'</p>'
  card=ROOT/'build/bestiary-v43/wing-reference'/row['card'];assert digest(card)==row['card_sha256']
  refs+=f'<img loading="lazy" src="../../../build/bestiary-v43/wing-reference/{esc(row["card"],quote=True)}" alt="实际查看的参考卡"><p class="sub">{esc(row["limits"])}</p></article>'
 (DOC/'wing-reference.html').write_text(page('100项鸟体、翼面与材质参考 · 来源与观察',refs))
 # Preserve all earlier humanoid research below a clearly current result.
 index=DOC/'index.html';text=index.read_text()
 banner='<section id="wood-kite-current"><h2>本轮实际资源：鲁班一杀双形态</h2><p>木、铜、铁、工作刃与观察口已分别绘制，独立逐面UV；形体与动作不动。100项相近模型与贴图研究已核对。</p><p><a href="wood-kite/index.html">查看原色前后对照、完整动作和真实PNG</a> · <a href="wing-reference.html">参考画面与逐项观察</a></p><a href="wood-kite/index.html"><img src="wood-kite/luban_yisha/comparison-45.png" alt="实际资源前后对照"></a><p>下方为此前的人形研究候选，和本轮鸟类100项研究分开记录。新资源游戏内验证仍待完成。</p></section>'
 if 'id="wood-kite-current"' not in text:
  text=text.replace('<h1>V43：模型与原始图集核查</h1>','<h1>V43：未完成生物美术与资源核查</h1>'+banner)
  text=text.replace('102张候选卡已检查；追加11个铁魔法角色、44张逐面PNG身体层视图，底层共6个Geo文件。没有新增Dynasty模型；没有为下一只达成100个相似参考门槛。','此前人形研究：102张候选卡、11个角色44张逐面PNG身体层视图，共6个Geo；这部分不冒充本轮机关鸟参考。')
  index.write_text(text)
 inventory=json.loads((DOC/'unfinished-registered.json').read_text())
 inventory['baseline_note']='findings retains PRE-EDIT measurements and hashes; see current_state for current production status.'
 inventory['current_state']={id:('MATERIAL_UV_EXPORTED_NATIVE_BAKED_GAME_PENDING' if id in exported else 'REFERENCE_GATE_PENDING_UNMODIFIED') for id in inventory['findings']}
 write(DOC/'unfinished-registered.json',inventory)
 owned=[ASSET/folder/'blueprint/boss'/(id+suffix) for id in exported for folder,suffix in [('geo','.geo.json'),('textures/entity','.png')]]
 owned+=[ROOT/'tools/blueprint'/name for name in ('generate_wood_kite.py','validate_wood_kite.py')]
 owned+=[ROOT/'tools/art/bestiary-v43'/name for name in ('wood_kite_materials.py','wood-kite-material-map.json','review_wood_kite.py','check_wood_kite_export.py','publish_wood_kite.py','NativeKiteCheck.java','wing_reference.py','wing_review.py')]
 delivery=dict(status='REAL_UV_PNG_EXPORTED_NATIVE_GECKOLIB_BAKED_GAME_PENDING',registered_entity='dynasty:luban_yisha',existing_forms=list(exported),new_entities=0,body_geometry_changed=False,animations_or_gameplay_changed=False,
  changed_runtime_files=entries,source_sha256={str(p.relative_to(ROOT)):digest(p) for p in owned},
  material_reference=dict(reviewed=101,accepted=100,excluded=1,record='../wing-reference-review.json'),
  verification=dict(geckolib_bake='PASS_4.8.4',full_clips_parsed=24,software_geometry_samples=26*81,reexport='PASS_9_FILES',uv='PASS',approved_resources='PASS',full_gradle_build='NOT_RUN_NO_JAVA_CODE_CHANGE',actual_game='PENDING'),
  resource_pack=dict(file=pack.name,sha256=digest(pack),installed=False),
  remaining_registered_art=['gongsun_wuwang','gongsun_wuwang_foot','taoyan_zhishi','taoyan_zhishi_phase2'],
  not_changed=['approved creature batches','held weapons','AI/skills/collision/drops','other chats files','prompt files','sound/brightness/live client'])
 write(OUT/'delivery.json',delivery)
 progress_path=ROOT/'tools/art/bestiary-v43/progress.json';progress=json.loads(progress_path.read_text())
 if 'previous_execution' not in progress:progress['previous_execution']=progress.get('latest_execution',{})
 progress.setdefault('previous_humanoid_candidate_research',dict(candidate_count=progress.pop('candidate_count',102),accepted_for_that_target=progress.pop('accepted_for_per_creature_gate',0),record='docs/art/bestiary-v43/reference-review.json'))
 progress.update(scope='Direct human confirmed: find unfinished already registered creatures; preserve approved art.',
  status='WOOD_KITE_TWO_EXISTING_FORMS_MATERIALS_DONE_GAME_PENDING_OTHER_FOUR_REFERENCE_PENDING',
  pending_user_scope=None,scope_answer='找尚未完成的已注册生物，已认可的不动',
  reference_gate_by_target={'luban_yisha':100,'gongsun_wuwang':0,'taoyan_zhishi':0},
  latest_execution=delivery,reference_review='docs/art/bestiary-v43/wing-reference-review.json')
 progress['completed_this_turn']=dict(entity='luban_yisha',existing_forms=2,stage='original pixel material and UV completion; no body geometry change',gallery='docs/art/bestiary-v43/wood-kite/index.html')
 write(progress_path,progress)
 print('Published both existing forms, real runtime resource override,100-reference gallery, exact preservation and explicit game-pending status.')

if __name__=='__main__':main()
