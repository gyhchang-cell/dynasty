from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'docs/art/armor-zanite-whole-20261114/combined-semantic-ledger.json'
PROGRESS = ROOT / 'docs/art/armor-continuation-20261102/progress.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

manifest = json.loads((OUT / 'source-manifest.json').read_text())
java = {Path(r['local']).stem: ROOT / r['local'] for r in manifest['entries'] if r['local'].endswith('.java')}

def evidence(classname, needles):
    path = java[classname]
    lines = path.read_text().splitlines()
    found = []
    for needle in needles:
        hits = [{'line': i + 1, 'text': line.strip()} for i, line in enumerate(lines) if needle in line]
        assert hits, (classname, needle)
        found.append({'needle': needle, 'hits': hits})
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path), 'declarations': found}

cases = [
    {
        'key': 'wizards_reborn:soul_hunter/cosmetic_on_inventor_wizard',
        'skin_class': 'SoulHunterSkin', 'slots': ['hood', 'costume', 'trousers', 'boots'],
        'consumer': 'SoulHunterArmorModel',
        'visual_observations': [
            '兜帽保持短宽开口，紫色一条硬边圈出脸部，顶部暗布块不靠渐变塑形。',
            '胸前左右两条紫边向下延续，短袖肩部与双靴有对应横带；亮紫只占小面积。',
            '裤腿分开、靴底分开，深色主体靠两到三档离散灰紫区分，未画完整人物。',
        ],
        'geometry_observations': '128×64自定义图集；8×8×8头块、8×12×4胸块、4×6×4袖块；头和躯干有独立外层，两侧1×3×7耳块。不能套用64×32原版UV裁片。',
        'acquisition': '本地配方声明alchemy_machine：wisestone_trim、两黑羊毛、两紫羊毛，wissen300/steam100；只证明生成trim，不证明依赖侧应用流程。',
    },
    {
        'key': 'wizards_reborn:royal_guard/cosmetic_on_inventor_wizard',
        'skin_class': 'RoyalGuardSkin', 'slots': ['hat', 'costume', 'trousers', 'boots'],
        'consumer': 'InventorWizardArmorModel',
        'visual_observations': [
            '窄蓝帽带和短宽帽冠清楚区分职业；胸前细蓝竖带与蓝靴口呼应。',
            '棕灰大色块支撑轮廓，肩部短宽，没有外扩成巨肩；裤装和短靴仍是MC物品比例。',
            '它沿用发明家法师几何，不能因为新贴图或新名字就自动算全新独立盔甲。',
        ],
        'geometry_observations': '128×64图集沿用InventorWizardArmorModel：10×4×10帽冠与16×0×16平面帽檐；texOffs(-16,14)不能按负坐标直接判错。',
        'acquisition': '截取范围内未找到royal_guard_trim配方；来源与依赖应用链待验，不编造可获取路径。',
    },
    {
        'key': 'wizards_reborn:magnificent_maid/default_and_slim_cosmetic',
        'skin_class': 'MagnificentMaidSkin', 'slots': ['headwear', 'suit', 'stockings', 'boots'],
        'consumer': 'MagnificentMaidArmorModel',
        'visual_observations': [
            '黑裙和白围裙用大块直边分区，头饰用少量白格形成横向轮廓；白色是衣料主体，不能删成透明。',
            '上衣图标带短宽肩部、前白围裙和下摆；袜子与鞋子分别辨识，不用同一靴模板换名。',
            '宽臂和细臂贴图属于同一套；不能把两图集、四部位或左右袜子拆成独立设计。',
        ],
        'geometry_observations': '128×64；CHEST绘制body/arms及左右skirt，LEGS仅绘制stockings，FEET绘制feet；细臂3宽对普通4宽，纹样须随真实UV重排。',
        'acquisition': 'arcane_iterator配方声明arcane_wood_trim、两黑羊毛、两白羊毛和arcanum标签，wissen100；应用与玩家获取未实测。',
    },
]
for case in cases:
    stem = case['skin_class']
    case['binding_evidence'] = [evidence(stem, ['addSkinEntry(', '.addArmorSkin(EquipmentSlot.HEAD',
        '.addArmorSkin(EquipmentSlot.CHEST', '.addArmorSkin(EquipmentSlot.LEGS',
        '.addArmorSkin(EquipmentSlot.FEET', 'getArmorModel(']),
        evidence(case['consumer'], ['LayerDefinition.create(mesh, 128, 64)'])]
    case['is_new_registered_armor_id'] = False
    case['new_accepted_design_credit'] = 0
    case['status'] = 'VISUAL_AND_DECLARED_BINDING_REVIEWED_GLOBAL_SEMANTIC_ACCEPTANCE_PENDING'
    case['applicable_learning'] = '仅学习MC物品部位比例、材料色块和穿戴UV分区方法；不复制原作者图像到Dynasty运行资源。'

