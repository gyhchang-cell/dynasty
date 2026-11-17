"""D22: observations after all three icons and six original-atlas pages were opened."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
keys=[c['case_key'] for c in json.loads((D/'provenance.json').read_text())['cases']]
hard=[k for k in keys if ':hardened_' in k];scales=[k for k in keys if ':mutant_' in k]
assert len(hard)==len(scales)==8
rows=[{
 'semantic_group':'complete_chitin_rib_shell_flared_hip','cases':hard,'credit':'NEW_CONSERVATIVE_LEARNING_GROUP',
 'observation':'八种硬化甲壳甲共用分叉额角和暗闭面、由粗横肋与两竖线围出的开口胸壳、腰两侧外翻小刺和较长分腿靴。海生青、洞穴粉白、绯红洋红、末影紫、丛林绿、恶地棕橙、沼泽黄、诡异青绿只是同一完整壳架的环境配色，八名合为一个保守学习组，不能当八套独立设计。区别于封闭肉甲的是胸中镂空壳架与外翻腰片连续；可学外壳对内衬的粗线层次和脚背亮护片。128方原图同一UV岛布局，深色壳片间密集亮点，反例是黑大面在暗界面不易读、亮色满身撒开和肋线过细；Dynasty需集中识别区、保留大块材料面。仅头盔getArmorTexture直接字符串已读，其他槽位与模型全链未核，图集不是标准64×32。'
},{
 'semantic_group':'dragon_scale_family_conservative','prior_group':'dragon_scale_family_conservative','cases':scales,'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS',
 'observation':'八种突变鳞甲共用双侧长斜角、短V肩胸片和中间深竖缝、倒U裤和有明显脚尖的长靴。洞穴粉白最亮，其余蓝/红紫/紫/绿/橙/黄/青基本同一轮廓；全追加已有龙鳞甲族而不以生物名和环境换色加信用。胸、裤、靴比硬壳族更接近普通甲比例，借鉴腰腿开口清楚和两脚分离。八张128方原图都大片密棋格式鳞纹，缩成物品栏会噪，不能照搬为粗像素成稿；只借明暗面分区而非满图重复小鳞。Crimson的部分物品图层名叫nether，这是源声明命名，不当缺图。头盔返回的entities图集存在，但未证四槽全链。'
},{
 'semantic_group':'organic_flesh_rib_armor_family','prior_group':'organic_flesh_rib_armor_family','cases':['pathogen:pathogen_armor'],'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS',
 'observation':'病原甲是短圆暗罩盔两侧米金骨脊、中央暗胸与左右成V的黄褐骨片、窄直腿甲和有脚背折角的双靴。比彩色鳞甲少了长角，但与已有有机骨肋族保守合并，不凭短角和颜色再计整套。64方图集骨米色集中在肩/胸与边缘、其余深褐，局部斑点很密；可学硬骨承托暗软层的色块主次，避免肌肉人台、全身细碎骨线和浅骨白满铺。原图、声明和头盔类字节已固定，未核模型或四槽玩家显示。'
}]
flat=[k for r in rows for k in r['cases']];assert len(flat)==len(set(flat))==17 and set(flat)==set(keys)
x={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':[f'icons-{i:02}.png' for i in range(1,4)]+[f'worn-{i:02}.png' for i in range(1,7)],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':17,'native_icon_entries_viewed':68,'item_model_declarations_read':68,'native_layer_candidate_entries_viewed':17,'helmet_texture_declarations':17,'animation_metadata_present':0,'new_conservative_learning_groups':1,'append_observations':2,'limits':'四件图标完整名称仍不是适用独立完整设计验收；两个八环境配色系列分别保守合并。新硬壳组仅为学习组，已验独立整套总数仍未核定。额外三板甲名称仅外部指针、零已读信用。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
(D/'semantic-review.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('17 names / 68 icons / 17 atlases / 1 conservative learning group, 2 append observations')
