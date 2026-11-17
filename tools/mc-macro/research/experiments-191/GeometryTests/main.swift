import Foundation
func check(_ value:Bool,_ why:String) {if !value {fatalError(why)}}
let block=F3Block(x:0,y:79,z:0)
var windows=0
for quarter in 0..<4 {
    let a=Double(quarter)*Double.pi/2
    func rotate(_ x:Double,_ z:Double)->(Double,Double) {
        (0.5+(x-0.5)*cos(a)-(z-0.5)*sin(a),0.5+(x-0.5)*sin(a)+(z-0.5)*cos(a))
    }
    let result=rotate(1.5,0.5),face=rotate(1,0.5)
    let axis=quarter%2==0 ? 0:2, sign=quarter<2 ? 1:-1
    let placement=TellyPlacement(support:block,result:F3Block(x:Int(floor(result.0)),y:79,z:Int(floor(result.1))),axis:axis,sign:sign,x:face.0,y:79.65,z:face.1)
    for step in 0..<36 {
        let d=Double(step)/100
        let samples=[(1.9+d,81.17,-0.7-d),(1.7+d,81.00,-0.5-d),(1.98+d,81.18,-0.78-d)]
        let poses=samples.map {v->F3Pose in let p=rotate(v.0,v.2);return F3Pose(x:p.0,y:v.1,z:p.1,yaw:45+Double(quarter)*90,pitch:75,time:0)}
        if let aim=placement.sharedSideAim(from:poses,yaw:45+Double(quarter)*90,eyeHeight:1.62) {
            windows+=1
            for p in poses {
                let ray=F3Pose(x:p.x,y:p.y,z:p.z,yaw:aim.yaw,pitch:aim.pitch,time:0)
                check(placement.isVisibleFace(from:ray),"common aim must hit same side from all three eye positions")
            }
        }
    }
    let inside=F3Pose(x:0.5,y:80,z:0.5,yaw:0,pitch:80,time:0)
    check(placement.sharedSideAim(from:[inside],yaw:0,eyeHeight:1.62)==nil,"hidden side must not produce a click window")
}
check(windows>=100,"mirrored corner windows must actually be exercised")
print("PASS shared side windows: \(windows), four orientations, three eye positions per case; hidden faces rejected")
