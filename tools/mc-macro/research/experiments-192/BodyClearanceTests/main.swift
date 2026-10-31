import Foundation
let b=F3Block(x:0,y:80,z:0)
let top=TellyPlacement(support:F3Block(x:0,y:79,z:0),result:b,axis:1,sign:1,x:0.5,y:80,z:0.5)
func p(_ x:Double,_ y:Double,_ z:Double)->F3Pose {F3Pose(x:x,y:y,z:z,yaw:0,pitch:45,time:0)}
// Early ascent remains blocked while either observed body occupies the new block.
assert(!top.clearOfBody([p(0.5,80.753,0.5)]))
assert(!top.clearOfBody([p(-0.38,80.753,0.5),p(-0.14,80.42,0.5)]))
// Once both ticks have passed a side, ascent height is irrelevant.
for (x,z) in [(-0.38,0.5),(1.38,0.5),(0.5,-0.38),(0.5,1.38)] {
    assert(top.clearOfBody([p(x,80.753,z),p(x,80.42,z)]))
}
assert(!top.clearOfBody([p(-0.2999,80.42,-0.2999)]))
assert(top.clearOfBody([p(0.5,81.002,0.5)]))
assert(!top.clearOfBody([]))
print("Body clearance: 9 geometric cases passed")
