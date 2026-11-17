#!/usr/bin/env python3
"""Record this agent's actual visual observations, with zero production credit."""
import copy
import hashlib
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
KEYS=['layout','proportion','facade','roof','materials','circulation','terrain']
def get(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
OBS={
 (21,'T01'):[
 '下部疏框架托宽台，台上是收进的小上室，室外仍有周边平台；y11中心留空，不宜笼统称为封闭中心柱。',
 '保存19×34×19；主体上台y17，小上室及屋盖集中于其上，y27–33细旗不折算七层楼。',
 '下部柱框疏、上台宽，上室墙线明显退进台缘，与birch几乎占满上部轮廓的宽房不同。',
 '小上室有局部屋盖，台缘未被同宽室墙占满；与dark_forest无上室露台不同。',
 '橡木柱、云杉板阶与苔石基脚；学习承托与围护分工，不照搬材质或西式旗顶。',
 '原状态梯(9,12)y19–22，无普通下半门；仅证实梯段存在，不声称地面到台顶全程可达。',
 '自带低地脚和柱脚，原占用边界x1–18/z1–17；未生成真实地形，避免把留空地脚当额外庭院实例。'],
 (21,'T02'):[
 '同样是疏框架托宽台、台上收进小上室，与T01的主体空间关系重合。',
 '同为19×34×19，主台y17，上部室层与细旗段高度对应，不能因现代版本名再计一次。',
 '柱框和台缘分层对应T01；边饰与材料改变不构成另一完整设计。',
 '小房屋盖与宽台的收放对应T01，屋盖外观变化不足以另计。',
 '深色橡木与云杉混合替代部分原木板阶，保留原状态而非按颜色猜材料。',
 '梯(9,6)y19–22在对侧，无普通门；梯侧变化按同族变体记录，不据此拆成两栋。',
 '地脚草土加厚等局部差异可见，不等于独立地形建筑；未装配任何jigsaw外接对象。'],
 (21,'C01'):[
 '细颈承托宽封闭上室，上室墙体占据大部上层轮廓；不同于T01小上室外留宽台。',
 '21×31×21；上室y19–22宽，细旗y23起；比较围护比例，不以总高判新颖。',
 '下柱框和上层切角墙体形成实体房间；不是T01的紧凑小房加台缘柱。',
 '上室宽屋盖覆盖主要房体，屋盖与上室边界关系不同于收进小上室。',
 '橡木板柱与石砖主构，桦木填充；材质差异不作为本次独立性主要证据。',
 '六个下半门均在y19，门种及朝向存原状态；无普通梯，不把门数当六个实例。',
 '单塔自带低地脚；对照的是整座旧入账建筑，不新增地脚参考。'],
 (21,'C02'):[
 '宽底向上收小，y9及y17均呈开敞台，缺T01台上围合小上室。',
 '17×27×17，原占用y0–25；两开台沿同一竖向守望轴排列。',
 '斜撑与柱框显露，下层宽、上台窄；不是宽平台上再收房。',
 '上部开放平台无T01的小上室屋盖，不以末端灯柱计楼。',
 '深色橡木、云杉与圆石；结构开敞关系是本次对照重点。',
 '梯(8,7)y2–16连续存储；原梯段不替代游戏碰撞通行验收。',
 '柱脚与底台一体，未将外接actor或地基组件计成建筑。'],
 (21,'C03'):[
 '下部连续泥墙筒体承托上露台，y6墙圈围合；不同于T01疏框架。',
 '15×25×15，原最高非空气y22，塔身围护与露台有明确高低分工。',
 '连续墙筒与西侧开口形成实面，T01下部主要疏框架。',
 '露台上方木构开放屋盖，无独立收进小上室。',
 '夯实泥、泥砖与剥皮云杉混合；只借鉴围护及承托关系。',
 '单下半门和梯状态留档，不能由剖面推定所有屋顶可站立。',
 '原泥墙和低脚整体一次；不将泥墙片、柱脚各算新例。'],
 (22,'T01'):[
 '下部多层围合房/平台叠置，上部拓宽为覆盖平台；与中心竖轴小占地塔原型仍有同族疑问。',
 '保存15×25×15，实际非空气y0–23；低檐与较少室层不足以独立排除旧tudor原型。',
 'y7木石围边与中央实体、y15外圈台缘可见，结构层次比全景更明确，但不足作新设计结论。',
 '上盖约y20–23，不能因tudor砖尖盖更高而算成独立建筑。',
 '桦木板、深色橡木与石砖混合；换材不解同族阻塞。',
 '三段梯分别位于(7,4)y2–6、(4,10)y7–10、(5,10)y11–14；转位梯段不直接证明完整通行。',
 '低石木地脚随塔整体；未解析外接15个socket为额外完整建筑。'],
 (22,'H01'):[
 '紧凑中心叠层，外圈包围不同高度室层，上端加宽；仍保留原同族待查。',
 '15×39×15，其中屋盖及旗高占明显部分，不以39对25的差异认定独立。',
 'y7实心/窄环下段，y15外圈房与柱体；和默认塔的竖向叠置关系需继续核对原型。',
 '陡砖坡盖约y20–32，旗约y33–38；高屋顶不能替代平面及室层独立性证据。',
 '砖、剥皮云杉与安山岩板，变化主要不能单靠外皮证明独立。',
 '梯(6,7)y14–20，无普通门；少量原梯不能推断所有内部楼层已连通。',
 '同一15格地脚，未额外装配actors；旧011-F04继续零计数待查。'],
 (22,'C01'):[
 '小占地多层疏围合托上覆盖台，与竖向中心塔原型有可比关系，不能补本范围数量。',
 '15×21×15，实际y0–20，低于当前25–53格保存高范围；沿用018排除结论。',
 '下围栏、细柱中段、宽上台三段；与两候选的差异仍不能自动解除其原型疑问。',
 '低平覆盖上台，不能拿平帽对尖帽凑出新例。',
 '红砂岩、陶瓦为主；渲染分类色不当作原版纹理。',
 '可见阶块仅保存形态证据，非原生碰撞检验；无普通门。',
 '低围脚整体仅作对照，原范围排除仍为0。'],
 (23,'T01'):[
 '一端高塔接连续长厅，y2室层呈纵向连续大厅，y9有横隔；未见足以排除教堂类原型的双向门廊组织。',
 '29×40×17，保存非空气最高y39；旗不算楼层，长宽符合候选范围不等于用途验收。',
 '连续侧壁扶垛、长侧窗与单端塔体现教堂式骨架；与swedish横向门廊差异显著。',
 '长厅坡屋盖接端塔敞顶，高塔不是整栋屋盖中心；细旗段不计守望室。',
 '石板、安山岩板、深色橡木板及砂砾凝灰岩；军事命名和换材不足证明新空间原型。',
 '塔端两梯y1–11，另一端两梯y1–3，中央塔梯(6,8)y11–29；长梯不证明用途及原型独立。',
 '基脚低，未原生摆放于坡地；作为待查完整主体保存，不删原012-F03阻塞。'],
 (23,'C01'):[
 '旧swamp_church_1为一端高塔接狭长厅；明确提供教堂类对照，不转入守备厅计数。',
 '19×28×11，比目标小，虽比例近似，不能放大解释为同规模新参考。',
 '长壁开窗和塔厅高低组织相近；藤蔓与破损不产生第二实例。',
 '狭长坡厅顶接单端高锥帽，原屋盖不同不直接解除候选同族疑问。',
 '云杉、圆石与藤蔓，保留真实名称；不从分类投影视图推断贴图。',
 '可见塔梯原状态与厅长轴，未进行行走或碰撞验证。',
 '自带小地脚，3个socket未装配；原148墓祀记录不挪借到当前范围。'],
 (23,'C02'):[
 '横向长厅与偏置竖向高低段相交，并有横向门廊；不只是单端高塔接长厅。',
 '24×37×15，低厅、高塔及较低副段形成不同长短关系，旗段不计楼。',
 'y3厅体两侧伸出部分，y12横向高段清楚，主体围护与T01的连续长墙不同。',
 '横厅屋脊叠两个不等高竖向屋盖，屋面交接服务实际横向组织。',
 '深色橡木及黑石/深板岩构件；仅借鉴厅塔联系，不搬用异域立面到中式战场。',
 '两处低层开口与横向厅组织可见；无普通下半门不代表自动通行验收。',
 '地脚随完整主体，7个socket不作建筑数；维持011-F03原入账一次。']}
FAR=[
 (11,'F02','同心层台逐级收尖，塔身实墙/层台交替，非宽台上单个退进小房；台层和细尖顶不拆例。'),
 (12,'F01','偏置高低平台与长外阶形成破损塔，非对称外攀组织；局部屋盖不能视为T01同宽居中上室。'),
 (12,'F02','不规则束腰和偏移小室沿高轴穿插，层间平台收放不对称；并非直柱宽台的整体原型。'),
 (13,'F01','不对称并列小竖室和露台组成石塔，下部围合较密；非疏柱框承一处小上室的组织。')]
def main():
 parent=BASE/'research-20261101-dungeons-020/scoped-reference-update.json'
 for n in [21,22,23]:
  folder=BASE/f'research-20261101-dungeons-{n:03d}';src=get(folder/'sources.json');entries=[]
  for c in src['candidates']:
   ident=c['id'];credit=int((n,ident)==(21,'T01'))
   is_target=ident.startswith('T')
   decision=('ACCEPT_ONE_PREVIOUSLY_HELD_COMPLETE_DESIGN'if credit else
    'SAME_FAMILY_NO_ADDITIONAL_REFERENCE'if(n,ident)==(21,'T02')else
    'HOLD_EXISTING_PROTOTYPE_EVIDENCE'if is_target or ident=='H01'else'PREVIOUS_CONTROL_NO_CREDIT')
   entries.append(dict(id=ident,prior_identity=c['prior_identity'],source=c,decision=decision,credit=credit,
    credit_identity=c['prior_identity']if credit else None,
    scope_id='DUN03-SINGLE-WATCHPOST'if credit else None,
    observations=dict(zip(KEYS,OBS[(n,ident)])),
    actual_images_viewed=[c['original_whole_image'],ev(folder/f'{ident}-details.png')],
    native_acceptance=False,independent_human_review=False))
  far=[]
  if n==21:
   for batch,ident,note in FAR:
    far.append(dict(prior_identity=f'{batch:03d}-{ident}',image=ev(BASE/f'research-20261101-dungeons-{batch:03d}/{ident}-whole.png'),
     actual_image_viewed=True,observation=note,new_template_credit=0,reference_credit=0))
  added=['013-F03']if n==21 else[]
  rev=dict(entries=entries,historical_far_controls=far,new_source_templates=0,previous_source_template_rereads=len(entries),
   actual_new_section_images_viewed=len(entries),actual_unique_previous_whole_images_viewed=len(entries)+len(far),
   independent_references_added=len(added),credit_identity_rule='Original 013-F03 credited once; 021 IDs are review rows, never additional designs.',
   reviewer='Same Codex agent visual/source review; not independent human approval',
   semantic_rationale=('013-F03的宽台外缘+台上退进小上室，与已入账七例的上室占地、围护及台层组织均不同；和016-F05视作同一族，代表013-F03仅加1。'if n==21 else
    '默认塔/旧tudor及端塔长厅旧阻塞仍保留；本批新剖面提高描述精度，不自动转正。'),
   native_routes_verified=False,production_changes=0,checklist_deletions=0)
  dump(folder/'manual-review.json',rev)
  old=get(parent);scopes=copy.deepcopy(old['scopes'])
  if added:
   scope=next(s for s in scopes if s['scope_id']=='DUN03-SINGLE-WATCHPOST')
   assert '013-F03'not in scope['accepted_ids'];scope['accepted_ids']+=added
   scope['accepted_references']=len(scope['accepted_ids']);scope['remaining']=1000-scope['accepted_references']
  update=dict(prior_update=ev(parent),original_scope_definitions=old['original_scope_definitions'],scopes=scopes,
   added_ids=added,added_credit=len(added),scope_definitions_changed=False,
   previous_two_holds_retained=['011-F04','012-F03'],other_holds_retained=['016-F01','019-F02'],
   old_holds_reopened=['011-F04']if n==22 else['012-F03']if n==23 else[],
   previous_hold_evidence=old['previous_hold_evidence'],
   independent_human_reviewer_claimed=False,production_tasks_completed=0,production_changes=0,checklist_deletions=0,
   limits='三个用途分别每范围1000，当前6/8/1均未达。只记辅助守备构筑布局；不代表中式夯土瓮城、古战场、任务或指南针完成。')
  dump(folder/'scoped-reference-update.json',update)
  dump(folder/'discovery-boundary.json',dict(local_only=True,network_requests=0,new_source_templates=0,
   indices_checked=[c['original_index']for c in src['candidates']],java_run=False,game_run=False,
   generated_structure_assets=0,components_assembled=False,source_archive_opening='Read-only fixed local archives',
   sound_brightness_window_save_changes=0,production_changes=0,checklist_deletions=0,
   method='Targeted rereads and fresh selected planes of old sources, no new architecture production or external source retrieval.'))
  handoff=(f'# 第{n:03d}批本地建筑复核\n\n'
   f'本批重看{len(entries)}个既有完整主体并实际查看{len(entries)}张新选层剖面；新来源0，新增有效参考{len(added)}。'
   '不是新增一批建筑制作。三范围累计：驻防堡/营院6/1000，独立守望塔8/1000，连厅守望楼1/1000。\n\n'
   +rev['semantic_rationale']+'\n\n'
   '完整来源、原始状态、七项观察、重复归并及图像散列见本目录JSON。旧文件不改；原待查保留。未运行Java或游戏，未改任务、指南针及清单。\n')
  if n==23:
   handoff+=('\n## 第021–023批合并结果\n\n'
    '重看11个既有主体，实际查看11张新选层剖面和15张不重复的既有全景图（含4例远端对照）。新来源0。'
    '原待查013-F03 taiga经室层与既有七例对照后作为一族代表加1，016-F05 modern并入同族不另加。'
    '全体非空气占用交并比约0.816，上室/平台/盖y17–26段约0.906；这两个数字不是原方块状态相同比例，也不是自动独立性判定。\n\n'
    '011-F04、012-F03、016-F01、019-F02继续待查，旧文件未改。驻防堡/营院仍缺994例，独立守望塔缺992例，连厅守望楼缺999例；用途不混计。'
    '复看与新增剖面不冒充新增设计；其他范围登记和第016–020批及原语义验收包保持原校验值。\n\n'
    '联验入口：本目录verify_delivery.py；结果verification.json，三批各自RECEIPT.json封存本批文件。'
    '这些是同一代理的证据检查，不声称独立人工验收或游戏内通行验证。任务清单交由协调统一验收，本轮无可删除的生产任务。\n')
  (folder/'HANDOFF.md').write_text(handoff)
  parent=folder/'scoped-reference-update.json'
 print('Recorded three rereview batches: new source templates 0, added 013-F03 once, counts 6/8/1.')
if __name__=='__main__':main()
