from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-native-face-uv-20261111'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 pages=read(D/'source-pages.json')['pages'];obs={
 'botania:manasteel':'图标蓝色短胸、细窄手臂分离、倒U盔面和两只短靴；穿戴源码以9宽盔壳、9宽上胸/5宽腹片、窄护臂与晶体分层，图集不是原版L1。可学胸腹材质分区和点亮接边，不照搬专用UV。',
 'botania:elementium':'粉色甲正面白色集中亮面，头侧尖翼和肩部上挑，裤腰保留深色开口，靴子仍短；源码的零厚平面翼和多段头翼与甲壳分开。只学习少量特征件，Dynasty不得因此扩大普通装备肩宽。',
 'botania:terrasteel':'绿甲大块亮面配棕色枝条，头肩保留分叉和叶片，腿靴同一材料衔接。源码头壳、枝条、叶片、护肩和靴沿为独立Cuboid；适合学习中后期材料身份，但不能移植其整套造型。',
 'botania:manaweave':'青色兜帽深色脸孔、短胸带扣和两片长下摆，鞋用极暗大块区；源码两条腿各带13高旋转裙片，证明长布区有结构用途，不能把长袍L2一律当错误填色清掉。'}
 review={'scope':'D34 Botania四套原生图标与专用穿戴图集、源码默认分支；未重建3D、未实机','pages_actually_viewed':pages,'observations':[{'case_key':k,'observation':v} for k,v in obs.items()],'grouping':'三套金属甲暂并为一个作者共享分段甲风格学习组；法袍并入既有长袍组。不是四个已验独立完整设计。','new_reviewed_name_families':4,'new_conservative_learning_groups':1,'new_validated_independent_design_credit':0,'reference_gate_met':False,'runtime_acceptance':False,'pending':['默认16槽原生源码链已读取；phantom ink隐形和holiday分支未实际看图，不加信用','专用模型实际三维、正侧背45度黑剪影与真实穿戴接缝仍待验','与既有同类完整设计进一步语义比较后才可记有效独立设计信用']};save('semantic-review.json',review)
 ledger=read(P/'combined-semantic-ledger.json');group='botania_segmented_crystal_fairy_branch_plate_family';source=str((D/'semantic-review.json').relative_to(R));members=['botania:manasteel','botania:elementium','botania:terrasteel'];assert all(k not in ledger['reviewed_case_keys'] for k in obs)
 ledger['groups'].append({'semantic_group':group,'cases':members,'observations':[{'source':source,'observation':'三套共享分段甲体系保守合组；图标和图集已看，专用三维与运行未验，不算完成信用。'}]})
 for k in members:ledger['case_to_group'][k]=group
 robe=next(g for g in ledger['groups'] if g['semantic_group']=='immersive_robe_open_front');robe['cases'].append('botania:manaweave');robe['observations'].append({'source':source,'observation':obs['botania:manaweave']});ledger['case_to_group']['botania:manaweave']=robe['semantic_group'];ledger['reviewed_case_keys']=sorted(ledger['reviewed_case_keys']+list(obs));ledger['name_families']+=4;ledger['armor_name_families']+=4;ledger['conservative_learning_groups']=len(ledger['groups']);ledger['source_reviews'].append({'path':source,'sha256':sha(D/'semantic-review.json'),'new_names':4,'new_groups':1,'new_validated_independent_design_credit':0});save('combined-semantic-ledger.json',ledger)
 print('Four newly viewed namefamilies; one conservative learninggroup; zero new validated independent design credit.')
if __name__=='__main__':main()
