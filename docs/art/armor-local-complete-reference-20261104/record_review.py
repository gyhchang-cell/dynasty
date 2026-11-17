"""Visual observations recorded after six icon pages and sixteen full atlas pages were opened."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=[]
def row(group,cases,observation,new=False):
 x={'semantic_group':group,'cases':cases,'observation':observation,'credit':'NEW_CONSERVATIVE_LEARNING_GROUP' if new else 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'}
 if not new: x['prior_group']=group
 rows.append(x)
def terra(names): return ['terra_equipment:'+n for n in names.split()]
row('complete_astrumm_plate_pink_inset',['ulterlands:astrumm_set'],'灰紫短盔两侧粉红嵌片、两根直面护颊，短胸用浅灰方肩与中央紫格，裤胫粉带和尖顶短靴贯穿颜色。只学灰板承力面与粉色小嵌片位置；头面留大暗口，粉色不涂满全身。80×80原生astrumm_full图按独立布局阅读，不把它套标准64×32UV。',True)
row('souls_black_knight_dark_silhouette',['born_in_chaos_v1:dark_metal_armor'],'暗铁头盔有竖向双耳/角、浅灰横面板，胸的银色弧带夹黑腹，靴仍分为两脚。保守追加黑骑士剪影组，角高是MC比例边界。两张darkmetar候选是细密灰棋盘，不由文件名当作图标对应的实际穿戴面；后续应查自定义渲染链。')
row('mixed_nether_star_pale_plate',['fantasy_ending:fantasy_ending'],'青白主面、粉紫侧边、头顶高刺与高靴侧刺四件呼应，追加既有浅色星甲族。过亮主面和满边粉刺是过曝/装饰超主体反例；原生层颜色对应但只证候选，不能说实机成立。')
row('vanilla_outline_elemental_palette',['fantasy_ending:star_particle']+terra('bee pumpkin')+['terramity:'+n for n in ['topaz_armor','iridium_armor','onyx_armor','sapphire_armor','ruby_armor']],'八名称按基础盔口、V胸、直裤与成对短靴共同组织保守追加已有模板材料组，不作八个新设计。star_particle深蓝外框青绿心、蜂甲黄棕大带、南瓜橙主面绿靴底分别可辨；terramity五矿物甲主面边缘明暗几乎相同，红/蓝/粉/金换色不独立。南瓜圆顶和蜂甲细胸不作为MC硬轮廓模板，高亮不要填满胸主面。')
row('splendour_textured_metal_family',['splendour_ablaze_epoch:mold_tin_armor'],'黑灰甲用少量白灰头额、胸中斜板和靴口反光，裤腿保持直而短。追加既有棠煌材质族。原生层有明显银灰板区，图标和候选分别记录，不把图层2短腿条当整套新设计。')
row('unrealium_dark_purple_insets',['born_in_chaos_v1:nightmare_mantleofthe_night']+terra('obsidian'),'夜之披风四件补全已读nightmareboots所属暗底嵌片组：面罩下缘白骨/牙、深蓝竖襟与浅肩片，和单靴不重复给一套信用。obsidian的黑紫竖面盔/胸与暗连接同族，仅是另一材料表达。夜袍实体候选128×128与独立64×32裤层不能混切，深黑细纹在小图易糊，保留明暗大面。')
row('bossloot_kobeko_shared_armor_family',['monsterexpansion:skrythe','monsterexpansion:rakoth'],'两套角盔、V胸叠片、直腿和长L靴追加已有怪物掉落共用甲族。skrythe黑紫双细角与亮紫胸节点，rakoth棕金短角和浅肩骨片；只借鉴素材身份与关节暗隙，不把颜色/某一角形拆信用。skrythe的全图、四分件原生图集一同读，32×32裤/靴和128×128全图是同套布局变体，不是五套。')
row('malum_purple_cosmetic_plate_family',['malum:soul_stained_steel'],'紫色短盔侧颊、亮粉紫胸上部与肩边、暗紫腰腿和浅靴面追加Malum已有灵钢族。源128×128重铸层与图标亮紫区有共同材料组织，但未证其渲染选中关系；不把本体、古代饰面、发光层重复算设计。')
row('gem_plate_metal_variants',terra('copper pearl ebony ash tin plank lead shadow_plank'),'八名称共享短V胸、直裤和分靴，保守与已读铂/银/钨材料族合并：铜橙板、珍珠米色斜面、乌木与灰烬暗紫灰、锡暗金灰、木板棕横面、铅深蓝灰、影木浅灰框。乌木/灰烬与影木多数原生层的布局重复；材质差应靠主面色和少量结构线，不能全身棋盘纹。珍珠盔小凸顶与木板方盔均不单独加信用。')
row('gemmed_sharp_plate_variants',terra('orichalcum cobalt titanium mythril golden'),'五名称在尖/角盔和V胸模板内变体，追加既有尖板甲族。山铜紫粉粗亮边、钴深蓝青亮板、钛浅蓝紫交叉条、秘银青竖面甲、金甲黄中线与小红扣；胸留深侧、肩不无限向外挑。钛原生层大量横条不能以条/UV岛计设计，亮色和复杂UV布局也不自动代表高级MC质感。')
row('bone_reptile_rib_vest',terra('necro'),'黑棕底配米白眉/脸骨、肋状V胸和肩骨，腿上缘米条、黑靴浅口，追加骨肋组。小骨区能说明用途，但不能把整胸画成人体骨架插画。原生128×128层多骨片仍是一个候选。')
row('mixed_copper_classical_helm',terra('gladiator'),'红棕短缨、金面甲配红侧护颊，金胸横板与红底、金护胫同套，追加古典金属盔族。缨只在盔顶侧后少量，保留鼻/面甲空隙；不直接拷贝原作者头盔徽形。')
row('wood_green_armor_family',terra('spore_root cactus'),'树根棕框、青绿两枝角与绿靴口，仙人掌暗绿大面配少量浅点，追加木绿材料甲族。树根长角/靴尖是装饰上限，仙人掌大面不用满贴浅点噪声。原生根甲层很多枝条与仙人掌层多孤点，只借材料主次，不照搬密点。')
row('ninja_cloth_cowl',terra('ninja'),'黑兜帽中浅灰倒V绑布、深胸少量肩口和腕/靴口浅边，追加已有忍者布甲组。布领连接左右、腰腿留暗大块；白边不是全金属框，不能因是甲物品就画成亮钢板。')
row('void_purple_inset_plate',['terramity:cosmilite_armor'],'紫主面配窄金边，头盔大暗口和金色下沿，胸的两直肩片向上，腿腰小金带、靴口金边。追加既有紫色嵌片甲族，注意过饱和紫与密亮边会偏离材料感；128×128候选上下大面不是标准UV矩形。')
row('vanilla_outline_elemental_palette',['terramity:dimlite'],'青黑主面头盔被两道浅色横带夹住，胸浅色倒V三角/肩小片和靴胫短横条保留普通轮廓；保守模板变体，不因青色材料新命名增加设计。两张候选标准比例层可观察领/腕端，但尚未证实际选中。')
row('complete_conjuror_dark_gold_chain',['terramity:conjuror'],'灰黑圆口兜罩下垂一颗方金扣，胸用同材质大暗面和金色U形短链，裤仍深灰而鞋为红白短鞋。材料身份来自少量链与鞋区，黑胸不可完全糊成一团；头圆环感和不一致鞋色是限制例，不用来重设计已认可的神圣甲。64×64实体候选把链、扣与红鞋独立分区，只是候选而非实穿证明。',True)
row('complete_crowned_white_fur_purple_cloth',['terramity:evil_king_armor'],'紫色低顶帽/冠配宽白毛沿，胸上白毛领接紫短衣、棕红腰带，紫腿和棕靴。横向毛领在头胸重复，使织物和毛皮易辨；头冠/胸领过宽，作为MC紧凑比例反例。只学材料区顺序，不直接使用宽毛沿与原作者冠形。64×64原生候选有紫布、白领和棕条，但没证明绑定。',True)
row('mixed_maid_clothing_apron',['lethality:hf_battle_maid'],'洋红头巾配白花边、胸的白围裙V口、白/红裙片和红鞋白口，追加已读battle_maid同衣型变体，不能只因配色和前缀再算设计。64×64合层和64×32分层都读过，一套三图，不是三套。')
row('molten_plate_dark_shell',['mythsandlegends:infernum_warplate'],'深红紫底、红上额/尖角与V胸红边，裤暗红直面和靴口窄亮面，追加已有熔融暗壳族。头胸角不要比主体还高，红黑低对比是限制；原生身体层和arm分图只描述一套的布局，不拆信用。')
prior=json.loads((D.parents[2]/'docs/art/armor-unindexed-reference-20261104/combined-semantic-ledger.json').read_text())
keys={c['case_key'] for c in json.loads((D/'provenance.json').read_text())['cases']}
flat=[c for r in rows for c in r['cases']]; assert len(flat)==len(set(flat))==41 and set(flat)==keys
assert len([r for r in rows if r['credit'].startswith('NEW_')])==3
# Multiple observations may append to the same semantic group (dimlite); they do not create groups.
out={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':[f'icons-{i:02}.png' for i in range(1,7)]+[f'worn-{i:02}.png' for i in range(1,17)],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':41,'native_icon_entries_viewed':164,'item_model_declarations_read':164,'native_layer_candidate_entries_viewed':61,'animation_metadata_present':0,'new_conservative_learning_groups':3,'append_observations':17,'limits':'41个四部件齐全名称不等于41个独立设计；61原生候选无玩家绑定证明。203学习组含局部/变体/反例，已验完整独立设计总数未知。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
assert len(rows)==20
(D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print('41 cases / 164 icon entries / 61 atlas candidates / 3 new conservative learning groups / 17 append observations')
if __name__=='__main__': pass
