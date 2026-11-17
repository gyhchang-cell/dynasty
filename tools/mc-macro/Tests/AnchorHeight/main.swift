import Foundation
var checks=0,failures=0
func check(_ v:Bool,_ why:String){checks+=1;if !v {failures+=1;print("FAIL",why)}}
let root="research/high-anchor-20261103/"
func fixture(_ n:Int)->[String:Any] {try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:root+"fixture-\(n).json"))) as! [String:Any]}
func state(_ d:[String:Any],_ t:Double)->AnchorState {AnchorState.parse(d,now:t)!}
func cell(_ d:inout [String:Any],_ p:F3Block,_ id:String,_ flags:Int,_ charge:Int) {
 var palette=d["palette"] as! [String];if !palette.contains(id){palette.append(id)};d["palette"]=palette
 var rows=d["cells"] as! [[Any]];rows.removeAll{($0[0] as! Int)==p.x && ($0[1] as! Int)==p.y && ($0[2] as! Int)==p.z};rows.append([p.x,p.y,p.z,palette.firstIndex(of:id)!,flags,charge]);d["cells"]=rows
}
for level in 0...2 {
 let d=fixture(level),p=try! AnchorPlan.make(state(d,10),now:10)
 check(p.placements.count==1,"one shield remains sufficient at height \(level)")
 check(p.shieldFirst==(level>0),"only high geometry uses uncharged anchor support")
 check(AnchorRay.distance(p.origin,p.triggerOrigin)<=(level==1 ? 0.75:0.01),"minimal position change at height \(level)")
 check(p.usableAt(state(d,10).positioned(p.origin)),"planned eye can still use anchor at height \(level)")
}
do {
 var d=fixture(1);d["movementUsable"]=false
 check((try? AnchorPlan.make(state(d,10),now:10))==nil,"ambiguous movement binding refuses automatic stepping")
 d=fixture(1);d["movementDown"]=true
 check((try? AnchorPlan.make(state(d,10),now:10))==nil,"manual movement cannot be adopted as a nudge")
 d=fixture(1)
 var rows=d["cells"] as! [[Any]];rows.removeAll{($0[1] as! Int)==64 && (($0[0] as! Int) != 0 || ($0[2] as! Int) != 0)};d["cells"]=rows
 check((try? AnchorPlan.make(state(d,10),now:10))==nil,"unsupported floor cannot authorize a nudge")
}
for obstructed in [false,true] {
 var d=fixture(1);let c=AnchorController();var held=Set<UInt16>(),uses=0
 c.movement={held=$0};c.release={held=[]};c.click={uses+=1};c.start(state(d,20),now:20);let p=c.plan!
 cell(&d,p.anchor,"minecraft:respawn_anchor",1,0)
 if obstructed {cell(&d,F3Block(x:-1,y:65,z:0),"minecraft:stone",1,-1)}
 c.tick(state(d,20.1),now:20.1,allowed:true)
 if obstructed {check(c.phase == .restore && held.isEmpty && uses==0,"new obstacle aborts before moving or charging");continue}
 check(c.repositioning && held==[2] && uses==0,"south-facing negative-X nudge uses D before charging")
 d["position"]=p.origin;d["eye"]=[p.origin[0],p.origin[1]+1.62,p.origin[2]]
 c.tick(state(d,20.2),now:20.2,allowed:true)
 check(held.isEmpty,"nudge releases at a usable position")
 d["velocity"]=[0.01,0.0,0.0]
 c.tick(state(d,20.32),now:20.32,allowed:true)
 check(c.repositioning && uses==0,"residual coast must settle before edge charging")
 d["velocity"]=[0.0,0.0,0.0]
 c.tick(state(d,20.35),now:20.35,allowed:true)
 check(c.phase == .shield,"confirmed stationary endpoint advances to shielding")
 d["selected"]=p.shieldSlot;d["hit"]=["pos":[p.anchor.x,p.anchor.y,p.anchor.z],"face":p.placements[0].face,"point":[0.5,66.5,3.0]]
 c.tick(state(d,20.4),now:20.4,allowed:true)
 check(uses==1,"first generated use places shielding on uncharged anchor")
 cell(&d,p.shield,p.shieldID,1,-1)
 c.tick(state(d,20.5),now:20.5,allowed:true)
 check(c.phase == .charge && uses==1,"confirmed shield is required before charging")
 // A manual interruption must cancel even during the new sequence.
 c.stop("manual");c.tick(state(d,20.6),now:20.6,allowed:true)
 check(!c.active && held.isEmpty && uses==1,"manual stop releases movement and cannot resume itself")
}
do {
 var d=fixture(2);let c=AnchorController();var uses=0;c.click={uses+=1};c.start(state(d,30),now:30);let p=c.plan!
 cell(&d,p.anchor,"minecraft:respawn_anchor",1,0);c.tick(state(d,30.1),now:30.1,allowed:true)
 cell(&d,p.anchor,"minecraft:respawn_anchor",1,1);d["selected"]=p.shieldSlot
 c.tick(state(d,30.2),now:30.2,allowed:true)
 check(c.phase == .restore && uses==0,"unexpected charge cannot turn shield placement into premature explosion")
}
print("Anchor height checks \(checks), failed \(failures)");exit(failures==0 ? 0:1)
