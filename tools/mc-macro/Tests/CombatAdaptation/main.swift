import Foundation
var passed=0,failed=0
func check(_ b:Bool,_ name:String){if b {passed+=1}else{failed+=1;print("FAIL "+name)}}
let initial=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
let target:[String:Any] = ["id":42,"distance":2.4,"range":3.0,"valid":true,"hurtTime":0,"ground":true,"blocking":false]
func state(_ updates:[String:Any]=[:],combat:[String:Any]=[:],targetChanges:[String:Any]?=[:],at:Double=10,tick:Int=100,item:String="minecraft:diamond_sword")->AnchorState {
 var d=initial;d["active"]=true;d["age"]=0.0;d["mouseReady"]=true;d["selected"]=0;d["tick"]=tick;d["ground"]=true;d["using"]=false;d["rightDown"]=false
 d["sprintKey"]="key.keyboard.left.control";d["toggleSprint"]=false;d["sprintKeyDown"]=true;d["sprinting"]=true
 var slots=d["slots"] as! [[String:Any]];slots[0]["id"]=item;slots[0]["count"]=item=="minecraft:air" ? 0:1;d["slots"]=slots
 var c:[String:Any] = ["cooldown":1.0,"delayTicks":12.5,"attackKey":"key.mouse.left","jumpKey":"key.keyboard.space","forwardKey":"key.keyboard.w","jumpDown":false,"forwardDown":true,"jumpUsable":true,"forwardUsable":true,"hurtTime":0,"fallDistance":0.0,"critEnvironment":true,"attacker":42,"safeJump":true,"critTicks":3]
 if let changes=targetChanges {var t=target;changes.forEach{t[$0.key]=$0.value};c["target"]=t}
 combat.forEach{c[$0.key]=$0.value};d["combat"]=c;updates.forEach{d[$0.key]=$0.value};return AnchorState.parse(d,now:at)!
}
func rig()->(SwordController,()->Int,()->Int,()->[Bool]) {
 let c=SwordController();var clicks=0,jumps=0,moves:[Bool]=[]
 c.click={clicks+=1};c.jump={jumps+=1};c.forward={moves.append($0)}
 return (c,{clicks},{jumps},{moves})
}

let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
// An opponent reaches the range edge after W was released for a crit.
do {
 let(c,n,_,m)=rig();let s=state(fall,combat:["fallDistance":0.4,"cooldown":0.84]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 check(m()==[true],"baseline starts crit preparation")
 c.tick(state(fall,combat:["fallDistance":0.5],targetChanges:["distance":2.9],at:10.05,tick:101),now:10.05,allowed:true)
 check(m()==[true,false] && !c.suppressSprint,"range edge immediately restores pursuit")
 check(n()==1,"ready edge hit does not wait another tick for sprint off")
}
// Preparation failed: reduced critical charge cannot be used for a sprint hit.
do {
 let(c,n,_,m)=rig();let s=state(fall,combat:["fallDistance":0.4,"cooldown":0.84]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 c.tick(state(fall,combat:["fallDistance":0.5,"cooldown":0.94],at:10.12,tick:103),now:10.12,allowed:true)
 check(n()==0 && m()==[true,false] && !c.suppressSprint,"failed crit restores W and waits for ordinary full damage")
 c.tick(state(fall,combat:["fallDistance":0.6],at:10.16,tick:104),now:10.16,allowed:true)
 check(n()==1 && m()==[true,false],"ordinary full hit recovers without repeated W tap")
}
// A different crosshair target must not inherit the previous target's W hold.
do {
 let(c,n,_,m)=rig();let s=state(fall,combat:["fallDistance":0.4]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 c.tick(state(fall,combat:["fallDistance":0.5],targetChanges:["id":43,"hurtTime":5],at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==0 && m()==[true,false] && !c.suppressSprint,"target change cancels obsolete crit preparation")
}
// A fresh incoming hit invalidates optional crit preparation, preserving movement.
do {
 let(c,n,_,m)=rig();let s=state(fall,combat:["fallDistance":0.4]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 c.tick(state(fall,combat:["fallDistance":0.5,"hurtTime":10],at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==1 && m()==[true,false] && !c.suppressSprint,"received hit interrupts optional crit wait")
}
// Aim loss closes a decision episode; the next apex wait gets its own deadline.
do {
 let(c,n,_,_)=rig();let rising:[String:Any] = ["ground":false,"velocity":[0.0,0.08,0.0]]
 c.begin(state(rising),now:10);c.tick(state(rising,at:10.06,tick:101),now:10.06,allowed:true)
 c.tick(state(rising,targetChanges:nil,at:10.10,tick:102),now:10.10,allowed:true)
 c.tick(state(rising,at:10.18,tick:103),now:10.18,allowed:true)
 check(n()==0,"reacquired aim does not inherit expired apex timer")
 var stopped=fall;stopped["sprinting"]=false
 c.tick(state(stopped,combat:["fallDistance":0.3,"cooldown":0.92],at:10.23,tick:104),now:10.23,allowed:true)
 check(n()==1,"reacquired target still attacks on real falling critical window")
}
// Existing grounded attacks must not be throttled or jittered by these fixes.
do {let(c,n,_,m)=rig();c.begin(state(),now:10);c.tick(state(),now:10,allowed:true);check(n()==1 && m().isEmpty,"unchanged full grounded attack")}
do {let(c,n,_,m)=rig();c.begin(state(combat:["cooldown":0.94]),now:10);c.tick(state(combat:["cooldown":0.94]),now:10,allowed:true);check(n()==0 && m().isEmpty,"ordinary weak attack remains suppressed")}
do {
 let(c,n,_,m)=rig();c.preserveSprint=true
 let s=state(fall,combat:["fallDistance":0.4]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 check(n()==1 && m().isEmpty && !c.suppressSprint,"forced sprint never releases W for optional crit")
}
print("Combat adaptation checks \(passed+failed), passed \(passed), failed \(failed)");exit(failed==0 ? 0:1)
