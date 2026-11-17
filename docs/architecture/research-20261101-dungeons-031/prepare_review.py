#!/usr/bin/env python3
"""Compare an old complete tower with unresolved closed-room tower families."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.OUT = OUT
    return m


if __name__ == '__main__':
    m = load('prepare', OUT.parent / 'research-20261101-dungeons-021/prepare_review.py')
    m.SELECTION = [('T01', 1, 'F05', (5, 15, 9, 9)), ('T02', 16, 'F01', (5, 16, 7, 7)),
                   ('T03', 11, 'F04', (6, 20, 7, 7)), ('C01', 2, 'F02', (12, 20, 7, 7))]
    m.main()
    load('audit', OUT.parent / 'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup', OUT.parent / 'research-20261101-dungeons-002/check_dedup.py').main()
