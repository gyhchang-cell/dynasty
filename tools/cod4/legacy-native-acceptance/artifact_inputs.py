"""Load exactly the independently compiled resource bytes, rejecting unreviewed additions."""
from pathlib import Path
import hashlib


def load_resources(root: Path, expected: dict[str, str]) -> dict[str, bytes]:
    if root.resolve(strict=True) != root:
        raise ValueError('Resource directory must be canonical')
    files = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink in frozen resources')
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path
    if set(files) != set(expected):
        raise ValueError('Frozen resource file set differs from compiled inputs')
    payload = {}
    for name, path in files.items():
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected[name]:
            raise ValueError('Frozen resource bytes changed: ' + name)
        payload[name] = data
    return payload
