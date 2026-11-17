"""Serialize manually read reference observations; does not execute upstream code."""
from pathlib import Path
import json, hashlib, re, shutil

ROOT = Path(__file__).resolve().parents[5]
DOC = ROOT / 'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
OUT = Path(__file__).parent / 'sources-batch009'
SRC = ROOT / 'tools/cod4/immune-feedback-research/sources'
namespace = {'__name__': 'static_reader', '__file__': str(ROOT / 'tools/cod4/immune-feedback-research/helpers/halley-immune/inspect_methods.py')}
exec((ROOT / 'tools/cod4/immune-feedback-research/helpers/halley-immune/inspect_methods.py').read_text(), namespace)
end_method = namespace['end_method']
manifest = {}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def reference(repo, file, method=None):
    base = SRC / repo
    matches = [base / (file + '.java')] if '/' in file else list(base.rglob(file + '.java'))
    if len(matches) != 1:
        raise ValueError((file, matches))
    path = matches[0]
    rel = path.relative_to(base).as_posix()
    raw = path.read_bytes()
    meta = json.loads((base / 'source.json').read_text())
    tree = json.loads((base / 'tree.json').read_text())
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    expected = next(x['sha'] for x in tree['tree'] if x['path'] == rel)
    if blob != expected or tree['sha'] != meta['commit']:
        raise ValueError(('source mismatch', rel))
    dest = OUT / repo / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    for name in ['source.json', 'tree.json']:
        target = OUT / repo / name
        if not target.exists():
            shutil.copyfile(base / name, target)
    lines = raw.decode().splitlines(keepends=True)
    if method:
        found = [i for i, line in enumerate(lines, 1) if re.match(r'\s*(public|protected|private|static)\s', line) and re.search(r'\b'+re.escape(method)+r'\s*\(', line) and not line.strip().endswith(';')]
        if len(found) != 1:
            raise ValueError((file, method, found))
        start = found[0]
        stop = end_method(lines, start)
    else:
        start, stop = 1, len(lines)
    text = ''.join(lines[start-1:stop])
    key = repo + '/' + rel
    manifest[key] = dict(repo=meta['repo'], commit=meta['commit'], path=rel,
                         file_sha256=digest(raw), git_blob_sha1=blob,
                         fixed_tree_blob_verified=True,
                         tree_api_url=tree.get('url'),
                         provenance_limit='MPS metadata uses MachineMuse alias; cached tree API resolves flowtender. No new remote ownership verification claimed.',
                         local=str(dest.relative_to(ROOT)))
    return dict(unit='complete_method' if method else 'complete_file_support_only',
                source_key=key, method=method, lines=[start,stop],
                url=f"https://github.com/{meta['repo']}/blob/{meta['commit']}/{rel}#L{start}-L{stop}",
                file_sha256=digest(raw), excerpt_sha256=digest(text.encode()),
                normalized_excerpt_sha256=digest(re.sub(r'\s+', '', text).encode()), excerpt=text)

P = 'MachineMuse__MachineMusePowersuits'
C = 'CammiesCorner__Arcanus'
ref = lambda file, method=None: reference(P, 'src/main/java/net/machinemuse/powersuits/common/proxy/CommonProxy' if file == 'CommonProxy' else file, method)
cref = lambda file, method=None: reference(C, file, method)
rows = []

def add(number, key, status, refs, observation, application, limits, dedup):
    rows.append(dict(id=f'herschel-009-{number:02}', semantic_dedup_key=key,
                     status=status, research_credit=0, suggested_credit=0,
                     source_refs=refs, concrete_observation=observation,
                     application=application, limits=limits, semantic_dedup=dedup))

