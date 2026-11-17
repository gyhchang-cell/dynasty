from pathlib import Path
from PIL import Image
import json,hashlib,math
B=Path(__file__).resolve().parent;root=Path.cwd();R=B/'source/src/main/resources/assets/dungeons_gear';G=B/'source/src/generated/resources/assets/dungeons_gear';prior=root/'docs/art/armor-dungeons-three-whole-20261114/combined-semantic-ledger.json';old=json.loads(prior.read_text());names=['climbing','spelunker','snow'];slots=['helmet','chestplate','leggings','boots']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
observations={
'climbing':{'outline':'棕米头罩以灰扣横带和砖红下缘分区；胸为暗绿底、浅米绳带与窄青蓝横条，裤是短腰/裆片，米靴分成两只直筒。','color_blocks':'衣身、领口、红边和绳带各占清楚大区，肩和躯干仍窄而紧凑；原图米/绿有离散块状明暗，不能靠大量细刻线表现功能。','occlusion':'头罩8×9×8外壳附10×2×1横条；臂和腿存在同尺寸两层盒，以不同inflate0.5/0.76、0.75/0.74与UV承担外层/底层。必须保留透明区域与穿着次序，不能将整块空口补满；最终遮挡尚未运行。','fit':'96×65专用图集；身体8×12×4、臂腿4×12×4。真实绑定沿注册四槽/专用geo而来，不能按64×32模板裁图。','counterexample':'裤图标是短裤而非完整双直腿；细绳交叉面积大，不能用于每套普通布甲，也不能复制绳带坐标/造型。','declared_material':'dungeons_gear:pelt','prior_groups':['explorer_straps_iron_variant'],'semantic_overlap':'旧探索装已有棕底交叉绑带；本次头罩横扣、蓝绳带与双层臂腿仅保存区别候选，不直接算独立新设计。'},
'spelunker':{'outline':'头部物品是棕色烛台带和单根白烛；胸为深蓝黑底加棕金肩带、腰扣，裤是短裤，靴为两块深青护片。','color_blocks':'胸中央暗区与两条暖棕竖带相衬，金扣只是小块；深色主材不需要满胸高亮或宝石，功能由烛光附件表达。','occlusion':'头骨没有完整8³盔壳，而是烛体、灯芯和边带7盒；flame父骨下五个7×9×0平面由动画交替缩放。服装身体基础盒透明大区不能凭PNG背景推断人体裸露/最终遮挡。','fit':'104×64专用图集；PetBatArmorGear四槽和独立spelunker动画，并非直接用默认空idle。五火焰骨的存在/引用已核，运行blend/可见性未核。','counterexample':'头烛台不适合作普通倒U护盔；短裤和扁靴不能作为用户普通裤甲/短直靴比例模板，火焰也不能当五设计或五张不同盔甲。','declared_material':'minecraft:light_plate (literal config; registered/resolved identity NOT verified)','prior_groups':['mining_apron_chest','explorer_straps_iron_variant'],'semantic_overlap':'旧采矿围裙仅胸部已读，旧探索装也有肩带；完整烛台头具/交替火焰用途提供不同候选，独立语义适用性仍待验。'},
'snow':{'outline':'浅蓝盔面以深灰倒U边口和白鼻梁收束，顶部两短片；胸灰蓝侧片加青色中央框/腰缘，裤图标为两小膝片，黑靴有青口和浅蓝前片。','color_blocks':'浅蓝硬片、深蓝底、青边和白色亮区在大面积中区分，饱和青只留局部；图集不含白毛皮，不能按名字臆测白毛外套。','occlusion':'头5盒包含8³盔壳及两条细轨/短片；胸主体8×12×4另有8×4×1子片，两臂各一片1×3×4侧甲。亮片与底层不能混涂，帽壳空口与最终人体衬色未实机。','fit':'96×65专用图集；FreezingResistanceArmorGear四槽继承父级getter，仅额外返回25抗冻数值，研究不修改玩法。config明确heavy_plate，不把蓝色当布料。','counterexample':'普通布皮不学青色发亮框和头顶轨片；裤只有护膝不适合完整直腿图标。当前显示看似发亮不等于已证明emissive渲染。','declared_material':'dungeons_gear:heavy_plate','prior_groups':['arctic_fur_leather','functional_fur_color_block_clothing'],'semantic_overlap':'旧毛皮两组一个棕白皮毛、一个紫粉/蓝黄衣装，本套不是同名毛皮套；仍需与旧其他灰蓝护甲完整语义对照，不能凭雪/冷色独立计数。'}}
records=[]
for n in names:
 g=json.loads((R/'geo/armor'/f'{n}_armor.geo.json').read_text())['minecraft:geometry'][0];desc=g['description'];bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones']);boxes=[]
 with Image.open(R/'textures/models/armor'/f'{n}_armor.png') as im:assert im.size==(desc['texture_width'],desc['texture_height'])
 for bone in g['bones']:
  chain=set();p=bone
  while 'parent' in p:
   assert p['name'] not in chain;chain.add(p['name']);assert p['parent'] in bones;p=bones[p['parent']]
  for i,c in enumerate(bone.get('cubes',[])):
   w,h,d=c['size'];u,v=c['uv'];bounds=[u,v,u+2*(w+d),v+d+h];assert all(math.isfinite(x) for x in [w,h,d,u,v]);assert 0<=u<=bounds[2]<=desc['texture_width'] and 0<=v<=bounds[3]<=desc['texture_height']
   boxes.append({'bone':bone['name'],'cube':i,'source_cube':c,'nominal_box_net_bounds':bounds})
 items=[]
 for slot in slots:
  mpath=G/'models/item'/f'{n}_{slot}.json';m=json.loads(mpath.read_text());assert m=={'parent':'minecraft:item/generated','textures':{'layer0':f'dungeons_gear:item/armor/{n}_{slot}'}}
  png=R/'textures/item/armor'/f'{n}_{slot}.png'
  with Image.open(png) as im:size=list(im.size);alpha=list(im.convert('RGBA').getchannel('A').getextrema())
  items.append({'id':f'dungeons_gear:{n}_{slot}','slot':slot,'model':str(mpath),'texture':str(png),'native_size':size,'alpha_range':alpha})
 config=json.loads((B/'source/src/main/resources/data/dungeons_gear/gearconfig/armor'/f'{n}_armor.json').read_text())
 records.append({'whole_key':f'dungeons_gear:{n}/default_config','design':n,'items':items,'gearconfig':config,'geo_description':desc,'bones':g['bones'],'boxes':boxes,'box_count':len(boxes),'plane_count':sum(0 in c['source_cube']['size'] for c in boxes),'constructor':{'climbing':'ArmorGear / COLD','spelunker':'PetBatArmorGear / BASIC','snow':'FreezingResistanceArmorGear / BASIC'}[n],'animation':f'dungeons_gear:animations/armor/spelunker_armor.animation.json' if n=='spelunker' else 'dungeons_libraries:animations/armor/armor_default.animation.json'})
