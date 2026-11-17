#!/usr/bin/env python3
"""Reconcile whole ice-tower and ice-ruin evidence without restoring damage."""
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
    m.SELECTION = [('T01', 1, 'F11', (5, 20, 8, 8)), ('T02', 3, 'F11', (4, 23, 7, 11)),
                   ('C01', 15, 'F01', (6, 21, 9, 9))]
    m.main()
    load('audit', OUT.parent / 'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup', OUT.parent / 'research-20261101-dungeons-002/check_dedup.py').main()