bindings = {
    'scope': '源码声明与原生图像的离线研究；不是游戏穿戴、视角或完整依赖运行验收。',
    'cases': cases,
    'shared_evidence': [
        evidence('ArcaneArmorClassSkinEntry', ['canApplyOnItem', 'armor.hasCustomModel()', 'skins.containsKey', 'getItemModelName']),
        evidence('InventorWizardArmorItem', ['ItemSkin.getSkinFromItem', 'model.slot = type.getSlot()', 'hasCustomModel()']),
        evidence('ArcaneArmorItem', ['isDefaultModel', 'getModelName().equals("default")']),
        evidence('MagnificentMaidSkin', ['MAGNIFICENT_MAID_SLIM_ARMOR', 'skin + "_slim.png"']),
        evidence('MagnificentMaidArmorModel', ['slot == EquipmentSlot.CHEST', 'slot == EquipmentSlot.LEGS', 'slot == EquipmentSlot.FEET']),
        evidence('MagnificentMaidSlimArmorModel', ['3.0F, 12.0F, 4.0F']),
        evidence('WizardsRebornModels', ['SoulHunterArmorModel::createBodyLayer', 'MagnificentMaidArmorModel::createBodyLayer', 'MagnificentMaidSlimArmorModel::createBodyLayer']),
    ],
    'limitations': ['FluffyFur ItemSkin/ArmorClassSkinEntry/ArmorModel依赖未在本批展开，不能称完整消费者链闭合。',
                    '未启动客户端，未查看游戏正面/45度/侧面/背面或黑剪影。图集总览不是穿戴模拟。',
                    '未核实全历史图片语义等价性；3个完整配置均保留待全局去重，不追加1000门槛信用。',
                    '女仆鞋块有同名嵌套child命名；本批按原源码记录，未改依赖作者代码或声称运行异常。'],
}
save('whole-configuration-study.json', bindings)
ledger = json.loads(PRIOR.read_text())
for case in cases:
    assert case['key'] not in ledger['case_scope_followups']
    ledger['case_scope_followups'][case['key']] = {
        'source': str((OUT / 'whole-configuration-study.json').relative_to(ROOT)),
        'sha256': digest(OUT / 'whole-configuration-study.json'), 'new_design_credit': 0,
        'whole_cosmetic_configuration_reviewed': True, 'runtime_acceptance': False,
        'global_semantic_dedup_acceptance_pending': True,
    }
ledger['current_batch_prior'] = {'path': str(PRIOR.relative_to(ROOT)), 'sha256': digest(PRIOR)}
ledger['gate_met'] = False
ledger['production_authorized_by_this_register'] = False
save('combined-semantic-ledger.json', ledger)

# Independently re-read captured bytes from their existing project-local archive.
with zipfile.ZipFile(ROOT / manifest['archive']) as z:
    for row in manifest['entries']:
        assert hashlib.sha256(z.read(row['archive_entry'])).hexdigest() == row['sha256']
        assert digest(ROOT / row['local']) == row['sha256']
before = json.loads((OUT / 'protected-before.json').read_text())
for group, files in before.items():
    assert all(digest(ROOT / path) == expected for path, expected in files.items()), group
