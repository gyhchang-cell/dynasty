"""Freeze reference evidence. Runtime assets, Java and task checklists are untouched."""
from pathlib import Path
import json,hashlib,shutil,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=R/'docs/art/armor-bone-whole-20261112';PRIOR=R/'docs/art/armor-syrmorite-whole-20261112'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):
 p=B/n;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return {'path':str(p),'sha256':h(p)}
prov=json.loads((B/'provenance.json').read_text())
with zipfile.ZipFile(prov['archive']) as z:
 assert h(prov['archive'])==prov['sha256']
 for f in prov['files']:assert hashlib.sha256(z.read(f['entry'])).hexdigest()==f['sha256']==h(f['path'])
# Reuse already fixed legacy consumers; verify bytes instead of executing Java again.
context=[]
for p in sorted((OLD/'context').iterdir()):
 if p.is_file():
  q=B/'context'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);assert h(p)==h(q);context.append({'source':str(p),'source_sha256':h(p),'copy':str(q)})
save('context-provenance.json',{'reuse_from':str(OLD/'context-provenance.json'),'reuse_from_sha256':h(OLD/'context-provenance.json'),'files':context,'legacy_scope':'MC1.12.2 + Forge2773 fixed context from D65, not current Dynasty1.20.1 consumer or compatibility proof','java_executed':False})
S=B/'source/src/main';J=S/'java/thebetweenlands';T=S/'resources/assets/thebetweenlands'
item=(J/'common/item/armor/ItemValoniteArmor.java').read_text();parent=(J/'common/item/armor/ItemBLArmor.java').read_text();reg=(J/'common/registries/ItemRegistry.java').read_text();gem=(J/'common/capability/circlegem/CircleGemHelper.java').read_text()
assert 'ARMOR_VALONITE, 3, slot, "valonite"' in item
assert 'getArmorModel' not in item+parent and 'getColor' not in item+parent and 'hasOverlay' not in item+parent
assert 'EntityEquipmentSlot.LEGS' in parent and 'texture2' in parent and 'type' in parent
assert 'nbt.hasKey(ITEM_GEM_NBT_TAG, Constants.NBT.TAG_INT)' in gem
resolved=[]
for part,slot in [('helmet','HEAD'),('chestplate','CHEST'),('leggings','LEGS'),('boots','FEET')]:
 assert f'VALONITE_{part.upper()} = new ItemValoniteArmor(EntityEquipmentSlot.{slot})' in reg
 p=T/f'models/item/valonite_{part}.json';d=json.loads(p.read_text());assert [x['predicate']['gem'] for x in d['overrides']]==[1,2,3]
 for suffix in ['', '_aqua_gem','_crimson_gem','_green_gem']:
  q=T/f'models/item/valonite_{part}{suffix}.json';m=json.loads(q.read_text());assert m['parent']=='item/generated';tex=T/'textures'/(m['textures']['layer0'].split(':')[1]+'.png');assert tex.exists();resolved.append({'id':'thebetweenlands:valonite_'+part,'variant':suffix or 'base','model':str(q),'model_sha256':h(q),'texture':str(tex),'texture_sha256':h(tex)})
