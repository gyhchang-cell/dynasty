from pathlib import Path
import json,datetime,hashlib,html,os
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):(B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ranges={'SynchedEntityData':[[1,287]],'ClientboundSetEntityDataPacket':[[1,43]],'ModelPart':[[1,358]],'CubeDefinition':[[1,37]],'LayerDefinition':[[1,24]],'EntityRenderDispatcher':[[1,190],[348,364]],'EntityRenderer':[[1,106]],'PoseStack':[[1,105]],'PartDefinition':[[1,53]],'EntityDataSerializers':[[31,42],[135,148],[178,190]],'ClientPacketListener':[[490,508],[521,579]],'RenderType':[[34,48],[188,198]],'RenderStateShard':[[75,86],[508,542]],'VertexConsumer':[[1,84]],'AbstractTexture':[[1,97]],'SimpleTexture':[[1,132]],'TextureManager':[[1,155],[210,241]]}
m=json.loads((B/'acquisition.json').read_text());registry=[]
for f in m['files']:
 id=Path(f['path']).stem;f['id']=id;f['reviewed_ranges']=ranges[id];f['read_status']='FULL_FILE_READ' if f['reviewed_ranges']==[[1,f['lines']]] else 'SELECTED_RANGES_READ'
 registry.append(dict(id=id,local=f['reading_view'],sha256=f['reading_view_sha256'],lines=f['lines'],reviewed_ranges=f['reviewed_ranges'],version='forge-47.3.0',provenance='acquisition.json'))
for a in m['assets']:a['review_status']='ORIGINAL_PNG_VISUALLY_VIEWED' if a['path'].endswith('.png') else 'FULL_FILE_READ'
m['review_updated_utc']=now;save('acquisition.json',m)
def old(id,p,rs,version,origin):
 registry.append(dict(id=id,local=os.path.relpath(p,B),sha256=sha(p),lines=len(p.read_text().splitlines()),reviewed_ranges=rs,version=version,provenance=origin))
s=R/'batch-06/sources/dercodeKoenig__marvins-minecraft-mods/aw_vehicles/src/main/java/Vehicles'
version='dercodeKoenig/marvins-minecraft-mods@20d02ec1300ff6011683d9fd43ef76fd47256234; aw_vehicles1.0.6 MC1.20.1 Forge47.3.0'
for id,n,rs in [('Ballista','Ballista.java',[[29,63],[96,184],[290,306]]),('BallistaBolt','BallistaBolt.java',[[27,51],[69,183]]),('BallistaRenderer','BallistaRenderer.java',[[1,476]]),('BallistaBoltRenderer','BallistaBoltRenderer.java',[[1,228]]),('Registry','Registry.java',[[1,66]])]:old(id,s/n,rs,version,'../batch-06/selected-source-acquisition.json')
old('Main',B/'reference-assets/aw_vehicles/src/main/java/Vehicles/Main.java',[[1,50]],version,'acquisition.json')
# Main has50 actual lines; never label a longer synthetic range as a full read.
registry[-1]['reviewed_ranges']=[[1,registry[-1]['lines']]]
old('ServerEntity',R/'batch-09/native/forge-47.3.0/reading_view/net/minecraft/server/level/ServerEntity.java',[[35,211],[227,316]],'forge-47.3.0','../batch-09/native-source-manifest.json')
sh=json.loads((B/'shader-provenance.json').read_text())
for f in sh['files']:
 p=B/f['local'];f['reviewed_ranges']=[[1,len(p.read_text().splitlines())]];f['read_status']='FULL_TEXT_READ';old(Path(f['entry']).name,p,f['reviewed_ranges'],'official Minecraft1.20.1 shader text','shader-provenance.json')
sh['review_updated_utc']=now;save('shader-provenance.json',sh)
e=[]
def add(id,title,claim,support,limit='静态选读；未执行渲染、网络或游戏。'):
 e.append(dict(id=id,title=title,claim=claim,support=[dict(source=s,ranges=rs) for s,rs in support],qualification=limit,independent_reference_credit=0))
add('R01','固定注册与资源','Main事件注册明确绑定BallistaRenderer与BallistaBoltRenderer；modid为aw_vehicles。Renderer分别请求ballista_stand_3.png和arrow_wood.png，不是依据名字猜测纹理。',[('Main',[[18,38]]),('Registry',[[30,45]]),('BallistaRenderer',[[24,33],[146,149]]),('BallistaBoltRenderer',[[22,30],[64,67]])])
add('R02','状态字段与传输','DRAW_PROGRESS、CONSTRUCTION_PROGRESS、IS_BROKEN及箭VELOCITY是SynchedEntityData；set检测变化后标dirty，ServerEntity.packDirty通过SetEntityData包发送，客户端按实体IDassignValues。该链不是几何JSON，也没有保存owner普通引用。',[('Ballista',[[29,31],[54,61],[299,304]]),('BallistaBolt',[[27,51],[150,156]]),('SynchedEntityData',[[119,164],[185,209]]),('ServerEntity',[[113,125],[175,179],[290,307]]),('ClientboundSetEntityDataPacket',[[1,43]]),('ClientPacketListener',[[498,505]])])
add('R03','初次跟踪与晚到边界','ServerEntity维护非默认状态，出生包后可发非默认字段包；持续dirty传输不是每帧所有字段全量同步。客户端找不到包中实体ID时直接跳过该次赋值，真实网络/资源重载顺序尚未运行。',[('SynchedEntityData',[[142,209]]),('ServerEntity',[[64,75],[227,259],[290,296]]),('ClientPacketListener',[[498,505]])])
add('R04','射击后坐力是显示计算','器械客户端在draw<=0时递增clien_ticksAfterShoot，draw>0时归零。Renderer据此做阻尼三角函数后坐力与弦臂角；不是独立服务端射击事件。初始draw==0也满足计数条件，不能把所有可见震动都当真实开火凭证。',[('Ballista',[[144,182]]),('BallistaRenderer',[[35,82]])])
add('R05','两种不同时间采样','拉弦使用prev+(current-prev)*partialTick；瞄准角使用current+(current-last)*partialTick，并由客户端tick先做0.3平滑。后者相对last→current属于向前外推；这只是公式差异，不足以宣称实际卡顿或错误。',[('Ballista',[[144,182]]),('BallistaRenderer',[[38,39],[69,74]]),('BallistaBoltRenderer',[[43,51]])])
add('R06','施工与损坏必须每次绘制驱动','施工阈值0–17决定部件可见性；损坏分支覆盖弓臂/绳索姿态，正常分支重设所改的关键偏移旋转，而不是仅换贴图。共享ModelPart并不自动证明串状态；需要核对每个被改字段的正常路径。',[('BallistaRenderer',[[89,141]]),('ModelPart',[[56,70],[109,129]])])
add('R07','逐顶点UV而非平均面色','ModelPart保存Cuboid六面UV，Polygon用纹理宽高归一化；compile逐顶点输出UV、RGBA、光照与法线。简版render重载传入RGBA=1，当前Renderer没有额外角色色乘数。不能用面平均色预览代替实际PNG采样。',[('ModelPart',[[109,129],[212,329]]),('VertexConsumer',[[17,59]]),('BallistaRenderer',[[138,142]]),('BallistaBoltRenderer',[[53,55]])])
add('R08','UV尺寸与像素密度不是一回事','LayerDefinition/PartDefinition把声明宽高传给CubeDefinition与ModelPart。原图与声明均匹配：256×256、192×36。器械模型16单位对应1格；箭还有0.2缩放，80单位轴干约1格，说明不能单看图集大小判断世界像素密度。',[('LayerDefinition',[[1,24]]),('PartDefinition',[[35,47]]),('CubeDefinition',[[23,36]]),('ModelPart',[[153,160],[279,294]]),('BallistaBoltRenderer',[[39,41],[81,85],[225,225]])])
add('R09','原色仍会受游戏光照影响','ModelPart的原色乘数为1不等于最终屏幕颜色不变。entitySolid的vsh读取法线灯光/lightmap/overlay，fsh采样PNG后再乘ColorModulator并施加雾；Renderer也传packedLight。因此离线原色与普通游戏光照应分别验。',[('EntityRenderer',[[33,43]]),('rendertype_entity_solid.vsh',[[31,40]]),('rendertype_entity_solid.fsh',[[21,26]]),('BallistaRenderer',[[138,142]])])
add('R10','采样过滤与资源来源','entitySolid指定TextureStateShard(texture,false,false)，该状态设置纹理过滤并绑定Sampler0；AbstractTexture在两标志false时选9728最近邻。SimpleTexture从ResourceManager按ResourceLocation读取、加载失败由TextureManager进入缺失纹理后备。当前运行资源包优先级未验证。',[('RenderType',[[39,42],[192,194]]),('RenderStateShard',[[512,536]]),('AbstractTexture',[[20,37]]),('SimpleTexture',[[28,59],[83,104]]),('TextureManager',[[94,123]])])
add('R11','透明RGB不能单独诊断','两张原图大片RGB品红像素的alpha为0。只读UV展开69个Cuboid边界均在图集内；器械没有六面全透明采样，箭headPoint小方块六面采样全透明。entitySolid.fsh没有discard，而cutout.fsh有alpha<0.1丢弃。是否实际可见还涉及完整混合/深度状态，不能仅凭PNG alpha保证隐藏，也不能把整个图集判成缺失纹理。',[('BallistaBoltRenderer',[[73,79]]),('RenderType',[[39,45]]),('rendertype_entity_solid.fsh',[[1,26]]),('rendertype_entity_cutout.fsh',[[21,30]]),('rendertype_entity_solid.json',[[1,8]])],'原图实际视觉查看与atlas-check.json的像素中心分析；不是GPU输出，也未验证ShaderInstance混合状态。')
add('R12','显示位移与实体碰撞不同','箭Renderer在0.2缩放之后再加dx/dy/dz*partialTick局部平移；Dispatcher已先平移到其接收的实体绘制位置。不能由局部几何长度推断服务器命中范围，是否叠加多重插值需继续核对上游位置采样。',[('BallistaBoltRenderer',[[34,55]]),('BallistaBolt',[[69,76],[154,181]]),('EntityRenderDispatcher',[[125,170]]),('PoseStack',[[21,51]])])
add('R13','渲染包围盒不能从模型自动推定','注册器械碰撞1×2，箭0.25×0.25；EntityRenderer按实体culling AABB加0.5视锥检查，不按每个模型零件自动重算。较长箭/外扩弓臂在视野边缘的实际裁切仍需运行验证，未扩大任何碰撞。',[('Registry',[[30,37]]),('EntityRenderer',[[46,59]]),('BallistaBoltRenderer',[[39,41],[81,85]])])
add('R14','资源重载重新构造映射','Dispatcher按非玩家实体type取renderer，资源重载时重新createEntityRenderers并post AddLayers；不是每次draw都bake模型。已读代码不能证明当前整合包没有其他注册覆盖或资源包替换。',[('EntityRenderDispatcher',[[92,100],[358,363]]),('BallistaRenderer',[[24,33]]),('BallistaBoltRenderer',[[27,30]])])
limits=['本批仅Ballista既有家族的渲染/同步消费者，0新增家族/信用；不计69Cuboid、17原生类、两张贴图、14条证据为参考数量。','PNG为原作者固定提交的参考资产，仅研究目录持有，未复制至Dynasty生产资源。机械器械不是生物参考，不抵逐生物100个模型+PNG。','实际Forge客户端注册/覆盖、ShaderInstance混合与深度状态、资源包优先级、多人同步顺序、视锥边缘及完整动作未运行。','Arrow headPoint透明面、current+diff外推及idle draw0的后坐计数均是源码/图集边界，尚未复现视觉故障。','已认可资源、共享生产Jar、存档、用户实例保持不碰；无Java/游戏/声音/焦点/唤醒/发布。','GitHub网页工具本次cache miss；原始资产使用系统curl正常TLS并按同固定提交完整树Git blob校验；未将网页失败冒称已看网页。']
save('render-sync-review.json',dict(updated_utc=now,status='STATIC_REVIEW_READY_FOR_INDEPENDENT_REVIEW',source_registry=registry,evidence=e,atlas_check='atlas-check.json',shader_provenance='shader-provenance.json',limitations=limits,new_source_families=0,new_accepted_gate_credit=0,global_accepted_total=None))
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>弩炮显示链补读</title><style>body{font:16px/1.7 system-ui;background:#14202d;color:#e7edf5;max-width:1100px;margin:40px auto;padding:24px}a{color:#a4d8f4}article{padding:18px;background:#1c2d3c;border-radius:12px;margin:16px 0}.atlas{image-rendering:pixelated;background:repeating-conic-gradient(#777 0 25%,#bbb 0 50%) 0/16px 16px;border:8px solid #364b5f;max-width:100%;object-fit:contain}small{color:#c7d1db}</style><h1>弩炮：真实PNG、逐面UV与客户端显示链</h1><p>固定提交只读研究；不是Dynasty模型成果，也不是游戏截图。0新增家族/验收信用。</p><p><a href="render-sync-review.json">证据</a> · <a href="acquisition.json">来源与阅读范围</a> · <a href="atlas-check.json">只读UV检查</a> · <a href="shader-provenance.json">官方着色器来源</a> · <a href="local-verification.json">文件校验</a> · <a href="../batch-09/index.html">前批归属链</a></p><h2>实际看过的原图：棋盘仅用于显示透明区域</h2>']
for a in m['assets']:
 if a['path'].endswith('.png'):
  parts.append('<p>'+html.escape(Path(a['path']).name)+'</p><img class="atlas" src="'+a['local']+'" width="768" alt="原作者PNG参考，不是自产贴图"><p><small><a href="'+html.escape(a['url'],quote=True)+'">固定提交原图</a> · 原作者资产仅研究，未复制生产。</small></p>')
for x in e:
 links=[]
 for ref in x['support']:
  src=next(s for s in registry if s['id']==ref['source']);links.append('<a href="'+html.escape(src['local'],quote=True)+'">'+html.escape(src['id'])+'</a> '+html.escape(str(ref['ranges'])))
 parts.append('<article><b>'+x['id']+' '+x['title']+'</b><p>'+x['claim']+'</p><small>'+'；'.join(links)+'</small></article>')
parts.append('<h2>未完成边界</h2><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in limits)+'</ul></html>');(B/'index.html').write_text('\n'.join(parts)+'\n')
p=json.loads((B/'progress.json').read_text());p.update(updated_utc=now,status='BOUNDED_RENDER_SUBRANGE_READY_CONTINUING_NEXT_BATCH',existing_family_context_extensions=1,reviewed_evidence_records=len(e),actual_png_viewed=2,atlas_declared_size_mismatches=0,remaining=limits,report='index.html');save('progress.json',p)
root=json.loads((R/'progress.json').read_text());oldbatch=root.get('this_batch',{})
if oldbatch.get('id')!='batch-10' and not any(x.get('id')==oldbatch.get('id') for x in root.get('previous_batches',[])):root.setdefault('previous_batches',[]).append(dict(oldbatch,report=oldbatch['id']+'/index.html'))
root.update(updated_utc=now,status='ACTIVE_SEQUENTIAL_RESEARCH_WITH_SAVED_RECEIPTS',latest_batch='batch-10',this_batch=dict(id='batch-10',source_studies=0,existing_family_context_extensions=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='Ballista渲染/同步补读和真实PNG，仍为同一家族；不是生物视觉参考。'))
root['continuation_window'].update(status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH',last_saved_utc=now,report='batch-10/index.html',full_three_hours_claimed=False)
root['next']=['接续未读的原范围真实链或所有权/恢复/实际渲染消费者；不以小批完成自动停止。','先补原生Shader混合/位置上游或其他已登记家族关键断点；新链须固定源并全局语义去重。','记录当前资产只读问题与真实任务物品ID映射，不修改主协调待办/研究主账。','独立验收与实机仍待；不以本地18/14证据条数或源码文件抵1000参考。','逐生物100个相近模型+贴图门槛及认可资源边界不变。']
(R/'progress.json').write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(evidence=len(e),native_sources=len(m['files']),png_viewed=2,new_credit=0,continue_until='2026-10-31T12:09:23+08:00')))
