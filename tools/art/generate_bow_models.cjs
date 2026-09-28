// Shared sprite/pose contract for all drawn bows. No texture resampling.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const base = path.join(root, 'src/main/resources/assets/dynasty');
const bows = ['houyi_bow','zhuxing_bow','fengling_bow','shenbi_bow','dragon_bow','chang_gong'];
for (const bow of bows) for (let stage=-1; stage<3; stage++) {
  const id=bow+(stage<0?'':`_pulling_${stage}`);
  const file=path.join(base,'textures/item',id+'.png');
  const [w,h]=execFileSync('magick',['identify','-format','%w %h',file],{encoding:'utf8'}).split(' ').map(Number);
  if (w!==h || ![64,128].includes(w)) throw Error('Unsupported sprite: '+file);
  const rgba=execFileSync('magick',[file,'-alpha','on','-depth','8','RGBA:-'],{maxBuffer:w*h*4+1024});
  const solid=(x,y)=>x>=0&&y>=0&&x<w&&y<h&&rgba[(y*w+x)*4+3]>=26;
  const s=16/w, z0=8-s/2, z1=8+s/2, face=uv=>({texture:'#layer0',uv});
  // Same face-UV convention as Minecraft ItemModelGenerator: NORTH reverses U.
  const elements=[{from:[0,0,z0],to:[16,16,z1],shade:false,faces:{
    north:face([16,0,0,16]),south:face([0,0,16,16])}}];
  // Each silhouette edge samples its own opaque pixel, ignoring transparent noise.
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) if(solid(x,y)) {
    const faces={}, uv=[(x+.25)*s,(y+.25)*s,(x+.75)*s,(y+.75)*s];
    if(!solid(x-1,y)) faces.west=face(uv);
    if(!solid(x+1,y)) faces.east=face(uv);
    if(!solid(x,y-1)) faces.up=face(uv);
    if(!solid(x,y+1)) faces.down=face(uv);
    if(Object.keys(faces).length) elements.push({from:[x*s,16-(y+1)*s,z0],to:[(x+1)*s,16-y*s,z1],shade:false,faces});
  }
  const model={parent:'dynasty:item/solid_bow',
    gui_light:'front',render_type:'minecraft:cutout',ambientocclusion:false,
    textures:{layer0:`dynasty:item/${id}`,particle:`dynasty:item/${id}`},elements};
  if(stage<0) model.overrides=[0,.65,.9].map((pull,i)=>({predicate:{'dynasty:pulling':1,...(i?{'dynasty:pull':pull}:{})},model:`dynasty:item/${bow}_pulling_${i}`}));
  else model.display=Object.fromEntries([['righthand',-76.87],['lefthand',103.13]].map(([side,yaw])=>[
    'firstperson_'+side,{rotation:[26.78,yaw,0],translation:[.8,3.2,.8],scale:[.62,.62,.62]}]));
  fs.writeFileSync(path.join(base,'models/item',id+'.json'),JSON.stringify(model)+'\n');
  console.log(id,w+'px',elements.length+' mesh elements');
}
