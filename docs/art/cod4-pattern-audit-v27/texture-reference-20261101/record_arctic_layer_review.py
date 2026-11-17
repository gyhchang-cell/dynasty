"""Narrow a held visual mismatch with actual item-layer source evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json
D=Path(__file__).resolve().parent
x=json.loads((D/'arctic-item-layer-binding.json').read_text())
out={'recorded_at':datetime.now(timezone.utc).isoformat(),
    'status':'ITEM_OVERLAY_OMISSION_RESOLVED_WEARABLE_BINDING_STILL_HELD',
    'inspection_sheet':x['inspection_sheet'],'source_pngs_opened':8,'derived_raw_composites_not_cases':4,
    'new_equipment_credit':0,'production_changes':0,'same_agent_not_independent_acceptance':True,
    'observations_zh':[
        '四个物品模型都明确引用 layer0 和 layer1，旧索引只记录某个 PNG，不是完整图标最终外观。',
        '胸甲 layer0 确实是褐皮胸形；layer1 有两块白肩毛和底边白齿，原先“旧图没有白毛”只对单层 PNG 成立，不能推为游戏中整件物品没有白毛。',
        '裤甲 layer1 是上端一块白灰毛沿，靴层是两个白灰靴筒；头盔 layer0 本身已蓝白，layer1 再加灰白帽沿，四槽分工不同。',
        '诊断合成只按原始 RGBA 覆盖，未计算染色；不能把第三列叫默认游戏图标或实际穿戴外观。',
        '同一固定归档的哈希链已确认，现有差异无需先猜版本不同；但物品 JSON 没有给出穿戴 arcticarmor_* 的模型/染色分支完整绑定。',
        '当前蓝白毛/棕带穿戴图集与物品白毛覆层有相近材质分工；全 UV 与染色运行时仍未实测，暂不提升为已验完整套装案例。'],
    'application_zh':'以后复查其他模组装备，必须先核模型的全部 texture layer；单独打开 layer0 不代表最终图标。同设计的层、染色和 trim 状态不拆计。',
    'preserved_hold':'prior-batch07-semantic-review.json / twilightforest:arctic: zero new credit; hold now narrowed to wearable binding and runtime tint, not absence of white item overlay.'}
(D/'arctic-layer-manual-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(out['status'])