targets = json.loads((ROOT / 'docs/art/armor-target-path-index-20261114/targets.json').read_text())
for target in targets:
    for field in ['current_icon', 'current_model', 'worn_uv']:
        assert digest(Path(target[field])) == target[field + '_sha256']
old = json.loads(PRIOR.read_text())
assert all(ledger[k] == v for k,v in old.items() if k not in ['case_scope_followups', 'current_batch_prior'])
assert all(ledger['case_scope_followups'][k] == v for k,v in old['case_scope_followups'].items())
save('verification.json', {'source_entries_verified': len(manifest['entries']), 'native_png_viewed': 16,
    'complete_configurations_reviewed': 3, 'new_accepted_design_credit': 0,
    'protected_resources_unchanged': {k: len(v) for k,v in before.items()},
    'target_rows_unchanged': len(targets), 'prior_ledger_preserved': True,
    'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0,
    'gate_met': False, 'validated_independent_design_total': None, 'exact_remaining_gap_to_1000': None})
save('requirements-snapshot.json', {x.name: digest(x) for x in OUT.glob('requirements-*.md')})
(OUT / 'README.md').write_text('''# 2026-11-20：三套完整盔甲皮肤研究

接续D124，完成Soul Hunter、Royal Guard、Magnificent Maid三套原作者外观的实际图像与声明绑定研究。原始来源固定为WizardsReborn提交7ba78764cf6b4b0ca60e39722ca1452f7bd7f66b；仅复用项目内现存ZIP，未下载、恢复旧副本或更改运行贴图。

实际查看12张物品图标、4张128×64穿戴图集。女仆装普通臂/细臂为同一设计；这些是皮肤配置，不是新注册装备ID。离线总览只展示作者原图整数放大，不是Dynasty新增美术或实机截图。

具体外观、UV、四槽映射与证据行号见whole-configuration-study.json。灵魂猎手通过少量紫边识别兜帽/上衣；皇家卫士沿用原法师模型；女仆裙摆属于胸槽，袜子属于腿槽，不能按原版两层UV模板套图。上述方法可借鉴，作者资产不得直接覆盖进游戏。

本批42份源码/资源逐项回读SHA通过；289份保护资源、70份优先资源与28项目标索引均未变化。1000有效不同设计门槛仍未通过，新增正式信用0，精确总数和缺口仍未知。三套待全局语义去重；依赖侧皮肤应用与运行穿戴待验。本轮没有生产改图、构建、启动游戏或删除提示词。
''')
frozen = {str(p.relative_to(ROOT)): digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
save('bounded-receipt.json', {'files': frozen, 'scope': 'Offline author reference research only'})
delivery = {'status': 'THREE_COSMETIC_CONFIGURATIONS_REVIEWED', 'ids': [x['key'] for x in cases],
    'study': str((OUT / 'whole-configuration-study.json').relative_to(ROOT)),
    'verification': str((OUT / 'verification.json').relative_to(ROOT)),
    'receipt': str((OUT / 'bounded-receipt.json').relative_to(ROOT)),
    'receipt_sha256': digest(OUT / 'bounded-receipt.json'), 'gate_met': False, 'new_artwork': 0,
    'pending': bindings['limitations']}
save('coordinator-delivery.json', delivery)
progress = json.loads(PROGRESS.read_text())
assert progress['status'] == 'D124_ZANITE_NATIVE_WHOLE_REFERENCE_SAVED', 'Concurrent checkpoint change; delivery saved, progress not changed'
progress['status'] = 'THREE_COSMETIC_REFERENCE_CONFIGURATIONS_SAVED_20261120'
progress['latest_combined_semantic_ledger'] = str(OUT / 'combined-semantic-ledger.json')
progress['latest_skin_three_delivery'] = {'path': str(OUT / 'coordinator-delivery.json'), 'sha256': digest(OUT / 'coordinator-delivery.json')}
PROGRESS.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(delivery, ensure_ascii=False))
