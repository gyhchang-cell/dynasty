// Merge only the four prototype translations; never replace unrelated localization entries.
import fs from 'node:fs';
import path from 'node:path';
const resource = 'src/main/resources';
const prototypes = [
  ['zuwu_daoshou', '卒伍刀手', 'Rank-and-File Swordsman', [['dynasty:copper_coin', 1, 3]], ['残破的生铁刀片', '粗麻碎布']],
  ['ludun_jiashi', '橹盾甲士', 'Tower-Shield Armiger', [], ['沉重盾面残件', '熟铁铸块', '损毁的重锁子甲']],
  ['fufa_jijiu', '符法祭酒', 'Talisman Ritualist', [['dynasty:cinnabar', 0, 2], ['dynasty:talisman_paper', 0, 1]], ['干枯桃木枝']],
  ['shanjing_shanxiao', '山精山魈', 'Shanxiao Mountain Spirit', [], ['坚硬山魈爪', '鬼面皮毛', '青绿兽胆']],
  ['juma_changqiangbing','拒马长枪兵','Hooked Spearman',[],['铁枪头','坚韧木杆','生锈扎甲片']],
  ['liannu_zhenzu','连弩阵卒','Repeating Crossbowman',[['minecraft:leather',0,2]],['短弩箭','青铜齿轮机件']],
  ['tiesuo_chihou','铁索斥候','Chain Scout',[],['精钢细链条','透骨生铁爪','迅捷皮靴残料']],
  ['kuijun_sishi','溃军死士','Powder Deserter',[],['劣质火药粉','碎陶瓦片','染血白布条']],
  ['zhenwang_zhangqiguan','阵亡掌旗官','Fallen Standard Bearer',[],['残破虎符碎片','玄黑军旗残片','怨魂战魂']],
];
const write = (file, value) => { fs.mkdirSync(path.dirname(file), {recursive:true}); fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n'); };
const langs = Object.fromEntries(['zh_cn','en_us'].map(locale => [locale, JSON.parse(fs.readFileSync(`${resource}/assets/dynasty/lang/${locale}.json`, 'utf8'))]));
for (const [id, zh, en, drops] of prototypes) {
  langs.zh_cn[`entity.dynasty.${id}`] = zh;
  langs.en_us[`entity.dynasty.${id}`] = en;
  langs.zh_cn[`item.dynasty.${id}_spawn_egg`] = `${zh}刷怪蛋`;
  langs.en_us[`item.dynasty.${id}_spawn_egg`] = `${en} Spawn Egg`;
  write(`${resource}/assets/dynasty/models/item/${id}_spawn_egg.json`, {parent:'minecraft:item/template_spawn_egg'});
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
for (const [locale, entries] of Object.entries(langs)) write(`${resource}/assets/dynasty/lang/${locale}.json`, entries);
write('docs/blueprint-cod1/template-loot-status.json', {
  policy:'cod1 supplement: unique decorative drops without a registered item and real use remain PENDING; no substitute items or invented recipes.',
  templates:prototypes.map(([id, zh, , drops, pending]) => ({id:`dynasty:${id}`,name:zh,
    implemented:drops.map(([id,min,max])=>({id,min,max})),pending,
    status:pending.length ? 'PARTIAL_PENDING_ITEM_USE_MAPPING' : 'DONE'})),
});
console.log(`Generated ${prototypes.length} loot tables/egg models, merged zh_cn/en_us, and explicit pending-drop mapping.`);
