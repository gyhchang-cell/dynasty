"""D23 after actual viewing of two native-icon and five normal/slim source-atlas pages."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent;rows=[]
def row(group,cases,obs,new=False):
    x={'semantic_group':group,'cases':['armoroftheages:'+c for c in cases],'observation':obs,'credit':'NEW_CONSERVATIVE_LEARNING_GROUP' if new else 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'}
    if not new:x['prior_group']=group
    rows.append(x)
row('complete_banded_headdress_apron_armor',['anubis_armor','pharaoh_armor'],'两套共享蓝金横条头巾与金腰白裙、深腿靴轮廓，阿努比斯改暗兽面双耳、厚金胸腹板、靴口金白横带；法老改浅金白胸布、蓝金头巾围空脸和脚踝金扣。合为1个保守头巾/围裙甲学习组，不以神名和兽面算两整套。16像素图标用连续三四格横条和大胸面建立身份，小脚深边保留分离。原生常规/细臂各一图，128×64或64×64，袖/肩/饰件不同岛不能按普通玩家甲裁。只借头巾与领胸腰裙材料连续和边界清楚，不将兽耳、埃及纹样复制给Dynasty。',True)
row('complete_crested_centurion_sash_tunic',['centurion_armor'],'红顶羽橙金包颊盔、红棕短甲身配斜金绶带与亮肩、金短腿甲和红棕绑带靴。新增1个保守百夫长绶带短衣组，区别整片钢胸和长袍：胸只有一个斜带焦点，短裙两腿清楚、鞋绑带由大横段读出。两张128×64常规/细臂原图有金肩大片与红棕织纹/细岛，细臂版本只是同套适配，零额外设计。可学斜带到腰、护腿到靴的材质衔接，避免全身均匀金亮线；西式题材不直接搬成中国盔甲。',True)
row('divine_ornate_gold',['exalted_aurum_armor','raijin_armor'],'尊金甲为米金竖冠、金肩与胸腹竖板、左右外翻裙片和金长靴，少量暗红布作重心；雷神为短金角、红金环绕颈框、深棕宽裤红垂带和黑底金踝环。两名只追加已有华金组：前者可学米金正面与深褐侧面的大色块、裙片留缝；后者只是冠/颈框与松裤装束，不能把稀疏几件饰物按四槽名称当普通完整胸甲信用。原图常规/细臂存在不同岛和小装饰，零新增整套，不照抄角冠、环鼓或古代纹样。')
row('immersive_divine_sparse_trim_reference',['holy_armor'],'圣甲在灰白闭面盔上集中一道金十字面甲与两短侧翼，短胸白金V护片、深腰两侧灰块，腰腿保留黑链甲间隙，靴白脚背配小金口。追加既有稀金神圣甲族。16像素内靠灰暗面分隔白板、亮金只落额鼻胸腰，整体仍读作MC甲，适合学习神圣感靠焦点而非再加大肩。128×128原图另有细链、翼/饰物岛，不假定全用在玩家上；只学金边面积控制，不动已认可成稿，也不复制十字/翅翼像素。')
row('magistu_closed_helmet_family',['iron_plate_armor'],'铁板甲是黑灰闭面横目盔配红短羽、灰白短胸和两方肩、分片护裙及两只黑灰靴。追加既有闭面板甲族，不因加羽新增独立设计。图标胸板用一大浅灰面和一道暗缝，肩由两格亮边框住深中面，裤腰暗带把裙片和靴分开；比满面亮点更适合MC读图。两张128×64原图金属有较密斑点和附属条岛，只借主板/接缝，不将满图斑点复制为材质。')
row('samurai_plate_variants_conservative',['japanese_light_armor','o_yoroi_armor'],'日本轻甲是绑额侧结、棕黑四横片胸、棕短裤与深灰护腿；大铠改金角红盔、黑肩红横片胸、红裙与棕腿红膝。两者追加既有武士片甲组，不凭轻重名和红棕换材加整套信用。轻甲64×32与大铠64×64原图均常规/细臂成对，且即便64×32也不能未经模型核对当标准玩家UV。可学粗横片分层、黑底红片留缝、膝片和腰条呼应，限制是饱和红过亮且肩条偏细，不照搬冠和绑结。')
row('complete_skull_feather_harness_armor',['quetzalcoatl_armor'],'羽蛇甲头为浅骷髅面配绿羽外圈与小金尖，胸中央黑空口内金黄焦点、左右绿红肩羽，下方细白骨围腰红带，棕靴配浅灰胫片。新增1个保守骷髅羽冠/骨羽肩带学习组，但稀疏胸带不是普通封闭胸甲的成稿样板，仍非有效完整独立总数验收。四图16像素有限色块使羽/骨/皮靴可区分，两个128×64原图绿羽和红色绳/片很多附属岛；只学骨白、羽绿、皮褐的材料对比，避免大羽冠抢走盔甲本体和每像素零碎挂件。',True)
keys={a['case_key'] for a in json.loads((D/'provenance.json').read_text())['cases']};flat=[k for r in rows for k in r['cases']];assert len(flat)==len(set(flat))==10 and set(flat)==keys and len(rows)==7
x={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':[f'icons-{i:02}.png' for i in range(1,3)]+[f'worn-{i:02}.png' for i in range(1,6)],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':10,'native_icon_entries_viewed':40,'item_model_declarations_read':40,'native_layer_candidate_entries_viewed':20,'static_context_classes':5,'animation_metadata_present':0,'new_conservative_learning_groups':3,'append_observations':4,'limits':'常规/细臂20图不算20独立设计。10名中稀疏仪式胸带、既有盔型和材料变体仅用于学习；3新保守组也不是新增3套已验适用独立设计。图集未证明最终四槽选中链与实际玩家效果。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
(D/'semantic-review.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('10 names / 40 native icons / 20 normal-slim atlases / 3 learning groups / 4 append observations')
