import Foundation
let data=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
let d=try JSONSerialization.jsonObject(with:data) as! [String:Any]
let p=d["p"] as! [Double],v=d["v"] as! [Double]
var x=p[0]-107012,z=p[2]-12,dx=v[0],dz=v[2],yaw = -45.0,b=F3Block(x:0,y:88,z:0)
for _ in 0..<4 {
    let pose=F3Pose(x:x,y:p[1],z:z,yaw:yaw,pitch:45,time:0)
    let state=BridgeWorldState(pose:pose,renderPose:pose,previousPose:pose,velocity:(dx,v[1],dz),onGround:false,flying:false,hasBlocks:true,world:1,tick:1,face:nil,solid:[b],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
    let f=BridgeLandingForecast.predict(state,height:89,yaw:yaw,acceleration:0.026)!
    let ux = -sin(yaw * .pi/180),uz=cos(yaw * .pi/180)
    func past(_ x:Double,_ z:Double)->(Double,Double) {(ux>0 ? x-Double(b.x+1):Double(b.x)-x,uz>0 ? z-Double(b.z+1):Double(b.z)-z)}
    let before=past(x,z),after=past(f.x,f.z)
    assert(before.0<0.10 && before.1<0.10)
    assert(f.seconds<=0.051 && after.0>0.10 && after.1>0.10)
    (x,z)=(-z,x);(dx,dz)=(-dz,dx);b=F3Block(x:-b.z-1,y:b.y,z:b.x);yaw+=90
}
print("Recorded prelanding corner: all four rotations detect the actual landing overhang")
