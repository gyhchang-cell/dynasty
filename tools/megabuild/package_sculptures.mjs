import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {refineCourtyard} from './courtyard_refinement.mjs';

// Generated model packaging, never reads/writes a Minecraft save.
const project=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const source=resolve(process.argv[2]||'/Users/a15356015027/Documents/Codex/2026-09-18/ni/outputs/dragon-ruin');
const target=resolve(project,'src/main/resources/data/dynasty/sculptures');
const {validateSchematic}=await import(pathToFileURL(resolve(source,'minecraft/schematic-test.mjs')));
const sha=b=>createHash('sha256').update(b).digest('hex');
const jobs=[{id:'longque_sanctuary',title:'龙阙镇渊巨像',folder:'altar/combined-minecraft',owned:'altar/combined-owned-altar.json'},
  {id:'yunqi_manor',title:'云栖庄园',folder:'manor/minecraft'}];
mkdirSync(target,{recursive:true});const report=[];
for(const job of jobs){
  const dir=resolve(source,job.folder),meta=JSON.parse(readFileSync(resolve(dir,'metadata.json'),'utf8')),raw=readFileSync(resolve(dir,'blocks.bin'));
  const {width:w,height:h,length:l}=meta,stride=w*l,volume=w*h*l;
  if(raw.length!==volume)throw new Error('Voxel byte length mismatch '+job.id);
  const counts=new Array(meta.palette.length).fill(0),lo=[w,h,l],hi=[-1,-1,-1];
  for(let y=0;y<h;y++)for(let z=0;z<l;z++)for(let x=0;x<w;x++){
    const p=raw[x+z*w+y*stride];if(p>=counts.length)throw new Error('Palette overflow');counts[p]++;
    if(p){lo[0]=Math.min(lo[0],x);lo[1]=Math.min(lo[1],y);lo[2]=Math.min(lo[2],z);hi[0]=Math.max(hi[0],x);hi[1]=Math.max(hi[1],y);hi[2]=Math.max(hi[2],z);}
  }
  if(volume-counts[0]!==meta.blockCount)throw new Error('Source count mismatch');
  const filename=meta.files?.schematic||meta.schematic;
  if(!filename)throw new Error('Missing source schem filename');
  const roundTrip=validateSchematic(resolve(dir,filename),{width:w,height:h,length:l,blocks:raw,palette:meta.palette.map(p=>p.id),offset:meta.offset});
  const dims=hi.map((n,i)=>n-lo[i]+1),[cw,ch,cl]=dims,crop=Buffer.alloc(cw*ch*cl);
  for(let y=0;y<ch;y++)for(let z=0;z<cl;z++)raw.copy(crop,y*cw*cl+z*cw,(y+lo[1])*stride+(z+lo[2])*w+lo[0],(y+lo[1])*stride+(z+lo[2])*w+lo[0]+cw);
  let compressed=gzipSync(crop,{level:9});const round=gunzipSync(compressed);
  if(!round.equals(crop))throw new Error('Compressed resource failed full byte roundtrip');
  let checked=0;for(let y=0;y<h;y++)for(let z=0;z<l;z++)for(let x=0;x<w;x++){
    const inside=x>=lo[0]&&y>=lo[1]&&z>=lo[2]&&x<=hi[0]&&y<=hi[1]&&z<=hi[2];
    const value=inside?round[(x-lo[0])+(z-lo[2])*cw+(y-lo[1])*cw*cl]:0;
    if(value!==raw[x+z*w+y*stride])throw new Error('Crop reconstruction changed a voxel');checked++;
  }
  let ritual=null;
  if(job.owned){
    const own=JSON.parse(readFileSync(resolve(source,job.owned),'utf8'));
    const local=p=>({x:p.x-lo[0],y:p.y-lo[1],z:p.z-lo[2]});
    ritual={returnFeet:own.returnFeet.map((v,i)=>v-lo[i]),nodes:own.nodes.map(n=>({...local(n),slot:n.slot})),
      owned:own.blocks.map(b=>({...local(b),state:b.state}))};
    for(const b of ritual.owned)if(meta.palette[crop[b.x+b.z*cw+b.y*cw*cl]].id!==b.state)throw new Error('Ritual ownership mismatch');
  }
  const manifest={version:1,id:job.id,title:job.title,format:'dense-u8-gzip',order:'x+z*width+y*width*length',width:cw,height:ch,length:cl,
    blockCount:meta.blockCount,voxelCount:crop.length,palette:meta.palette.map(p=>p.id),sha256:sha(crop),gzipSha256:sha(compressed),data:job.id+'.vox.gz',
    source:{original:true,kind:'Original procedural model and original voxel conversion',dimensions:[w,h,l],cropOffset:lo,voxelSha256:sha(raw),schematicSha256:sha(readFileSync(resolve(dir,filename)))},
    placement:'Admin placement retains preflight. Natural generation uses deterministic rare sites and chunk-local structure tiles.',ritual};
  if(job.id==='yunqi_manor'){
    const refined=refineCourtyard(crop,manifest);refined.copy(crop);compressed=gzipSync(crop,{level:9});
    manifest.blockCount=crop.reduce((n,v)=>n+(v!==0),0);manifest.sha256=sha(crop);manifest.gzipSha256=sha(compressed);
    if(!gunzipSync(compressed).equals(crop))throw new Error('Refined courtyard roundtrip failed');
  }
  writeFileSync(resolve(target,job.id+'.json'),JSON.stringify(manifest,null,2)+'\n');writeFileSync(resolve(target,job.id+'.vox.gz'),compressed);
  report.push({id:job.id,title:job.title,dimensions:dims,sourceDimensions:[w,h,l],cropOffset:lo,blockCount:manifest.blockCount,originalBlockCount:meta.blockCount,fullSourceVoxelsCompared:checked,
    rawSha256:manifest.sha256,gzipSha256:manifest.gzipSha256,gzipBytes:compressed.length,schematicRoundTrip:roundTrip,
    ritualOwnedCount:ritual?.owned.length||0,ritualNodes:ritual?.nodes.length||0,gameTested:false,saveModified:false});
}
const out=resolve(project,'docs/megabuild/sculpture-resource-validation.json');mkdirSync(dirname(out),{recursive:true});
writeFileSync(out,JSON.stringify({version:1,validation:'Full source schematic readback, gzip readback, all-voxel crop reconstruction, source/model SHA256 and ritual ownership checks.',buildings:report},null,2)+'\n');
console.log(JSON.stringify(report,null,2));
