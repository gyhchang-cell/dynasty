"""Record the actual 7 icon and 17 native-atlas pages viewed in this batch."""
from pathlib import Path
from collections import Counter
import hashlib,json,zipfile

D=Path(__file__).resolve().parent
R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,a):(D/n).write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')

def main():
    provenance=read(D/'provenance.json');available={c['case_key'] for c in provenance['cases']};groups=[]
    def g(key,cases,note):groups.append({'semantic_group':key,'cases':cases.split(),'observation':note,'status':'VIEWED_CONSERVATIVE_RELATED_DESIGN_LEARNING_GROUP'})
    g('abyssal_purple_plate','aquamirae:abyssal','仅库存裤靴：紫黑主材、腰部白扣和靴外紫亮边；原生穿戴图胸片是成对弧边与大块深紫区，帽壳与冠带拆图。部位不分计，不能照搬其专用UV。')
    g('terrible_icy_ribs','aquamirae:terrible','青亮肋形胸片、分叉下摆与尖顶盔构成同套；深青底占主要面积，亮青限制在棱与粗肋。穿戴图有专用散开条带与尖片，不能按64×64尺寸认定原版布局。')
    g('three_bolt_diver','aquamirae:three_bolt','铜边封闭潜水盔与灰布直裤有实际用途；圆窗以阶梯块近似。封闭面孔是有意装备身份，不可把不露玩家脸统一当错。穿戴窗格分区与普通头壳不同。')
    g('bone_reptile_rib_vest','cataclysm:bone_reptile','单件骨肋胸甲：金白肋片围深蓝底，宽肩和窄腰用留黑缝分开。原生128图集是专用片区；只记一件设计，不把每根肋片计数，也不按本项目身体UV硬套。')
    g('cursium_related_plate_conservative','cataclysm:cursium traveloptics:cursed_wraithguard','均为青金胸心、红褐包边与宽肩，局部附层更复杂；跨模组升级/近亲外观保守同组，未声称完全同像素。原生128图集附层不当额外设计。亮青只集中在胸心，能避免全身均匀发亮。')
    g('ignitium_elytra_same_kit','cataclysm:ignitium cataclysm:ignitium_elytra','深红甲片和黄橙边沿形成同套火甲；鞘翅胸版是本套扩展，合并不另加。黑红内部给亮橙外缘留空间，盔口是深色负形；不借机给鸿蒙添加火焰角。')
    g('sterling_padded_metal','galosphere:sterling','两个归档版本的棕红绗衣、浅青肩/腕甲和棕靴合并。大块软布与小块硬金属有明确面积关系，金属不必铺满身体。原生64×32内层腿/腰与外层胸肩分开。')
    g('black_iron_buckled_vest','goety:black_iron','库存只胸甲，平直黑肩、灰锁片与圆方扣构成单件身份；原生64×64有大片底材与独立附条，灰亮仅分配给扣和边。不能根据缺失图标虚构整套。')
    g('cursed_knight_closed_visor','goety:cursed_knight','深蓝封闭面甲配短红羽，层叠胸片与两条细直腿；该头型应保持封闭，不自动开大U口。128×64原生图区还含下摆，不能把该下摆当成Dynasty layer_2整胸应保留的证据。')
    g('dark_paladin_shared_shell','goety:cursed_paladin goety:dark','深青壳胸和双上角盔轮廓近亲，dark主要增加绿色点缀；保守合并。区别可以用一处小色块表达，底材仍应是连续大区，不把面板拆成噪点。')
    g('apocalyptium_bright_plate','goety_revelation:apocalyptium','整套橙红与淡黄阶梯条；64×32穿戴图对亮部/暗条作大区分配。强光比款只学形状与色区，不能把全图高亮细纹套到朴素布竹甲。')
    g('spectre_rib_shared_family','goety_revelation:spectre goety_revelation:spectre_darkmage','两款同族肋状胸、直腿和骨边，暗法师有紫色替代与额外帽图；保守合并。帽64×64、基础甲64×32是同套资源分工，不能算额外设计。')
    g('spider_armor_variants','goety_revelation:spider goety_revelation:spider_darkmage','紫红蜘蛛头眼与青蓝法师变体共享肩/肢线结构，合并。原生128图只在甲片边、腰与蛛形附片上留发亮纹；附片不是基础人形身体新增授权。')
    g('wizard_hat_robe_variants','irons_spellbooks:archevoker irons_spellbooks:electromancer irons_spellbooks:pyromancer irons_spellbooks:pumpkin irons_spellbooks:wandering_magician','五款帽袍胸型有黄长襟、蓝灰红带、红圆肩、棕布和蓝披肩等局部差别；按同系列帽袍版式保守合并，不声称相同图片。大面积底布+窄襟边比满幅雕花更适合MC布甲。')
    g('cryomancer_fur_collar','irons_spellbooks:cryomancer','白色宽领与近黑内布对照明显，裤靴以短浅边重复材料身份；主体仍短宽。96×96专用UV含领围片，不直接转成普通身体骨骼。')
    g('cultist_belted_cloth','irons_spellbooks:cultist','棕红衣身、灰肩披与单个腰扣，灰帽下留暗面；软布层级靠两三块材料表达，无密金线。适合借鉴布/皮/织锦的收边节奏，而非复制图形。')
    g('infernal_gold_coat','irons_spellbooks:infernal_sorcerer','仅胸甲：黑底、金外襟、红中线；金色沿衣缘有连续形状，内布保持一大暗区。金边不能扩大到压住胸甲原版比例。')
    g('mage_wizard_version_family','irons_spellbooks:netherite_mage irons_spellbooks:wizard','下界法师两归档版本变化很大：黑红钢肩/尖帽与浅白紫袍；wizard又有白紫交襟与兜帽。保守合并版本/同族，不以改名和每版四部位凑数；颜色和材质确实不同，未声称字节相同。')
    g('paladin_gold_single_chest','irons_spellbooks:paladin','单件金胸甲，亮胸心、暗金侧与分开的方肩组成短宽体；没有库存头裤靴不能补全参考。用于学习大亮面与边侧暗色，不照搬黄白炫光。')
    g('plagued_hood_beak','irons_spellbooks:plagued','深绿灰兜帽与白喙状前片建立职业身份；胸/裤用低亮大面，黄褐仅作缘。帽前的浅色功能部件是主体，不能当成白背景删掉。')
    g('priest_white_gold_cloth','irons_spellbooks:priest','白色胸襟/肩片配金边，暗缝分开身段；金面罩与白衣属于有意闭面/分层。96图集与本机geo原生逐面UV要一起读，不可直接缩为64×32。适合鸿蒙学白材为主、金边为辅的面积关系。')
    g('shadowwalker_version_family','irons_spellbooks:shadowwalker','两版黑紫暗甲存在肩形和头口变化，合并同套历史版本。暗甲用灰紫边区维持辨识，不宜靠纯黑大块抹掉部位轮廓。')
    g('speed_boots_single_item','irons_spellbooks:speed','仅一双棕靴，白短翼/翻边位于靴筒上侧，脚掌仍短且分开。单件设计只记一次，不把左右脚或贴图片区拆计；不自动用于所有靴子。')
    g('abyssal_hide_cloth','traveloptics:abyssal_hide_mage','库存仅裤靴，紫色沿膝/靴端少量发亮，暗布连为大块；128专用穿戴及稀疏亮层只记同套。可学克制点缀，不学额外人形挂件或复杂骨骼。')
    g('deepling_mage_rib_cloth','traveloptics:deepling_mage','青色靴横带、深蓝面、头部细紫点共同识别；64×64原生有肋片、帽与不对称布纹专用区。不能把附层的透明缺口当成底材缺面。')
    g('forlorn_harbinger_dark_flaps','traveloptics:forlorn_harbinger','库存仅黑红外翻靴；128穿戴图有大块暗红片与窄红纹，说明单张图标不能推断完整身体穿戴。只记录现有设计证据，不虚构部位。')
    g('crest_plate_variants','traveloptics:primordial_crest traveloptics:tectonic_crest','两款深红黑同形短胸、角肩与浅色/熔红边，轮廓近亲保守同组。底图与发亮层为同套，不拆计；肩角只作比例反例，不能加大本项目已认可肩宽。')
    g('riptide_blue_gold_legwear','traveloptics:riptide_sovereign','库存裤靴以青蓝鳞条和少量金缘辨认，原生128图的金线区较密；学蓝主金辅的面积组织，不把高频线条整套挪入鸿蒙/青龙。')
    g('arctic_fur_leather','twilightforest:arctic','棕皮衣裤配白毛帽和毛口，64×32原生图把染色底与固定棕皮包边分开；_dyed/_overlay均属同套。袖/下摆的软毛边由少量阶梯缺口表达，不需柔光渐变。')
    g('ironwood_metal_rivets','twilightforest:ironwood','灰褐铁木甲只用小浅绿钉/扣装饰，肩胸裤脚均保持大灰面。库存四部位和穿戴两层是一套，亮扣位置一致可学，不能照搬排列。')
    g('knightly_metal_waist','twilightforest:knightmetal','本批库存只有腿甲：暗绿直腿、红腰与黄扣；原生外层另含浅绿金属面/盔口。以同套合并，不把缺图标误记成新套，也不凭原生帽口要求所有闭盔改开口。')
    g('naga_scale_green','twilightforest:naga','库存胸裤两件，亮绿胸心和暗边的大鳞块；穿戴前后与腿边的粗条排列仍有材料一致性。没有库存头靴不虚构；本套专有胸材不等同钢叶的换色。')
    g('steeleaf_leaf_plate','twilightforest:steeleaf','斜叶胸片和相连裤腰、深绿腿边区分于娜迦大胸心；两种绿色装备有实际纹样结构差异。用几片大斜阶梯表达叶材，避免满身细碎鳞点。')
    g('yeti_pale_blue_fur','twilightforest:yeti','白毛大面、蓝色边/角与窄暗缝，保持短宽胸形；64×32穿戴中大白衣面用粗蓝缝分段。白色是主体毛料，绝不能按白底去除；角与毛口不等于新增独立设计。')
    flat=[c for r in groups for c in r['cases']]
    assert len(flat)==len(set(flat))==45 and set(flat)==available
    assert len(groups)==34
    prior=read(R/'docs/art/armor-worn-uv-20261102/reference-variant-review.json')
    prior_cases=set()
    for p,key in [(R/'docs/art/armor-continuation-20261102/reference-review.json','observations'),(R/'docs/art/armor-worn-uv-20261102/reference-variant-review.json','observations')]:
        prior_cases.update(c for g in read(p)[key] for c in g['cases'])
    assert not prior_cases&available
    save('semantic-review.json',{'icon_pages_opened':[f'icons-{i:02}.png' for i in range(1,8)],
          'worn_pages_opened':[f'worn-{i:02}.png' for i in range(1,18)],
          'observations':groups,'reviewed_icon_name_families':45,'reviewed_icon_png':144,'viewed_worn_png':101,
          'new_conservative_learning_groups':34,'prior_conservative_learning_groups':23,
          'combined_conservative_learning_groups':57,'combined_name_families':len(prior_cases|available),
          'counting':'本批45名称族合并为34组，与前批23组复用合并，共57个保守设计学习组；非1000达标证明。穿戴101PNG是相同设计的部位/附层/版本，新增独立设计信用为0。',
          'prior_review':'docs/art/armor-worn-uv-20261102/reference-variant-review.json',
          'supplementary_worn_not_new_designs':['fiery','phantom','frost','bone_crown','gold_crown','tarnished','monstrous_helm','bloom_stone_pauldrons','mechanized_exoskeleton'],
          'gate_met':False,'production_allowed':False,'game_acceptance':False})
    # Exact native geometry is study evidence, never copied into Dynasty.
    jar=next(j['path'] for j in provenance['archives'] if '3.15.6' in j['path'])
    native=[]
    with zipfile.ZipFile(jar) as z:
        for kind in ['priest','wizard']:
            entry=f'assets/irons_spellbooks/geo/{kind}_armor.geo.json';data=z.read(entry)
            target=D/'native-geometry'/f'{kind}_armor.geo.json';target.parent.mkdir(exist_ok=True);target.write_bytes(data)
            geo=json.loads(data)['minecraft:geometry'][0]
            names={'armorHead','armorBody','armorRightArm','armorLeftArm','armorLeggingTorsoLayer','dyeArmorLeggingTorsoLayer'}
            native.append({'jar':jar,'entry':entry,'sha256':hashlib.sha256(data).hexdigest(),'local':str(target.relative_to(D)),
                 'description':geo['description'],'selected_bones':[b for b in geo['bones'] if b['name'] in names],
                 'meaning':'原生96×96与逐面/盒UV/独立衣摆，不能直接套本项目64×32；命名相关性不单独证明渲染器运行绑定。',
                 'runtime_binding_proven':False})
    save('native-geometry-study.json',{'models':native,'new_design_credit':0,'body_changes':0,
          'observations':['priest腰部专用8×4×4小盒使用V=28..31，与上胸分工明确；袖子有不等长专用盒与逐面UV。只学局部职责，不挪用其骨骼。',
                          'wizard有dye与固定装饰两组盒、独立长衣摆，穿戴96×96；原生某些整躯干层来自有意的服装系统，不可拿整胸不透明单独判所有盔甲错误。']})
    materials={}
    for m in ['hongmeng','cinnabar','brocade']:
        paths=[R/f'src/main/resources/assets/dynasty/textures/item/{m}_{part}.png' for part in ['helmet','chestplate','leggings','boots']]
        materials[m]={'icons_to_preserve':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in paths]}
    principles=[
      {'finding':'F1_ISOLATED_SLEEVE_CAPS','materials':['bamboo','brocade','cloth','leather','sea_silk'],
       'source_evidence':'docs/art/armor-worn-uv-20261102/findings.json#orphan_caps',
       'related_groups':['arctic_fur_leather','sterling_padded_metal','cultist_belted_cloth'],
       'apply_after_gate':['先依据获选袖型决定短袖开口或长袖收口，不为修alpha问题重新设计衣服。','短袖时保留现有侧面裁切并去掉物理腕底的孤立可见端片；不能把底片画到缩短的袖口位置假装移动了几何。','长袖时让末行四面与端盖形成连贯包边，前后/两侧同高；保持原材质大色区，左右共享UV按现有镜像检查。'],
       'acceptance':['本项目实际UV的4条端盖邻边逐条有明确开口或材料连接意图','不修改头胸/人物骨骼或库存图标','后续实际屈肘/持物验证仍需保留']},
      {'finding':'F2_OLD_WHOLE_TORSO_WORN','materials':['bronze','general','jade','sky','xuantian'],
       'source_evidence':'docs/art/armor-worn-uv-20261102/waist-coverage-review.json',
       'related_groups':['three_bolt_diver','cursed_knight_closed_visor','ironwood_metal_rivets','knightly_metal_waist'],
       'apply_after_gate':['逐套以精致获选图标确认板甲/衣袍/面甲意图；闭盔保留有意义的面甲轮廓，不自动全部开脸。','对普通护腿，内层躯干职责是腰部包裹；先核获选护腿腰线，再限制覆盖范围，避免旧胸章重复出现在腿甲槽。','若获选设计确为长袍/高腰护腹，保留有目的的覆盖，不照抄原生板甲掩码擦掉衣料。','材质按既有铜、将军黑金红、玉、白蓝金、金白等身份分大区，原尺寸适配UV；不再运行旧满画布渐变生成器。'],
       'acceptance':['仅腿槽与全套穿戴分别核验，避免胸甲遮住内层问题','head与hat两壳分别按面甲意图裁切','全部20精致老库存图标SHA不变']},
      {'finding':'F3_SELECTED_ICON_WORN_MATERIAL_MISMATCH','materials':['hongmeng','cinnabar','brocade'],
       'related_groups':['priest_white_gold_cloth','yeti_pale_blue_fur','cultist_belted_cloth','infernal_gold_coat'],
       'apply_after_gate':['鸿蒙：保留白金圣甲原设计，把穿戴主板恢复成大块象牙白材，金缘作辅，侧面用少量离散暗阶；不新增圆环/巨大肩冠。','朱砂：保留红与米白符纸的面积关系，纸片白是实体，红料与纸片硬边分区，符墨只占小块；不继续以橙土黄覆盖主要纸白。','织锦：保留深紫主衣与米白交襟，前胸斜襟、后背底衣、袖口三者有材料连续性，不填满细金网线。'],
       'acceptance':['库存获选原稿RGBA/分辨率与SHA保持','正侧背按实际UV看主材连续性，再复核披肩/腰线','图标材质配套不等于实机穿戴通过']}
    ]
    save('application-principles.json',{'state':'RESEARCH_ONLY_NOT_A_PATCH','protected_selected_materials':materials,
          'requirements_sha256':sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md'),
          'principles':principles,'gate_met':False,'production_edits':0,'checklist_deletions':0,
          'limits':'上述为达到1000真实独立相关参考后的处理原则，未覆盖任何贴图、未改人物，不是已完成修图或穿戴验收。'})
    print(json.dumps({'reviewed_icons':144,'viewed_worn_textures':101,'new_groups':34,'combined_groups':57,'application_findings':3,'native_geo':2},ensure_ascii=False))

if __name__=='__main__':main()
