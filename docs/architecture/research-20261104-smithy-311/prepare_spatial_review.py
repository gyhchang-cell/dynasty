"""Read-only fixed reference analysis. Writes only this unsealed research batch."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert not (HERE / 'RECEIPT.json').exists(), 'Sealed research is immutable'
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from whole_building_candidates import AIR, color, iso
from PIL import Image, ImageDraw

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def binding(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))

src = HERE.parent / 'research-20261104-smithy-310/merged-original-reference.json'
d = json.loads(src.read_text())
pal = d['palette']
grid = {tuple(b['pos']): b['state'] for b in d['blocks']}
assert len(grid) == 126405 and len(pal) == 308
def cell(pos):
    return dict(pos=list(pos), palette_id=grid[pos], state=pal[grid[pos]])

columns = [[26,26],[12,26],[26,7],[26,44],[38,8],[39,11],[39,18]]
chest = [(26,3,26),(27,3,26),(25,3,26),(26,4,26),(26,2,26),(26,3,27),(26,3,25)]
ladders = sorted(p for p,i in grid.items() if pal[i]['Name']=='minecraft:ladder')
ladder_neighborhoods = []
for x,y,z in ladders:
    ladder_neighborhoods.append(dict(ladder=cell((x,y,z)),
        vertical_column=[cell((x,h,z)) for h in range(30,38)],
        south_column=[cell((x,h,z+1)) for h in range(30,38)],
        north_column=[cell((x,h,z-1)) for h in range(30,38)]))
apertures = {str(y):[list(p) for p,i in grid.items()
    if p[1]==y and 20<=p[0]<=32 and 38<=p[2]<=48 and pal[i]['Name'] in AIR]
    for y in [19,20,21]}
write('spatial-probes.json', dict(source=binding(src),
    columns=[dict(x=x,z=z,states=[cell((x,y,z)) for y in range(45)]) for x,z in columns],
    chest_and_six_neighbors=[cell(p) for p in chest],
    all_ladder_neighborhoods=ladder_neighborhoods,
    local_aperture_air_cells=apertures,
    limits='Exact original states, not collision, climbability, loot access or native generation.'))

ref = ROOT / 'docs/architecture/continuation-20261022/references'
ledger_path = ref / 'full-buildings.json'
ledger = json.loads(ledger_path.read_text())
old_review_path = ref / 'whole-candidates/review-batch-001.json'
old_review = json.loads(old_review_path.read_text())
graveyards = [x for x in ledger['entries'] if x['id'] in ['COD4-R001-W002','COD4-R001-W026']]
mausoleum = next(x for x in ledger['entries'] if x['id']=='COD4-R001-W028')
f42 = ROOT / 'docs/architecture/research-20261103-funerary-042/manual-review.json'
main42 = Path(mausoleum['manual_review_file'])
read42 = json.loads(f42.read_text())
main42data = json.loads(main42.read_text())
comparisons = [
 dict(identity='COD4-R001-W002', comparison={
 'layout':'交错墓位和露天水格 vs 古陵低部大厅、中部空间、上部多室；无把墓碑阵列放大为地下多层的证据。',
 'proportion':'12×6×15低墓园 vs53×45×53保存边界；古陵上四层显式空，不以45称楼层。',
 'facade':'低围墙/铁栏/破口 vs厚连续墓体外壳及内部柱列。',
 'roof':'露天无屋顶 vs多道封闭分隔和顶盖。',
 'materials':'草、蛀虫石砖、铁栏和水 vs侵蚀深板岩砖瓦、玄武岩、机关；差异不只换色。',
 'circulation':'墓间横向留缝 vs古陵内部高差与不连续梯子；两者均不能由空白断言原生可达。',
 'terrain':'齐平草地园界 vs负高度埋置墓体；前者不是后者地上入口的证据。'}),
 dict(identity='COD4-R001-W026', comparison={
 'layout':'成排墓位、角部小墓室与开敞入园区 vs古陵地下主体多室分级，无庭院墓排。',
 'proportion':'15×40×18保存范围有大量空高；古陵53×45×53也需区分实际占据，不能按高度数字判同族。',
 'facade':'园界低墙与角墓室朝园内 vs古陵封闭厚壳、内部重复支撑；不是把小墓室独立增计。',
 'roof':'主要露天、角室局部坡顶 vs古陵全主体封闭顶盖。',
 'materials':'土、粗土、草、苔石的地表墓园 vs深板岩/玄武岩与机关墓体。',
 'circulation':'东侧道路、墓排分流与小墓室门 vs古陵外部入口仍未验，不能以园门替代陵墓入口。',
 'terrain':'地表土台入口层对路 vs古陵四块按生成器固定偏移拼接后埋置；各自保持不同边界。'}),
 dict(identity='COD4-R001-W028', comparison={
 'layout':'旧陵墓上部四厚角体之间十字通道，中下室/侧室；古陵低部大柱厅、中部独立层、上部多分室及书架墙，分隔次序不同。',
 'proportion':'旧37×48×37实高47 vs当前53×45×53非空气至y40；当前更宽且低厅占多层净空，非旧体等比或换皮。',
 'facade':'两者地下封闭外壳有共性；旧四角竖向支撑和横带，对比当前低层内部高柱与多道平整封闭层，不能仅以材质做排重。',
 'roof':'旧多级收分厚盖、顶轴木桶和半砖；当前y37..39砖瓦厚盖并保留不规则空隙，y40为49地附地衣而非49屋面实体。',
 'materials':'旧crypt砖/柱与3934黑羊毛原样计入；当前深板岩砖瓦/侵蚀砖、玄武岩及机关，比较空间而不把黑羊毛隐藏为空气。',
 'circulation':'旧普通门0、连续通路未验；当前也无已验外部入口，三格梯子不贯穿主空间分隔。完整作者主体与可达性分别记录。',
 'terrain':'旧jigsaw根池1/2二选一、bury起高[-40,0]；当前四不同部分是同一生成器固定拼接，非四个独立墓体，也不能把根JSON与类中高度差当运行结果。'})]
write('pre-image-whole-family-comparison.json', dict(
    status='ACTUAL_FULL_SEVEN_DIMENSION_RECORDS_READ_BEFORE_CURRENT_IMAGES',
    bindings=[binding(p) for p in [ledger_path,old_review_path,f42,main42,
      ref/'whole-candidates-004/review-batch-004.json',ref/'whole-candidates-004/manual-visual-ledger.json']],
    prior_whole_entries=graveyards+[mausoleum],
    prior_manual_seven_dimensions={k:old_review['accepted'][k] for k in ['W002','W026']},
    prior_mausoleum_full_manual_entries=read42['entries'],
    prior_mausoleum_main_observations=main42data['independent_observations'],
    comparisons=comparisons,
    excluded_nearby=dict(D010='围栏空基，尚未组装墓碑/陷阱，不是完整墓园，信用0。',
      D012='33×48×33水下箱形墓体，旧记录因当前村落用途相关性不足暂缓；此处只读旧有限观察，不冒充七维完整研究或新增信用。'),
    prior_images_reopened_this_batch=0, formal_credit_added=0,
    strict_Chinese_Hui_credit_added=0,
    limit='Full textual source/manual comparisons; no claim of source visual rereading, native routes, global novelty or whole gate.'))

cells = {p:pal[i]['Name'] for p,i in grid.items() if pal[i]['Name'] not in AIR}
views = [('01-whole.png',None,None),('02-lower.png',17,19),
         ('03-middle.png',27,29),('04-upper.png',35,37)]
for name,a,b in views:
    img=Image.new('RGB',(1520,720),'#edf0f2')
    img.paste(iso(cells,d['size'],0,f'Guling reference: y <= {a}' if a is not None else 'Guling whole fixed assembly',a),(0,0))
    img.paste(iso(cells,d['size'],1,f'Quarter turn: y <= {b}' if b is not None else 'Whole quarter turn',b),(760,0))
    ImageDraw.Draw(img).text((20,690),'SOURCE RESEARCH ONLY / cubes, not native meshes / no collision or route acceptance / one assembly, zero credit',(20,35,40))
    img.save(HERE/name)

# Exact-coordinate slices retain explicit air as white; diagrams do not invent collision shapes.
def slice_panel(axis, value, title):
    im=Image.new('RGB',(760,700),'#edf0f2');draw=ImageDraw.Draw(im)
    draw.text((20,12),title,fill='#17252c')
    w,h=(53,53) if axis=='y' else (53,45)
    step=11; left=65; top=65
    for u in range(w):
        for v in range(h):
            p=(u,value,v) if axis=='y' else ((value,44-v,u) if axis=='x' else (u,44-v,value))
            state=pal[grid[p]];c=(255,255,255) if state['Name'] in AIR else color(state['Name'])
            draw.rectangle((left+u*step,top+v*step,left+(u+1)*step,top+(v+1)*step),fill=c,outline='#cbd1d5')
    for u in range(0,w,5):draw.text((left+u*step,top-20),str(u),fill='#17252c')
    for v in range(0,h,5):draw.text((left-30,top+v*step),str(v if axis=='y' else 44-v),fill='#17252c')
    draw.text((20,665),'WHITE explicit air; colors classify names, not textures or shapes',fill='#17252c')
    return im
for name,panels in [
 ('05-horizontal.png',[('y',5,'y5 lower hall / +X right +Z down'),('y',22,'y22 middle / +X right +Z down'),('y',31,'y31 upper / +X right +Z down'),('y',35,'y35 upper ceiling zone / +X right +Z down')]),
 ('06-vertical.png',[('x',26,'x26 section / +Z right +Y up'),('z',26,'z26 section / +X right +Y up'),('x',40,'x40 near ladder / +Z right +Y up'),('z',44,'z44 aperture / +X right +Y up')])]:
    sheet=Image.new('RGB',(1520,1400),'#edf0f2')
    for n,(axis,value,title) in enumerate(panels):sheet.paste(slice_panel(axis,value,title),((n%2)*760,(n//2)*700))
    sheet.save(HERE/name)

print(json.dumps(dict(spatial_probes='saved',ladder_count=len(ladders),
    local_aperture_air_counts={k:len(v) for k,v in apertures.items()},
    prior_complete_family_records=3,generated_images=6,viewed_images=0,credit=0)))
