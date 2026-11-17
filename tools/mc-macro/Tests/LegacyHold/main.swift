import Foundation
var g=HeldKeyReconciler()
var n=0
func check(_ b:Bool){n+=1;assert(b)}
g.begin(hardwareDown:false)
for t in [0.0,0.008,0.1,1.0] {check(!g.released(hardwareDown:false,now:t))}
check(!g.released(hardwareDown:true,now:2))
check(!g.released(hardwareDown:false,now:2.008))
check(!g.released(hardwareDown:true,now:2.016))
check(!g.released(hardwareDown:false,now:2.04))
check(g.released(hardwareDown:false,now:2.13))
g.begin(hardwareDown:false)
check(!g.released(hardwareDown:false,now:3))
g.begin(hardwareDown:true)
check(!g.released(hardwareDown:false,now:4))
check(g.released(hardwareDown:false,now:4.09))
print("Held-key fallback: \(n) checks passed")
