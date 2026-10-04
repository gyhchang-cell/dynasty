// Preserve the complete original placements; add a rare footprint exclusion, not replacement spawns.
import fs from 'node:fs';
import cp from 'node:child_process';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const source='/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar';
const zone={other_set:'dynasty:sculpture_tiles',chunk_count:8};
const own=path.join(root,'src/main/resources/data/dynasty/worldgen/structure_set');
for(const file of fs.readdirSync(own)){
 if(file==='sculpture_tiles.json')continue;
 const p=path.join(own,file),m=JSON.parse(fs.readFileSync(p));
 if(m.placement.exclusion_zone&&m.placement.exclusion_zone.other_set!==zone.other_set)throw Error('Preserve existing exclusion: '+file);
 m.placement.exclusion_zone=zone;fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
}
const out=path.join(root,'src/main/resources/data/minecraft/worldgen/structure_set');fs.mkdirSync(out,{recursive:true});
for(const id of ['villages','pillager_outposts','desert_pyramids','igloos','jungle_temples','swamp_huts','woodland_mansions','ruined_portals','ocean_ruins','shipwrecks','ocean_monuments']){
 const p=path.join(out,id+'.json');
 if(fs.existsSync(p)){if(JSON.parse(fs.readFileSync(p)).placement.exclusion_zone?.other_set===zone.other_set)continue;throw Error('Inspect existing vanilla override before replacing '+p);}
 const m=JSON.parse(cp.execFileSync('unzip',['-p',source,'data/minecraft/worldgen/structure_set/'+id+'.json'],{encoding:'utf8'}));
 // Pillager outposts already exclude villages. Preserve that native rule;
 // the sculpture itself rejects nearby outpost candidates instead.
 if(m.placement.exclusion_zone)continue;
 m.placement.exclusion_zone=zone;fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
}