add(1, 'mps-ray-hit-native-result-gates-target-impulse-but-not-shot-feedback-recoil',
    'pending_primary_semantic_review',
    [ref('RailgunModule','onItemRightClick'), ref('RailgunModule','drawParticleStreamTo'),
     ref('RailgunModule','onPlayerTickActive'), ref('ItemPowerFist','onItemRightClick'),
     ref('MusePlayerUtils','doCustomRayTrace'), ref('MusePlayerUtils','raytraceEntities'),
     ref('MusePlayerUtils','raytraceBlocks'), ref('Config','loadPowerModules'),
     ref('CommonProxy','init'), ref('MPSItems','populateItems'), ref('ModularPowersuits','init')],
    '电磁炮MAIN_HAND且energy>cost、timer==0才先扣能/设10tick/加热；实际64格射线比较最近实体和方块。实体分支先绘束流，再调用玩家源attackEntityFrom；只有返回true才给目标addVelocity。非空射线结果（包括方块）都会给射手反冲和第二次箭声；空结果仍有首次声、资源扣除且返回SUCCESS。计时只在active tick递减，不能推成卸下也按墙钟恢复。onItemRightClick本身没有服务端专用门，不声称源码已保证双端不重复。',
    '区分施放成功、碰撞可见、目标接纳伤害与目标实际位移四种回执；拒伤时不能仅凭束流/声/SUCCESS判目标已受控。',
    ['无Boss专用灰字，不提供拒绝原因；true也不等同于已观测位移。', '原生raytrace及物品分发全文已读；未运行该历史Forge版本，未审核全部第三方模块环境。', '须主岗判断与既有SpellEngine直接位移独立性；不得按每种武器另计。'],
    '主账reviewed.json本轮未命中MachineMuse/Railgun/PowerFist；与008-12忽略hurt结果后仍位移相反。本条仅一个候选，动力拳同构伤害门并入支持。')

add(2, 'mps-fist-same-result-gate-with-pre-damage-rotation-side-effect', 'support_only_not_effective',
    [ref('ItemPowerFist','hitEntity'),ref('MeleeAssistModule','MeleeAssistModule')],
    'OmniWrench激活先把目标rotationYaw加90取模，与MeleeAssist和hurt结果无关；近战辅助需玩家且energy>drain，扣能在hurt之前，整数截断伤害；仅hurt返回true才目标加速度，外层hitEntity最终总true。',
    '最终拒控门需要覆盖伤害前的方向副作用；外层物品回调true不是伤害接纳凭据。',
    ['不把原生目标yaw字段写入等同于双客户端可见旋转。', '没有移植或修改正式代码；同构伤害门不再计独立信用。'],
    '目标速度门并入009-01；伤害前副作用与GuardVillagers旧归属研究原则近似，守卫旧账不转免疫信用。')

add(3, 'mps-plasma-native-hurt-ignored-explosion-and-expiry-support', 'support_only_not_effective',
    [ref('PlasmaCannonModule','onPlayerStoppedUsing'),ref('PlasmaCannonModule','onItemRightClick'),
     ref('EntityPlasmaBolt','onImpact'),ref('EntityPlasmaBolt','onEntityUpdate'),
     ref('EntityPlasmaBolt','readEntityFromNBT'),ref('EntityPlasmaBolt','writeSpawnData'),ref('EntityPlasmaBolt','readSpawnData')],
    '停止蓄力先clamp10..50，服务端先加热后检查energy>cost，通过才扣能生成弹。onImpact非本人实体伤害忽略bool，随后服务端爆炸/销毁与8火粒子不依赖bool；mobGriefing只作为爆炸flag传入。水中销毁伴随火粒子；ticksExisted>200而非>=200销毁。存档read直接销毁，额外spawn数据只size。',
    '伤害未接纳仍存在碰撞/爆炸视觉，粒子与资源付费不能证明目标免疫失败。',
    ['爆炸伤害最终原生消费及受害者清单未读，不声称绕过目标免疫或伤及本人。', '不拆生命周期、size同步、伤害忽略成多个有效单位。'],
    '与008-12忽略原生hurt结果仍反馈同族，且缺原生爆炸消费，保留支持0。')

add(4, 'mps-fall-distance-energy-strict-boundary-before-client-sound', 'support_only_not_effective',
    [ref('MovementManager','handleFallEvent'),ref('ShockAbsorberModule','ShockAbsorberModule'),ref('CommonProxy','registerEvents'),ref('ModularPowersuits','preInit')],
    '玩家脚装备有ShockAbsorber激活且落距>3时，先算distanceAbsorb=原始落距*配置倍率；client声在energy比较前产生。只有drain<avail才扣能并减event距离，能量恰好等于cost拒绝，代码没有显式cancel事件或按1下限clamp倍率。',
    '声是尝试回执而非减伤成功回执；付费比较边界需明确，不凭声音证明免伤。',
    ['仅改落距，原生最终落伤计算未读，不能断言零伤；普通玩家装备不是Boss拒控实现。', '注册链支持已读；不运行客户端。'],
    '与008-15普通装备减伤同为辅助，Boss免疫/灰字相关性不足，0信用。')

