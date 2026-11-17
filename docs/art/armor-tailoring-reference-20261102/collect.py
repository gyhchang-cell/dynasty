"""Unread plate/cloth reference batch; reuse fixed exact-byte collector and prior semantic ledger."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-cloth-reference-20261102/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_local_armor_research', COLLECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'magistuarmory', 'dark_souls_expansion', 'immersive_armors', 'aether', 'classic_base', 'classic_125', 'classic_b173'}
    module.SKIP_CASES = set(prior['case_to_group'])
    module.COLLECT_WORN = False
    module.APPLICATION = '第四批未读板甲布甲与Aether装备参考：沿用227名称/104保守学习组，实际读取固定原图，归并经典包、同款版本、锈蚀换色及同套部件。重点观察袖口闭合、躯干/腰带覆盖和已认可图标的材料对应，不动112图标/56穿戴资源、身体、Java、实例、共享Jar、清单；1000真实独立相关设计门槛未达标前不制作。'
    module.main()
    context = {
        'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
        'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
        'scope': 'Unread native icons plus separately selected native worn texture study; no production edits.',
    }
    (D / 'collection-context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
