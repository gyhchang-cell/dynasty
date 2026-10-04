// Original Dynasty sculpture. Bedrock geometry is directly editable with Blockbench's GeckoLib format.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const bones=[];
function bone(name,parent,pivot,cubes=[],rotation) {const b={name,pivot,cubes};if(parent)b.parent=parent;if(rotation)b.rotation=rotation;bones.push(b);return name;}
function box(x,y,z,w,h,d,material=0,rotation,pivot) {
  const origin=[x,y,z],size=[w,h,d],uv={};
  const tile=[[0,0],[32,0],[0,32],[32,32]][material];
  for(const face of ['north','south','east','west','up','down'])uv[face]={uv:[tile[0]+1,tile[1]+1],uv_size:[30,30]};
  const b={origin,size,uv};if(rotation){b.rotation=rotation;b.pivot=pivot??[x+w/2,y+h/2,z+d/2];}return b;
}
bone('root',null,[0,0,0]);
bone('seal_core','root',[0,24,0],[box(-13,11,-13,26,26,26,0,[0,0,45]),box(-9,15,-15,18,18,30,1,[0,0,45]),box(-5,19,-17,10,10,34,3,[0,0,45])]);
bone('pelvis','root',[0,31,1],[box(-9,27,-6,18,10,14,0),box(-11,33,-7,22,3,15,1)]);
bone('abdomen','pelvis',[0,37,0],[box(-6,35,-5,12,10,11,2)]);
bone('spine_01','abdomen',[0,39,2],[box(-7,39,-5,14,7,13,0)]);
bone('spine_02','spine_01',[0,44,2],[box(-10,44,-7,20,9,16,0)]);
bone('chest','spine_02',[0,50,2],[box(-15,49,-9,30,13,21,0),box(-12,59,-7,24,5,16,2)]);
for(let s of [-1,1]) {
  const side=s<0?'right':'left';
  bone('chest_armor_'+side,'chest',[s*7,56,-8],[box(s*7-7,49,-12,14,13,5,0,[0,0,s*-12]),box(s*7-6,59,-13,12,3,5,1,[0,0,s*-12])]);
  for(let i=0;i<3;i++)bone(side+'_rib_'+i,'spine_02',[s*8,44+i*4,-7],[box(s*8-4,43+i*4,-9,8,2,3,1,[0,0,s*18])]);
  bone(side+'_hip_plate','pelvis',[s*9,33,0],[box(s*10-5,21,-7,10,14,3,0,[0,0,s*-16]),box(s*10-5,21,-8,10,2,4,1,[0,0,s*-16])]);
  const x=s*20;
  bone(side+'_shoulder','chest',[s*15,58,1],[box(x-6,53,-6,12,10,14,2)]);
  bone(side+'_shoulder_armor',side+'_shoulder',[x,61,1],[box(x-9,60,-10,18,6,22,0,[0,0,s*14]),box(x-9,65,-10,18,2,22,1,[0,0,s*14]),box(x-7,54,-11,14,5,22,0,[0,0,s*22])]);
  for(let i=0;i<3;i++)bone(side+'_shoulder_spike_'+i,side+'_shoulder_armor',[x+s*(3+i*3),64,2],[box(x+s*(3+i*3)-1,64,0,2,9-i,4,1,[0,0,-s*(20+i*13)])]);
  bone(side+'_upper_arm',side+'_shoulder',[x,55,0],[box(x-4,42,-4,8,15,10,2)]);
  bone(side+'_elbow',side+'_upper_arm',[x,42,0],[box(x-5,38,-5,10,7,12,1)]);
  bone(side+'_forearm',side+'_elbow',[x,40,0],[box(x-6,26,-7,12,14,15,0),box(x-6,26,-8,12,3,16,1),box(x-3,31,-9,6,7,3,2)]);
  bone(side+'_wrist',side+'_forearm',[x,26,0],[box(x-4,23,-4,8,5,9,1)]);
  bone(side+'_hand',side+'_wrist',[x,24,-1],[box(x-6,16,-6,12,9,12,0),box(x-5,17,-8,10,6,2,1)]);
  for(let i=1;i<=3;i++) {
    let cx=x+(i-2)*4;
    bone(side+'_claw_0'+i,side+'_hand',[cx,18,-5],[box(cx-1.5,10,-7,3,9,4,0,[12,0,0]),box(cx-1,7,-9,2,5,3,1,[28,0,0])]);
  }
  bone(side+'_thumb',side+'_hand',[x-s*6,22,0],[box(x-s*8-1.5,16,-4,3,7,4,1,[0,0,s*35])]);
  let lx=s*8;
  bone(side+'_thigh','pelvis',[lx,30,2],[box(lx-5,18,-4,10,13,13,2)]);
  bone(side+'_knee',side+'_thigh',[lx,19,0],[box(lx-5,15,-7,10,7,6,0,[0,0,12*s]),box(lx-2,17,-9,4,4,3,1)]);
  bone(side+'_shin',side+'_knee',[lx,17,1],[box(lx-4,5,-4,8,13,10,0),box(lx-3,7,-6,6,11,3,1)]);
  bone(side+'_ankle',side+'_shin',[lx,6,1],[box(lx-3,3,-4,6,4,9,2)]);
  bone(side+'_foot',side+'_ankle',[lx,4,0],[box(lx-5,0,-10,10,5,16,0)]);
  for(let i=0;i<3;i++)bone(side+'_toe_'+i,side+'_foot',[lx-3+i*3,2,-8],[box(lx-4+i*3,0,-13,2,3,6,1,[10,0,0])]);
}
bone('core','chest',[0,54,-12],[box(-4,50,-15,8,8,4,3,[0,0,45]),box(-5,49,-13,10,10,2,1,[0,0,45])]);
bone('back_structure','chest',[0,56,11],[box(-9,46,10,18,16,5,0),box(-2,43,14,4,25,3,1)]);
for(let s of [-1,1]) {
  const side=s<0?'right':'left';
  bone(side+'_back_blade','back_structure',[s*7,53,13],[box(s*17-3,45,13,6,34,4,0,[0,0,-s*30]),box(s*17-2,45,12,4,34,2,1,[0,0,-s*30])]);
  for(let i=0;i<3;i++)bone(side+'_back_fin_'+i,side+'_back_blade',[s*(13+i*4),62-i*7,13],[box(s*(13+i*4)-2,52-i*6,14,4,17,3,0,[0,0,-s*40])]);
}
bone('neck','chest',[0,63,0],[box(-4,62,-3,8,6,8,2)]);
bone('neck_armor','neck',[0,64,0],[box(-6,62,-5,12,3,12,1)]);
bone('main_head','neck',[0,68,0],[box(-5,65,-5,10,10,11,0),box(-4,70,-7,8,5,4,0)]);
bone('face_armor','main_head',[0,70,-6],[box(-3,68,-10,6,5,5,0),box(-1,69,-12,2,5,3,1),box(-4,72,-9,8,2,3,1)]);
bone('jaw','main_head',[0,67,-3],[box(-4,64,-9,8,3,8,0),box(-3,62,-8,6,2,4,1)]);
for(let s of [-1,1]) {
 const side=s<0?'right':'left';
 bone(side+'_face_armor','main_head',[s*4,69,-5],[box(s*4-2,65,-8,4,8,4,1,[0,0,-s*14])]);
 bone(side+'_eye','main_head',[s*2.8,70,-10],[box(s*2.8-1.5,70,-10.5,3,1,1,3,[0,0,s*10])]);
 bone(side+'_horn','main_head',[s*4,74,1],[box(s*4-1.5,73,-1,3,10,4,1)],[0,0,-s*30]);
 bone(side+'_horn_tip',side+'_horn',[s*4,82,1],[box(s*4-1,81,-.5,2,7,3,0)],[0,0,s*15]);
 bone(side+'_jaw_fang','jaw',[s*3,66,-9],[box(s*3-.6,65,-10,1.2,4,1.5,1,[0,0,-s*10])]);
}
bone('rear_horn','main_head',[0,74,5],[box(-1.5,73,4,3,9,4,1,[25,0,0])]);
const names=new Set(bones.map(b=>b.name));assert.equal(names.size,bones.length);
for(const b of bones)if(b.parent)assert(names.has(b.parent));
assert(bones.length>85);
const resource='src/main/resources/assets/dynasty';
fs.mkdirSync(`${resource}/geo`,{recursive:true});fs.mkdirSync(`${resource}/animations`,{recursive:true});
fs.writeFileSync(`${resource}/geo/zhenyuan_sovereign.geo.json`,JSON.stringify({format_version:'1.12.0','minecraft:geometry':[{description:{identifier:'geometry.zhenyuan_sovereign',texture_width:64,texture_height:64,visible_bounds_width:10,visible_bounds_height:9,visible_bounds_offset:[0,3,0]},bones}]},null,2));
const idle={chest:{rotation:["math.sin(query.anim_time * 90) * 1.1",0,0]},jaw:{rotation:["2 + math.sin(query.anim_time * 90)",0,0]}};
const walk={root:{position:[0,"math.abs(math.sin(query.anim_time * 240)) * 1.2",0]},spine_01:{rotation:[0,"math.sin(query.anim_time * 240) * 3",0]}};
for(const [side,sign] of [['left',1],['right',-1]]) {
 idle[side+'_shoulder']={rotation:["math.sin(query.anim_time * 90) * 1.2",0,sign*9]};
 idle[side+'_elbow']={rotation:[-12,0,0]};
 walk[side+'_thigh']={rotation:[`math.sin(query.anim_time * 240) * ${sign*20}`,0,0]};
 walk[side+'_knee']={rotation:[`math.max(0, math.sin(query.anim_time * 240) * ${sign*24})`,0,0]};
 walk[side+'_foot']={rotation:[`math.sin(query.anim_time * 240) * ${-sign*9}`,0,0]};
 walk[side+'_shoulder']={rotation:[`math.sin(query.anim_time * 240) * ${-sign*12}`,0,sign*9]};
 walk[side+'_elbow']={rotation:[-12,0,0]};
}
fs.writeFileSync(`${resource}/animations/zhenyuan_sovereign.animation.json`,JSON.stringify({format_version:'1.8.0',animations:{'animation.sovereign.idle':{loop:true,animation_length:4,bones:idle},'animation.sovereign.walk':{loop:true,animation_length:1.5,bones:walk}}},null,2));
console.log(`Original sovereign: ${bones.length} bones, ${bones.reduce((n,b)=>n+b.cubes.length,0)} cuboids; height 87/16 blocks.`);
