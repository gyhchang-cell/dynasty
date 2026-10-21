#!/usr/bin/env python3
"""Source-coordinate and spawn-policy checks; never starts Java or Minecraft."""
import hashlib
import json
import math
import re
from pathlib import Path
from review_chensha_architecture import ROOT, PARSER, load_coordinates

OUT=ROOT/'docs/blueprint-cod2/evidence/garrisons-20261018'


def review():
    java,piece,vault,_,_=load_coordinates()
    guards=java.load('ChenshaGarrisons',['jinwuOffset','hammerOffset','maySpawn','inRoom'])
    content=(ROOT/'src/main/java/com/dynasty/blueprint/elite/EliteContent.java').read_text()
    results=[];positions=[]
    def check(value,description):
        assert value,description
        results.append(description)
    for role,registration,feet in [('jinwu','JINWU',guards.jinwuOffset()),('hammer','HAMMER',guards.hammerOffset())]:
        line=next(s for s in content.splitlines() if f' {registration}=' in s)
        match=re.search(r'\.sized\(([.\d]+)F,([.\d]+)F\)',line);assert match,line
        width,height=map(float,match.groups());x,y,z=feet
        ranges=[range(math.floor(x+.5-width/2),math.ceil(x+.5+width/2)),
                range(y,math.ceil(y+height)),range(math.floor(z+.5-width/2),math.ceil(z+.5+width/2))]
        occupied=[(X,Y,Z,piece.cell(X,Y,Z)) for X in ranges[0] for Y in ranges[1] for Z in ranges[2]
                  if piece.cell(X,Y,Z)!='AIR']
        check(not occupied,f'{role}: full registered {width}×{height} body has authored air clearance; {occupied[:3]}')
        check(all((piece.cell(X,y-1,Z) or '').startswith('MASONRY_') for X in ranges[0] for Z in ranges[2]),
              role+': entire footprint supported by dry protected masonry')
        check(guards.inRoom(role=='hammer',*feet),role+': spawn belongs to the intended dungeon floor')
        positions.append({'role':role,'offset':feet,'width':width,'height':height,'body_cells':len(ranges[0])*len(ranges[1])*len(ranges[2])})
    check(guards.maySpawn(False,0,0,0,100),'Fresh singleton eligible')
    check(not guards.maySpawn(False,0,0,101,100),'Future retry cannot run early')
    check(guards.maySpawn(False,0,0,100,100),'Retry boundary is inclusive')
    for members in (1,2,12):
        check(not guards.maySpawn(False,0,members,0,100),f'{members} persisted unloaded members block new spawn')
    for produced in (1,2,99,-1):
        check(not guards.maySpawn(False,produced,0,0,100),f'Produced={produced} does not mint another elite')
    check(not guards.maySpawn(True,0,0,0,100),'Cleared singleton remains cleared')
    for pos in [(32,49,60),(32,73,5),(2,25,60),(32,34,60),(32,0,15),(60,1,15)]:
        check(not guards.inRoom(False,*pos) and not guards.inRoom(True,*pos),f'Wrong floor/outside entrant {pos} rejected')
    check(guards.inRoom(False,32,25,60) and not guards.inRoom(True,32,25,60),'Middle room only requests Jinwu')
    check(guards.inRoom(True,32,1,27) and not guards.inRoom(False,32,1,27),'Vault entry only requests Hammer')
    # Verify the scheduler and lifecycle edges in parsed production source. These
    # are static integration checks, not claims of runtime spawn/portal testing.
    g=(ROOT/'src/main/java/com/dynasty/dungeon/ChenshaGarrisons.java').read_text()
    b=(ROOT/'src/main/java/com/dynasty/blueprint/BlueprintSpawns.java').read_text()
    e=(ROOT/'src/main/java/com/dynasty/blueprint/elite/EliteEncounters.java').read_text()
    check('ChenshaGarrisons.spawnOne(level,origin,player.blockPosition())' in b and 'int remaining=2;' in b,
          'Elites use existing two-member tomb scheduler budget')
    check(g.index('if(!level.addFreshEntity(actor))return false;')<g.index('marker.members.add(actor.getUUID())'),
          'Failed world insertion cannot consume ledger slot')
    check(g.index('loadedStandingSpace(level,feet,box)')<g.index('!level.noCollision(null,box)'),
          'Loaded footprint checked before collision query')
    check('level.getServer().overworld()' in g and 'marker.members.remove(actor.getUUID())' in g,
          'Terminal release resolves exact UUID in owning Overworld ledger')
    check('ChenshaGarrisons.release(mob);' in e and 'getRemovalReason().shouldDestroy()' in e,
          'Existing confirmed death/terminal-removal path calls owner release; chunk unload is retained')
    check('"entrance").completed()' in g and 'hammer&&!rooms.room(instance,"mercury").completed()' in g,
          'Actual entrance and mercury completion records gate the appropriate elite')
    check('ChenshaStructure.instanceId(level.getSeed(),origin)' in g,'Authored seed/origin instance identity required')
    files=[ROOT/f'src/main/java/com/dynasty/{p}.java' for p in
           ['dungeon/ChenshaGarrisons','dungeon/ChenshaGarrisonGameTests','blueprint/BlueprintSpawns','blueprint/elite/EliteEncounters']]
    for path in files: check(not PARSER.parse(path.read_bytes()).root_node.has_error,'Java syntax: '+str(path.relative_to(ROOT)))
    OUT.mkdir(parents=True,exist_ok=True)
    report={'date':'2026-10-18','passed':len(results),'checks':results,'spawns':positions,
            'java_started':False,'native_spawn_tested':False,'native_game_tests_prepared_not_executed':3,
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'limitations':['Source syntax is not Java compilation','Entity collision, AI combat, spawning and portal persistence still need native validation'],
            'textures':'Existing Jinwu/Hammer resources reused; no new texture request was necessary'}
    (OUT/'static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':len(results),'spawns':positions,'java_started':False},ensure_ascii=False))


if __name__=='__main__':review()
