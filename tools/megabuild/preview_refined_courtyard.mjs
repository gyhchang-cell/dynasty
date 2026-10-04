// Native plan view from the exact packaged voxels; not an illustrative reconstruction.
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
const base=new URL('../../src/main/resources/data/dynasty/sculptures/',import.meta.url);
const m=JSON.parse(readFileSync(new URL('yunqi_manor.json',base))),b=gunzipSync(readFileSync(new URL(m.data,base)));
const color=s=>s.includes('copper')?'#648d82':s.includes('leaves')?'#496545':s.includes('water')?'#49778f':s.includes('gold')?'#bba46b':s.includes('dark_oak')?'#614934':s.includes('log')?'#78634a':s.includes('grass')||s.includes('moss')?'#627251':s.includes('deepslate')?'#3f4c55':s.includes('concrete')?'#d7d5c9':s.includes('lantern')?'#e4e5b7':s.includes('stone')?'#aaa99e':'#928678';
const parts=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${m.width} ${m.length}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#25332b"/>`];
for(let z=0;z<m.length;z+=2)for(let x=0;x<m.width;x+=2){
 let y=m.height-1;while(y>=0&&!b[x+z*m.width+y*m.width*m.length])y--;
 if(y>=0)parts.push(`<rect x="${x}" y="${z}" width="2" height="2" fill="${color(m.palette[b[x+z*m.width+y*m.width*m.length]])}"/>`);
}
for(const f of m.courtyardRefinement.placements)parts.push(`<circle cx="${f.x}" cy="${f.z}" r="17" fill="none" stroke="#efd291" stroke-width="1"/><text x="${f.x}" y="${f.z+22}" text-anchor="middle" fill="#f7e7c2" font-size="6">${f.name}</text>`);
parts.push('</svg>');writeFileSync(new URL('../../docs/art/unification/courtyard-plan.svg',import.meta.url),parts.join('\n'));
