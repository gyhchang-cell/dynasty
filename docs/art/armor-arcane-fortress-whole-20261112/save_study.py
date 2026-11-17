from pathlib import Path
import json,hashlib,shutil,re
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parents[2];P=R/'docs/art/armor-arcane-exact-consumer-20261112';OLD=R/'docs/art/armor-arcane-gold-whole-20261112'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=B/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return {'path':str(p),'sha256':h(p)}
# Preserve fixed dependency context with its original provenance, not an exact-version assertion.
D=R/'docs/art/armor-inventor-whole-20261112/dependency-context'
for n in ['ArmorModel.java','gradle.properties','provenance.json']:
 p=B/'dependency-context'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/n,p)
S=B/'source/src/main';J=S/'java/mod/maxbogomol/wizards_reborn';T=S/'resources/assets/wizards_reborn'
reg=(J/'registry/common/item/WizardsRebornItems.java').read_text();models=(J/'registry/client/WizardsRebornModels.java').read_text();item=(J/'common/item/equipment/ArcaneFortressArmorItem.java').read_text();alias=(B/'dependency-context/ArmorModel.java').read_text()
resolved=[]
for part in ['helmet','chestplate','leggings','boots']:
 id='arcane_fortress_'+part
 assert f'ITEMS.register("{id}", () -> new ArcaneFortressArmorItem' in reg
 m=T/f'models/item/{id}.json';d=json.loads(m.read_text());assert d=={'parent':'item/generated','textures':{'layer0':'wizards_reborn:item/'+id}}
 png=T/f'textures/item/{id}.png';im=Image.open(png).convert('RGBA');old=Image.open(OLD/f'source/src/main/resources/assets/wizards_reborn/textures/item/arcane_gold_{part}.png').convert('RGBA')
 resolved.append({'id':'wizards_reborn:'+id,'model':str(m),'model_sha256':h(m),'texture':str(png),'texture_sha256':h(png),'original_dimensions':im.size,'changed_RGBA_pixels_from_ArcaneGold':sum(a!=b for a,b in zip(im.getdata(),old.getdata()))})
