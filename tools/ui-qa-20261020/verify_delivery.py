"""Read-only audit of delivered UI payload, unchanged JAR members and exports."""
from pathlib import Path
import hashlib, io, json, zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'docs/ui-fixes-20261020'
d = json.loads((O / 'deployment.json').read_text())
hud = 'armorpointspp-forge-1.20-3.1.1.jar'
hud_bytes = (R / 'libs' / hud).read_bytes()
quests = {p.relative_to(R / 'modpack').as_posix(): p.read_bytes()
          for p in (R / 'modpack/config/ftbquests/quests').rglob('*.snbt')}
pack = (R / 'modpack/resourcepacks/dynasty-quest-guides-v3.zip').read_bytes()
assert (O / 'native-final/COMPLETE.txt').exists()
assert not (O / 'native-final/FAIL.txt').exists()
checks = (O / 'native-final/checks.txt').read_text()
assert 'Native typed negative query filters out unrelated items' in checks
assert all('Native typed query applies filtering: ' + q + ' results=1' in checks
           for q in ('结构罗盘', 'Jiegouluopan', 'Structure Compass'))
with zipfile.ZipFile(R / 'build/ui-client-20261020-final/mods/dynasty-1.4.0.jar') as z:
    expected = {n: z.read(n) for n in d['patch_members']}

def core(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert all(z.read(n) == b for n, b in expected.items())

jars = 0
archives = 0
preserved = 0
for rec in d['records']:
    p = Path(rec['path'])
    if p.name == 'dynasty-1.4.0.jar' and rec.get('after'):
        core(p.read_bytes())
        with zipfile.ZipFile(p) as z, zipfile.ZipFile(O / 'install-backup' / rec['before'] / p.name) as before:
            for entry in before.infolist():
                if entry.filename not in expected:
                    assert z.getinfo(entry.filename).CRC == entry.CRC, (p, entry.filename)
                    preserved += 1
        jars += 1
    if p.suffix in ('.mrpack', '.zip') and p.parent in (R / 'dist', Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')):
        with zipfile.ZipFile(p) as z:
            core(z.read('overrides/mods/dynasty-1.4.0.jar'))
            assert all(z.read('overrides/' + n) == b for n, b in quests.items())
            assert z.read('overrides/resourcepacks/dynasty-quest-guides-v3.zip') == pack
            assert not any('overflowingbars' in n.lower() or 'dynasty-audit-' in n.lower()
                           or 'dynasty-playtest-helper' in n.lower() for n in z.namelist())
            if 'modrinth.index.json' in z.namelist():
                idx = json.loads(z.read('modrinth.index.json'))
                assert not any('overflowingbars' in f['path'].lower() for f in idx['files'])
                downloaded = [f for f in idx['files'] if f['path'] == 'mods/' + hud]
                if downloaded:
                    assert downloaded[0]['hashes']['sha512'] == hashlib.sha512(hud_bytes).hexdigest()
                else:
                    assert z.read('overrides/mods/' + hud) == hud_bytes
            else:
                manifest = json.loads(z.read('manifest.json'))
                assert {'projectID': 396094, 'fileID': 4613606, 'required': True} in manifest['files']
                assert not any(f['projectID'] == 852662 for f in manifest['files'])
        archives += 1
for root in map(Path, d['profiles_and_distribution_roots']):
    assert (root / 'mods' / hud).read_bytes() == hud_bytes
    assert all((root / n).read_bytes() == b for n, b in quests.items())
    assert (root / 'resourcepacks/dynasty-quest-guides-v3.zip').read_bytes() == pack
for p, digest in d['user_options_unchanged'].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest
assert jars == 8 and archives == 6, (jars, archives)
report = dict(core_jars=jars, export_archives=archives,
              untouched_core_members_verified=preserved,
              native_search_actually_filters=True, user_options_unchanged=True,
              all_delivered_payloads_match_native_test=True)
(O / 'post-delivery-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
