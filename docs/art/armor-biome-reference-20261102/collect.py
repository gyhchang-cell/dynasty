"""Unread biome and creature-material armor, retaining all prior reviewed-name exclusions."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-tailoring-reference-20261102/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_local_armor_research', COLLECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'alexsmobs', 'alexscaves', 'hybrid-aquatic', 'betterend', 'betternether', 'deep_aether', 'terramity', 'malum', 'soulsweapons'}
    module.SKIP_CASES = set(prior['case_to_group'])
    module.COLLECT_WORN = False
    module.APPLICATION = '第五批未读生物材料和地域甲参考：沿用264已读名称及117保守学习组与缺口记录，实际看完整原图，分清单件、同套部位、材质换色与独立设计。重点学习粗像素材料块、衣甲分工和原版紧凑比例；不重画已认可/精致老稿，不改人物、Java、实例、Jar、清单。1000真实独立相关参考达标前不制作，保存完整要求与目标。'
    module.main()
    context = {'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
               'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
               'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
               'scope': 'Native icon research only; anatomy/geometry/runtime binding not inferred from icons.'}
    (D / 'collection-context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
