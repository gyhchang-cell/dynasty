// Read-only counterpart of the client's two-link wall IK; preserves real palm/sole orientation.
export function applyClimbPose(T,groups,tick,speed=.22){
 const phase=(tick%6)/6,results=[],point=o=>o.getWorldPosition(new T.Vector3());
 const aim=(joint,end,target,component)=>{
  groups.root.updateMatrixWorld(true);const p=point(joint),a=point(end).sub(p),b=target.clone().sub(p),axis=component==='x'?new T.Vector3(1,0,0).applyQuaternion(joint.getWorldQuaternion(new T.Quaternion())):new T.Vector3(0,0,1).applyQuaternion(joint.parent.getWorldQuaternion(new T.Quaternion()));axis.normalize();a.addScaledVector(axis,-a.dot(axis));b.addScaledVector(axis,-b.dot(axis));joint.rotation[component]+=Math.atan2(axis.dot(a.clone().cross(b)),a.dot(b));
 };
 for(let side=0;side<2;side++)for(let rear=0;rear<2;rear++){
  const prefix=side?'left':'right',p=(phase+(side===rear?0:.5))%1,c=rear?4.85:-10.45;
  const z=p<.5?c-3.5+16*p*6*speed:(c+3.5)*(1-(p-.5)*2)+(c-3.5)*((p-.5)*2);
  const target=new T.Vector3((side?-1:1)*(rear?2.8:5.4),.16+(p<.5?0:Math.sin(Math.PI*(p-.5)*2)*1.28),Math.max(c-3.6,Math.min(c+3.6,z)));
  const parts=rear?['thigh','knee','ankle']:['shoulder','elbow','wrist'],j=parts.map(n=>groups[prefix+'_climb_'+n]),end=groups[prefix+(rear?'_foot_contact':'_claw_contact')];
  const wristTarget=target.clone().add(new T.Vector3(0,rear?1.72:1.95,rear?1.95:4.85));
  for(let iteration=0;iteration<6;iteration++){
   groups.root.updateMatrixWorld(true);const a=point(j[0]),b=point(j[1]),d=point(j[2]),l1=a.distanceTo(b),l2=b.distanceTo(d),dir=wristTarget.clone().sub(a),len=Math.max(.001,Math.min(l1+l2-.002,dir.length()));dir.normalize();const bend=new T.Vector3(0,0,rear?1:-1);bend.addScaledVector(dir,-bend.dot(dir)).normalize();const along=(len*len+l1*l1-l2*l2)/(2*len),height=Math.sqrt(Math.max(0,l1*l1-along*along)),elbowTarget=a.clone().addScaledVector(dir,along).addScaledVector(bend,height);
   for(let repeat=0;repeat<3;repeat++){aim(j[0],j[1],elbowTarget,'x');aim(j[0],j[1],elbowTarget,'z');}aim(j[1],j[2],wristTarget,'x');
   groups.root.updateMatrixWorld(true);const parentQ=j[2].parent.getWorldQuaternion(new T.Quaternion());j[2].quaternion.copy(parentQ.invert());
  }
  groups.root.updateMatrixWorld(true);const at=point(end),normal=new T.Vector3(0,1,0).applyQuaternion(end.getWorldQuaternion(new T.Quaternion())).y;results.push({leg:prefix+(rear?'H':'F'),stance:p<.5,error:at.distanceTo(target),y:at.y,normal});
 }
 return results;
}
