"""Fresh local organic/rib/cloth references, with generic part names normalized by parent."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
R = D.parents[2]
COLLECTOR = R / 'docs/art/armor-reference-study-20261102/collect.py'
PRIOR = R / 'docs/art/armor-binding-reference-20261103/combined-semantic-ledger.json'


def main():
    assert not (D / 'provenance.json').exists(), 'Do not overwrite fixed collection'
    spec = importlib.util.spec_from_file_location('fixed_source', COLLECTOR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    old_family = m.family

    def family(entry):
        if Path(entry).stem in {'helmet', 'chestplate', 'leggings', 'boots'}:
            return Path(entry).parent.name
        return old_family(entry)

    m.family = family
    prior = json.loads(PRIOR.read_text())
    m.D = D
    m.NAMESPACES = {'biomancy', 'callfromthedepth_', 'eeeabsmobs', 'utopiabosses',
                    'the_awakening_of_the_elder_souls', 'mutantmonsters', 'mutantmore',
                    'butcher', 'geckolib', 'goetyawaken', 'mutationcraft_origins'}
    explicitly_outside = {'butcher:armor_placeholder', 'butcher:bottleof'}
    m.SKIP_CASES = set(prior['reviewed_case_keys']) | explicitly_outside
    m.COLLECT_WORN = False
    m.APPLICATION = '第十一批固定本地来源研究：复用442已读名称/184保守学习组；实际读骨质、植物、布和板片盔甲，重点检查四部件身份与大材料分区。通用部件文件名按父目录归类，组件/换色/演示层不算独立设计。1000真实适用独立设计未达前不制作，保护289路径、精致旧稿、实例、共享Jar、主清单、声音与亮度。'
    m.main()
    data = {
        'collector': str(COLLECTOR.relative_to(R)), 'collector_sha256': hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
        'batch_collector': str(Path(__file__).resolve().relative_to(R)),
        'batch_collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        'skipped_previously_reviewed_cases': sorted(prior['reviewed_case_keys']),
        'explicitly_outside_scope': sorted(explicitly_outside),
        'normalization': 'Generic helmet/chestplate/leggings/boots stem -> actual parent folder; other part suffixes -> existing collector normalization.',
        'scope': 'Native PNG icon study only. Filenames are research keys, not newly registered IDs or game acceptance.',
    }
    (D / 'collection-context.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
