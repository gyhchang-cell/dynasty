"""Source-only bind/last-key skin observation, no interpolation or native runtime."""
from pathlib import Path
import json,math
B=Path(__file__).resolve().parent
mesh=json.loads((B/'sources/hoglin.json').read_text())
tracks=json.loads((B/'sources/hoglin-death.json').read_text())['animation']
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def mv(a,v):return [sum(x*y for x,y in zip(row,v)) for row in a]
def mat(v):return [v[i:i+4] for i in range(0,16,4)]
def inv(a):
    b=[list(row)+[float(i==j) for j in range(4)] for i,row in enumerate(a)]
    for i in range(4):
        k=max(range(i,4),key=lambda k:abs(b[k][i]));b[i],b[k]=b[k],b[i]
        d=b[i][i];assert abs(d)>1e-9;b[i]=[x/d for x in b[i]]
        for j in range(4):
            if i!=j:
                d=b[j][i];b[j]=[x-d*y for x,y in zip(b[j],b[i])]
    return [r[4:] for r in b]
I=[[float(i==j) for j in range(4)] for i in range(4)]
C=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]] # Blender Z up -> Minecraft Y up
local={};parents={}
def walk(node,parent=None):
    name=node['name'];local[name]=mat(node['transform']);parents[name]=parent
    for child in node.get('children',[]):walk(child,name)
walk(mesh['armature']['hierarchy'][0])
assert set(local)==set(x['name'] for x in tracks)
end={x['name']:mat(x['transform'][-1]) for x in tracks}
assert all(x['time'][-1]==0.8333 for x in tracks)
def globals_for(vals):
    cache={}
    def g(n):
        if n not in cache:cache[n]=mm(g(parents[n]) if parents[n] else C,vals[n])
        return cache[n]
    for n in vals:g(n)
    return cache
bg=globals_for(local);eg=globals_for(end)
v=mesh['vertices'];pos=v['positions']['array'];counts=v['vcounts']['array'];indices=v['vindices']['array'];weights=v['weights']['array'];names=mesh['armature']['joints']
assert len(counts)==len(pos)//3==132 and set(counts)=={1,2}
assert sum(counts)*2==len(indices)
skin={n:mm(eg[n],inv(bg[n])) for n in names}
bind=[];dead=[];max_bind_error=0;offset=0
weight_sums=[]
for i,count in enumerate(counts):
    p=mv(C,pos[3*i:3*i+3]+[1]);bind.append(p[:3]);q=[0.,0.,0.,0.];ws=0
    for j in range(count):
        ji,wi=indices[2*offset:2*offset+2];offset+=1;w=weights[wi];ws+=w
        value=mv(skin[names[ji]],p);q=[x+w*y for x,y in zip(q,value)]
        test=mv(mm(bg[names[ji]],inv(bg[names[ji]])),p)
        max_bind_error=max(max_bind_error,max(abs(a-b) for a,b in zip(test,p)))
    assert abs(ws-1)<1e-8;weight_sums.append(ws);dead.append(q[:3])
assert offset*2==len(indices) and max_bind_error<1e-9
parts={}
for n,part in v['parts'].items():
    ids=sorted(set(part['array'][0::3]));assert all(0<=i<144 for i in ids)
    parts[n]={'unique_vertex_count':len(ids),'bind_y_range':[min(bind[i][1] for i in ids),max(bind[i][1] for i in ids)],'terminal_y_range':[min(dead[i][1] for i in ids),max(dead[i][1] for i in ids)]}
report={'scope':'OFFLINE_LAST_KEY_RAW_MATRIX_SKIN_APPROXIMATION_NOT_NATIVE_CONTACT_ACCEPTANCE','time_seconds':0.8333,'reference_candidates_not_frames':1,'joint_channels_not_references':len(tracks),'vertex_count':len(counts),'vertices_with_two_weights':counts.count(2),'source_coordinate_conversion':'Rx(-90deg) at root and vertex positions; original JSON row matrices; loader inverse local canceled by local bind on exact key; parent products and inverse global bind skin.','assumptions':['Only death pose, no transition blend/additional layers; adult neutral yaw/scale, nominal groundY0.','132 vertices, vcounts1/2 and weight sums1 validated; pair reading and weighted skin checked in actual SkinnedMesh44–78/140–155/193–219.','Uses raw end matrices; native decomposes/normalizes quaternion/recomposes, so small rounding differences not modeled.','Source1.21.1 NeoForge not Dynasty1.20.1 Forge; no library update or code copied.','No native terrain/collision/renderer full hook acceptance; optional vanilla-part transforms omitted; adult only (baby has Head1.25 plus global0.5).'], 'identity_bind_max_abs_error':max_bind_error,'parts':parts,'joint_end_positions':{n:[eg[n][i][3] for i in range(3)] for n in names},'new_accepted_credit':0}
(B/'hoglin-terminal-observation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Same-scale side views of actual triangle geometry, gray source diagram, not textured preview.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620"><rect width="1200" height="620" fill="#f1f1ed"/>']
for panel,pts,label in [(0,bind,'SOURCE BIND'),(1,dead,'SOURCE LAST KEY 0.8333 s')]:
    ox=300+600*panel;oy=510;scale=108
    svg.append(f'<text x="{ox-245}" y="32" font-family="sans-serif" font-size="18">{label}</text><line x1="{ox-280}" y1="{oy}" x2="{ox+280}" y2="{oy}" stroke="#aa6666"/>')
    triangles=[]
    for name,part in v['parts'].items():
        ids=part['array'][::3]
        assert len(ids)%3==0
        for k in range(0,len(ids),3):
            ps=[pts[i] for i in ids[k:k+3]];triangles.append((sum(p[0] for p in ps),ps))
    for _,ps in sorted(triangles):
        coords=' '.join(f'{ox+p[2]*scale:.3f},{oy-p[1]*scale:.3f}' for p in ps)
        svg.append(f'<polygon points="{coords}" fill="#939b9f" stroke="#48545b" stroke-width="0.6"/>')
svg.append('<text x="22" y="590" font-family="sans-serif" font-size="14">OFFLINE SOURCE MESH / NO TEXTURE / NO GAME / nominal floor Y=0 / same scale / no contact certification</text></svg>')
(B/'hoglin-source-side.svg').write_text('\n'.join(svg))
print(json.dumps({'parts':parts,'bind_identity_error':max_bind_error},indent=2))
# Separate disconnected geometry inside the author-named head mesh part.
# These indices are geometry components, not invented author semantic names.
ids=v['parts']['head']['array'][::3];adj={i:set() for i in ids}
for k in range(0,len(ids),3):
    for i in ids[k:k+3]:adj[i].update(ids[k:k+3])
seen=set();components=[]
for i in sorted(adj):
    if i in seen:continue
    todo=[i];component=set()
    while todo:
        j=todo.pop()
        if j in component:continue
        component.add(j);todo.extend(adj[j]-component)
    seen.update(component);row={'indices':sorted(component)}
    for label,pts in [('bind',bind),('dead',dead)]:
        row[label+'_xyz_bounds']=[[min(pts[j][a] for j in component),max(pts[j][a] for j in component)] for a in range(3)]
    components.append(row)
(B/'head-component-observation.json').write_text(json.dumps({'scope':'source-connected-components-not-auto-semantic-labels','components':components},indent=2)+'\n')
