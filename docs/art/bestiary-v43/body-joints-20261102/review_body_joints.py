"""Bounded read-only body/animation review. Writes evidence here, never assets."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
A = ROOT / 'src/main/resources/assets/dynasty'
INPUTS = {}

def read(path):
    p = ROOT / path if not isinstance(path, Path) else path
    data = p.read_bytes()
    INPUTS[str(p.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return json.loads(data) if p.suffix == '.json' else data.decode()

ANATOMY = {'pelvis', 'waist', 'chest', 'neck', 'head'} | {
    f'{side}_{part}' for side in ('left', 'right')
    for part in ('upper_arm', 'elbow', 'forearm', 'hand', 'thigh', 'shin', 'foot')}
GROUPS = {
    'swindler': {'garment': {'robe', 'left_cuff', 'right_cuff'}, 'headwear': {'crown'},
                 'back_attachment': set(), 'held_attachment': {'abacus'}},
    'herb_picker': {'garment': {'straps'}, 'headwear': {'hat'},
                    'back_attachment': {'basket'}, 'held_attachment': {'sickle'}}}
BASES = {
    'zuwu_daoshou': {'held': {'weapon_shaft'}, 'back': set()},
    'juma_changqiangbing': {'held': {'weapon_shaft'}, 'back': set()},
    'liannu_zhenzu': {'held': set(), 'back': {'quiver', 'arrow_0', 'arrow_1', 'arrow_2'}},
    'fufa_jijiu': {'held': {'held_talisman'}, 'back': {'talisman_bundle'}},
    'tiesuo_chihou': {'held': {'weapon_shaft'}, 'back': {'small_pouch', 'chain_coil'}},
    'kuijun_sishi': {'held': {'weapon_shaft'}, 'back': {'powder_pack'}}}

def faces(c):
    uv = c.get('uv', c.get('faces'))
    return len(uv) if isinstance(uv, dict) else 6

def sample(track, time, default):
    if track is None: return np.array(default, dtype=float)
    if isinstance(track, list): return np.array(track, dtype=float)
    pairs = sorted((float(t), np.array(v, dtype=float)) for t, v in track.items())
    if time <= pairs[0][0]: return pairs[0][1]
    for (t, v), (s, w) in zip(pairs, pairs[1:]):
        if time <= s: return v + (w-v)*(time-t)/(s-t)
    return pairs[-1][1]

def matrix(pos, rot, scale):
    x, y, z = np.radians(np.array(rot) * [-1, -1, 1])
    cx, cy, cz, sx, sy, sz = math.cos(x), math.cos(y), math.cos(z), math.sin(x), math.sin(y), math.sin(z)
    rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    m = np.eye(4); m[:3,:3] = rz @ ry @ rx @ np.diag(scale)
    m[:3,3] = np.array(pos) * [-1,1,1]
    return m

CORNERS = np.array([[x,y,z] for x in (0,1) for y in (0,1) for z in (0,1)])
EDGES = [(i,j) for i in range(8) for j in range(i+1,8) if np.abs(CORNERS[i]-CORNERS[j]).sum() == 1]

def pose(bones, clip, time):
    world = {}; cubes = []
    def resolve(name):
        if name in world: return world[name]
        b = bones[name]; parent = b.get('parent'); channel = clip.get('bones', {}).get(name, {})
        delta = np.array(b['pivot']) - np.array(bones[parent]['pivot'] if parent else [0,0,0])
        delta = delta + sample(channel.get('position'), time, [0,0,0])
        rot = np.array(b.get('rotation', [0,0,0])) + sample(channel.get('rotation'), time, [0,0,0])
        m = matrix(delta, rot, sample(channel.get('scale'), time, [1,1,1]))
        world[name] = (resolve(parent) if parent else np.eye(4)) @ m
        return world[name]
    for name, b in bones.items():
        m = resolve(name)
        if name not in ANATOMY: continue
        for c in b.get('cubes', []):
            cp = np.array(c.get('pivot', b['pivot']))
            cm = m @ matrix(cp-np.array(b['pivot']), c.get('rotation', [0,0,0]), [1,1,1])
            points = (CORNERS*np.array(c['size'])+np.array(c['origin'])-cp)*[-1,1,1]
            points = points @ cm[:3,:3].T + cm[:3,3]
            cubes.append((name, points))
    return world, cubes

def font(size):
    return ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', size)

def diagram(ident, bones, clipname, clip, time):
    world, cubes = pose(bones, clip, time)
    im = Image.new('RGB', (1000,600), '#eeeae0'); d = ImageDraw.Draw(im)
    d.text((20,12), f'{ident} / {clipname} / {time*20:.1f} tick', font=font(22), fill='#29373c')
    for column, (yaw, title) in enumerate(((0, '正面'), (90, '侧面'))):
        a = math.radians(yaw); right = np.array([math.cos(a),0,math.sin(a)])
        def project(p): return (column*500+250+float(p@right)*14, 510-p[1]*14)
        d.line((column*500+25,510,column*500+475,510), fill='#8f9998', width=2)
        for name, pts in cubes:
            col = '#445a67' if 'arm' not in name and 'hand' not in name and 'elbow' not in name else '#a05b35'
            for i,j in EDGES: d.line((*project(pts[i]),*project(pts[j])), fill=col, width=2)
        for side in ('left','right'):
            chain=[f'{side}_{part}' for part in ('upper_arm','elbow','forearm','wrist','hand')]
            for parent,child in zip(chain,chain[1:]):
                d.line((*project(world[parent][:3,3]),*project(world[child][:3,3])),fill='#b22245',width=3)
            for name in chain:
                x,y=project(world[name][:3,3]);d.ellipse((x-3,y-3,x+3,y+3),fill='#b22245')
        d.text((column*500+20,55), title+' · 固定比例 · 仅身体与关节',font=font(18),fill='#29373c')
    d.text((20,548),'原几何的离线线框诊断；省略服制/挂件仅用于分项检查，运行资产全部保留。',font=font(16),fill='#29373c')
    d.text((20,575),'无PNG材质、无遮挡判定、非游戏截图；不能证明触地、穿插或原生动画混合通过。',font=font(15),fill='#29373c')
    return im

def main():
    receipt={'recorded_utc':datetime.now(timezone.utc).isoformat(),
             'status':'BOUNDED_BODY_JOINT_REVIEW_NOT_RUNTIME_ACCEPTANCE', 'entities':[], 'baselines':[],
             'production_changes':0,'external_semantic_credit_added':0,'game_or_java_started':False}
    for p in ['docs/cod4/request.txt', 'docs/cod4/audit-20261022/attachment-interface-handoff-20261102.json',
              'docs/art/armor-worn-uv-20261102/attachment-handoff-received.json',
              'src/main/java/com/dynasty/expansion/ExpansionClient.java',
              'src/main/java/com/dynasty/expansion/SecondaryMob.java',
              'src/main/java/com/dynasty/expansion/SecondaryMobs.java',
              'src/main/java/com/dynasty/client/steve/SteveFighterModel.java',
              'src/main/java/com/dynasty/client/steve/SteveFighterRenderer.java',
              'src/main/java/com/dynasty/client/steve/SteveFighterBindings.java',
              'tools/art/secondary-cuboid/build_humans.py']:
        read(p)
    for ident, roots in BASES.items():
        j=read(A/f'models/entity/steve_fighters/{ident}.json');parts={p['name']:p for p in j['parts']}
        def descendants(rootset):
            answer=set(rootset)
            while True:
                new=answer|{n for n,p in parts.items() if p['parent'] in answer}
                if new==answer:return answer
                answer=new
        held,back=descendants(roots['held']),descendants(roots['back'])
        count=lambda names:sum(faces(parts[n]) for n in names)
        receipt['baselines'].append({'id':ident,'role':j['role'],'scale':j['scale'],
          'all_embedded_quads':count(parts),'anatomical_quads':count({'head','body','right_arm','left_arm','right_leg','left_leg'}),
          'held_embedded_quads':count(held),'carried_embedded_quads':count(back),
          'body_and_worn_quads':count(set(parts)-held-back),
          'held_parts':sorted(held),'carried_parts':sorted(back),
          'limits':'Candidate only, not unique accepted profession baseline; external ItemStack/layer quads excluded.'})
    sample_rows=[]
    for ident, categories in GROUPS.items():
        g=read(A/f'geo/secondary/{ident}.geo.json')['minecraft:geometry'][0]
        anim=read(A/f'animations/secondary/{ident}.animation.json')['animations']
        tex=A/f'textures/entity/secondary/{ident}.png'
        INPUTS[str(tex.relative_to(ROOT))]=hashlib.sha256(tex.read_bytes()).hexdigest()
        names=[b['name'] for b in g['bones']];bones={b['name']:b for b in g['bones']}
        unknown=set(bones)-ANATOMY-set().union(*categories.values())
        assert all(not bones[n].get('cubes') for n in unknown), unknown
        counts={group:sum(faces(c) for n in ns for c in bones[n].get('cubes',[]))
                for group,ns in {'anatomy':ANATOMY,**categories}.items()}
        total=sum(counts.values());body=total-counts['held_attachment']-counts['back_attachment']
        skeleton_errors=[]
        for n,b in bones.items():
            if b.get('parent') and b['parent'] not in bones:skeleton_errors.append([n,'missing_parent'])
            seen={n};parent=b.get('parent')
            while parent in bones:
                if parent in seen:skeleton_errors.append([n,'cycle']);break
                seen.add(parent);parent=bones[parent].get('parent')
        clips=[];endpoint_changes=[]
        for name,clip in anim.items():
            missing=sorted(set(clip['bones'])-set(bones));assert not missing,missing
            duration=clip['animation_length'];times=sorted(set(np.linspace(0,duration,61).tolist()+[
                float(t) for channels in clip['bones'].values() for track in channels.values()
                if isinstance(track,dict) for t in track]))
            seams=[];ranges={}
            for n,channels in clip['bones'].items():
                for channel,track in channels.items():
                    default=[1,1,1] if channel=='scale' else [0,0,0]
                    first=sample(track,0,default);last=sample(track,duration,default)
                    if not np.allclose(first,last):seams.append({'bone':n,'channel':channel,'delta':(last-first).tolist()})
                    values=np.stack([sample(track,t,default) for t in times])
                    ranges[n+'.'+channel]={'min':values.min(0).tolist(),'max':values.max(0).tolist()}
            contacts=[]
            for time in times:
                world,cubes=pose(bones,clip,time);assert all(np.isfinite(p).all() for _,p in cubes)
                for side in ('left','right'):
                    # Shared bind-space surface point, transformed through each neighbour.
                    # This tests seam-transform agreement, not whole-surface contact or collision.
                    for parent,child,point in [('upper_arm','elbow',[4 if side=='left' else -4,15,0]),
                                               ('elbow','forearm',[4 if side=='left' else -4,14,0]),
                                               ('forearm','hand',[4 if side=='left' else -4,10,0])]:
                        pn,cn=f'{side}_{parent}',f'{side}_{child}'
                        def transform_point(n):
                            q=(np.array(point)-np.array(bones[n]['pivot']))*[-1,1,1]
                            return world[n][:3,:3]@q+world[n][:3,3]
                        gap=float(np.linalg.norm(transform_point(pn)-transform_point(cn)))
                        contacts.append(gap)
                hand=world['right_hand'][:3,3]
                feet=np.concatenate([p for n,p in cubes if n.endswith('_foot')])
                sample_rows.append({'id':ident,'clip':name,'seconds':round(time,8),
                    'right_hand_software_model_units':hand.tolist(),'feet_min_y':float(feet[:,1].min())})
            for side in ('left','right'):
                path=[f'{side}_{x}' for x in ('upper_arm','elbow','forearm','wrist','hand')]
                endpoint_changes.append({'clip':name,'side':side,'direct_channels':{
                  n:clip['bones'].get(n,{}) for n in path},
                  'note':'Absent direct track inherits all ancestor transforms; not frozen hand.'})
            clips.append({'name':name,'duration_seconds':duration,'loop':clip.get('loop'),
                'samples':len(times),'missing_bones':missing,'loop_endpoint_mismatches':seams,
                'max_shared_surface_point_separation_units':max(contacts),'channel_ranges':ranges})
        outlines={n:[c['size'] for c in bones[n].get('cubes',[])] for n in ('head','chest','waist','pelvis','left_upper_arm','left_forearm','left_hand','left_foot')}
        comparisons=[{'candidate':b['id'],'all_model_delta':total-b['all_embedded_quads'],
                      'body_worn_delta':body-b['body_and_worn_quads']} for b in receipt['baselines']]
        row={'id':ident,'bones':len(bones),'cubes':sum(len(b.get('cubes',[])) for b in bones.values()),
          'quad_partition':counts,'all_embedded_quads':total,'body_and_worn_quads':body,
          'partition_is_accounting_only_no_parts_removed':True,'outline_sizes_units':outlines,
          'anatomical_height_units':28,'anatomical_height_nominal_blocks':1.75,
          'not_exact_six_steve_body_cuboids':True,'anatomical_cuboids':19,
          'collision_declared_blocks':[0.6,1.8],'skeleton_errors':skeleton_errors,
          'duplicate_bone_names':len(names)!=len(set(names)), 'clips':clips,'joint_tracks':endpoint_changes,
          'candidate_comparisons':comparisons}
        receipt['entities'].append(row)
        for clipname in ('idle','wander','flee','special'):
            clip=anim[clipname];duration=clip['animation_length']
            frames=[diagram(ident,bones,clipname,clip,float(t)) for t in np.linspace(0,duration,max(3,round(duration*20)+1))]
            frames[0].save(OUT/f'{ident}-{clipname}.webp',save_all=True,append_images=frames[1:],
                duration=50,loop=0,lossless=True)
            strip=Image.new('RGB',(2000,1200),'#eeeae0')
            for i,t in enumerate(np.linspace(0,duration,4)):
                strip.paste(diagram(ident,bones,clipname,clip,float(t)),((i%2)*1000,(i//2)*600))
            strip.save(OUT/f'{ident}-{clipname}-frames.png')
    receipt['findings']=[
      '192/180 remain the authored full embedded model totals. Accounting subtraction is not a runtime optimisation.',
      'Swindler anatomy114 + garments30 + headwear12 + held36 =192; body with worn garments/headwear156.',
      'Herb picker anatomy114 + straps12 + hat12 + basket24 + sickle18 =180; body with straps/hat138.',
      'Zuwu156 includes60 authored weapon quads; equivalent body+worn comparison is96, not156. No unique neutral profession baseline is declared.',
      'Both current bodies have19 anatomical cubes and segmented elbows/knees, not the accepted standard six-cube Steve construction. Preserve current approved art; any redesign remains gated.',
      'No wrist/hand direct animation channels. Shoulder rotation carries the hand; right elbow animates attack/special. This is not evidence of an immobile hand.',
      'Swindler special is the same arm/chest gesture as the generic special template while source selects special before exposure. Identity/gesture match needs visual and runtime acceptance, not a new damage change.',
      'All19 clips are declared loop=true. Derived attack aliases are not19 independent reviewed actions. Non-combatant reachability must not be inferred from file presence.'
    ]
    receipt['limits']=[
      'Python serial matrix/linear-track diagnostic only: no GeckoLib controller blending, easing, look override, game tick interpolation or renderer root pose reconstructed.',
      'Shared-point agreement does not prove all-surface contact, absence of intersections, foot placement or support; foot motion needs actual client inspection.',
      'Wireframe diagnostic omits garments/props only in evidence rendering. No production geometry, atlas, UV, animation or accessory changed.',
      'Declared quads are not visible GPU triangles or measured frame time; external equipped ItemStacks/render layers excluded from both columns.',
      '1000 applicable different semantic references not established by this local QA; zero research credit. No fixes generated.',
      'No current native bake, game,20-mob performance, acquisition/quest acceptance, checklist deletion, shared JAR install or push.'
    ]
    receipt['input_sha256']=INPUTS
    receipt['all_inputs_unchanged_during_check']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in INPUTS.items())
    assert receipt['all_inputs_unchanged_during_check']
    (OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    (OUT/'joint-samples.json').write_text(json.dumps(sample_rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'inputs':len(INPUTS),'pose_samples':len(sample_rows),
      'entities':[{k:e[k] for k in ('id','quad_partition','all_embedded_quads','body_and_worn_quads')} for e in receipt['entities']]},ensure_ascii=False))

if __name__=='__main__':main()
