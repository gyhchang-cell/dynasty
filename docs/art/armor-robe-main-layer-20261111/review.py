from pathlib import Path
import json,hashlib,re,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-robe-piece-reference-20261111';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def src(n):return (D/'source'/n).read_text()
for file in ['provenance.json','mod-followup-provenance.json']:
 p=json.loads((D/file).read_text());assert H(Path(p['archive']))==p['archive_sha256']
 with zipfile.ZipFile(p['archive']) as z:
  for f in p['files']:
   assert H(D/f['path'])==f['sha256']==hashlib.sha256(z.read(f['entry'])).hexdigest()
   if 'disassembly' in f:assert H(D/f['disassembly'])==f['disassembly_sha256']
p=json.loads((D/'target-signature-provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:assert H(D/p['local'])==p['sha256']==hashlib.sha256(z.read(p['entry'])).hexdigest()
assert H(D/p['disassembly'])==p['disassembly_sha256']
forge=src('net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java');assert 'return p_117129_ == EquipmentSlot.LEGS;' in forge and 'String domain = "minecraft";' in forge
assert 'getArmorResource(p_117121_, itemstack, p_117122_, "overlay")' in forge and 'armoritem instanceof net.minecraft.world.item.DyeableLeatherItem' in forge
assert 's1 = net.minecraftforge.client.ForgeHooksClient.getArmorTexture' in forge
hooks=src('net/minecraftforge/client/ForgeHooksClient.java');assert 'return result != null ? result : _default;' in hooks
mix=(P/'bytecode/MixinArmorFeatureRenderer.txt').read_text();start=mix.index('  void immersiveArmors$injectRenderArmor(');end=mix.index('  public void immersiveArmors$render',start);cancel=mix[start:end];assert 'Field immersive_armors/Main.FORGE:Z' in cancel and 'instanceof' in cancel and 'ExtendedArmorItem' in cancel and 'CallbackInfo.cancel:' in cancel and 'cancellable=true' in cancel
common=(D/'CommonForge.txt').read_text();stat=common[common.index('  static {};'):];assert re.search(r'iconst_1\n[^\n]+putstatic[^\n]+Main.FORGE:Z',stat) and 'net.minecraftforge.fml.common.Mod(' in common
ref=json.loads(src('immersive_armors-common-refmap.json'))['mappings']['immersive_armors/mixin/MixinArmorFeatureRenderer'];sig=(D/'HumanoidArmorLayer-signatures.txt').read_text();targets=[]
for k,v in ref.items():
 method,desc=v.split(';',1)[1].split('(',1);desc='('+desc
 assert method+'(' in sig and 'descriptor: '+desc in sig
 targets.append({'source_selector':k,'mapped_target':v,'same_name_and_descriptor_in_cached_forge_srg':True})
material=(P/'bytecode/ExtendedArmorMaterial.txt').read_text();assert 'Field name:Ljava/lang/String;' in material
paths=[]
for slot in ['HEAD','CHEST','LEGS','FEET']:
 layer=2 if slot=='LEGS' else 1
 for overlay in [False,True]:
  rel=f'assets/minecraft/textures/models/armor/robe_layer_{layer}'+('_overlay' if overlay else '')+'.png';f=P/'source'/rel;assert Image.open(f).size==(64,32)
  paths.append({'slot':slot,'texture_if_regular_path_not_cancelled':'minecraft:'+rel.split('assets/minecraft/',1)[1],'sha256':H(f),'conditions':'Forge cancellation injection not active or FORGE flag false; does not prove actual selection'})
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert len(base)==289 and all(H(R/n)==h for n,h in base.items())
assert H(D/'texture-requirements-1a083176c885.md')==H(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==H(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
result={'scope':'D44 bounded conventional main-layer branch relation, not game acceptance','case':'immersive_armors:robe','source_context':'local cached Forge1.20.1-47.4.10; user live version not asserted','regular_source_paths':paths,'refmap_targets_checked':targets,'forge_cancellation_declared':True,'forge_flag_static_assignment_in_annotated_mod_class':True,'whole_relation':'FORGE=true + ExtendedArmorItem + applied injection -> cancel conventional armor path; own Piece list renders separately. If no cancellation, vanilla/Forge regular path uses LEGS L2 else L1 and DyeableLeatherItem base color + white overlay. Native files existence is not execution evidence.','d43_precision':'D43追加片消费者保持成立；常规4图不再当作Forge成功加载时的主层必用资产。旧冻结收据不改，本记录补充分支。','learning':['底图/覆盖层必须区分消费者与平台，不按文件名判使用','保留附加片和普通层的原始UV、材质分区，不把文件数算设计数','精确名称+描述符匹配只关闭静态目标存在缺口，不代表混入成功或穿戴实测'],'limits':['未执行游戏、加载器或混入转换，配置/冲突/生命周期效果未验','跨平台注册实现与实时资源包覆盖仍未验','第三方原图不复制到生产资源','source archive is generated local Forge cache, not attested upstream git tree'],'prior_source_pages_reused':3,'new_images_viewed':0,'new_design_credit':0,'name_families':654,'armor_name_families':640,'conservative_groups':215,'reference_gate_met':False,'protected_paths_unchanged':289,'production_changes':0,'game_starts':0,'checklist_deletions':0}
(D/'main-layer-branch-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS bounded main-layer branch / 2 refmap target signatures / 289 protected paths; actual runtime pending')
