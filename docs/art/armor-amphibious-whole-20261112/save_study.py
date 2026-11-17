"""Write bounded source-study evidence. No production edits or checklist writes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=R/'docs/art/armor-mummy-whole-20261112';C=R/'docs/art/armor-three-consumers-20261112'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p).resolve();return {'path':str(p),'sha256':sha(p)}
def write(n,x): (B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
now=datetime.now(timezone.utc).isoformat();prov=json.loads((B/'provenance.json').read_text());geo=json.loads((B/'geometry-uv-context.json').read_text());prior=json.loads((OLD/'combined-semantic-ledger.json').read_text())
ids=['thebetweenlands:amphibious_'+s for s in ['helmet','chestplate','leggings','boots']]
limits=['Main独立整族语义去重与适用性审查未通过，本批新增信用0。','仅源代码静态对应；未加载精确Forge2773+Betweenlands实际二进制、coremod、资源包和实体渲染状态。','软件预览是构造器绑定姿势、四槽并集、双面简化；不是实机或真人，未模拟原生背面剔除、动画、混穿、光照/附魔及双遍绘制。','28个零维平面、61体块、366面、80节点和4槽不是独立设计；三宝石变体不新增信用。','三种宝石版本只固定源文件和分支，未逐图观看或测试获得条件。','289保护资产、70优先文件和现有精致旧稿保留；七家族从未重画资格仍未确认。','1000适用设计总数与准确缺口仍null；不制作、不接入、不删除任何待办。']
observations=[
 '四张16px原图与128方图集已实际查看：深苔绿硬片、灰蓝内衬、少量粉红鳃/须及米白眼/腰扣；有机功能身份由材料分区和小面积异色共同形成。',
 '头图有两侧米白眼位和红须，正面盔下灰蓝颈面；不能把这种生物脸部照搬普通人类头盔或把有意封闭部当缺面。',
 '原像素中胸是短宽绿肩/绿胸上段与灰蓝下段；裤上缘绿腰带加米白正扣，直裤灰蓝为主；双靴绿筒分开，红条只在局部边。',
 '绑定姿势正面显示窄鼻甲和下伸须，45度/侧面可见三段鳃链、胸下鳍与脚背前伸鳍，背面保留灰蓝连续背衬和上缘绿带；不是普通板甲的同布局换色。',
 '黑剪影表明鳃须会改变头侧宽度，斜肩和长靴前伸明显；灰模显示层叠靠专用几何承担，而非普通64x32上贴图就可复现。此两点作为禁止直接套用的限制。',
 '逐面页1-2：头顶绿大面、侧板灰蓝/浅绿、前眼米白红点、须末端红块；28个平面中的须/鳃两面UV是同一条矩形反向，不可把其空白UV面误判漏贴。',
 '逐面页3-4：胸左右大片绿壳，内臂和躯干灰蓝像素簇，胸/背鳍粉紫；腰两侧绿环带与米白扣连续，零X腰鳍的左右面读同一UV区。',
 '逐面页5-6：裤腿灰蓝大面、顶部浅绿边、靴筒深绿、前侧三块脚背片与红鳍；左右腿/靴是显式不同位置及UV，所有ModelBox镜像参数false，不能用同一mirror模板代替。',
 '灰蓝内衬像素簇呈密集斜格，移用到鲛绡会放大现有密鳞纹问题；只学深浅主面面积分工，不学满面斜格或绿色/红鳃配色。'
]
application={
 'target_ids':['dynasty:sea_silk_'+s for s in ['helmet','chestplate','leggings','boots']],
 'actual_identity':'DynastyGear.java91-95：鲛绡甲，水战轻甲；现有四图32x32，两穿戴层64x32，保持其浅青布/鳞材料和已认可轮廓。',
 'current_pixel_observation':'本轮只读current-target-readonly.png：浅青短盔、V领短胸、直腿及分开靴；穿戴图深浅菱片较密，头顶区域有稀疏分布。不是证实全套需重画或坏图。',
 'possible_later_use':['胸与背使用成片浅青主材，侧面保留较深衬区，避免四面同等亮度。','袖缘、腰边、靴口以同一条低对比材质边呼应，而非满身加红点/金边。','保留原版尺寸和UV接口；若将来确认修复，只做既有穿戴UV的材质区微调，不扩大肩、加鳍须或重画获选图标。'],
 'not_applicable':['怪物眼位/鼻甲/须/鳃和动画骨架不适用于普通鲛绡甲。','128方自定义UV与现有64x32标准甲不兼容，不缩图、不直接粘贴或复制。','不能用参考生物甲的复杂度证明普通布甲需要增加几何。'],
 'production_authorized_by_this_study':False}
write('semantic-review.json',{'batch':'D63','key':'thebetweenlands:amphibious','updated_utc':now,'source':ref(B/'provenance.json'),'native_slots':ids,'whole_family_candidate':1,'new_validated_credit':0,'new_learning_groups':0,'viewed_pages':[ref(B/n) for n in ['native-pixels.png','whole-static-views.png','current-target-readonly.png']+[f'raw-uv-faces-{i}.png' for i in range(1,7)]],'observations':observations,'application':application,'limits':limits})
near={
 'tide_fins':'同有水生鳍片与浅下沿，最接近；本套另有显式须鳃链、分段胸壳、腰鳍及前脚鳍。不能仅凭这些附件就授新族信用，待Main原源去重。',
 'organic_aquatic_horned_plate':'同水系壳甲/内衬主次，本套没有横长角冠，以鳃须和灰蓝衬区区别；仅属当前源观察，不能排除归并。',
 'biome_closed_diving_equipment':'旧记录以封闭观察窗及密封裤靴表达潜水；本套是仿两栖生物的须鳃片。功能同为水域，不把水域名称当新设计依据。',
 'three_bolt_diver':'铜圈观察窗/灰布与本套有机鳃/绿硬片不同，但均水域装备；须保持审查，不按材质不同直接加数。',
 'deepling_mage_rib_cloth':'旧记录蓝底/肋片/布料，本套绿胸壳和灰衬、红鳍；是否独立需旧原模型重开，不仅靠颜色。',
 'myrmex_shell':'旧组只有三部位虫壳中缝与尖胸，本套四部位和鳃/脚鳍链；虫/两栖来源也不自动证明两设计。',
 'creature_hide_shell_vests':'共同是生物材料与硬软分区；旧组含短胸/牙骨边，本套没有白牙栅栏，仍保留生物壳族重叠风险。',
 'functional_tattered_cloth':'本套明确硬绿壳+灰内衬+红平面，区别D62缠布/破布；不是用另一颜色重复上批缠布。'}
write('dedup-comparison.json',{'prior':ref(OLD/'combined-semantic-ledger.json'),'historical_groups_preserved':prior['groups'],'historical_groups_count':len(prior['groups']),'current_explicitly_reread_nearest_groups':[{'full_prior_group':g,'comparison':near[g['semantic_group']],'new_credit':0} for g in prior['groups'] if g['semantic_group'] in near],'coverage_limit':'215组全文原样保留，并复用先前已读记录；本轮只重读上述8组观察，不声称重开全部640名字原图/模型。','whole_key_absent_from_prior_case_list':'thebetweenlands:amphibious' not in prior['reviewed_case_keys'],'name_absence_not_semantic_independence':True,'decision':'PENDING_INDEPENDENT_WHOLE_DEDUP','new_credit':0})
consumer_rel=['derived-1.12-final/bpx.java','derived-1.12-final/brq.java','derived-1.12-final/brs.java','derived-1.12-final/cbp.java','derived-1.12-final/ccb.java','derived-1.12-final/agv.java','derived-1.12-final/vl.java','derived-1.20.1-and-old-quad/bql.java','debug-strip-receipt.json','class-source-provenance.json','additional-derivation-receipt.json','source/forge-1.12.2-14.23.5.2773-userdev.jar','source/mcp-config-1.12.2.zip','source/mojang-1.12.2-version.json','source/mojang-client-provenance.json']
consumer_rel += ['source/forge14.23.5.2773/'+p for p in ['patches.zip/net/minecraft/client/renderer/entity/layers/LayerArmorBase.java.patch','patches.zip/net/minecraft/client/renderer/entity/layers/LayerBipedArmor.java.patch','patches.zip/net/minecraft/item/Item.java.patch','patches.zip/net/minecraft/item/ItemArmor.java.patch','sources.zip/net/minecraftforge/client/ForgeHooksClient.java']]
for p in consumer_rel:assert (C/p).is_file(),p
write('static-bindings.json',{'key':'thebetweenlands:amphibious','version':'build.gradle85-93: MC1.12.2 Forge14.23.5.2773','actual_slots':[{'id':id,'slot':slot,'registry_source_lines':326+i,'model_json':f'models/item/{id.split(":")[1]}.json','base_icon':f'textures/items/{id.split(":")[1]}.png'} for i,(id,slot) in enumerate(zip(ids,['HEAD','CHEST','LEGS','FEET']))],
 'registration_chain':['TheBetweenlands.preInit145/159-160 registers registry owner; Registries.preInit12 calls ItemRegistry.preInit.','ItemRegistry604-627 reflects itemfields, lowercaseLocaleENGLISH -> registrythebetweenlands and same translation;823-841 registers each item and delegatesinventorymodel.','ClientProxy610-635 sets metadata0 registry#inventory for this class; four item/generated JSON resolve baseicons; gem1/2/3 variants remain same whole family.'],
 'material_chain':['ItemAmphibiousArmor78-89 ->Item3DArmor(BLMaterialRegistry.ARMOR_AMPHIBIOUS,3,slot,amphibious); createModelreturnsModelAmphibiousArmor.','BLMaterialRegistry32 creates separate amphibiouse num12,[1,2,3,1],enchant0,equipleather,toughness0; leather sound is NOT LEATHER material identity.'],
 'model_chain':['Item3DArmor49-67 staticclass-keyed modelcache; obtains/creates model, then calls ModelBodyAttachment.setVisibilities(armorSlot).','ModelBodyAttachment20-43 clears seven base cuboids plus empty boot/waist roots; boots remain legchildren, waist remains bodychild.','setVisibilities45-109 selects head subtree / chest+arm subtrees / waist+leg subtrees / boot subtrees. Extra-root exclusions preserve traversal but not other slot geometry.','Forge2773 LayerBipedArmor patch->ForgeHooksClient.getArmorModel->item hook. LayerArmorBase hook runs BEFORE copy attributes / setLivingAnimations / vanilla slotmask.','Default LayerBipedArmor mask HEAD head+hat;CHEST body+arms;LEGS body+legs;FEET legs. Actual child selection therefore matters; clearing root cuboids means no underlying vanilla armor shell.','ModelBodyAttachment112-140 special ArmorStand pose else ModelBiped animation; ModelAmphibiousArmor535-617 animates whisker/gill/fin deltas, resets listed baseangles each frame; not executed here.','ModelRenderer recursive render gate hidden/show then pivot*Rz*Ry*Rx; 61 ModelBox values parsed from constructor,28 planes, all mirrorfalse/inflate0; literal dimensions and UV retained.'],
 'texture_chain':['Item3DArmor23-39 overrides both armorTextures slots to textures/armor/amphibious.png; gem override maps both to amphibious_aqua/crimson/green.png.','ItemBLArmor60-78 reads CircleGemHelper.getGem NBT Gem and selects same configured atlas for LEGS vs other slots; ignores overlay type.','CircleGemHelper73-79 absentNBT ->NONE;130-132 inventorypredicate returns gem.id. Presence of branches does not prove normal gem application: isApplicable45-46 EXCLUDES ItemAmphibiousArmor; obtained variants not tested.'],
 'important_double_pass_correction':{'item_color':'Item3DArmor43-45 returns0xFFFFFFFF (-1)','forge_comparison':'ItemArmor2773.hasOverlay compares getColor !=0x00FFFFFF (16777215)','result':'true even though RGB white and material is not LEATHER; LayerArmorBase renders tinted pass then uncolored pass with same texture (type ignored), glint if enchanted. Not a single-pass armor.','preview_limit':'software is one alpha-tested pass without glint/blending/cull; no exact runtime equivalence claimed'},
 'consumer_source_provenance':[ref(C/p) for p in consumer_rel], 'geometry':ref(B/'geometry-uv-context.json'),'runtime_validated':False,'unresolved_runtime':['actualpatchedclientbinary+BLcoremod','resourceoverrides','precise culling+alpha+doublepass+glint','pose/animation/mixedset seams']})
write('source-reading.json',{'scope':'Bounded art-consumer study only. No upstream gameplay execution.','source_ranges':{'ModelAmphibiousArmor.java':[[1,623]],'ModelBodyAttachment.java':[[1,142]],'Item3DArmor.java':[[1,69]],'ItemBLArmor.java':[[1,178]],'ItemAmphibiousArmor.java':[[1,145],[580,717]],'CircleGemHelper.java':[[1,154]],'ItemRegistry.java':[[320,332],[595,635],[818,844]],'ClientProxy.java':[[610,635]],'TheBetweenlands.java':[[132,164]],'Registries.java':[[1,33]],'BLMaterialRegistry.java':[[32,32]],'build.gradle':[[1,95]]},'legacy_sources':'Exact Forge2773 patch bodies re-read, ModelBox and TexturedQuad complete and ModelRenderer render86-139 re-read; earlier D59-61 wholeconsumer reading reused by immutablehash.','not_claimed':['complete717linegameplayreview','gemobtainingplaytest','alloldoriginalassetsreread'],'pixels_viewed':[ref(p) for p in sorted(B.glob('*.png'))],'software_transform':'constructorhierarchy + biped bind pivots only; extra bipedBoot andWaistparent edges explicitlyseeded; standard rootcuboidsremoved','runtime_or_java_starts':0})
# Freeze integrity checks; never rewrite prior evidence.
z=zipfile.ZipFile(prov['archive']);zr=z.namelist()[0].split('/')[0]+'/'
assert sha(prov['archive'])==prov['archive_sha256']
for rel,h in prov['entries'].items(): assert sha(B/'source'/rel)==h==hashlib.sha256(z.read(zr+rel)).hexdigest(),rel
protected=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
for p,h in protected.items():assert sha(R/p)==h,p
targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text())
targetfiles={p:h for t in targets['targets'] for p,h in t['files'].items()}
for p,h in targetfiles.items():assert sha(R/p)==h,p
oldreceipt=next(OLD.glob('bounded-receipt-*.json'));oldobj=json.loads(oldreceipt.read_text())
for f in oldobj['files']:assert sha(f['path'])==f['sha256'],f['path']
# Preserve full accepted D54 object including authorACK and elevenfindings, not a count-only carry.
ledger=json.loads(json.dumps(prior));ledger['current_batch_prior']=ref(OLD/'combined-semantic-ledger.json');ledger['current_batch_additional_D54_carry_credit']=0
pending={'primary_whole_key':'thebetweenlands:amphibious','review':str(B/'semantic-review.json'),'sha256':sha(B/'semantic-review.json'),'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'nearest_old_group':'tide_fins','pending':limits}
assert not any(p.get('primary_whole_key')==pending['primary_whole_key'] for p in ledger['pending_whole_families'])
ledger['pending_whole_families'].append(pending)
ledger['reviewed_pending_whole_keys'].append('thebetweenlands:amphibious')
assert ledger['groups']==prior['groups'] and ledger['local_independently_accepted_whole_families']==prior['local_independently_accepted_whole_families']
assert ledger['gate_met'] is False and ledger['validated_independent_design_total'] is None
write('combined-semantic-ledger.json',ledger)
write('verification.json',{'updated_utc':now,'archive_members_verified':len(prov['entries']),'protected_unchanged':len(protected),'priority_source_files_unchanged':len(targetfiles),'prior_frozen_files_unchanged':len(oldobj['files']),'native_slots':4,'base_icons_viewed':4,'base_wear_atlases_viewed':1,'boxes':len(geo['boxes']),'zero_dimension_boxes':geo['zero_dimension_boxes'],'raw_uv_faces':len(geo['faces']),'uv_outside_128':0,'D54_full_object_preserved':True,'D54_repeat_credit':0,'prior215groups_unchanged':True,'new_credit':0,'global_total':None,'exact_gap':None,'gate_met':False,'production_changes':0,'game_starts':0,'java_cli_starts':0,'main_checklist_changes':0,'shared_jar_changes':0,'runtime_validated':False,'source_pixels_unchanged':True,'limits':limits})
write('progress.json',{'updated_utc':now,'batch':'D63','status':'WHOLE_SOURCE_STUDY_DONE_INDEPENDENT_REVIEW_AND_RUNTIME_PENDING','key':'thebetweenlands:amphibious','study':ref(B/'semantic-review.json'),'bindings':ref(B/'static-bindings.json'),'ledger':ref(B/'combined-semantic-ledger.json'),'production_changes':0,'new_credit':0,'gate_met':False})
(B/'README.md').write_text('''# D63：完整两栖甲参考源核查\n\n固定 Betweenlands eafac1c217cdf304d477b025708e0dadf82b6953，MC1.12.2 / Forge14.23.5.2773。四件属于一个待独立审查整族；3宝石变体、4槽、61体块和366面均不拆计。新信用0，适用1000门槛仍未达到。\n\n已查看四原生16px图标、128方基础穿戴原图、六页逐面UV，以及软件绑定姿势正面/45度/侧面/背面/黑剪影/灰模。当前Dynasty鲛绡四图及两穿戴层只读对照，未重画。参考只借鉴成片硬软材质分区与局部边缘呼应，不搬用怪物眼、鳃须、鳍片或专用UV。\n\n补全注册→四槽→材质→Item3DArmor类缓存→子树显隐→精确Forge2773消费补丁→旧ModelBox逐面UV的静态链。发现getColor为0xFFFFFFFF而Forge比较0x00FFFFFF，故会触发同纹理双遍，不能误记单遍。gem分支存在但普通isApplicable明确排除该甲，未声称生存获得可用。\n\n软件图不是游戏或穿戴验收，未模拟原生剔除、动画与双遍。未开Java/游戏、声音、亮度；未操作实例/存档；289保护资产和70优先文件哈希不变，无生产改动或清单删除。旧215组、D54完整接受对象和全部限制原样继承。详情见semantic-review、static-bindings和verification。\n''')
# immutable receipt excludes itself and subsequent delivery file
files=[ref(p) for p in sorted(B.rglob('*')) if p.is_file() and p.name!='coordinator-delivery.json' and not p.name.startswith('bounded-receipt-')]
payload={'schema':'D63.whole.amphibious.static.v1','updated_utc':now,'files':files};raw=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode();rp=B/f'bounded-receipt-{hashlib.sha256(raw).hexdigest()}.json';rp.write_bytes(raw)
write('coordinator-delivery.json',{'batch':'D63','key':'thebetweenlands:amphibious','receipt':ref(rp),'study':ref(B/'semantic-review.json'),'bindings':ref(B/'static-bindings.json'),'dedup':ref(B/'dedup-comparison.json'),'verification':ref(B/'verification.json'),'progress':ref(B/'progress.json'),'ledger':ref(B/'combined-semantic-ledger.json'),'new_credit':0,'gate_met':False,'production_changes':0,'main_review_required':True,'important_correction':'getColorFFFFFFFF !=Forge00FFFFFF ->sameatlasdoublepass, notsinglepass','pending':limits})
# CAS specialist pointer only; main/pending/ownership/session stay untouched.
pp=R/'docs/art/armor-continuation-20261102/progress.json';oldbytes=pp.read_bytes();ptr=json.loads(oldbytes)
assert ptr['latest_continuation']=='docs/art/armor-mummy-whole-20261112/progress.json'
ptr['status']='D63_WHOLE_AMPHIBIOUS_SOURCE_DONE_GATE_PENDING';ptr['latest_continuation']='docs/art/armor-amphibious-whole-20261112/progress.json';ptr['latest_combined_semantic_ledger']='docs/art/armor-amphibious-whole-20261112/combined-semantic-ledger.json';ptr['latest_reference_gate_met']=False;ptr['latest_local_delivery']=ref(B/'coordinator-delivery.json')
assert pp.read_bytes()==oldbytes;pp.write_text(json.dumps(ptr,ensure_ascii=False,indent=2)+'\n')
for f in payload['files']:assert sha(f['path'])==f['sha256'],f['path']
print(json.dumps({'delivery':ref(B/'coordinator-delivery.json'),'files_frozen':len(files),'protected':len(protected),'priority':len(targetfiles),'old_frozen':len(oldobj['files']),'new_credit':0},ensure_ascii=False))
