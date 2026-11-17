"""Written after all two icon and seven complete native atlas analysis pages were opened."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=[]
def row(group,cases,observation,new=False):
 x={'semantic_group':group,'cases':cases,'observation':observation,'credit':'NEW_CONSERVATIVE_LEARNING_GROUP' if new else 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'}
 if not new:x['prior_group']=group
 rows.append(x)
row('vanilla_outline_elemental_palette',['l2complements:'+s for s in ['eternium','poseidite','sculkium','shulkerate','totemic_gold']], '五套都以紧凑全罩盔、V领短胸、窄腰与分靴组织，保守合并已有原版材料甲模板，不把五种矿物计为五个设计。永恒甲蓝紫大面和白横额/亮肩、海神甲暗青蓝主面浅青胸带、幽匿甲深蓝与米白横眉/节点、潜影甲紫壳配棕红侧板、图腾金甲金面配少量绿点分别表达材料。腿图标有腰与膝小片而非把整腿填满亮色；原生64×32层均留透明间隔，但未证选中绑定，不能直接照坐标抄至Dynasty。永恒甲头肩亮度偏满作为限制；图腾绿点应少而明确，不增加全身噪点。')
row('complete_noir_mask_top_hat_tailcoat',['brutality:noir'], '低圆柱礼帽的台阶帽檐、白色两眼面具与窄下颌，下方黑西装以白领结/胸前小块、开襟和暗袖分区；裤腿宽窄不等于裙，鞋是成对短靴。帽+面具+领口组合暂设保守学习组；帽的圆形只学阶梯体块，不做圆滑高模。原生64×96图集另有帽顶圆环和西装分岛，非标准盔甲UV；发光候选只见极少孤立白点，不推断渲染bug，也不计成第二套。借鉴黑底上用少量中灰接缝与白领保持可读，不能让全套变成无层次黑块。',True)
row('wood_green_armor_family',['brutality:terra'], '棕木面带两根绿短枝、胸左右树皮块由中间暗缝分开，绿细藤顺着衣襟和腿中段延续；靴的浅色脚面与棕侧明确。追加木绿族，不因独特原生128×128图集再计一套。原生材料图有大木板面、深接缝、少量绿苔，另有独立稀疏绿点发光层；大面颗粒密度偏高，只借材质先后，不能用噪点画满现有竹布甲。')
row('dragonsteel_tall_plate',['dreadsteel:dreadsteel'], '黑色闭面盔留两点紫眼，胸有两根高肩柱和三块窄竖前板，腰腿同样靠黑灰分面，靴边少量紫点。保守追加既有龙钢高板甲族，黑白铜自定义模型覆盖只是同套颜色分支，未读分支图也不给信用。256×256原生候选包含上部黑纹大面、灰构件和紫节点，是专用图集，绝不能当64×32模板套用；小图肩柱偏高、纯黑面积过大作为MC紧凑比例的反例。')
row('complete_cardboard_box_folded_armor',['create:cardboard'], '平顶方纸箱头两个低位暗孔，胸为窄上口的直方纸板背心；腰横盒与两条直纸裤腿、两只小纸靴统一材料。图标用浅棕主面、深棕折边和有限横纸纹，无金属高光，区别于木板甲的硬护板结构。新增保守纸盒折边学习组；只学折线和留白，不能直接复制原版造型来冒充原创。两张原生64×32图层衣口深、袖条短，裤边有浅色竖条，仍需实际模型/材质绑定后才能判断对应接缝。',True)
row('complete_mechanized_dark_frame',['threateningly_mobs:bionics_armor'], '白蓝正面装甲片加暗紫外框，头面和胸上口各有少量暖橙，腹部三段横片、靴前口同色节点，追加机械骨架组。bionics_layer与bionic_armor_layer两对候选外观明显不同：前者灰白旧片、后者青白橙现代片；不能用近似名称假设前者已绑定或坏图。只学装甲板间保留关节暗隙，过亮白面容易像塑料，避免扩散柔光。')
row('vanilla_outline_elemental_palette',['threateningly_mobs:desert_armor'], '土灰面板配暗红棕连接，短头盔略遮颊，V领胸与裤膝横带、靴筒浅面构成基础材料模板，保守合并原版轮廓族而不因沙漠名另算设计。原生两层有密集交叉/棋盘带，只借土色主次和边口连接，不把粗布/皮甲画成全身高频格纹。')
row('souls_black_knight_dark_silhouette',['threateningly_mobs:ebonlord_armor'], '黑面窄灰额、两短侧角，胸浅灰倒V与暗腰、裤膝窄灰面和靴上口相应，追加黑骑士剪影族。图标比候选亮很多；ebonlord_layer_1候选几乎只见一条黑条，layer_2有少量暗胯腿片，未查实际渲染链不得断言缺失或显示异常。避免黑贴图只有图标可读而实际图层无分区，最终应核实际选中资源。')
keys={c['case_key'] for c in json.loads((D/'provenance.json').read_text())['cases']}
flat=[c for r in rows for c in r['cases']];assert len(flat)==len(set(flat))==12 and set(flat)==keys
assert len(rows)==8 and sum(r['credit'].startswith('NEW_') for r in rows)==2
out={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':['icons-01.png','icons-02.png']+[f'worn-{i:02}.png' for i in range(1,8)],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':12,'native_icon_entries_viewed':48,'item_model_declarations_read':48,'native_layer_candidate_entries_viewed':25,'animation_metadata_present':0,'new_conservative_learning_groups':2,'append_observations':6,'limits':'12完整四部件名称不等于12独立设计；25图集/发光候选无实际穿戴绑定证据。205学习组含局部/反例；有效独立完整设计总数未知，1000门槛未达。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
(D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('12 complete names / 48 icons / 25 native candidates / 2 new conservative groups / 6 appended observations')
