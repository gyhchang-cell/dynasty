"""Overlay exactly the two already-tested guard classes onto the verified private baseline."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'tools/cod4/guard-network-acceptance/.work'
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={
 'SummonedGuard':'f5239c711cfc7300989b9f41e672850d97b75ac8dadd0dfcbc05149f34a07229',
 'SecondaryMob':'53c7c824aa539c8e8af52c941d292ff1fd146d76b948cb854a2aec73d82d7cb1'}
for name,digest in expected.items():
    rel=Path('src/main/java/com/dynasty/expansion')/(name+'.java')
    assert sha((ROOT/rel).read_bytes())==digest
    assert sha((ROOT/'tools/cod4/guard-target-acceptance/.work/frozen'/rel).read_bytes())==digest
original=ROOT/'tools/cod4/armor-network-acceptance/.work/run-13/host/mods/dynasty-1.4.0.jar'
assert sha(original.read_bytes())=='ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b'
patch=BASE/'gradle/libs/dynasty-guard-patch-1.4.0.jar'
dest=BASE/'patched/dynasty-1.4.0.jar'
assert not dest.exists(),'Preserve the existing isolated artifact'
dest.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(original) as src,zipfile.ZipFile(patch) as changed,zipfile.ZipFile(dest,'w') as out:
    entries={f'com/dynasty/expansion/{n}.class':changed.read(f'com/dynasty/expansion/{n}.class') for n in expected}
    for info in src.infolist():out.writestr(info,entries.get(info.filename,src.read(info.filename)))
with zipfile.ZipFile(original) as src,zipfile.ZipFile(dest) as out:
    assert src.namelist()==out.namelist()
    different=[n for n in src.namelist() if src.read(n)!=out.read(n)]
    assert set(different)==set(entries),different
manifest={'baseline_sha256':sha(original.read_bytes()),'patched_sha256':sha(dest.read_bytes()),'changed_entries':different,'all_other_entries_byte_identical':True,'production_source_sha256':expected,'tested_native_ai_receipt':'docs/cod4/audit-20261022/guard-target-native-acceptance/verification.json','worlds_touched':False}
(dest.parent/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
