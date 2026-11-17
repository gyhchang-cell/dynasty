from pathlib import Path
import json,hashlib,zipfile,copy,datetime
R=Path.cwd();B=R/'docs/art/armor-arcane-gold-whole-20261112';P=R/'docs/art/armor-draco-whole-20261112'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(n,v):
 p=B/n;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return ref(p)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();key='wizards_reborn:arcane_gold';prov=read(B/'provenance.json');ctx=read(B/'context-provenance.json')
for rec,dest in [(prov,B/'source'),(ctx,B/'context')]:
 assert sha(rec['archive'])==rec['archive_sha256']
 with zipfile.ZipFile(rec['archive']) as z:
  for n,h in rec['entries'].items():assert sha(dest/n)==h==hashlib.sha256(z.read(rec.get('root','')+n)).hexdigest(),n
base=read(R/'docs/art/armor-ars-reference-20261111/source-baseline.json');assert len(base)==289
for n,h in base.items():assert sha(R/n)==h,n
priority_info=read(R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json');priority={n:h for t in priority_info['targets'] for n,h in t['files'].items()};assert len(priority)==70
for n,h in priority.items():assert sha(R/n)==h,n
pd=read(P/'coordinator-delivery.json');assert sha(pd['receipt']['path'])==pd['receipt']['sha256'];oldfiles=read(pd['receipt']['path'])['files']
for f in oldfiles:assert sha(f['path'])==f['sha256']
ledger=read(P/'combined-semantic-ledger.json');before=copy.deepcopy(ledger);assert key not in ledger['reviewed_pending_whole_keys']
limits=['正式新增信用0，Main独立完整设计去重/适用性待审；四图标、两图集、10默认体块、60面和多角度不拆设计。','固定模组依赖MC1.20.1 Forge47.3.0 FluffyFur0.3；本地消费者比较为Forge47.4.10，未证明精确47.3.0运行同源。','仅原生未附加ItemSkin基础套研究；皮肤NBT、FluffyFur全球重定向及ArcaneEnchantment产生的额外表现未闭环，不声称所有物品栈显示相同基础纹理。','软件诊断为中立四槽并集，不是游戏，不含皮肤实体、动作、资源包、光照、OpenGL深度/混合、trim/glint或实际接缝验收；局部覆盖条纹不当实机故障。','参考原生16px不代表将用户原稿压16；Dynasty运行原稿、注册ID、共享Jar、存档和主清单未修改。','289保护与70优先保持，精致/获认可图标保留；七优先家族从未改画资格仍0，不借旧穿戴疑点扩张重画权限。','1000适用有效设计总数及准确缺口仍null、gate=false；历史215组/640名称不冒充1000，不清零已有D54验收或此前固定证据。']
obs=['四原生16×16库存图标：紧凑倒U盔口、短宽胸、两条直腿和独立L靴；玫金主面、米黄亮阶、红褐暗边，靠大块离散明暗而非额外徽饰表现材料。',
'原生两层64×32；L1头/胸/臂/靴，L2腰腿。hat整层384像素全透明；头主层240/384非零，头顶与下颊处的alpha空白不同，不借空hat编造外冠。',
'头侧额一条米黄横面与棕红后下颊，正面亮眉/鼻边留面孔开口；背面是分层暗金面，不把库存头图直接扩大成穿戴。',
'胸前为米黄领边向下垂的亮面和玫金腹大区，背部三段横向亮暗层，左右窄暗面；胸222/352非零，明暗留白没有额外肩角或整套人台图案。',
'左右臂共享40,16矩形且左mirror，每臂96/224非零；短袖上部亮面/暗边与下部小腕区分开，中段透明，不把整个默认12高臂壳涂满。',
'外层靴112/224非零，即下半壳；脚面用少量米黄亮阶，两侧和背面玫棕暗区。图标里的清楚双靴与穿戴实际腿壳高度分别记录。',
'L2腰120/352非零，像素组织约4高带；裤腿各160/224非零，纵向亮片和相邻棕暗边保留，裤和靴分别属于两层，不把一张图标当穿戴层完成。',
'正面、45°、90°侧、背、alpha黑剪影、灰模和60逐面矩形已查看；整体默认短甲体块，不因魔法名称增加羽冠、披风或尖肩。软件拼合交界的深度采样不作游戏接缝结论。',
'四JSON parent item/generated、单层layer0引用实际wizards_reborn:item/arcane_gold_*，无本批图标多层tint或模型override声明；源PNG均保留RGBA未改。',
'实际构造ArcaneArmorItem(ARCANE_GOLD,Type,Properties).addArcaneEnchantmentType(ARCANE_COLD)；类继承ArmorItem且无getArmorTexture/initializeClient/getArmorModel覆盖，hasCustomModel返回false。材质名返回wizards_reborn:arcane_gold；ItemSkin tooltip存在，基础显示不扩张到全部皮肤栈。']
app={'targets':['leather','hongmeng'],'target_files':[ref(R/n) for n in priority if any(f+'_' in n for f in ['leather','hongmeng']) and n.endswith('.png')],'current_pixel_evidence_reused':[ref(R/'docs/art/armor-bone-whole-20261112/current-target-readonly.png'),ref(R/'docs/art/armor-ra-atem-whole-20261112/current-target-readonly.png')],'observed':'皮甲棕皮/缝线和鸿蒙白金紫获选图标保持；当前输入哈希未变，不重复制作。','applicable_learning':'只学前大亮面/侧窄暗面、袖腕与负空间位置以及L1/L2的材质连续；普通装备不需装饰堆叠也能有清楚金属感。','reject':'不把皮革改玫金，不把鸿蒙白金改粉铜，不挪用原作者像素；材质相近不等于新完整设计。'}
study=write('semantic-review.json',{'batch':'D68','primary_whole_key':key,'source':prov,'actually_viewed':['native-pixels.png','whole-static-views.png','raw-uv-faces.png'],'observations':obs,'applications':app,'source_whole_designs':1,'new_validated_credit':0,'limits':limits})
reg=next((B/'source').rglob('WizardsRebornItems.java')).read_text();registrations=[l.strip() for l in reg.splitlines() if 'public static final' in l and ' ARCANE_GOLD_' in l and 'new ArcaneArmorItem(' in l];assert len(registrations)==4
models=read(B/'item-model-resolution.json');assert len(models)==4
bind=write('static-bindings.json',{'actual_registrations':registrations,'actual_mod_chain':'WizardsReborn @Mod MOD_ID -> constructor WizardsRebornItems.register(eventBus) -> ITEMS DeferredRegister.create(ForgeRegistries.ITEMS,MOD_ID) -> ITEMS.register(eventBus) and four explicit registry names/suppliers. No Valhelsia helper in this mod path.','actual_material':'WizardsRebornArmorMaterials.ARCANE_GOLD name arcane_gold, getName prefixes WizardsReborn.MOD_ID. Values and source preserved; no balance change.','actual_item_class':'ArcaneArmorItem extends ArmorItem implements IArcaneItem; no getArmorTexture/initializeClient/getArmorModel, hasCustomModel=false; ItemSkin tooltip and ArcaneEnchantment calls exist and remain separate conditions.','models':models,'consumer_comparison':ctx,'comparative_default_resource':'47.4.10 splits material namespace then uses wizards_reborn:textures/models/armor/arcane_gold_layer_2.png LEGS, layer1 all other slots; Forge texture hook can replace path. Not exact47.3.0/skin runtime proof.','comparative_default_pass':'Basic item not DyeableLeatherItem: one untinted base pass; optional trim/glint separate. Skin/custom enchantment extra effects excluded, no inherited 1.12.2 FFFFFFFF doublepass assumption.','comparative_pose':'PlayerRenderer -> LayerDefinitions inner.5/outer1 64x32 -> HumanoidArmorModel legs extend-.1 gives leggings.4 and boots.9; hat1.5. Layer parent copy and slot mask precede Forge model hook; IClientItemExtensions default returns original model.','mirror':'left arm/leg share source UV with mirrored geometry and quad order; inflation changes vertices, not texture rectangles.','slot_masks':read(B/'geometry-uv-context.json')['slot_masks'],'geometry':ref(B/'geometry-uv-context.json'),'alpha':ref(B/'uv-alpha-measurements.json'),'exact_dependency_and_skin_consumer_verified':False,'runtime_verified':False})
nearest=[g for g in ledger['groups'] if g['semantic_group'] in ['conductite_copper_dark_panels','mixed_copper_classical_helm','vanilla_outline_elemental_palette']]
dedup=write('dedup-comparison.json',{'prior':ref(P/'combined-semantic-ledger.json'),'nearest_saved_observations_reread':nearest,'comparison':'玫金亮面/暗边与已有原版轮廓材料族非常接近；Conductite暗裤分工和古典铜盔另有功能形态。ArcaneGold基础套较朴素，不能因为魔法材质名、四部位补全或颜色新增独立信用；待Main整体比较，保守不增215历史学习组。','not_repeated':'InventorWizard(D57)独立专用模型不再计；Tyr/Draco的固定MC消费者证据只复用，不算额外参考。','new_learning_groups':0,'new_validated_credit':0,'gate_met':False})
ledger['pending_whole_families'].append({'primary_whole_key':key,'review':study['path'],'sha256':study['sha256'],'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':limits});ledger['reviewed_pending_whole_keys'].append(key);ledger['current_batch_prior']=ref(P/'combined-semantic-ledger.json');ledger['current_batch_additional_D54_carry_credit']=0
assert ledger['groups']==before['groups'] and ledger['local_independently_accepted_whole_families']==before['local_independently_accepted_whole_families']
led=write('combined-semantic-ledger.json',ledger)
verify=write('verification.json',{'source_archive_entries_verified':len(prov['entries']),'different_version_context_entries_verified':len(ctx['entries']),'actual_item_models_resolved':4,'original_PNGs':6,'UV_rectangles_in_bounds':60,'protected_assets_unchanged':289,'priority_files_unchanged':70,'prior_D67_frozen_files_verified':len(oldfiles),'prior_D67_delivery':ref(P/'coordinator-delivery.json'),'D54_full_accepted_object_preserved':True,'historic215_groups_preserved':True,'exact_Forge47_3_0_and_ItemSkin_runtime_verified':False,'production_changes':0,'java_game_runs':0,'checklist_deletions':0,'valid_total':None,'exact_gap':None,'gate_met':False})
(B/'README.md').write_text('# D68 · Arcane Gold 基础整套原图与穿戴 UV\n\n固定 WizardsReborn commit `'+prov['commit']+'`。范围为未附加ItemSkin基础四槽；正式新增信用0，原生16px不代表压缩用户原稿。\n\n'+'\n\n'.join(obs)+'\n\n## 消费者边界\n\n模组注册DeferredRegister和四个ArcaneArmorItem构造/材质名已固定。实际依赖Forge47.3.0与FluffyFur0.3；本地同MC1.20.1 Forge47.4.10仅默认消费者比较，基础皮肤与额外附魔渲染未实机验证。\n\n## 应用原则\n\n皮甲不改玫金、鸿蒙白金紫图标保留；只学习大亮面/窄暗侧与L1袖胸和L2腿、L1靴的材质连续。\n\n'+'\n'.join('- '+x for x in limits)+'\n')
progress=write('progress.json',{'batch':'D68','updated_utc':now,'status':'BASE_WHOLE_PIXEL_UV_STUDY_DONE_EXACT_DEPENDENCY_SKIN_AND_MAIN_REVIEW_PENDING','key':key,'study':study,'bindings':bind,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0})
manifest={'schema':'D68.arcane_gold.base_whole.bounded.v1','updated_utc':now,'files':[ref(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]};raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(raw).hexdigest();rp=B/('bounded-receipt-'+h+'.json');assert not rp.exists();rp.write_bytes(raw)
delivery=write('coordinator-delivery.json',{'batch':'D68','key':key,'receipt':ref(rp),'study':study,'bindings':bind,'dedup':dedup,'verification':verify,'progress':progress,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0,'main_review_required':True,'pending':limits})
for f in manifest['files']:assert sha(f['path'])==f['sha256']
ptr=R/'docs/art/armor-continuation-20261102/progress.json';original=ptr.read_bytes();state=json.loads(original);assert state['latest_continuation']=='docs/art/armor-draco-whole-20261112/progress.json','pointer moved leave evidence only'
state.update(status='D68_ARCANE_GOLD_BASE_PIXEL_UV_DONE_DEPENDENCY_PENDING',latest_continuation=str((B/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((B/'combined-semantic-ledger.json').relative_to(R)),latest_arcane_gold_receipt=str(rp.relative_to(R)),latest_arcane_gold_delivery=delivery,latest_reference_gate_met=False)
assert ptr.read_bytes()==original;ptr.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'delivery':delivery,'frozen_files':len(manifest['files']),'protected':289,'priority':70},ensure_ascii=False))
