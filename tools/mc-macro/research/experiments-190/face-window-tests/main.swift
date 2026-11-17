import Foundation

func require(_ value:Bool,_ message:String) {if !value {fatalError(message)}}
let block=F3Block(x:0,y:79,z:0)
for quarter in 0..<4 {
    let rotation=Double(quarter)*90, a=rotation * .pi/180
    func rotated(_ x:Double,_ z:Double)->(Double,Double) {
        (0.5+(x-0.5)*cos(a)-(z-0.5)*sin(a),0.5+(x-0.5)*sin(a)+(z-0.5)*cos(a))
    }
    func eye(_ x:Double,_ y:Double,_ z:Double,_ pitch:Double=0)->F3Pose {
        let point=rotated(x,z)
        return F3Pose(x:point.0,y:y,z:point.1,yaw:127+rotation,pitch:pitch,time:0)
    }
    let point=rotated(1,0.5), result=rotated(1.5,0.5)
    let axis=quarter%2==0 ? 0:2, sign=quarter<2 ? 1:-1
    let target=TellyPlacement(support:block,result:F3Block(x:Int(floor(result.0)),y:79,z:Int(floor(result.1))),
                              axis:axis,sign:sign,x:point.0,y:79.65,z:point.1)
    let rendered=eye(1.23,80.4,0.54), logical=eye(1.31,80.1,0.62)
    require(target.sidePitchWindow(eyes:[rendered,logical],yaw:rendered.yaw,eyeHeight:1.62)==nil,
            "Near-corner descent can have no common logical/render pitch; never invent an overlap")
    guard let range=target.sidePitchWindow(eyes:[rendered],yaw:rendered.yaw,eyeHeight:1.62) else {
        fatalError("The actual render eye still has a valid side window")
    }
    for fraction in [0.01,0.25,0.5,0.75,0.99] {
        let pitch=range.lowerBound+(range.upperBound-range.lowerBound)*fraction
        let hit=BridgeRay.intersection(block:block,pose:eye(1.23,80.4,0.54,pitch))
        require(hit?.axis==axis && hit?.sign==sign,"The proposed pitch must hit the intended side in every quadrant")
    }
    let nearby=eye(1.25,80.38,0.56)
    guard let common=target.sidePitchWindow(eyes:[rendered,nearby],yaw:rendered.yaw,eyeHeight:1.62) else {
        fatalError("Nearby eyes should retain their shared placement window")
    }
    for p in [rendered,nearby] {
        let aimed=F3Pose(x:p.x,y:p.y,z:p.z,yaw:p.yaw,pitch:(common.lowerBound+common.upperBound)/2,time:0)
        let hit=BridgeRay.intersection(block:block,pose:aimed)
        require(hit?.axis==axis && hit?.sign==sign,"The shared midpoint must be valid for both eyes")
    }
    require(target.sidePitchWindow(eyes:[eye(0.9,80.4,0.5)],yaw:rendered.yaw,eyeHeight:1.62)==nil,"A hidden side has no window")
    require(target.sidePitchWindow(eyes:[rendered],yaw:rendered.yaw+180,eyeHeight:1.62)==nil,"A ray facing away cannot place")
}
print("Passed: four-quadrant render/logical window geometry, disjoint intervals, hidden and backward faces.")
