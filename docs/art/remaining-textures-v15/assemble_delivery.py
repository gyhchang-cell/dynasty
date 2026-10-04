"""Collect narrowly scoped candidates; validate references; build offline gallery.
Does not write src, build jars, run the game, or touch an installed instance.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,zipfile,collections,csv,html
D=Path(__file__).resolve().parent; ROOT=D.parents[2]; S=ROOT/'src/main/resources'; AS=S/'assets/dynasty'
GROUPS=['items-core','items-equipment','items-accessories','armor-a','armor-b','blocks-bounty']
PACK=D/'resource-pack'; BACK=D/'source-backup'; PRE=D/'previews'
SNAP=json.loads((D/'initial-source-hashes.json').read_text())
AUD=json.loads((D/'audit-items.json').read_text()); BYID={r['id']:r for r in AUD['items']}
LANG=json.loads((AS/'lang/zh_cn.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def label(name):return LANG.get('item.dynasty.'+name,LANG.get('block.dynasty.'+name,name))
def main():
 PACK.mkdir(exist_ok=True);BACK.mkdir(exist_ok=True);PRE.mkdir(exist_ok=True)
 rows=[];seen=set();models=[]
 for group in GROUPS:
  for p in sorted((D/group/'candidate').rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(D/group/'candidate');assert str(rel).startswith('assets/dynasty/')
   assert rel not in seen,rel;seen.add(rel)
   out=PACK/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
   src=S/rel;src_rel=str(src.relative_to(ROOT));source_hash=None
   if src.exists():
    source_hash=sha(src);assert SNAP.get(src_rel)==source_hash,('source changed during task',src_rel)
    before=BACK/rel;before.parent.mkdir(parents=True,exist_ok=True)
    if before.exists():assert sha(before)==source_hash
    else:shutil.copy2(src,before)
   if p.suffix=='.png':
    im=Image.open(p).convert('RGBA');alphas=sorted(set(im.getchannel('A').tobytes()));assert set(alphas)<={0,255}
    kind='item' if '/textures/item/' in str(rel) else 'armor' if '/models/armor/' in str(rel) else 'block'
    expected=(32,32) if kind=='item' else (64,32) if kind=='armor' else (16,16);assert im.size==expected,(rel,im.size)
    if kind=='item':
     bb=im.getbbox();assert bb and bb[0]>0 and bb[1]>0 and bb[2]<32 and bb[3]<32,(rel,bb)
     record=BYID[p.stem];assert record['classification']=='legacy_pending' or p.stem=='dark_iron_chestplate'
     assert record['sha256']==source_hash
    if kind=='block':assert alphas==[255]
    rows.append({'id':'dynasty:'+p.stem,'name':label(p.stem),'kind':kind,'group':group,'resource_path':str(rel),
      'candidate_path':str(out.relative_to(D)),'before_path':str((BACK/rel).relative_to(D)) if src.exists() else None,
      'source_path':src_rel if src.exists() else None,'source_sha256':source_hash,'sha256':sha(out),
      'dimensions':list(im.size),'visible_colors':len({c[:3] for c in im.getdata() if c[3]}),'alpha_values':alphas,
      'status':'resource_pack_only_not_installed','animation':False,'emissive':False})
   elif p.suffix=='.json':models.append({'path':str(rel),'sha256':sha(out),'source_sha256':source_hash})
   else:raise AssertionError(rel)
 ids={r['id'].split(':')[1] for r in rows if r['kind']=='item'}
 expected=set(AUD['pending_non_armor_ids']+AUD['pending_armor_ids'])|{'dark_iron_chestplate'}
 assert ids==expected,{'missing':sorted(expected-ids),'extra':sorted(ids-expected)}
 assert len([r for r in rows if r['kind']=='armor'])==46
 assert len([r for r in rows if r['kind']=='block'])==5
 assert len(models)==29
 # All per-item models are backed up and resolved, even if no model update is needed.
 for name in ids:
  p=AS/'models/item'/f'{name}.json';r=p.relative_to(S);dst=BACK/r;dst.parent.mkdir(parents=True,exist_ok=True)
  assert SNAP[str(p.relative_to(ROOT))]==sha(p)
  if dst.exists():assert sha(dst)==sha(p)
  else:shutil.copy2(p,dst)
 # Minecraft's own parent/resource definitions are read from the local 1.20.1 archive.
 jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
 z=zipfile.ZipFile(jar);zn=set(z.namelist());cache={}
 def exists(rel):return (PACK/rel).is_file() or (S/rel).is_file() or rel in zn
 def resource(name,folder,suffix):
  ns,path=name.split(':',1) if ':' in name else ('minecraft',name)
  return f'assets/{ns}/{folder}/{path}{suffix}'
 def model(name,chain=()):
  if name in cache:return cache[name]
  assert name not in chain,('parent cycle',chain,name)
  if name in ('builtin/generated','minecraft:builtin/generated','builtin/entity','minecraft:builtin/entity'):return {'textures':{}}
  path=resource(name,'models','.json');assert exists(path),('missing model',path)
  raw=next((q.read_text() for q in [PACK/path,S/path] if q.exists()),None)
  d=json.loads(raw if raw is not None else z.read(path))
  par=model(d['parent'],chain+(name,)) if 'parent' in d else {};m=dict(par);m.update(d);m['textures']={**par.get('textures',{}),**d.get('textures',{})};cache[name]=m;return m
 def resolve_tex(value,textures,visited=()):
  if value.startswith('#'):
   key=value[1:];assert key in textures and key not in visited,('bad texture variable',value)
   return resolve_tex(textures[key],textures,visited+(key,))
  assert exists(resource(value,'textures','.png')),('missing texture',value);return value
 references=[]
 for name in sorted(ids):
  m=model('dynasty:item/'+name);tex=m.get('textures',{});assert tex.get('layer0')=='dynasty:item/'+name,(name,tex)
  for value in tex.values():resolve_tex(value,tex)
  for e in m.get('elements',[]):
   for face in e.get('faces',{}).values():resolve_tex(face['texture'],tex)
  for o in m.get('overrides',[]):model(o['model'])
  assert not exists(resource('dynasty:item/'+name,'textures','.png.mcmeta')),('unexpected old animation',name)
  references.append({'id':'dynasty:'+name,'item_model':'dynasty:item/'+name,'layer0':tex['layer0'],
   'effective_parent':json.loads((PACK/'assets/dynasty/models/item'/f'{name}.json').read_text()).get('parent') if (PACK/'assets/dynasty/models/item'/f'{name}.json').exists() else json.loads((AS/'models/item'/f'{name}.json').read_text()).get('parent'),
   'model_changed':(PACK/'assets/dynasty/models/item'/f'{name}.json').exists()})
 bounty=model('dynasty:block/bounty_board')
 for v in bounty['textures'].values():resolve_tex(v,bounty['textures'])
 assert model('dynasty:item/bounty_board')['textures']==bounty['textures']
 # Preservation verification across the original observed project, not a rollback.
 changed=[];missing=[]
 for rel,old in SNAP.items():
  p=ROOT/rel
  if not p.exists():missing.append(rel)
  elif sha(p)!=old:changed.append(rel)
 protected_items=[r for r in AUD['items'] if r['classification']=='completed_elsewhere']
 protected_blocks=AUD['block_textures']
 for r in protected_items+protected_blocks:assert sha(ROOT/r['path'])==r['sha256'],('protected source modified',r['id'])
 for r in AUD['items']:assert sha(ROOT/r['path'])==r['sha256'],('source item modified',r['id'])
 dup=collections.defaultdict(list)
 for r in rows:dup[r['sha256']].append(r['id'])
 duplicates=[v for v in dup.values() if len(v)>1];assert not duplicates,duplicates
 counts=dict(collections.Counter(r['kind'] for r in rows))
 report={'result':'PASS','counts':counts,'png_total':len(rows),'models_changed_in_pack':len(models),'item_ids_verified':len(ids),
  'pending_items_completed':339,'approved_dark_iron_refinement':1,'armor_sets':23,'new_block_id':'dynasty:bounty_board',
  'protected_other_task_item_pngs':130,'protected_other_task_block_pngs':34,'uncertain_item_ids':['zhuque_fan','juling_axe','bawang_spear'],
  'source_item_pngs_unchanged':476,'duplicate_candidate_png_hashes':duplicates,
  'all_candidate_pngs_binary_alpha':True,'models_and_textures_resolve':True,'native_sizes_verified':True,
  'unexpected_original_files_changed':changed,'unexpected_original_files_missing':missing,
  'external_changes_note':'Observed concurrently; no rollback. This batch writes only docs/art/remaining-textures-v15 and exported outputs.',
  'game_tested':False,'installed_to_project_src':False,'synced_to_game_instance':False,'animations_added':0,'emissive_rendering_added':False}
 write(D/'delivery-manifest.json',{'files':rows,'models':models,'report':report})
 write(D/'verification.json',report);write(D/'resource-references.json',references)
 write(PACK/'pack.mcmeta',{'pack':{'pack_format':15,'description':'Dynasty v15 · 原生像素剩余物品与盔甲 / 1.20.1 / 候选资源包'}})
 with (D/'resource-inventory.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['id','type','current_path','current_resolution','previous_status','evidence','new_candidate','new_resolution','integration'])
  for r in AUD['items']:
   new=next((v for v in rows if v['kind']=='item' and v['id']==r['namespace_id']),None)
   w.writerow([r['namespace_id'],'item',r['path'],'x'.join(map(str,r['size'])),r['classification'],'; '.join(e['path'] for e in r['evidence']+r['legacy_evidence']),new['candidate_path'] if new else '', '32x32' if new else '', 'candidate pack only' if new else 'preserved'])
  for r in AUD['block_textures']:w.writerow([r['namespace_resource'],'block',r['path'],'x'.join(map(str,r['size'])),r['classification'],'; '.join(e['path'] for e in r['evidence']),'','','preserved'])
  w.writerow(['dynasty:bounty_board','block','models/block/bounty_board.json (minecraft:block/bookshelf)','16x16','confirmed temporary','docs/content/bounty-board-v1.md:178','resource-pack/assets/dynasty/models/block/bounty_board.json','5 x 16x16','candidate pack only'])
 gallery(rows,counts,report)
 with zipfile.ZipFile(D/'Dynasty-v15-candidate-resource-pack.zip','w',zipfile.ZIP_DEFLATED) as out:
  for p in sorted(PACK.rglob('*')):
   if p.is_file():out.write(p,p.relative_to(PACK))
 print(json.dumps(report,ensure_ascii=False,indent=2))
def gallery(rows,counts,report):
 group_labels={'items-core':'材料与食物','items-equipment':'旧兵器与工具','items-accessories':'饰品与机关材料','armor-a':'盔甲·材质系列','armor-b':'盔甲·高阶系列','blocks-bounty':'告示板'}
 cards=[]
 for r in rows:
  if r['kind']!='item':continue
  id=r['id'];p=r['candidate_path'];before=r['before_path'];old=Image.open(D/before)
  cards.append(f'<article data-group="{r["group"]}" data-search="{html.escape(id+" "+r["name"])}"><h3>{html.escape(r["name"])}</h3><code>{id}</code><div class="compare"><figure><img class="zoom" loading="lazy" src="{before}"><figcaption>原稿 {old.width}×{old.height}</figcaption></figure><figure><a href="{p}"><img class="zoom" loading="lazy" src="{p}"></a><figcaption>新稿 32×32</figcaption></figure></div><div class="native">原尺寸：<img loading="lazy" src="{before}" width="{old.width}" height="{old.height}"><img loading="lazy" src="{p}" width="32" height="32"></div><small>{r["visible_colors"]} 色 · 透明边缘 0/255 · <a href="{p}" download>PNG</a></small></article>')
 opts=''.join(f'<option value="{k}">{v}</option>' for k,v in group_labels.items() if k!='blocks-bounty')
 armora=json.loads((D/'armor-a/manifest.json').read_text());armorb=json.loads((D/'armor-b/manifest.json').read_text())
 armor=[]
 for group,names in [('armor-a',armora['sets']),('armor-b',[s['set'] for s in armorb['sets']])]:
  for name in names:
   pic=f'{group}/previews/{name}-worn.png' if group=='armor-a' else f'{group}/previews/{name}-overview.png'
   armor.append(f'<details><summary>{html.escape(label(name+"_chestplate"))} · {name}</summary><img class="wide" loading="lazy" src="{pic}"><div class="atlas">'+''.join(f'<a href="resource-pack/assets/dynasty/textures/models/armor/{name}_layer_{n}.png"><img loading="lazy" width="512" height="256" src="resource-pack/assets/dynasty/textures/models/armor/{name}_layer_{n}.png"></a>' for n in (1,2))+'</div></details>')
 content='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>王朝 · 剩余贴图 v15</title>
<style>*{box-sizing:border-box}body{background:#f0eee5;color:#273933;font:16px/1.7 system-ui,sans-serif;margin:0}main{max-width:1440px;margin:auto;padding:32px}header{border-bottom:1px solid #c0c4b5;padding-bottom:25px}h1{font-size:38px;margin:8px 0}h2{margin-top:38px}a{color:#357369}p{max-width:1050px}.pill{display:inline-block;padding:6px 12px;background:#d9e4d4;border-radius:8px;margin-right:8px}.controls{position:sticky;top:0;background:#f0eee5f5;padding:15px 0;z-index:1;display:flex;gap:14px;flex-wrap:wrap}input,select{font:inherit;border:1px solid #a9b3a4;padding:9px 12px;border-radius:6px;background:#fffef9}input{min-width:320px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px}article{background:#faf9f1;border:1px solid #ccd0c2;border-radius:10px;padding:16px}article h3{margin:0;font-size:19px}code{font-size:12px;overflow-wrap:anywhere;color:#5d6d65}.compare{display:flex;justify-content:space-between;gap:10px}.compare figure{margin:15px 0;text-align:center}.zoom{width:112px;height:112px;object-fit:contain}.native{display:flex;align-items:center;gap:18px;min-height:52px;overflow:auto}.native img{object-fit:contain;flex-shrink:0}img{image-rendering:pixelated}.compare img,.native img,.atlas img{background:repeating-conic-gradient(#d9ddd3 0 25%,#e8ebe2 0 50%) 0/16px 16px}small,figcaption{font-size:12px;color:#647365}.wide{max-width:100%;height:auto;display:block;margin:18px 0}.atlas{display:flex;gap:20px;overflow:auto}.atlas img{max-width:100%;height:auto}details{border:1px solid #bec8bb;background:#e6eadf;padding:14px;margin:12px 0}summary{cursor:pointer;font-weight:600}.note{background:#e3e8da;border-left:4px solid #5b887b;padding:14px 20px}button{font:inherit}article[hidden]{display:none}</style><main>
<header><div>DYNASTY / ORIGINAL NATIVE PIXELS</div><h1>剩余贴图 · v15</h1><p>339 件旧占位或未精修物品已补齐，另精修已认可方向的玄铁胸甲。包括 23 套盔甲的 92 张物品图标、46 张穿戴展开图；告示板另有 5 张原生 16×16 面贴图。</p><span class="pill">340 件物品</span><span class="pill">23 套盔甲</span><span class="pill">391 张 PNG</span><span class="pill">29 个必要模型引用更新</span><p><a href="Dynasty-v15-candidate-resource-pack.zip" download>下载 1.20.1 候选资源包 ZIP</a> · <a href="resource-inventory.csv">完整资源清单</a> · <a href="delivery-manifest.json">逐文件 SHA256</a> · <a href="verification.json">静态检查</a> · <a href="README.md">交付说明</a></p><div class="note">仅接入此独立资源包，未覆盖项目 src、模组 JAR 或正在玩的实例。未启动游戏；穿戴预览按实际 UV 离线绘制，尚未游戏内实测。新稿均静态；亮色不是发光功能。</div></header>
<h2>原尺寸与最近邻对比</h2><p>直接在 32×32 网格绘制物品，延续这些资源已有的分辨率规范；盔甲保留实际 64×32 展开图。没有高清原稿缩小、抗锯齿或随机噪声。材料与装备靠轮廓、色块、接缝和局部亮边区分。</p><div class="controls"><input id="q" aria-label="搜索名称或ID" placeholder="搜索中文名称 / ID"><select id="g" aria-label="筛选类型"><option value="">全部 340 件</option>OPTIONS</select><span id="count"></span></div><div class="grid" id="cards">CARDS</div>
<h2>23 套盔甲穿戴与 UV</h2><p>头盔开脸孔，胸甲、护腿、靴子各自使用正确区域；左右肢体遵循标准镜像。平面图标中的角冠和肩形不会凭贴图增加穿戴模型几何。</p>ARMOR
<h2>告示板 · 唯一补绘的未完成方块</h2><p>项目说明明确标注此前是临时书架贴图。新图分正面告示、背面木板、侧面木纹及顶底面；保持原完整立方体和交互代码。当前方块无朝向属性，因此告示正面固定北向，需旋转放置须由代码任务实现。</p><a href="blocks-bounty/previews/bounty-board-comparison.png"><img class="wide" src="blocks-bounty/previews/bounty-board-comparison.png"></a><p>上图同时包含 1×、8× 最近邻、3×3 重复铺贴和原书架对比。<a href="blocks-bounty/manifest.json">五个面与模型引用</a></p>
<h2>已完成资源保留</h2><p>其他任务已有完成记录的 130 张物品、34 张方块贴图保持原样。将军、玉、天空、青铜、玄天五套盔甲未重复制作；展示架及并行龙口/召唤祭坛资源未改。</p><p>诸葛扇（zhuque_fan 的中文名以项目为准）、juling_axe、bawang_spear 的完成来源仍不够明确，按最初约定保留、不覆盖。具体证据见 <a href="audit-items.json">原始审计</a> 与 <a href="PROTECTED.md">保护清单</a>。本对话已完成的铜镜、玉佩、雷纹护符及 v11 样稿没有再次重画。</p><p><a href="source-backup/">本轮目标源文件备份</a> · <a href="resource-references.json">340 件物品引用核对</a></p></main>
<script>const q=document.querySelector('#q'),g=document.querySelector('#g'),cards=[...document.querySelectorAll('article')];function filter(){let n=0;for(const c of cards){const ok=(!g.value||c.dataset.group===g.value)&&c.dataset.search.toLowerCase().includes(q.value.trim().toLowerCase());c.hidden=!ok;if(ok)n++}document.querySelector('#count').textContent=n+' / '+cards.length}q.addEventListener('input',filter);g.addEventListener('change',filter);filter();</script></html>'''
 content=content.replace('OPTIONS',opts).replace('CARDS',''.join(cards)).replace('ARMOR',''.join(armor))
 # Use actual project translations, not a guessed localized weapon name.
 content=content.replace('诸葛扇（zhuque_fan 的中文名以项目为准）',html.escape(label('zhuque_fan'))+'（zhuque_fan）')
 (D/'review.html').write_text(content)
if __name__=='__main__':main()
