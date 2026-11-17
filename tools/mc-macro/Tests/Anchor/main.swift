import Foundation
var count=0,failed=0
func check(_ value:Bool,_ label:String){count+=1;if !value {failed+=1;print("FAIL "+label)}}
let fixture=CommandLine.arguments[1]
let data=try! Data(contentsOf:URL(fileURLWithPath:fixture))
var base=try! JSONSerialization.jsonObject(with:data) as! [String:Any]
base["active"]=true;base["age"]=0.0;base["mouseReady"]=true
func state(_ changes:[String:Any]=[:],now:Double=10)->AnchorState {
    var d=base;for (k,v) in changes {d[k]=v}
    return AnchorState.parse(d,now:now)!
}
func rejects(_ changes:[String:Any],_ label:String) {check((try? AnchorPlan.make(state(changes),now:10))==nil,label)}
check((try? AnchorPlan.make(state(),now:10)) != nil,"valid real snapshot plans a sequence")
rejects(["dimension":"minecraft:the_nether"],"Nether cannot explode")
rejects(["dimension":"example:unknown"],"unknown dimension does not guess")
rejects(["offhand":"minecraft:glowstone"],"offhand glowstone cannot accidentally recharge")
rejects(["sneaking":true],"sneaking prevents normal anchor interaction")
rejects(["using":true],"item use cannot overlap")
rejects(["ground":false],"airborne position rejected")
rejects(["active":false],"menus and loss of capture rejected")
rejects(["useKey":"key.keyboard.q"],"custom use binding not guessed")
rejects(["hit":["pos":[0,64,3],"point":[0.5,65.0,3.5],"face":"NORTH"]],"side face rejected")
rejects(["position":[0.5,65.0,2.5]],"shield would overlap player")
for missing in ["minecraft:respawn_anchor","minecraft:glowstone","minecraft:obsidian"] {
    var slots=base["slots"] as! [[String:Any]]
    for i in slots.indices where slots[i]["id"] as? String==missing {slots[i]["id"]="minecraft:air";slots[i]["count"]=0}
    rejects(["slots":slots],"missing "+missing)
}
var rows=base["cells"] as! [[Any]]
if let i=rows.firstIndex(where:{($0[0] as? Int)==0 && ($0[1] as? Int)==65 && ($0[2] as? Int)==2}) {
    rows[i][3]="minecraft:stone";rows[i][4]=true;rows[i][5]=false
}
check((try? AnchorPlan.make(state(["cells":rows]),now:10))?.reuseShield==true,"existing solid shield can be reused")
let controller=AnchorController();var clicks=0,keys=0,moves=0,releases=0
controller.click={clicks+=1};controller.select={_ in keys+=1};controller.move={_,_ in moves+=1};controller.release={releases+=1}
controller.start(state(),now:10)
controller.start(state(),now:10.01)
check(controller.phase == .awaitPlacement,"repeated trigger cannot create a second sequence")
controller.tick(state(now:10.02),now:10.02,allowed:true)
controller.tick(state(now:10.04),now:10.04,allowed:true)
check(clicks==0 && keys==0 && moves==0,"native placement wait sends no input")
controller.tick(state(now:10.3),now:10.3,allowed:true)
check(clicks==0,"no blind placement retries")
controller.tick(state(now:11.3),now:11.3,allowed:true)
check(controller.phase == .restore && releases>0 && clicks==0,"unconfirmed placement times out, releases and permits only restoration")
controller.tick(state(now:11.4),now:11.4,allowed:true)
check(!controller.active && clicks==0,"unconfirmed placement restoration ends without another use")
controller.start(state(now:20),now:20)
controller.tick(state(["world":999],now:20.01),now:20.01,allowed:true)
check(!controller.active,"world change cancels")
controller.start(state(now:30),now:30)
controller.tick(state(now:30.01),now:30.01,allowed:false)
check(!controller.active,"foreground loss cancels")
controller.start(state(now:40),now:40)
controller.tick(state(now:40),now:40.2,allowed:true)
check(!controller.active,"stale telemetry cancels")
controller.start(state(now:50),now:50)
controller.tick(state(["position":[0.5,65.0,1.0]],now:50.01),now:50.01,allowed:true)
check(!controller.active,"moving out of the planned shielding position cancels")
controller.start(state(now:60),now:60)
var placed=base["cells"] as! [[Any]]
let planned=controller.plan!.anchor
let index=placed.firstIndex{($0[0] as? Int)==planned.x && ($0[1] as? Int)==planned.y && ($0[2] as? Int)==planned.z}!
placed[index][3]="minecraft:respawn_anchor";placed[index][4]=true;placed[index][5]=false;placed[index][6]=0;placed[index][7]=true
controller.tick(state(["cells":placed],now:60.1),now:60.1,allowed:true)
check(controller.phase == .awaitPlacement && clicks==0,"predicted placement cannot start charging")
check(keys==1,"predicted placement may prepare the slot without using it")
placed[index][7]=false
controller.tick(state(["cells":placed],now:60.2),now:60.2,allowed:true)
check(controller.phase == .charge && keys==1,"server-confirmed native placement starts charge")
check(clicks==0,"slot and aim must settle before charge click")
let movesBefore=moves
controller.tick(state(["cells":placed],now:60.24),now:60.24,allowed:true)
controller.tick(state(["cells":placed],now:60.28),now:60.28,allowed:true)
check(moves==movesBefore && clicks==0,"delayed render cannot duplicate movement or click while in flight")
controller.tick(state(["cells":placed],now:60.6),now:60.6,allowed:true)
check(!controller.active,"unacknowledged camera motion stops safely")
controller.stop("test")
controller.start(state(["mouseReady":false],now:70),now:70)
let previousMoves=moves,previousClicks=clicks
controller.tick(state(["mouseReady":false,"cells":placed],now:70.1),now:70.1,allowed:true)
controller.tick(state(["mouseReady":false,"cells":placed],now:70.15),now:70.15,allowed:true)
check(moves==previousMoves+1 && clicks==previousClicks,"first-move initialization is sent once without clicking")
check(controller.phase == .awaitPlacement,"camera readiness required before continuing")
controller.tick(state(["mouseReady":true,"cells":placed],now:70.2),now:70.2,allowed:true)
check(controller.phase == .charge,"readiness confirmation resumes charging")
let diagonal=state(["yaw":45.0,"hit":["pos":[-2,64,2],"point":[-1.5,65.0,2.5],"face":"UP"]])
let diagonalPlan=try! AnchorPlan.make(diagonal,now:10)
check(diagonalPlan.shield==F3Block(x:-1,y:65,z:1),"diagonal anchor uses a shield on the actual player-anchor line")
check(!AnchorPlan.shieldsBody(anchor:F3Block(x:-2,y:65,z:2),shield:F3Block(x:-2,y:65,z:1),position:[0.5,65,0.5]),"a corner-touching shield cannot authorize detonation")
for (x,z) in [(0,3),(3,0),(0,-3),(-3,0),(2,2),(-2,2),(2,-2),(-2,-2)] {
 let s=state(["hit":["pos":[x,64,z],"point":[Double(x)+0.5,65.0,Double(z)+0.5],"face":"UP"]])
 check((try? AnchorPlan.make(s,now:10)) != nil,"flat ground supports shield geometry \(x),\(z)")
}
let far=state(["range":4.5,"position":[0.5,65.0,0.2],"eye":[0.5,66.62,0.2],"hit":["pos":[0,64,4],"point":[0.5,65.0,4.2],"face":"UP"]])
check((try? AnchorPlan.make(far,now:10)) != nil,"legal survival reach beyond old four-block center limit")
let near=state(["hit":["pos":[0,64,2],"point":[0.5,65.0,2.5],"face":"UP"]])
check((try? AnchorPlan.make(near,now:10)) != nil,"safe two-block placement no longer rejected by old2.4 threshold")
let creativeEdge=state(["range":5.0,"hit":["pos":[0,64,5],"point":[0.5,65.0,5.03],"face":"UP"]])
let edgePlan=try? AnchorPlan.make(creativeEdge,now:10)
check(edgePlan != nil,"reachable block edge accepted when center is out of reach")
if let p=edgePlan {
 let ray=AnchorRay.visible(p.anchor,state:creativeEdge,extraBlocks:[p.shield])
 check(ray != nil && AnchorRay.distance(creativeEdge.eye,ray!.point)<5,"post-shield edge aim remains in real reach")
}
rejects(["range":4.5,"hit":["pos":[0,64,5],"point":[0.5,65.0,5.03],"face":"UP"]],"cannot exceed actual survival reach")
var sideCells=base["cells"] as! [[Any]]
let wall=sideCells.firstIndex{($0[0] as? Int)==0 && ($0[1] as? Int)==65 && ($0[2] as? Int)==3}!
sideCells[wall][3]="minecraft:stone";sideCells[wall][4]=true;sideCells[wall][5]=false
let side=state(["cells":sideCells,"hit":["pos":[0,65,3],"point":[0.5,65.8,3.0],"face":"NORTH"]])
check((try? AnchorPlan.make(side,now:10))?.anchor==F3Block(x:0,y:65,z:2),"side placement follows the actual hit face")
for (x,z) in [(1,4),(2,3),(-3,1),(3,-2)] {
 let angled=state(["range":4.5,"hit":["pos":[x,64,z],"point":[Double(x)+0.5,65.0,Double(z)+0.5],"face":"UP"]])
 check((try? AnchorPlan.make(angled,now:10)) != nil,"off-axis placement \(x),\(z)")
}
// Delayed slot confirmation must not consume the post-click confirmation budget.
func confirmationRig(_ start:Double)->(AnchorController,()->Int,[[Any]],Int) {
 let c=AnchorController();var n=0;c.click={n+=1};c.start(state(now:start),now:start)
 let p=c.plan!;var cells=base["cells"] as! [[Any]]
 let at=cells.firstIndex{($0[0] as? Int)==p.anchor.x && ($0[1] as? Int)==p.anchor.y && ($0[2] as? Int)==p.anchor.z}!
 cells[at][3]="minecraft:respawn_anchor";cells[at][4]=true;cells[at][5]=false;cells[at][6]=0;cells[at][7]=false
 return(c,{n},cells,at)
}
func anchorHit(_ c:AnchorController)->[String:Any] {let a=c.plan!.anchor;return ["pos":[a.x,a.y,a.z],"point":[Double(a.x)+0.5,Double(a.y)+1,Double(a.z)+0.5],"face":"UP"]}
do {
 let(c,n,cells,at)=confirmationRig(100);let hit=anchorHit(c);let glow=c.plan!.glowSlot
 c.tick(state(["cells":cells,"hit":hit],now:100.06),now:100.06,allowed:true)
 c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:101.15),now:101.15,allowed:true)
 check(n()==1,"delayed slot results in exactly one charge click")
 c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:101.30),now:101.30,allowed:true)
 check(c.phase == .charge && n()==1,"confirmation budget begins at click, not phase entry")
 var done=cells;done[at][6]=1
 c.tick(state(["cells":done,"hit":hit,"selected":glow],now:101.35),now:101.35,allowed:true)
 check(c.phase == .shield,"late authoritative charge still advances")
}
for rollback in [false,true] {
 let(c,n,cells,at)=confirmationRig(200);let hit=anchorHit(c);let glow=c.plan!.glowSlot
 var cameraYaw=base["yaw"] as! Double,cameraPitch=base["pitch"] as! Double
 let degrees=pow((base["sensitivity"] as! Double)*0.6+0.2,3)*1.2
 c.move={x,y in cameraYaw=F3Pose.angle(cameraYaw+Double(x)*degrees);cameraPitch+=Double(y)*degrees}
 c.tick(state(["cells":cells,"hit":hit],now:200.06),now:200.06,allowed:true)
 c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:200.12),now:200.12,allowed:true)
 c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:200.15),now:200.15,allowed:true)
 check(c.active && n()==1,"old confirmed state immediately after click is not a rejection")
 if rollback {
  var predicted=cells;predicted[at][6]=1;predicted[at][7]=true
  c.tick(state(["cells":predicted,"hit":hit,"selected":glow],now:200.18),now:200.18,allowed:true)
  c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:200.22),now:200.22,allowed:true)
  check(c.phase == .restore && c.failure?.contains("充能被回退")==true && n()==1,"authoritative rollback restores without retry")
  c.tick(state(["cells":cells,"selected":base["selected"]!,"yaw":cameraYaw,"pitch":cameraPitch],now:200.3),now:200.3,allowed:true)
  c.tick(state(["cells":cells,"selected":base["selected"]!,"yaw":cameraYaw,"pitch":cameraPitch],now:200.35),now:200.35,allowed:true)
  check(!c.active && c.failure?.contains("已回正")==true && n()==1,"rollback retains failure after restoration, never claims success")
 } else {
  var removed=cells;removed[at][3]="minecraft:air";removed[at][4]=false;removed[at][5]=true
  c.tick(state(["cells":removed,"hit":hit,"selected":glow],now:200.22),now:200.22,allowed:true)
  check(c.phase == .restore && c.failure?.contains("锚已被移除")==true,"confirmed target removal restores instead of generic timeout")
 }
}
do {
 let(c,n,cells,at)=confirmationRig(300);let hit=anchorHit(c);let glow=c.plan!.glowSlot
 c.tick(state(["cells":cells,"hit":hit],now:300.06),now:300.06,allowed:true)
 c.tick(state(["cells":cells,"hit":hit,"selected":glow],now:300.12),now:300.12,allowed:true)
 var predicted=cells;predicted[at][6]=1;predicted[at][7]=true
 c.tick(state(["cells":predicted,"hit":hit,"selected":glow],now:300.125),now:300.125,allowed:true)
 predicted[at][7]=false
 c.tick(state(["cells":predicted,"hit":hit,"selected":glow],now:300.130),now:300.130,allowed:true)
 check(c.active && n()==1,"fast successful confirmation is not mistaken for rollback")
 c.tick(state(["cells":predicted,"hit":hit,"selected":glow],now:300.140),now:300.140,allowed:true)
 check(c.phase == .shield,"fast confirmation advances after minimum interval")
}
do {
 let compact=state(["cells":[[0,64,0,0,1,-1],[0,65,1,1,6,-1]],"palette":["minecraft:stone","minecraft:air"],"volume":[-5,5,60,70,-5,5]])
 check(compact.cells[F3Block(x:0,y:64,z:0)]?.full==true,"compact palette retains solids")
 check(compact.cells[F3Block(x:0,y:65,z:1)]?.pending==true,"predicted air must stay explicit")
 check(compact.cells[F3Block(x:1,y:61,z:1)]?.replaceable==true,"known omitted air covers lower terrain")
 check(compact.cells[F3Block(x:1,y:59,z:1)]==nil,"outside capture volume is unknown, not air")
}
do {
 let options=[AnchorItem(slot:0,id:"minecraft:obsidian",count:64,full:true),AnchorItem(slot:2,id:"minecraft:glowstone",count:64,full:true),AnchorItem(slot:5,id:"minecraft:oak_planks",count:64,full:true)]
 check(AnchorPlan.shieldSlot(options)?.slot==5,"prefer another full block over obsidian and glowstone")
 check(AnchorPlan.shieldSlot(Array(options.prefix(2)))?.slot==0,"obsidian remains the fallback")
 for id in ["minecraft:tnt","minecraft:respawn_anchor","minecraft:sand","minecraft:red_concrete_powder","minecraft:glowstone","minecraft:slime_block"] {
  check(!AnchorPlan.shieldMaterial(id),"exclude unstable or explosive shield material "+id)
 }
}
do {
 var dense:[[Any]]=[]
 for x in -5...5 {for y in 60...70 {for z in -5...5 {dense.append([x,y,z,0,1,-1])}}}
 let denseState=state(["cells":dense,"palette":["minecraft:stone"],"volume":[-5,5,60,70,-5,5]])
 check(denseState.cells.values.count==1331,"dense vertical capture remains readable")
 var sideRows=base["cells"] as! [[Any]]
 for i in sideRows.indices {
  let x=sideRows[i][0] as! Int,y=sideRows[i][1] as! Int,z=sideRows[i][2] as! Int
  if y==64 && (x != 0 || ![0,3].contains(z)) {sideRows[i]=[x,y,z,"minecraft:air",false,true,-1,false]}
  if x==1 && y==65 && z==2 {sideRows[i]=[x,y,z,"minecraft:stone",true,false,-1,false]}
 }
 let sideSupport=try? AnchorPlan.make(state(["cells":sideRows]),now:10)
 check(sideSupport?.shieldFace=="WEST" && sideSupport?.shieldSupport==F3Block(x:1,y:65,z:2),"wall face can support shield when floor is absent")
}
// Recoil after our final use must not discard the remaining view/item restore.
do {
 var existing=base["cells"] as! [[Any]]
 let shieldIndex=existing.firstIndex{($0[0] as? Int)==0 && ($0[1] as? Int)==65 && ($0[2] as? Int)==2}!
 existing[shieldIndex]=[0,65,2,"minecraft:stone",true,false,-1,false]
 let c=AnchorController();var uses=0,recoilMoves=0;c.click={uses+=1};c.move={_,_ in recoilMoves+=1}
 c.start(state(["cells":existing],now:400),now:400)
 let p=c.plan!,hit=anchorHit(c),at=existing.firstIndex{($0[0] as? Int)==p.anchor.x && ($0[1] as? Int)==p.anchor.y && ($0[2] as? Int)==p.anchor.z}!
 existing[at]=[p.anchor.x,p.anchor.y,p.anchor.z,"minecraft:respawn_anchor",true,false,0,false]
 c.tick(state(["cells":existing,"hit":hit,"selected":p.glowSlot],now:400.1),now:400.1,allowed:true)
 check(uses==1,"recoil fixture charged once")
 existing[at][6]=1
 c.tick(state(["cells":existing,"hit":hit,"selected":p.glowSlot],now:400.2),now:400.2,allowed:true)
 c.tick(state(["cells":existing,"hit":hit,"selected":p.detonateSlot],now:400.3),now:400.3,allowed:true)
 check(uses==2 && c.phase == .detonate,"recoil fixture issued final use once")
 existing[at]=[p.anchor.x,p.anchor.y,p.anchor.z,"minecraft:air",false,true,-1,true]
 let moved=[p.origin[0]+0.6,p.origin[1]+0.5,p.origin[2]]
 c.tick(state(["cells":existing,"position":moved,"ground":false,"yaw":p.yaw+30,"selected":p.detonateSlot],now:400.35),now:400.35,allowed:true)
 check(c.phase == .detonate && uses==2,"recoil with pending removal waits without repeating use")
 existing[at][7]=false
 c.tick(state(["cells":existing,"position":moved,"ground":false,"yaw":p.yaw+30,"selected":p.detonateSlot],now:400.4),now:400.4,allowed:true)
 check(c.phase == .restore,"confirmed detonation still restores after recoil")
 c.tick(state(["cells":existing,"position":moved,"ground":false,"yaw":p.yaw+30,"selected":p.detonateSlot],now:400.45),now:400.45,allowed:true)
 check(recoilMoves==1 && uses==2,"recoil recovery changes only view, no extra use")
 c.tick(state(["cells":existing,"position":moved,"ground":false,"yaw":p.yaw,"pitch":p.pitch,"selected":base["selected"]!],now:400.5),now:400.5,allowed:true)
 check(!c.active && c.failure==nil && uses==2,"recoil recovery ends with original view and slot")
}
do {
 let(c,n,cells,_)=confirmationRig(500);let hit=anchorHit(c);let p=c.plan!
 c.tick(state(["cells":cells,"hit":hit,"selected":p.glowSlot],now:500.1),now:500.1,allowed:true)
 c.tick(state(["cells":cells,"hit":hit,"selected":p.glowSlot],now:501.31),now:501.31,allowed:true)
 check(c.phase == .restore && n()==1,"missing use acknowledgement recovers instead of leaving view and slot stranded")
 c.tick(state(["cells":cells,"selected":base["selected"]!,"yaw":p.yaw,"pitch":p.pitch],now:501.4),now:501.4,allowed:true)
 check(!c.active && c.failure?.contains("已回正")==true && n()==1,"timeout recovery does not retry a potentially destructive use")
}
print("Anchor checks \(count), failed \(failed)");exit(failed==0 ? 0:1)
