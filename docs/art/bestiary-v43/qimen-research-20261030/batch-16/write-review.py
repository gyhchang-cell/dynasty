from pathlib import Path
import json,hashlib,datetime,html,os
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sources=[]
def source(id,p,rg,kind='FIXED_SOURCE_REVIEW'):
 sources.append(dict(id=id,local=os.path.relpath(p,B),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reviewed_ranges=rg,review_kind=kind))
a=json.loads((B/'asset-acquisition.json').read_text())
for x in a['rows']:
 p=B/x['local'];suffix=p.suffix
 x['status']='ACTUAL_PNG_VIEWED_NATIVE_AND_12X' if suffix=='.png' else ('FULL_MTL_READ' if suffix=='.mtl' else 'OBJ_STRUCTURE_PARSED_AND_SOFTWARE_VIEWS_INSPECTED')
 x['reviewed_utc']=now
 source('texture' if suffix=='.png' else 'mtl' if suffix=='.mtl' else 'obj',p,[],x['status'])
save(B/'asset-acquisition.json',a)
a=json.loads((B/'consumer-acquisition.json').read_text())
for x in a['rows']:
 p=B/x['local'];x['status']='FULL_SOURCE_READ';x['reviewed_ranges']=[[1,x['lines']]];x['reviewed_utc']=now
 source(p.stem,p,[[1,x['lines']]])
save(B/'consumer-acquisition.json',a)
for id,path,rg in [('ChemthrowerCallbacks','sources/BluSunrize__ImmersiveEngineering/src/main/java/blusunrize/immersiveengineering/client/models/obj/callback/item/ChemthrowerCallbacks.java',[[1,76]]),('IEOBJLoader','sources/BluSunrize__ImmersiveEngineering/src/main/java/blusunrize/immersiveengineering/client/models/obj/IEOBJLoader.java',[[38,76]]),('SpecificIEOBJModel','sources/BluSunrize__ImmersiveEngineering/src/main/java/blusunrize/immersiveengineering/client/models/obj/SpecificIEOBJModel.java',[[185,285]]),('item-json','batch-04/sources/BluSunrize__ImmersiveEngineering/src/generated/resources/assets/immersiveengineering/models/item/chemthrower.json',[[1,160]])]:
 p=R/path
 if not p.exists():
  matches=list(R.glob('batch-04/**/'+Path(path).name)) if id=='item-json' else list((R/'sources').glob('**/'+Path(path).name))
  assert len(matches)==1,(id,matches);p=matches[0]
 source(id,p,rg)
