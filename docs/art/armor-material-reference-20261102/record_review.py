"""Record 11 actually viewed icon pages with cross-batch template merging."""
from pathlib import Path
from datetime import datetime,timezone
import json

D=Path(__file__).resolve().parent
R=D.parents[2]
def read(p):return json.loads(p.read_text())
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    p=read(D/'provenance.json');available={c['case_key'] for c in p['cases']};groups=[]
    def g(key,cases,note,prior=None):
        groups.append({'semantic_group':key,'cases':cases.split(),'observation':note,
                       'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                       **({'prior_group':prior} if prior else {})})
    special={'corrupted','skythern','divine','elite_realmite','realmite','frozen','santa'}
    plain=sorted(c for c in available if c.startswith('divinerpg:') and c.split(':')[1] not in special)
    plain.append('valoria:black_gold')
    g('vanilla_outline_elemental_palette',' '.join(plain),
      '32个DivineRPG名称及Valoria黑金甲，共享原版短胸、倒U帽口、直裤与L靴基本版式；末影和卢比各色、盐类/层级胸色、附加兜帽与零散材料纹都保守合并入前批已有模板。颜色/头件变体并非同像素，但不能各算新设计。观察正面亮面、窄暗侧与少量领口留白，不把红衣青帽的游戏配装自动当成要复制的材料标准。',
      'docs/art/armor-continuation-20261102/reference-review.json#vanilla_outline_elemental_palette')
    g('banded_plate_variants','divinerpg:corrupted divinerpg:skythern','紫甲与白灰甲的胸片横向粗分带比普通整色胸面更明确，头腿仍接近基础版式；保守同组。条带应用于材质分片，不能变成满画布细条/渐变。')
    g('divine_ornate_gold','divinerpg:divine','金胸有分开的横片/红色连接，帽边短外伸，灰靴与金腿有材料区别。神圣感主要来自成块金面与少量红/暗缝，不能用巨大圆肩和人台身段替代。')
    g('realmite_crown_versions','divinerpg:elite_realmite divinerpg:realmite','同系列橙金胸与冠式头件，精英版胸前多几何纹；两版保守合并。冠仅局部改变头顶，正面甲体保持短宽，不能把中心纹放大挤掉底材。')
    g('frozen_crown_plate','divinerpg:frozen','浅冰蓝的阶梯冠和胸肩边比普通平顶头壳有明确外形变化，胸与腿中间仍留深缝。只学少量冰晶阶梯，不将青蓝甲全涂成连续白高光。')
    g('santa_fur_trim_clothing','divinerpg:santa','红衣以白色交襟/毛领分成明确块，黑靴白口、短帽白边有服装身份。白边是毛料主体，不能当白背景删除；四部位和帽/胡须式前缘只算同套。')
    g('botanical_boot_variants','terra_equipment:flower terra_equipment:tiki','两张都是带植物顶饰的单靴侧面：紫靴绿叶与棕靴橙顶。按近亲植物靴合并；单侧靴可作材料/外形研究，但本项目盔甲物品仍遵守已认可双短靴比例，不照搬单脚图。')
    g('gem_plate_metal_variants','terra_equipment:silver terra_equipment:tungsten terra_equipment:platinum','浅金属V胸与一颗中心彩扣、角状头件共享版式，银/绿/浅紫按材质变体合并。小扣能区分材料，胸侧仍应大块低亮，不用整片噪点。')
    g('dark_rib_chest_variants','terra_equipment:crimson terra_equipment:shadow','暗红与暗紫短胸均用大黑缝隔开条片与肩区，保守同组；不是说像素相同。深底只在边缘给少量亮色，能保持低亮装备轮廓。')
    g('gemmed_sharp_plate_variants','terra_equipment:adamantite terra_equipment:meteor','洋红/青白与紫红/橙黄共享尖肩V胸和中央小亮点，头件局部不同；保守合并。高阶甲允许鲜明材料对照，但不沿所有边平均撒高光。')
    g('cold_crystal_open_plate','terra_equipment:cold_crystal','浅青与深蓝框片、中央大负形使胸部结构明确，靴和裤用尖阶梯衔接；不是本项目重画骨骼授权。借鉴块面分工，保持用户原版比例。')
    g('fossil_bone_plate','terra_equipment:fossil','浅褐骨片围暗缝，胸部翼状骨与裤膝小金缘构成同套，只有三件。骨白/褐是材质分区而非白底；不把每根骨头当成新参考。')
    g('heim_blue_angular','terra_equipment:heim','胸甲是青蓝V片与深蓝外框，头盔两侧尖片绕黑口；仅两件。阶梯斜边能表达高级材料，但外挑尖片需克制，不能让装饰淹没主体。')
    g('jungle_leaf_headgear','terra_equipment:jungle','仅头件，蓝白顶块配几层绿叶。粗层片组织明确，用于学习植物身份，不推断不存在的胸裤靴。')
    g('mining_apron_chest','terra_equipment:mining','仅胸甲：棕色肩带和深青围裙胸面，材料/工作用途清楚；没有宝石仍能识别。适合朴素装备保持大色面，不为高级感强添金边。')
    g('molten_plate_dark_shell','terra_equipment:molten','暗灰/褐壳占主体，红橙集中在下缘/关节缺口；四部位重复同一材料逻辑。不将熔亮纹画满所有面，避免整体变成均匀橙色。')
    g('palladium_crested_helmet','terra_equipment:palladium','仅金色前面甲与浅灰顶羽/侧壳，黑色面口保留身份。封闭前甲可以有目的存在，不自动要求露脸。')
    g('awakened_void_segmented','valoria:awakened_void','暗紫胸体、窄粉亮边与两块分离肩甲，头部亮心为单大块；两腿和短靴轮廓分开。粉色只作少量部件身份，不形成柔光球。')
    g('cobalt_ethereal_plate_variants','valoria:cobalt valoria:ethereal','蓝白与青白共享横分段胸和闭合水平面罩，保守同组。面罩保留一条粗暗缝，头顶/胸片亮面为大区，不把闭盔误判封脸bug。')
    g('crimtane_depth_framed_plate','valoria:crimtane valoria:depth','红橙/暗灰与亮青/红边共享几何框胸、分段腿和横向盔架，局部配件有差别，保守同组。取材料分区、窄腰黑缝，不复制配件。')
    g('knight_metal_color_family','valoria:diamond_knight valoria:golden_knight valoria:iron_knight','青、金、银骑士同有红背布、短羽盔与圆阶梯胸片，合并同族材质款；铁版本批未含靴。可学金属前亮后暗/布料单大红区，但肩部圆块是需收敛的反例，不加大已认可肩宽。')
    g('warm_plate_helm_variants','valoria:infernal valoria:pyratite','火红与橙金使用分离肩块、前面甲和直裤；帽檐/鼻甲差异尚不拆计。黑缝连贯，比全身均匀金线更利于小尺寸识别。')
    g('wood_green_armor_family','valoria:marsh valoria:nature','棕木框和绿衬/绿亮区构成同族，头件层级与胸形有不同但保守合并。材料色与承力框应分开，绿色不能只随意点在金属边上。')
    g('phantasm_closed_face_plate','valoria:phantasm','蓝银小甲片构成闭面盔与分片方肩，胸前大暗缝/窄亮层明确；两腿与短靴直立。闭面可为设计目标，不能一律擦成U口。')
    g('samurai_plate_variants_conservative','valoria:samurai','本批仅红黑金胸、裤、靴，横向层甲与既读武士版式近亲；归入前批已有武士组，额外新增信用为0。颜色条带不等于新结构，亦不推断头盔。',
      'docs/art/armor-worn-uv-20261102/reference-variant-review.json#samurai_plate_variants_conservative')
    g('spider_blue_cloth_shell','valoria:spider','灰紫封面头盔、深蓝胸心、分离灰肩，靴筒直立；颜色与大片分工清楚，蛛材身份由局部胸纹表达。肩片宽度应视为对照，不能直接增宽本项目原版肩。')
    g('collector_hooded_legwear','valoria:the_fallen_collector','棕兜帽配金色口缘、棕直裤与红靴，只有三件；帽前的阶梯负形能表达职业，浅金边不占满帽身。不能补造未见胸甲。')
    flat=[c for r in groups for c in r['cases']]
    assert len(flat)==len(set(flat))==72 and set(flat)==available
    new=[r for r in groups if r['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP']
    appended=[r for r in groups if r['credit']!='NEW_CONSERVATIVE_LEARNING_GROUP']
    assert len(new)==25 and len(appended)==2
    save('semantic-review.json',{'reviewed_at':datetime.now(timezone.utc).isoformat(),
      'pages_opened':[f'icons-{i:02}.png' for i in range(1,12)],'observations':groups,
      'icon_name_families':72,'original_icon_png':259,'new_conservative_learning_groups':25,
      'append_to_existing_groups':2,'prior_learning_groups_reused':57,'combined_conservative_learning_groups':82,
      'combined_name_families':192,'fresh_worn_png':0,'new_artwork':0,'production_changes':0,'gate_met':False,
      'counting':'两个连续批次共117个新打开名称族/403张图标，加101张原生穿戴图；同套部位、颜色、版本、附层不分计。当前全部证据合并为82保守设计学习组；这不是1000独立盔甲达标证明。',
      'prior_context':'collection-context.json','limits':'本批只看库存设计/材料与比例；没有生成穿戴图、修改112保护图标或运行游戏。已读同模板追加原组，绝不每批清零凑数。'})
    print(json.dumps({'reviewed_names':72,'reviewed_png':259,'new_groups':25,'append_prior_groups':2,'combined_groups':82},ensure_ascii=False))

if __name__=='__main__':main()
