"""Seal this batch once. No production output and no checklist mutation."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
assert not (HERE/'RECEIPT.json').exists()
def write(name,data):
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def bind(path):
    b=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(name):return json.loads((HERE/name).read_text())

image_notes = {
 '01-whole.png':'完整双视角是宽方封闭墓体，四周重复凹框/横带，浅色屋顶簇须按实际地衣状态理解；不是独立地上宫殿或中式徽派外观证明。',
 '02-lower.png':'y17切面可见低部大开敞柱厅、周边重复支撑与内缘点位；y19封闭面与小缺口可对照。柱厅高度跨多层坐标，不等于多楼层。',
 '03-middle.png':'初次合图展示不完整，后由07/08左右全幅裁片复核全部区域；中部内方形区与周圈带不同，y29再成为大封闭层。',
 '04-upper.png':'y35多室区可见互异分隔和近墙储物点，右侧y37封闭盖与机关点位；封闭面不替代房间间通路验证。',
 '05-horizontal.png':'四横切面+X右/+Z下：y5大空区、y22内外圈与南侧局部口、y31不对称多室及熔岩点、y35高处构件；高处白格不推出地面通畅。',
 '06-vertical.png':'x26/z26主轴、x40梯子邻近与z44空隙剖面：低厅高净空、中部独立净空、上部多室净空分开，封闭层和局部空隙不能证明连续竖向通路。',
 '07-middle-left-detail.png':'03左半原像素全幅裁片：中央方区、周圈带与重复矮构/梁线可分辨，未修改原状态。',
 '08-middle-right-detail.png':'03右半原像素全幅裁片：y29实封闭面占主体，远端局部缺口及亮点保留；不把局部缺口当已验外部入口。'
}
observations = {
 'layout':'四源片固定拼接为同一个53×45×53作者墓体：低部宽柱厅，中部内方区/周圈带，上部不对称多分室、书架墙及局部储物装置；不是四栋、45层楼或52书架建筑。',
 'proportion':'完整126405坐标均有显式状态，61650非空气、64755空气；非空气y0..40，上四层全空，y40仅49地附地衣。低厅净空跨y5..17，中/上空间较矮；坐标带不能直接称可行走楼层。',
 'facade':'封闭地下外壳四边重复凹框与横带，内部低厅柱列比外壳细分更显著；不得将埋置外壳冒充地上窗廊，凹框不自动等于可穿窗。',
 'roof':'y18/19低厅顶、y20/21分隔，中部y27/28顶及y29/30厚分隔，上部y36/37顶及y38/39砖瓦盖分层。y40地衣的立方示意不代表实体厚屋面或原生网格。',
 'materials':'读完308调色状态及113方块实体，侵蚀深板岩/砖瓦/玄武岩和机关保留全部属性；18标记、52书架、8空桶、5LootTable箱和陷阱双箱等仅是同一墓体内部内容。分类色不是原材质贴图。',
 'circulation':'全部梯子仅[39,33,11]及[40,32/33,18]，仅处上部局部设施；南侧x25..27/z43..45在y19..21有3×3空气口，y22中心有非空气构件。未证实外部入口、低中上连续通路、机关后状态或实际碰撞。地下[26,3,26]箱六邻均非空气，上邻自定义soul_light，未推断可开箱或可取物。',
 'terrain':'使用310已读原生成类固定偏移合并：四块归一化原点[26,0,26]/[0,0,26]/[0,0,0]/[26,0,0]，源世界y=-30..14为保存边界。地下JSON/类高度声明分别保留，无原生地形适配或玩家到达证明；不改用户实例/存档。'
}
manual=dict(batch=311,status='COMPLETE_AUTHORED_ASSEMBLY_REFERENCE_CANDIDATE_PENDING_MAIN_REVIEW',
    source_stage=310,source_identity='eeeabsmobs:guling, four fixed pieces form one authored assembly',
    purpose='COD4墓地配套葬室的空间组织辅助；不冒充义庄、严格中式徽派或地表墓园整体。',
    actual_palette_states_read=308,actual_block_entities_read=113,
    actual_full_layers_read=list(range(45)),actual_ordered_rows_read=2385,
    source_entities_read_stage310=11,observations=observations,
    prior_complete_comparisons=['COD4-R001-W002','COD4-R001-W026','COD4-R001-W028'],
    comparison_boundary='实际读完整七维文字记录、042原专岗两变体全文与主协调七维判断；本批未重开旧PNG，不把旧审阅或变体重计。D010/D012仅有限排除观察。',
    actual_images_viewed=[dict(**bind(HERE/n),observation=note) for n,note in image_notes.items()],
    unique_reference_assemblies_studied=1,formal_credit_added=0,
    strict_Chinese_Hui_credit_added=0,coordinator_acceptance_pending=True,
    native_generation_or_collision=False,native_entry_or_routes_verified=False,
    whole_total=None,whole_gap=None,applicable_gate_met=False,
    production_changes=0,tasks_deleted=0,java_executed=False,
    learning=['完整主体拼接以生成器偏移为依据，不按源文件数计建筑。',
      '高厅、较矮过渡层、多分室层的净空节奏可比较；承重/楼层和可达性需各自核查。',
      '先落实连续路线与地表接入，再安排储物/机关；空口、梯子和战利品声明均不代替可达性。',
      '研究空间组织，不复制作者结构、模型或贴图作原创。'])
write('manual-review.json',manual)
props=load('properties-BE-reading.json')
props['status']='ACTUAL_ALL_PALETTE_AND_BE_READ_FULL_LAYERS_AND_IMAGES_COMPLETED'
props['PNGs']=8
props['observations'][3]='[26,3,26]普通箱含12/14槽各1下界合金锭、13槽1附魔金苹果；六邻实际均非空气，上邻自定义soul_light；未证实可开启或取得。'
write('properties-BE-reading.json',props)
checkpoint=load('active-checkpoint.json')
checkpoint.update(status='SEALED_REFERENCE_CANDIDATE_PENDING_MAIN_REVIEW',PNGs=8,
    candidate_whole_assemblies_studied=1,whole_studies_added=0,
    next='主协调实际审阅311完整状态/分层、三组完整近族文字、8张研究PNG后决定是否有适用辅助信用；未验入口/通路保留。')
write('active-checkpoint.json',checkpoint)

checks=[]
def check(name,value):
    assert value,name
    checks.append(dict(name=name,passed=True))
for b in load('source-bindings.json')['sources']:
    check('unchanged source '+b['path'],bind(Path(b['path']))==b)
family=load('pre-image-whole-family-comparison.json')
for b in family['bindings']:check('unchanged old whole source '+b['path'],bind(Path(b['path']))==b)
check('three complete comparisons each seven dimensions',len(family['comparisons'])==3 and all(len(c['comparison'])==7 for c in family['comparisons']))
source=json.loads(Path(load('source-bindings.json')['sources'][1]['path']).read_text())
grid={tuple(b['pos']):b['state'] for b in source['blocks']}
dictionary=load('full-layer-row-dictionary.json')
check('45 layers 2385 ordered rows',len(dictionary['layers'])==45 and sum(len(l['row_ids_by_z']) for l in dictionary['layers'])==2385)
reconstructed={}
for layer in dictionary['layers']:
    for z,ident in enumerate(layer['row_ids_by_z']):
        x=0
        for state,count in dictionary['dictionary'][ident]:
            for step in range(count):reconstructed[(x+step,layer['y'],z)]=state
            x+=count
        assert x==53
check('all126405 original states exactly round trip',reconstructed==grid and len(grid)==126405)
probes=load('spatial-probes.json')
all_probes=[s for c in probes['columns'] for s in c['states']]+probes['chest_and_six_neighbors']
for n in probes['all_ladder_neighborhoods']:
    all_probes += [n['ladder']]+n['vertical_column']+n['south_column']+n['north_column']
check('all exact probes original states',all(grid[tuple(p['pos'])]==p['palette_id'] and source['palette'][p['palette_id']]==p['state'] for p in all_probes))
check('all three ladders captured',len(probes['all_ladder_neighborhoods'])==3 and sum(source['palette'][i]['Name']=='minecraft:ladder' for i in grid.values())==3)
check('all aperture air coordinates exact',all(source['palette'][grid[tuple(p)]]['Name']=='minecraft:air' for positions in probes['local_aperture_air_cells'].values() for p in positions))
for n in image_notes:
    with Image.open(HERE/n) as im:im.verify()
check('8 actual image bindings',len(manual['actual_images_viewed'])==8)
check('no formal credit production task deletion or native claim',manual['formal_credit_added']==manual['production_changes']==manual['tasks_deleted']==0 and not manual['native_entry_or_routes_verified'])
write('verification.json',dict(checks=checks,passed=len(checks),
    exact_probe_records=len(all_probes),unique_probe_positions=len({tuple(p['pos']) for p in all_probes}),
    count_boundary='Checks/probes/rows/PNGs are not building reference credit.'))
(HERE/'HANDOFF.md').write_text('311：古陵完整作者主体参考候选，等待主协调实际审阅。\n\n已读308状态、113BE、45层/2385行，继310保留11实体；完成三组完整近族七维文字比较，实际看8张研究图（含中部左右裁片，不新增建筑）。\n\n低厅—中部—上部多室的空间组织明确；只有三格局部梯子，外部入口、连续通路和原生碰撞均未验。埋箱六邻非空气，不认定可取得奖励。四块只构成一座作者墓体；本批正式/严格中式信用0，1000门槛未达，不生产、不删清单、不运行Java。\n',encoding='utf-8')
files=[bind(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='RECEIPT.json']
write('RECEIPT.json',dict(batch=311,status='SEALED_PENDING_MAIN_ACTUAL_REVIEW',files=files,
    data_checks=checks,actual_palette_read=308,actual_BE_read=113,actual_full_layers_read=45,
    actual_full_rows_read=2385,PNGs_actually_viewed=8,
    candidate_complete_assemblies_studied=1,new_complete_whole_studies_accepted=0,
    formal_credit_added=0,strict_Chinese_Hui_credit_added=0,whole_total=None,whole_gap=None,
    applicable_gate_met=False,tasks_deleted=0,production_changes=0,java_executed=False,
    native_acceptance=False,all_tasks_complete=False,
    mutation_boundary='Only this new research directory written; sealed prior stages read only. No master/session/ownership/pending/checklist/asset/Jar writes.'))
print(json.dumps(dict(receipt=bind(HERE/'RECEIPT.json'),manual=bind(HERE/'manual-review.json'),checks=len(checks),files=len(files)),ensure_ascii=False))
