from pathlib import Path
import json,hashlib,datetime,html,math
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
m=json.loads((B/'acquisition.json').read_text())
nr={'TippableArrowRenderer':[[1,20]],'ArrowRenderer':[[1,73]],'Arrow':[[1,226]],'ArrowItem':[[1,23]],'EntityType':[[303,349],[649,659],[748,772]]}
fr={'NetworkHooks':[[60,105]],'PlayMessages':[[1,200]],'IEntityAdditionalSpawnData':[[1,31]]}
sr={'ISpellCaster':[[1,195]],'SpellCaster':[[1,221]],'Spell':[[1,213]],'SpellContext':[[1,220]],'ModEntities':[[88,130]]}
sources=[]
for group,ranges in [('native',nr),('framework',fr),('mod_sources',sr)]:
 for e in m[group]:
  e['reviewed_ranges']=ranges.get(e['id'],[])
  if e['id']=='spell_crossbow':e['read_status']='ORIGINAL_PNG_AND_12X_NEAREST_VISUALLY_VIEWED'
  else:e['read_status']='REVIEWED_FULL' if e['reviewed_ranges']==[[1,e['lines']]] else 'SELECTED_RANGES_REVIEWED'
  sources.append(dict(id=e['id'],local=e.get('reading_view',e.get('local')),sha256=e.get('reading_view_sha256',e.get('sha256')),ranges=e['reviewed_ranges'],status=e['read_status']))
base=R/'batch-06/sources/baileyholl__Ars-Nouveau';prefix='src/main/java/com/hollingsworth/arsnouveau/'
old=[('ICasterTool','api/item/ICasterTool.java',[[1,105]]),('SpellArrow','common/items/SpellArrow.java',[[1,66]]),('SpellCrossbow','common/items/SpellCrossbow.java',[[1,65],[190,305]]),('EntitySpellArrow','common/entity/EntitySpellArrow.java',[[1,80],[165,193],[267,318]]),('SpellCrossbowRenderer','client/renderer/item/SpellCrossbowRenderer.java',[[1,128]]),('ClientHandler','client/registry/ClientHandler.java',[[58,69],[119,131]])]
for id,p,rg in old:
 f=base/prefix/p;sources.append(dict(id=id,local='../'+str(f.relative_to(R)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),ranges=rg,status='SELECTED_RANGES_REREAD_EXISTING_FAMILY'))
