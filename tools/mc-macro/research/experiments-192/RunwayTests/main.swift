import Foundation
var block=F3Block(x:35,y:79,z:-34), x=35.34938847985,z = -33.86010224568, ox=0.5,oz=0.5,yaw = -135.0
for _ in 0..<4 {
    let route=TellyRoute(x:ox,z:oz,yaw:yaw)
    let pose=F3Pose(x:x,y:80,z:z,yaw:yaw,pitch:45,time:0)
    assert(route.runway(on:block)==nil, "Old centre line should only clip this cell's corner")
    guard let span=route.landingRunway(on:block,from:pose) else {fatalError("Actual supported path was rejected")}
    assert(span.contains(route.along(x,z)))
    assert(span.upperBound-span.lowerBound>0.65)
    (x,z)=(-z,x);(ox,oz)=(-oz,ox);block=F3Block(x:-block.z-1,y:79,z:block.x);yaw+=90
}
let b=F3Block(x:0,y:79,z:0), diagonal=TellyRoute(x:0.5,z:0.5,yaw:-135)
assert(diagonal.landingRunway(on:b,from:F3Pose(x:1.4,y:80,z:1.4,yaw:0,pitch:45,time:0))==nil)
for yaw in [0.0,90,-90,180] {
    let r=TellyRoute(x:0.5,z:0.5,yaw:yaw)
    assert(r.landingRunway(on:b,from:F3Pose(x:0.6,y:80,z:0.55,yaw:yaw,pitch:45,time:0))==r.runway(on:b))
}
print("Actual landing runway: four rotated recorded cases, unsupported case, four cardinal regressions passed")
