"""Read the distributed server handler and model uninterrupted play across join offsets."""
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
WRAPPER = ROOT / 'dist/dynasty-1.4.0-modrinth.mrpack'
ENTRY = 'com/dynasty/DynastyWorldEvents.class'


def instructions(code):
    return [(int(pc), op, args.strip()) for pc, op, args in
            re.findall(r'^\s*(\d+):\s+(\w+)([^\n]*)', code, re.MULTILINE)]


def conditional_periods(rows):
    # Read the two branch targets so a check moved to another path cannot pass.
    counter = next(i for i, row in enumerate(rows) if row[1] == 'putstatic' and 'tickCounter:I' in row[2])
    assert [r[1] for r in rows[counter-4:counter+7]] == [
        'getstatic','iconst_1','iadd','dup','putstatic','sipush','if_icmpge','return','iconst_0','putstatic','invokestatic']
    assert int(rows[counter+2][2]) == rows[counter+4][0]
    assert 'tickCounter:I' in rows[counter+5][2]
    poll = int(rows[counter+1][2])
    player = next(i for i, row in enumerate(rows) if row[1] == 'getfield' and 'ServerPlayer.f_19797_:I' in row[2])
    assert [r[1] for r in rows[player:player+8]] == [
        'getfield','bipush','irem','ifne','aload','invokestatic','aload','invokestatic']
    assert 'DynastyAdvancements.checkDerived:' in rows[player+5][2]
    assert 'DynastyWeaponGifts.tick:' in rows[player+7][2]
    assert int(rows[player+3][2]) == rows[player+8][0]
    return poll, int(rows[player+1][2])


def main():
    scratch = ROOT / 'build/cod4-gift-polling'
    scratch.mkdir(parents=True, exist_ok=True)
    with ZipFile(WRAPPER) as wrapper, ZipFile(io.BytesIO(wrapper.read('overrides/mods/dynasty-1.4.0.jar'))) as jar:
        handler = jar.read(ENTRY)
        routes = {}
        for name in ('evolution_path_sword_seven_star','evolution_path_sword_dragon_slayer','evolution_path_sword_supreme'):
            key = f'data/dynasty/recipes/{name}.json'
            recipe = json.loads(jar.read(key))
            assert recipe == json.loads((ROOT/'src/main/resources'/key).read_bytes())
            routes[name] = recipe
    with tempfile.TemporaryDirectory(dir=scratch) as temp:
        path = Path(temp)/'DynastyWorldEvents.class'
        path.write_bytes(handler)
        code = subprocess.check_output(['javap','-p','-c',str(path)], text=True)
    method = code.split(' void onServerTick(',1)[1].split('private static void ',1)[0]
    poll, modulus = conditional_periods(instructions(method))
    # One full residue cycle suffices: subsequent poll ages repeat modulo modulus.
    polls = modulus // math.gcd(modulus,poll)
    hits = [sum((age + k*poll) % modulus == 0 for k in range(polls)) for age in range(modulus)]
    print(json.dumps(dict(handler=ENTRY, sha256=hashlib.sha256(handler).hexdigest(),
        outer_period=poll, player_modulus=modulus, polls_per_residue_cycle=polls,
        eligible_initial_age_residues=[i for i,n in enumerate(hits) if n],
        unreachable_initial_age_residues=[i for i,n in enumerate(hits) if not n],
        smithing_routes=routes, native_player_run=False),indent=2))


if __name__ == '__main__':
    main()
