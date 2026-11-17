"""Source icon findings do not silently promote wearable binding holds."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
x=json.loads((D/'held-item-source-binding.json').read_text())
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),inspection_sheet=x['inspection_sheet'],
 source_item_jsons_read=4,source_pngs_opened=4,new_equipment_case_credit=0,production_changes=0,
 rows=[
  dict(item='alexscaves:primordial_helmet',observation_zh='当前原始 item JSON 只引用单层骨白头壳图，与旧索引的原PNG字节完全相同；不能将它当新头盔案例。',conclusion='SAME_ITEM_ICON_EXACT_BYTES_NO_NEW_CREDIT'),
  dict(item='alexscaves:primordial_tunic',observation_zh='胸衣图标是橙褐毛皮与两侧骨色短束件；整图集中的橙褐材料并不与骨白头盔矛盾，可能属于不同装备部位。',conclusion='ITEM_SLOT_ICON_CONFIRMED_NOT_PER_FACE_WEARABLE_BINDING'),
  dict(item='alexscaves:primordial_pants',observation_zh='裤图标为浅肤/皮褐主面，黑褐腰边与脚端；浅色不是头盔骨壳的统一白色主材。',conclusion='ITEM_SLOT_ICON_CONFIRMED_NOT_PER_FACE_WEARABLE_BINDING'),
  dict(item='cataclysm:monstrous_helm',observation_zh='原模组实际 JSON 引用短灰黑罩、左右橙色下角图标；旧 Modular Golems 图为金白高双角与红额，两者不应作为同一玩家头盔配对。',conclusion='WRONG_PRIOR_EQUIPMENT_SOURCE_EXPLICITLY_REJECTED'),
 ],
 remaining='Primordial resource-only item chains explain material differences but do not bind head/body/leg atlas faces. Cataclysm correct icon rejects old expansion pairing; global prior/new-design acceptance still pending. No wearable geo or runtime acceptance claimed.',
 policy='Supplementary4 source PNG reads include one exact previously viewed icon; do not add4 independent designs or promote a hold to full UV acceptance.')
(D/'held-item-manual-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