gp=base/'src/main/resources/assets/ars_nouveau/geo/spell_crossbow.geo.json';sources.append(dict(id='crossbow_geo',local='../'+str(gp.relative_to(R)),sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),ranges=[[1,235]],status='FULL_GEO_REREAD_AND_LITERAL_UV_CHECKED'))
save(B/'acquisition.json',m)
rows=[]
def ev(id,claim,refs,limit):rows.append(dict(id=id,finding=claim,sources=[dict(source=s,ranges=rg) for s,rg in refs],limits=limit,new_reference_credit=0))
ev('A01','特殊SpellArrow弹药先检查mana capability；无mana返回原生Arrow。非玩家或主手不是ICasterTool时返回父ArrowItem工厂。先new出的未返回自定义箭不是已入世界的额外箭。',[('SpellArrow',[[41,54]]),('ArrowItem',[[13,17]])],'仅所读固定版本工厂，不代表所有其他射手/附魔模组。')
ev('A02','所读SpellCrossbow未重写getSpellCaster，使用ICasterTool默认new SpellCaster(stack)。其构造从NBT反序列化新的Spell；getSpell返回本次caster内存对象；modifySpell append没有调用writeItem。此路径不能宣称永久给武器追加增幅。',[('ICasterTool',[[84,96]]),('SpellCaster',[[23,37],[164,205]]),('Spell',[[143,159]]),('SpellArrow',[[48,52]])],'其他ICasterTool实现可以覆盖工厂；未把所有法器推为同样行为。')
ev('A03','SpellContext保存传入Spell引用，复制casterTool ItemStack，另克隆颜色。这个上下文/工具快照与射手主手条件须分开。',[('SpellContext',[[49,64]]),('SpellArrow',[[48,52]])],'引用/复制结论限这些字段；无线程、NBT持久化或实际耗蓝成功断言。')
ev('A04','普通Items.ARROW且isSpell会替换为buildSpellArrow；SpellArrow特殊弹药则使用其工厂结果，只有结果确为EntitySpellArrow才叠加弩穿透与设置拖尾颜色。',[('SpellCrossbow',[[196,217],[237,251],[291,301]])],'同一家族不同分支，不拆成新参考；addFreshEntity成功仍未实测。')
ev('A05','特殊箭RGB为三个自定义SynchedEntityData字段，setColors只写这三项；client拖尾消费RGB。并非原生Arrow的ID_EFFECT_COLOR。',[('EntitySpellArrow',[[38,65],[174,189],[269,274]]),('Arrow',[[27,31],[89,92],[127,134]])],'包到达/粒子设置/其他扩展仍影响观感；不把拖尾颜色说成整根箭染色。')
ev('A06','ENTITY_SPELL_ARROW实际绑定TippableArrowRenderer，后者仅用Arrow.getColor()>0选择原版tipped_arrow.png或arrow.png；ArrowRenderer顶点是白色不额外使用自定义RGB。',[('ClientHandler',[[61,66],[128,128]]),('TippableArrowRenderer',[[9,20]]),('ArrowRenderer',[[22,71]])],'所读默认自定义箭不设置原生药水色，因此该路径选普通arrow；外部修改/getColor覆盖不在结论中。')
ev('A07','箭身使用entityCutout与原版交叉平面/尾部面，0.05625缩放、插值yaw/pitch及shake；并未加载弩的geo.json给飞行箭。',[('ArrowRenderer',[[22,71]])],'尺度是所读模型局部，不是游戏命中箱或所有姿态截图。')
ev('A08','EntitySpellArrow重写getAddEntityPacket使用NetworkHooks；Neo47.1.64 NetworkHooks将PlayMessages.SpawnEntity封为PLAY_TO_CLIENT。不能直接套B09原生Projectile的owner runtime ID字段。',[('EntitySpellArrow',[[305,317]]),('NetworkHooks',[[70,75]]),('PlayMessages',[[43,74],[94,128]])],'框架源码精确版本重建；未运行网络。')
ev('A09','SpawnEntity基本字段为type、entity ID/UUID、位置角度速度，无单独owner字段；只有IEntityAdditionalSpawnData能额外写读。对应注册customClientFactory调用客户端构造，而构造只super(type,world)，不解析packet。',[('PlayMessages',[[43,74],[94,178]]),('IEntityAdditionalSpawnData',[[10,31]]),('EntityType',[[654,657],[754,768]]),('ModEntities',[[123,126]]),('EntitySpellArrow',[[315,317]])],'选定生成路径没有显式恢复owner；不据此声称服务端owner丢失、客户端所有外部包都不可能补充。原生父类层级见既有B08。')
ev('A10','Neo生成包handle设置位置/旋转/ID/UUID，add到ClientLevel，lerpMotion初速度，再读额外数据；速度发送被限[-3.9,3.9]并量化8000。',[('PlayMessages',[[54,74],[143,178]])],'这只是初始包；后续ServerEntity速度/位移包不能据此断言永远限速。')
ev('A11','弩真实PNG32×32与geo声明一致；16个cuboid共96个逐面UV矩形，负uv_size表示有方向的范围，不能仅因负值判出界。',[('crossbow_geo',[[1,235]]),('spell_crossbow',[])],'只检查显式UV与PNG尺寸/像素，不是Gecko运行烘焙或玩家握持验收。')
ev('A12','gem的六个2×2 UV面是粉紫/淡黄色阶且alpha255，并非纯白中性图；宝石保留getRenderColor乘色，其他骨骼强制白色alpha1；最终entityTranslucent。',[('SpellCrossbowRenderer',[[25,38],[115,128]]),('crossbow_geo',[[16,36]]),('spell_crossbow',[])],'原图观察和逐面采样，不宣称游戏最终色；光照/色调/外部资源包仍未验证。')
ev('A13','近手粒子仅FIRST_PERSON_RIGHT_HAND且未暂停分支，由本地player、当前stack法术色计算；renderFinal也读取本地player使用状态。',[('SpellCrossbowRenderer',[[41,65],[69,113]])],'不是所有第三人称/NPC都获得同一效果的证明；既有Gecko renderFinal时序限制沿用B08。')
ev('A14','EntitySpellArrow普通字段resolver/pierceLeft/lastHit未见本类NBT覆盖；Arrow父类保存Potion/Color/effects并继承更上层Owner。本类RGB≠父类Color保存。',[('EntitySpellArrow',[[33,40],[267,318]]),('Arrow',[[136,174]])],'父类NBT与完整本类的既有B06/B09研究相互补充；本批不宣称reload后技能仍完整或已复现失效。')
geo=json.loads(gp.read_text())['minecraft:geometry'][0];im=Image.open(B/'sources/baileyholl__Ars-Nouveau/src/main/resources/assets/ars_nouveau/textures/item/spell_crossbow.png').convert('RGBA');faces=[]
for bone in geo['bones']:
 for ci,cube in enumerate(bone.get('cubes',[])):
  for name,uv in cube['uv'].items():
   u,v=uv['uv'];w,h=uv['uv_size'];box=[min(u,u+w),min(v,v+h),max(u,u+w),max(v,v+h)];samples=im.crop(box);cs=samples.getcolors(maxcolors=10000)
   faces.append(dict(bone=bone['name'],cube=ci,face=name,uv=uv,box=box,in_bounds=0<=box[0]<=box[2]<=im.width and 0<=box[1]<=box[3]<=im.height,colors=[dict(count=n,rgba=list(c)) for n,c in cs] if bone['name']=='gem' else None))
