"""Read current authored geometry and trace supported steps past the exit gate."""
from collections import deque
from functools import cache
from hashlib import sha256
from pathlib import Path
import json
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0,str(ROOT / "tools/blueprint"))
from review_chensha_architecture import load_coordinates

_, piece, *_ = load_coordinates()
SOURCE = ROOT / "src/main/java/com/dynasty/dungeon"
DIRECTIONS = ((0,1),(1,0),(-1,0),(0,-1))
START = (32,25,53)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def create_geometry(trial_running=False, artisan_open=False, exit_open=True):
    @cache
    def block(x,y,z):
        if (x,z) in {(25,57),(31,57),(37,57)} and y==28:
            return "EYE"
        if (x,y,z)==(25,24,55):
            return "CORE"
        if y==30 and z==60 and x in (26,37):
            return "SOUL_LANTERN"
        if (x,y,z) in {(52,25,91),(55,25,91),(50,26,92),(53,26,90)}:
            return "FIXTURE"
        if 25<=y<=28:
            if z==52 and 30<=x<=34:
                return "AIR" if exit_open else "CLOSED_EXIT"
            if ((z==67 and 30<=x<=34) or (x in (24,39) and z in (59,60))):
                return "CLOSED_ENTRY" if trial_running else "AIR"
        if artisan_open and 51<=x<=53 and z==87 and 25<=y<=27:
            return "AIR"
        return piece.cell(x,y,z)
    return block


def support(material):
    return material in {"CUT_COPPER","BONE_BLOCK","LIGHT_BLUE_STAINED_GLASS"} or (material or "").startswith("MASONRY_")


def stands(block, cell):
    x,y,z=cell
    return support(block(x,y-1,z)) and block(x,y,z)==block(x,y+1,z)=="AIR"


def neighbors(block, cell, drop_limit=1):
    x,y,z=cell
    for dx,dz in DIRECTIONS:
        nx,nz=x+dx,z+dz
        for dy in range(1,-drop_limit-1,-1):
            other=(nx,y+dy,nz)
            if not (4<=nx<=59 and 18<=y+dy<=32 and 32<=nz<=93 and stands(block,other)):
                continue
            if dy==1 and block(x,y+2,z)!="AIR":
                continue
            if dy<0 and any(block(nx,level,nz)!="AIR" for level in range(y+dy+2,y+2)):
                continue
            yield other


def trace(block, start, drop_limit=1):
    assert stands(block,start), start
    parents={start:None}
    queue=deque([start])
    while queue:
        cell=queue.popleft()
        for node in neighbors(block,cell,drop_limit):
            if node not in parents:
                parents[node]=cell
                queue.append(node)
    return parents


def route(parents, end):
    path=[]
    while end is not None:
        path.append(end)
        end=parents[end]
    return path[::-1]


def compressed(path):
    segments=[]
    for start,end in zip(path,path[1:]):
        move=tuple(b-a for a,b in zip(start,end))
        if not segments or segments[-1]["delta"]!=move:
            segments.append(dict(start=start,end=end,delta=move,steps=1))
        else:
            segments[-1]["end"]=end
            segments[-1]["steps"]+=1
    return segments


if __name__=="__main__":
    source_ready=create_geometry()
    opened_wall=create_geometry(artisan_open=True)
    source_active=create_geometry(trial_running=True)
    reachable=trace(source_ready,START)
    with_wall_open=trace(opened_wall,START)
    with_entries_closed=trace(source_active,START)
    targets={
        "north_jinwu_landing":(32,25,42),
        "east_channel_north_rim":(47,25,53),
        "south_trial_entry":(32,25,67),
        "southeast_dry_wall_approach":(54,25,86),
        "artisan_cracked_wall_front":(52,25,86),
        "artisan_inner_landing":(52,25,88),
        "artisan_chest_north":(52,25,89),
        "artisan_workbench_west":(54,25,91),
    }
    assert targets["north_jinwu_landing"] not in with_entries_closed
    assert targets["south_trial_entry"] not in with_entries_closed
    assert targets["artisan_inner_landing"] not in reachable
    assert all(p in with_wall_open for p in targets.values())
    assert create_geometry(exit_open=False)(32,25,52)=="CLOSED_EXIT"
    assert (32,25,50) not in reachable
    assert source_ready(32,23,51).startswith("MASONRY_") and source_ready(32,24,51)=="AIR"
    assert all(source_ready(*p)=="CRACKED_STONE_BRICKS" for p in ((52,25,87),(52,26,87)))
    assert all(source_ready(x,24,z)=="LIGHT_BLUE_STAINED_GLASS" for x in range(50,54) for z in (85,86))
    # South route reaches the east end of the marked strip on a safe stone cell.
    # From there one adjacent glass cell is enough to reach the two-high breach.
    wall_edge=targets["southeast_dry_wall_approach"]
    direct_breach=[wall_edge,(53,25,86),(53,25,87),(53,25,88)]
    assert all(b in neighbors(opened_wall,a) for a,b in zip(direct_breach,direct_breach[1:]))
    drops=[]
    for x in (21,22,41,42):
        for high_z,low_z in ((58,57),(61,62)):
            lip,bottom=(x,25,high_z),(x,19,low_z)
            assert lip in reachable and bottom in neighbors(source_ready,lip,6)
            assert not set(trace(source_ready,bottom)).intersection({lip,START,targets["north_jinwu_landing"]})
            assert source_ready(x,18,low_z)=="LIGHT_BLUE_STAINED_GLASS"
            drops.append(dict(lip=lip,bottom=bottom,vertical_blocks=6))
    paths={}
    for name,target in targets.items():
        graph=reachable if target in reachable else with_wall_open
        path=route(graph,target)
        assert all(y==25 for _,y,_ in path),name
        assert all(a in neighbors(opened_wall,b) for a,b in zip(path,path[1:])),name
        paths[name]=dict(steps=len(path)-1,segments=compressed(path),path=path)
    inputs=[SOURCE / (name+".java") for name in (
        "ChenshaPiece","ChenshaArchitecture","ChenshaVaultLayout","ChenshaEnvironment",
        "ChenshaGarrisons","DungeonMechanismBlock","DungeonMechanismBlockEntity",
        "DungeonRoomController")]
    inputs.extend([ROOT/"tools/blueprint/review_chensha_architecture.py",
        OUT.with_name("audit-20261126-chensha-stair-gate")/"RECEIPT.json"])
    result=dict(
        start=START, paths=paths, hazardous_drops=drops, wall_edge_breach=direct_breach,
        east_side_entry=dict(x=39,z=[59,60]),west_side_entry=dict(x=24,z=[59,60]),
        south_entry=dict(x=[30,34],z=67),
        constraints="干地卡迪纳尔移动，一格台阶须有净空。玻璃为可支撑但可能触发效果。碰撞按体素保守估计，当前结构外天然地形、游泳、跳跃、护栏碰撞、开门同步、实体和战斗均未验证。",
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
        java_runs=0,game_starts=0,
    )
    (OUT/"gate-forward-readback.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print({k:v["steps"] for k,v in paths.items()})
