"""Original cuboid art for Dynasty's existing 74-bone Ghost Carriage Bird.

Run from any directory with Python + Pillow. No combat source is generated.
The captured pre-art rig is the compatibility contract, not a third-party asset.
"""
import copy
import json
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
ASSETS = REPO / 'src/main/resources/assets/dynasty'
SOURCE = REPO / 'docs/art/guiche-v2/source'
ID = 'guiche_jiushouniao'
GEO = ASSETS / f'geo/blueprint/elite/{ID}.geo.json'
ANIM = ASSETS / f'animations/blueprint/elite/{ID}.animation.json'
TEX = ASSETS / f'textures/entity/blueprint/elite/{ID}.png'
PALETTE = ['#ffffff', '#793e4b', '#292631', '#78727b']
PORTRAIT = ['WGWGWGW', 'DRDRDRD', 'WGWGWGW', 'RGRDRGR',
            'DDRRRDD', 'GGDRDGG', '..DDD..']
ISLANDS = {}


def make_atlas():
    # A front-facing eight-head bird portrait, seven 2x2 cells across with a
    # one-pixel pure-white border. Mesh faces reuse the actual colour islands.
    im = Image.new('RGB', (16, 16), 'white')
    d = ImageDraw.Draw(im)
    colors = dict(zip('WRDG', PALETTE))
    for y,row in enumerate(PORTRAIT):
        for x,key in enumerate(row):
            if key == '.': continue
            at = [1+2*x, 1+2*y]
            d.rectangle((*at, at[0]+1, at[1]+1), fill=colors[key])
            ISLANDS.setdefault(key, at)
    TEX.parent.mkdir(parents=True, exist_ok=True)
    im.save(TEX)


def uv(tile):
    key = {0:'W',1:'R',2:'D',3:'G',4:'R',5:'G',6:'W',7:'W',
           8:'D',9:'D',10:'R',11:'G',12:'R'}[tile]
    return {'uv': ISLANDS[key].copy(), 'uv_size': [2, 2]}


def cube(origin, size, tile, faces=None):
    return dict(origin=origin, size=size, uv={f: uv((faces or {}).get(f, tile))
                for f in ('north', 'south', 'east', 'west', 'up', 'down')})


def channel(points, kind='rotation'):
    return {kind: {f'{t:g}': v for t, v in sorted(points)}}