anim=json.loads((R/'animations/armor/spelunker_armor.animation.json').read_text());animation=anim['animations']['idle'];sp=next(r for r in records if r['design']=='spelunker');bn={b['name'] for b in sp['bones']};assert set(animation['bones'])<bn;assert animation['animation_length']==1.28 and animation['loop'];save('flame-animation-binding.json',{'source_animation':anim,'bone_names_resolve':True,'linked_geo_bones':list(animation['bones']),'scope':'Five animation planes/state phases are ONE armor design, no runtime timing/visibility acceptance'})
save('three-whole-bindings.json',{'scope':'Static resource references, parent graph, atlas dimensions and nominal Bedrock list-UV bounds; NOT final signed faces/mirror/rotation/pose/seams or game proof','designs':records})
reviewrows=[]
for n in names:
 k=f'dungeons_gear:{n}/default_config';assert k not in old['reviewed_pending_whole_keys'];assert not any(k0==f'dungeons_gear:{n}' for k0 in old['reviewed_case_keys']);related=[]
 for gn in observations[n]['prior_groups']:
  g=next(g for g in old['groups'] if g['semantic_group']==gn);related.append({'group':gn,'cases':g['cases'],'read_observations':g['observations'][:1]})
 reviewrows.append({'whole_key':k,'four_source_slots':4,'observations':observations[n],'old_related_records_read':related,'new_validated_credit':0,'independent_novelty':'Pending; not inferred from namespace, number of files or material name'})
