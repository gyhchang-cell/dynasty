from pathlib import Path
import json,hashlib,zipfile,datetime,copy
R=Path.cwd();B=R/'docs/art/armor-bone-whole-20261112';P=R/'docs/art/armor-ra-atem-whole-20261112'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(n,d):
 p=B/n;assert not p.exists(),p;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return ref(p)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();key='thebetweenlands:bone';prov=read(B/'provenance.json');assert sha(prov['archive'])==prov['archive_sha256']
with zipfile.ZipFile(prov['archive']) as z:
 for n,h in prov['entries'].items():assert sha(B/'source'/n)==h==hashlib.sha256(z.read(prov['root']+n)).hexdigest(),n
ctx=read(B/'context-provenance.json')
for row in ctx['files']:assert sha(row['path'])==row['sha256']==sha(row['copy'])
# Reuse precise fixed input class provenance without Java/decompiler execution.
legacy_inputs=[]
for row in read(B/'context/class-source-provenance.json')['input_members']:
 if row['entry'].split('.')[0].split('$')[0] in ['bpx','brq','brs','agv','ccb','cbp','vl']:
  with zipfile.ZipFile(row['archive']) as z:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['sha256']
  legacy_inputs.append(row)
for row in read(B/'context/additional-derivation-receipt.json')['records']:
 if row['entry'] in ['bql.class','brd.class']:
  with zipfile.ZipFile(row['archive']) as z:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['original_sha256']
  legacy_inputs.append(row)
