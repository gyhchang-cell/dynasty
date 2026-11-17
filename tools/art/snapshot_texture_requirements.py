"""Save the user's actual texture rules with each batch; never touch artwork."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / 'docs/art/USER_TEXTURE_REQUIREMENTS.md'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-dir', required=True, type=Path)
    parser.add_argument('--targets', nargs='+', required=True)
    parser.add_argument('--application', required=True,
                        help='What this batch does, preserves, and still needs to verify')
    args = parser.parse_args()
    batch = args.batch_dir.resolve()
    batch.relative_to((ROOT / 'docs/art').resolve())
    data = RULES.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    batch.mkdir(parents=True, exist_ok=True)
    snapshot = batch / f'texture-requirements-{digest[:12]}.md'
    if snapshot.exists() and snapshot.read_bytes() != data:
        raise RuntimeError('Existing rule snapshot differs; refusing overwrite')
    snapshot.write_bytes(data)
    receipt = dict(saved_at=datetime.now(timezone.utc).isoformat(),
        source=str(RULES), snapshot=str(snapshot.relative_to(ROOT)), sha256=digest,
        targets=args.targets, application=args.application,
        production_complete=False, limitation='A saved rule snapshot is not visual or runtime acceptance.')
    receipt_path = batch / f'texture-requirements-receipt-{digest[:12]}.json'
    if receipt_path.exists():
        old = json.loads(receipt_path.read_text())
        if old['targets'] != receipt['targets'] or old['application'] != receipt['application']:
            raise RuntimeError('Existing batch receipt differs; preserve it and use another batch directory')
    else:
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(snapshot=str(snapshot), receipt=str(receipt_path), sha256=digest)))

if __name__ == '__main__':
    main()
