"""Second bounded batch: unread material armor only, reusing existing reviewed cases."""
from pathlib import Path
import hashlib,importlib.util,json

D=Path(__file__).resolve().parent
R=D.parents[2]
COLLECTOR=R/'docs/art/armor-reference-study-20261102/collect.py'

def main():
    spec=importlib.util.spec_from_file_location('fixed_local_armor_research',COLLECTOR)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    skip=set()
    ledgers=[R/'docs/art/armor-continuation-20261102/reference-review.json',
             R/'docs/art/armor-worn-uv-20261102/reference-variant-review.json',
             R/'docs/art/armor-reference-study-20261102/semantic-review.json']
    for p in ledgers:
        skip.update(c for g in json.loads(p.read_text())['observations'] for c in g['cases'])
    module.D=D
    module.NAMESPACES={'divinerpg','valoria','terra_equipment'}
    module.SKIP_CASES=skip
    module.COLLECT_WORN=False
    module.APPLICATION='第二批本地未读材料盔甲参考：复用前批57保守设计学习组，跳过已读名称族，实际看材料分区、原版轮廓与封闭面甲，合并同款色阶/部位/版本。只研究原始图标，不重复穿戴UV；1000真实独立相关参考未达标前不制作；保护112库存图标和56穿戴图，不改Java、人物、实例、共享Jar或清单。'
    module.main()
    record={'collector':str(COLLECTOR.relative_to(R)),'collector_sha256':hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(),
      'prior_ledgers':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in ledgers],
      'skipped_previously_reviewed_cases':sorted(skip),'scope':'icons only; worn atlas study already completed in preceding batch'}
    (D/'collection-context.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
