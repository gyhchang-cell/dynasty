// Native model geometry for the five bows that had no pull predicates/poses.
// Existing inventory icons and the six previously animated bows remain intact.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const dir=path.resolve(__dirname,'../../src/main/resources/assets/dynasty/models/item');
const bows={lie_gong:['spruce_planks','iron_block'],luoyan_bow:['dark_oak_planks','copper_block'],tianlang_bow:['deepslate_tiles','lapis_block'],sunbow:['gold_block','orange_terracotta'],zhuque_bow:['red_terracotta','gold_block']};
for(const [bow,materials] of Object.entries(bows)) {
 const basePath=path.join(dir,bow+'.json');if(!fs.existsSync(basePath))throw Error('Missing '+bow);
 const base=JSON.parse(fs.readFileSync(basePath));
 base.overrides=[0,.65,.9].map((pull,i)=>({predicate:{'dynasty:pulling':1,...(i?{'dynasty:pull':pull}:{})},model:`dynasty:item/${bow}_pulling_${i}`}));
 fs.writeFileSync(basePath,JSON.stringify(base)+'\n');
 let previous=0;
 for(let stage=0;stage<3;stage++) {
  const elements=[],pull=[.3,.65,1][stage],tip=11+pull*.6,nock=11.7+pull*3.4;
  const cube=(x,y,z,w,h,d,tex)=>elements.push({from:[x,y,z],to:[x+w,y+h,z+d],faces:Object.fromEntries(['north','south','east','west','up','down'].map(side=>[side,{texture:'#'+tex,uv:[0,0,16,16]}]))});
  const line=(a,b,width,tex)=>{let length=Math.hypot(b[0]-a[0],b[1]-a[1]),count=Math.ceil(length/.15);for(let i=0;i<count;i++){let t=(i+.5)/count;cube(a[0]+(b[0]-a[0])*t-width/2,a[1]+(b[1]-a[1])*t-width/2,8-width/2,width,width,width,tex);}};
  cube(7.5,6.8,7.55,1,2.4,.9,'wood');
  for(const side of [-1,1]) {
   const points=[[8,8],[8.3,8+side*2.4],[9.7,8+side*(4.7-pull*.4)],[tip,8+side*(6.3-pull*.5)]];
   for(let i=1;i<points.length;i++)line(points[i-1],points[i],i==3?.35:.5,i==3?'trim':'body');
   line(points.at(-1),[nock,8],.10,'string');
   if(bow==='zhuque_bow')for(let k=0;k<3;k++)line([9.7,8+side*(3+k*.6)],[8.5-k*.3,8+side*(5+k*.6)],.18,'trim');
  }
  cube(3,7.91,7.91,nock-3,.18,.18,'wood'); // Shaft ends exactly at the drawn string nock.
  for(let k=0;k<3;k++)cube(2.4+k*.22,7.65+k*.09,7.88,.3,.7-k*.18,.24,'trim');
  cube(nock-.75,7.7,7.95,.55,.6,.1,'string');
  assert(nock>previous&&nock<=16);previous=nock;
  const display=Object.fromEntries([['righthand',-76.87],['lefthand',103.13]].map(([hand,y])=>['firstperson_'+hand,{rotation:[26.78,y,0],translation:[.8,3.2,.8],scale:[.62,.62,.62]}]));
  const model={parent:'dynasty:item/solid_bow',render_type:'minecraft:cutout',textures:{body:'minecraft:block/'+materials[0],trim:'minecraft:block/'+materials[1],wood:'minecraft:block/dark_oak_planks',string:'minecraft:block/white_wool',particle:'dynasty:item/'+bow},elements,display};
  fs.writeFileSync(path.join(dir,`${bow}_pulling_${stage}.json`),JSON.stringify(model)+'\n');
  console.log(`${bow} stage ${stage}: grip=8,8 nock=${nock.toFixed(2)},8 arrow/string coincide; ${elements.length} cuboids`);
 }
}
