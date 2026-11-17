#!/usr/bin/env python3
"""Audit old identities without reclassifying them as new sources."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent


def run(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.main()


if __name__ == '__main__':
    run('raw_audit', OUT.parent / 'research-20261101-dungeons-017/audit_sources.py')
    run('old_identity_dedup', OUT.parent / 'research-20261101-dungeons-002/check_dedup.py')
