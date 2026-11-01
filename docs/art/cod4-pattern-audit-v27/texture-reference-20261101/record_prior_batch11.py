"""Manual same-equipment exclusions after five comparison sheets were opened."""
from pathlib import Path
from datetime import datetime, timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'prior-batch11-pairs.json').read_text())['rows']
notes={
363:'旧图标是深紫鳞片胸甲、银灰两肩点，当前图集中暗紫 V 形鳞/槽和灰色小配件相应；同装备复查，不按图标与展开加两例。',
373:'旧胸甲铜棕大板的横向暗槽、浅铜肩块，与当前铜宽板/嵌框材料对应。图标没表现所有蓝色附岛，不凭此认作新套装。',
375:'旧暗红胸甲用几道深横缝分壳段，当前红甲层同类横节宽带；同红蠕虫壳甲案例。',
381:'旧龙钢胸甲是紫灰竖板、黑槽和红暗边；展开还含链网及许多窄岛。是同火龙钢装备，非新增一套。',
401:'旧蓝潮汐胸甲上深蓝粗鳞、下浅青区域，与当前蓝鳞/浅青分区一致；多面附片不是新装备。',
416:'旧胸甲深苔绿底、骨色袖端与下沿，与当前苔绿皮面和骨齿同套；不把齿边和身体岛拆计。',
426:'旧沙色虫壳胸甲以金褐 V 形粗脊和暗边分层，当前同沙色壳节/粗折纹；同设计的物品/穿戴图重复。',
430:'旧图标是白灰两侧配中央棕皮条、黑边的伪装甲；当前白羊毛与棕带配色/结构同套。',
434:'旧潜水胸甲铜橙边、暗棕中腹和方亮点，与当前铜壳/暗带同套；这只证明已有装备案例，不等于与 Create 潜水服相同。',
440:'旧图标为骨白前壳配棕暗连接，当前128图集也有骨白叉块/骨盘，但另有橙毛皮、肤色长条和多组岛。未读模型槽位，不能声称该头盔图标已逐面对应整张 armor_0。',
445:'旧蜈蚣腿甲上端暗紫黑、两腿橙红宽段，当前图集的红壳/暗带相应；同腿甲复查。',
446:'旧鳄鱼胸甲橄榄绿短矩片和中央宽层，与当前绿鳞面同类板区；图标与展开不是两个甲设计。',
447:'旧鸸鹋腿甲浅棕羽簇集中在上腿、下方暗色，当前浅棕羽带/细缝吻合；同物品，羽数不加案例。',
449:'旧飞鱼靴是蓝青成对鞋翼，当前浅蓝岛与独立小翅片延续同材质。仍没有从平面证明附片三维朝向。',
451:'旧冰潜盔大浅蓝罩配正中紫色长棘，当前浅蓝锯齿罩岛和紫色附岛同套。图集不是一个新冰冠案例。',
455:'旧岩甲为骨灰宽块配棕暗缝及少量尖点，当前相同骨灰石片和窄节岛；同装备复查。',
462:'旧骨爬甲以骨白中轴、金边、深蓝暗底分区，当前骨白块、金连接、暗底相应；同甲图标与展开。',
463:'旧咒源胸甲大青块、金边、暗红紫袖；当前图集有独立青条、金边和暗紫红板。面积分布差异需实际模型解释，但作为已研究同名同源套装不再新增。',
465:'旧焰甲金黄硬亮边压在紫黑板上，当前板/橙黄边及节点同套；普通/腿层/鞘翅胸也不扩成多套。',
468:'旧索引命中的是 modulargolems 归档内 assets/cataclysm/textures/item/equipments/monstrosity_helmet.png；图标有高长双角和火色面罩，当前原 Cataclysm monstrous_helm 展开是灰黑长岛与橙点。来源/装备槽语义不同，不能只凭 namespace 和近名认同设计。',
}
for r in rows:
    n=int(r['current_reference'].split('-')[1]);r['accepted_credit']=0
    if 'prior_local_png' not in r:
        r.update(slot_comparable=False,novelty_decision='HOLD_PRIOR_PNG_UNAVAILABLE',
            observation_zh='两个旧盔甲索引中未找到此装备对应原图；当前图已核看，不能把旧图缺失当成设计新颖或门槛已通过。')
    else:
        r['observation_zh']=notes[n]
        if n==440:
            r.update(slot_comparable=False,novelty_decision='HOLD_SLOT_BINDING_NOT_PROVEN')
        elif n==468:
            r.update(slot_comparable=False,novelty_decision='HOLD_VARIANT_OR_VERSION_BINDING',
                explicit_source_mismatch='Old item icon belongs to Modular Golems equipment namespace; current texture is original Cataclysm player-armor source. No equivalence accepted.')
        else:r.update(slot_comparable=True,novelty_decision='ALREADY_STUDIED_EQUIPMENT_CASE')
    r['comparison_limit']='语义排除重复用；不声称图标与图集像素相同、完整 UV 绑定、三维穿戴或游戏验收。'
out={'recorded_at':datetime.now(timezone.utc).isoformat(),'new_credit':0,'prior_icons_actually_reopened':20,
    'same_equipment_reuse_rows':18,'held_slot_or_source_rows':2,'prior_unavailable_rows':6,
    'reviewer':'same agent visual pass, not independent acceptance','rows':rows}
(D/'prior-batch11-semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
