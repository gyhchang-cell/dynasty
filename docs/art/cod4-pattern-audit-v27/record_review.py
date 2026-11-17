"""Record only manually read source implementations; fetched files are not automatically reviews."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[2]
review={
 'BoltRenderer.java':(54,153,'雷符杖/北辰枪','独立发射器持有有限寿命闪电；按世界刻与partial刷新，顶点颜色不依赖贴图。雷纹的时序须独立于帧率，不能靠换一张图冒充完整雷击表现。'),
 'BloodSlashRenderer.java':(44,100,'流云剑/承影剑','两张错开旋转的斩击面；八帧原版横扫纹理、按时间选帧。可借鉴交错层与方向识别，不采用其每次render递增动画时间的做法，以免帧率影响寿命。'),
 'MagicSwordRenderer.java':(28,42,'流云剑/承影剑','剑体先移到实体半高，再插值偏航/俯仰，使用独立magic渲染类型。专属纹样要与真实剑体朝向一致，不能做面向摄像机的固定图标。'),
 'LightningLanceRenderer.java':(28,75,'北辰枪/雷符杖','按运动矢量求俯仰偏航；七格横向动画UV，两个交叉平面增强侧面可见性。借鉴长柄纵轴和正侧可读性，不能把交叉面数或七帧重复算七个实现。'),
 'ShieldRenderer.java':(40,77,'两把帝王剑护体','实体朝向决定盾方向，主体和trim分层，按tick加partial产生独立UV偏移。护体主体应保持轮廓，纹样用单独层控制；不把声明但未使用的SIGIL_TEXTURE当已生效纹样。'),
 'EnderSlashParticle.java':(22,139,'镇岳刀/流云剑/承影剑','5刻寿命；forward与up叉积建立局部顶点，正反面均提交；首刻生成余烬而非每帧重复生成。纹样必须跟随攻击平面，正反皆可读且按寿命清除。'),
 'RenderDrive.java':(71,125,'镇岳刀/北辰枪','无纹理色顶点刀气按yaw/pitch/roll朝向，alpha按剩余寿命平方衰减，退出恢复纹理/光照状态。旧版OpenGL实现仅作表现结构参考，不移植接口或顶点。'),
 'RenderPhantomSwordBase.java':(78,152,'学院近战残影','三角剑形通过实体旋转插值定位，跨±180度做角度归一。可借鉴旋转连续性；旧版接口不可直接用于Forge1.20.1，不把通用变换重复算不同武器研究。'),
 'RenderSlashDimension.java':(55,173,'承影剑/逐星弓/风翎弓','按寿命衰减，主体层与多个错时扩散层分离，seed参与次层运动；矩阵/混合状态有成对恢复。借鉴短促层次和稳定种子，拒绝照搬模型、贴图或密集发光面。'),
}
rows=[];excluded=[]
for r in json.loads((D/'fetched.json').read_text()):
 name=Path(r['path']).name
 if name not in review:
  excluded.append({**r,'reason':'仅为粒子工厂转发，没有实际纹理表现实现' if 'ParticleType' in name else '与MagicSwordRenderer共享居中/magic渲染结构，不重复计数'})
  continue
 lo,hi,target,observation=review[name]
 rows.append({**r,'lineStart':lo,'lineEnd':hi,'source':r['url']+f'#L{lo}-L{hi}','dedupKey':r['repo']+'@'+r['commit']+':'+r['path'],'targets':target,'observation':observation,'review':'READ_SOURCE_ONLY; not game visual acceptance'})
assert len(rows)==len({r['dedupKey'] for r in rows})==9
(D/'reference-ledger.json').write_text(json.dumps({'requiredPerTask':1000,'reviewedDistinctImplementations':len(rows),'remainingAtLeast':1000-len(rows),'unit':'one distinct related implementation, not line/vertex/frame/project count','rows':rows,'excluded':excluded,'newProductionAllowed':False,'reason':'各目标尚未达到1000处；本批只做只读核查和研究'},ensure_ascii=False,indent=2)+'\n')
paths=['src/main/java/com/dynasty/ImperialWeaponEffects.java','src/main/java/com/dynasty/client/ImperialWeaponRenderer.java','src/main/java/com/dynasty/client/ImperialWeaponGeometry.java','src/main/java/com/dynasty/client/DragonDecalRenderer.java','src/main/java/com/dynasty/cod3/DragonDecal.java','src/main/java/com/dynasty/cod3/EquipmentFeedback.java','src/main/java/com/dynasty/client/Cod3AfterImages.java','src/main/java/com/dynasty/client/Cod3VfxRenderer.java','src/main/java/com/dynasty/expansion/EffectPresentation.java','src/main/resources/assets/dynasty/textures/effect/dragon_slayer_decal.png']
snapshot={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
(D/'inspected-source-hashes.json').write_text(json.dumps(snapshot,indent=2)+'\n')
print('Recorded 9 distinct reviewed implementations; 3 fetched files excluded; production gate remains closed')
