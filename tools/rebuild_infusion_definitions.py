#!/usr/bin/env python3
"""Build explicit original-material mappings from inspected registry identities and loot/recipe sources."""
import json,re,subprocess,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'src/main/resources';BASE='86c3d2a422a4413626d10bc6f1728bca5744e2b6'
old=subprocess.check_output(['git','show',BASE+':src/main/java/com/dynasty/infusion/InfusionTraits.java'],cwd=ROOT).decode()
zh=json.loads((RES/'assets/dynasty/lang/zh_cn.json').read_text());en=json.loads((RES/'assets/dynasty/lang/en_us.json').read_text())
profiles={}
for id,name,desc,kind,family,cost,gate in re.findall(r't\("([a-z_]+)","([^"]+)","([^"]+)",Kind.(\w+),"([^"]+)",(\d),"([^"]*)"\)',old):profiles[id]=[name,desc,kind,family,int(cost),gate]
english={
'shanxiao_claw':('Claw Pursuit','Every third charged melee hit on one target adds 15% damage and slows briefly; 3s cooldown.'),
'ghost_face_fur':('Ghost Escape','Heavy hostile hits grant 2s invisibility; 12s cooldown.'),
'yin_jade_shard':('Soul Suppression','Charged hits slow undead for 2s; 6s cooldown.'),
'nether_tatter':('Spectral Deflection','Magic hits deal 20% less damage and grant 3s slow falling; 8s cooldown.'),
'blackened_bone':('Bone Purification','Undead hits cleanse poison and grant 2s resistance; 10s cooldown.'),
'vengeful_war_soul':('War Soul','Every fourth charged hit on one target adds 20% damage and weakness; 4s cooldown.'),
'heavy_shield_remnant':('Shield Stability','Successful blocks prevent shield durability loss; 6s cooldown.'),
'fine_steel_chain':('Chain Anchor','Halves hostile knockback; 5s cooldown.'),
'swift_boot_scrap':('Swift Recovery','Hostile hits grant 2s speed; 8s cooldown.'),
'dry_peach_branch':('Peach Exorcism','Charged undead hits reveal for 4s and weaken for 2s; 6s cooldown.'),
'bronze_ingot':('Bronze Disruption','Charged hits interrupt non-boss enemies using items; 8s cooldown.'),
'silver_ingot':('Silver Revelation','Charged hits remove invisibility and reveal enemies for 4s; 6s cooldown.'),
'jade':('Jade Recovery','Every third charged hit on one target restores 1 food point; 10s cooldown.'),
'dragon_scale':('Dragon Ward','Heavy hostile hits grant 4 absorption for 3s; 12s cooldown.'),
'dragon_crystal':('Thunder Seal','Every second charged hit on one target adds 12% damage and slows; 8s cooldown.'),
'cinnabar':('Cinnabar Fire','Charged hits ignite for 3s; 6s cooldown.'),
'refined_steel':('Steel Breach','Charged hits on armored enemies add 10% damage and 1s weakness; 5s cooldown.'),
'xuanwu_shell':('Perfect Guard','Blocking in the first 8 ticks grants 3s resistance; 10s cooldown.'),
'qinglong_scale':('Dragon Chase','Charged hits on enemies below half health grant 2s speed and jump; 8s cooldown.'),
'baihu_fang':('Tiger Impact','Charged critical melee hits add 15% damage and knockback; 6s cooldown.'),
'zhuque_feather':('Phoenix Ward','Fire damage extinguishes you and grants 3s fire resistance; 12s cooldown.'),
'taiyi_jade':('Wind Descent','Falls beyond 3 blocks deal half damage; 8s cooldown.'),
'ink_stick':('Talisman Guidance','Equipped: talisman spell hits grant 3s resistance; 10s cooldown.'),
 'talisman_paper':('Talisman Recovery','Equipped: talisman spell hits restore 2 food points; 12s cooldown.')}
