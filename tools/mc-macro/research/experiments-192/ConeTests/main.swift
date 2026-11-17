import Foundation
let target=TellyPlacement(support:F3Block(x:94002,y:79,z:-1),result:F3Block(x:94002,y:80,z:-1),axis:1,sign:1,x:94002.5,y:80,z:-0.5)
let data=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
let cases=try JSONSerialization.jsonObject(with:data) as! [[String:Any]]
var checked=0
for c in cases {
    let p=c["p"] as! [Double],v=c["v"] as! [Double],desired=c["desired"] as! [Double]
    let eye=F3Pose(x:p[0],y:p[1],z:p[2],yaw:desired[0],pitch:desired[1],time:0)
    let next=F3Pose(x:p[0]+v[0],y:p[1]+v[1],z:p[2]+v[2],yaw:desired[0],pitch:desired[1],time:0.05)
    guard let aim=TopFaceCone.aim(target:target,eyes:[eye,next],eyeHeight:1.62,desiredYaw:desired[0],desiredPitch:desired[1]) else {fatalError("No cone for recorded reachable top")}
    for p in [eye,next] {
        let view=F3Pose(x:p.x,y:p.y,z:p.z,yaw:aim.yaw,pitch:aim.pitch,time:p.time)
        assert(target.isVisibleFace(from:view))
        let hit=BridgeRay.intersection(block:target.support,pose:view)!
        assert(hit.axis==1 && hit.sign==1)
    }
    checked+=1
}
assert(checked>=4)
print("Recorded top-face click window: \(checked) frame pairs preserve target face")