e=[]
def add(id,finding,refs,limit):e.append(dict(id=id,finding=finding,sources=refs,limit=limit,credit_added=0))
add('A01','实际固定OBJ、MTL、64×64PNG同时检查；272顶点、179个四边形、7组共用一个材质。PNG只有0/255透明度，透明像素不能当作黑色材质缺口。',['obj','mtl','texture'],'数量只是同一资源的结构统计；不新增生物或武器参考计数。')
add('A02','贴图原图和12倍最近邻图已看：深灰金属大面、通风暗缝、红蓝容器及棕色握持部件分工明确，亮部集中在边缘转折、带箍与接口。',['texture','obj'],'该参考也有重复边框/铆接，不能声称它完全没有；借鉴用途分区与主次，不复制工业题材或原像素。')
add('A03','MTL只指向chemthrower贴图，没有另写Kd；默认回调不替换贴图/原色。材质颜色和sprite消费者会优先考虑回调及可选Shader，因此基础贴图检查与改装Shader显示必须区分。',['mtl','MaterialColorGetter','MaterialSpriteGetter','IEOBJCallback'],'没有运行Shader或最终atlas；不把软件原色图当所有游戏显示情形。')
add('A04','非absoluteUV路径在PolygonUtils明确使用getU(16*u)、getV(16*(1-v))；离线UV按此翻转V，实际200个UV坐标均在0..1，叠加图已逐组查看。',['PolygonUtils','IEOBJCallback','obj'],'源码与离线采样对应，不等同执行了ModelSplitter解析、图集烘焙和GPU插值。')
add('A05','可见性回调始终显示base/grip/cage/tanks；容量和多罐仅各追加large_tank/multi_tank，最后tank仍为true。默认111面、容量121面、多罐169面、全开179面。',['ChemthrowerCallbacks','obj'],'不能把基础tank误读成升级时必隐藏；离线按回调集合筛组，没有假定独立新物品。')
add('A06','四种可见组合都用相同全模型取景，另给7组拆解图。观察到外壳、带箍与容器有连续组织；色块不能仅按每面平均色代替。',['obj','texture','ChemthrowerCallbacks'],'原始OBJ正交yaw0/45/90，不是Boss前侧背，也没有玩家手臂、display矩阵或真实光照。')
add('A07','物品JSON为动态IE OBJ、cutout层，左右手和一三人称有各自display变换；Chemthrower回调的额外姿态仅给Bulwark第三人称，普通玩家不能直接套用。',['item-json','ChemthrowerCallbacks'],'这批只看静态原OBJ；持物矩阵组合与实际持握仍待验证。')
add('A08','IEOBJLoader先加载、quadify并重算零法线，SpecificIEOBJModel再按可见组、材质、回调和pass烘焙；自己的三角化软件预览只用于纹理观察。',['IEOBJLoader','SpecificIEOBJModel'],'未运行第三方parser或游戏烘焙；前端细线等差异保留为软件/源模型待核，不指认为游戏缺陷。')
views=['reference-assets/chemthrower-inspection-12x.png','uv-overlay-12x.png','default-software.png','capacity-software.png','multitank-software.png','both-software.png','groups-software.png']
v=dict(saved_utc=now,status='SAVED_ACTUAL_FIXED_OBJ_MTL_PNG_AND_MATERIAL_CONSUMERS',repo='BluSunrize/ImmersiveEngineering',commit='e63e4824800945eccf3684200a2c2270e2e1cdf2',sources=sources,evidence=e,actually_viewed=views,source_asset_credit='Immersive Engineering；OBJ作者注释Damien A.W. Hazard；仅研究，禁止冒充Dynasty原创交付',new_source_families=0,new_accepted_gate_credit=0,production_changed=False,java_game_started=False,pending=['真正持物变换、图集烘焙、ModelSplitter与游戏基础光照尚未运行','这是已登记家族延伸，未满足逐生物100或机巧1000参考门槛'])
save(B/'obj-texture-review.json',v)
out=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>B16 实际OBJ与像素材质</title><style>body{font:16px/1.6 system-ui;background:#162027;color:#e0e6e9;max-width:1200px;margin:28px auto}a{color:#a4dde5}img{max-width:100%;image-rendering:pixelated}article{padding:16px;border-bottom:1px solid #43535a}</style><h1>B16 · 实际OBJ、MTL、PNG与逐面采样</h1><p>外部作者研究资产，非Dynasty新作品。离线正交预览，不是游戏截图。不新增参考计数，不修改生产资源。</p><p><a href="obj-texture-review.json">固定来源与判断边界</a> · <a href="asset-inspection.json">UV/组统计</a> · <a href="local-verification.json">静态检查</a></p>']
for x in e:out.append('<article><b>'+x['id']+'</b><p>'+html.escape(x['finding'])+'</p><small>'+html.escape(x['limit'])+'</small></article>')
for f in views:out.append('<figure><figcaption>'+html.escape(f)+' · 源资产软件检查</figcaption><img src="'+f+'"></figure>')
(B/'index.html').write_text('\n'.join(out)+'\n</html>')
save(B/'progress.json',dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',new_source_families=0,new_accepted_credit=0,report='index.html',next='补读尚未看的固定源模型/PNG或新在范围链，按家族去重'))
p=json.loads((R/'progress.json').read_text());old=p['this_batch']
if not any(x['id']==old['id'] for x in p['previous_batches']):p['previous_batches'].append(dict(old,report=old['id']+'/index.html'))
p.update(updated_utc=now,latest_batch=B.name,this_batch=dict(id=B.name,source_studies=0,existing_family_context_extensions=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='实际OBJ/MTL/PNG和材质消费者，仍为既有IE家族，0新参考。'))
p['continuation_window'].update(last_saved_utc=now,report=B.name+'/index.html',progress=B.name+'/progress.json',status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH')
p['next']=['补尚未看的已固定模型+PNG与持物消费者，或真正新在范围链；按家族去重','记录实际物品任务映射与资产问题，保持只读生产资源与主账边界','119注册清点不代表新参考，逐生物100门槛和已认可资产不变','不启动游戏；实际运行与独立验收仍待，计数不自增']
save(R/'progress.json',p);print('saved',len(e))
