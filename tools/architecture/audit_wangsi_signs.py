#!/usr/bin/env python3
"""Read Wangsi wall-sign placement and reproduce its compatibility patch.

Only Python literal parsing and local mapped-source reads are used. This does
not execute Minecraft, validate native collision, or regenerate architecture.
"""
import argparse
import difflib
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J = 'src/main/java/com/dynasty/'
PIECE = J + 'dungeon/WangsiPiece.java'
ARCH = J + 'dungeon/WangsiArchitecture.java'
OUT = ROOT / 'docs/architecture/continuation-20261022'
MEMBERS = {
    'net/minecraft/world/level/levelgen/structure/StructurePiece.java': [(145, 188), (431, 456)],
    'net/minecraft/world/level/block/Mirror.java': [(38, 48)],
    'net/minecraft/world/level/block/WallSignBlock.java': [(44, 46), (69, 71), (82, 88)],
    'net/minecraft/world/level/block/entity/SignBlockEntity.java': [(92, 140), (173, 195), (243, 259)],
    'net/minecraft/world/level/block/entity/SignText.java': [(21, 35)],
    'net/minecraft/world/level/block/entity/BlockEntity.java': [(53, 79), (135, 140)],
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mapped-sources', type=Path, default=Path.home() / (
        '.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/'
        '1.20.1-47.4.10_mapped_official_1.20.1/'
        'forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar'))
    args = parser.parse_args()
    paths = [PIECE, ARCH, J + 'dungeon/WangsiStructure.java',
             J + 'structure/DynastyStructurePiece.java', J + 'dungeon/DungeonMasonryBlock.java',
             J + 'dungeon/DungeonContent.java']
    raw = {p: (ROOT / p).read_bytes() for p in paths}
    src = {p: data.decode() for p, data in raw.items()}
    current_piece, arch = src[PIECE], src[ARCH]
    facing_old = '.setValue(net.minecraft.world.level.block.WallSignBlock.FACING,Direction.NORTH)'
    facing_new = '.setValue(net.minecraft.world.level.block.WallSignBlock.FACING,Direction.SOUTH)'
    orientation_comment = '        // SOUTH pieces mirror Z-facing states; SOUTH input places a north-facing sign.\n'
    init_old = '            sign.setText(text,true);sign.setWaxed(true);sign.setChanged();'
    init_new = '''            if(sign.hasLevel()){
                sign.setText(text,true);sign.setWaxed(true);sign.setChanged();
            }else{
                // FEATURES generation may expose a ProtoChunk entity before it has a Level.
                CompoundTag initialized=sign.saveWithoutMetadata();
                initialized.put("front_text",SignText.DIRECT_CODEC.encodeStart(net.minecraft.nbt.NbtOps.INSTANCE,text)
                    .result().orElseThrow(()->new IllegalStateException("Cannot encode Wangsi sign text")));
                initialized.putBoolean("is_waxed",true);
                sign.load(initialized);
                sign.setChanged();
            }'''
    applied = 'if(sign.hasLevel())' in current_piece
    piece = current_piece
    if applied:
        assert current_piece.count(init_new) == current_piece.count(facing_new) == current_piece.count(orientation_comment) == 1
        piece = piece.replace(init_new, init_old).replace(facing_new, facing_old).replace(orientation_comment, '')
    assert 'setOrientation(Direction.SOUTH)' in piece
    assert 'placeBlock(level, state, dx, dy, dz, box);' in src[J + 'structure/DynastyStructurePiece.java']
    assert 'for(int cx=0;cx<6;cx++)for(int cz=0;cz<8;cz++)builder.addPiece(new WangsiPiece(origin,cx,cz,instance));' in src[J + 'dungeon/WangsiStructure.java']
    dims = tuple(map(int, re.search(r'WIDTH=(\d+),HEIGHT=(\d+),DEPTH=(\d+)', arch).groups()))
    body = arch.split('private static final int[][] BOXES={', 1)[1].split('\n    };', 1)[0]
    boxes = [tuple(map(int, m.split(','))) for m in re.findall(r'\{([\d,]+)\}', body)]
    assert boxes and not re.sub(r'\{[\d,]+\}|[\s,]', '', body)
    assert all(len(b) == 7 and all(0 <= b[a] <= b[a+3] < dims[a] for a in range(3)) for b in boxes)
    palette = arch.split('static final BlockState[] STATES={', 1)[1].split('};', 1)[0].split(',')
    assert all(b[6] < len(palette) for b in boxes)
    calls = re.findall(r'sign\(level,clip,new BlockPos\((\d+),(\d+),(\d+)\),((?:"[^"\n]*",?){4})\);', piece)
    assert len(calls) == piece.count('sign(level,clip,new BlockPos(') == 4

    def cell(p):
        if not all(0 <= p[a] < dims[a] for a in range(3)):
            return {'position': p, 'status': 'OUTSIDE_DECLARED_CITY', 'palette': None, 'last_box_zero_based': None}
        hits = [(i, b[6]) for i, b in enumerate(boxes) if all(b[a] <= p[a] <= b[a+3] for a in range(3))]
        i, value = hits[-1] if hits else (None, 0)
        return {'position': p, 'status': 'EXPLICIT_AIR' if value == 1 else 'DECLARED_STATE_ONLY',
                'palette': palette[value], 'palette_index': value, 'last_box_zero_based': i}

    records = []
    for x, y, z, rows in calls:
        p = [int(x), int(y), int(z)]
        north = cell([p[0], p[1], p[2]-1])
        south = cell([p[0], p[1], p[2]+1])
        records.append({'position_relative_to_city_origin': p,
                        'rows': re.findall(r'"([^"\n]*)"', rows),
                        'piece_column': [p[0]//16, p[2]//16],
                        'before_fix_input_facing': 'NORTH', 'before_fix_after_mirror_facing': 'SOUTH',
                        'before_fix_required_support': north,
                        'proposed_input_facing': 'SOUTH', 'proposed_after_mirror_facing': 'NORTH',
                        'proposed_required_support': south,
                        'proposed_support_in_same_piece': [p[0]//16, (p[2]+1)//16] == [p[0]//16, p[2]//16]})

    with zipfile.ZipFile(args.mapped_sources) as z:
        mapped = {m: z.read(m) for m in MEMBERS}
    sp = mapped['net/minecraft/world/level/levelgen/structure/StructurePiece.java'].decode()
    assert 'case SOUTH:\n               this.mirror = Mirror.LEFT_RIGHT;' in sp
    assert 'p_73436_ = p_73436_.mirror(this.mirror);' in sp
    assert 'p_73435_.setBlock(blockpos, p_73436_, 2);' in sp
    mirror = mapped['net/minecraft/world/level/block/Mirror.java'].decode()
    assert 'direction$axis != Direction.Axis.Z' in mirror and 'Rotation.CLOCKWISE_180' in mirror
    wall = mapped['net/minecraft/world/level/block/WallSignBlock.java'].decode()
    assert '.relative(p_58073_.getValue(FACING).getOpposite())).isSolid()' in wall
    assert 'p_58078_.getRotation(p_58077_.getValue(FACING))' in wall
    entity = mapped['net/minecraft/world/level/block/entity/BlockEntity.java'].decode()
    sign_entity = mapped['net/minecraft/world/level/block/entity/SignBlockEntity.java'].decode()
    assert 'public boolean hasLevel()' in entity and 'public final CompoundTag saveWithoutMetadata()' in entity
    assert 'public void load(CompoundTag' in sign_entity

    assert piece.count(facing_old) == piece.count(init_old) == 1
    proposed = piece.replace('        put(level,clip,p,Blocks.DARK_OAK_WALL_SIGN',
                             orientation_comment + '        put(level,clip,p,Blocks.DARK_OAK_WALL_SIGN', 1)
    proposed = proposed.replace(facing_old, facing_new).replace(init_old, init_new)
    assert current_piece == (proposed if applied else piece), 'Mixed/unrecognized patch state'
    assert re.findall(r'sign\(level,clip,new BlockPos.*', proposed) == re.findall(r'sign\(level,clip,new BlockPos.*', piece)
    patch_name = 'wangsi-sign-worldgen-proposal-20261026.patch'
    patch = ''.join(difflib.unified_diff(piece.splitlines(True), proposed.splitlines(True),
                                       fromfile='a/'+PIECE, tofile='b/'+PIECE))
    report = {
        'date': '2026-10-26', 'status': 'SOURCE_FIX_APPLIED__NATIVE_ACCEPTANCE_PENDING' if applied else 'STATIC_SUPPORT_DEFECT_CONFIRMED__COMBINED_PATCH_NOT_APPLIED',
        'scope': 'Existing Wangsi wall-sign placement only; no architecture generation or redesign',
        'java_executed': False, 'production_source_changed': applied,
        'runtime_resources_changed': False, 'checklist_deleted': [],
        'new_architecture_references_added': 0, 'city_dimensions': dims, 'literal_box_count': len(boxes),
        'piece_count_preserved': 48, 'chinese_sign_count_preserved': len(records), 'signs': records,
        'transform': ['WangsiPiece declares SOUTH; positions use minZ + localZ',
                      'StructurePiece SOUTH assigns LEFT_RIGHT mirror and NONE rotation',
                      'placeBlock mirrors the state before setBlock',
                      'WallSignBlock.mirror rotates Z-facing signs 180 degrees',
                      'canSurvive reads the block opposite FACING'],
        'limitations': ['Native generation, isSolid, survival, neighbor updates and rendering are NOT executed',
                        'Before the fix, three backing cells were explicitly AIR; the fourth lay outside the city and depended on terrain',
                        'Proposed backing cells are declared dark oak planks / masonry; actual native support remains unaccepted',
                        'No claim that a sign necessarily drops immediately with flag 2; neighbor-update survival is a separate risk',
                        'Only fresh SOUTH pieces are traced; loaded pieces with other serialized orientations need separate review',
                        'Source correction is not completed native verification or checklist acceptance'],
        'supersedes_proposal': 'wangsi-sign-worldgen-proposal-20261024.patch',
        'initialization_source_report': 'wangsi-sign-worldgen-compatibility-20261024.json',
        'pending_native_acceptance': [
            'Generate all 48 pieces to FULL through natural WorldGenRegion / ProtoChunk path without sign NPE',
            'Read all four signs after FULL, chunk unload/reload and save/reopen: 16 Chinese rows, red entrance, wax flag',
            'Read all four final FACING states and actual supporting blocks; exercise supporting-neighbor updates',
            'Confirm no missing pieces, architecture changes or mechanism regressions',
        ],
        'proposed_patch': patch_name, 'proposed_patch_sha256': sha(patch.encode()),
        'source_before_sha256': sha(piece.encode()), 'proposed_source_sha256': sha(proposed.encode()),
        'source_current_sha256': sha(raw[PIECE]),
        'input_sha256': {p: sha(b) for p, b in raw.items()},
        'mapped_sources': {'path': str(args.mapped_sources), 'sha256': sha(args.mapped_sources.read_bytes()),
                           'members': [{'path': m, 'sha256': sha(data), 'excerpts': [
                               {'first_line': a, 'last_line': b,
                                'text': '\n'.join(data.decode().splitlines()[a-1:b])}
                               for a, b in MEMBERS[m]]} for m, data in mapped.items()]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / patch_name).write_text(patch)
    target = OUT / 'wangsi-sign-support-20261026.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert (ROOT / PIECE).read_bytes() == raw[PIECE], 'Audit must not modify production source'
    print(json.dumps({'report': str(target), 'patch': patch_name, 'signs': len(records),
                      'before_fix_explicit_air_backings': sum(r['before_fix_required_support']['status'] == 'EXPLICIT_AIR' for r in records),
                      'production_source_fix_applied': applied, 'java_executed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