add(5, 'arcanus-float-head-hurt-removal-and-nogravity-exit-support', 'support_only_not_effective',
    [cref('LivingEntityMixin','onDamage'),cref('LivingEntityMixin','attemptToRemoveEffect'),
     cref('LivingEntityMixin','floatAround'),cref('ArcanusStatusEffect','onEffectAdded')],
    'hurt HEAD在amount>0且未被盾挡时，若配置removedUponTakingDamage先移除FLOAT，早于DangerSense可能返回false，不能称HP真减少后才解除。onEffectAdded服务端FLOAT设noGravity(true)；onEffectRemoved HEAD再次设true而非false。floatAround在状态仍存在时直接增加Y输入速度。',
    '解除控制必须区分尝试受伤与实际接纳；退出后恢复重力要审查全部原生链，不能因状态列表消失就宣称恢复。',
    ['FloatSpellEffect.java不在固定缓存，不能闭合实际施放入口，因此不申请独立信用。', '静态可疑退出写值，不宣称本项目或外部实机已复现bug。', '共享onDamage完整方法含旧DangerSense已计链，本条不重计。'],
    '入口不完整；重力退出与主账其它mod控制清理同族，只作支持。')

add(6, 'arcanus-effect-sync-removal-true-and-anonymity-only-support', 'support_only_not_effective',
    [cref('ArcanusStatusEffect'),cref('ArcanusMobEffects'),cref('LivingEntityMixin','attemptToRemoveEffect'),
     cref('ClientboundStatusEffectPacket')],
    '完整状态注册显示只有ANONYMITY传shouldSync=true，FLOAT/DISCOMBOBULATE默认false。添加和移除两生产端均发hasEffect=true；客户端当前level按整数entityId找到Living后添加100tick/amp0，false才移除；不含UUID、维度或不存在实体重试。',
    '状态移除的布尔方向及接收者定位需要独立核查；不能把通用同步类存在当作每个控制状态已同步。',
    ['ANONYMITY施法来源不在固定缓存；不声称FLOAT通过该包错误重加。', '无真实网络/视觉验收；没有改外部代码。'],
    '与007 Ars原生整数id有损效果同步同族，且当前实际同步的是中立匿名状态，支持0。')

excluded = [dict(id='herschel-009-excluded-sonic', research_credit=0,
                 reason='SonicWeaponModule.java全部内容均为行注释，没有生效类或原生实现；完整读取后排除，不计reviewed_units。',
                 source_ref=ref('SonicWeaponModule'))]
batch = dict(batch='herschel-immune-009', research_credit=0, suggested_credit=0,
             effective_promoted=0, reviewed_units=6, pending_primary_review_units=1,
             support_only_units=5, excluded_nonimplementation_files=1,
             method_count_is_not_credit=True, rows=rows, excluded=excluded,
             review_boundary='人工实际阅读后序列化；哈希/原始文件数量只证明证据一致性，不替代Russell最终语义去重。没有1000达标声明。')
def write(name, value):
    (DOC / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
write('batch-009.json',batch)
write('source-manifest-009.json',dict(files=manifest, research_credit=0))
write('receipt-009.json', dict(status='PENDING_PRIMARY_REVIEW_NOT_ACCEPTANCE',
      batch_sha256=digest((DOC/'batch-009.json').read_bytes()),
      reviewed_units=6, candidate_units=1, support_only=5, excluded=1,
      source_files=len(manifest), research_credit=0,
      evidence_type='fixed cached source and manual static reading; no runtime validation',
      production_modified=False, master_modified=False, todo_modified=False,
      game_launches=0, compilation_runs=0, runtime_tests=0, external_requests=0))
print(json.dumps(json.loads((DOC/'receipt-009.json').read_text()),ensure_ascii=False))
