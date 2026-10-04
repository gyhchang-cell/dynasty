// Native Minecraft JSON models: original geometry, vanilla pixel material palette; no bitmap resampling.
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const resources=path.join(root,'src/main/resources/assets/dynasty');
const ids=['mingyuan_soul_lantern','longmai_prism','chengque_mending_seal','zhengwu_oath_tally','zhouguang_star_leaf','chixiao_ember'];
const names=['冥垣镇魂灯','龙脉棱心','承阙修兵印','征武誓契','宙光星简','赤霄焰种'];
const english=['Mingyuan Soul Lantern','Leyline Prism Heart','Chengque Mending Seal','Zhengwu Oath Tally','Zhouguang Star Leaf','Chixiao Ember Seed'];
const tips=['右键显露附近亡灵，持续10秒；24次。','右键引龙脉之光：夜视60秒、急迫30秒；24次。','另一只手持受损装备，右键修复20%耐久；24次。','右键守誓：自身及8格内同队玩家获得10秒抗性；冷却30秒，24次。','在四象核心附近右键，读取已经归位的贡品数量；24次。','右键点燃护身焰：防火60秒；24次。'];
const enTips=['Reveal nearby undead for 10s. 24 charges.','Night vision for 60s and haste for 30s. 24 charges.','Repair damaged equipment in the other hand by 20%. 24 charges.','Resistance for you and nearby teammates for 10s. 30s cooldown. 24 charges.','Read the completed offerings near a Four Symbols heart. 24 charges.','Fire resistance for 60s. 24 charges.'];
for(let i=0;i<ids.length;i++){
 const elements=[];
 const box=(from,to,texture='frame',rotation)=>{const e={from,to,faces:Object.fromEntries(['north','south','east','west','up','down'].map(f=>[f,{texture:'#'+texture}]))};if(rotation)e.rotation=rotation;elements.push(e);};
 const core=['prismarine','amethyst_block','emerald_block','red_terracotta','lapis_block','magma'][i];
 if(i===0){ // Pagoda lantern cage around a suspended jade heart.
  box([3,2,4],[13,4,12]);box([4,12,4],[12,14,12]);box([6,14,6],[10,15,10]);
  for(const x of [3,11])for(const z of [4,10])box([x,4,z],[x+2,12,z],'dark');
  box([6,5,6],[10,11,10],'core');box([7,0,7],[9,2,9],'dark');
 }else if(i===1){ // Stepped crystal held in a narrow bronze cradle.
  for(let y=2;y<14;y+=2){const w=y<8?2+(y-2)/2:2+(14-y)/2;box([8-w,y,6],[8+w,y+2,10],'core');}
  box([3,1,4],[13,3,12]);for(const x of [3,11])box([x,3,5],[x+2,7,11]);
 }else if(i===2){ // Square jade seal, bridge-shaped handle.
  box([3,2,3],[13,6,13]);box([4,6,4],[12,9,12],'core');
  box([5,9,6],[7,13,10],'dark');box([9,9,6],[11,13,10],'dark');box([5,12,6],[11,14,10]);
 }else if(i===3){ // Paired split tally, asymmetrical tooth interlock.
  box([3,3,6],[7,13,10],'dark');box([9,3,6],[13,13,10],'core');
  for(let y=4;y<12;y+=3)box([7,y,6],[9,y+1,10]);
  box([3,13,6],[6,15,10]);box([10,13,6],[13,15,10]);box([4,1,7],[6,3,9],'core');
 }else if(i===4){ // Three bound carved tablets, not a recolored gem.
  for(let x=3;x<=11;x+=4)box([x,2,7],[x+3,14,9],'core');
  box([2,4,6],[15,5,10]);box([2,11,6],[15,12,10]);
  for(let y=6;y<11;y+=2)box([7,y,6],[10,y+1,7],'light');
 }else { // Bronze vessel with rising stepped ember.
  box([4,2,4],[12,4,12]);box([3,4,3],[13,6,13],'dark');
  box([5,6,5],[11,9,11],'core');box([6,9,6],[10,12,10],'core');box([8,12,7],[10,15,9],'light');
  for(const x of [2,12])box([x,5,5],[x+2,10,11]);
 }
 const model={parent:'minecraft:block/block',textures:{frame:'minecraft:block/gold_block',dark:'minecraft:block/polished_deepslate',core:'minecraft:block/'+core,light:'minecraft:block/sea_lantern',particle:'minecraft:block/'+core},elements,
 display:{gui:{rotation:[25,225,0],translation:[0,0,0],scale:[.85,.85,.85]},ground:{rotation:[0,0,0],translation:[0,3,0],scale:[.5,.5,.5]},fixed:{rotation:[0,0,0],translation:[0,0,0],scale:[.7,.7,.7]},firstperson_righthand:{rotation:[0,-45,15],translation:[0,1,0],scale:[.5,.5,.5]},thirdperson_righthand:{rotation:[75,45,0],translation:[0,2,0],scale:[.45,.45,.45]}}};
 fs.writeFileSync(path.join(resources,'models/item',ids[i]+'.json'),JSON.stringify(model,null,2)+'\n');
}
for(const locale of ['zh_cn','en_us']){
 const file=path.join(resources,'lang',locale+'.json');const lang=JSON.parse(fs.readFileSync(file,'utf8'));const zh=locale==='zh_cn';
 ids.forEach((id,i)=>{lang['item.dynasty.'+id]=(zh?names:english)[i];lang['treasure.dynasty.'+id]=(zh?tips:enTips)[i];});
 Object.assign(lang,zh?{'workshop.dynasty.next':'下一份：%s（已投入 %s/%s）','jei.dynasty.workshop':'王朝 · 古法炼制','jei.dynasty.workshop.steps':'按左至右逐个投料；完成后空手领取。','treasure.dynasty.altar_read':'宙光星简：四象归位 %s/4','treasure.dynasty.no_target':'未找到可作用的目标。'}:{'workshop.dynasty.next':'Next: %s (%s/%s deposited)','jei.dynasty.workshop':'Dynasty · Ancient Craft','jei.dynasty.workshop.steps':'Deposit one at a time, left to right. Collect with an empty hand.','treasure.dynasty.altar_read':'Star Leaf: %s/4 offerings complete','treasure.dynasty.no_target':'No valid target found.'});
 // No obsolete tutorial text remains for the retired inventory-bulk transactions.
 for(const key of Object.keys(lang))if(key.startsWith('workshop.dynasty.')&&key!=='workshop.dynasty.next')delete lang[key];
 fs.writeFileSync(file,JSON.stringify(lang,null,2)+'\n');
}
console.log('Generated six original JSON relic models and localized station/relic text.');
