"""Non-JVM checks: interpret actual sluice Java with a narrow, fail-closed adapter.
Minecraft fluid scheduling, Forge loading and real movement remain unverified.
"""
import json,re,unittest,zipfile,os
from dataclasses import dataclass
from types import SimpleNamespace
from pathlib import Path
from review_chensha_architecture import JavaCoordinates,PARSER,ROOT
from review_wangsi import grid,reachable

@dataclass(frozen=True)
class Pos:
    x:int;y:int;z:int
    def subtract(self,p):return Pos(self.x-p.x,self.y-p.y,self.z-p.z)
    def offset(self,x,y,z):return Pos(self.x+x,self.y+y,self.z+z)
    def getX(self):return self.x
    def getZ(self):return self.z

class SluiceCode(JavaCoordinates):
    def expr(self,n):
        f=n.child_by_field_name;text=n.text.decode()
        if n.type=='string_literal':return repr(json.loads(text))
        if n.type=='update_expression' and text.endswith('--'):return self.expr(n.named_children[0])+' -= 1'
        if n.type=='binary_expression':
            a,b=f('left'),f('right');op=n.text[a.end_byte-n.start_byte:b.start_byte-n.start_byte].decode().strip()
            if op=='>>':return '('+self.expr(a)+' >> '+self.expr(b)+')'
        if n.type=='method_invocation':
            name=f('name').text.decode();obj=f('object');raw=obj.text.decode() if obj else ''
            args=[self.expr(c) for c in f('arguments').named_children]
            if name=='equals':return '('+self.expr(obj)+' == '+args[0]+')'
            if name in ('location','toString','getChunkSource'):return self.expr(obj)
            if name=='is':return '('+self.expr(obj)+' == '+args[0]+')'
            if name=='isAir':return '('+self.expr(obj)+" == 'AIR')"
            if raw=='WangsiStructure' and name=='instanceId':return 'identity('+','.join(args)+')'
            if name in ('roomId','mechanismId','completed','shortcutOpen','getBlockPos','subtract','dimension','getSeed',
                        'instance','getChunkNow','getX','getZ','offset','getBlockState','setBlock','unlockShortcut'):
                return self.expr(obj)+'.'+name+'('+','.join(args)+')'
        return super().expr(n)

def identity(seed,origin):return str((seed,origin))

class Room:
    def __init__(self,done=True):self.done=done;self.keys=set()
    def completed(self):return self.done
    def shortcutOpen(self,key):return key in self.keys
    def unlockShortcut(self,key):
        if key in self.keys:return False
        self.keys.add(key);return True

class World:
    def __init__(self,origin):
        self.cells={origin.offset(x,y,z):'WATER' for y in range(6,9) for z in range(94,100) for x in range(14,17)}
        self.writes=[];self.missing=set()
    def dimension(self):return 'dynasty:underworld'
    def getSeed(self):return 123
    def getChunkNow(self,x,z):return None if (x,z) in self.missing else True
    def getBlockState(self,p):return self.cells.get(p,'STONE')
    def setBlock(self,p,state,flags):self.cells[p]=state;self.writes.append((p,state,flags));return True

class WangsiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(ROOT/'src/main/java/com/dynasty/dungeon/WangsiSluice.java').read_text()
        core=Pos(*map(int,re.search(r'CORE=new BlockPos\(([^)]+)',source)[1].split(',')))
        constants=dict(re.findall(r'(ROOM|DRAINED)="([^"]+)"',source))
        translator=SluiceCode();translator.env.update(constants,CORE=core,identity=identity)
        cls.impl=translator.load('WangsiSluice',['tick']);cls.core=core

    def setup_world(self,origin=Pos(0,0,0),done=True):
        world=World(origin);room=Room(done)
        be=SimpleNamespace(roomId=lambda:'wangsi_sluice',mechanismId=lambda:'wangsi_sluice_core',
            getBlockPos=lambda:origin.offset(self.core.x,self.core.y,self.core.z),instance=lambda:identity(123,origin))
        return world,be,room

    def test_actual_source_budget_and_open_only_after_empty(self):
        world,be,room=self.setup_world()
        for expected in (38,22,6,0):
            before=len(world.writes);changed=self.impl.tick(world,be,room)
            self.assertEqual(expected,sum(v=='WATER' for v in world.cells.values()))
            self.assertLessEqual(len(world.writes)-before,16)
            self.assertEqual(expected==0,changed)
        self.assertTrue(room.shortcutOpen('wangsi_sump_drained'))
        self.assertFalse(self.impl.tick(world,be,room));self.assertEqual(54,len(world.writes))
        self.assertEqual({2},{flags for _,_,flags in world.writes})

    def test_unstarted_and_wrong_instance_make_no_changes(self):
        world,be,room=self.setup_world(done=False);self.assertFalse(self.impl.tick(world,be,room));self.assertFalse(world.writes)
        room.done=True;be.instance=lambda:'another-city'
        self.assertFalse(self.impl.tick(world,be,room));self.assertFalse(world.writes)

    def test_missing_chunk_prevents_partial_drain_at_negative_origin(self):
        world,be,room=self.setup_world(Pos(-112,-30,-144));world.missing.add((-6,-3))
        self.assertFalse(self.impl.tick(world,be,room));self.assertFalse(world.writes)

    def test_reload_resumes_from_remaining_cells_without_refilling(self):
        world,be,room=self.setup_world();self.impl.tick(world,be,room)
        saved=dict(world.cells);new_room=Room();world.cells=saved
        for _ in range(3):self.impl.tick(world,be,new_room)
        self.assertEqual(54,len(world.writes));self.assertTrue(new_room.shortcutOpen('wangsi_sump_drained'))

    def test_player_replacement_is_never_erased_or_counted_drained(self):
        world,be,room=self.setup_world();p=Pos(14,6,94);world.cells[p]='DIAMOND_BLOCK'
        self.assertFalse(self.impl.tick(world,be,room));self.assertEqual('DIAMOND_BLOCK',world.cells[p]);self.assertFalse(room.keys)

    def test_failed_world_write_keeps_grates_locked(self):
        world,be,room=self.setup_world();world.setBlock=lambda *args:False
        self.assertFalse(self.impl.tick(world,be,room));self.assertFalse(room.keys)
        self.assertEqual(54,sum(v=='WATER' for v in world.cells.values()))

    def test_all_authored_java_parses(self):
        paths=list((ROOT/'src/main/java/com/dynasty/dungeon').glob('Wangsi*.java'))
        paths += [ROOT/'src/main/java/com/dynasty/dungeon'/name for name in ('DungeonContent.java','DungeonMechanismBlock.java','DungeonMechanismBlockEntity.java','DungeonDefinition.java')]
        for p in paths:self.assertFalse(PARSER.parse(p.read_bytes()).root_node.has_error,p.name)

    def test_new_reference_set_has_one_hundred_new_author_projects(self):
        base=ROOT/'docs/blueprint-cod2/evidence';a=json.loads((base/'wangsi-20261018/references.json').read_text())
        old={r['url'].rstrip('/') for r in json.loads((base/'architecture-20261018/references.json').read_text())}
        urls={r['url'].rstrip('/') for r in a}
        self.assertEqual(100,len(a));self.assertEqual(100,len(urls));self.assertFalse(urls&old)
        self.assertTrue(all(r['author'] and r['comparison_zh'] for r in a))

    def test_new_model_parents_and_textures_resolve(self):
        assets=ROOT/'src/main/resources/assets/dynasty'
        classpath=(ROOT/'build/classpath/runClient_minecraftClasspath.txt').read_text()
        jar=next(Path(s.strip()) for s in classpath.replace(os.pathsep,'\n').splitlines() if s.strip().endswith('/client-extra.jar') and Path(s.strip()).is_file())
        with zipfile.ZipFile(jar) as z:
            for name in ('wangsi_soul_lamp','wangsi_soul_lamp_broken'):
                model=json.loads((assets/f'models/block/{name}.json').read_text())
                self.assertIn('assets/minecraft/models/'+model['parent'].split(':')[-1]+'.json',z.namelist())
                for value in model['textures'].values():
                    if not value.startswith('#'):self.assertIn('assets/minecraft/textures/'+value.split(':')[-1]+'.png',z.namelist())

if __name__=='__main__':unittest.main()
