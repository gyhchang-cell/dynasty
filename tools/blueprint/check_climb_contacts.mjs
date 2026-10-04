// Read-only local resource/CCD check; does not substitute for the actual wall-collision client QA.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as T from '/Users/a15356015027/Documents/Codex/2026-09-18/ni/outputs/dragon-ruin/node_modules/three/build/three.module.js';
import {applyClimbPose} from './climb_ik_math.mjs';
const res='src/main/resources/assets/dynasty',geo=JSON.parse(fs.readFileSync(res+'/geo/blueprint/shanjing_shanxiao.geo.json'))['minecraft:geometry'][0],anim=JSON.parse(fs.readFileSync(res+'/animations/blueprint/shanjing_shanxiao.animation.json')).animations['animation.shanjing_shanxiao.climb'];
function sample(c,t){if(!c)return[0,0,0];if(Array.isArray(c))return c;const k=Object.keys(c).map(Number).sort((a,b)=>a-b),get=k=>c[Object.keys(c).find(x=>+x===k)];for(let i=1;i<k.length;i++)if(t<=k[i]){let u=(t-k[i-1])/(k[i]-k[i-1]);return get(k[i-1]).map((v,j)=>v+(get(k[i])[j]-v)*u);}return get(k.at(-1));}
let maxError=0,minDistance=100,maxDistance=-100,minNormal=1;
for(let tick=0;tick<12;tick++){
 const g={};for(const b of geo.bones){const o=new T.Object3D(),p=b.parent?geo.bones.find(x=>x.name===b.parent).pivot:[0,0,0],r=sample(anim.bones[b.name]?.rotation,tick/20),off=sample(anim.bones[b.name]?.position,tick/20);o.position.set(-(b.pivot[0]-p[0]+off[0]),b.pivot[1]-p[1]+off[1],b.pivot[2]-p[2]+off[2]);o.rotation.set(...r.map((v,i)=>(v+(b.rotation?.[i]||0))*Math.PI/180*(i<2?-1:1)),'ZYX');if(b.parent)g[b.parent].add(o);g[b.name]=o;}
 const result=applyClimbPose(T,g,tick);let near=0;
 for(const q of result){maxError=Math.max(maxError,q.error);const distance=.02+q.y/16;minDistance=Math.min(minDistance,distance);maxDistance=Math.max(maxDistance,distance);if(distance<=.06)near++;const bone=g[q.leg.replace(/F$/,'_claw_contact').replace(/H$/,'_foot_contact')],normal=new T.Vector3(0,1,0).applyQuaternion(bone.getWorldQuaternion(new T.Quaternion())).y;minNormal=Math.min(minNormal,normal);assert(distance>=-.04&&distance<=.16,`tick ${tick} ${q.leg} distance ${distance}`);}
 assert(near>=2,`tick ${tick}: only ${near} near contacts`);
}
console.log(JSON.stringify({frames:12,contacts:48,maxError,minDistance,maxDistance,minNormal},null,2));