alpha=json.loads((B/'uv-alpha-measurements.json').read_text());assert len(alpha)==240
geo=json.loads((B/'geometry-uv-context.json').read_text());assert len(geo['boxes'])==10
save('item-model-resolution.json',resolved)
save('static-bindings.json',{'source_chain':'TheBetweenlands.preInit -> REGISTRIES.preInit -> ItemRegistry.preInit reflected four VALONITE fields -> lower-case field names Locale.ENGLISH -> thebetweenlands registry namespace -> Register<Item> registers ITEMS', 'inventory':'ClientProxy registerDefaultItemRenderer/getItemModelMap selects meta0 registryName#inventory; sixteen original JSONs resolved. CircleGemHelper gem property reads Gem integer IDs1/2/3; NONE0 default.', 'worn':'ItemValoniteArmor -> ItemBLArmor -> ItemArmor; no custom model/getColor/hasOverlay override. Same fixed legacy default geometry chain as D65, not Bone textures or material.', 'texture':'valonite_1 for HEAD/CHEST/FEET, valonite_2 LEGS; constructor sets Aqua/Crimson/Green per-gem overrides to both paths. type argument ignored, does not force overlay.', 'passes':'Nonleather ItemArmor default16777215=0x00FFFFFF, Forge2773 hasOverlay false: one untinted base and optional separate glint. Do not inherit Item3DArmor -1 double-pass conclusion.', 'gem_applicability':'ItemArmor and not ItemAmphibiousArmor passes isApplicable; getter/model routing verified statically, gameplay attachment/acquisition not tested.', 'geometry':'legacy outer1/inner0.5; legs have no modern -.1 adjustment; hat1.5. Mirror swaps geometryX and reverses UV corner ordering; 64x32 original atlas. Neutral four-slot diagnostic only.', 'consumer_provenance':str(B/'context-provenance.json'), 'legacy_exact_source_not_current_runtime':True,'game_verified':False})
observations=[
 '四原生16x16物品图深紫轮廓、浅紫金属面与小片白高光；头盔为纵向中央面片/两侧颊片，胸有浅色V领与暗腰分界，直裤和短底双靴保持基础轮廓。',
 '基础L1/L2原生64x32；整体浅紫白，胸正背横向板带，深紫关节和腕部留白形成分段。局部小格高光偏密、全套偏浅，只借主/侧面面积与透明分段，不照搬成大片粉白或噪点。',
 '头256/384像素非零，正36/64背54/64，左右51/64，水平UP面透明，另一面64/64；hat全384像素透明。不能把图集空头顶当图标可见轮廓缺失，也不拿同构开口另计设计。',
 '胸264/352，正86/96背92/96，两侧43/48，上下水平面透明；双臂各126/224，侧面有34/48与24/48差异，正背26/48，衣袖与腕段由透明区分开。',
 '双靴各100/224，前24/48后18/48、两侧21/48；腰120/352，双腿各160/224。腿腰按默认内层0.5，靴按默认外层1，不套用现代腿部减0.1。',
 '三个宝石变体只改变额心、胸前、腕侧、膝和靴胫节点的蓝白/红/绿，基本浅紫甲保持；四套配色、十六图标与八图集只作同一候选家族，不拆独立设计。',
 '实际看过基础60面、八张图集、四变体正/45/侧/背/黑/灰；软件图的层交叉斑点不作引擎故障，身体/姿态/真实光照和游戏接缝未验。',
 '与D71 Syrmorite共享默认体型、宝石路由与大量材料甲分区；Valonite头面纵条、袖腕空区和胸背亮片有差异，但不因此判新独立视觉家族。与D65骨甲的骨白绿根/肋负形区别明确，消费者共享不等于设计信用。',
 '本批实际复看七家族当前运行PNG，精确记录28注册ID/70文件哈希；四家族图标千像素原稿、三家族32px历史稿，穿戴图均64x32。低阶简洁不等于简陋，未确证任何从未改过且可直接重画ID。',
]
pending=['Main独立整套语义去重/与Dynasty旧简盔甲适用性待审，新信用0；四件、24PNG、四变体、60基础面与多角度不拆计设计。','Legacy1.12.2/Forge2773源码/反编译上下文只支持参考绑定；不是当前Dynasty47.4.10兼容验证，不含实际加载模组/其他全局替换。','宝石NBT与模型路径静态成立，不等于真实原生获取、安装和游玩验证；此轮不启动Java或游戏。','软件诊断无身体/姿态/光照/OpenGL/资源包/附魔闪光和游戏接缝；四槽中立并集不当实机或真人验收。','有效适用1000总数与精确缺口仍null，gate=false；原稿与289保护/70优先不变，不删主清单/提示词。']
review=save('semantic-review.json',{'batch':'D72','key':'thebetweenlands:valonite','observations':observations,'actually_viewed_pages':['native-all-icons.png','native-all-atlases.png','raw-uv-faces.png','whole-all-variants.png'],'comparison_page_actually_viewed':str(R/'docs/art/armor-syrmorite-whole-20261112/native-all-icons.png'), 'current_Dynasty_page_actually_viewed':'current-target-readonly.png', 'target_qualification':str(B/'current-target-status.json'),'whole_candidate_families':1,'original_icons':16,'original_worn_atlases':8,'raw_base_faces_viewed':60,'all_variant_face_measurements':240,'new_validated_credit':0,'new_learning_groups':0,'runtime_accepted':False,'pending':pending})
save('dedup-comparison.json',{'nearest':['vanilla_outline_elemental_palette','thebetweenlands:syrmorite','thebetweenlands:bone'],'observations':['Valonite and Syrmorite share default geometry and Gem machinery; pale-purple material, face stripe and split cuffs alone do not establish an independently accepted whole family.','Bone rib/green-root identity differs, but same consumer machinery is not another design.','Three gem palettes remain variants; new learning groups and validated design credit remain zero.'],'new_validated_credit':0})
ledger=json.loads((PRIOR/'combined-semantic-ledger.json').read_text());old_accepted=ledger['local_independently_accepted_whole_families'];assert 'thebetweenlands:valonite' not in ledger['reviewed_pending_whole_keys'];ledger['reviewed_pending_whole_keys'].append('thebetweenlands:valonite');ledger['pending_whole_families'].append({'primary_whole_key':'thebetweenlands:valonite','review':review['path'],'sha256':review['sha256'],'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':pending});assert ledger['local_independently_accepted_whole_families']==old_accepted
save('combined-semantic-ledger.json',ledger)
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text());priority={p:s for t in targets['targets'] for p,s in t['files'].items()}
for group in [base,priority]:
 for p,s in group.items():assert h(R/p)==s,p
