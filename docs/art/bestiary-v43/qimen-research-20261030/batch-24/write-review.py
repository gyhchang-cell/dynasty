from pathlib import Path
import json,hashlib,datetime,html
B=Path(__file__).resolve().parent;m=json.loads((B/'selected-source-manifest.json').read_text());e=[]
def ref(name,lo,hi):
 x=next(x for x in m['files'] if Path(x['path']).name==name);assert any(u<=lo<=hi<=v for u,v in x['ranges']);return dict(local=x['local'],sha256=x['sha256'],range=[lo,hi],artifact='software.bernie.geckolib:geckolib-fabric-1.19:3.1.6:sources')
def add(id,title,fact,limit,*rs):e.append(dict(id=id,title=title,fact=fact,limit=limit,sources=[ref(*r) for r in rs],credit_added=0))
add('G01','精确发布依赖而非浮动分支','已取得 Ballista build.gradle 指定的 Fabric1.19 Gecko3.1.6 sources，发布SHA1与本地4600785f88b0cebef137d5e6dbdf4eb32c03e35c一致。POM声明geckolib-core1.0.14。','1.19当前分支6b17247不是已证明3.1.6的源码，不拿它代替。')
add('G02','动画先走super，再写模型观察角','AnimatedGeoModel.setLivingAnimations调用preAnimationSetup/tickAnimation；Ballista覆写先super，再把head.rotationY、bow.rotationX和base Y/Z写定。','只能闭合这些分量的调用先后，core控制器优先级/STOP仍未读，不能宣称所有组件重复旋转。',('AnimatedGeoModel.java',47,77))
add('G03','坐标转换必须进入预览边界','GeoBuilder对原rotation乘(-1,-1,1)，转弧度，pivotX取负。GeoCube originX=-(originX+sizeX)/16，其余轴按16缩放；cube pivotX也取负。','batch23标准坐标技术图仅近似，未验证原生PoseStack实现，不把它当游戏姿态。',('GeoBuilder.java',41,76),('GeoCube.java',23,65))
add('G04','小数几何不等于小数UV','GeoCube boxUV使用floor(sizeX/Y/Z)；原实际顶点仍按完整size建立。43个cube里10个含小数尺寸、8个有floor后为0的纹理轴。','只说明UV区间退化，实际过滤/纹理像素结果需GPU；不声称几何消失。',('GeoCube.java',96,112),('GeoCube.java',157,190))
add('G05','mirror并非简单整体倒图','GeoQuad按cube mirror改变顶点UV方向；GeoCube在cube或bone mirror时重建东西面，但GeoQuad接受的仍是cube mirror。','bone/cube mirror与面位交换要分别理解；不以一次水平翻图当精确原生消费。',('GeoQuad.java',11,55),('GeoCube.java',149,190))
add('G06','真实递归与材质消费','递归骨骼 translate→pivot→Rz/Ry/Rx→scale→back pivot，子骨继承矩阵；默认renderColor白色，packedlight交给顶点。','基础漫反射是离线检查手段；无游戏光照/阴影验收。',('IGeoRenderer.java',40,100),('IGeoRenderer.java',118,126),('RenderUtils.java',20,48))
add('G07','renderer实际回调顺序','GeoEntityRenderer在取model后调用setLivingAnimations，再取renderColor与renderType绘制；EntityModelData传入负headPitch/netHeadYaw。','所选intermediary源码与具体映射有界；不以1.20消费者替换1.19。',('GeoEntityRenderer.java',130,181))
add('G08','core读取断点明确保留','精确geckolib-core1.0.14 sources URL返回404，未重试；因此Controller PlayState.STOP、markNeedsReload和多Controller写入顺序未闭合。','下载了外围sources不等于读完core，也不等于动画运行已验证。')
j=dict(scope='existing Defensive Measures ballista exact dependency consumers',artifact='software.bernie.geckolib:geckolib-fabric-1.19:3.1.6:sources',sources=m['files'],evidence=e,new_source_studies=0,existing_family_extensions=1,accepted_credit=0,creature_reference_credit=0,production_changed=False,java_game_started=False,core_sources_unavailable=m['unavailable'],next_breakpoint='obtain verifiable geckolib-core1.0.14 source identity, then Controller STOP/reload/order; do not replace with current1.19 branch')
(B/'dependency-consumers.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
css='body{max-width:1060px;margin:32px auto;background:#19262c;color:#dce7e7;font:16px/1.65 system-ui}a{color:#9ed4d1}article{border-top:1px solid #49606a;padding:16px 0}small{color:#aabfc5}'
p=[f'<!doctype html><meta charset="utf-8"><title>Gecko3.1.6 exact consumers</title><style>{css}</style><h1>弩炮：精确 GeckoLib 3.1.6 几何与调用消费者</h1><p>补读既有家族，新增参考验收0。只读发布源码；未启动Java/游戏、未改生产模型。</p><p><a href="dependency-consumers.json">8项证据与断点</a> · <a href="fractional-box-uv-diagnostic.json">10个小数Cuboid的UV检查</a> · <a href="selected-source-manifest.json">来源/发布SHA1/阅读范围</a> · <a href="local-verification.json">局部校验</a> · <a href="../batch-23/index.html">模型PNG和近似动作图</a></p>']
for x in e:p.append('<article><b>'+html.escape(x['title'])+'</b><p>'+html.escape(x['fact'])+'</p><small>'+html.escape(x['limit'])+'</small></article>')
p.append('<p>本轮并未完成Controller完整回放校验。源码下载404与未关闭消费者都留在记录，不以技术图冒充实机。</p>');(B/'index.html').write_text('\n'.join(p))
# Preserve previous render output, add explicit known-gap notice instead of pretending it matched this loader.
p=B.parent/'batch-23/geometry-inspection.json';g=json.loads(p.read_text());note='Exact Gecko3.1.6 GeoCube floors box UV extents and flips X/XY rotation conventions; these earlier standard-box numerical diagrams are approximate, not loader parity.'
if note not in g['limits']:g['limits'].append(note)
p.write_text(json.dumps(g,indent=2)+'\n');p=B.parent/'batch-23/index.html';s=p.read_text();note='<p>后续核对：<a href="../batch-24/index.html">精确Gecko3.1.6消费者</a>发现box UV取整、镜像与轴转换规则；以上软件图仅近似，不是加载器一致性或实机证明。</p>'
if note not in s:p.write_text(s+'\n'+note)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();pj=dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',report='index.html',new_source_studies=0,accepted_credit=0,next=j['next_breakpoint']);(B/'progress.json').write_text(json.dumps(pj,ensure_ascii=False,indent=2)+'\n')
rp=B.parent/'progress.json';p=json.loads(rp.read_text())
if p['latest_batch']!='batch-24':
 old=p['this_batch'];old['report']=p['latest_batch']+'/index.html';p['previous_batches'].append(old)
p['latest_batch']='batch-24';p['this_batch']=dict(id='batch-24',source_studies=0,existing_family_context_extensions=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='Gecko3.1.6同家族精确依赖消费者；core1.0.14 sources404保持未闭合。');p['updated_utc']=now;p['continuation_window'].update(progress='batch-24/progress.json',report='batch-24/index.html',last_saved_utc=now);rp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');print('saved',len(e),'findings')
