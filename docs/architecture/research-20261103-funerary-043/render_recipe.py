"""Research diagram of authored placement envelope, not a generated/game asset."""
import json
from collections import Counter, deque
from zipfile import ZipFile
from read_recipe import OUT, ROOT, read, sha
from whole_building_candidates import AIR, iso, plans
from PIL import Image, ImageDraw

def main():
    src=json.loads((OUT/'recipe-source.json').read_text());templates={}
    with ZipFile(src['source_archive']) as z:
        for item in src['templates']:
            n=read(z.read(item['member']));pal=n['palette']
            templates[item['member'].rsplit('/',1)[1][:-4]]=(n,{tuple(b['pos']):pal[b['state']] for b in n['blocks']})
    base,bs=templates['graveyard'];gn,gs=templates['grave_full']
    # Normalize the averaged-ground startPos to (0,0,0), NONE rotation/mirror.
    base_origin=(1,-1,0);start=(1,1,0);inner=(3,1,2);inner_size=(17,0,8);fixed_size=(15,0,8)
    origins=[(inner[0]+x,inner[1]-2,inner[2]+z) for x in range(0,fixed_size[0]+1,5)
             for z in range(0,fixed_size[2]+1,2) if x!=inner_size[0]//2 and z!=inner_size[2]//2]
    assert len(origins)==16
    states={tuple(p[i]+base_origin[i] for i in range(3)):s for p,s in bs.items()}
    # Full is one selected reference glyph used at each slot solely to read spacing.
    # It is NOT a seed, not an actual outcome and not proof of surviving processors.
    overwritten=[]
    for origin in origins:
        for p,s in gs.items():
            q=tuple(p[i]+origin[i] for i in range(3))
            if q in states and states[q]!=s:overwritten.append(dict(position=q,old=states[q],new=s))
            states[q]=s
    cells={p:s['Name'] for p,s in states.items() if s['Name'] not in AIR}
    # Image coordinates shift X=-1,Y=+1; underlying evidence stays in source space.
    image_cells={(x-1,y+1,z):n for (x,y,z),n in cells.items()}
    raw_cells={p:s['Name'] for p,s in bs.items() if s['Name'] not in AIR}
    sheet=Image.new('RGB',(1520,1400),'#edf0f2')
    for col,rotation in enumerate((0,1)):
        sheet.paste(iso(raw_cells,base['size'],rotation,'D010 original base ONLY; no processor'),(col*760,0))
        sheet.paste(iso(image_cells,(22,4,13),rotation,'D010 authored-slot diagram; Full glyph x16; NOT a seed'),(col*760,680))
    ImageDraw.Draw(sheet).text((18,1368),'STRUCTURAL RESEARCH / air writes honored / webs, traps, actors, terrain NOT simulated / cubes not collision',fill='#17252c')
    sheet.save(OUT/'D010-base-and-layout.png')
    pl=plans(image_cells,(22,4,13),1,'D010 RECIPE DIAGRAM (image y=source y+1; x=source x-1)')
    pl.save(OUT/'D010-layout-sections.png')
    # Original fence layer exact perimeter, before any random processor.
    fence=sorted(p for p,s in bs.items() if s['Name']=='twilightforest:canopy_fence')
    perimeter={(x,2,z) for x in range(22) for z in range(13) if x in (0,21) or z in (0,12)}
    closed=set(fence)==perimeter
    report=dict(old_identity='COD4-R004-D010',diagram_is_not_native_generated_instance=True,
        source_archive_sha256=src['source_archive_sha256'],rotation='NONE',mirror='NONE',
        normalized_average_ground_start=[0,0,0],base_origin=base_origin,start=start,inner=inner,
        inner_size=inner_size,fixed_size=fixed_size,grave_origins=origins,grave_slot_count=len(origins),
        illustration_grave_glyph='grave_full',all_full_random_outcome_or_seed_verified=False,
        explicit_air_writes_honored=True,overwrite_changes=overwritten,
        raw_fence_positions=fence,raw_fence_is_closed_perimeter=closed,raw_fence_count=len(fence),
        raw_template_door_or_gate_count=sum('door' in s['Name'] or 'gate' in s['Name'] for s in bs.values()),
        raw_template_jigsaw_count=sum(s['Name']=='minecraft:jigsaw' for s in bs.values()),
        raw_grave_blocks={k:[dict(position=p,state=s) for p,s in ss.items()] for k,(n,ss) in templates.items() if k!='graveyard'},
        diagram_material_counts=dict(Counter(cells.values())),diagram_occupied_bounds=[[min(p[i] for p in cells),max(p[i] for p in cells)] for i in range(3)],
        limitations=['Full仅重复表示作者墓位间距，不宣称存在对应种子或这是实际生成结果。',
            '未执行WebTemplateProcessor；该同版本类用process第二个BlockPos参数构造替换结果，不能直接视为普通原地材料替换。',
            '地面蛛网、箱子、TNT、亡灵与数据方块后处理未模拟；不存在原生入口/碰撞/玩家连续路线验收。',
            '不把三个墓碑变体、16墓位、两方向或两切层分别计作建筑。'],
        java_run=False,game_run=False,nbt_written=False,production_changes=0,formal_credit_added=0)
    (OUT/'layout-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('grave_origins','raw_fence_count','raw_fence_is_closed_perimeter','raw_template_door_or_gate_count','diagram_occupied_bounds','diagram_material_counts')},ensure_ascii=False))
if __name__=='__main__':main()
