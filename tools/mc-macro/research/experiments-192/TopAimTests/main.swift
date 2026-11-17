import Foundation
func check(_ value:Bool,_ why:String) {if !value {fatalError(why)}}
var count=0
for yaw in [-135.0,-45,45,135] {
 let r=yaw * .pi/180,ux = -sin(r),uz=cos(r)
 for distance in [0.8,1.2,1.8] {
  for offset in [-0.3,0.0,0.3] {
   let block=F3Block(x:65986,y:89,z:-15)
   let target=TellyPlacement(support:block,result:F3Block(x:block.x,y:90,z:block.z),axis:1,sign:1,x:65986.5,y:90,z:-14.5)
   let x=65986.5+ux*distance+uz*offset,z = -14.5+uz*distance-ux*offset
   let poses=[F3Pose(x:x,y:91.0013,z:z,yaw:yaw,pitch:45,time:0),F3Pose(x:x-ux*0.15,y:90.85,z:z-uz*0.15,yaw:yaw,pitch:45,time:0)]
   guard let aim=target.sharedTopAim(from:poses,preferredYaw:F3Pose.angle(yaw+180),eyeHeight:1.62) else {fatalError("missing shared top \(yaw),\(distance),\(offset)")}
   check(poses.allSatisfy{target.isVisibleFace(from:F3Pose(x:$0.x,y:$0.y,z:$0.z,yaw:aim.yaw,pitch:aim.pitch,time:0))},"shared ray must hit UP from both actual eye positions")
   count+=1
  }
 }
}
let target=TellyPlacement(support:F3Block(x:0,y:79,z:0),result:F3Block(x:0,y:80,z:0),axis:1,sign:1,x:0.5,y:80,z:0.5)
check(target.sharedTopAim(from:[F3Pose(x:2,y:78,z:2,yaw:0,pitch:0,time:0)],preferredYaw:135,eyeHeight:1.62)==nil,"an eye below the top cannot hit UP")
check(target.sharedTopAim(from:[],preferredYaw:0,eyeHeight:1.62)==nil,"missing observations must not invent an aim")
print("PASS \(count) shared top windows across four directions and off-centre starts; invalid input rejected")
