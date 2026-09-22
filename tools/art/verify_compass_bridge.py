"""Validate navigation against current registries and actual installed optional APIs."""
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
data = root / 'src/main/resources/data/dynasty'
source = (root / 'src/main/java/com/dynasty/DynastyCompassBridge.java').read_text()
rows = re.findall(r'new Destination\("([^"]+)","[^"]+","([^"]+)","([^"]+)",(true|false)\)', source)
assert len(rows) == 12 and len({r[0] for r in rows}) == 12
for key, dimension, target, biome in rows:
    assert (data / 'dimension' / (dimension + '.json')).exists(), dimension
    folder = 'biome' if biome == 'true' else 'structure'
    assert (data / 'worldgen' / folder / (target + '.json')).exists(), target
    if biome == 'true':
        found = False
        for path in (data / 'forge/biome_modifier').glob('*.json'):
            record = json.loads(path.read_text())
            spawners = record.get('spawners', [])
            if isinstance(spawners, dict):
                spawners = [spawners]
            if not any(s.get('type') == 'dynasty:' + key for s in spawners):
                continue
            biomes = record.get('biomes', [])
            if isinstance(biomes, str):
                biomes = [biomes]
            for value in biomes:
                if value.startswith('#dynasty:'):
                    tag = data / 'tags/worldgen/biome' / (value.split(':')[1] + '.json')
                    found |= 'dynasty:' + target in json.loads(tag.read_text())['values']
                else:
                    found |= value == 'dynasty:' + target
        assert found, f'{key}: no confirmed spawn rule in {target}'
for mod, jar, clazz, method in [
    ('explorerscompass', 'ExplorersCompass-1.20.1-1.4.0-forge.jar', 'ExplorersCompassItem', 'searchForStructure'),
    ('naturescompass', 'NaturesCompass-1.20.1-1.12.0-forge.jar', 'NaturesCompassItem', 'searchForBiome'),
]:
    output = subprocess.check_output(['javap', '-p', '-classpath', str(root/'modpack/mods'/jar),
        f'com.chaosthedude.{mod}.items.{clazz}'], text=True)
    assert f'public void {method}(' in output
    assert 'public boolean isBroken(net.minecraft.world.item.ItemStack)' in output
print('PASS: 6 structures, 6 verified Boss habitats, existing compass JAR public search methods.')