context=root/'docs/art/armor-dungeons-three-whole-20261114';refs=[]
for p in [context/'source/src/main/java/com/infamous/dungeons_gear/registry/ClientEventBusSubscriber.java',context/'consumer-provenance.json',context/'consumer-source/src/main/java/com/infamous/dungeons_libraries/items/gearconfig/ArmorGear.java',context/'consumer-source/src/main/java/com/infamous/dungeons_libraries/client/renderer/gearconfig/ArmorGearModel.java',context/'consumer-source/src/main/java/com/infamous/dungeons_libraries/client/renderer/gearconfig/ArmorGearRenderer.java',context/'consumer-source/src/main/java/com/infamous/dungeons_libraries/init/ClientEventBusSubscriber.java',context/'consumer-source/src/main/resources/assets/dungeons_libraries/animations/armor/armor_default.animation.json']:
 refs.append({'path':str(p),'sha256':sha(p)})
save('source-consumer-context.json',{'reused_files':refs,'version_limit':'Same bounded D88 context: requestedLibraries3.0.10/Gecko3.1.40 vs contextLibraries3.0.12/Gecko3.1.39; runtime equivalence still unverified','new_subclass_sources':'Both constructors pass resource locations to ArmorGear unchanged; Gear CLIENT MOD AddLayers subscriber registers both subclasses with ArmorGearRenderer','old_consumer_not_recounted_as_new_design':True})
review={'batch':'D89','status':'THREE_NEW_FIELD_ARMOR_SOURCE_CASES_STUDIED_PENDING_ACCEPTANCE','new_source_whole_cases':3,'native_png_viewed':15,'new_validated_credit':0,'new_learning_groups':0,'requirements':{'global_sha256':sha(B/'global-texture-requirements.txt'),'project_sha256':sha(B/'project-texture-requirements.txt'),'target_scope':'70 protected priority armor resources; no target both never-redrawn and crude established','production':False},'designs':reviewrows,'global_gate':{'met':False,'accepted_total':None,'exact_gap':None},'pending':['Independent complete design novelty and applicability acceptance; old related groups not reset','Exact requested consumer and loaded binary equivalence unverified','Final slot visibility, signed UV/mirror/seams/pose/fiveviews/silhouette not game tested','literal minecraft:light_plate material resolution, actual native source/loot/payment unverified','No priority resource proven both never-redrawn and crude; no redraw permission created','Global1000 accepted total and exact gap unverified'],'prior_D88_view_index':str(B/'prior-D88-view-index.json')}
save('semantic-review.json',review)
new=json.loads(prior.read_text());new['current_batch_prior']={'path':str(prior),'sha256':sha(prior)}
for r in reviewrows:
 k=r['whole_key'];new['reviewed_pending_whole_keys'].append(k);new['pending_whole_families'].append({'primary_whole_key':k,'review':str(B/'semantic-review.json'),'sha256':sha(B/'semantic-review.json'),'already_recorded_case':None,'whole_slots':4,'new_learning_groups':0,'new_validated_credit':0,'pending':review['pending']})
save('combined-semantic-ledger.json',new);print([(r['design'],r['box_count'],r['plane_count']) for r in records])
