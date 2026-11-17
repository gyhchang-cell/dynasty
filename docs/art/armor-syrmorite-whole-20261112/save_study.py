"""Freeze reference evidence. Runtime assets, Java and task checklists are untouched."""
from pathlib import Path
import json,hashlib,shutil,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=R/'docs/art/armor-bone-whole-20261112';PRIOR=R/'docs/art/armor-arcane-fortress-whole-20261112'
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
item=(J/'common/item/armor/ItemSyrmoriteArmor.java').read_text();parent=(J/'common/item/armor/ItemBLArmor.java').read_text();reg=(J/'common/registries/ItemRegistry.java').read_text();gem=(J/'common/capability/circlegem/CircleGemHelper.java').read_text()
assert 'ARMOR_SYRMORITE, 3, slot, "syrmorite"' in item
assert 'getArmorModel' not in item+parent and 'getColor' not in item+parent and 'hasOverlay' not in item+parent
assert 'EntityEquipmentSlot.LEGS' in parent and 'texture2' in parent and 'type' in parent
assert 'nbt.hasKey(ITEM_GEM_NBT_TAG, Constants.NBT.TAG_INT)' in gem
resolved=[]
for part,slot in [('helmet','HEAD'),('chestplate','CHEST'),('leggings','LEGS'),('boots','FEET')]:
 assert f'SYRMORITE_{part.upper()} = new ItemSyrmoriteArmor(EntityEquipmentSlot.{slot})' in reg
 p=T/f'models/item/syrmorite_{part}.json';d=json.loads(p.read_text());assert [x['predicate']['gem'] for x in d['overrides']]==[1,2,3]
 for suffix in ['', '_aqua_gem','_crimson_gem','_green_gem']:
  q=T/f'models/item/syrmorite_{part}{suffix}.json';m=json.loads(q.read_text());assert m['parent']=='item/generated';tex=T/'textures'/(m['textures']['layer0'].split(':')[1]+'.png');assert tex.exists();resolved.append({'id':'thebetweenlands:syrmorite_'+part,'variant':suffix or 'base','model':str(q),'model_sha256':h(q),'texture':str(tex),'texture_sha256':h(tex)})
alpha=json.loads((B/'uv-alpha-measurements.json').read_text());assert len(alpha)==240
geo=json.loads((B/'geometry-uv-context.json').read_text());assert len(geo['boxes'])==10
save('item-model-resolution.json',resolved)
save('static-bindings.json',{'source_chain':'TheBetweenlands.preInit -> REGISTRIES.preInit -> ItemRegistry.preInit reflected four SYRMORITE fields -> lower-case field names Locale.ENGLISH -> thebetweenlands registry namespace -> Register<Item> registers ITEMS', 'inventory':'ClientProxy registerDefaultItemRenderer/getItemModelMap selects meta0 registryName#inventory; sixteen original JSONs resolved. CircleGemHelper gem property reads Gem integer IDs1/2/3; NONE0 default.', 'worn':'ItemSyrmoriteArmor -> ItemBLArmor -> ItemArmor; no custom model/getColor/hasOverlay override. Same fixed legacy default geometry chain as D65, not Bone textures or material.', 'texture':'syrmorite_1 for HEAD/CHEST/FEET, syrmorite_2 LEGS; constructor sets Aqua/Crimson/Green per-gem overrides to both paths. type argument ignored, does not force overlay.', 'passes':'Nonleather ItemArmor default16777215=0x00FFFFFF, Forge2773 hasOverlay false: one untinted base and optional separate glint. Do not inherit Item3DArmor -1 double-pass conclusion.', 'gem_applicability':'ItemArmor and not ItemAmphibiousArmor passes isApplicable; getter/model routing verified statically, gameplay attachment/acquisition not tested.', 'geometry':'legacy outer1/inner0.5; legs have no modern -.1 adjustment; hat1.5. Mirror swaps geometryX and reverses UV corner ordering; 64x32 original atlas. Neutral four-slot diagnostic only.', 'consumer_provenance':str(B/'context-provenance.json'), 'legacy_exact_source_not_current_runtime':True,'game_verified':False})
observations=[
 '四原生16x16图标紧凑：深蓝轮廓、亮钴蓝面、左上少量白蓝高光；胸甲短宽、盔下两颊开口、裤腿直、靴筒长且成对。没有把整套画成人台。',
 '基础穿戴图L1/L2原生64x32；蓝紫金属面混有密集小格明暗，胸前斜向亮带、腰与关节深蓝分区。借鉴少量亮面和关节分工，不把其密集斑点照搬到用户要求的大像素簇。',
 '头六面非零226/384；正38/64背52/64、顶部对应UP空，侧36/64。hat仅WEST有1个非零像素，其余五面空；如实记录，不将参考原图散点当已授权修复目标。',
 '胸222/352，正76/96背74/96，左右36/48，上下水平面透明；双臂各96/224，肩顶16/16，边带侧20/48。',
 '双靴各108/224，前28/48后18/48；腰120/352，腿各160/224。左右共用UV镜像，膝前及侧边亮蓝，正背保持不同甲片面积。',
 'Aqua/Crimson/Green只给额心、胸腰前、靴胫与双膝加宝石：图标中的白蓝/红/绿小块对应实际穿戴位置，背面大体保持基底。原生变体三套纹理不是额外独立设计。',
 '四变体均实际查看正/45/侧/背/黑/灰软件页；底层仍是原版方体比例。细小交叉点来自软件双面层深度近似，不声称实机接缝故障。',
 'D65骨甲同用默认几何与宝石路由，但骨白绿根和肋状负形不同；Syrmorite更接近原版金属甲蓝色材质族。共享消费者不证明共享视觉设计，蓝色名也不证明新设计。',
]
pending=['Main独立整套语义去重/与Dynasty旧简盔甲适用性待审，新信用0；四件、24PNG、四变体、60基础面与多角度不拆计设计。','Legacy1.12.2/Forge2773源码/反编译上下文只支持参考绑定；不是当前Dynasty47.4.10兼容验证，不含实际加载模组/其他全局替换。','宝石NBT与模型路径静态成立，不等于真实原生获取、安装和游玩验证；此轮不启动Java或游戏。','软件诊断无身体/姿态/光照/OpenGL/资源包/附魔闪光和游戏接缝；四槽中立并集不当实机或真人验收。','有效适用1000总数与精确缺口仍null，gate=false；原稿与289保护/70优先不变，不删主清单/提示词。']
review=save('semantic-review.json',{'batch':'D71','key':'thebetweenlands:syrmorite','observations':observations,'actually_viewed_pages':['native-all-icons.png','native-all-atlases.png','raw-uv-faces.png','whole-all-variants.png'],'comparison_page_actually_viewed':str(OLD/'native-pixels.png'),'whole_candidate_families':1,'original_icons':16,'original_worn_atlases':8,'raw_base_faces_viewed':60,'all_variant_face_measurements':240,'new_validated_credit':0,'new_learning_groups':0,'runtime_accepted':False,'pending':pending})
save('dedup-comparison.json',{'nearest':['vanilla_outline_elemental_palette','thebetweenlands:bone'],'observations':['Original compact vanilla geometry with blue mineral material is conservative overlap with existing material-variant group; no independent new group claimed.','Bone has pale bone ribs and green roots; same Gem override mechanism is reused technology, not additional semantic credit.','Three gem palettes remain same armor with localized colored sockets, not three whole designs.'],'new_validated_credit':0})
ledger=json.loads((PRIOR/'combined-semantic-ledger.json').read_text());old_accepted=ledger['local_independently_accepted_whole_families'];assert 'thebetweenlands:syrmorite' not in ledger['reviewed_pending_whole_keys'];ledger['reviewed_pending_whole_keys'].append('thebetweenlands:syrmorite');ledger['pending_whole_families'].append({'primary_whole_key':'thebetweenlands:syrmorite','review':review['path'],'sha256':review['sha256'],'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':pending});assert ledger['local_independently_accepted_whole_families']==old_accepted
save('combined-semantic-ledger.json',ledger)
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text());priority={p:s for t in targets['targets'] for p,s in t['files'].items()}
for group in [base,priority]:
 for p,s in group.items():assert h(R/p)==s,p