new=[
('heavy_stagger','重骨震击','同目标第三次蓄满近战减速并击退、打断普通敌人；冷却6秒。','Heavy Stagger','Every third charged melee hit slows and interrupts non-boss enemies; 6s cooldown.','WEAPON','impact',2),
('venom','妖毒蚀身','同目标第二次蓄满命中使非亡灵中毒3秒；冷却8秒。','Venom','Every second charged hit poisons non-undead enemies for 3s; 8s cooldown.','WEAPON','venom',1),
('backstrike','残刃背袭','从目标背后蓄满近战使其虚弱、减速2秒；冷却6秒。','Backstrike','Charged melee hits from behind weaken and slow for 2s; 6s cooldown.','WEAPON','pursuit',1),
('night_soul','阴夜索魂','夜间或阴司蓄满命中使目标发光、虚弱3秒；冷却8秒。','Night Soul','Charged hits at night or in the Underworld reveal and weaken; 8s cooldown.','WEAPON','yin',1),
('storm_call','雷雨引雷','雷雨中蓄满命中使目标虚弱、减速2秒；冷却8秒。','Storm Call','Charged hits during thunderstorms weaken and slow for 2s; 8s cooldown.','WEAPON','spell',2),
('sunpurge','阳炁净秽','白天蓄满命中亡灵将其点燃2秒并净化自身中毒；冷却8秒。','Sun Purge','Charged daytime undead hits ignite for 2s and cleanse your poison; 8s cooldown.','WEAPON','purify',1),
('hunter_mark','猎手远标','满蓄力箭命中8格外目标使其发光5秒并赋予射手疾行2秒；冷却8秒。','Hunter Mark','Fully charged arrows beyond 8 blocks reveal for 5s and grant 2s speed; 8s cooldown.','WEAPON','pursuit',1),
('air_step','御风踏空','空中蓄满近战获得缓降3秒并击退普通目标；冷却8秒。','Air Step','Charged airborne melee grants 3s slow falling and knocks back non-bosses; 8s cooldown.','WEAPON','escape',1),
('soul_siphon','阴煞蚀魂','夜间或阴司蓄满命中亡灵赋予凋零2秒；冷却10秒。','Soul Erosion','Charged undead hits at night or in the Underworld apply wither; 10s cooldown.','WEAPON','yin',2),
('water_ward','水府护佑','水中受敌人攻击获得水下呼吸和海豚恩惠5秒；冷却10秒。','Water Ward','Hostile hits underwater grant 5s water breathing and dolphins grace; 10s cooldown.','ARMOR','ward',1),
('last_stand','残血护心','生命不高于30%时受敌人攻击减伤25%并获得护盾3秒；冷却12秒。','Last Stand','Hostile hits below 30% health deal 25% less damage and grant absorption; 12s cooldown.','ARMOR','ward',2),
('retaliation','甲壳反震','受敌人重击时击退普通攻击者并使其虚弱1秒；冷却8秒。','Shell Retaliation','Heavy hostile hits knock back non-boss attackers and weaken for 1s; 8s cooldown.','ARMOR','impact',1),
('poison_ward','兽胆解毒','受敌人攻击时净化现有中毒及缓慢；冷却10秒。','Venom Ward','Hostile hits cleanse existing poison and slowness; 10s cooldown.','ARMOR','purify',1),
('lifebloom','树心回春','受敌人重击时获得生命恢复3秒；冷却12秒。','Lifebloom','Heavy hostile hits grant 3s regeneration; 12s cooldown.','ARMOR','resource',2),
('wither_ward','镇煞守魂','受亡灵攻击时净化现有凋零与虚弱；冷却10秒。','Soul Ward','Undead hits cleanse existing wither and weakness; 10s cooldown.','ARMOR','yin',1),
('parry_cleanse','完璧净身','举盾前8刻成功格挡净化中毒、虚弱及缓慢；冷却8秒。','Purifying Parry','Blocking in the first 8 ticks cleanses poison, weakness and slowness; 8s cooldown.','ARMOR','guard',1)]
for id,zn,zd,ename,ed,kind,family,cost in new:profiles[id]=[zn,zd,kind,family,cost,''];english[id]=(ename,ed)
profiles['refined_steel'][1]='蓄满命中有护甲敌人时追加10%伤害并使其虚弱1秒；冷却5秒。'
# Material choices are explicit: registry identity and actual original sources determine each behavior.
groups={
'heavy_stagger':'kaishan_axe_blade wrought_iron_billet strongman_wrist_weight qilin_horn emperor_bone hard_bluestone',
'refined_steel':'refined_wrought_iron iron_spearhead metal_sting_needle',
'last_stand':'broken_heart_mirror broken_tiger_tally',
'night_soul':'ancient_coin_rust black_army_banner_scrap eunuch_token',
'backstrike':'broken_iron_blade paper_cutting_knife fox_tail',
'swift_boot_scrap':'coarse_linen raw_silk silk',
'fine_steel_chain':'damaged_chainmail ancient_bronze_chain_ring',
'poison_ward':'green_beast_gall slippery_jiao_gall',
'hunter_mark':'tough_wood_shaft bronze_gear_part blueprint',
'retaliation':'rusted_lamellar_plate pottery_fragment resonant_scorpion_shell roof_tile',
'shanxiao_claw':'iron_grappling_claw pale_milk_tooth pointed_dead_tooth',
'cinnabar':'poor_gunpowder painted_cinnabar fire_talisman',
'lifebloom':'bloodied_cloth ancient_tree_heart glowing_parasite_mushroom',
'soul_siphon':'congealed_corpse_oil soul_talisman',
'sunpurge':'white_wax_tear phoenix_feather',
'wither_ward':'wronged_shroud pure_yellow_sand',
'air_step':'tough_bamboo_sliver wind_talisman',
'venom':'red_toad_gland poison_gel',
'water_ward':'tough_toad_hide yin_air_sac sea_token young_jiao_scale cold_pool_essence',
'bronze_ingot':'rusted_helmet_spike rebel_head',
'parry_cleanse':'hardened_dead_bark return_talisman warding_inscription_shard',
'storm_call':'sky_token thunder_token thunder_talisman',
'nether_tatter':'brocade',
'ink_stick':'bamboo_slip',
'dragon_scale':'dragon_emperoror_seal',
'xuanwu_shell':'xuantian_jade vajra_talisman',
'jade':'hunyuan_pearl tianming_jade',
'ghost_face_fur':'stealth_talisman'}
groups['dragon_scale']='dragon_emperor_seal'
materials={id:id for id in profiles if id in re.findall(r't\("([a-z_]+)"',old)}
for effect,ids in groups.items():
 for id in ids.split():assert id not in materials,id;materials[id]=effect
