from pathlib import Path
import json,hashlib,datetime,html
B=Path(__file__).resolve().parent; S=B.parent/'batch-21/sources/myriantics__klaxon'; E=B/'sources/myriantics__klaxon'
commit='7d31931c1c94dc3d3e4209c6897bc77aad8c8432'
names=['GrappleClawEntityRenderer.java','KlaxonItemModelPredicates.java','KlaxonEntityRenderers.java','KlaxonClient.java','ClientGrappleWinchConnection.java','ClientGrappleWinchConnectionManager.java','GrappleWinchCableRenderer.java','KlaxonTextures.java','KlaxonItemModelPredicateIds.java','ItemRendererMixin.java','ModelBakeryMixin.java','ModelUtils.java','AdvancedItemModelHelper.java','BlockModelAccessor.java','ItemOverrideAccessor.java','MinecraftMixin.java','LocalPlayerMixin.java','MinecraftClientUsageLockoutAccess.java','ItemUsageLockoutTrigger.java','KlaxonClientPlayNetworkHandler.java','GrappleWinchConnectionSyncPacket.java','GrappleWinchConnectionDiscardPacket.java','KlaxonClientPackets.java','ClientLevelMixin.java','LevelRendererMixin.java','MultiPlayerGameModeMixin.java']
paths=[]
for name in names:
 a=list(E.rglob(name))+list(S.rglob(name))
 if name in ['MinecraftMixin.java','LocalPlayerMixin.java']:a=[p for p in a if 'item_usage_lockout' in str(p)]
 if name=='ItemRendererMixin.java':a=[p for p in a if 'advanced_item_models' in str(p)]
 assert len(a)==1,(name,a)
 paths+=a
sources=[]
for i,p in enumerate(paths,1):
 n=len(p.read_text().splitlines()); root=E if p.is_relative_to(E) else S
 sources.append(dict(id='S'+str(i),path=str(p.relative_to(root)),local=str(p.relative_to(B,walk_up=True)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),ranges=[[1,n]],status='FULL_SELECTED_FILE_READ',url=f'https://github.com/myriantics/klaxon/blob/{commit}/'+str(p.relative_to(root))))
