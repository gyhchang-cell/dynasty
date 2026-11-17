from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pages=[f'icons-{i:02}.png' for i in range(1,5)]+[f'atlas-{i:02}.png' for i in range(1,7)]+['sw_wukong-'+x+'-assembly.png' for x in ['dark_wukong','ghost_wukong','iron_wukong','wukong']]
 out={'scope':'D27原生16px物品图与自定义穿戴模型的完整材质/绑定研究；非Dynasty成稿、非游戏验收',
 'pages_actually_viewed':[{'path':p,'sha256':sha(D/p)} for p in pages],
 'observations':[{'semantic_group':'simian_mask_banded_gold_plate','credit':'NEW_CONSERVATIVE_LEARNING_GROUP','cases':['sw_wukong:'+x for x in ['dark_wukong','ghost_wukong','iron_wukong','wukong']],
 'observation':'四套都是黑底猴面金箍、白眼、双折翎、短台阶肩、横片护臂、腰下分裙、长背带及粗靴；原生图标16×16，胸图用少量横向色带读出肩/腹，不靠高分辨率人台插画。暗色为棕金、普通为橙金、幽魂为青绿、铁为银灰，几何全相同。四张软件正/45/侧/背/黑剪影实际查看，背带与侧挂黑棍清楚，肩/头仍偏大；四张不能计四个设计。',
 'binding_observation':'16条注册工厂→具体槽类→客户端扩展→模型字段→自定义实体图集静态对应：头/胸/腿统一Modelwukong_reworked1，靴用Modelwukong_reworked2；声明分别66/6原始addBox，共72，不是72设计。四套护腿与靴图标字节完全共用，所以幽魂图标的棕靴不能用作其青色穿戴材质范本。四个实体图集各128×128；两个200×200默认inv图集全透明，但16件都在getArmorTexture声明实体图集，不能据此声称全套隐形或缺图。',
 'application':'对Dynasty保留胸腹大块色带、明确衬底、边缘少量离散高光；材质身份须让图标与穿戴一起核对，不能复用棕靴冒充全部配色。借鉴读形而非复制猴面/翎/背带/像素；控制原版肩宽，护腿、披带及靴按目标UV分工。与旧片甲等组比较后单列猴面+背带的保守学习组，四套同模变体合一，未将其自动认证为1000门槛的独立完整设计信用。'}],
 'native_bindings':{'names':4,'icons':16,'distinct_icon_png':10,'source_atlases':6,'custom_worn_atlases':4,'transparent_default_atlases':2,'native_classes':43,'native_model_definitions':2,'raw_addbox_calls':72,'slot_chains':16,'software_sheets':4},
 'dedup_limits':['四套同主模型/同靴模型只增1学习组，不加4','四槽、72体块、两个模型、14页查看或四配色不能加独立设计信用','与既有212组一起仍含变体/反例，已验完整独立设计总数保持未知'],
 'runtime_limits':['静态常量读取未执行模组类；软件组装不证明游戏槽位、玩家动作、采样、shader或接缝','透明默认图不能单独证明隐形，覆盖调用链与其他mod实际行为未实机验收'],
 'new_names':4,'new_learning_groups':1,'new_validated_independent_design_credit':0,'reference_gate_met':False,'production_changes':0,'new_artwork':0,'game_starts':0,'checklist_deletions':0}
 (D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print('D27 four variants conservatively one learning group; no artwork or game acceptance.')
if __name__=='__main__':main()
