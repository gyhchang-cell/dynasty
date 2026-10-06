// Extend registered cod1 content; never replace unrelated localization entries.
import fs from 'node:fs';
import path from 'node:path';
const resource = 'src/main/resources';
const prototypes = [
  ['muxue_feilu','墓穴飞颅','Tomb Flying Skull',[['dynasty:pointed_dead_tooth',1,2],['dynasty:rusted_helmet_spike',0,1],['dynasty:yin_air_sac',0,1]],[]],
  ['zhiren_jianke','纸人剑客','Paper Swordsman',[['dynasty:tough_bamboo_sliver',1,2],['dynasty:paper_cutting_knife',0,1],['dynasty:painted_cinnabar',0,2]],[]],
  ['zuwu_daoshou', '卒伍刀手', 'Rank-and-File Swordsman', [['dynasty:copper_coin',1,3],['dynasty:broken_iron_blade',0,1],['dynasty:coarse_linen',0,2]],[]],
  ['ludun_jiashi', '橹盾甲士', 'Tower-Shield Armiger', [['dynasty:heavy_shield_remnant',0,1],['dynasty:wrought_iron_billet',1,2],['dynasty:damaged_chainmail',0,1]],[]],
  ['fufa_jijiu', '符法祭酒', 'Talisman Ritualist', [['dynasty:cinnabar',0,2],['dynasty:talisman_paper',0,1],['dynasty:dry_peach_branch',1,2]],[]],
  ['shanjing_shanxiao', '山精山魈', 'Shanxiao Mountain Spirit', [['dynasty:shanxiao_claw',1,2],['dynasty:ghost_face_fur',0,1],['dynasty:green_beast_gall',0,1]],[]],
  ['juma_changqiangbing','拒马长枪兵','Hooked Spearman',[['dynasty:iron_spearhead',0,1],['dynasty:tough_wood_shaft',1,2],['dynasty:rusted_lamellar_plate',0,2]],[]],
  ['liannu_zhenzu','连弩阵卒','Repeating Crossbowman',[['minecraft:leather',0,2],['dynasty:short_crossbow_bolt',1,4],['dynasty:bronze_gear_part',0,1]],[]],
  ['tiesuo_chihou','铁索斥候','Chain Scout',[['dynasty:fine_steel_chain',1,2],['dynasty:iron_grappling_claw',0,1],['dynasty:swift_boot_scrap',0,1]],[]],
  ['kuijun_sishi','溃军死士','Powder Deserter',[['dynasty:poor_gunpowder',1,3],['dynasty:pottery_fragment',0,2],['dynasty:bloodied_cloth',0,1]],[]],
  ['zhenwang_zhangqiguan','阵亡掌旗官','Fallen Standard Bearer',[['dynasty:broken_tiger_tally',0,1],['dynasty:black_army_banner_scrap',1,2],['dynasty:vengeful_war_soul',0,1]],[]],
  ['pijia_panjiang_huwei','披甲叛将护卫','Rebel Axeguard',
    [['dynasty:kaishan_axe_blade',0,1],['dynasty:refined_wrought_iron',1,2],['dynasty:broken_heart_mirror',0,1]],[]],
  ['fuhun_baibu_tongzi','缚魂白布童子','Shrouded Lantern Child',[['dynasty:white_wax_tear',1,2],['dynasty:wronged_shroud',0,2],['dynasty:pale_milk_tooth',0,1]],[]],
  ['shibian_lishi','尸变力士','Corpse Strongman',[['dynasty:blackened_bone',1,2],['dynasty:congealed_corpse_oil',0,2],['dynasty:strongman_wrist_weight',0,1]],[]],
  ['yinbing_guizu','阴兵鬼卒','Spectral Halberdier',
    [['dynasty:yin_jade_shard',1,2],['dynasty:nether_tatter',0,1],['dynasty:ancient_coin_rust',0,2]],[]],
];
const write = (file, value) => { fs.mkdirSync(path.dirname(file), {recursive:true}); fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n'); };
const langs = Object.fromEntries(['zh_cn','en_us'].map(locale => [locale, JSON.parse(fs.readFileSync(`${resource}/assets/dynasty/lang/${locale}.json`, 'utf8'))]));
for (const [id, zh, en, drops] of prototypes) {
  langs.zh_cn[`entity.dynasty.${id}`] = zh;
  langs.en_us[`entity.dynasty.${id}`] = en;
  langs.zh_cn[`item.dynasty.${id}_spawn_egg`] = `${zh}刷怪蛋`;
  langs.en_us[`item.dynasty.${id}_spawn_egg`] = `${en} Spawn Egg`;
  write(`${resource}/assets/dynasty/models/item/${id}_spawn_egg.json`, {parent:'minecraft:item/template_spawn_egg'});
  write(`${resource}/data/dynasty/advancements/story_slay_${id}.json`,{criteria:{slay:{trigger:'minecraft:player_killed_entity',conditions:{entity:{type:`dynasty:${id}`}}}}});
  write(`${resource}/data/dynasty/loot_tables/entities/${id}.json`, {type:'minecraft:entity', pools:drops.map(([item,min,max]) => ({
    rolls:1, entries:[{type:'minecraft:item',name:item,functions:[{function:'minecraft:set_count',count:{type:'minecraft:uniform',min,max}}]}],
  }))});
}
langs.zh_cn['entity.dynasty.template_projectile'] = '阴火符／山魈投石';
langs.en_us['entity.dynasty.template_projectile'] = 'Spirit Talisman / Hurled Stone';
langs.zh_cn['effect.dynasty.bingsha_possession'] = '兵煞附体';
langs.en_us['effect.dynasty.bingsha_possession'] = 'Soldier-Spirit Possession';
langs.zh_cn['effect.dynasty.junhun_aura']='军魂不散';langs.en_us['effect.dynasty.junhun_aura']='Unbroken Army Spirit';
langs.zh_cn['entity.dynasty.army_caltrop']='扎马钉';langs.en_us['entity.dynasty.army_caltrop']='Caltrop';
langs.zh_cn['effect.dynasty.spirit_chill']='阴寒蚀骨';langs.en_us['effect.dynasty.spirit_chill']='Spirit Chill';
fs.copyFileSync(`${resource}/assets/dynasty/textures/mob_effect/iron_wall.png`,`${resource}/assets/dynasty/textures/mob_effect/spirit_chill.png`);
langs.zh_cn['entity.dynasty.skull_blood_pool']='腐蚀污血';langs.en_us['entity.dynasty.skull_blood_pool']='Corrosive Skull Blood';
langs.zh_cn['tooltip.dynasty.yin_air_sac']='吞服后获得10秒缓降和水下呼吸，不恢复饱食度。';langs.en_us['tooltip.dynasty.yin_air_sac']='Consume for10 seconds of slow falling and water breathing; restores no hunger.';
langs.zh_cn['entity.dynasty.corpse_miasma']='尸毒黏液';langs.en_us['entity.dynasty.corpse_miasma']='Corpse Miasma';
langs.zh_cn['effect.dynasty.soul_bind']='白布缚魂';langs.en_us['effect.dynasty.soul_bind']='Soul Binding';
langs.zh_cn['effect.dynasty.lantern_glare']='惨白灯晕';langs.en_us['effect.dynasty.lantern_glare']='Lantern Glare';
for(const effect of ['soul_bind','lantern_glare'])fs.copyFileSync(`${resource}/assets/dynasty/textures/mob_effect/iron_wall.png`,`${resource}/assets/dynasty/textures/mob_effect/${effect}.png`);
const components=[
 ['kaishan_axe_blade','开山斧刃','Broad Axe Blade','minecraft:block/iron_block',[[3,5,7,12,12,9],[1,4,7,4,13,9],[10,7,6,14,10,10]]],
 ['refined_wrought_iron','精炼熟铁锭','Refined Wrought Iron','minecraft:block/iron_block',[[3,4,5,13,8,11],[4,8,6,12,10,10]]],
 ['broken_heart_mirror','破损护心镜','Broken Heart Mirror','dynasty:block/bronze_block',[[4,5,7,11,12,9],[2,7,7,4,11,9],[5,12,7,10,14,9],[6,3,7,11,5,9]]],
 ['yin_jade_shard','聚阴寒玉屑','Yin Jade Shard','minecraft:block/prismarine',[[3,4,7,6,9,10],[8,6,6,11,12,9],[6,3,6,8,6,8]]],
 ['nether_tatter','幽冥残缕','Nether Tatter','minecraft:block/cyan_wool',[[3,9,7,11,12,8],[4,5,7,7,10,8],[8,3,7,10,10,8],[11,8,7,13,11,8]]],
 ['ancient_coin_rust','古币锈块','Ancient Coin Rust','minecraft:block/oxidized_copper',[[3,5,7,7,9,9],[8,8,6,12,12,8],[7,3,7,12,6,9]]],
];
const shapes={blade:[[6,2,7,9,12,9],[4,10,7,7,14,9]],cloth:[[3,5,7,12,12,8],[4,2,7,6,6,8],[9,3,7,11,6,8]],plate:[[3,4,7,12,12,9],[5,12,7,10,14,9]],
 ingot:[[3,5,5,13,9,11]],branch:[[7,2,7,9,13,9],[4,9,7,7,11,9]],claw:[[6,3,7,9,7,9],[4,6,7,7,11,9],[4,10,7,6,14,9]],
 gall:[[4,5,6,11,11,10],[6,11,7,9,14,9]],bolt:[[7,2,7,8,13,8],[6,11,6,9,14,9],[5,3,7,10,5,8]],
 gear:[[3,6,7,6,10,9],[10,6,7,13,10,9],[6,3,7,10,6,9],[6,10,7,10,13,9]],chain:[[4,3,7,6,9,9],[8,3,7,10,9,9],[6,3,7,8,5,9],[6,7,7,8,9,9],[8,8,7,10,14,9],[12,8,7,14,14,9],[10,8,7,12,10,9],[10,12,7,12,14,9]],
 dust:[[3,3,6,6,6,9],[8,3,7,12,6,10],[6,6,7,9,9,10]],tally:[[3,6,6,12,10,10],[3,10,6,6,12,10],[10,3,7,12,6,9]],soul:[[5,4,6,11,11,10],[7,11,7,10,14,9],[6,2,7,8,4,9]]};
for(const [id,zh,en,shape,texture]of [
 ['pointed_dead_tooth','尖锐死人牙','Pointed Dead Tooth','claw','bone_block_side'],['rusted_helmet_spike','生锈盔顶刺','Rusted Helmet Spike','blade','exposed_copper'],['yin_air_sac','阴气囊','Yin Air Sac','gall','gray_terracotta'],
 ['tough_bamboo_sliver','极轻的韧竹篾','Tough Bamboo Sliver','branch','bamboo_block'],['paper_cutting_knife','裁纸小刀','Paper Cutting Knife','blade','iron_block'],['painted_cinnabar','点朱丹砂','Painted Cinnabar','dust','red_terracotta'],
 ['white_wax_tear','白蜡灯泪','White Wax Tear','gall','white_terracotta'],['wronged_shroud','冤魂碎布片','Wronged Soul Shroud','cloth','white_wool'],['pale_milk_tooth','惨白乳齿','Pale Milk Tooth','claw','bone_block_side'],
 ['blackened_bone','发黑的腐骨','Blackened Rotten Bone','branch','black_terracotta'],['congealed_corpse_oil','凝固尸油','Congealed Corpse Oil','gall','purple_terracotta'],['strongman_wrist_weight','力士铅腕套','Strongman Wrist Weight','gear','deepslate'],
 ['broken_iron_blade','残破的生铁刀片','Broken Iron Blade','blade','iron_block'],['coarse_linen','粗麻碎布','Coarse Linen Scrap','cloth','brown_wool'],
 ['heavy_shield_remnant','沉重盾面残件','Heavy Shield Remnant','plate','spruce_planks'],['wrought_iron_billet','熟铁铸块','Wrought Iron Billet','ingot','iron_block'],
 ['damaged_chainmail','损毁的重锁子甲','Damaged Heavy Chainmail','chain','iron_block'],['dry_peach_branch','干枯桃木枝','Dry Peachwood Branch','branch','stripped_oak_log'],
 ['shanxiao_claw','坚硬山魈爪','Hardened Shanxiao Claw','claw','bone_block_side'],['ghost_face_fur','鬼面皮毛','Ghost-Face Fur','cloth','gray_wool'],
 ['green_beast_gall','青绿兽胆','Green Beast Gall','gall','green_terracotta'],['iron_spearhead','铁枪头','Iron Spearhead','blade','iron_block'],
 ['tough_wood_shaft','坚韧木杆','Tough Wooden Shaft','branch','dark_oak_planks'],['rusted_lamellar_plate','生锈扎甲片','Rusted Lamellar Plate','plate','exposed_copper'],
 ['short_crossbow_bolt','短弩箭','Short Crossbow Bolt','bolt','iron_block'],['bronze_gear_part','青铜齿轮机件','Bronze Gear Part','gear','copper_block'],
 ['fine_steel_chain','精钢细链条','Fine Steel Chain','chain','iron_block'],['iron_grappling_claw','透骨生铁爪','Iron Grappling Claw','claw','iron_block'],
 ['swift_boot_scrap','迅捷皮靴残料','Swift Boot Scrap','cloth','black_wool'],['poor_gunpowder','劣质火药粉','Poor Gunpowder','dust','coal_block'],
 ['pottery_fragment','碎陶瓦片','Pottery Fragment','plate','terracotta'],['bloodied_cloth','染血白布条','Bloodied Cloth Strip','cloth','red_wool'],
 ['broken_tiger_tally','残破虎符碎片','Broken Tiger Tally','tally','copper_block'],['black_army_banner_scrap','玄黑军旗残片','Black Army Banner Scrap','cloth','black_wool'],
 ['vengeful_war_soul','怨魂战魂','Vengeful War Soul','soul','cyan_glazed_terracotta']])components.push([id,zh,en,`minecraft:block/${texture}`,shapes[shape]]);
for(const [id,zh,en,texture,boxes]of components){
 langs.zh_cn[`item.dynasty.${id}`]=zh;langs.en_us[`item.dynasty.${id}`]=en;
 write(`${resource}/assets/dynasty/models/item/${id}.json`,{parent:'minecraft:block/block',textures:{all:texture,particle:texture},
  display:{gui:{rotation:[20,-30,0],scale:[.9,.9,.9]},ground:{translation:[0,3,0],scale:[.4,.4,.4]},fixed:{scale:[.65,.65,.65]}},
  elements:boxes.map(b=>({from:b.slice(0,3),to:b.slice(3),faces:Object.fromEntries(['north','south','east','west','up','down'].map(f=>[f,{texture:'#all'}]))}))});
}
for(const [key,zh,en]of [
 ['iron_axe','铁砧修复铁斧：每件恢复25%耐久，消耗材料和经验。','Anvil: repairs 25% iron axe durability per component; costs materials and levels.'],
 ['iron_gear','铁砧修复铁制工具或铁甲：每锭恢复25%耐久。','Anvil: repairs 25% iron tool or iron armour durability per ingot.'],
 ['iron_armor','铁砧修复铁甲：每件恢复25%耐久，保留名称与附魔。','Anvil: repairs 25% iron armour durability, preserving names and enchantments.'],
 ['jade_gear','铁砧修复原本使用玉石修复的装备：每片恢复25%耐久。','Anvil: repairs 25% durability on equipment whose original repair material is jade.'],
 ['leather_armor','铁砧修补皮甲：每缕恢复25%耐久，保留染色与附魔。','Anvil: repairs 25% leather armour durability, preserving dye and enchantments.']]){
 langs.zh_cn[`tooltip.dynasty.salvage.${key}`]=zh;langs.en_us[`tooltip.dynasty.salvage.${key}`]=en;
}
for(const [key,zh,en]of [['shears','剪刀','shears'],['iron_sword','铁剑','iron swords'],['leather_boots','皮靴','leather boots'],['shield','普通盾牌','ordinary shields'],['chainmail','锁链甲','chainmail armour'],['bows','普通弓或弩','ordinary bows or crossbows'],['crossbow','普通弩','ordinary crossbows']]){
 langs.zh_cn[`tooltip.dynasty.salvage.${key}`]=`铁砧修复${zh}：每件恢复25%耐久，消耗材料与经验。`;
 langs.en_us[`tooltip.dynasty.salvage.${key}`]=`Anvil: repairs 25% durability on ${en} per component; costs materials and levels.`;
}
langs.zh_cn['tooltip.dynasty.green_beast_gall']='食用后解除中毒，不恢复饱食度。';langs.en_us['tooltip.dynasty.green_beast_gall']='Consume to cure poison; does not restore hunger.';
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/rebel_guard_sites.json`,{replace:false,values:['dynasty:great_wall_gate']});
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/ghost_sites.json`,{replace:false,values:['dynasty:ruined_battlefield']});
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/corpse_sites.json`,{replace:false,values:['dynasty:imperial_tomb']});
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/shroud_child_sites.json`,{replace:false,values:['dynasty:imperial_tomb']});
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/paper_swordsman_sites.json`,{replace:false,values:['dynasty:imperial_tomb']});
write(`${resource}/data/dynasty/tags/worldgen/structure/blueprint/flying_skull_sites.json`,{replace:false,values:['dynasty:imperial_tomb']});
const arrowsFile=`${resource}/data/minecraft/tags/items/arrows.json`;
const arrows=fs.existsSync(arrowsFile)?JSON.parse(fs.readFileSync(arrowsFile,'utf8')):{replace:false,values:[]};
if(!arrows.values.includes('dynasty:short_crossbow_bolt'))arrows.values.push('dynasty:short_crossbow_bolt');write(arrowsFile,arrows);
for(const [id,ingredient,count,result,extra]of [
 ['recover_dead_tooth','pointed_dead_tooth',2,'minecraft:bone_meal'],
 ['recover_painted_cinnabar','painted_cinnabar',2,'dynasty:cinnabar'],
 ['recover_wax_candle','white_wax_tear',2,'minecraft:candle','minecraft:string'],['recover_milk_tooth','pale_milk_tooth',2,'minecraft:bone_meal'],
 ['recover_rotten_bone','blackened_bone',2,'minecraft:bone_meal'],
 ['recover_ancient_coin','ancient_coin_rust',4,'dynasty:copper_coin'],['recover_gunpowder','poor_gunpowder',4,'minecraft:gunpowder'],
 ['recover_pottery','pottery_fragment',4,'minecraft:brick'],['recover_tiger_tally','broken_tiger_tally',4,'dynasty:tiger_crest'],
 ['recover_army_banner','black_army_banner_scrap',6,'minecraft:black_banner','minecraft:stick'],['bottle_war_soul','vengeful_war_soul',1,'minecraft:experience_bottle','minecraft:glass_bottle']]){
 const ingredients=Array.from({length:count},()=>({item:`dynasty:${ingredient}`}));if(extra)ingredients.push({item:extra});
 write(`${resource}/data/dynasty/recipes/${id}.json`,{type:'minecraft:crafting_shapeless',ingredients,result:{item:result}});
 write(`${resource}/data/dynasty/advancements/recipes/${id}.json`,{criteria:{has_material:{trigger:'minecraft:inventory_changed',conditions:{items:[{items:[`dynasty:${ingredient}`]}]}}},rewards:{recipes:[`dynasty:${id}`]}});
}
for (const [locale, entries] of Object.entries(langs)) write(`${resource}/assets/dynasty/lang/${locale}.json`, entries);
write('docs/blueprint-cod1/template-loot-status.json', {
  policy:'Unique drops remain pending until registered and connected to gameplay use. Loot implementation is not entity DONE: current singleplayer and multiplayer acceptance is still required.',
  templates:prototypes.map(([id, zh, , drops, pending]) => ({id:`dynasty:${id}`,name:zh,
    implemented:drops.map(([id,min,max])=>({id,min,max})),pending,
    status:pending.length ? 'PARTIAL_PENDING_ITEM_USE_MAPPING' : 'IMPLEMENTED_PENDING_CLIENT_VALIDATION'})),
});
console.log(`Generated ${prototypes.length} loot tables/egg models, merged zh_cn/en_us, and explicit pending-drop mapping.`);
