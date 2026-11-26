"""Assemble the two reviewed migration classes against the distribution in memory."""
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[3]
WRAPPER = ROOT / 'dist/dynasty-1.4.0-modrinth.mrpack'
MEMBER = 'overrides/mods/dynasty-1.4.0.jar'
RELEASE_SHA = 'eb9faca14934773092fe506c4c5471bd6f407944f60eec50044d6388d29d8e85'
LOOKUP = ROOT / 'build/cod4-legacy-overlay-linkage-20261120/migration-class-lookup.zip'
MIGRATION = {
    'com/dynasty/LegacyItemMappings.class': '12b3c9499d8eb5ad1b687832d70f6f70cbaf26633fefb0a79598a785ade7ef68',
    'com/dynasty/LegacyPlayerProgression.class': '566a4d4a40cb0752f7362c3e576bed881960fed46b81ce28d0ee4d848f71df3c',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def members(archive):
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate archive members')
    return {name: digest(archive.read(name)) for name in names}


def main():
    with ZipFile(WRAPPER) as wrapper:
        if wrapper.namelist().count(MEMBER) != 1:
            raise ValueError('Expected one packaged Dynasty JAR')
        source = wrapper.read(MEMBER)
    if digest(source) != RELEASE_SHA:
        raise ValueError('Distribution changed since review')
    candidate = io.BytesIO(source)
    with ZipFile(candidate) as base:
        original = members(base)
    if original.keys() & MIGRATION.keys():
        raise ValueError('Release already supplies a migration class')

    with ZipFile(LOOKUP) as additions, ZipFile(candidate, 'a') as out:
        if members(additions) != MIGRATION:
            raise ValueError('Unexpected lookup contents')
        for name in MIGRATION:
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_STORED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            out.writestr(entry, additions.read(name))
    with ZipFile(candidate) as merged:
        if members(merged) != original | MIGRATION:
            raise ValueError('Merged archive differs outside the approved entries')
    print(json.dumps({
        'release': str(WRAPPER.relative_to(ROOT)), 'member': MEMBER,
        'base_sha256': RELEASE_SHA, 'unchanged_members': len(original),
        'added_members': MIGRATION, 'in_memory_candidate_sha256': digest(candidate.getbuffer()),
        'candidate_size': len(candidate.getbuffer()),
    }, indent=2))


if __name__ == '__main__':
    main()
