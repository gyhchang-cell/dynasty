"""Seal selected read-only death-intent review; never writes production resources."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'docs/art/bestiary-v43/suanni-gait-landing-research-20261110'
ID = 'zhenmu_suanni_tonghou'
ASSETS = ROOT / 'src/main/resources/assets/dynasty'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def evidence(p):
    p = Path(p)
    return {'path': str(p), 'sha256': sha(p)}

def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

inputs = [ASSETS / f'geo/blueprint/elite/{ID}.geo.json',
          ASSETS / f'animations/blueprint/elite/{ID}.animation.json',
          ASSETS / f'textures/entity/blueprint/elite/{ID}.png',
          ASSETS / f'textures/entity/blueprint/elite/{ID}_dead.png']
before = {str(p): sha(p) for p in inputs}
prior = json.loads((PRIOR / 'sampling-summary.json').read_text())
for path, digest in prior['source_hashes'].items():
    assert sha(path) == digest, 'Existing measured input changed; do not reuse measurement.'
manifest_path = ROOT / 'docs/art/creature-mc-v35/runtime-manifest.json'
manifest = json.loads(manifest_path.read_text())
manifest_text = json.dumps(manifest)
assert all(before[str(p)] in manifest_text for p in inputs[:3])
native_path = ROOT / 'docs/art/creature-mc-v35/native-checks.json'
native = json.loads(native_path.read_text())
prompt = Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt')
lines = prompt.read_text().splitlines()
heading = next(i for i, s in enumerate(lines, 1) if s.startswith('### 15.') and '狻猊' in s)
requirement = next(i for i, s in enumerate(lines, 1) if '兽首砸在地面' in s)
verification = json.loads(Path('/tmp/suanni-ender-golem-pin-verification-20261110.json').read_text())
write('upstream-byte-verification.json', verification)

review = {
    'target': ID,
    'status': 'OFFLINE_HEAD_TOUCH_REQUIREMENT_NOT_MET; REPAIR_PENDING_APPLICABLE_GATE',
    'design_intent': {
        'source': evidence(prompt), 'heading_line': heading, 'death_requirement_line': requirement,
        'paraphrase_only': '死亡要求包含铜腿关节断裂坍塌以及兽首落地；只记录任务定位，不备份待办全文。',
        'generator': evidence(ROOT / 'tools/blueprint/generate_bronze_suanni.py'),
        'generator_selected_lines': [107, 117],
        'generator_intent': '对死亡断肢防穿地，并按生成时的头颚几何计算本地地面补偿；后续最终几何改变使旧补偿不能直接作为验收依据。'
    },
    'approval_boundary': {
        'manifest': evidence(manifest_path), 'current_geo_animation_live_png_match_v35': True,
        'native_checks': evidence(native_path), 'historical_native_scope_verbatim': native['scope'],
        'interpretation': '保留已认可的主体形态；历史受控FIRE451渲染检查不等于自然死亡验收。',
        'original_software_death_preview': evidence(ROOT / f'docs/art/creature-mc-v35/{ID}/death.webp'),
        'preview_limit': '原软件预览没有可信地面基准，不能据其宣布头颚已触地，也不是实机死亡截图。'
    },
    'current_offline_evidence': {
        'sampling_summary': evidence(PRIOR / 'sampling-summary.json'),
        'raw_death_samples': evidence(PRIOR / 'death-key-midpoint.json'),
        'same_scale_side_preview': evidence(PRIOR / 'contact-poses.png'),
        'previous_visual_review': evidence(PRIOR / 'visual-inspection.json'),
        'head_jaw_minimum_units': prior['death']['lowest_head']['head_and_jaw_min_y_units'],
        'head_jaw_minimum_metres': prior['death']['lowest_head']['head_and_jaw_min_y_units'] / 16,
        'cast_limb_minimum_units': prior['death']['lowest_cast_limb']['cast_limb_min_y_units'],
        'adjudication': '全局最低点Y0来自独立支撑部件，不证明头颚触地。约7.9厘米正间隙与明确头部落地要求不符。断肢约4.2厘米正间隙需结合连接及支撑解释，不能要求每个方块均独立触地。',
        'clarifies_previous_review': '此前仅以父子连接判断正间隙不足以证明缺陷的结论，在明确兽首落地要求这一子范围不成立；保留旧收据原样。',
        'limits': '沿用已有165关键点/中点线性软件采样，不重复运行。不是原生Gecko、地形、重力、重载或多人验证。'
    },
    'minimal_future_repair_boundary': {
        'allowed_scope_after_gate': '仅最终几何对应的死亡头颚父链补偿及权威生成顺序；不更换形态、重做骨架或调整技能。',
        'not_a_ready_offset': '不能直接把世界Y间隙当作局部Y偏移；须按父链缩放/旋转反解，并检查头部附属结构、颚部、躯干穿插和过渡。',
        'retain': '已认可geo/比例、活体walk/stomp/fire、90tick死亡生命周期、贴图及物件资产。',
        'future_acceptance': '最终几何下的头颚接触、无穿地、落地过渡和余段稳定；再做符合隔离规则的自然死亡实机。'
    },
    'reference_method': {
        'identity': 'new1.20.1:Ender_Golem_',
        'revision': '819937203e22b4fa72fdeccc6c56ad415d65eeef',
        'ledger': evidence(ROOT / 'docs/art/creature-mc-v35/reference-ledger.json'),
        'read_scope': '模型构造层级与完整死亡分支/setupAnim；实体动画常量、觉醒保存/读档、tick觉醒层和死亡回调；LLibrary_Monster全文件；Boss父类保存/读档与tick；Animation_Monsters完整选定死亡触发/移除方法；Renderer全文件。未读取全部攻击分支或Lionfish AnimationHandler。',
        'phases_ticks': [10, 5, 20, 5, 5, 50],
        'authored_clip_ticks': 95,
        'actual_base_removal_threshold_ticks': 75,
        'lifecycle': 'LLibrary_Monster.tickDeath触发死亡动画并调用onDeathUpdate(duration-20)；父死亡更新先调用AI回调再递增deathTime，服务器达到75后移除。不可把95tick整段声明为实际可见。',
        'landing_event': '实体在回调deathTime==40调用落地声；因回调先于递增，不把该数值声称为无偏移的动画接触帧。只读源码，未播放声音。',
        'body_method': '腿与躯干分别下降，屈腿/前臂支撑，先沉降、短保持、再躯干翻倒；与保持最终姿态组合，而非只下移整体root。',
        'state_layers': '觉醒/未觉醒两分支属于同一机制；deactivateProgress叠加于动画后，觉醒状态保存但进度不是所选类自定义保存字段。不得只看裸死亡关键帧断言实际姿态或完整重载连续性。',
        'renderer': '本地Renderer scale1、death flip0；该文件本次远端TLS验证失败，只保留本地SHA，不宣称已完成其远端字节核验。',
        'transfer': '学习阶段性失重、支撑、落定与真实实体生命周期对应；狻猊仍保留青铜滚动支撑与原90tick机制，不复制模型/关键帧。',
        'dedup': '扩展历史已存在的EnderGolem身份；两觉醒分支、多个文件和阶段不重复计数。',
        'new_accepted_reference_credit': 0
    },
    'gate': {
        'historical_static_structure_accepted': 1000, 'prior_target100s_preserved': True,
        'current_applicable_whole_accepted_total': None, 'current_gap': None,
        'reason': '当前修复范围的适用实现映射、语义去重及独立验收尚未完成；不把历史静态1000自动换算为当前动态验收。',
        'no_production_repair_before_gate': True
    },
    'production_hashes': before,
    'production_unchanged': before == {str(p): sha(p) for p in inputs},
    'native_run': False, 'java_run': False, 'original_task_retained': True,
    'coordinator_checklists_edited': False, 'shared_jar_or_user_instance_touched': False
}
assert review['production_unchanged']
write('review.json', review)
write('progress.json', {
    'target': ID, 'completed': ['原要求与生成源意图定位', '最终认可资源与原实机范围核对', '已有密集数据的要求判定', '关联末影傀儡死亡完整选定流程研究'],
    'pending': ['当前适用参考门槛映射与独立验收', '门槛满足后的死亡头颚最小补偿修复', '隔离自然死亡实机验收'],
    'new_accepted_reference_credit': 0, 'production_modified': False, 'task_complete': False
})
write('handoff-metadata.json', {n: evidence(OUT / n) for n in ['review.json', 'progress.json', 'upstream-byte-verification.json', 'README.md', 'record.py']})
print(json.dumps({'handoff': evidence(OUT / 'handoff-metadata.json'), 'production_unchanged': review['production_unchanged']}, ensure_ascii=False))
