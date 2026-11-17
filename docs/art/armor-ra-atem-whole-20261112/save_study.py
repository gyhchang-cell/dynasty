from pathlib import Path
import json,hashlib,zipfile,datetime,copy
R=Path.cwd(); B=R/'docs/art/armor-ra-atem-whole-20261112'; P=R/'docs/art/armor-amphibious-whole-20261112'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(n,d):
 p=B/n;assert not p.exists(),p;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return {'path':str(p),'sha256':sha(p)}
def ref(p):return {'path':str(p),'sha256':sha(p)}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();key='atum:ra_atem_ceremonial_family'
prov=read(B/'provenance.json');assert sha(prov['archive'])==prov['archive_sha256']
with zipfile.ZipFile(prov['archive']) as z:
 for n,h in prov['entries'].items():
  assert sha(B/'source'/n)==h
  matches=[x for x in z.namelist() if x.endswith('/'+n)];assert len(matches)==1 and hashlib.sha256(z.read(matches[0])).hexdigest()==h
base=read(R/'docs/art/armor-ars-reference-20261111/source-baseline.json')
assert len(base)==289
for n,h in base.items():assert sha(R/n)==h,n
priority=read(R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json');files={k:v for t in priority['targets'] for k,v in t['files'].items()};assert len(files)==70
for n,h in files.items():assert sha(R/n)==h,n
prev=read(P/'coordinator-delivery.json');assert sha(prev['receipt']['path'])==prev['receipt']['sha256'];oldreceipt=read(prev['receipt']['path'])
for row in oldreceipt['files']:assert sha(row['path'])==row['sha256'],row['path']
ledger=read(P/'combined-semantic-ledger.json');before=copy.deepcopy(ledger);assert not any(x.get('primary_whole_key')==key for x in ledger['pending_whole_families'])
limits=['独立整族去重与适用性审查待Main；本批信用0，不作1000完成声明。','精确Neo20.4.232实际二进制、事件注册、资源包及穿戴运行状态未验证。','ModelPart反编译上下文来自历史MCP/Forge缓存，不是NeoForm154220逐class同源证明；Neo补丁和扩展源码单独固定。','软件六视图为四槽并集与简化双面绑定姿势，不是游戏，不含实体皮肤、动作、光照、混穿、trim/glint或重复披片绘制。','零维原始尺寸不等于无厚度：Atem侧鳍与两套postiche存在deformation；零面积原始UV面不凭空补纹理。','Ra/Atem合一候选族；8部位、10PNG、64体块、384面及多角度不能拆计设计。','289保护与70优先文件未变；当前鸿蒙及朱砂图标保留，不据旧穿戴疑点自动取得重画资格。','1000有效适用总数与准确缺口仍null，gate=false，无制作覆盖、实机、主清单删除。']
observations=[
'两套原生四部位图标均16×16，穿戴图集各64×96；金属主块用黄、赭、深棕离散阶梯，Ra为胭脂红布，Atem为青绿布。图标与穿戴不是同一PNG。',
'胸部8×12×4主壳与倾斜胸片分开；原图金色V领和腰带在前后保持宽度，中心只少量宝石色。不是密集噪点或柔滑高光。',
'左右护臂以金色纵面、深棕腕带和肩部红/青块区分层次；外肩透明区裁出边缘，不是整块实心方肩。原图簇面积优先于细雕花。',
'长披片原始4×16×0，正背长布条与金色末梢；render copyFrom手臂后再绘制，不能按构造器异常pivot直接定位。',
'腿壳原始高15且有deformation，但图集透明区让可见金缘成为窄轨，内侧红/青布与外侧金甲区别明显；不能用box数量/高度代替像素面积。',
'靴为4×6×4主体加3×2×1趾片，金脚面与棕底条组成短靴；左右分别绑定腿的实际pose而非构造器共享原点。',
'Ra头顶有两片4×11×1长羽冠；Atem改成零X侧鳍并膨胀.1，两套面甲大金面、下颌小坠和头顶边层仍同族。差异没有把相同胸腿靴拆成两个完整设计。',
'正面清楚领、腹、腰、靴；45°显示斜胸片与肩层；侧面可见披片/腿壳厚度；背面长披条和V金领；灰模/黑剪影暴露高冠与长下摆过量，不能照搬普通MC轮廓。',
'Ra与Atem所有腿靴逐面图实际查看：腿外附片大面积透明，只剩红/青窄条和少量金点；靴前后多道金棕横带，趾上小亮面而非白色画布。',
'逐面矩形是源UV读取诊断；镜像在整套几何视图中处理，raw页不冒充最终屏幕朝向。所有原始PNG只读保留，未缩写运行资源。']
application={
 'hongmeng':{'name':'鸿蒙帝铠','read_only_files':[ref(R/n) for n in files if 'hongmeng_' in n and n.endswith('.png')], 'observed':'现有白主体、深紫内衬和金结构线；短宽胸、直腿、分靴已清楚。','apply_if_later_authorized':'仅研究金领/腰金块与有色内衬的面积分工；L1胸袖前后侧保持同一材质，L2腿内外边缘避免全部金化。保留当前白金紫获选图标。','reject':'Ra高羽冠、宽扇形面甲、长披片和全金腿靴不迁移，不改身体几何。'},
 'cinnabar':{'name':'朱砂符甲','read_only_files':[ref(R/n) for n in files if 'cinnabar_' in n and n.endswith('.png')], 'observed':'现有红布、米白符纸片、暗红接边和离散红符纹；头胸腿靴材料一致。','apply_if_later_authorized':'只借cloth与metal的层级方法，红布与符纸仍主材；L1袖背和胸侧、L2两腿接缝按原生UV核查，不把朱砂布误成金甲。','reject':'红色相似不代表材料身份相同；不复制神祇徽记/纹样、不增加金护肩或披风。'}}
study=write('semantic-review.json',{'batch':'D64','primary_whole_key':key,'source':prov,'actually_viewed':['native-ra.png','native-atem.png','whole-ra.png','whole-atem.png','raw-ra-1.png','raw-ra-2.png','raw-ra-3.png','raw-atem-1.png','raw-atem-2.png','raw-atem-3.png','current-target-readonly.png'],'observations':observations,'applications':application,'whole_candidate_families':1,'source_whole_sets':2,'new_validated_credit':0,'limits':limits})
consumer=R/'docs/art/armor-three-consumers-20261112/source/neo20.4.232'
context=R/'docs/art/armor-three-consumers-20261112/derived-source/net/minecraft/client/model/geom/ModelPart.java'
bindings=write('static-bindings.json',{'version':'Minecraft1.20.4 / NeoForge20.4.232 source only','item_chain':'AtumItems.ITEM_DEFERRED -> Atum modBus -> 8 named artifact items / HELMET,CHESTPLATE,LEGGINGS,BOOTS / NEBU -> RaArmor or AtemArmor -> ArtifactArmor -> TexturedArmorItem -> ArmorItem','inventory_models':{p.stem:read(p) for p in (B/'source/src/main/resources/assets/atum/models/item').glob('*.json')},'worn_chain':'initializeClient.getHumanoidArmorModel -> fresh bakeLayer RA_ARMOR/ATEM_ARMOR registered ClientHandler -> customModel(slot,hasFullSet) -> ArmorModel(HumanoidModel)','texture':'setHasRender=true -> TexturedArmorItem.getArmorTexture same <ra|atem>_armor.png all slots/type; not standard layer1/layer2 and not DyeableLeatherItem','actual_consumer':[ref(p) for p in [consumer/'patches/net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java.patch',consumer/'net/neoforged/neoforge/client/ClientHooks.java',consumer/'net/neoforged/neoforge/client/extensions/common/IClientItemExtensions.java']], 'context_only':ref(context),'context_limit':limits[2],'pose_visibility':'Neo parent copy and slot visibility before getArmorModelHook; IClientItemExtensions generic copies pose and 7 part visibility to replacement. Custom render overrides masks: head HEAD, body+arms CHEST, legs LEGS, boots FEET, hat false. Cape visible hasFullSet independently of slot.','copy_correction':{'left_cape':'left_arm','right_cape':'right_arm','left_boot':'left_leg','right_boot':'right_leg'},'full_set':'StackHelper compares four actual slot item objects against four specific family getters. No guessed NBT variant.','pass_limit':'Cape manually rendered whenever hasFullSet in each equipment model invocation; whole diagnostic union renders once, does not simulate up to four base invocations or trim/glint extra invocations. This is a static call-path risk, not observed runtime failure.','event_limit':'RenderPlayerEvent.Post visibility changes occur after player render; no claim they hide same-frame skin in advance. Atem constructor EVENT_BUS registration read, runtime effects untested.','model_algorithm':'AST parses constant arithmetic, UV/mirror/deformation/PartPose; hierarchy T*Rz*Ry*Rx; inflated cube vertices, mirror X swap + polygon order reversal. Actual custom cape/boot copyFrom applied before neutral rendering.','runtime_verified':False})
nearest=[g for g in ledger['groups'] if g['semantic_group'] in ['aether_valkyrie_white_gold_crown','simian_mask_banded_gold_plate']]
dedup=write('dedup-comparison.json',{'prior':ref(P/'combined-semantic-ledger.json'),'nearest_saved_observations_reread':nearest,'comparison':'Valkyrie已有白金层级与短冠，Wukong已有面罩金箍/横臂片/分裙长背带。Ra/Atem的神祇金面、V领和红青双披片可提供组合研究，但不是仅换色就独立；旧215组原图未在本批全部复看，独立性由Main审查。','internal_merge':'Ra/Atem胸腿靴与肩披片大量共用，头冠/侧鳍及布色不拆全套信用。','previous_inventor_excluded':'D57 armor-inventor-whole-20261112 already studied; not reopened as new design.','new_learning_groups':0,'new_validated_credit':0,'gate_met':False})
ledger['pending_whole_families'].append({'primary_whole_key':key,'review':study['path'],'sha256':study['sha256'],'source_sets':2,'whole_candidate_learning_families':1,'new_validated_credit':0,'new_learning_groups':0,'pending':limits})
ledger['reviewed_pending_whole_keys'].append(key);ledger['current_batch_prior']=ref(P/'combined-semantic-ledger.json');ledger['current_batch_additional_D54_carry_credit']=0
assert ledger['groups']==before['groups'] and ledger['local_independently_accepted_whole_families']==before['local_independently_accepted_whole_families']
led=write('combined-semantic-ledger.json',ledger)
verify=write('verification.json',{'archive_entries_verified':len(prov['entries']),'protected_assets_verified':len(base),'priority_files_verified':len(files),'prior_D63_receipt_files_verified':len(oldreceipt['files']),'prior_D63_delivery':ref(P/'coordinator-delivery.json'),'D54_full_accepted_object_preserved':True,'historic_215_groups_preserved':True,'original_rgba_production_changes':0,'software_pages_actually_viewed':11,'java_game_runs':0,'checklist_deletions':0,'gate_met':False,'validated_independent_total':None,'exact_gap':None,'scope':'source hashes and static texture/UV correspondence only'})
(B/'README.md').write_text('# D64 · Ra / Atem 整族原图与穿戴 UV 研究\n\n固定 Atum2 commit `'+prov['commit']+'`。两套合并一个待审族，新增有效信用 0。\n\n'+ '\n\n'.join(observations)+'\n\n## 消费链与限制\n\n见 static-bindings.json：Neo 20.4.232补丁/扩展和原生模型链分开固定，历史MCP几何上下文不冒充精确Neo二进制。披片和靴须应用运行copyFrom，四槽披片重复调用未在软件并集中模拟。\n\n## 对当前资源的用途\n\n鸿蒙白金紫图标、朱砂红布米白符纸图标只读保留。学习金属/布料材质主次；不照搬长羽冠、金面、全金腿靴或长披风，不制作和覆盖资产。\n\n'+ '\n'.join('- '+x for x in limits)+'\n\n只读核验289保护文件、70优先文件和此前D63全部冻结证据；未启动Java、游戏或操作存档。参考诊断图不是成稿/实机。\n')
progress=write('progress.json',{'updated_utc':now,'batch':'D64','status':'WHOLE_SOURCE_STUDY_DONE_INDEPENDENT_REVIEW_AND_RUNTIME_PENDING','key':key,'study':study,'bindings':bindings,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0})
manifest={'schema':'D64.whole.ra_atem.static.v1','updated_utc':now,'files':[ref(p) for p in sorted(B.rglob('*')) if p.is_file()]}
raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(raw).hexdigest();rp=B/('bounded-receipt-'+h+'.json');assert not rp.exists();rp.write_bytes(raw)
delivery=write('coordinator-delivery.json',{'batch':'D64','key':key,'receipt':ref(rp),'study':study,'bindings':bindings,'dedup':dedup,'verification':verify,'progress':progress,'ledger':led,'new_credit':0,'gate_met':False,'production_changes':0,'main_review_required':True,'pending':limits})
for row in manifest['files']:assert sha(row['path'])==row['sha256']
ptr=R/'docs/art/armor-continuation-20261102/progress.json';original=ptr.read_bytes();state=json.loads(original)
assert state['latest_continuation']=='docs/art/armor-amphibious-whole-20261112/progress.json','pointer moved; leave evidence, no overwrite'
state.update(status='D64_WHOLE_RA_ATEM_SOURCE_DONE_GATE_PENDING',latest_continuation=str((B/'progress.json').relative_to(R)),latest_combined_semantic_ledger=str((B/'combined-semantic-ledger.json').relative_to(R)),latest_ra_atem_whole_receipt=str(rp.relative_to(R)),latest_ra_atem_delivery=delivery,latest_reference_gate_met=False)
assert ptr.read_bytes()==original,'concurrent pointer mutation';ptr.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'delivery':delivery,'frozen_files':len(manifest['files']),'protected':289,'priority':70,'prior_receipt_verified':len(oldreceipt['files'])},ensure_ascii=False))
