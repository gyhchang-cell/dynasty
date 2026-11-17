import Foundation
let data=try Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))
let cases=try JSONSerialization.jsonObject(with:data) as! [[String:Any]]
var shared=0,upcoming=0,unreachable=0
for c in cases {
    let p=c["p"] as! [Double],v=c["v"] as! [Double],a=c["angle"] as! [Double]
    let b=c["support"] as! [Int],r=c["result"] as! [Int]
    let axis=c["axis"] as! Int,sign=c["sign"] as! Int,height=c["eye"] as! Double
    let target=TellyPlacement(support:F3Block(x:b[0],y:b[1],z:b[2]),result:F3Block(x:r[0],y:r[1],z:r[2]),axis:axis,sign:sign,
        x:Double(b[0])+(axis==0 ? (sign>0 ? 1:0):0.5),y:Double(b[1])+0.65,z:Double(b[2])+(axis==2 ? (sign>0 ? 1:0):0.5))
    let eye=F3Pose(x:p[0],y:p[1],z:p[2],yaw:a[0],pitch:a[1],time:0)
    let next=F3Pose(x:p[0]+v[0],y:p[1]+((c["ground"] as! Bool) ? 0:v[1]),z:p[2]+v[2],yaw:a[0],pitch:a[1],time:0.05)
    var eyes=[eye,next]
    var answer=SideFaceCone.aim(target:target,eyes:eyes,eyeHeight:height,desiredYaw:a[0],desiredPitch:a[1])
    if answer != nil {shared+=1}
    else {
        eyes=[next]
        answer=SideFaceCone.aim(target:target,eyes:eyes,eyeHeight:height,desiredYaw:a[0],desiredPitch:a[1])
        if answer != nil {upcoming+=1} else {unreachable+=1}
    }
    guard let answer else {continue}
    for p in eyes {
        let view=F3Pose(x:p.x,y:p.y,z:p.z,yaw:answer.yaw,pitch:answer.pitch,time:p.time)
        precondition(target.isVisibleFace(from:view,eyeHeight:height),"Solver returned wrong face for \(c)")
    }
}
precondition(shared>100 && cases.count>=200)
print("Recorded side-face pairs: shared=\(shared), next-only=\(upcoming), unavailable=\(unreachable); every returned ray hits intended face")
