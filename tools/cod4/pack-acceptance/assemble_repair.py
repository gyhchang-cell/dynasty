"""Overlay only privately compiled/reobfuscated WorkshopJei classes onto the verified jar."""
from pathlib import Path
import hashlib,json,zipfile,difflib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/pack-acceptance'
sha=lambda b:hashlib.sha256(b).hexdigest()
baseline=R/'build/cod4-audit-20261022/verified-gradle/libs/dynasty-1.4.0.jar';patch=R/'build/cod4-pack-20261022/gradle/libs/dynasty-language-repair-classes-1.4.0.jar'
verified=json.loads((R/'docs/cod4/audit-20261022/verification.json').read_text())['jar']['sha256'];assert sha(baseline.read_bytes())==verified
assert json.loads((O/'language-study/summary.json').read_text())['valid_implementation_sites']==1000
dest=R/'build/cod4-pack-20261022/language-repair/dynasty-1.4.0.jar';dest.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(patch) as z:updates={n:z.read(n) for n in z.namelist() if n.endswith('.class')}
assert updates and all(n.startswith('com/dynasty/workshop/WorkshopJei') for n in updates)
with zipfile.ZipFile(baseline) as old,zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as new:
 originals={n:old.read(n) for n in old.namelist()}
 for info in old.infolist():new.writestr(info,updates.get(info.filename,originals[info.filename]))
 for n,b in updates.items():
  if n not in originals:new.writestr(n,b)
with zipfile.ZipFile(dest) as z:
 assert all(z.read(n)==b for n,b in originals.items() if n not in updates)
 assert set(z.namelist())==set(originals)|set(updates)
changed=[n for n,b in updates.items() if originals.get(n)!=b]
source=R/'src/main/java/com/dynasty/workshop/WorkshopJei.java';frozen=R/'build/cod4-audit-20261022/frozen/src/main/java/com/dynasty/workshop/WorkshopJei.java'
(O/'WorkshopJei-repair-source.java.txt').write_bytes(source.read_bytes())
(O/'WorkshopJei-repair.patch').write_text(''.join(difflib.unified_diff(frozen.read_text().splitlines(True),source.read_text().splitlines(True),fromfile='verified-frozen/WorkshopJei.java',tofile='src/main/java/com/dynasty/workshop/WorkshopJei.java')))
record={'baseline':str(baseline),'baseline_sha256':verified,'repair_jar':str(dest),'repair_sha256':sha(dest.read_bytes()),'reobf_patch_sha256':sha(patch.read_bytes()),'source_sha256':sha(source.read_bytes()),'changed_or_added_entries':changed,'compiled_entries':list(updates),'all_other_entries_byte_identical':True,'asset_or_recipe_data_changes':False,'source_diff':'WorkshopJei-repair.patch','build_log':'language-repair-build.log'}
(O/'language-repair-build.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
