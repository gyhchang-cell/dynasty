"""Unread fixed-local armor families; no production art mutations."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-functional-reference-20261103/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_sources', COLLECTOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'legendary_monsters', 'monsterexpansion', 'weirdmobs', 'ice_and_fire_spellbooks',
                         'mythsandlegends', 'stalwart_dungeons', 'block_factorys_bosses', 'dragonloot',
                         'dungeonnowloading', 'royalvariations', 'undead_unleashed', 'spore'}
    module.SKIP_CASES = set(prior['reviewed_case_keys'])
    module.COLLECT_WORN = False
    module.APPLICATION = '第八批未读套装原图研究：累计374已看名称/154保守学习组；重点学习强力甲的小尺度轮廓、材料主次与布甲层次。Boss掉落名称不替代实际获取/数值依据；组件、换色、版本、怪物/坐骑甲不冒充独立玩家甲设计。达1000有效参考前不制作，保护既有289路径与用户实例/声音/亮度，保存完整要求与目标。'
    module.main()
    ctx = {'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
           'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
           'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
           'scope': 'Fixed local original icons only; filenames are candidates, not registered IDs or completion evidence.'}
    (D / 'collection-context.json').write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
