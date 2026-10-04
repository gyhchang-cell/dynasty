"""Prepare instance-only v6 projection copies; never edit source or release files."""
import gzip
import hashlib
import math
from pathlib import Path
from audit_patrol_population import nbt

SOURCE = Path('/Users/a15356015027/Desktop/投影文件')
DEST = Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/schematics/狸小星/1.20.1兼容副本')

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob('*.litematic')):
        raw = gzip.decompress(source.read_bytes())
        original = nbt(raw)
        assert original['Version'] == 7, source.name
        # These files use the same contiguous palette packing as v6. Keep every
        # region, palette entry, block entity and entity verbatim; only relax the
        # format header. Do not pretend the newer Minecraft data version is old.
        for region in original['Regions'].values():
            volume = math.prod(abs(region['Size'][axis]) for axis in ('x','y','z'))
            bits = max(2, (len(region['BlockStatePalette']) - 1).bit_length())
            assert len(region['BlockStates']) == ((volume * bits + 63) // 64) * 8
        marker = b'\x03\x00\x07Version\x00\x00\x00\x07'
        assert raw.count(marker) == 1, source.name
        updated = raw.replace(marker, marker[:-1] + b'\x06', 1)
        converted = nbt(updated)
        assert converted.pop('Version') == 6
        check = dict(original)
        check.pop('Version')
        assert converted == check
        destination = DEST / source.name
        packed = gzip.compress(updated, mtime=0)
        if destination.exists() and destination.read_bytes() != packed:
            raise RuntimeError('Refusing to replace a different existing copy: ' + str(destination))
        destination.write_bytes(packed)
        assert gzip.decompress(destination.read_bytes()) == updated
        print(source.name, 'v6 projection copy verified; source sha256:', hashlib.sha256(source.read_bytes()).hexdigest())

if __name__ == '__main__':
    main()