base=read(R/'docs/art/armor-ars-reference-20261111/source-baseline.json');assert len(base)==289
for n,h in base.items():assert sha(R/n)==h,n
priority=read(R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json');files={n:h for t in priority['targets'] for n,h in t['files'].items()};assert len(files)==70
for n,h in files.items():assert sha(R/n)==h,n
prev=read(P/'coordinator-delivery.json');assert sha(prev['receipt']['path'])==prev['receipt']['sha256'];frozen=read(prev['receipt']['path'])['files']
for row in frozen:assert sha(row['path'])==row['sha256']
ledger=read(P/'combined-semantic-ledger.json');before=copy.deepcopy(ledger);assert key not in ledger['reviewed_pending_whole_keys']
limits=['Main独立整套语义去重与适用性未验，本批正式信用0；不因四部位/宝石颜色/两层图集拆分设计。','固定源码是MC1.12.2 Forge14.23.5.2773；未启动精确patched二进制、Betweenlands coremod、客户端或资源包。','软件中立姿势双面透明诊断，不是游戏；未模拟动画、皮肤底层、OpenGL深度/混合、附魔glint或真实穿戴接缝，局部深度条纹不是游戏故障证据。','继承默认ItemArmor颜色00FFFFFF，Bone无覆盖；这与Item3DArmor自定义FFFFFFFF不同，不能套用后者双遍结论。外部mod改动消费者时需另验。','宝石NBT与模型predicate和wear路径静态闭合；实际合成镶嵌获取、缓存刷新及游戏显示未验，不把基础ID冒充额外注册ID。','64×32原图UV只供本甲默认模型；不把绿色面积直接复制为Dynasty竹材/皮革，也不把骨白主体当白底删掉。','289保护与70优先文件无变化；竹甲大原稿仅参考页NN缩略，运行原稿未缩16/减色或覆盖；从未重画资格仍0。','1000有效适用设计总数及准确缺口仍null、gate=false；不制作不覆盖，不操作共享Jar/主清单/用户实例。']
obs=[
'基础四图标16×16，头是紧凑圆阶顶与下部双颊，胸短宽肩与骨肋横块，裤直腿分空，靴细筒折脚；苔/黏绿偏侧附着，主体为黄灰骨片，不是白色画布。',
'基础穿戴两图集均64×32；L1头表面与胸臂、靴有实际像素，第二头帽层六面全透明；不能仅看到HEAD槽会显示head+hat就宣称额外冠层存在。',
'头主壳有20/64正面像素透明，源UV[8,8,16,16]其余44为骨色/绿；y最小的封顶面不透明64/64，y最大封底面全透明。源face标签DOWN/UP不代替模型坐标朝向。',
'胸前骨肋用中部少量骨白竖桥与横向条块，侧面多为绿/暗间隔，下摆留空；背面保留两侧骨条与中间绿，不用整张白壳糊满躯干。',
'护臂64×32共享一组40,16源UV，左臂镜像；上段骨袖和局部绿边短，前后/侧面空白让裸露区域保留。不能把16×16图标扩大后充当穿戴纹理。',
'L2腰四侧只有12/48或24/96像素不透明，上下封面透明，是3像素高的腰条而非整12高躯干布；裤腿正侧仍有骨色大片，绿色多集中外侧和下端。',
'外层足部沿用原生12高腿壳、inflate1；图集透明上段使可见靴低于全壳高度。内层裤腿inflate.5，不使用现代模型腿/靴减.1的形变。',
'正面看骨片肋与绿色竖缝，45°看头/胸/靴材质从正面接侧面，90°无额外肩角、披风或身体模型，背面骨条不与正面同纹理区；黑剪影/灰模显示实际透明负空间。',
'三宝石版本实际逐图检查：蓝/红/绿小亮核加在额中、胸背、护臂/腿靴横带处；底骨绿材质与几何保持同一布局，不是三套新设计。16个JSON的parent/layer0/predicate均本地解析到真实PNG。',
'相较Ra/Atem金属礼仪裙披片，本甲为原生双层biped上的骨片负空间，无专用几何/长冠/披风；相较旧骨肋学习族仍很接近，不凭材质色另授独立信用。']
models=read(B/'item-model-resolution.json');assert len(models)==16
for row in models:assert Path(row['texture']).exists()
applications={}
for fam in ['bamboo','leather']:
 applications[fam]={'files':[ref(R/n) for n in files if (fam+'_') in n and n.endswith('.png')], 'scope':'只读当前原稿和两层UV；不自动判为应重画，也不覆盖已认可资产。'}
applications['bamboo'].update(observed='现有竹黄绿纵板、深棕扎带与金黄竹节；大分辨率获选图标和64×32穿戴分开。',allowed_learning='只学习板片边界与底层负空间：L1袖/胸侧连续竹板和扎带分工，L2腿边保持纵向；已有竹材身份和获选比例保留。',reject='不变成白骨、苔绿甲或把骨肋形复制为竹条；不复制别人源像素。')
applications['leather'].update(observed='现有棕皮大块、深棕缝、斜胸带、短宽胸与两只靴；32×32图标无需重画。',allowed_learning='只学习较暗结构缝与材料主面的面积分工，穿戴袖口/胸侧/裤靴边界另核实际UV。',reject='皮革不画成硬骨白甲片或苔绿发光纹；材质学习不构成重画图标授权。')
study=write('semantic-review.json',{'batch':'D65','primary_whole_key':key,'source':prov,'actually_viewed':['native-pixels.png','native-all-icons.png','whole-all-variants.png','raw-uv-faces.png','current-target-readonly.png'],'observations':obs,'applications':applications,'source_whole_designs':1,'gem_variants_not_additional_designs':3,'new_validated_credit':0,'limits':limits})
bind=write('static-bindings.json',{'source_chain':'TheBetweenlands.preInit -> REGISTRIES.preInit -> ItemRegistry.preInit -> reflected BONE_HELMET/CHESTPLATE/LEGGINGS/BOOTS fields -> ItemBoneArmor(HEAD/CHEST/LEGS/FEET) -> ItemBLArmor(ARMOR_BONE,3,slot,bone) -> ItemArmor','registration':'registerItem lowercases field Locale.ENGLISH, setsRegistryName ModInfo.ID; registerItems event registers ITEMS; TheBetweenlands registers ItemRegistry event subscriber.','inventory':'ItemRegistry.registerModels -> proxy.registerDefaultItemRenderer -> ClientProxy.getItemModelMap default meta0 registryName#inventory -> base model item/generated and layer0. Gem property from CircleGemHelper controls three override models, all16 resolved. ItemBoneArmor not ITintedItem; no bone custom icon color handler in this hierarchy.','worn':'No getArmorModel override in ItemBoneArmor or ItemBLArmor; ForgeHooksClient getArmorModel returns provided default when item hook null. Legacy LayerBipedArmor ccb creates inner ModelBiped(.5) and outer(1); head+hat, chest body+arms, legs body+legs, feet legs.','texture':'ItemBLArmor.getArmorTexture tests CircleGemHelper.getGem; LEGS -> bone_2, other slots bone_1. Per gem replaces both resource paths. type parameter ignored but does not itself force overlay.','actual_pass':'Vanilla agv.c(ItemStack) returns16777215 for nonLEATHER ARMOR_BONE. No getColor or hasOverlay override in bone hierarchy. Forge2773 hasOverlay compares !=0x00FFFFFF or LEATHER; false -> one untinted base pass, optional separate glint. Do not carry Item3DArmorFFFFFFFF doublepass to Bone.','UV':'brq inflated8vertices with integer sourceUV unchanged; mirror swapsX and bql reverses ordered quad; bql UV corner order u2v1,u1v1,u1v2,u2v2. Original64×32 texture size bpx constructor. Default source establishes geometry, not final patched runtime proof.','geometry':ref(B/'geometry-uv-context.json'),'alpha':ref(B/'uv-alpha-measurements.json'),'consumer_context':ref(B/'context-provenance.json'),'legacy_inputs_checked':legacy_inputs,'gem_limit':'isApplicable accepts ItemArmor except ItemAmphibiousArmor; Bone qualifies statically. Gem tag int maps ids1/2/3 via enum. Actual acquisition/event runtime not tested.','runtime_verified':False})
nearest=[g for g in ledger['groups'] if g['semantic_group'] in ['bone_reptile_rib_vest','fossil_bone_plate','rib_armor_shared_layout']]
dedup=write('dedup-comparison.json',{'prior':ref(P/'combined-semantic-ledger.json'),'nearest_saved_observations_actually_reread':nearest,'comparison':'骨肋负空间/骨片甲已有近组，骨甲四槽及苔绿附着提供完整消费者研究但不能仅凭颜色或更完整槽位证明新设计。先列一个待审整族；由Main独立确认合组/适用性，不追加历史215学习组。','not_repeated':['atum:mummy','thebetweenlands:amphibious','atum:ra_atem_ceremonial_family','wizards_reborn:inventor_wizard'],'new_validated_credit':0,'historic_groups_added':0,'gate_met':False})
ledger['pending_whole_families'].append({'primary_whole_key':key,'review':study['path'],'sha256':study['sha256'],'whole_slots':4,'whole_candidate_learning_families':1,'new_validated_credit':0,'new_learning_groups':0,'nearest_old_groups':[x['semantic_group'] for x in nearest],'pending':limits});ledger['reviewed_pending_whole_keys'].append(key);ledger['current_batch_prior']=ref(P/'combined-semantic-ledger.json');ledger['current_batch_additional_D54_carry_credit']=0
assert ledger['groups']==before['groups'] and ledger['local_independently_accepted_whole_families']==before['local_independently_accepted_whole_families']
led=write('combined-semantic-ledger.json',ledger)
verify=write('verification.json',{'archive_entries_verified':len(prov['entries']),'context_source_copies_verified':len(ctx['files']),'legacy_class_inputs_verified':len(legacy_inputs),'model_JSON_texture_resolutions':len(models),'source_RGBA_images':24,'UV_rectangles_within64x32':60,'protected_assets_unchanged':289,'priority_files_unchanged':70,'prior_D64_frozen_files_verified':len(frozen),'prior_D64_delivery':ref(P/'coordinator-delivery.json'),'D54_full_accepted_object_preserved':True,'historic215_groups_preserved':True,'production_changes':0,'game_java_runs':0,'checklist_deletions':0,'gate_met':False,'validated_total':None,'exact_gap':None})
(B/'README.md').write_text('# D65 · Betweenlands 骨甲完整原图与穿戴 UV\n\n固定 commit `'+prov['commit']+'`，MC1.12.2 / Forge14.23.5.2773。四槽一套、三种宝石变化仍一套，新增正式信用0。\n\n'+ '\n\n'.join(obs)+'\n\n## 消费链差异\n\n骨甲继承ItemArmor非皮革默认颜色00FFFFFF，Forge2773 hasOverlay为false；仅基础未染色一遍，可另有glint。与Item3DArmor返回FFFFFFFF触发双遍不同。ItemBLArmor忽略type本身并不意味着双遍。\n\n原生旧版内层形变.5，外层1，头帽层1.5；不误套现代腿/靴减.1。raw-uv与alpha测量记录真实空白面，软件图不含玩家皮肤与真实深度/动作验收。\n\n## 当前资源对照\n\n竹甲大原稿只在分析页缩略，运行文件原分辨率保留；竹节/扎带不改为骨片。皮甲32px获选图标保持棕皮身份，只读对照穿戴材质主次。\n\n'+ '\n'.join('- '+x for x in limits)+'\n\n核验289保护、70优先资源及D64冻结文件；不启动Java/游戏，不碰共享Jar、主清单或用户存档。\n')
progress=write('progress.json',{'batch':'D65','updated_utc':now,'status':'WHOLE_SOURCE_STUDY_DONE_MAIN_INDEPENDENT_REVIEW_PENDING','key':key,'study':study,'bindings':bind,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0})
manifest={'schema':'D65.bone.whole.static.v1','updated_utc':now,'files':[ref(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]};raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(raw).hexdigest();rp=B/('bounded-receipt-'+h+'.json');assert not rp.exists();rp.write_bytes(raw)
delivery=write('coordinator-delivery.json',{'batch':'D65','key':key,'receipt':ref(rp),'study':study,'bindings':bind,'dedup':dedup,'verification':verify,'ledger':led,'progress':progress,'new_credit':0,'gate_met':False,'production_changes':0,'main_review_required':True,'pending':limits})
for row in manifest['files']:assert sha(row['path'])==row['sha256']
ptr=R/'docs/art/armor-continuation-20261102/progress.json';original=ptr.read_bytes();state=json.loads(original);assert state['latest_continuation']=='docs/art/armor-ra-atem-whole-20261112/progress.json','pointer moved, do not overwrite'
state.update(status='D65_WHOLE_BONE_SOURCE_DONE_GATE_PENDING',latest_continuation=str((B/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((B/'combined-semantic-ledger.json').relative_to(R)),latest_bone_whole_receipt=str(rp.relative_to(R)),latest_bone_delivery=delivery,latest_reference_gate_met=False)
assert ptr.read_bytes()==original;ptr.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'delivery':delivery,'frozen_files':len(manifest['files']),'archive_entries':len(prov['entries']),'context_files':len(ctx['files']),'legacy_inputs':len(legacy_inputs)},ensure_ascii=False))
