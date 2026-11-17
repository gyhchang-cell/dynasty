"""Unread armor with suffix normalization, preventing four unseparated filenames becoming four designs."""
from pathlib import Path
from collections import defaultdict
import hashlib
import importlib.util
import json
import re

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-biome-reference-20261102/combined-semantic-ledger.json'


def main():
    spec = importlib.util.spec_from_file_location('fixed_local_armor_research', COLLECTOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    prior = json.loads(PRIOR.read_text())
    module.D = D
    module.NAMESPACES = {'shadowlands', 'bloodmagic', 'mokels_rpg_two', 'advancednetherite', 'tenebrous_lands', 'splendour_ablaze_epoch', 'supernatural'}
    module.SKIP_CASES = set(prior.get('reviewed_case_keys', prior['case_to_group']))
    module.COLLECT_WORN = False
    original_family = module.family

    def normalize(entry):
        stem = Path(entry).stem
        # These namespaces use both foohelmet.png and foo_helmet.png. Same family, no extra credit.
        return re.sub(r'_?(helmet|chestplate|leggings|boots)$', '', stem) if entry.split('/')[1] in module.NAMESPACES else original_family(entry)

    module.family = normalize
    module.APPLICATION = '第六批未读模板甲参考：沿用已读304名称/136保守学习组，先归并无下划线helmet/chestplate/leggings/boots命名，防止四部件凑四设计。实际查看原图，严格归并换色、锈蚀、升级与附层，观察MC轮廓和材质区；不覆盖已认可112图标/56穿戴，不碰人物、Java、实例、Jar与清单。1000适用独立设计证据未满足前不制作，保存要求全文/哈希/目标。'
    module.main()
    aliases = defaultdict(set)
    for index in module.INDEXES:
        for a in json.loads(index.read_text()):
            bits = a['entry'].split('/')
            if bits[0] != 'assets' or bits[1] not in module.NAMESPACES:
                continue
            aliases[bits[1] + ':' + normalize(a['entry'])].add(bits[1] + ':' + original_family(a['entry']))
    context = {'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
               'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
               'skipped_previously_reviewed_cases': sorted(module.SKIP_CASES),
               'normalization': 'Within selected namespaces only, strip optional underscore plus helmet/chestplate/leggings/boots suffix; no new design credit.'}
    (D / 'collection-context.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n')
    (D / 'name-normalization.json').write_text(json.dumps({'raw_index_name_families': len({v for values in aliases.values() for v in values}),
        'normalized_families': len(aliases), 'aliases': {k: sorted(v) for k, v in sorted(aliases.items())},
        'credit': 'NAME_CORRECTION_ONLY_NOT_MANUAL_DESIGN_ACCEPTANCE'}, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