for folder in [OLD,PRIOR]:
 receipt=next(folder.glob('bounded-receipt-*.json'))
 for f in json.loads(receipt.read_text())['files']:assert h(f['path'])==f['sha256']
save('verification.json',{'archive_entries_verified':len(prov['files']),'copied_fixed_consumer_files':len(context),'prior_frozen_D65_and_D71_verified':True,'protected_unchanged':len(base),'priority_unchanged':len(priority),'base_models_with_3_overrides':4,'resolved_models':16,'native_icons':16,'native_atlases':8,'default_cubes':10,'UV_faces_measured':len(alpha),'all_bounds_inside64x32':True,'new_credit':0,'production_changes':0,'game_verified':False,'D54_accepted_full_object_preserved':True})
save('progress.json',{'batch':'D72','status':'WHOLE_BASE_AND_GEM_SOURCE_STUDY_SAVED_PENDING_MAIN_ACCEPTANCE','prior':str(PRIOR/'progress.json'),'review':review,'pending':pending,'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'production_changes':0,'target_status':str(B/'current-target-status.json'),'confirmed_old_crude_redraw_IDs':[], 'next_scope':'Continue actual related unfinished whole references; keep old-crude qualification unresolved rather than redraw protected historical work.'})
(B/'README.md').write_text('D72 Valonite整套原图/穿戴UV与Dynasty目标资格断点\n\n实际检查16原生图标、8穿戴图集、基础60面与四变体多角度；240面度量及52份源文件逐字节核验。复用已固定1.12.2/Forge2773消费者，非当前Dynasty兼容或实机验证。与Syrmorite共享原版甲与Gem机制，正式新增设计信用0，不将换色/组件/文件数凑成1000。\n\ncurrent-target-status.json逐项列出七家族28个精确ID、70份图标/模型/穿戴文件原尺寸与哈希、历史状态与可复用参考证据。全部289保护文件保持。当前未确证任何从未改过且简陋的可直接重画ID；旧静态UV/材质或比例疑点仍待独立核验，不能据此重画认可原稿。current-target-readonly.png仅诊断缩略，大原稿不缩16、不量化、不覆盖。\n\nD54旧验收与D70/D71研究保留；1000有效适用总数/精确缺口未知，gate=false。无Java/游戏、实例/存档/Jar/主清单改动。\n')
files=[{'path':str(p),'sha256':h(p)} for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('bounded-receipt-') and p.name!='coordinator-delivery.json'];data=(json.dumps({'schema':'D72.valonite.whole_source.v1','files':files},ensure_ascii=False,indent=2)+'\n').encode();digest=hashlib.sha256(data).hexdigest();receipt=B/f'bounded-receipt-{digest}.json';receipt.write_bytes(data)
save('coordinator-delivery.json',{'batch':'D72','receipt':{'path':str(receipt),'sha256':digest},'review':review,'verification':{'path':str(B/'verification.json'),'sha256':h(B/'verification.json')},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
print(json.dumps({'frozen_files':len(files),'receipt':str(receipt),'protected':len(base),'priority':len(priority)}))