lookup={Path(x['path']).name:x['id'] for x in sources}
def refs(*ns):return [lookup[n] for n in ns]
F=[]
def add(id,title,fact,limit,*ns):F.append(dict(id=id,title=title,fact=fact,limit=limit,sources=refs(*ns),credit_added=0))
add('R01','实体爪体与手持卷扬器分开','实体 renderer 使用 32×32 钢爪 PNG，2对反面+4旋转爪面共8quads；手持另走物品 JSON。item registry path 拼入 Klaxon 目录，不保留外部命名空间。','不是 Gecko 生物或通用跨模组自动纹理机制；无游戏画面。','GrappleClawEntityRenderer.java','KlaxonTextures.java','KlaxonEntityRenderers.java')
add('R02','实际替换上下文','ALT_HAND_MODEL 对 GUI/FIXED/GROUND 之外上下文启用，alternate 模型再解析自己的 overrides；左手可选 mirrored。','不能说仅第一人称；未模拟 Minecraft 烘焙与手臂矩阵。','ItemRendererMixin.java','AdvancedItemModelHelper.java','ModelBakeryMixin.java')
add('R03','镜像有具体边界','ModelUtils 围绕 X=8 反转 from/to、换东西面UV、反转Y/Z角；rotation origin 和 display transforms 保持。','非中心 origin 的一般情况不可直接保证；本轮不修改作者资源、不宣称运行出错。','ModelUtils.java','BlockModelAccessor.java','ItemOverrideAccessor.java')
add('R04','状态谓词按玩家连接','cable_length 为已有连接 cable/max；charged 看 charged projectiles；retracting 看玩家连接状态。未连接缺省0。','未绑定原始发射 stack，不能称逐 stack 独立状态。','KlaxonItemModelPredicates.java','KlaxonItemModelPredicateIds.java','KlaxonClient.java')
add('R05','客户端真实接收链','S2C 注册→client.execute→新建或sync连接→重置manager更新计数；discard按connectionID排队。fallback positions经VECTOR3F编码再转Vec3。','double坐标记录不等于网络保留双精度；未闭合1.21原生codec/merged Mixin。','KlaxonClientPackets.java','KlaxonClientPlayNetworkHandler.java','GrappleWinchConnectionSyncPacket.java','GrappleWinchConnectionDiscardPacket.java')
add('R06','长度同步会发送C2S','客户端 override setCableLength 无条件发 C2S；构造与远端sync也会调用。sync先按旧max处理长度再更新max；本地有连接时可保留预测长度。','服务端按sender当前连接处理，不能推定为跨玩家控制或已复现网络漏洞。','ClientGrappleWinchConnection.java')
add('R07','名称与位置基准不同','loaded getPlayerEyePos 返回player.position；丢实体时fallback来自服务器eye。画线getHandPos另取眼高/手部矩阵。','这是所选源码的基准差异，不是实测位移；不以1.20原生代码冒充1.21。','ClientGrappleWinchConnection.java','GrappleWinchCableRenderer.java')
add('R08','逐段缆线而非长条拉伸','实际循环每整格一段、末尾按余长；3/16格宽，两交叉cutout面，U按段余长，V0..3/16。代码注释2段每格与循环不一致。','同一绳索家族；不是实体链环，也不新增参考。','GrappleWinchCableRenderer.java')
add('R09','短缆与整数末段边界','distance<1 时maxSegments=0，segmentIndex/maxSegments为float0/0；整数距离会多绘制长度0末段。','记录算术边界，不宣称GPU画面/崩溃；没有游戏执行。','GrappleWinchCableRenderer.java')
add('R10','普通光照消费','两端block/sky光插值；午夜daylight multiplier=0，夜视最低13，燃烧/发光端block15，白色顶点与传入packedlight。','这不是发光PNG材质，软件基础漫反射不等同游戏光照。','GrappleWinchCableRenderer.java','ClientGrappleWinchConnectionManager.java')
add('R11','管理器与绘制注入','ClientLevel.tick TAIL tickmanager；renderLevel在endLastBatch前调用manager.render；客户端disconnect会调用hook onDisconnect。','与服务端断连实现不同；仅检查源码配置入口，未验证混入后的字节码。','ClientLevelMixin.java','LevelRendererMixin.java','ClientGrappleWinchConnectionManager.java')
add('R12','停止使用的后续输入锁','S2C lockout 在client线程设flag并stopUsingItem；Minecraft startUseItem/LocalPlayer isUsingItem包装阻断，按键路径特定ordinal重新放行。','MultiPlayerGameMode目标method_41929仍须相同版本运行校验，不因源码存在就判定注入成功。','KlaxonClientPlayNetworkHandler.java','MinecraftMixin.java','LocalPlayerMixin.java','MultiPlayerGameModeMixin.java','ItemUsageLockoutTrigger.java')
assets=json.loads((B/'asset-inspection.json').read_text())
viewed=['actual-pngs-integer-zoom.png','full-loaded-software.png','full-unloaded-software.png','empty-loaded-software.png','full-retracting-software.png','uv-structure.png','uv-spool.png','uv-steel_grapple_claw.png']
visual=dict(original_png_count=10,actually_viewed=viewed,observations=['钢壳冷灰紫阶、握柄近黑、卷轴古金形成部件主次；没有随机满面噪点。','loaded/unloaded 通过#3实际钢爪/透明PNG切换，14元素几何仍在；不是新模型案例。','spool6满卷与spool0空卷改变线圈体量；空卷露出金轴。','第一次软件图 coplanar 深度比较产生噪点；加比较epsilon后消失，原PNG未变。','spool_retracting 32×64 两帧，每帧3tick；软件图仅首帧。','原始资源属于作者，仅保留研究副本；不进入 Dynasty 生产资源。'],limits=assets['limitations'])
(B/'render-client-study.json').write_text(json.dumps(dict(repo='myriantics/klaxon',commit=commit,version='1.21.1 Fabric / 1.0.0b1; NOT Forge1.20.1 compatible',scope='same-family render/client closure',sources=sources,evidence=F,visual=visual,new_source_studies=0,existing_family_extensions=1,accepted_credit=0,creature_reference_credit=0,production_changed=False,java_game_started=False),ensure_ascii=False,indent=2)+'\n')
a=json.loads((B/'consumer-acquisition.json').read_text())
for x in a['files']:
 if x['path'].endswith('.java'):
  p=B/x['local'];x['read_ranges']=[[1,len(p.read_text().splitlines())]];x['status']='FULL_SELECTED_FILE_READ'
 else:x['status']='VIEWED_IN_ACTUAL_PNG_CONTACT_SHEET';x['view']='actual-pngs-integer-zoom.png'