assert len(faces)==96 and all(f['in_bounds'] for f in faces)
save(B/'atlas-check.json',dict(size=list(im.size),declaration=[geo['description']['texture_width'],geo['description']['texture_height']],bounds=list(im.getbbox()),cuboids=sum(len(b.get('cubes',[])) for b in geo['bones']),faces=faces,original_viewed=True,nearest_12x_viewed=True,production_asset=False))
report=dict(saved_utc=now,title='Ars特殊箭工厂、实际飞行渲染与Neo生成消费者',scope='既有C-ARS邻接上下文补读，不是连弩直接链、不新增家族。',sources=sources,evidence=rows,new_source_families=0,new_accepted_gate_credit=0,global_accepted_total=None,production_modified=False,java_game_started=False,pending=['实际Forge/Neo环境编译与网络顺序未验证','客户端额外数据与资源包/其他模组插入未运行','法术箭卸载重载与实际持握/粒子截图未验收','逐生物100参考和六武器1000各自门槛仍未满足/不得相互抵扣'])
save(B/'special-arrow-render-review.json',report)
body='<html lang="zh"><meta charset="utf-8"><title>B11 Ars特殊箭与真实贴图</title><style>body{font:16px/1.65 system-ui;background:#131b20;color:#dde3e5;max-width:1060px;margin:32px auto}article{padding:18px 0;border-bottom:1px solid #40515a}a{color:#9ed1e1}img{image-rendering:pixelated;background:#333}code{color:#f4d994}</style><h1>B11 · Ars特殊箭与真实贴图</h1><p>只读研究；0个新增家族、0个验收计数。软件/源码证据，不是游戏验证。</p><p><a href="special-arrow-render-review.json">逐项证据与阅读范围</a> · <a href="acquisition.json">固定版本与来源</a> · <a href="atlas-check.json">96面UV检查</a> · <a href="local-verification.json">本地一致性检查</a></p><figure><img src="spell_crossbow-inspection-12x.png" width="384"><figcaption>实际作者PNG的12倍最近邻检查图。仅参考，未放入Dynasty生产资源。</figcaption></figure>'
for e in rows:body+='<article><b>'+e['id']+'</b><p>'+html.escape(e['finding'])+'</p><small>'+html.escape(e['limits'])+'</small></article>'
body+='<p>后续继续原范围未读的真实链/消费者，已认可资产保持；不以文件数、UV面数或本地校验替代100/1000参考。</p></html>'; (B/'index.html').write_text(body)
p=json.loads((B/'progress.json').read_text());p.update(saved_utc=now,status='SAVED_STATIC_REVIEW_CONTINUE_NEXT_BATCH',evidence_records=len(rows),source_families_added=0,accepted_credit_added=0,report='index.html',next='继续原范围真实链；登记真实任务物品与节点映射。');save(B/'progress.json',p)
rp=R/'progress.json';p=json.loads(rp.read_text());prev=p['this_batch'];prev['report']=p['latest_batch']+'/index.html'
if not any(x['id']==prev['id'] for x in p['previous_batches']):p['previous_batches'].append(prev)
p.update(updated_utc=now,latest_batch='batch-11',this_batch=dict(id='batch-11',source_studies=0,existing_family_context_extensions=1,evidence_records=len(rows),new_accepted_gate_credit=0,count_note='Ars特殊箭与真实PNG/Neo生成消费者，仍为既有邻接家族；不计生物或连弩直接参考。'))
p['continuation_window'].update(last_saved_utc=now,report='batch-11/index.html',progress='batch-11/progress.json',status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH');save(rp,p)
print(json.dumps(dict(evidence=len(rows),uv_faces=len(faces),new_credit=0)))
