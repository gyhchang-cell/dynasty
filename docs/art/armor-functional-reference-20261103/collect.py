"""Unread functional clothing and footwear; preserve prior reviewed and excluded-name keys."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-template-reference-20261103/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_armor_sources', COLLECTOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'create', 'confluence', 'wooledboots', 'candlelight', 'kaleidoscope_cookery', 'meadow', 'vinery', 'brewery', 'dimdoors', 'majruszsdifficulty', 'aquaculture', 'artifacts', 'undergarden'}
    module.SKIP_CASES = set(prior.get('reviewed_case_keys', prior['case_to_group']))
    module.COLLECT_WORN = False
    module.APPLICATION = '第七批未读功能服装与靴参考：沿用341已读规范名称/145保守学习组，实际看图研究布衣开襟、袖口、腰线、靴筒与材料用途。毛靴材料/蜡化/升级、同系Terraria靴、同套部件不重复计设计，先核对是否玩家装备。1000适用真实独立相关设计未达标前不制作；不动已认可112图标/56穿戴、人物/Java/实例/共享Jar/清单，保存全文要求/哈希/目标。'
    module.main()
    context = {'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
               'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
               'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
               'scope': 'Read-only fixed local archive icon research. No actual artwork, body geometry or game acceptance.'}
    (D / 'collection-context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