(B/'consumer-acquisition.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
css='body{max-width:1100px;margin:32px auto;background:#152129;color:#dce7e7;font:16px/1.65 system-ui}a{color:#9ed4d1}img{max-width:100%;image-rendering:pixelated}article{border-top:1px solid #49606a;padding:18px 0}small{color:#aabfc5}'
parts=[f'<!doctype html><meta charset="utf-8"><title>KLAXON 实际资源与客户端消费核对</title><style>{css}</style><h1>KLAXON：实际 PNG / JSON / 客户端消费者</h1><p>固定 {commit} · 1.21.1 Fabric 跨版本研究。延伸既有家族，新增验收计数 0。未修改生产资源、未启动 Java 或游戏。</p>', '<p><a href="render-client-study.json">逐项源码证据</a> · <a href="asset-inspection.json">资产检查</a> · <a href="local-verification.json">局部校验</a></p>']
for x in F:parts.append('<article><b>'+html.escape(x['title'])+'</b><p>'+html.escape(x['fact'])+'</p><small>'+html.escape(x['limit'])+'</small></article>')
parts.append('<h2>实际查看的像素图与离线技术预览</h2><p>同尺度、逐面采样真实PNG；不是 Minecraft 截图，不代表游戏烘焙/手持镜像/光照验收。</p>')
for v in viewed:parts.append(f'<p>{html.escape(v)}</p><img loading="lazy" src="{v}" alt="{v}">')
parts.append('<p>可借鉴：状态与图形分开；干净大面、材质定向对比；卷轴余量与动作状态可见。不能把4状态、10 PNG、28 overrides各算独立参考。</p>')
(B/'index.html').write_text('\n'.join(parts))
now=datetime.datetime.now(datetime.timezone.utc).isoformat();pj=dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',report='index.html',new_source_studies=0,existing_family_extensions=1,accepted_credit=0,next='继续真正新的范围链或未读原生/归属消费者；不重复计图帧与同源组件')
(B/'progress.json').write_text(json.dumps(pj,ensure_ascii=False,indent=2)+'\n')
rp=B.parent/'progress.json';p=json.loads(rp.read_text());old=p['this_batch'];old['report']=p['latest_batch']+'/index.html';p['previous_batches'].append(old);p['latest_batch']='batch-22';p['this_batch']=dict(id='batch-22',source_studies=0,existing_family_context_extensions=1,evidence_records=len(F),new_accepted_gate_credit=0,count_note='KLAXON同家族实际PNG/JSON/客户端消费者，0新增参考。');p['updated_utc']=now;p['continuation_window'].update(progress='batch-22/progress.json',report='batch-22/index.html',last_saved_utc=now);rp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');print('saved',len(F),'findings',len(sources),'source reads')
