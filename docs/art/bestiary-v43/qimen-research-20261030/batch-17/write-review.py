from pathlib import Path
import json,hashlib,datetime,os,html,itertools,math
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def src(id,p,rg,kind='FIXED_SOURCE_REVIEW'):return dict(id=id,local=os.path.relpath(p,B),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reviewed_ranges=rg,kind=kind)
s=[];a=json.loads((B/'asset-acquisition.json').read_text())
for x in a['rows']:
 p=B/x['local'];x['status']='ACTUAL_PNG_VIEWED_INTEGER_CONTACT' if p.suffix=='.png' else 'FULL_JSON_READ';x['reviewed_utc']=now
 s.append(src(x['path'].split('assets/grapplemod/')[1],p,[] if p.suffix=='.png' else [[1,len(p.read_text().splitlines())]],x['status']))
save(B/'asset-acquisition.json',a)
for id,path,rg in [('RenderGrapplehookEntity','batch-03/sources/yyon__grapplemod/src/main/java/com/yyon/grapplinghook/entities/grapplehook/RenderGrapplehookEntity.java',[[1,377]]),('ClientSetup','batch-03/sources/yyon__grapplemod/src/main/java/com/yyon/grapplinghook/client/ClientSetup.java',[[99,148]]),('GrapplehookItem','batch-03/sources/yyon__grapplemod/src/main/java/com/yyon/grapplinghook/items/GrapplehookItem.java',[[544,574]]),('Vec','batch-04/sources/yyon__grapplemod/src/main/java/com/yyon/grapplinghook/utils/Vec.java',[[99,109],[176,196]])]:
 p=R/path
 if id=='GrapplehookItem':rg=[[544,len(p.read_text().splitlines())]]
 s.append(src(id,p,rg))
m=json.loads((B/'native-consumers.json').read_text());ranges={'ItemOverride':[[1,78]],'ItemOverrides':[[1,145]],'ItemModelGenerator':[[1,218]],'BlockModel':[[85,150],[180,230],[275,305]],'ItemRenderer':[[95,148],[203,237]]}
for x in m['files']:
 x['reviewed_ranges']=ranges[x['id']];x['status']='SELECTED_RANGES_READ';s.append(src(x['id'],B/x['reading_view'],x['reviewed_ranges'],'EXACT_FORGE_47_1_0_RECONSTRUCTION'))
save(B/'native-consumers.json',m)
for id,manifest in [('UnbakedGeometryHelper','forge-helper-provenance.json')]:
 x=json.loads((B/manifest).read_text());s.append(src(id,B/x['local'],x['reviewed_ranges'],'OFFICIAL_FORGE_47_1_0_SOURCE'))
for x in json.loads((B/'parent-provenance.json').read_text())['files']:s.append(src(Path(x['entry']).stem+'-parent',B/x['local'],x['reviewed_ranges'],'OFFICIAL_MC_1_20_1_MODEL_JSON'))
# Conditional replay of the actually read threshold matcher, not Minecraft execution.
model=json.loads((B/'reference-assets/src/main/resources/assets/grapplemod/models/item/grapplinghook.json').read_text());names=['attached','magnet','enderstaff','motor','smart','double','rocket','hook'];trace=[]
for bits in itertools.product([0,1],repeat=8):
 props=dict(zip(names,bits));winner='grapplemod:item/grapplinghook';idx=None
 for i in range(len(model['overrides'])-1,-1,-1):
  rule=model['overrides'][i]
  if all(props.get(k,float('-inf'))>=threshold for k,threshold in rule['predicate'].items()):winner=rule['model'];idx=i;break
 trace.append(dict(properties=props,model=winner,source_rule_index=idx))
