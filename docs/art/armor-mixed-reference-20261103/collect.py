"""Unread fixed-local armor families; no production art mutations."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-bossloot-reference-20261103/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_sources', COLLECTOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'celestisynth', 'rainbowcompound', 'enigmaticlegacy', 'enigmaticaddons', 'fantasy_ending', 'deeperdarker', 'illagerinvasion', 'alshanex_familiars', 'unusualend', 'savage_and_ravage', 'lethality', 'ulterlands', 'ageofweapons', 'glass_armor', 'enderitemod', 'jerotes', 'lost_aether_content', 'call_of_yucutan', 'call_of_drowner', 'fathomless', 'born_in_chaos_v1', 'bloodandmadness', 'iceandfire'}
    module.SKIP_CASES = set(prior['reviewed_case_keys'])
    module.COLLECT_WORN = False
    module.APPLICATION = '第九批未读玩家衣甲研究：复用406已看规范名称/168保守学习组，逐图确认材料、盔口、胸腰、靴筒；不凭名称捏造注册或强度。部件、版本、色变、图标外的身体不可虚增。1000有效参考未达前不制作，维持289路径、用户实例、声音、亮度和清单边界；要求全文/哈希/目标逐批保存。'
    module.main()
    ctx = {'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
           'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
           'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
           'scope': 'Fixed local original icons only; filenames are candidates, not registered IDs or completion evidence.'}
    (D / 'collection-context.json').write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
