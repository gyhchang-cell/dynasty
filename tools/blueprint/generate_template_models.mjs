// Original cod1 rigs. Geometry/animation JSON are the shipped sources, never embedded in Java.
// One unit = 1/16 block, +Y up, -Z forward. Existing repository atlases remain untouched.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import zlib from 'node:zlib';
const base='src/main/resources/assets/dynasty', out='docs/blueprint-cod1/models';
const palette={skin:0xad896f,leather:0x51402e,iron:0x484c48,edge:0xa4a38f,red:0x74352a,cloth:0x564537,gold:0xa98b4e,black:0x242621,paper:0xc2a963,fur:0x454945,jade:0x617765,bone:0xb3a58a};
// Read-only PNG decoding locates continuous opaque material swatches; no bitmap is edited.
function pngPixels(file){
 const b=fs.readFileSync(file);let p=8,w,h,ct,bd,id=[];
 while(p<b.length){const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=n+12;if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);bd=d[8];ct=d[9];}if(t==='IDAT')id.push(d);}
 assert.equal(bd,8);assert([2,6].includes(ct));const c=ct===6?4:3,s=w*c,r=zlib.inflateSync(Buffer.concat(id)),data=Buffer.alloc(w*h*c);let q=0;
 for(let y=0;y<h;y++){const f=r[q++];for(let x=0;x<s;x++){const a=x>=c?data[y*s+x-c]:0,b=y?data[(y-1)*s+x]:0,d=y&&x>=c?data[(y-1)*s+x-c]:0;let v=r[q++];if(f===1)v+=a;if(f===2)v+=b;if(f===3)v+=Math.floor((a+b)/2);if(f===4){const t=a+b-d,pa=Math.abs(t-a),pb=Math.abs(t-b),pc=Math.abs(t-d);v+=pa<=pb&&pa<=pc?a:pb<=pc?b:d;}data[y*s+x]=v&255;}}
 return {w,h,c,data};
}
const atlasNames={zuwu_daoshou:'royal_guard',ludun_jiashi:'royal_guard',fufa_jijiu:'imperial_soldier',shanjing_shanxiao:'nian_beast'};
let bones=[],activeId='',uvMap={};
function bone(name,parent,pivot,cubes=[],rotation){const b={name,pivot,cubes};if(parent)b.parent=parent;if(rotation)b.rotation=rotation;bones.push(b);return name;}
function cube(x,y,z,w,h,d,mat='cloth',rotation,pivot){
 const uv={},patch=uvMap[mat];
 for(const [face,fw,fh] of [['north',w,h],['south',w,h],['east',d,h],['west',d,h],['up',w,d],['down',w,d]]){
  const width=Math.min(patch.size[0],Math.max(1,Math.round(fw))),height=Math.min(patch.size[1],Math.max(1,Math.round(fh)));
  uv[face]={uv:[patch.uv[0]+Math.floor((patch.size[0]-width)/2),patch.uv[1]+Math.floor((patch.size[1]-height)/2)],uv_size:[width,height]};
 }
 const c={origin:[x,y,z],size:[w,h,d],uv};if(rotation){c.rotation=rotation;c.pivot=pivot??[x+w/2,y+h/2,z+d/2];}return c;
}
function add(name,...c){bones.find(b=>b.name===name).cubes.push(...c);}
function insertBone(name,parent,pivot,before,cubes=[]){bone(name,parent,pivot,cubes);const b=bones.pop();bones.splice(bones.findIndex(b=>b.name===before),0,b);return b;}
function wrapBone(child,name){const b=bones.find(b=>b.name===child);insertBone(name,b.parent,[...b.pivot],child);b.parent=name;}
function materialPatch(im,mat,col){
 const target=[col>>16,(col>>8)&255,col&255],n=['edge','gold','bone','paper'].includes(mat)?2:['skin','black','leather','cloth'].includes(mat)?4:8;let best,bestScore=Infinity;
 for(let y=0;y<=im.h-n;y++)for(let x=0;x<=im.w-n;x++){
  const sum=[0,0,0],square=[0,0,0];let opaque=true;
  for(let dy=0;dy<n&&opaque;dy++)for(let dx=0;dx<n;dx++){
   const p=((y+dy)*im.w+x+dx)*im.c;if(im.c===4&&im.data[p+3]<250){opaque=false;break;}
   for(let c=0;c<3;c++){const v=im.data[p+c];sum[c]+=v;square[c]+=v*v;}
  }
  if(!opaque)continue;
  const mean=sum.map(v=>v/(n*n)),variance=square.reduce((v,s,c)=>v+s/(n*n)-mean[c]**2,0)/3;
  // Reward modest native grain without sampling eyes, transparent borders or high-contrast motifs.
  const wanted=['skin','black','bone','paper'].includes(mat)?35:110;
  const score=mean.reduce((v,m,c)=>v+(m-target[c])**2,0)+Math.abs(variance-wanted)*.65+Math.max(0,variance-800)*3;
  if(score<bestScore){bestScore=score;best={uv:[x,y],size:[n,n],mean:mean.map(v=>Math.round(v)),variance:Math.round(variance)};}
 }
 assert(best,`No opaque ${n}x${n} swatch for ${activeId}/${mat}`);return best;
}
function start(id){activeId=id;bones=[];const im=pngPixels(`${base}/textures/entity/${atlasNames[id]}.png`);uvMap={};for(const [mat,col]of Object.entries(palette))uvMap[mat]=materialPatch(im,mat,col);bone('root',null,[0,0,0]);return im;}
function face(head,y,z,width=4.2,mask=false){
 add(head,cube(-width/2,y,z,width,4,3.4,mask?'black':'skin'),cube(-1.7,y-.65,z-.1,3.4,1.2,3,'skin'),cube(-.42,y+1,z-.65,.84,1.7,.75,mask?'red':'skin'));
 for(const s of [-1,1]){add(head,cube(s*1.14-.65,y+2.7,z-.3,1.3,.35,.45,'black',[0,0,s*12]),cube(s*1.08-.35,y+2.2,z-.4,.7,.28,.15,'paper'),cube(s*1.06-.14,y+2.2,z-.53,.28,.28,.14,'black'));
 if(mask)add(head,cube(s*1.8-.45,y+.6,z-.35,.9,2.2,.55,'red',[0,0,-s*13]),cube(s*1.1-.18,y-.1,z-.55,.36,1.35,.4,'bone',[0,0,-s*15]));}
}
function human({hip=11.5,chestY=22.5,shoulder=4.4,width=7.4,depth=4.2,headY=25,heavy=false,priest=false}){
 bone('pelvis','root',[0,hip,0],[cube(-3,hip-1,-2.1,6,2.8,4.2,'cloth')]);
 bone('waist','pelvis',[0,hip+1.3,0],[cube(-2.55,hip+1,-1.85,5.1,2.8,3.7,'leather')]);
 bone('waist_upper','waist',[0,hip+3.6,0],[cube(-2.7,hip+3.4,-1.8,5.4,2.6,3.6,'cloth')]);
 bone('chest','waist_upper',[0,chestY,0],[cube(-width/2,hip+5,-depth/2,width,chestY-hip-4.3,depth,priest?'red':'cloth')]);
 bone('chest_front','chest',[0,chestY-2,-depth/2],[cube(-width/2-.1,hip+5,-depth/2-.7,width+.2,chestY-hip-4.6,.8,priest?'red':heavy?'iron':'leather')]);
 bone('chest_back','chest',[0,chestY-2,depth/2],[cube(-width/2,hip+5,depth/2-.1,width,chestY-hip-4.4,.7,priest?'red':'leather')]);
 bone('neck','chest',[0,chestY+.3,0],[cube(-1.1,chestY,-1,2.2,2.5,2.2,'skin')]);
 bone('head','neck',[0,headY+.7,-.4]);face('head',headY-1.2,-2.1,heavy?4.8:4.2,priest);
 for(const s of [-1,1]){
  const side=s<0?'right':'left',x=s*shoulder,e=chestY-5.4,w=heavy?3.25:priest?1.8:2.35;
  bone(`${side}_shoulder`,'chest',[x,chestY,0]);
  bone(`${side}_upper_arm`,`${side}_shoulder`,[x,chestY,0],[cube(x-w/2,e,-1.45,w,5.4,2.9,priest?'red':heavy?'iron':'cloth')]);
  bone(`${side}_elbow`,`${side}_upper_arm`,[x,e,0],[cube(x-w/2,e-.65,-1.3,w,1.3,2.6,'leather')]);
  bone(`${side}_forearm`,`${side}_elbow`,[x,e,0],[cube(x-w/2,e-4.7,-1.2,w,4.7,2.4,heavy?'iron':s<0?'iron':'paper')]);
  bone(`${side}_wrist`,`${side}_forearm`,[x,e-4.7,0],[cube(x-.85,e-5,-.9,1.7,1.2,1.8,'leather')]);
  bone(`${side}_hand`,`${side}_wrist`,[x,e-5.1,0],[cube(x-1.1,e-6.3,-1.15,2.2,1.9,2.3,'skin')]);
  const lx=s*(heavy?3:2.2),k=hip*.53;
  bone(`${side}_thigh`,'pelvis',[lx,hip,0],[cube(lx-(heavy?1.7:1.2),k,-1.7,heavy?3.4:2.4,hip-k,3.4,'cloth')]);
  bone(`${side}_knee`,`${side}_thigh`,[lx,k,0],[cube(lx-1.4,k-.8,-1.9,2.8,1.7,3.7,heavy?'iron':'leather')]);
  bone(`${side}_shin`,`${side}_knee`,[lx,k,0],[cube(lx-1.1,1.7,-1.3,2.2,k-1.2,2.6,'cloth')]);
  bone(`${side}_ankle`,`${side}_shin`,[lx,1.7,0],[cube(lx-1.2,.8,-1.3,2.4,1.9,2.7,'leather')]);
  bone(`${side}_foot`,`${side}_ankle`,[lx,1,0],[cube(lx-1.5,0,-3,3,1.4,4.5,'black')]);
 }
}
function soldier(){
 human({});
 // Layered, stepped conical iron brim, intentionally far wider than the face.
 bone('helmet','head',[0,28,0]);
 for(let i=0;i<5;i++){const w=12.6-i*2.1;add('helmet',cube(-w/2,27.1+i*.55,-w*.38,w,.65,w*.76,i%2?'iron':'black'));}
 bone('chin_cord','head',[0,24,-1.8],[cube(-2.45,24.2,-1.4,.35,3.2,.4,'paper'),cube(2.1,24.2,-1.4,.35,3.2,.4,'paper'),cube(-2.1,23.7,-1.7,4.2,.45,.45,'paper')]);
 for(const s of [-1,1]){const side=s<0?'right':'left',x=s*4.4;
  bone(`${side}_shoulder_plate`,`${side}_shoulder`,[x,22.5,0],[cube(x-1.9,21.5,-2,3.8,1.4,4,'leather',[0,0,-s*13]),cube(x-1.7,20.6,-2.1,3.4,1,4.2,'iron',[0,0,-s*19])]);
  bone(`${side}_rag`,`${side}_shoulder_plate`,[x,22,-1],[cube(x-1.1,s<0?16.7:18.6,-2.3,1.2,s<0?5.6:3.7,.35,'red',[0,0,s*12]),cube(x+.15,s<0?18.7:20,-2.15,.75,s<0?3.4:2.1,.3,'red',[0,0,-s*10])]);
  for(let k=0;k<3;k++)add(`${side}_shin`,cube(s*2.2-1.2,2+k*1.1,-1.4,2.4,.35,2.8,'paper'));
 }
 bone('belt','waist',[0,13,0],[cube(-3.1,12.2,-2.3,6.2,1.2,4.6,'leather'),cube(-.8,12.2,-2.65,1.6,1.2,.45,'gold')]);
 bone('skirt_left','pelvis',[2.5,11,0],[cube(.9,7,-2.5,3.4,4.7,.7,'leather',[0,0,8])]);
 bone('skirt_right','pelvis',[-2.5,11,0],[cube(-4.3,7.7,-2.55,3.4,4,.7,'leather',[0,0,-7])]);
 bone('dao','right_hand',[-4.4,11.9,-.6],[cube(-4.75,9.2,-.9,.7,3.8,.7,'leather'),cube(-5.7,9,-1,2.6,.45,.9,'gold'),cube(-4.85,-1.9,-.95,.85,11,.5,'iron'),cube(-4.05,-1.8,-1,.22,10.8,.6,'edge'),cube(-4.7,-3,-.96,.7,1.3,.5,'edge',[0,0,-18])],[0,0,43]);
 for(const [x,y,w,h]of [[-5.1,13.1,1.5,.32],[-5.1,14.3,1.5,.32],[-5.1,13.1,.3,1.4],[-3.9,13.1,.3,1.4]])add('dao',cube(x,y,-.9,w,h,.6,'gold'));
 bone('scabbard','pelvis',[3,11,1.2],[cube(2.8,1.4,1.1,.9,10.2,1.1,'black'),cube(2.6,10.4,.95,1.25,.65,1.4,'gold')],[0,0,-15]);
}
function shieldman(){
 human({hip:12.6,chestY:25.2,shoulder:6.5,width:11.5,depth:6.2,headY:28,heavy:true});
 bone('helmet','head',[0,31,0],[cube(-2.9,30,-2.5,5.8,1.7,5.1,'iron'),cube(-2,31.6,-1.9,4,1.1,3.8,'black'),cube(-2.9,29.5,-2.65,5.8,.5,.5,'gold')]);
 for(const s of [-1,1]){const side=s<0?'right':'left',x=s*6.5;
  bone(`${side}_shoulder_plate`,`${side}_shoulder`,[x,25,0]);for(let k=0;k<3;k++)add(`${side}_shoulder_plate`,cube(x-2.6,24-k*.8,-3.3,5.2,1.2,6.6,k?'iron':'gold',[0,0,-s*(6+k*5)]));
  wrapBone(`${side}_shoulder_plate`,`${side}_shoulder_rail`);
  bone(`${side}_hip_plate`,`${side}_thigh`,[s*3.5,13,0],[cube(s*3.5-2.1,9.8,-2.7,4.2,3.2,1,'iron',[0,0,s*7],[s*3.5,10,-2.2])]);
  bone(`${side}_hip_plate_lower`,`${side}_hip_plate`,[s*3.5,10.4,0],[cube(s*3.5-2.1,7,-2.699,4.2,3.4,.998,'iron',[0,0,s*7],[s*3.5,10,-2.2])]);
  for(let k=0;k<4;k++)add(`${side}_hip_plate${k<2?'_lower':''}`,cube(s*3.5-1.9,7.3+k*1.35,-2.95,3.8,.4,.4,'edge'));
  add(`${side}_shin`,cube(s*3-1.5,1.5,-1.8,3,4.8,.8,'iron'));
 }
 for(let y=0;y<4;y++)for(let x=0;x<7;x++)add('chest_front',cube(-5+x*1.45,18+y*1.45,-3.9,1.3,1.4,.35,(x+y)%3?'iron':'edge'));
 // The shield body has exactly 28.8 x 14.4 units (1.8 x 0.9 blocks), three bowed vertical leaves.
 bone('shield_grip','left_hand',[6.5,14,-.6],[cube(1.5,13,-3,5.2,.8,.8,'leather'),cube(5.8,11.4,-3,.7,4,.8,'leather')]);
 bone('shield','shield_grip',[2,15.4,-5]);
 for(let i=0;i<3;i++)add('shield',cube(-5.2+i*4.8,1,-5.3-(i===1?.6:0),4.8,28.8,1.7,'leather'));
 for(const x of [-5.2,8.5])add('shield',cube(x,1,-6,.7,28.8,2.6,'gold'));
 for(const y of [1,28.95,9.8,20])add('shield',cube(-5.2,y,-6.05,14.4,.85,2.65,'gold'));
 for(const s of [-1,1])add('shield',cube(1.7+s*2.7,11.5,-6.5,.65,8.7,.6,'iron',[0,0,s*27]));
 add('shield',cube(.7,14.8,-6.7,2.6,3.3,.9,'iron',[0,0,45]));
 for(const x of [-4.8,8.4])for(const y of [4,8,13,18,24,27])add('shield',cube(x,y,-6.4,.4,.45,.45,'edge'));
 bone('mace','right_hand',[-6.5,14.4,0],[cube(-6.9,12.5,-.4,.8,14.5,.8,'leather'),cube(-8.2,25,-1.7,3.4,4.4,3.4,'gold'),cube(-8.15,25,-1.75,3.3,4.4,3.5,'gold',[0,45,0]),cube(-6.9,29.2,-.4,.8,3,.8,'iron'),cube(-8.4,26.8,-.35,4,.65,.7,'iron'),cube(-6.85,26.8,-2.2,.7,.65,4.4,'iron')],[0,0,8]);
}
function priest(){
 human({hip:11,chestY:20.6,shoulder:4,width:5.6,depth:3.2,headY:24.1,priest:true});
 // Actual stoop is built into the torso hierarchy, separate from the head's mask and crown.
 bones.find(b=>b.name==='waist_upper').rotation=[12,0,0];bones.find(b=>b.name==='head').rotation=[-9,0,0];
 bone('mask','head',[0,25,-2.6]);
 for(const s of [-1,1]){
  const part=s<0?'mask_right':'mask_left';
  bone(part,'mask',[s,25,-2.8],[cube(s<0?-2:0,23.8,-2.9,2,3.9,.6,'red'),cube(s<0?-.5:0,24.4,-3.7,.5,2.3,1,'gold'),cube(s*1.12-.65,26,-3.1,1.3,.4,.3,'black',[0,0,-s*17]),cube(s*1.1-.2,23.2,-3.1,.4,1.7,.4,'bone',[0,0,s*10])]);
 }
 bone('crown','head',[0,27,0],[cube(-2.1,27.2,-1.8,4.2,1,3.6,'black'),cube(-1.7,28,-1.4,3.4,2.2,2.8,'red'),cube(-1.1,30,-1,2.2,1.7,2,'black'),cube(-.55,31.6,-.55,1.1,1.5,1.1,'gold')]);
 bone('robe_front','pelvis',[0,12,-1.7],[cube(-3.3,7,-2.3,6.6,5.4,1,'red'),cube(-4.2,2,-2.4,8.4,5.2,1.3,'red'),cube(-.55,2,-3.15,1.1,9.3,.3,'gold')]);
 bone('robe_back','pelvis',[0,12,1.9],[cube(-3.6,6.7,1.6,7.2,5.4,1,'red'),cube(-4.5,1.6,1.9,9,5.7,1,'red',[14,0,0])]);
 for(const s of [-1,1]){const side=s<0?'right':'left',x=s*4;
  bone(`${side}_sleeve_inner`,`${side}_upper_arm`,[x,20.4,0],[cube(x-1.7,17.2,-1.9,3.4,3.2,3.8,'red'),cube(x-2,14,-2.1,4,3.4,4.2,'red')]);
  bone(`${side}_sleeve_outer`,`${side}_forearm`,[x,15.2,0],[cube(x-2.5,11.5,-2.5,5,3.9,5,'red'),cube(x-3.2,8,-2.7,6.4,3.7,5.4,'red'),cube(x-3.3,8,-2.8,6.6,.75,5.6,'gold')]);
  bone(`${side}_sleeve_tail`,`${side}_sleeve_outer`,[x,8,1],[cube(x-2.25,5.4,.7,4.5,2.9,.7,'red',[10,0,s*8])]);
  bone(`${side}_robe_panel`,'pelvis',[s*3.1,11.5,.3],[cube(s<0?-4.4:3.1,2.1,-1.8,1.3,9.4,4.2,'red',[0,0,s*5])]);
 }
 bone('beads','chest',[0,19,-2.7]);for(let i=0;i<9;i++){const a=Math.PI*(i/8);add('beads',cube(Math.cos(a)*2.5-.6,19.2-Math.sin(a)*3,-3,.95,.95,.95,'black',[0,0,45]));}
 bone('staff','right_hand',[-4,9,-.5],[cube(-7.4,1,-1,.85,31,.85,'leather'),cube(-8.1,25.2,-1.2,2.1,1.1,1.3,'gold'),cube(-7.8,31.4,-1.4,1.6,2,1.6,'leather'),cube(-11.6,30.2,-1.05,9.3,.8,.95,'leather',[0,0,-5]),cube(-7.2,9,-.9,3.4,.7,.7,'leather')]);
 for(let i=0;i<3;i++){const x=-10.5+i*3.3;
  bone(`talisman_${i}`,'staff',[x,30,-.8],[cube(x-.65,23.1+(i%2),-1.05,1.3,6.7-(i%2),.18,'paper')]);
  bone(`talisman_tip_${i}`,`talisman_${i}`,[x,23.6+(i%2),-1],[cube(x-.65,19.4+(i%2),-1,1.3,4.2,.18,'paper')]);
  for(let k=0;k<3;k++)add(`talisman_${i}`,cube(x-.35,24+k*1.1,-1.17,.7,.25,.08,'red'),cube(x-.12,24+k*1.1,-1.17,.24,.8,.08,'red'));
 }
 // Height through the crown is 1.8m including the 0.1m hover; sleeve width stays generous.
 for(const b of bones){b.pivot[1]*=.815;for(const c of b.cubes){c.origin[1]*=.815;c.size[1]*=.815;if(c.pivot)c.pivot[1]*=.815;}}
 // Skin/body surfaces can disappear without scaling their joint parents and attached clothing.
 // At rest these identity children render exactly the same cubes at exactly the same positions.
 const anatomy=new Set(['pelvis','waist','waist_upper','chest','neck','head']);
 for(const b of [...bones])if(anatomy.has(b.name)||/_(upper_arm|elbow|forearm|wrist|hand|thigh|knee|shin|ankle|foot)$/.test(b.name)){
  if(!b.cubes.length)continue;
  const cubes=b.cubes;b.cubes=[];bone(`body_${b.name}`,b.name,[...b.pivot],cubes);
 }
 for(const s of [-1,1]){const side=s<0?'right':'left',x=s*4,inner=bones.find(b=>b.name===`${side}_sleeve_inner`),outer=bones.find(b=>b.name===`${side}_sleeve_outer`);
  wrapBone(inner.name,`${side}_sleeve_inner_spring`);wrapBone(outer.name,`${side}_sleeve_outer_spring`);
  insertBone(`${side}_sleeve_inner_tip`,inner.name,[x,14.018,0],outer.parent,inner.cubes.splice(1));
  insertBone(`${side}_sleeve_outer_tip`,outer.name,[x,9.3725,0],`${side}_sleeve_tail`,outer.cubes.splice(1));
  bones.find(b=>b.name===`${side}_sleeve_tail`).parent=`${side}_sleeve_outer_tip`;
 }
 for(let i=0;i<3;i++)wrapBone(`talisman_${i}`,`talisman_spring_${i}`);
}
function beast(){
 bone('pelvis','root',[0,9,6],[cube(-3.2,6.8,3.4,6.4,5.4,7,'fur')]);
 bone('waist','pelvis',[0,10,2],[cube(-3.6,7.2,-1.5,7.2,5.8,6.7,'fur')]);
 bone('chest','waist',[0,12,-3],[cube(-5.6,8.6,-7.5,11.2,6.8,9,'fur'),cube(-4.7,14,-5.4,9.4,2.2,6.3,'black')]);
 bone('neck','chest',[0,12.4,-7],[cube(-3.4,10,-10.7,6.8,4.9,4,'fur')]);
 bone('head','neck',[0,12,-10],[cube(-3.5,8.6,-14.1,7,6.3,5.1,'jade'),cube(-2.75,8.5,-16.3,5.5,3.2,3.5,'black'),cube(-2.6,11.1,-15.8,5.2,1.1,2.5,'jade')]);
 bone('jaw','head',[0,9.2,-13],[cube(-2.65,7.8,-16.5,5.3,1.2,4,'fur')]);
 for(const s of [-1,1]){add('head',cube(s*2-.8,12.6,-14.75,1.6,.8,1.1,'black',[0,0,-s*16]),cube(s*1.9-.38,12.2,-14.9,.76,.35,.15,'paper'),cube(s*2.1-.25,8.3,-16.35,.5,2.8,.65,'bone',[0,0,-s*8]),cube(s*3.4-.5,11.4,-12.7,1,2.2,1.5,'black'));
  const side=s<0?'right':'left',x=s*5.4;
  bone(`${side}_shoulder`,'chest',[x,12.8,-5.6],[cube(x-2.5,9.3,-7.7,5,5.4,5.3,'fur')]);
  bone(`${side}_upper_arm`,`${side}_shoulder`,[x,12.2,-5.6],[cube(x-1.9,6.5,-7.3,3.8,6.7,4,'fur')]);
  bone(`${side}_elbow`,`${side}_upper_arm`,[x,6.8,-5.8],[cube(x-2,5.3,-7.4,4,2.8,3.9,'black')]);
  bone(`${side}_forearm`,`${side}_elbow`,[x,6.5,-5.8],[cube(x-1.8,1.9,-8,3.6,4.9,4.5,'fur')]);
  bone(`${side}_wrist`,`${side}_forearm`,[x,2.4,-6.7],[cube(x-1.7,1,-8.7,3.4,1.9,4.3,'black')]);
  bone(`${side}_hand`,`${side}_wrist`,[x,1.3,-7.3],[cube(x-2,0,-10.3,4,1.8,4.8,'fur')]);
  for(let k=0;k<3;k++)add(`${side}_hand`,cube(x-1.5+k*1.15,0,-11.6,.75,1,2.4,'black',[10,0,0]));
  const hx=s*2.8;
  bone(`${side}_thigh`,'pelvis',[hx,9,6.8],[cube(hx-1.6,5.3,5.2,3.2,5,4.6,'fur')],[25,0,s*5]);
  bone(`${side}_knee`,`${side}_thigh`,[hx,5.4,7.7],[cube(hx-1.3,4.2,6.3,2.6,2.1,3.2,'fur')]);
  bone(`${side}_shin`,`${side}_knee`,[hx,5,7.7],[cube(hx-1,1.4,7.2,2,3.8,2.6,'fur')],[-32,0,0]);
  bone(`${side}_ankle`,`${side}_shin`,[hx,1.8,8],[cube(hx-1.1,.7,7.2,2.2,1.7,2.7,'black')]);
  bone(`${side}_foot`,`${side}_ankle`,[hx,.8,8],[cube(hx-1.5,0,5.7,3,1.3,4.9,'fur')]);
 }
 for(let k=0;k<5;k++){const z=-4.8+k*2.6,y=15.5-k*.8;bone(`spine_${k}`,k<3?'chest':'waist',[0,y,z],[cube(-.6,y-.4,z-.5,1.2,3.2-k*.17,1.25,'black',[-33,0,0])]);}
 bone('tail','pelvis',[0,10,9],[cube(-.8,9.3,9,1.6,1.5,4.2,'fur')]);
 bone('tail_hook','tail',[0,10.2,12.2],[cube(-.7,10,11.7,1.4,3.5,1.4,'black'),cube(-.65,13,10.2,1.3,1.2,2.4,'black')]);
 // Compensate the shortened vertical projection of the folded hind chain, keeping four contacts.
 for(const b of bones)if(/_(thigh|knee|shin|ankle|foot)$/.test(b.name)){b.pivot[1]-=.9;for(const c of b.cubes){c.origin[1]-=.9;if(c.pivot)c.pivot[1]-=.9;}}
 for(const s of [-1,1]){const side=s<0?'right':'left';
  for(const part of ['shoulder','elbow','wrist','thigh','knee','ankle'])wrapBone(`${side}_${part}`,`${side}_climb_${part}`);
  bone(`${side}_claw_contact`,`${side}_hand`,[s*5.4,.45,-11.55]);
  bone(`${side}_foot_contact`,`${side}_foot`,[s*2.8,-.82,6.05]);
 }
}
function frames(values){return Object.fromEntries(values.map(([t,v])=>[(t/20).toFixed(2),v]));}
function channel(values,kind='rotation'){return {[kind]:frames(values)};}
const rot=(...v)=>channel(v),pos=(...v)=>channel(v,'position');
const scale=(...v)=>channel(v,'scale');
// Offline kinematics pins detached gear and flattened cloth to the authored floor. No runtime
// client bone positions participate in combat. Coordinates match GeckoLib's mirrored X basis.
const ident=[1,0,0,0,1,0,0,0,1],addV=(a,b)=>a.map((v,i)=>v+b[i]),subV=(a,b)=>a.map((v,i)=>v-b[i]);
const mulV=(m,v)=>[0,1,2].map(i=>m[i*3]*v[0]+m[i*3+1]*v[1]+m[i*3+2]*v[2]);
const mulM=(a,b)=>Array.from({length:9},(_,i)=>[0,1,2].reduce((v,k)=>v+a[Math.floor(i/3)*3+k]*b[k*3+i%3],0));
const transpose=m=>[m[0],m[3],m[6],m[1],m[4],m[7],m[2],m[5],m[8]];
const mirror=v=>[-v[0],v[1],v[2]];
function eulerMatrix(v){const [x,y,z]=v.map((n,i)=>n*Math.PI/180*(i<2?-1:1)),cx=Math.cos(x),sx=Math.sin(x),cy=Math.cos(y),sy=Math.sin(y),cz=Math.cos(z),sz=Math.sin(z);return [cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx,sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx,-sy,cy*sx,cy*cx];}
function matrixEuler(m){const y=Math.asin(Math.max(-1,Math.min(1,-m[6]))),x=Math.atan2(m[7],m[8]),z=Math.atan2(m[3],m[0]);return [-x*180/Math.PI,-y*180/Math.PI,z*180/Math.PI];}
function sample(ch,t,fallback){if(!ch)return fallback;if(Array.isArray(ch))return ch;const keys=Object.keys(ch).map(Number).sort((a,b)=>a-b),get=k=>ch[Object.keys(ch).find(x=>+x===k)];if(t<=keys[0])return get(keys[0]);for(let i=1;i<keys.length;i++)if(t<=keys[i]){const f=(t-keys[i-1])/(keys[i]-keys[i-1]);return get(keys[i-1]).map((v,j)=>v+(get(keys[i])[j]-v)*f);}return get(keys.at(-1));}
function posed(death,tick){const map={};function get(name){if(!name)return {a:ident,p:[0,0,0],pivot:[0,0,0]};if(map[name])return map[name];const b=bones.find(b=>b.name===name),parent=get(b.parent),ch=death[name]||{},r=addV(b.rotation||[0,0,0],sample(ch.rotation,tick/20,[0,0,0])),s=sample(ch.scale,tick/20,[1,1,1]);return map[name]={a:mulM(parent.a,mulM(eulerMatrix(r),[s[0],0,0,0,s[1],0,0,0,s[2]])),p:addV(parent.p,mulV(parent.a,mirror(addV(subV(b.pivot,parent.pivot),sample(ch.position,tick/20,[0,0,0]))))),pivot:b.pivot};}for(const b of bones)get(b.name);return map;}
function subtreeBounds(death,name,tick,exclude=[]){const transforms=posed(death,tick),min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];for(const b of bones){let ancestor=b,skip=false;while(ancestor){if(exclude.includes(ancestor.name))skip=true;if(ancestor.name===name)break;ancestor=bones.find(x=>x.name===ancestor.parent);}if(!ancestor||skip)continue;const tr=transforms[b.name];for(const c of b.cubes)for(let i=0;i<8;i++){let p=c.origin.map((v,j)=>v+((i>>j)&1)*c.size[j]);if(c.rotation){const center=c.pivot||c.origin.map((v,j)=>v+c.size[j]/2);p=addV(mirror(center),mulV(eulerMatrix(c.rotation),mirror(subV(p,center))));}else p=mirror(p);p=addV(tr.p,mulV(tr.a,subV(p,mirror(b.pivot))));for(let j=0;j<3;j++){min[j]=Math.min(min[j],p[j]);max[j]=Math.max(max[j],p[j]);}}}return {min,max};}
function key(death,name,channel,tick,value){(death[name]??={})[channel]??={};death[name][channel][(tick/20).toFixed(2)]=value.map(v=>Math.round(v*1e6)/1e6);}
function land(death,name,tick,{x,z,y=.05,rotation,exclude=[]}={}){const b=bones.find(b=>b.name===name);if(rotation){const parent=b.parent?posed(death,tick)[b.parent]:{a:ident};let local=subV(matrixEuler(mulM(transpose(parent.a),eulerMatrix(rotation))),b.rotation||[0,0,0]);const keys=Object.keys(death[name]?.rotation||{}).map(Number).filter(t=>t<tick/20).sort((a,b)=>a-b),previous=keys.length?sample(death[name].rotation,keys.at(-1),[0,0,0]):[0,0,0];local=local.map((v,i)=>v+360*Math.round((previous[i]-v)/360));key(death,name,'rotation',tick,local);}const bounds=subtreeBounds(death,name,tick,exclude),delta=[x===undefined?0:x-(bounds.min[0]+bounds.max[0])/2,y-bounds.min[1],z===undefined?0:z-(bounds.min[2]+bounds.max[2])/2],parent=b.parent?posed(death,tick)[b.parent]:{a:ident};const local=mirror(mulV(transpose(parent.a),delta));key(death,name,'position',tick,addV(sample(death[name]?.position,tick/20,[0,0,0]),local));}
function animations(id){
 const quad=id==='shanjing_shanxiao',priest=id==='fufa_jijiu',heavy=id==='ludun_jiashi',result={};
 const put=(key,ticks,loop,b)=>result[`animation.${id}.${key}`]={loop,animation_length:ticks/20,bones:b};
 const idle={chest:rot([0,[0,0,0]],[30,[1.4,0,0]],[60,[0,0,0]])};
 if(priest)idle.root=pos([0,[0,1.6,0]],[30,[0,2.05,0]],[60,[0,1.6,0]]);
 if(!quad&&!heavy&&!priest){idle.waist_upper={rotation:[6,0,0]};idle.left_elbow={rotation:[-58,0,12]};}
 for(const [key,period,amp]of [['walk',32,heavy?15:quad?24:28],['run',20,heavy?22:quad?40:42]]){
  const b=JSON.parse(JSON.stringify(idle));b.chest=rot([0,[0,0,0]],[period/2,[1.4,0,0]],[period,[0,0,0]]);b.root=pos([0,[0,priest?1.6:0,0]],[period/4,[0,priest?2.1:.4,0]],[period/2,[0,priest?1.6:0,0]],[period*3/4,[0,priest?2.1:.4,0]],[period,[0,priest?1.6:0,0]]);
  for(const s of [-1,1]){const side=s<0?'right':'left';const cycle=[0,period/4,period/2,period*3/4,period];
   if(!priest){b[`${side}_thigh`]=channel(cycle.map((t,i)=>[t,[[0,amp,0,-amp,0][i]*s,0,0]]));b[`${side}_knee`]=channel(cycle.map((t,i)=>[t,[Math.max(0,[0,-amp,0,amp,0][i]*s)*1.3,0,0]]));
   b[`${side}_shoulder`]=channel(cycle.map((t,i)=>[t,[[0,-amp,0,amp,0][i]*s*(quad?1:.5),0,0]]));
   b[`${side}_elbow`]=channel(cycle.map((t,i)=>[t,[quad?Math.max(0,[0,amp,0,-amp,0][i]*s)*.75:-8,0,0]]));}
   if(priest)b[`${side}_sleeve_outer`]=channel(cycle.map((t,i)=>[t,[[0,5,0,-5,0][i],0,s*3]]));
  }put(key,period,true,b);
 }put('idle',60,true,idle);
 if(quad){const b={root:{position:[0,-1,0]},chest:rot([0,[0,0,0]],[3,[2,0,0]],[6,[0,0,0]],[9,[2,0,0]],[12,[0,0,0]])};for(const s of [-1,1]){const side=s<0?'right':'left',t=[0,3,6,9,12],wave=[0,1,0,-1,0];b[`${side}_shoulder`]=rot(...t.map((n,i)=>[n,[wave[i]*s*16,0,0]]));b[`${side}_elbow`]=rot(...t.map((n,i)=>[n,[-12-Math.max(0,wave[i]*s)*18,0,0]]));b[`${side}_thigh`]=rot(...t.map((n,i)=>[n,[-wave[i]*s*18,0,0]]));b[`${side}_knee`]=rot(...t.map((n,i)=>[n,[Math.max(0,-wave[i]*s)*24,0,0]]));}put('climb',12,true,b);}
 let attack,skill,total,skillTotal;
 if(id==='zuwu_daoshou'){
  total=36;attack={waist:rot([0,[0,0,0]],[8,[3,-28,0]],[12,[-6,28,0]],[18,[2,32,0]],[22,[0,-30,0]],[36,[0,0,0]]),right_shoulder:rot([0,[0,0,0]],[8,[35,-20,-23]],[12,[-78,10,22]],[18,[-70,-25,20]],[22,[-5,45,-60]],[36,[0,0,0]]),right_elbow:rot([0,[0,0,0]],[8,[-38,0,0]],[12,[-15,0,0]],[18,[-55,0,0]],[22,[-10,0,0]],[36,[0,0,0]]),right_wrist:rot([0,[0,0,0]],[12,[8,0,27]],[18,[-10,0,-24]],[22,[0,0,-48]],[36,[0,0,0]])};skill=attack;skillTotal=36;
 }else if(heavy){
  total=32;attack={waist:rot([0,[0,0,0]],[10,[-8,0,0]],[16,[16,0,0]],[23,[5,0,0]],[32,[0,0,0]]),shield:pos([0,[0,0,0]],[10,[0,0,1.6]],[16,[0,0,-3]],[24,[0,0,-1]],[32,[0,0,0]]),right_shoulder:rot([0,[0,0,0]],[16,[40,0,-15]],[24,[-62,0,0]],[32,[0,0,0]]),right_elbow:rot([0,[0,0,0]],[16,[-35,0,0]],[24,[-5,0,0]],[32,[0,0,0]])};skill=attack;skillTotal=32;
 }else if(priest){
  total=50;attack={right_shoulder:rot([0,[0,0,0]],[18,[-35,0,-18]],[24,[-58,0,5]],[26,[-40,0,-8]],[28,[-58,0,5]],[30,[-40,0,-8]],[32,[-58,0,5]],[50,[0,0,0]]),left_shoulder:rot([0,[0,0,0]],[18,[-30,0,35]],[32,[-35,0,40]],[50,[0,0,0]]),root:pos([0,[0,1.6,0]],[18,[0,2.7,0]],[32,[0,2.7,0]],[50,[0,1.6,0]])};
  skillTotal=40;skill={left_shoulder:rot([0,[0,0,0]],[20,[-75,0,32]],[29,[-75,0,32]],[40,[0,0,0]]),right_shoulder:rot([0,[0,0,0]],[20,[-25,0,-20]],[29,[-25,0,-20]],[40,[0,0,0]]),root:pos([0,[0,1.6,0]],[20,[0,3.4,0]],[28,[0,3.4,0]],[40,[0,1.6,0]])};
  for(let i=0;i<3;i++){attack[`talisman_${i}`]=rot([0,[0,0,0]],[18,[-18,0,0]],[24,[26,0,0]],[32,[20,0,0]],[50,[0,0,0]]);skill[`talisman_${i}`]=rot([0,[0,0,0]],[20,[-35,0,0]],[28,[22,0,0]],[40,[0,0,0]]);}
  put('buff',40,false,skill);
 }else{
  total=42;attack={chest:rot([0,[0,0,0]],[10,[12,0,0]],[14,[-18,0,0]],[22,[-12,0,0]],[24,[20,0,0]],[42,[0,0,0]]),root:pos([0,[0,0,0]],[10,[0,-1.5,0]],[14,[0,.4,0]],[22,[0,0,0]],[24,[0,-.8,0]],[42,[0,0,0]])};
  for(const side of ['left','right']){attack[`${side}_shoulder`]=rot([0,[0,0,0]],[10,[28,0,0]],[14,[-78,0,0]],[22,[-52,0,0]],[24,[24,0,0]],[42,[0,0,0]]);attack[`${side}_elbow`]=rot([0,[0,0,0]],[10,[-30,0,0]],[14,[-15,0,0]],[24,[0,0,0]],[42,[0,0,0]]);}
  skill=attack;skillTotal=42;
  put('rock',32,false,{chest:rot([0,[0,0,0]],[12,[-18,-20,0]],[18,[12,22,0]],[32,[0,0,0]]),right_shoulder:rot([0,[0,0,0]],[12,[-140,0,-15]],[18,[-50,0,5]],[32,[0,0,0]]),right_elbow:rot([0,[0,0,0]],[12,[-65,0,0]],[18,[0,0,0]],[32,[0,0,0]])});
 }
 put('attack',total,false,attack);put('skill',skillTotal,false,skill);
 put('hurt',10,false,{chest:rot([0,[0,0,0]],[3,[-12,0,7]],[10,[0,0,0]]),head:rot([0,[0,0,0]],[3,[-10,0,-8]],[10,[0,0,0]])});
 const death=quad?{root:rot([0,[0,0,0]],[12,[0,0,65]],[32,[0,0,86]]),chest:rot([0,[0,0,0]],[20,[20,0,0]],[32,[24,0,0]])}:heavy?{root:pos([0,[0,0,0]],[18,[0,-4.5,0]],[40,[0,-5,0]]),right_knee:rot([0,[0,0,0]],[18,[72,0,0]],[40,[72,0,0]]),head:rot([0,[0,0,0]],[20,[28,0,0]],[40,[28,0,0]])}:priest?{root:pos([0,[0,1.6,0]],[18,[0,0,0]],[40,[0,-7,0]]),chest:rot([0,[0,0,0]],[20,[45,0,0]],[40,[70,0,0]]),mask:pos([0,[0,0,0]],[16,[0,0,0]],[40,[0,-10,-6]])}:{root:pos([0,[0,0,0]],[16,[0,-5,0]],[40,[0,-8,0]]),waist:rot([0,[0,0,0]],[18,[20,0,0]],[40,[25,0,-65]]),head:rot([0,[0,0,0]],[18,[25,0,0]],[40,[25,0,0]]),right_knee:rot([0,[0,0,0]],[16,[80,0,0]],[40,[80,0,0]]),left_knee:rot([0,[0,0,0]],[16,[80,0,0]],[40,[80,0,0]]),helmet:{...pos([0,[0,0,0]],[18,[0,0,0]],[40,[7,-23,-1]]),...rot([0,[0,0,0]],[18,[0,0,0]],[40,[0,0,720]])}};
 if(id==='zuwu_daoshou')attack.right_shoulder.rotation['1.10']=[-112,45,-60];
 if(priest){
  // Only anatomy surface children shrink; the original clothing and mask hierarchy survives.
  death.root=pos([0,[0,1.6,0]],[12,[0,.8,0]],[28,[0,0,0]],[40,[0,0,0]]);
  delete death.chest;delete death.mask;
  for(const b of bones.filter(b=>b.name.startsWith('body_')))death[b.name]=scale([0,[1,1,1]],[8,[1,1,1]],[18,[.15,.15,.15]],[24,[.001,.001,.001]],[40,[.001,.001,.001]]);
  const cloth=[['robe_front',[88,0,0],0,-2],['robe_back',[-86,0,0],0,2],['left_robe_panel',[0,0,78],-3.3,.3],['right_robe_panel',[0,0,-78],3.3,.3],['chest_front',[84,0,0],0,-1.2],['chest_back',[-84,0,0],0,1.2],['left_sleeve_inner',[60,0,32],-4.5,.7],['right_sleeve_inner',[60,0,-32],4.5,.7],['left_sleeve_outer',[76,0,24],-6,-1.3],['right_sleeve_outer',[76,0,-24],6,-1.3],['beads',[85,0,0],0,-2.1],['crown',[70,0,20],-2.5,3.8],['staff',[86,0,-12],7,0]];
  for(const [name,r,x,z]of cloth){death[name]={...rot([0,[0,0,0]],[10,[0,0,0]]),...pos([0,[0,0,0]],[10,[0,0,0]])};if(name.includes('sleeve'))death[name].scale=frames([[0,[1,1,1]],[10,[1,1,1]],[34,[1,.42,.5]],[40,[1,.42,.5]]]);land(death,name,40,{rotation:r,x,z,y:.12});}
  for(const s of [-1,1]){const name=s<0?'mask_right':'mask_left';death[name]={...rot([0,[0,0,0]],[12,[0,0,0]],[22,[20,s*24,s*16]]),...pos([0,[0,0,0]],[12,[0,0,0]],[22,[s*1.8,-5,-1.5]])};land(death,name,34,{rotation:[86,s*12,s*8],x:s*2.6,z:-5,y:.08});land(death,name,40,{rotation:[88,s*12,s*8],x:s*2.9,z:-5.2,y:.05});}
 }
 if(id==='zuwu_daoshou'){
  death.root.rotation=frames([[0,[0,0,0]],[20,[0,0,0]],[40,[0,0,-78]]]);
  death.waist=rot([0,[0,0,0]],[18,[20,0,0]],[40,[25,0,-8]]);
  death.right_shoulder=rot([0,[0,0,0]],[8,[-30,0,-12]],[18,[-60,0,0]],[24,[-48,0,5]],[40,[8,0,18]]);
  death.right_elbow=rot([0,[0,0,0]],[8,[-75,0,0]],[18,[-25,0,0]],[24,[-35,0,0]],[40,[-10,0,0]]);
  death.right_wrist=rot([0,[0,0,0]],[8,[0,0,-20]],[18,[0,0,-10]],[40,[0,0,0]]);
  death.scabbard=rot([0,[0,0,0]],[18,[60,0,15]],[40,[60,0,15]]);
  death.dao={...rot([0,[0,0,0]],[8,[0,0,-20]]),...pos([0,[0,0,0]],[8,[0,0,0]])};
  // Release from the hand at impact; compensate the collapsing parent every authored tick.
  for(let tick=1;tick<=40;tick++)land(death,'root',tick,{y:.03,exclude:['dao','helmet','scabbard']});
  for(let tick=18;tick<=40;tick++)land(death,'dao',tick,{rotation:[0,0,0],x:4.4,z:-9,y:-.18});
  for(let tick=19;tick<=40;tick++)land(death,'helmet',tick,{rotation:[0,0,Math.max(0,tick-28)*60],x:-5-(tick-19)*.16,z:2.5,y:Math.max(.03,(28-tick)*1.4)});
 }
 if(quad){
  death.root={...pos([0,[0,0,0]],[12,[0,-.5,0]],[32,[0,0,0]]),...rot([0,[0,0,0]],[12,[0,0,45]],[32,[0,0,86]])};
  death.waist=rot([0,[0,0,0]],[14,[18,0,0]],[32,[32,0,0]]);
  death.chest=rot([0,[0,0,0]],[14,[25,0,0]],[32,[42,0,0]]);
  death.neck=rot([0,[0,0,0]],[14,[24,0,0]],[32,[42,0,0]]);
  death.head=rot([0,[0,0,0]],[14,[15,0,0]],[32,[26,0,0]]);
  for(const s of [-1,1]){const side=s<0?'right':'left';death[`${side}_shoulder`]=rot([0,[0,0,0]],[14,[-25,0,s*12]],[32,[-42,0,s*28]]);death[`${side}_elbow`]=rot([0,[0,0,0]],[14,[-65,0,0]],[32,[-112,0,0]]);death[`${side}_wrist`]=rot([0,[0,0,0]],[14,[20,0,0]],[32,[40,0,0]]);death[`${side}_thigh`]=rot([0,[0,0,0]],[14,[-48,0,0]],[32,[-78,0,0]]);death[`${side}_knee`]=rot([0,[0,0,0]],[14,[75,0,0]],[32,[120,0,0]]);death[`${side}_ankle`]=rot([0,[0,0,0]],[14,[-25,0,0]],[32,[-50,0,0]]);}
  death.tail=rot([0,[0,0,0]],[14,[28,0,0]],[32,[68,0,0]]);death.tail_hook=rot([0,[0,0,0]],[14,[18,0,0]],[32,[30,0,0]]);
  for(let tick=1;tick<=32;tick++)land(death,'root',tick,{y:.03});
 }
 if(quad)attack.root.position['1.20']=[0,.3,0];
 if(heavy){
  death.root=pos([0,[0,0,0]],[18,[0,-3.7,0]],[40,[0,-4,0]]);
  death.right_knee=rot([0,[0,0,0]],[18,[90,0,0]],[40,[90,0,0]]);
  death.left_thigh=rot([0,[0,0,0]],[18,[-30,0,0]],[40,[-30,0,0]]);
  death.left_knee=rot([0,[0,0,0]],[18,[90,0,0]],[40,[90,0,0]]);
  death.left_ankle=rot([0,[0,0,0]],[18,[-60,0,0]],[40,[-60,0,0]]);
  death.shield=pos([0,[0,0,0]],[18,[0,3,0]],[40,[0,3.3,0]]);
  // Reparented living armour follows each thigh. Death retains the original pelvis-relative
  // cover silhouette, independently of the new passive layer, at every authored tick.
  for(const side of ['left','right']){const name=`${side}_hip_plate`,b=bones.find(b=>b.name===name),parent=b.parent;for(let tick=0;tick<=40;tick++){
   const saved=death[name];delete death[name];b.parent='pelvis';const desired=posed(death,tick)[name];b.parent=parent;if(saved)death[name]=saved;
   const p=posed(death,tick)[parent];key(death,name,'rotation',tick,matrixEuler(mulM(transpose(p.a),desired.a)));key(death,name,'position',tick,subV(mirror(mulV(transpose(p.a),subV(desired.p,p.p))),subV(b.pivot,p.pivot)));
  }}
 }
 put('death',quad?32:40,'hold_on_last_frame',death);return {format_version:'1.8.0',animations:result};
}
fs.mkdirSync(`${base}/geo/blueprint`,{recursive:true});fs.mkdirSync(`${base}/animations/blueprint`,{recursive:true});fs.mkdirSync(out,{recursive:true});
const report=[];
for(const [id,build]of Object.entries({zuwu_daoshou:soldier,ludun_jiashi:shieldman,fufa_jijiu:priest,shanjing_shanxiao:beast})){
 const im=start(id);build();const names=new Set(bones.map(b=>b.name));assert.equal(names.size,bones.length);for(const b of bones){if(b.parent)assert(names.has(b.parent),b.name);for(const c of b.cubes){assert(c.size.every(n=>n>0));for(const f of Object.values(c.uv)){assert(f.uv[0]>=0&&f.uv[1]>=0&&f.uv[0]+f.uv_size[0]<=im.w&&f.uv[1]+f.uv_size[1]<=im.h);for(let y=f.uv[1];y<f.uv[1]+f.uv_size[1];y++)for(let x=f.uv[0];x<f.uv[0]+f.uv_size[0];x++)assert(im.c!==4||im.data[(y*im.w+x)*im.c+3]>=250,'Transparent UV pixel');}}}
 const geo={format_version:'1.12.0','minecraft:geometry':[{description:{identifier:`geometry.${id}`,texture_width:im.w,texture_height:im.h,visible_bounds_width:4,visible_bounds_height:4,visible_bounds_offset:[0,1.4,0]},bones}]},anim=animations(id);
 for(const [key,a]of Object.entries(anim.animations))for(const [n,channels]of Object.entries(a.bones)){assert(names.has(n),`${key}: ${n}`);for(const ch of Object.values(channels)){if(Array.isArray(ch))assert(ch.every(Number.isFinite));else for(const [t,v]of Object.entries(ch)){assert(+t>=0&&+t<=a.animation_length,`${key}: time ${t}`);assert(v.every(Number.isFinite));}}}
 if(id!=='shanjing_shanxiao')for(const side of ['left','right'])for(const joint of ['shoulder','upper_arm','elbow','forearm','wrist','hand','thigh','knee','shin','ankle','foot'])assert(names.has(`${side}_${joint}`));
 const impacts={zuwu_daoshou:[12,22],ludun_jiashi:[16],fufa_jijiu:[24,28,32],shanjing_shanxiao:[14,24]}[id];
 for(const t of impacts)assert(Object.values(anim.animations[`animation.${id}.attack`].bones).some(b=>Object.values(b).some(c=>Object.hasOwn(c,(t/20).toFixed(2)))),`${id}: missing contact/launch ${t}`);
 fs.writeFileSync(`${base}/geo/blueprint/${id}.geo.json`,JSON.stringify(geo,null,2)+'\n');fs.writeFileSync(`${base}/animations/blueprint/${id}.animation.json`,JSON.stringify(anim,null,2)+'\n');
 const faces=bones.flatMap(b=>b.cubes).flatMap(c=>Object.values(c.uv)),nativePatchFaces=faces.filter(f=>f.uv_size[0]*f.uv_size[1]>1).length;
 report.push({id,texture:`textures/entity/${atlasNames[id]}.png`,bones:bones.length,cubes:bones.reduce((n,b)=>n+b.cubes.length,0),animations:Object.keys(anim.animations).length,uv_patches:uvMap,native_patch_faces:nativePatchFaces,total_faces:faces.length,visual_review_file:'REVIEW.txt',runtime_verified:false});
}
fs.writeFileSync(`${out}/model-manifest.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.map(({id,bones,cubes,animations})=>({id,bones,cubes,animations})),null,2));
// The existing internal-injury sigil is already original pixel art for blood magic.
fs.copyFileSync(`${base}/textures/mob_effect/internal_injury.png`,`${base}/textures/mob_effect/bingsha_possession.png`);