save(B/'conditional-override-trace.json',dict(kind='STATIC_SOURCE_MATCHER_REPLAY_NOT_GAME',states=trace,hook_present_all_select_hook=all(x['model']=='grapplemod:item/hook' for x in trace if x['properties']['hook']),zero_is_lower_bound_not_equality=True,independent_reference_credit=0))
e=[]
def add(id,f,refs,limit):e.append(dict(id=id,finding=f,sources=refs,limit=limit,credit_added=0))
add('G01','当前钩头不是直接绑定HOOK_TEXTURES画平面：活着的renderer分支给新栈写hook标签，ItemRenderer.getModel解析覆盖，再用NONE上下文绘制真实baked item。老平面代码整段被注释。',['RenderGrapplehookEntity','ItemRenderer','models/item/grapplinghook.json'],'getTextureLocation返回的textures/entity/entity_hook.png在固定树不存在，但当前钩体绘制读item/entity_hook.png；不能因此断言实际钩体缺图。')
add('G02','最后一条hook=1覆盖优先，hook属性按标签是否存在而非boolean值真假。原生按列表倒序、每属性>=阈值匹配；attached=0不表示必须未挂接。',['models/item/grapplinghook.json','ClientSetup','GrapplehookItem','ItemOverrides'],'256种二值输入仅离线条件回放，未运行客户端；升级子模型与其全部贴图本批未读，不宣称整套外观闭合。')
add('G03','held attached属性来自当前entity对应控制器且不是AirfrictionController，entity为null则0；它不是检查这根钩实体或当前栈本身。飞出钩getModel传null owner，由hook标签稳定选hook模型。',['ClientSetup','RenderGrapplehookEntity'],'物理实体attached、控制器存在和物品覆盖状态是不同身份；不据此推导网络时序无误。')
add('G04','hook模型明确使用grapplemod:item/entity_hook，rope模型使用item/rope；它们都继承handheld→generated。真正绳管则单独用textures/entity/rope.png。',['models/item/hook.json','models/item/rope.json','handheld-parent','generated-parent','RenderGrapplehookEntity'],'textures/item/hook.png也是实际查看的备用资产，不能因为名字相近便认为当前hook JSON加载它。')
add('G05','5张原始PNG的整数倍图实际查看：16×16物品靠冷灰钩头与暖棕绳圈区别，entity钩头省略绳圈；实体绳图仅2×16，暖色阶有编织方向。',['textures/item/grapplinghook.png','textures/item/hook.png','textures/item/entity_hook.png','textures/item/rope.png','textures/entity/rope.png'],'这是1个既有机制家族的不同用途资源，不计5个新生物参考；不复制作者像素。')
add('G06','generated不是自建厚3D钩爪。Forge同版本helper把builtin/generated送ItemModelGenerator；基面Z7.5..8.5、整图正反面及透明轮廓侧面来自PNG。',['UnbakedGeometryHelper','ItemModelGenerator','generated-parent'],'这是薄挤出像素物品；本批没有执行atlas、烘焙或GPU，也不把其薄片结构作为所有生物制作标准。')
add('G07','实际绳段是四侧方管，half-width0.025，短于0.05的段跳过；当前调用taut固定1，因此每段一个纵向quad，不走16段垂弧。',['RenderGrapplehookEntity'],'此处只是视觉绳管，不代表物理折点数量或真实拉力；被注释的hookEntity.taut不生效。')
add('G08','每根折段都把V从0铺到1，未按世界长度重复；2×16编织贴图会随段长拉伸。最后手端cap用V0.99..1，折点列表首尾分别换成插值钩位置与手端。',['RenderGrapplehookEntity','textures/entity/rope.png'],'不同长度的纹理密度不自动一致；不把物理折线和固定密度绳纹混淆。')
add('G09','角度消费者有实际单位不匹配：Vec.getYaw/getPitch明确toDegrees，renderer把其结果及45/-45/-90常量交给JOML setAngleAxis。JOML1.10.5接口单位是弧度。',['Vec','RenderGrapplehookEntity'],'仅记录参考源的静态单位边界，不修外部源码、不改Dynasty、不声称已测到实际朝向。官方API链接单独保存；不是新机制案例。')
add('G10','钩体绘制缩放0.5后额外旋转，物品上下文是NONE；正常手持则继承handheld的一三人称左右手变换。两者不能拿同一角度截图互相证明持握正确。',['RenderGrapplehookEntity','handheld-parent','ItemRenderer'],'源路径已经分开，真正手臂、FOV、动画和相机画面仍未运行。')
v=dict(saved_utc=now,status='SAVED_REAL_GRAPPLE_MODEL_PNG_OVERRIDE_AND_ROPE_CONSUMERS',repo='yyon/grapplemod',commit='40080155cf1160b3ef4c6db9d47d01746925f9f1',version='1.20.1-v13 / Forge47.1.0',sources=s,evidence=e,external_primary_docs=[dict(url='https://joml-ci.github.io/JOML/apidocs/org/joml/Quaternionf.html',version='1.10.5 per cached official MC dependency JSON',viewed_utc=now,observation='setAngleAxis accepts radians; Vec getter returns degrees')],actually_viewed=['actual-textures-contact.png'],new_source_families=0,new_accepted_gate_credit=0,production_changed=False,java_game_started=False,pending=['本批没有完整查看升级子模型PNG或游戏光照','不是100相似生物或1000机巧门槛的完成记录','实际持握、断线、读档和模型烘焙仍待'])
save(B/'model-texture-review.json',v)
a=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>B17 钩头真实模型/贴图</title><style>body{font:16px/1.6 system-ui;background:#172129;color:#dce5e8;max-width:1120px;margin:30px auto}a{color:#9ed9e6}img{max-width:100%;image-rendering:pixelated}article{padding:16px;border-bottom:1px solid #40535c}</style><h1>B17 · 钩头、物品覆盖、绳纹消费者</h1><p>外部固定源研究，不是Dynasty新模型。0新参考，生产资源未动，未启动游戏。</p><p><a href="model-texture-review.json">真实来源与边界</a> · <a href="conditional-override-trace.json">条件覆盖回放</a> · <a href="local-verification.json">静态检查</a></p><img src="actual-textures-contact.png">']
for x in e:a.append('<article><b>'+x['id']+'</b><p>'+html.escape(x['finding'])+'</p><small>'+html.escape(x['limit'])+'</small></article>')
a.append('<p><a href="https://joml-ci.github.io/JOML/apidocs/org/joml/Quaternionf.html">JOML官方API：角度单位</a></p></html>');(B/'index.html').write_text('\n'.join(a))
save(B/'progress.json',dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',report='index.html',new_source_families=0,new_accepted_credit=0,next='真正新在范围链或旧链未读恢复边界；不按PNG/文件/状态重复计数'))
p=json.loads((R/'progress.json').read_text());old=p['this_batch']
if not any(x['id']==old['id'] for x in p['previous_batches']):p['previous_batches'].append(dict(old,report=old['id']+'/index.html'))
p.update(updated_utc=now,latest_batch=B.name,this_batch=dict(id=B.name,source_studies=0,existing_family_context_extensions=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='同一GrappleMod家族真实JSON/PNG与同版本Forge覆盖消费者，0新增参考。'));p['continuation_window'].update(last_saved_utc=now,report=B.name+'/index.html',progress=B.name+'/progress.json',status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH');save(R/'progress.json',p);print('saved',len(e))
