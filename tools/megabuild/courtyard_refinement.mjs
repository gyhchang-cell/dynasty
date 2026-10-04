// Original giant-martial courtyard overlay. Coordinates match the existing manor, not a replacement.
export function refineCourtyard(raw,m){
 const {width:w,height:h,length:l,palette}=m,b=Buffer.from(raw),stride=w*l;
 const id=s=>{let i=palette.indexOf('minecraft:'+s);if(i<0){if(palette.length===256)throw Error('Palette full');i=palette.push('minecraft:'+s)-1;}return i;};
 const stone=id('smooth_stone'),edge=id('polished_andesite'),brick=id('stone_bricks'),dark=id('polished_deepslate'),wood=id('stripped_dark_oak_log[axis=y]'),plank=id('dark_oak_planks'),copper=id('waxed_cut_copper'),lamp=id('sea_lantern');
 const floor=new Set(['grass_block','moss_block','sandstone'].map(id));let paved=0;
 const at=(x,y,z)=>x+z*w+y*stride;
 // Formal paired courts only. Preserve the eastern pond, western rock garden, roofs and interiors.
 for(let x=125;x<=325;x++)for(let z=284;z<=449;z++){
  let i=at(x,3,z);if(!floor.has(b[i])||b[i+stride]!==0)continue;
  if(Math.abs(x-225)<15)continue; // Existing axial road is the primary visual axis.
  b[i]=(x===125||x===325||z===284||z===449||x%24===0||z%24===0)?edge:stone;paved++;
 }
 const placements=[];
 function feature(name,cx,cz,rx,rz,top,draw){
  for(let x=cx-rx;x<=cx+rx;x++)for(let z=cz-rz;z<=cz+rz;z++)for(let y=5;y<=top;y++)if(b[at(x,y,z)])throw Error('Courtyard feature intersects original '+name+' at '+[x,y,z]);
  const put=(x,y,z,state)=>{if(x<0||x>=w||z<0||z>=l||y<0||y>=h)throw Error('Outside manor');b[at(x,y,z)]=state;};
  const box=(x0,y0,z0,x1,y1,z1,state)=>{for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)put(cx+x,y,cz+z,state);};
  draw(box,put);placements.push({name,x:cx,z:cz,height:top-3});
 }
 // Oversized practice weapons and furniture establish a giant's scale, without copying architecture.
 feature('巨人练武桩',177,318,9,7,32,(box)=>{
  box(-7,4,-6,7,5,6,brick);box(-3,6,-3,3,29,3,wood);box(-9,19,-2,9,22,2,wood);
  box(-4,10,-4,4,11,4,copper);box(-4,25,-4,4,26,4,copper);box(-4,30,-4,4,32,4,plank);
 });
 feature('巨型兵器架',273,318,13,5,28,(box)=>{
  box(-13,4,-5,13,5,5,brick);for(const x of [-11,11])box(x-1,6,-1,x+1,25,1,wood);
  box(-13,11,-1,13,12,1,plank);box(-13,23,-1,13,24,1,plank);
  for(const x of [-7,0,7]){box(x,6,-3,x,24,-3,wood);box(x-2,24,-4,x+2,26,-2,dark);box(x-1,27,-4,x+1,28,-2,edge);}
 });
 feature('巨人会武石桌',177,397,12,7,16,(box)=>{
  for(const x of [-8,8])for(const z of [-4,4])box(x-1,4,z-1,x+1,12,z+1,brick);
  box(-12,13,-7,12,15,7,dark);box(-11,16,-6,11,16,6,stone);
 });
 feature('巨人镇庭石座',273,410,8,7,28,(box)=>{
  box(-8,4,-7,8,6,7,brick);box(-6,7,-5,6,13,5,dark);box(-6,14,3,6,26,5,brick);
  box(-7,13,-5,-5,18,3,edge);box(5,13,-5,7,18,3,edge);box(-7,27,2,7,28,6,edge);
 });
 // Quiet, regularly spaced stone lanterns flank the axial route, not a scatter of decorations.
 for(const x of [204,246])for(const z of [300,346,390,438]){
  if([4,5,6,7,8,9].some(y=>b[at(x,y,z)]))continue;
  for(let y=4;y<=7;y++)b[at(x,y,z)]=brick;b[at(x,8,z)]=lamp;b[at(x,9,z)]=dark;
 }
 m.courtyardRefinement={version:1,paved,placements};return b;
}
