from pathlib import Path
import hashlib,json,zipfile,copy,datetime
R=Path.cwd();B=R/'docs/art/armor-tyr-whole-20261112';P=R/'docs/art/armor-bone-whole-20261112'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(n,v):
 p=B/n;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return ref(p)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();key='forbidden_arcanus:tyr';prov=read(B/'provenance.json');ctx=read(B/'context-provenance.json')
for rec,prefix in [(prov,B/'source'),(ctx,B/'context')]:
 assert sha(rec['archive'])==rec['archive_sha256']
 with zipfile.ZipFile(rec['archive']) as z:
  for n,h in rec['entries'].items():assert sha(prefix/n)==h==hashlib.sha256(z.read(rec.get('root','')+n)).hexdigest(),n
base=read(R/'docs/art/armor-ars-reference-20261111/source-baseline.json');assert len(base)==289
for n,h in base.items():assert sha(R/n)==h,n
priorities=read(R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json');priority={n:h for t in priorities['targets'] for n,h in t['files'].items()};assert len(priority)==70
for n,h in priority.items():assert sha(R/n)==h,n
pd=read(P/'coordinator-delivery.json');assert sha(pd['receipt']['path'])==pd['receipt']['sha256'];frozen=read(pd['receipt']['path'])['files']
for f in frozen:assert sha(f['path'])==f['sha256']
ledger=read(P/'combined-semantic-ledger.json');before=copy.deepcopy(ledger);assert key not in ledger['reviewed_pending_whole_keys']
limits=['Main独立整套去重/适用性待审，正式信用0；四部位、六PNG、60面、10软件体块和六视图不拆设计。','模组实际声明MC1.20.1 Forge47.1.3 ValhelsiaCore1.1.2；本地上下文为同MC的Forge47.4.10，未逐class证明与47.1.3相同，不冒充精确消费链或实机。','Valhelsia RegistryManager/ItemRegistryHelper 1.1.2源实现本地未固定；只证模组对helper声明及四个ArmorItem构造器，不声称依赖注册内部全闭合。','软件诊断无皮肤、动作、资源包、OpenGL深度/混合、trim/glint；细碎覆盖/交界不能当游戏实测错误或接缝验收。','图标未压成16；16px是该参考原生尺寸，运行原稿与他人像素均未复制到Dynasty。','289保护、70优先及既有精致原稿保持；鸿蒙等只借材质面积原则，不因旧穿戴待验而重画认可图标。','1000有效适用总数/准确缺口仍null，gate=false，不制作覆盖、不删主清单、不启动Java/游戏。']
obs=['四原生16×16图标：短顶头盔中央金竖鼻梁、短宽蓝胸、直筒双腿、独立折角靴；橙金只占结构边/扣/鞋面，蓝不是全幅宝石噪点。',
'两个64×32穿戴图集L1含头/胸/臂/靴，L2腰腿。HEAD的默认hat六面均0alpha，所以此套没有额外头冠层；主体头顶封面64/64不透明、封底0/64、正脸30/64。',
'头正金鼻梁和颊边与侧面方金环、后脑小金牌不同，不是前后完全复制。深蓝沿盔顶与外缘留大面，普通短头几何无羽冠/鹿角。',
'胸正以U形金领、蓝腹和腰金边构成，后有金背扣/分段竖线；胸正66/96不透明、背80/96，左右36/48，透明领/下摆不误涂满。',
'左右袖共享40,16矩形且左臂mirror。肩顶16/16金面，袖侧蓝金短片与底部单条金袖环间留透明间隔，不能用整块盔甲长袖糊满。',
'L2腰侧16/48、前背32/96不透明即4像素高腰带，非整12高裤身；裤腿四侧36/48，深蓝菱状离散暗阶与一条金下缘，避免密线装饰。',
'L1靴上半透明，下部橙金脚面与蓝嵌片；几何仍默认12高腿，实际非零UV面积仅约半壳。靴与裤分别取L1/L2，不能图标修改冒充两层已修。',
'正面、45°、90°侧、背、alpha黑剪影和灰模已查看：主要靠短甲/窄金边区别，未凭空增肩甲、披风或人物身体；软件预览保留alpha凹口但不模拟游戏皮肤。',
'四generated模型JSON实际引用minecraft:item/generated和单层item/armor/tyr_* PNG，build.gradle明确将src/generated/resources加入main资源集；不是缺模型时猜同名PNG。',
'物品直接new ArmorItem(TYR,type)无自定义染色/模型扩展；源材质名ResourceLocation forbidden_arcanus:tyr。47.4.10比较上下文将域分开并选LEGS layer2/其他layer1，基础无染色单遍，可另trim/glint。47.1.3差异保持待验。']
app={'target':'hongmeng','target_files':[ref(R/n) for n in priority if 'hongmeng_' in n and n.endswith('.png')],'current_pixels_reused_readonly_evidence':ref(R/'docs/art/armor-ra-atem-whole-20261112/current-target-readonly.png'),'observed_current':'已读获选白主面、紫内衬与金结构边；保持既有比例和纹样。','limited_application':'若后续授权穿戴修复，只借金领/腰带/袖环的连续材质分区，L1前侧背不能断成不同材料；L2内侧与靴L1分清。','not_authorized':'不把白金紫改成Tyr蓝金、不重画已认可图标，不用高冠/外挑肩表现强力。'}
study=write('semantic-review.json',{'batch':'D66','primary_whole_key':key,'source':prov,'actually_viewed':['native-pixels.png','whole-static-views.png','raw-uv-faces.png'],'observations':obs,'application':app,'new_validated_credit':0,'source_whole_designs':1,'limits':limits})
models=read(B/'item-model-resolution.json');assert len(models)==4
reg=(B/'source/src/main/java/com/stal111/forbidden_arcanus/core/init/ModItems.java').read_text();registrations=[l.strip() for l in reg.splitlines() if 'public static final' in l and ' TYR_' in l];assert len(registrations)==4
bind=write('static-bindings.json',{'actual_registration_declarations':registrations,'actual_helper_boundary':'ForbiddenArcanus @Mod -> RegistryManager(ModRegistryCollector MOD_ID) -> ModDefinition.withRegistryManager; collector.addItemHelper(ModItems.class); ModItems.HELPER=REGISTRY_MANAGER.getItemHelper. Valhelsia helper internals not fixed.','models':models,'packaging':'build.gradle sourceSets.main.resources.srcDir src/generated/resources','actual_material':'TYR ResourceLocation forbidden_arcanus:tyr, direct ArmorItem per Type. Constructor defense array uses enum map; no program changes/tests.','consumer_comparison':ctx,'comparative_texture':'47.4.10 getArmorResource splits namespace before composing textures/models/armor/tyr_layer_1 or2; ForgeHooksClient getArmorTexture may override; direct ArmorItem has no custom override here.','comparative_pass':'Not DyeableLeatherItem -> one untinted base. Optional ArmorTrim and hasFoil/glint separate, not same concept as dye overlay.','comparative_pose':'PlayerRenderer armor inner/outer ModelLayers -> LayerDefinitions 64×32 HumanoidArmorModel(inner.5/outer1) -> replacement legs extends -.1 -> actualleg.4 and boot.9, headhat1.5. Parentcopy/visibility before modelhook in47.4.10.','slot_masks':read(B/'geometry-uv-context.json')['slot_masks'],'mirror_deformation':'left_arm/left_leg shared UV mirrored; ModelPart cube mirror swaps X and reverses polygon, inflation does not expand UV. Original 60rects all bounds checked.','geometry':ref(B/'geometry-uv-context.json'),'alpha':ref(B/'uv-alpha-measurements.json'),'exact_mod_dependency_consumer_verified':False,'runtime_verified':False})
nearest=[g for g in ledger['groups'] if g['semantic_group'] in ['riptide_blue_gold_legwear','knight_metal_color_family','complete_favor_crossed_gold_plate']]
dedup=write('dedup-comparison.json',{'prior':ref(P/'combined-semantic-ledger.json'),'nearest_saved_observations_reread':nearest,'comparison':'蓝金已有Riptide裤靴、金边骑士和交叉金甲的学习观察。Tyr四槽是完整原版布局并有特定鼻梁/背扣/U领，但不能因补齐槽位或换蓝底就认定独立。Main需比较完整旧像素决定合并；不宣称重读全部640名称原图。','new_learning_groups':0,'new_validated_credit':0,'gate_met':False})
ledger['pending_whole_families'].append({'primary_whole_key':key,'review':study['path'],'sha256':study['sha256'],'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':limits});ledger['reviewed_pending_whole_keys'].append(key);ledger['current_batch_prior']=ref(P/'combined-semantic-ledger.json');ledger['current_batch_additional_D54_carry_credit']=0
assert ledger['groups']==before['groups'] and ledger['local_independently_accepted_whole_families']==before['local_independently_accepted_whole_families']
led=write('combined-semantic-ledger.json',ledger)
verify=write('verification.json',{'archive_entries_verified':len(prov['entries']),'different_version_context_entries_verified':len(ctx['entries']),'generated_models_resolved':4,'native_PNGs':6,'UV_rectangles_in_bounds':60,'protected_assets_unchanged':289,'priority_files_unchanged':70,'prior_D65_frozen_files_verified':len(frozen),'prior_delivery':ref(P/'coordinator-delivery.json'),'D54_full_accepted_object_preserved':True,'historic215_groups_preserved':True,'exact_Forge47_1_3_and_Valhelsia1_1_2_verified':False,'production_changes':0,'java_game_runs':0,'checklist_deletions':0,'gate_met':False,'valid_total':None,'exact_gap':None})
(B/'README.md').write_text('# D66 · Tyr 蓝金甲原图与穿戴 UV\n\n固定 Forbidden-Arcanus commit `'+prov['commit']+'`，原生四件一套，正式信用0。\n\n'+'\n\n'.join(obs)+'\n\n## 依赖边界\n\n实际依赖Forge47.1.3、ValhelsiaCore1.1.2；固定的本地默认消费者为同MC1.20.1 Forge47.4.10比较上下文，不冒充精确闭合。模组helper调用、generated资源打包、直接ArmorItem构造和实际材质名/PNG链已保存。\n\n## 适用性\n\n对鸿蒙只学习金边/主面比例、L1胸袖前后侧连续和L2腰腿/靴L1分工；不换已认可白金紫设计。粗像素参考，不复制他人纹样或源图。\n\n'+'\n'.join('- '+x for x in limits)+'\n')
progress=write('progress.json',{'batch':'D66','updated_utc':now,'status':'WHOLE_PIXEL_UV_STUDY_DONE_EXACT_DEPENDENCY_CONSUMER_AND_MAIN_REVIEW_PENDING','key':key,'study':study,'bindings':bind,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0})
manifest={'schema':'D66.tyr.whole.bounded.v1','updated_utc':now,'files':[ref(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]};raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(raw).hexdigest();rp=B/('bounded-receipt-'+h+'.json');assert not rp.exists();rp.write_bytes(raw)
delivery=write('coordinator-delivery.json',{'batch':'D66','key':key,'receipt':ref(rp),'study':study,'bindings':bind,'dedup':dedup,'verification':verify,'progress':progress,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0,'main_review_required':True,'pending':limits})
for f in manifest['files']:assert sha(f['path'])==f['sha256']
ptr=R/'docs/art/armor-continuation-20261102/progress.json';original=ptr.read_bytes();state=json.loads(original);assert state['latest_continuation']=='docs/art/armor-bone-whole-20261112/progress.json','pointer moved leave study only'
state.update(status='D66_TYR_PIXEL_UV_DONE_EXACT_DEPENDENCY_PENDING',latest_continuation=str((B/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((B/'combined-semantic-ledger.json').relative_to(R)),latest_tyr_whole_receipt=str(rp.relative_to(R)),latest_tyr_delivery=delivery,latest_reference_gate_met=False);assert ptr.read_bytes()==original;ptr.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'delivery':delivery,'frozen_files':len(manifest['files']),'protected':289,'priority':70},ensure_ascii=False))
