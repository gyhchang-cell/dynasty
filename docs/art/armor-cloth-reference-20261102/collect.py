"""Third bounded study: unread hunter/cloth/material armor; source files stay read-only."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-material-reference-20261102/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_local_armor_research', COLLECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ledger = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'jerotesvillage', 'eternal_starlight'}
    module.SKIP_CASES = set(ledger['case_to_group'])
    module.COLLECT_WORN = False
    module.APPLICATION = '第三批本地未读猎装布甲和星光材料甲参考：复用既有82保守学习组及192名称，不按部件、换色、版本凑数。实际逐页看紧凑原版比例、布料与板甲分区，排除非盔甲或仅组件。保存原图精确出处，不重做已认可和精致老稿，不改生产资源、Java、实例、共享Jar和清单；1000真实独立相关参考未达标前不制作。'
    module.main()
    context = {
        'collector': str(COLLECTOR.relative_to(R)),
        'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
        'prior_ledger': str(PRIOR.relative_to(R)),
        'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
        'scope': 'Native armor icons only; no production artwork or game acceptance.',
    }
    (D / 'collection-context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