assert 'ArcaneFortressArmorModel::createBodyLayer' in models and 'ArcaneFortressSlimArmorModel::createBodyLayer' in models
assert 'new ArcaneFortressSlimArmorModel(event.getEntityModels().bakeLayer(ARCANE_FORTRESS_SLIM_ARMOR_LAYER))' in models
assert 'if (skin != null) model = skin.getArmorModel' in item and 'if (skin != null) return skin.getArmorTexture' in item
assert 'model.slot = type.getSlot();' in item and 'model.copyFromDefault(original);' in item
geo=json.loads((B/'geometry-uv-context.json').read_text());assert all(len(g['boxes'])==18 and g['face_count']==108 for g in geo.values())
a=Image.open(T/'textures/models/armor/arcane_fortress.png').convert('RGBA');b=Image.open(T/'textures/models/armor/arcane_fortress_slim.png').convert('RGBA');diff=[(i%128,i//128) for i,(x,y) in enumerate(zip(a.getdata(),b.getdata())) if x!=y]
save('item-model-resolution.json',resolved)
save('static-bindings.json',{'entry':'@Mod constructor -> WizardsRebornItems.register(eventBus) -> DeferredRegister literal four ArcaneFortressArmorItem instances', 'material':'ARCANE_FORTRESS: durability30 defenses[3,8,6,3] enchant30 toughness2 knockback0.15; unchanged reference values', 'client_chain':['registerLayerDefinition standard/slim -> createBodyLayer 128x64','AddLayers bakes both; slim layer is instantiated through ArcaneFortressSlimArmorModel, inheriting the base ArmorModel aliases','initializeClient supplies getHumanoidArmorModel; non-default AbstractClientPlayer name selects slim; other entities default','ItemSkin may replace model; then slot and copyFromDefault plus setupAnim','getArmorTexture checks ItemSkin first; otherwise standard/slim same atlas for all four slots; no _layer_1/_layer_2 convention'], 'default_alias_context':{'path':str(B/'dependency-context/ArmorModel.java'),'sha256':h(B/'dependency-context/ArmorModel.java'),'exact_loaded_FluffyFur_0_3_verified':False,'slot_roots':geo['standard']['slot_roots'],'copyFromDefault':'body/pelvis from original body; leggings/feet from original legs; head and arms inherited HumanoidModel animation. No claim about arbitrary poses.'}, 'forge_hook_context':str(P/'exact-consumer-review.json'),'current_Dynasty_47_4_10_compatibility_verified':False,'skin_item_model_event':'WizardsRebornItemSkins modelBakeSkins ModifyBakingResult calls FluffyFurItemSkins.addSkinModel for all four IDs; original JSON has no override but cannot guarantee resulting baked item model', 'skin_branch_closed':False,'runtime_verified':False})
observations=[
 '四原生16x16物品图：闭合圆角阶梯盔顶、暗面孔，两角短方肩、短宽胸、两条直腿和两只高筒短靴；玫棕边框、铜金主面、淡黄亮片，保持原版比例，非人台图。',
 '普通/纤细128x64图集共用整体编排；两图仅40个RGBA像素不同，差异位于x85..111,y43..61护腕区域。不能把两种宽度算两套设计。',
 '盔内层头顶对应UP面为0/64透明，另一水平面64/64；正面42/64、背52/64，头外层正面18/64与背10/64给额边/后颈小片。只看完整头图不能推断所有六面被填满。',
 '胸体上下水平面均0/32，正面86/96、背82/96；亮胸片以大片水平黄金带分层，侧面40/48玫棕窄条。透明边口承担形状，非满方块衣料。',
 '双腿内层0.75膨胀，外片1.02；左右另给UV而不mirror，亮侧相向组织；外片正背仅10/48，边面4/48或16/48，不能把稀疏外甲误当缺图。',
 '护腕是与上臂同根的平级部件，两层0.72与1.02膨胀；普通宽4、纤细宽3。纤细上臂本体仍宽4，不能概括成整条手臂都缩为3。外护腕正背薄深边，内层亮黄腕带。',
 '护腰codpiece宽8高5深4、局部y7，随pelvis复制身体；正背24/40，水平面一面空另一面32/32。足甲12高底盒但侧面仅16/48着色，外观短靴依赖透明区。',
 '软件正/45/侧/背/灰/黑均已查看，紧凑肩与直腿可辨；层间交叉细点仅为双面软件深度诊断，不能宣称引擎接缝错误或完成穿戴验收。',
 '与D68奥术金甲共享玫金材料及紧凑原版图标语言，新增专用多壳体与独立护腕并不自动证明全新视觉家族；D57发明巫师则为暗棕平檐帽/衣裤套，虽共享别名机制不能混为同视觉套。',
]
pending=['Main独立整套语义去重与Dynasty优先盔甲适用性待审；新信用0。','精确加载FluffyFur0.3二进制/ItemSkin/FluffyFurItemSkins实现未固定；只证模组侧显式替换路径及D57提交上下文，不声称皮肤全闭环。','Forge47.3.0源码钩子是参考版本；不等于当前Dynasty47.4.10已兼容，Minecraft姿态/普通纤细体型/游戏光照深度/穿戴接缝未实测。','软件中立四槽并集没有玩家身体、动作、trim/glint、资源包和实际皮肤；不当实机或真人验收。','1000有效适用设计总数和准确缺口仍null，gate=false；289保护/70优先不改，主清单不删，D68旧缺口保留。']
review=save('semantic-review.json',{'batch':'D70','key':'wizards_reborn:arcane_fortress','observations':observations,'actually_viewed_pages':['native-pixels.png','whole-standard.png','whole-slim.png','raw-standard-1.png','raw-standard-2.png','raw-slim-1.png','raw-slim-2.png'],'prior_pages_actually_reviewed':[str(R/'docs/art/armor-inventor-whole-20261112/native-pixels-01.png'),str(OLD/'native-pixels.png')],'native_whole_candidate_families':1,'standard_slim_not_independent_designs':True,'new_validated_credit':0,'new_learning_groups':0,'pending':pending})
save('dedup-comparison.json',{'nearest':['wizards_reborn:arcane_gold','wizards_reborn:inventor_wizard','vanilla_outline_elemental_palette'], 'comparison':'ArcaneGold shares rose-gold material and vanilla silhouettes; Fortress thicker chest plates, dedicated outer leg/head shells and bracers are actually visible but not independently accepted. Inventor shares aliases not visual identity. Keep pending with zero additional historical groups.', 'icon_pixel_differences':[{'id':x['id'],'pixels':x['changed_RGBA_pixels_from_ArcaneGold']} for x in resolved],'slim_atlas_changed_pixels':len(diff),'slim_difference_bbox_inclusive':[min(x for x,y in diff),min(y for x,y in diff),max(x for x,y in diff),max(y for x,y in diff)],'new_credit':0})
ledger=json.loads((P/'combined-semantic-ledger.json').read_text());accepted=ledger['local_independently_accepted_whole_families'];assert 'wizards_reborn:arcane_fortress' not in ledger['reviewed_pending_whole_keys'];ledger['reviewed_pending_whole_keys'].append('wizards_reborn:arcane_fortress');ledger['pending_whole_families'].append({'primary_whole_key':'wizards_reborn:arcane_fortress','review':review['path'],'sha256':review['sha256'],'whole_slots':4,'new_validated_credit':0,'new_learning_groups':0,'pending':pending});assert ledger['local_independently_accepted_whole_families']==accepted
save('combined-semantic-ledger.json',ledger)
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text());priority={p:s for t in targets['targets'] for p,s in t['files'].items()}
for group in [base,priority]:
 for p,s in group.items():assert h(R/p)==s,p
prior=next(P.glob('bounded-receipt-*.json')); priorfiles=json.loads(prior.read_text())['files']
for f in priorfiles:assert h(f['path'])==f['sha256']
for f in json.loads((B/'provenance.json').read_text())['files']:assert h(f['path'])==f['sha256']
save('verification.json',{'source_archive_entries_verified':21,'protected_unchanged':len(base),'priority_unchanged':len(priority),'prior_D69_frozen_files_verified':len(priorfiles),'models_resolve':4,'original_PNGs':6,'standard_cuboids':18,'slim_cuboids':18,'faces_each':108,'all_face_bounds_inside_128x64':True,'D54_accepted_full_object_preserved':True,'runtime_verified':False,'new_credit':0,'production_changes':0})
save('progress.json',{'batch':'D70','status':'WHOLE_BASE_SOURCE_STUDY_SAVED_PENDING_INDEPENDENT_ACCEPTANCE','prior':str(P/'progress.json'),'review':review,'new_credit':0,'gate_met':False,'validated_total':None,'exact_gap':None,'production_changes':0,'pending':pending,'next':'thebetweenlands:syrmorite — next whole family source/UV study, not production authorization'})
(B/'README.md').write_text('D70 奥术堡垒甲：原生整套图标、普通/纤细穿戴UV研究\n\n实际查看4图标、2图集、普通/纤细各18体块108面，正面/45度/侧/背/灰模/黑剪影。原生PNG保持字节不变，诊断仅最近邻放大，不是游戏或Dynasty生产图。\n\n核对四注册ID、item/generated基础模型、两模型层注册/烘焙、分槽别名与ItemSkin显式替换。纤细仅护腕几何缩窄，图集40像素不同；不另计设计。与奥术金甲大幅共享材质/轮廓，Main独立去重待审，新信用0。精确依赖/皮肤实现及实机保留缺口，47.3.0钩子不代表47.4.10兼容。\n\n289保护与70优先均未变。未启动Java、不碰存档/Jar/提示词/主协调checkpoint。下一组继续Syrmorite原生整套消费研究，不提前生产。\n')
files=[{'path':str(p),'sha256':h(p)} for p in sorted(B.rglob('*')) if p.is_file() and not p.name.startswith('bounded-receipt-') and p.name!='coordinator-delivery.json'];data=(json.dumps({'schema':'D70.arcane_fortress.whole_source.v1','files':files},ensure_ascii=False,indent=2)+'\n').encode();digest=hashlib.sha256(data).hexdigest();receipt=B/f'bounded-receipt-{digest}.json';receipt.write_bytes(data)
save('coordinator-delivery.json',{'batch':'D70','receipt':{'path':str(receipt),'sha256':digest},'review':review,'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
print(json.dumps({'frozen_files':len(files),'receipt':str(receipt),'protected':len(base),'priority':len(priority)},ensure_ascii=False))