for folder in [OLD,PRIOR]:
 receipt=next(folder.glob('bounded-receipt-*.json'))
 for f in json.loads(receipt.read_text())['files']:assert h(f['path'])==f['sha256']
save('verification.json',{'archive_entries_verified':len(prov['files']),'copied_fixed_consumer_files':len(context),'prior_frozen_D65_and_D70_verified':True,'protected_unchanged':len(base),'priority_unchanged':len(priority),'base_models_with_3_overrides':4,'resolved_models':16,'native_icons':16,'native_atlases':8,'default_cubes':10,'UV_faces_measured':len(alpha),'all_bounds_inside64x32':True,'new_credit':0,'production_changes':0,'game_verified':False,'D54_accepted_full_object_preserved':True})
save('progress.json',{'batch':'D71','status':'WHOLE_BASE_AND_GEM_SOURCE_STUDY_SAVED_PENDING_MAIN_ACCEPTANCE','prior':str(PRIOR/'progress.json'),'review':review,'pending':pending,'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'production_changes':0,'next_unfinished_reference':'thebetweenlands:valonite — whole family not yet examined; do not treat as an independent design until actual visual comparison'})
(B/'README.md').write_text('D71 Syrmorite整套原图/穿戴UV研究\n\n实际查看16原生图标、8穿戴图集，基础60面及四变体正/45/侧/背/灰/黑诊断；测量全部240变体面。52份固定源码/原图从原归档逐字节校验，复用D65固定消费者，不运行Java。\n\n四注册ID、原生Gem整数路由、16模型声明、两穿戴路径及三个变体均已静态核对。默认非皮革ItemArmor走单基础pass，不沿用Item3DArmor的双pass。依赖上下文仅是1.12.2参考，不冒充Dynasty1.20.1兼容或游戏验收。\n\n原版轮廓蓝色矿物甲与已有材质族重合，三宝石只为变体，正式新增信用0。保持D54及所有旧研究不清零；289保护/70优先不动，不改运行图、存档/Jar/提示词/主清单。\n')
files=[{'path':str(p),'sha256':h(p)} for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('bounded-receipt-') and p.name!='coordinator-delivery.json'];data=(json.dumps({'schema':'D71.syrmorite.whole_source.v1','files':files},ensure_ascii=False,indent=2)+'\n').encode();digest=hashlib.sha256(data).hexdigest();receipt=B/f'bounded-receipt-{digest}.json';receipt.write_bytes(data)
save('coordinator-delivery.json',{'batch':'D71','receipt':{'path':str(receipt),'sha256':digest},'review':review,'verification':{'path':str(B/'verification.json'),'sha256':h(B/'verification.json')},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
print(json.dumps({'frozen_files':len(files),'receipt':str(receipt),'protected':len(base),'priority':len(priority)}))
