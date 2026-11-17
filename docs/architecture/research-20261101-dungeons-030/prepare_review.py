#!/usr/bin/env python3
"""Reopen complete garrison candidates under the unchanged purpose scope."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent


def run(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    return module


if __name__ == '__main__':
    prepare = run('prepare', OUT.parent / 'research-20261101-dungeons-021/prepare_review.py')
    prepare.SELECTION = [('T01', 9, 'F01', (2, 6, 10, 11)), ('T02', 9, 'F04', (2, 5, 24, 14)),
                         ('C01', 10, 'F01', (2, 8, 3, 3)), ('C02', 19, 'F01', (1, 12, 28, 15))]
    prepare.main()
    run('audit', OUT.parent / 'research-20261101-dungeons-017/audit_sources.py').main()
    run('dedup', OUT.parent / 'research-20261101-dungeons-002/check_dedup.py').main()