def main():
    make_atlas()
    original = json.loads((SOURCE/'original.geo.json').read_text())
    geo = copy.deepcopy(original)
    bones = geo['minecraft:geometry'][0]['bones']
    by = {b['name']: b for b in bones}
    def set_bone(name, pivot, cubes, rotation=None):
        b = by[name]
        b.update(pivot=pivot, cubes=cubes)
        b.pop('rotation', None)
        if rotation and any(rotation):
            b['rotation'] = rotation
    set_bone('body', [0, 14, 0], [
        cube([-7, 10, -7], [14, 11, 16], 4),
        cube([-4.5, 6, -3], [9, 6, 14], 2),
        cube([-5.5, 12.2, 7], [11, 6, 8], 5),
        cube([-9, 18, -4], [18, 5, 10], 5),
        cube([-5, 21, -2], [10, 3, 10.8], 4),
        cube([-3, 23, 1], [6, 2, 7], 5),
        cube([-6, 16, -9], [12, 4, 3], 1),
        cube([-8, 19, -8], [5, 3, 5], 0),
        cube([3, 19, -8], [5, 3, 5], 0),
        cube([-4, 20.1, -8.1], [8, 2.1, 4.1], 3),
    ])
    tail = [cube([-4, 12, 12], [8, 3, 11], 4)]
    for n, length in enumerate([18, 25, 29, 25, 18]):
        x = (n-2)*2
        tail.append(cube([x-1, 11-(n%2)*.5, 19], [2, 1.5, length], 5 if n%2 else 4))
        tail.append(cube([x-1.05, 10.7-(n%2)*.5, 19+length-3.9], [2.1, 1, 4], 2))
    set_bone('tail', [0, 14, 12], tail, [8, 0, 0])
    for side, sign in [('left', 1), ('right', -1)]:
        def mirrored(at, size, tile, faces=None):
            at = list(at)
            if sign < 0:
                at[0] = -at[0]-size[0]
            return cube(at, size, tile, faces)
        wing = [mirrored([7, 18, -4], [12, 4, 11], 5),
                mirrored([10, 17, 4], [13, 2, 10], 4),
                mirrored([16, 18, -2], [8, 3, 10], 5)]
        for i in range(3):
            wing.append(mirrored([9+i*4, 16.5, 10], [3, 1.5, 10-i], 4))
        set_bone(side+'_wing', [sign*7, 19, 0], wing)
        set_bone(side+'_wing_tip', [sign*23, 19, 0], [
            mirrored([22, 18, -2], [11, 2, 9], 5),
            mirrored([28, 17, 2], [11.8, 2, 6], 4),
            mirrored([32, 16.9, 0], [8, 1.6, 4], 2)])
        for n in range(5):
            x, z, length = 20+n*4, 6+n*.4, 22-n*3
            set_bone(f'{side}_feather_{n}', [sign*(x+2), 18, z], [
                mirrored([x, 16.5, z], [3.5, 1.5, length], 5 if n%2 else 4),
                mirrored([x+.5, 16, z+length-5], [2.5, 1, 7], 2)])
        set_bone(side+'_leg', [sign*5, 9, 3], [
            cube([sign*5-2, 5, 2], [4, 6, 5], 4),
            cube([sign*5-1, 1.1, 3], [2, 4.9, 1.9], 3),
            cube([sign*5-1.5, 1, 1], [3, 1.5, 4], 0)])
        for n in range(3):
            x = sign*5+(n-1)*1.5
            set_bone(f'{side}_claw_{n}', [x, 1, 2], [
                cube([x-.5, .5, -3], [1, 1, 5.5], 0),
                cube([x-.55, 0, -4], [1.1, 1, 2], 2)])
    set_bone('central_stump', [0, 22, -7], [
        cube([-2, 22, -9], [4, 8, 4], 6),
        cube([-2.5, 29, -9.5], [5, 1.5, 5], 1, {'up':12}),
        cube([-1, 25, -9.5], [2, 4, .5], 1)])
    # Staggered heights and bent segments break the old straight fan silhouette.
    fans = [-48, -33, -20, -8, 8, 20, 33, 48]
    for n, fan in enumerate(fans):
        k = min(n, 7-n)
        x, y, z = (n-3.5)*2, 21, [-3,-6,-1,-4,-4,-1,-6,-3][n]
        a, b, c = 6+k, 6+k, 5+k*.5
        mid_z = (1 if n < 4 else -1)*(12-k*3)
        tip_z = (1 if n < 4 else -1)*5
        rx, mx, tx = [18,-8,12,-4,4,10,-10,16][n], -24, 12
        set_bone(f'neck_{n}_base', [x,y,z], [
            cube([x-1.5,y,z-1.5], [3,a,3], 6),
            cube([x-2,y-.1,z-2], [4,2.1,4], 1)], [rx,0,fan])
        set_bone(f'neck_{n}_middle', [x,y+a,z], [
            cube([x-1.25,y+a,z-1.25], [2.5,b,2.5], 6),
            cube([x-1.5,y+a+1,z-1.5], [3,2,3], 3)], [mx,0,mid_z])
        set_bone(f'neck_{n}_tip', [x,y+a+b,z], [
            cube([x-1,y+a+b,z-1], [2,c,2], 0),
            cube([x-1,y+a+b+1,z-1.3], [2,2,.3], 1)], [tx,0,tip_z])
        h = y+a+b+c
        set_bone(f'face_{n}', [x,h,z], [
            cube([x-2,h-1,z-2], [4,5,3.5], 0, {'north':7,'south':8}),
            cube([x-1.5,h-2,z-2], [3,1,3], 0),
            cube([x-2.3,h+3,z-2.25], [4.6,1.5,4.25], 8),
            cube([x-2.3,h-2.1,z+.5], [1,6.2,2], 8),
            cube([x+1.3,h-2.1,z+.5], [1,6.2,2], 8),
            cube([x-1.6,h+1,z-2.2], [1.2,.7,.3], 2),
            cube([x+.4,h+1,z-2.2], [1.2,.7,.3], 2),
            cube([x-1.3,h-.4,z-2.2], [.6,1.2,.3], 1),
            cube([x+.7,h-.4,z-2.2], [.6,1.2,.3], 1),
        ], [-(rx+mx+tx), 0, -(fan+mid_z+tip_z)])
        set_bone(f'beak_{n}', [x,h,z-2], [
            cube([x-.8,h-1,z-5], [1.6,1.4,3], 3),
            cube([x-.65,h-1.8,z-5.1], [1.3,1.4,1.1], 2)])
        set_bone(f'jaw_{n}', [x,h-1.3,z-2], [cube([x-.6,h-1.9,z-4.6], [1.2,.6,2.6],1)])
    description = geo['minecraft:geometry'][0]['description']
    description.update(texture_width=16, texture_height=16,
                       visible_bounds_width=8, visible_bounds_height=7,
                       visible_bounds_offset=[0,1.5,.5])
    animations = copy.deepcopy(json.loads((SOURCE/'original.animation.json').read_text()))
    clips = animations['animations']
    def clip(name): return clips[f'animation.{ID}.{name}']['bones']
    fly = clip('fly')
    for side, sign in [('left',1),('right',-1)]:
        fly[side+'_wing'] = channel([(0,[0,0,sign*12]),(.3,[0,0,-sign*19]),(.6,[0,0,-sign*10]),(.9,[0,0,sign*9]),(1.2,[0,0,sign*12])])
        fly[side+'_wing_tip'] = channel([(0,[0,0,sign*8]),(.35,[0,0,-sign*13]),(.7,[0,0,sign*3]),(1.2,[0,0,sign*8])])
        for n in range(5):
            fly[f'{side}_feather_{n}'] = channel([(0,[2+n,0,0]),(.4,[-5-n,0,0]),(.8,[3+n,0,0]),(1.2,[2+n,0,0])])
    for n in range(8):
        fly[f'neck_{n}_middle'] = channel([(0,[0,-2,0]),(.3,[2,0,(-1)**n*2]),(.6,[0,2,0]),(.9,[-2,0,-(-1)**n*2]),(1.2,[0,-2,0])])
    clip('stunned')['body'] = channel([(0,[0,0,12]),(.5,[0,0,-12]),(1,[0,0,12]),(1.5,[0,0,-12]),(2,[0,0,12])])
    # Contact peaks, rather than wind-up poses, land on the server's exact frames.
    peck = clip('peck')
    for n in range(8):
        points = [(0,[0,0,0])]
        for strike in (n,n+8):
            t = (12+strike*4)/20
            points += [(max(0,t-.15),[18,0,0]),(t,[138,0,0]),(t+.1,[28,0,0])]
        points += [(3.85,[18,0,0]),(4.85,[0,0,0])]
        peck[f'neck_{n}_base'] = channel(points)
    # Preserve the blood launch at 20 ticks and dive fold at 24 ticks.
    for side,sign in [('left',1),('right',-1)]:
        clip('bomb')[side+'_wing_tip'] = channel([(0,[0,0,0]),(.8,[0,0,sign*20]),(1,[0,0,-sign*8]),(2.55,[0,0,0])])
        clip('dive')[side+'_wing_tip'] = channel([(0,[0,0,0]),(1.2,[0,sign*18,sign*22]),(2.7,[0,sign*18,sign*22]),(3.7,[0,0,0]),(5.7,[0,0,0])])
    # A compressed asymmetric carcass, not a 90-degree tumble through the floor.
    death = {
        'body': channel([(0,[0,0,0]),(.5,[10,-6,8]),(1,[4,0,-7]),(1.5,[7,5,9]),(2,[0,5,7]),(5,[0,5,7])]),
        'tail': channel([(0,[0,0,0]),(.6,[-12,8,0]),(1.4,[-10,-6,4]),(2,[-15,10,-3]),(5,[-15,10,-3])]),
    }
    death['body'].update(channel([(0,[0,0,0]),(.6,[0,-1,0]),(1.6,[0,-4.4,0]),(2,[0,-4.7,0]),(5,[0,-4.7,0])],'position'))
    for side,sign in [('left',1),('right',-1)]:
        wing_fold = 18 if side == 'left' else 24
        tip_fold = 24 if side == 'left' else 22
        death[side+'_wing'] = channel([(0,[0,0,0]),(.5,[0,0,sign*38]),(1.1,[5,sign*10,sign*10]),(2,[0,sign*18,sign*wing_fold]),(5,[0,sign*18,sign*wing_fold])])
        death[side+'_wing_tip'] = channel([(0,[0,0,0]),(.8,[0,0,-sign*5]),(2,[0,sign*24,-sign*tip_fold]),(5,[0,sign*24,-sign*tip_fold])])
        death[side+'_leg'] = channel([(0,[0,0,0]),(.8,[-45,0,sign*8]),(2,[-65,0,sign*12]),(5,[-65,0,sign*12])])
        death[side+'_leg'].update(channel([(0,[0,0,0]),(.8,[0,1,0]),(2,[0,3,0]),(5,[0,3,0])],'position'))
    for n in range(8):
        b = by[f'neck_{n}_base']['rotation']; m = by[f'neck_{n}_middle']['rotation']; tip = by[f'neck_{n}_tip']['rotation']
        # The necks settle forward onto the ground in a spreading, readable bundle.
        base_final = [114-b[0],0,-b[2]+(n-3.5)*4]
        middle_final = [16-m[0],0,-m[2]]
        tip_final = [-22-tip[0],0,-tip[2]]
        death[f'neck_{n}_base'] = channel([(0,[0,0,0]),(.6,[15,0,(-1)**n*8]),(1.4,[v*.8 for v in base_final]),(2.2,base_final),(5,base_final)])
        death[f'neck_{n}_middle'] = channel([(0,[0,0,0]),(1,[20,0,0]),(2.2,middle_final),(5,middle_final)])
        death[f'neck_{n}_tip'] = channel([(0,[0,0,0]),(2.2,tip_final),(5,tip_final)])
        death[f'face_{n}'] = channel([(0,[0,0,0]),(2.2,[10,0,(n-3.5)*3]),(5,[10,0,(n-3.5)*3])])
        death[f'jaw_{n}'] = channel([(0,[0,0,0]),(1,[20,0,0]),(2.2,[12,0,0]),(5,[12,0,0])])
    clip('death').clear(); clip('death').update(death)
    assert [(b['name'],b.get('parent')) for b in bones] == [(b['name'],b.get('parent')) for b in original['minecraft:geometry'][0]['bones']]
    GEO.write_text(json.dumps(geo,indent=2)+'\n')
    ANIM.write_text(json.dumps(animations,indent=2)+'\n')
    print(f'{len(bones)} unchanged bone identities / {sum(len(b.get("cubes",[])) for b in bones)} cuboids / {len(clips)} clips / 4-colour atlas')


if __name__ == '__main__':
    main()
