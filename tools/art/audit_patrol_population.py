"""Read-only audit of saved entity regions. Never loads Minecraft or modifies a save.

Usage: python3 tools/art/audit_patrol_population.py /path/to/world
Uses only the Python standard library; outputs counts, not entity/player identities.
"""
import collections
import gzip
import io
import json
from pathlib import Path
import struct
import sys
import zlib


def nbt(data):
    stream = io.BytesIO(data)

    def number(fmt):
        return struct.unpack(">" + fmt, stream.read(struct.calcsize(fmt)))[0]

    def text():
        return stream.read(number("H")).decode("utf-8", errors="replace")

    def payload(kind):
        if kind in range(1, 7):
            return number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[kind])
        if kind == 8:
            return text()
        if kind == 9:
            element, size = number("B"), number("i")
            return [payload(element) for _ in range(size)]
        if kind == 10:
            value = {}
            while (entry := number("B")) != 0:
                name = text()
                value[name] = payload(entry)
            return value
        if kind in (7, 11, 12):
            return stream.read(number("i") * {7: 1, 11: 4, 12: 8}[kind])
        raise ValueError("Unknown NBT tag " + str(kind))

    kind = number("B")
    text()
    return payload(kind)


def audit(world):
    report = {}
    for dimension in sorted((world / "dimensions/dynasty").glob("*")):
        counts = collections.Counter()
        for path in sorted((dimension / "entities").glob("*.mca")):
            data = path.read_bytes()
            if not data:
                continue
            for slot in range(1024):
                location = int.from_bytes(data[slot * 4:slot * 4 + 4], "big")
                offset = (location >> 8) * 4096
                if not offset:
                    continue
                length = int.from_bytes(data[offset:offset + 4], "big")
                compression = data[offset + 4]
                raw = data[offset + 5:offset + 4 + length]
                if compression == 2:
                    raw = zlib.decompress(raw)
                elif compression == 1:
                    raw = gzip.decompress(raw)
                elif compression != 3:
                    raise ValueError(f"Unsupported region compression {compression}: {path.name}")
                for entity in nbt(raw).get("Entities", []):
                    counts["all_entities"] += 1
                    if entity.get("id") != "dynasty:imperial_soldier":
                        continue
                    counts["imperial_soldiers"] += 1
                    reason = entity.get("forge:spawn_type", "UNKNOWN")
                    counts["origin_" + reason] += 1
                    protected = (reason not in ("NATURAL", "CHUNK_GENERATION")
                                 or "DynastyOwner" in entity or bool(entity.get("CustomName"))
                                 or entity.get("PersistenceRequired", False)
                                 or "Leash" in entity or bool(entity.get("Passengers")))
                    counts["protected" if protected else "wild_despawn_eligible"] += 1
        report[dimension.name] = dict(counts)
    return report


if __name__ == "__main__":
    print(json.dumps(audit(Path(sys.argv[1])), ensure_ascii=False, indent=2))