# Categories follow inspected material identities, never texture colors.
categories={}
for category,ids in {
'body':'ghost_face_fur tough_toad_hide young_jiao_scale dragon_scale qinglong_scale xuanwu_shell zhuque_feather phoenix_feather resonant_scorpion_shell fox_tail green_beast_gall slippery_jiao_gall red_toad_gland yin_air_sac',
'beast':'shanxiao_claw blackened_bone pale_milk_tooth pointed_dead_tooth qilin_horn emperor_bone rebel_head',
'fiber':'coarse_linen swift_boot_scrap raw_silk silk brocade bloodied_cloth nether_tatter wronged_shroud',
'metal':'bronze_ingot silver_ingot refined_steel refined_wrought_iron wrought_iron_billet broken_iron_blade kaishan_axe_blade iron_spearhead iron_grappling_claw fine_steel_chain ancient_bronze_chain_ring bronze_gear_part metal_sting_needle damaged_chainmail rusted_lamellar_plate heavy_shield_remnant rusted_helmet_spike broken_heart_mirror strongman_wrist_weight paper_cutting_knife',
'soul':'yin_jade_shard vengeful_war_soul ancient_coin_rust congealed_corpse_oil black_army_banner_scrap',
'spirit':'jade dragon_crystal taiyi_jade xuantian_jade hunyuan_pearl tianming_jade cold_pool_essence ancient_tree_heart glowing_parasite_mushroom poison_gel pure_yellow_sand hard_bluestone',
'plant':'dry_peach_branch tough_wood_shaft tough_bamboo_sliver hardened_dead_bark'}.items():
 for id in ids.split():categories[id]=category
paths=list((RES/'data/dynasty/loot_tables').rglob('*.json'))+list((RES/'data/dynasty/recipes').rglob('*.json'))
references={str(p.relative_to(RES/'data/dynasty')):p.read_text() for p in paths}
rows=[]
for id,effect in materials.items():
 assert 'item.dynasty.'+id in zh,id
 zn,zd,kind,family,cost,gate=profiles[effect];key='infusion.dynasty.effect.'+effect
 zh[key]=zn+' I';zh[key+'.description']=zd;en[key]=english[effect][0]+' I';en[key+'.description']=english[effect][1]
 refs=[p for p,text in references.items() if '"dynasty:'+id+'"' in text]
 if not refs:refs=['java:registry-and-codex/'+id]
 rows.append(dict(itemId='dynasty:'+id,chineseName=zh['item.dynasty.'+id],materialCategory=categories.get(id,'ritual'),applicableTypes=[kind],enhancementId='dynasty:'+effect,tier=1,capacityCost=cost,requiredCount=2,conflictGroup=family,nameKey=key,descriptionKey=key+'.description',gate=gate,VFX='minecraft:electric_spark' if effect in ['dragon_crystal','storm_call'] else 'minecraft:enchant',SFX='minecraft:block.amethyst_block.chime',sourceReferences=refs))
assert len(rows)==95,len(rows)
p=RES/'data/dynasty/infusion/materials.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for locale,data in [('zh_cn',zh),('en_us',en)]:
 data={k:v for k,v in data.items() if not k.startswith('tooltip.dynasty.salvage.')}
 (RES/f'assets/dynasty/lang/{locale}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
out=ROOT/'docs/infusion/material-mapping.tsv';out.parent.mkdir(exist_ok=True,parents=True)
with out.open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['itemId','中文名','category','types','enhancementId','强化','tier','capacity','count','conflictGroup','descriptionKey','VFX','SFX','来源'])
 for r in rows:w.writerow([r['itemId'],r['chineseName'],r['materialCategory'],','.join(r['applicableTypes']),r['enhancementId'],zh[r['nameKey']],r['tier'],r['capacityCost'],r['requiredCount'],r['conflictGroup'],r['descriptionKey'],r['VFX'],r['SFX'],';'.join(r['sourceReferences'])])
print(len(rows),'existing materials;',len(profiles),'behaviors')
