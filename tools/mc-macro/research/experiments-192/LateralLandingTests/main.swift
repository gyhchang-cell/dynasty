import Foundation
let rows=try JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [[String:Any]]
precondition(!rows.isEmpty)
for row in rows {
    let p=row["p"] as! [Double],v=row["v"] as! [Double]
    let pose=F3Pose(x:p[0],y:p[1],z:p[2],yaw:35,pitch:86,time:0)
    let blocks=Set((row["solid"] as! [[Int]]).map{F3Block(x:$0[0],y:$0[1],z:$0[2])})
    let state=BridgeWorldState(pose:pose,renderPose:pose,previousPose:pose,velocity:(v[0],v[1],v[2]),onGround:false,flying:false,hasBlocks:true,world:1,tick:1,face:nil,solid:blocks,useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
    let target=F3Block(x:134009,y:79,z:-8)
    let coast=BridgeLandingForecast.predict(state,height:80,yaw:-135,acceleration:0)!
    precondition(coast.z<Double(target.z)-0.3,"Recorded uncorrected foot loses support")
    let yaw=BridgeLateralLanding.direction(state,floor:79,heading:-135,targets:[target])!
    precondition(abs(abs(F3Pose.angle(yaw+135))-90)<0.001,"Only perpendicular acceleration is allowed")
    let adjusted=BridgeLandingForecast.predict(state,height:80,yaw:yaw,acceleration:0.02)!
    precondition(adjusted.x>Double(target.x)-0.28 && adjusted.x<Double(target.x+1)+0.28)
    precondition(adjusted.z>Double(target.z)-0.28 && adjusted.z<Double(target.z+1)+0.28)
    precondition(BridgeLateralLanding.direction(state,floor:79,heading:-135,targets:[])==nil)
    print("Recorded NE correction: coast \(coast.x),\(coast.z), adjusted \(adjusted.x),\(adjusted.z), lateral yaw \(yaw)")
}
