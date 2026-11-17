"""Save manually reviewed whole-camp research; private evidence only, no admission."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
assert not (OUT / 'RECEIPT.json').exists()
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read

def put(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def bind(path):
    path = Path(path).resolve()
    b = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

row = json.loads((OUT / 'sources.json').read_text())['candidates'][0]
audit = json.loads((OUT / 'raw-source-audit.json').read_text())['candidates'][0]
n = audit['nbt_decoded_original']; pal = n['palette']
cells = {tuple(b['pos']): b for b in n['blocks']}
assert len(cells) == len(n['blocks']) == 7372
rle = []
for y in range(12):
    for z in range(30):
        runs = []
        for x in range(36):
            state = cells.get((x,y,z), {}).get('state', -1)
            if runs and runs[-1][0] == state:
                runs[-1][1] += 1
            else:
                runs.append([state, 1])
        rle.append({'y': y, 'z': z, 'runs_original_state_and_length': runs})
put('F01-full-layer-rle.json', {'size': n['size'], 'omitted': -1, 'rows': rle,
    'generated_reproducibility_not_extra_semantic_credit': True,
    'manual_coverage': 'All12 classified plan layers visually read; not claiming all12960 original-index cells manually read.'})

seven = {
 'layout': '完整同处营地：西北x2..10/z4..12一座东西向长A架帐棚、东南x16..24/z20..26同家族转向帐棚，两者朝中央开敞共用场；中西箱桶/制作台在两棚之间，东北x16..25/z3..13火堆及座形陈设，最东x29..34/z13..16一处抬高小型有盖工作/藏箱台。整体是围开敞公共场分置大帐与低小棚，不把两座旋转帐、火堆、箱桶、牌或地形socket拆数。最多提出NPC04雨护货/停驻空间辅助整处1，非已完成商人。',
 'proportion': '36×12×30/DV3465，声明12960位置、7372存储=1434nonair+5938显式air，5588省略unknown。99palette/154BE/7源实体；最高y11仅四个closed bottom活板装饰，不是十二生活层。大帐地面使用y1，东小棚top slab地板y1/使用y2；没有内楼梯/梯子/第二经营层/床，不凭snow或名称说雪山猎户木屋。',
 'facade': '大帐白毛面配少量红/橙毛和混凝土粉末端饰，木阶/栅/开闭栅门/活板构撑架，原64红/橙墙旗均Patterns[]；63墙牌及4吊牌两面全空，不是中文招牌。四普通门下半在10,1,6与10,1,10及18,1,19与22,1,19，均closed且为边框位置，8半块不当8门。中央10,y1..3,8和20,y1..3,19为孤栅立柱，门旁通缝不能概括成整幅无障碍敞口。',
 'roof': '两座高A架双坡与最东小低双坡构高低关系，white_wool161、spruce stairs100/trapdoor108/fence64/gate66等按原Properties保留；43真实snow_block与94 snow薄层混在盖/边缘，非全白皆羊毛或图中灰皆石瓦。雪薄层1..4原值，y10有2/3/4层；四顶饰活板y11只细部。帐篷脊与立柱连续但未作原生防雨、雪融火险或承重验收。',
 'materials': '地面granite154/packedmud156/dripstone169及少量dirt/roots并非完整厚基。4箱+1桶：7,1,10north与22,1,22west各vanilla plains house，12,1,15north桶原pillager_outpost，14,1,14north箱原jungle_temple_dispenser，32,2,15west箱own archer_chest；均只loot引用无现存Items/seed，不发物不替换NBT。制作台13,1,16与29,2,14，两个level0堆肥器13,1,14/13,2,16。17原campfire分5lit/12unlit，全部空Items及四零双计时；有些是座形陈设，不能算17炉/17厨房。',
 'circulation': '原索引312关键格实际读：西帐朝东在x10,z7/9,y1..3均air，x9/11相应也air，下面y0为混土石；x10,z8中心三高栅阻断中线，z6/10闭门位保留。东南帐朝北在x19/21,z19,y1..3均air并接z18/20，x20,z19中心柱非air；x18/22闭门不当必经双扇主入口。小东棚29..33,y1,z13..16为top slab，32,2,15箱前西侧31,2,15air而30,2,14/31,2,14省略unknown；没有证明上台踏步/完整绕行/NPC动线/开箱碰撞。火邻及跨院路线未逐格验证，不以类色空白代替air。',
 'terrain_and_dedup': '一完整帐棚营地模板而非只一个屋翼；down_north地形socket14,0,15 final granite接ati terrain_small池，该池自fallback且唯一rigid/single/mossify20元素；terrain_small NBT和原版mossify处理器不在本轮研究，不称已组装落地。root size7/max80/WORLD_SURFACE_WG/beardthin/expansiontrue/start0，monster fullbbox spawns[]不能抹掉原7敌对实体；直biome tag含原版/optional嵌套，nested未读。266完整7维及11限制先读保存：旧西窄拱货棚北桶南卧+东火圈，本源两长A架朝中央公共场/独立抬高工作小棚及分散货储整体不同；不是仅换材/放大/加箱断新。机器未命中只辅助，Main仍须判用途、完整建筑资格及近族；同源帐旋转本身0独立信用。',
}
limits = [
 '只研究NPC04遗迹入口/十字路口随机停驻、雨护货之建筑辅助空间。原营地为敌对掠夺者场景，没有百宝金、牵驴、算盘、稀有事件、古钱交易、中文任务/指南针/NBT获取回执；敌对用途与较大尺度可能使Main判相关性不足HOLD0，不提前认定有效参考。',
 '原7实体完整实质字段均读：4pillager持弩、2vindicator持铁斧且Johnny1、1illusioner持弓；PersistenceRequired1/CanJoinRaid1/原UUID与内绝对Pos保留，外pos/blockPos是相对值。图未画实体，不是新增建模、已生成游戏NPC或安全营地；root怪物空spawn配置不等于实体为空。',
 '完整99状态Properties、154BE按22同内容组及全坐标、7实体、三metadata、三上下文JSON及根/直tag两JSON已读。初次大输出截断后，22组全部及7实体另分段完整补读；未将截断段当完成。三原版loot和原版mossify处理器仅本Jar缺精确成员，不证明整包缺失。',
 '9PNG全部实际看：whole四方向、cut<=2/5、vertical两剖及6双层平面覆盖12层0..11。全格类色不是原贴图、光照或薄件/实体碰撞。360行RLE为复现生成，未宣12960位置逐格人工语义阅读；312关键索引实际读不冒充全部原格。',
 '5588省略与5938显式air严格分开。地形延伸NBT、nested群系tag、当前处理器顺序/引擎/structure set均未读未运行；地面y0一层、火下越界未知，不能保证承托、自然地形接入/跨院通路/防火防雨。',
 '两大帐同构转向、四闭门、两制作台、五储物点、17营火/64旗/67空牌不拆独立参考。整体围场组织与266静态比较不等于穷尽所有历史近族或自动通过Main。',
 'own archer loot10pools全文读，含4..5rolls+bonus1材料池、可选弓弩、.5附魔条件装备池/.2药水/.3钻石装备候选；函数条件/随机权重不是确定库存或实际交易，不复制到用户任务奖励。',
 '源文件名V1.4.2与mods/fabric内版本1.4.0不一致、mods显示名Structory/metadata作者ATi与pack_format15如实保留，不凭文件名推兼容。未经Java/当前包原生加载验收。',
 '正式信用0，最多1整处辅助营地候选待Main用途与家族复核，不更新NPC累计null。COD4旧范围153/847保持；不制作新建筑、不删任务、不改生产或共享Jar。',
]
images = [bind(f) for f in sorted(OUT.glob('*.png'))]
assert len(images) == 9
put('manual-review.json', {'batch': 273, 'case': 'F01', 'source': row,
 'seven_dimensions': seven, 'limits': limits,
 'status': 'COMPLETE_WHOLE_CAMP_STUDY_PENDING_MAIN_SCOPE_AND_FAMILY',
 'complete_original_spatial_study': True, 'new_reference_proposal_maximum': 1,
 'formal_credit_added': 0, 'native_acceptance': False,
 'actual_reading': {'palette':99, 'block_entities':154, 'BE_groups':22,
     'entities':7, 'PNG_actually_viewed':images, 'classified_plan_layers':12,
     'original_key_cells':312, 'generated_RLE_rows':360,
     'all_original_cells_manually_read':False},
 'applied_principles': ['以公共开敞院组织不同遮蔽工作/存货点，整处营地而非棚数计数。',
     '入口中心立柱与侧通缝分开判断，闭门/薄牌/半砖/未知格保留。',
     '屋盖、火位、货物遮蔽和人物真实行为分别验收；敌对场景不冒充行商完成。']})

# Fresh fixed-source equality is local reproducibility verification, not independent Main admission.
with ZipFile(row['source_archive']) as z:
    original_bytes = z.read(row['member'])
    fresh = read(original_bytes)
    assert fresh == n and hashlib.sha256(original_bytes).hexdigest() == row['nbt_sha256']
    contexts = json.loads((OUT / 'source-context.json').read_text())
    checked_contexts = contexts['candidates'][0]['contexts'] + json.loads((OUT / 'root-context.json').read_text())
    for c in checked_contexts:
        bb = z.read(c['member']); assert hashlib.sha256(bb).hexdigest() == c['sha256'] and json.loads(bb) == c['json']
    for m in contexts['metadata']:
        assert hashlib.sha256(z.read(m['member'])).hexdigest() == m['sha256']
for r in rle:
    expanded = [state for state, count in r['runs_original_state_and_length'] for _ in range(count)]
    assert expanded == [cells.get((x,r['y'],r['z']),{}).get('state',-1) for x in range(36)]
key = json.loads((OUT / 'key-source-route-matrices.json').read_text())
for r in key['rows']:
    assert r['original_indices'] == [cells.get((x,r['y'],r['z']),{}).get('state',-1) for x in r['xs']]
assert sum(len(r['xs']) for r in key['rows']) == 312
protected = []
prev = ROOT / 'docs/architecture/research-20261104-smithy-272'
for r in json.loads((prev / 'protected-inputs-current.json').read_text())['files']:
    before = r['current272']; now = bind(before['path'])
    protected.append({'previous272':before, 'current273':now, 'unchanged': before == now,
                      'this_chat_wrote_file':False})
put('protected-inputs-current.json', {'files':protected, 'this_chat_product_writes':0,
    'cod5_missing_not_invented':True})
session = json.loads((prev / 'session.json').read_text())
session.update({'batch':273, 'previous272_receipt':bind(prev/'RECEIPT.json'),
    'formal_credit_added':0, 'first_carry_added':0, 'current_batch_new_whole_studies':1,
    'current_batch_proposal':1, 'actual_active_work_hours':None,
    'next':'273 complete whole camp pending Main relevance/family. Continue distinct related whole building only;272 F02 duplicate165 and F01/F03 bounded0.',
    'all_tasks_complete':False})
session['pending_whole_reference_admissions'].append('273F01_ATI_WHOLE_NOMADIC_CAMP_NPC04_AUXILIARY_SPACE') if 'pending_whole_reference_admissions' in session else None
# Preserve the actual prior pending-list key without inventing a parallel acceptance ledger.
pending_keys = [k for k,v in session.items() if isinstance(v,list) and '270F01_SNOWY_SHEPHERD_WHOLE_NPC13_AUXILIARY_SPACE' in v]
assert len(pending_keys) == 1, pending_keys
if '273F01_ATI_WHOLE_NOMADIC_CAMP_NPC04_AUXILIARY_SPACE' not in session[pending_keys[0]]:
    session[pending_keys[0]].append('273F01_ATI_WHOLE_NOMADIC_CAMP_NPC04_AUXILIARY_SPACE')
put('session.json',session)
put('active-checkpoint.json', {'batch':273,'status':'WHOLE_CAMP_AUTHOR_REVIEW_COMPLETE_PENDING_MAIN',
 'new_whole_studies':1,'proposal_maximum':1,'formal_credit_added':0,
 'COD4_accepted':153,'COD4_gap':847,'NPC_totals':None,
 'native_acceptance':False,'tasks_deleted':0,'all_tasks_complete':False,
 'session':bind(OUT/'session.json'),'manual':bind(OUT/'manual-review.json')})
checks = {'fresh_source_equals_saved':fresh==n, 'source_archive_fixed':bind(row['source_archive'])['sha256']==row['source_archive_sha256'],
 'all_five_contexts_verified':len(checked_contexts)==5, 'three_metadata_verified':len(contexts['metadata'])==3,
 'all_360_RLE_rows_verified':len(rle)==360, 'key312_verified':sum(len(r['xs'])for r in key['rows'])==312,
 'nine_images_read':len(images)==9, 'BE_groups_cover154':sum(len(g['all_positions'])for g in json.loads((OUT/'full-BE-group-read.json').read_text()))==154,
 'full99_palette':len(pal)==99,'entities7':len(n['entities'])==7,
 'prior266_own7_limits11_preserved':len(json.loads((OUT/'saved-prior-whole-comparison.json').read_text())['own_seven_dimensions'])==7 and len(json.loads((OUT/'saved-prior-whole-comparison.json').read_text())['original_limits'])==11,
 'protected8_unchanged':len(protected)==8 and all(r['unchanged']for r in protected),
 'no_native_acceptance':True,'no_task_deletion':True}
assert all(checks.values()), checks
put('verification.json',{'checks':checks,'passed':True,'fresh_readback_same_parser_not_Main_independent_review':True,'formal_credit_added':0})
files=[bind(f)for f in sorted(OUT.iterdir())if f.is_file()and f.name!='RECEIPT.json']
put('RECEIPT.json',{'batch':273,'status':'SEALED_COMPLETE_WHOLE_CAMP_STUDY_PENDING_MAIN',
 'files':files,'checks':checks,'new_whole_studies':1,'proposal_maximum':1,
 'formal_credit_added':0,'native_acceptance':False,'tasks_deleted':0,
 'production_changes':0,'all_tasks_complete':False})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'manual':bind(OUT/'manual-review.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))
