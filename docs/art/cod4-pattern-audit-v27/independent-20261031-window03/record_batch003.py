from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;A=D.parent;sys.path.insert(0,str(A));import record_source_methods as M
specs=[
('bernie-g/geckolib','Forge/src/main/java/software/bernie/geckolib/renderer/DyeableGeoArmorRenderer.java','renderCubesOfBone','完整读取本类。isBoneDyeable/getColorForBone均为抽象钩子；renderCubesOfBone仅对缓存骨骼乘RGBA再调用父renderer，checkBoneDyeCache只在model对象改变时清理并递归收集。没有缓存实际子类消费者证明当前物品材质身份与选骨关联，且未产生新的UV变换。当前作为选择性tint封装排除，不把public API或缓存存在当完整实际盔甲实例；不能推论逐物品缓存安全，isBoneDyeable如果依赖当前栈需手动失效。getColorForBone在每次画骨骼时调用，颜色本身不在该集合缓存中。',[('preRender',0),('checkBoneDyeCache',0),('collectDyeableBones',0)]),
('lender544/new1.20.1','src/main/java/com/github/L_Ender/cataclysm/client/render/blockentity/RendererAltar_of_Fire.java','renderSigil','完整读取本类。summoningthis门控后用summoningticks clamp0..25等比长大单张静态sigil，再绕Y旋转；四顶点UV固定0..1，alpha恒255，发光类型和0.001高度不带贴面身份/逐面映射/历史快照。属于已审普通平面缩放旋转同类，且实际是祭坛视觉，不为皇权贴面增加计数。render确实调用renderSigil，并非死代码。drawVertex法线形参被重排：调用实参(1,0,1)最终写成normal(1,1,0)，不是单位上法线，不能把此模板直接当可靠范例。renderFlamePart取(int)((f2*.5)%7)，只索引0..6，不因声明8张图称8帧已实际使用。只读实现，未改祭坛或参考美术。',[('render',0),('drawVertex',0),('renderFlamePart',0),('getIdleTexture',0),('renderQuad',0),('vertex',0)]),
('AlexModGuy/Ice_and_Fire','src/main/java/com/github/alexthe666/iceandfire/client/render/entity/layer/LayerDragonBanner.java','render','完整读取本类。仅把OFF_HAND BannerItem挂到BodyUpper局部变换，再按renderSize反比缩放并调用原版ItemRenderer.renderStatic(NONE)；没有独立banner纹样解析/UV烘焙/合成，属于已审挂点调用包装，不增加imperial_decal或equipment_uv计数。BodyUpper.findFirst().get()无缺骨保护，renderSize/3为0时倒数不安全；postRender不递归父链，不能声称任意深层骨骼适配。无旋转分支条件第三项查offsetZ，但实际translate用rotationPointZ，两者不等价，可能漏掉纯rotationPointZ位移。只记录限制，不改代码。',[('postRender',0)]),
('AlexModGuy/Ice_and_Fire','src/main/java/com/github/alexthe666/iceandfire/client/render/entity/RenderStoneStatue.java','render','完整读取本类及IafRenderType相关方法。主体拿trapped entity renderer的原模型换stone纹理，裂纹阶段再用同几何和EQUAL_DEPTH_TEST重绘；getStoneMobRenderType的x/y参数未用于任何UV，未见UV坐标重建，不因getStoneMobRenderType(200,200)称图集200x200。与已接纳Vampirism独立几何投影裂纹不同，此处无新UV算法，且石像实体不属本次皇权/学校物品独立实现，排除。缓存按type字符串而非每实例NBT，hollowEntityMap.putIfAbsent返回旧值，首次写入时fakeEntity仍null；后续同类型沿用最早NBT，不能声称冻结每个石像真实姿态。两次绘制的自定义renderStatue路径fakeEntity判空条件不一致，不能据源码认定所有模型安全。',[('preRenderCallback',0)])]
rows=[]
for repo,p,n,note,ctx in specs:
 r=M.record(repo,p,n,0,'EXCLUDED',note);r['reviewMode']='READ_SOURCE_EXCLUDED_NO_COUNT';r['countsTowardReferenceGate']=False;r['callContext']=[]
 for name,i in ctx:
  c=M.record(repo,p,name,i,'CONTEXT_ONLY_NO_COUNT','完整读取，仅排除判定上下文，零计数。');c['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';r['callContext'].append(c)
 if n=='render' and 'RenderStoneStatue' in p:
  for name in ['getStoneMobRenderType','getStoneCrackRenderType']:
   c=M.record(repo,'src/main/java/com/github/alexthe666/iceandfire/client/render/IafRenderType.java',name,0,'CONTEXT_ONLY_NO_COUNT','完整读取实际纹理/深度状态方法；没有传入尺寸的UV消费。');c['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';r['callContext'].append(c)
 rows.append(r)
b={'reviewed':0,'rows':[],'excluded':rows,'parentReview':{'status':'LOCAL_ONLY_NO_NETWORK_AFTER403','newImplementations':0,'newExclusions':4,'mainLedgerUpdated':False,'productionChanges':False,'policy':'Complete unstudied local candidates, do not count abstract/missing consumers or helper wrappers; no API retry.'}}
(D/'batch-003.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');print('Recorded batch003: zero new, four exclusions')
