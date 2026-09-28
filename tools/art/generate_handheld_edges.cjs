// Preserve full front/back art; generate only genuine opaque silhouette side faces.
// Vanilla generated-item alpha>0 outlines include imperceptible alpha noise and make fins/gaps.
const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'src/main/resources/assets/dynasty');
let count=0;
for(const file of fs.readdirSync(path.join(base,'models/item'))) {
 const target=path.join(base,'models/item',file),m=JSON.parse(fs.readFileSync(target));
 if(!['item/handheld','minecraft:item/handheld','dynasty:item/solid_handheld'].includes(m.parent)||(m.elements&&!m.dynasty_solid_edges))continue;
 const tex=m.textures?.layer0;if(!tex?.startsWith('dynasty:item/'))continue;
 const png=path.join(base,'textures',tex.split(':')[1]+'.png');if(!fs.existsSync(png))continue;
 const [w,h]=execFileSync('magick',['identify','-format','%w %h',png],{encoding:'utf8'}).split(' ').map(Number);
 const data=execFileSync('magick',[png,'-alpha','on','-depth','8','RGBA:-'],{maxBuffer:w*h*4+1024});
 const solid=(x,y)=>x>=0&&y>=0&&x<w&&y<h&&data[(y*w+x)*4+3]>=26;
 const sx=16/w,sy=16/h,z0=7.75,z1=8.25;
 const face=uv=>({texture:'#layer0',uv});
 m.elements=[{from:[0,0,z0],to:[16,16,z1],shade:false,faces:{north:face([16,0,0,16]),south:face([0,0,16,16])}}];
 for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(solid(x,y)){
  const faces={},uv=[(x+.25)*sx,(y+.25)*sy,(x+.75)*sx,(y+.75)*sy];
  if(!solid(x-1,y))faces.west=face(uv);if(!solid(x+1,y))faces.east=face(uv);
  if(!solid(x,y-1))faces.up=face(uv);if(!solid(x,y+1))faces.down=face(uv);
  if(Object.keys(faces).length)m.elements.push({from:[x*sx,16-(y+1)*sy,z0],to:[(x+1)*sx,16-y*sy,z1],shade:false,faces});
 }
 // A builtin/generated ancestor causes ModelBakery to throw away these elements
 // and run ItemModelGenerator again. Keep transforms, but use a concrete parent.
 m.parent='dynasty:item/solid_handheld';
 m.render_type='minecraft:cutout';m.dynasty_solid_edges=true;
 fs.writeFileSync(target,JSON.stringify(m)+'\n');count++;
}
console.log('Rebuilt opaque silhouette edges for',count,'handheld models; textures unchanged.');
