"""D69: bounded source supplement only; never edits runtime assets."""
from pathlib import Path
import json, hashlib, zipfile, re, datetime

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'docs/art/armor-arcane-gold-whole-20261112'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def put(name, value):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
    if p.exists():
        assert p.read_bytes() == data, f'Existing evidence differs: {p}'
    else:
        p.write_bytes(data)
    return {'path': str(p), 'sha256': sha(data)}

def checked_baselines():
    baseline = json.loads((ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
    targets = json.loads((ROOT/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text())
    priority = {p:h for t in targets['targets'] for p,h in t['files'].items()}
    for mapping in [baseline, priority]:
        for p,h in mapping.items():
            assert sha((ROOT/p).read_bytes()) == h, p
    return {'protected_files_unchanged': len(baseline), 'priority_files_unchanged':len(priority)}

checks = checked_baselines()
prior_receipt = next(PRIOR.glob('bounded-receipt-*.json'))
prior_files = json.loads(prior_receipt.read_text())['files']
for f in prior_files:
    assert sha(Path(f['path']).read_bytes()) == f['sha256'], f['path']
checks['prior_frozen_files_verified'] = len(prior_files)

archive = ROOT/'docs/art/bestiary-v43/qimen-research-20261030/batch-08/source-archives/forge-47.3.0-sources.zip'
provenance = archive.parent.parent/'native-source-provenance.json'
origin = next(x for x in json.loads(provenance.read_text())['artifacts'] if x['version']=='forge-47.3.0' and 'sources.jar' in x['artifact'])
assert hashlib.sha1(archive.read_bytes()).hexdigest() == origin['sha1']
names = [
 'patches/net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java.patch',
 'patches/net/minecraft/world/item/ArmorItem.java.patch',
 'net/minecraftforge/client/ForgeHooksClient.java',
 'net/minecraftforge/client/extensions/common/IClientItemExtensions.java',
 'net/minecraftforge/common/extensions/IForgeItem.java',
]
copied = []
with zipfile.ZipFile(archive) as z:
    sources = {n:z.read(n) for n in names}
    for n,data in sources.items():
        copied.append({'entry':n, **put('exact-forge/'+n,data)})
put('source-provenance.json', {'archive':str(archive),'sha256':sha(archive.read_bytes()),'sha1_verified_against_existing_provenance':origin['sha1'], 'source_url':origin['artifact'], 'existing_provenance':str(provenance),'existing_provenance_sha256':sha(provenance.read_bytes()),'entries':copied, 'executed':False,'reading_scope':'HumanoidArmorLayer patch full; ArmorItem patch full; other files armor/model extension methods and default resolution only. Copied full files do not mean full-file review.'})

layer = sources[names[0]].decode()
hooks = sources[names[2]].decode()
ext = sources[names[3]].decode()
item = sources[names[4]].decode()
assert 'instanceof net.minecraft.world.item.DyeableLeatherItem' in layer
assert 'getArmorModelHook(p_117121_, itemstack' in layer
assert 'type == null ?' in layer and 'm_117128_(slot) ? 2 : 1' in layer
assert 'ForgeHooksClient.getArmorTexture(entity, stack, s1, slot, type)' in layer
assert 'return result != null ? result : _default;' in hooks
assert 'return IClientItemExtensions.of(itemStack).getGenericArmorModel' in hooks
assert 'instanceof IClientItemExtensions e ? e : DEFAULT' in ext
assert re.search(r'default String getArmorTexture\([^)]*\)\s*\{\s*return null;',item)
old_layer = (PRIOR/'context/net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java').read_text()
assert 'DyeableLeatherItem' in old_layer and 'getArmorModelHook' in old_layer
assert 'getArmorResource' in old_layer and 'ForgeHooksClient.getArmorTexture' in old_layer
findings = [
 {'claim':'slot validation and copied slot visibility precede Forge model callback','evidence':names[0], 'scope':'exact Forge added patch, SRG-named base context'},
 {'claim':'DyeableLeatherItem selects tinted base plus white overlay; ordinary armor selects one white base','evidence':names[0], 'scope':'same branch semantics as D68 context; not pixel/render equivalence'},
 {'claim':'namespace split; LEGS layer2, other armor layer1; optional overlay suffix; per-item hook before cache','evidence':names[0], 'scope':'exact resource selection source'},
 {'claim':'texture hook accepts item override and falls back to computed default on null','evidence':[names[2],names[4]], 'scope':'Forge defaults only; third-party mixins not excluded'},
 {'claim':'model callback selects IClientItemExtensions; default returns original; replacements copy model properties','evidence':[names[2],names[3]], 'scope':'exact Forge extension path, no guarantee third-party registration absent'},
 {'claim':'trim and glint call the selected Model in the active patched path','evidence':names[0], 'scope':'source call path, not actual draw/trim/glint validation'},
]
pending = [
 '精确47.3.0包为Forge源码与补丁，不包含完整已映射Minecraft几何源码；D68的64x32/膨胀量仍是47.4.10比较上下文，不能提升为精确几何验收。',
 'FluffyFur0.3的ItemSkin实现、全局重定向和实际加载二进制未固定；D57三份依赖上下文不等于此闭环。',
 '不证明所有NBT物品栈、资源包、整套叠加、动作及游戏画面一致，不增加设计独立性信用。',
 '1000适用有效参考总数与准确缺口未知；生产门槛仍未通过，Main独立去重验收待办保留。',
]
put('exact-consumer-review.json',{'batch':'D69','supplements':'D68','findings':findings,'version_gap_narrowed':True,'all_D68_gaps_closed':False,'pending':pending,'local_dependency_search':{'roots':['repository docs','~/.gradle/caches','~/Public/.minecraft','~/.m2'], 'result':'No fixed FluffyFur archive or ItemSkin implementation located in this bounded filename search; not a machine-wide absence claim.'}})

# Freeze the next candidate's actual source, but explicitly do NOT award whole-design credit.
warchive = ROOT/'docs/art/armor-three-whole-20261112/wizardsreborn-fixed.zip'
next_sources=[]
with zipfile.ZipFile(warchive) as z:
    suffixes=['/ArcaneFortressArmorItem.java','/ArcaneFortressArmorModel.java','/ArcaneFortressSlimArmorModel.java']
    for suffix in suffixes:
        n=next(n for n in z.namelist() if n.endswith(suffix))
        next_sources.append({'archive_entry':n, **put('next-candidate/'+n.split('/src/',1)[1],z.read(n))})
ledger=json.loads((PRIOR/'combined-semantic-ledger.json').read_text())
assert 'wizards_reborn:arcane_fortress' not in ledger['reviewed_pending_whole_keys']
put('next-candidate.json',{'key':'wizards_reborn:arcane_fortress','state':'SOURCE_SELECTED_NOT_WHOLE_STUDY_COMPLETE','archive':str(warchive),'archive_sha256':sha(warchive.read_bytes()),'sources':next_sources,'observed_source_distinction':'Dedicated pelvis, leggings and feet aliases; paired 0.72/1.02 arm shells, paired 0.75/1.02 leg shells; separate slim arm source; not just ArcaneGold material recolor.', 'required_next':['Read FluffyFur alias/slot visibility against pinned source; preserve version caveat','Inspect original icons and 128x64 standard/slim atlases, all faces, front/45/side/back/gray/black diagnostics','Check item registry/models and ItemSkin branches','Semantic dedup against inventor and historic groups; Main independent applicability review'], 'visual_distinctness_verified':False,'new_credit':0})
put('combined-semantic-ledger.json',(PRIOR/'combined-semantic-ledger.json').read_bytes())
checks.update({'exact_source_entries_verified':len(copied),'forge_archive_sha1_matches':True,'production_changes':0,'new_credit':0,'gate_met':False,'D54_accepted_object_and_entire_ledger_unchanged':True})
put('verification.json', checks)
put('progress.json',{'batch':'D69','status':'EXACT_FORGE_HOOK_SUPPLEMENT_SAVED_NEXT_WHOLE_SELECTED','prior':str(PRIOR/'progress.json'),'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending,'next_candidate':'wizards_reborn:arcane_fortress'})
put('README.md',('D69：奥术金甲精确Forge消费者补查\n\n复用固定本地Forge47.3.0源码包并核对既有官方来源SHA1。保存五份准确版本源码/补丁，逐项核对纹理路径、模型回调、染色分支及trim/glint调用。D68历史文件保持不变。\n\n此次仅收窄Forge钩子版本缺口；精确Minecraft几何、FluffyFur皮肤替换和实机仍未闭环。正式新增参考信用0，1000门槛未通过。\n\n下一整套选奥术堡垒甲，已固定普通/纤细模型和物品实现。尚未看图、逐面检查和整套去重，不计为已完成设计参考。未覆盖游戏美术、未启动Java、未碰共享Jar/存档/提示词。\n').encode())

files=[{'path':str(p),'sha256':sha(p.read_bytes())} for p in sorted(OUT.rglob('*')) if p.is_file() and not p.name.startswith('bounded-receipt-') and p.name!='coordinator-delivery.json']
receipt_data=(json.dumps({'schema':'D69.exact_forge_hook_supplement.v1','files':files},ensure_ascii=False,indent=2)+'\n').encode()
receipt=put('bounded-receipt-'+sha(receipt_data)+'.json',receipt_data)
put('coordinator-delivery.json',{'batch':'D69','receipt':receipt,'verification':{'path':str(OUT/'verification.json'),'sha256':sha((OUT/'verification.json').read_bytes())},'new_credit':0,'gate_met':False,'production_changes':0,'pending':pending})
print(json.dumps({'receipt':receipt,'checks':checks},ensure_ascii=False))
