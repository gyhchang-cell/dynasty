"""Checks packaged originals and actual vanilla first-person bow transform math."""
import hashlib
import json
import math
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/assets/dynasty'
DOC = ROOT / 'docs/art/realm-remaster-v4'

class RealmArtTests(unittest.TestCase):
    def test_manifest_assets(self):
        for manifest, count, size, color in [('assets.json',8,128,2),
                                              ('weapons.json',25,128,6),
                                              ('skins.json',6,256,6)]:
            rows=json.loads((DOC/manifest).read_text())
            self.assertEqual(count,len(rows))
            hashes=set()
            for row in rows:
                data=(ROOT/row['texture']).read_bytes()
                self.assertEqual(b'\x89PNG\r\n\x1a\n',data[:8])
                self.assertEqual((size,size),struct.unpack('>II',data[16:24]))
                self.assertEqual(color,data[25])
                self.assertTrue((ROOT/row['project_source']).is_file())
                self.assertTrue(row['prompt'])
                hashes.add(hashlib.sha256(data).hexdigest())
            self.assertEqual(count,len(hashes), 'Each asset is an independent image')

    def test_new_bows_aim_forward_both_hands(self):
        client=(ROOT/'src/main/java/com/dynasty/client/DynastyClientEvents.java').read_text()
        for name in ('shenbi_bow','dragon_bow','fengling_bow','chang_gong','zhuxing_bow','houyi_bow'):
            self.assertIn('DynastyWeapons.'+name.upper()+'.get()',client)
            base=json.loads((RES/f'models/item/{name}.json').read_text())
            self.assertEqual(3,len(base['overrides']))
            for stage in range(3):
                key=f'{name}_pulling_{stage}'
                model=json.loads((RES/f'models/item/{key}.json').read_text())
                self.assertEqual(f'minecraft:item/bow_pulling_{stage}',model['parent'])
                self.assertEqual('dynasty:item/'+key,model['textures']['layer0'])
                self.assertEqual([16,0,0,16],model['elements'][0]['faces']['north']['uv'])
                self.assertEqual([0,0,16,16],model['elements'][0]['faces']['south']['uv'])
                for side,hand in [('righthand',1),('lefthand',-1)]:
                    pose=model['display']['firstperson_'+side]
                    vector=[-1.,0.,0.]
                    def turn(axis,angle):
                        x,y,z=vector
                        s,c=math.sin(math.radians(angle)),math.cos(math.radians(angle))
                        if axis=='x': vector[:]=x,c*y-s*z,s*y+c*z
                        elif axis=='y': vector[:]=c*x+s*z,y,-s*x+c*z
                        else: vector[:]=c*x-s*y,s*x+c*y,z
                    turn('z',pose['rotation'][2]*hand)
                    turn('y',pose['rotation'][1]*hand)
                    turn('x',pose['rotation'][0])
                    turn('y',-45*hand)
                    vector[2]*=1.2
                    turn('z',-9.785*hand)
                    turn('y',35.3*hand)
                    turn('x',-13.935)
                    length=math.sqrt(sum(v*v for v in vector))
                    x,y,z=[v/length for v in vector]
                    self.assertLess(z,-.98,key)
                    self.assertGreater(y,.04,key)
                    self.assertLess(x*hand,-.04,key)
                    self.assertLessEqual(max(pose['scale']),.68)

if __name__=='__main__': unittest.main(verbosity=2)
