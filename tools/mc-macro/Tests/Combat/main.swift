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
for (label,s) in [("air",state(targetChanges:nil)),("wall",state(targetChanges:["valid":false])),("too far",state(targetChanges:["distance":3.1])),("shield",state(targetChanges:["blocking":true])),("hurt target",state(targetChanges:["hurtTime":5])),("cooldown",state(combat:["cooldown":0.5]))] {
 let(c,n,_,_)=rig();c.begin(s,now:10);c.tick(s,now:10,allowed:true);check(n()==0,label+" cannot click")
}
do {let(c,n,_,_)=rig();let s=state();c.tick(s,now:10,allowed:true);check(n()==0,"not armed");c.begin(s,now:10);c.tick(s,now:10,allowed:true);check(n()==1,"full cooldown hit");for i in 1...8 {c.tick(state(at:10+Double(i)*0.02,tick:100+i),now:10+Double(i)*0.02,allowed:true)};check(n()==1,"unchanged pre-click cooldown never repeats");c.tick(state(at:10.5,tick:110),now:10.5,allowed:true);check(!c.held && n()==1,"unacknowledged click disarms")}
do {let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(),now:10,allowed:true);c.tick(state(combat:["cooldown":0.12],at:10.05,tick:101),now:10.05,allowed:true);c.tick(state(at:10.65,tick:113),now:10.65,allowed:true);check(n()==2,"acknowledged cooldown cycle permits next hit");c.cancel();c.tick(state(at:11,tick:120),now:11,allowed:true);check(n()==2,"release stops")}
for (label,changed) in [("world",["world":999] as [String:Any]),("slot",["selected":1]),("menu",["active":false])] {let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(changed,at:10.03),now:10.03,allowed:true);check(!c.held && n()==0,label+" disarms")}
for (label,allowed,now) in [("focus",false,10.01),("stale",true,10.2)] {let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(),now:now,allowed:allowed);check(!c.held && n()==0,label+" disarms")}
for (change,clicks) in [(["using":true],0),(["rightDown":true],1)] {
 let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(change,at:10.03),now:10.03,allowed:true)
 check(n()==clicks && c.held && !c.requiresRearm,"native right input is independent; only actual game use defers attack")
}
do {let(c,n,_,_)=rig();c.begin(state(targetChanges:nil),now:10);c.tick(state(targetChanges:nil,at:10.1),now:10.1,allowed:true);c.tick(state(at:10.2),now:10.2,allowed:true);check(n()==1,"held aim enters target without new press")}
do {let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(at:10.02),now:10.03,allowed:true,aimAfter:10.025);check(n()==0,"old pre-motion ray cannot click");c.tick(state(at:10.04),now:10.04,allowed:true,aimAfter:10.025);check(n()==1,"fresh post-motion ray can click")}
do {let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]];c.begin(state(fall,combat:["fallDistance":0.4]),now:10);c.tick(state(fall,combat:["fallDistance":0.4]),now:10,allowed:true);check(n()==0 && c.suppressSprint && moves()==[true],"falling sprint asks bounded W release");var stopped=fall;stopped["sprinting"]=false;c.tick(state(stopped,combat:["fallDistance":0.5],at:10.05,tick:101),now:10.05,allowed:true);check(n()==1,"actual sprint off authorizes critical hit");c.tick(state(stopped,combat:["cooldown":0.12,"fallDistance":0.6],at:10.10,tick:102),now:10.10,allowed:true);check(moves()==[true,false],"W restored after attack acknowledgement");c.tick(state(at:10.15,tick:103),now:10.15,allowed:true);check(!c.suppressSprint,"force sprint recovers")}
do {let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]];c.begin(state(fall,combat:["fallDistance":0.4]),now:10);c.tick(state(fall,combat:["fallDistance":0.4]),now:10,allowed:true);c.tick(state(fall,combat:["fallDistance":0.5],at:10.12,tick:103),now:10.12,allowed:true);check(n()==1,"cannot stall forever for sprint off");c.cancel();check(moves()==[true,false] && !c.suppressSprint,"cancel releases sprint arbitration")}
for (label,changes,obs,targetChanges,shouldJump) in [
 ("new hit",[:],[:],[:],true),
 ("standing still",[:],["forwardDown":false],[:],false),
 ("not sprinting",["sprinting":false],[:],[:],false),
 ("airborne",["ground":false],[:],[:],false),
 ("edge",[:],["safeJump":false],[:],false),
 ("already jumping",[:],["jumpDown":true],[:],false),
 ("different attacker",[:],["attacker":13],[:],false),
 ("late damage",[:],["hurtTime":7],[:],false),
 ("far target",[:],[:],["distance":3.5],false)
] as [(String,[String:Any],[String:Any],[String:Any],Bool)] {
 let(c,_,j,_)=rig();c.begin(state(combat:["cooldown":0.4]),now:10)
 var o:[String:Any] = ["hurtTime":10,"cooldown":0.4];obs.forEach{o[$0.key]=$0.value}
 c.tick(state(changes,combat:o,targetChanges:targetChanges,at:10.05,tick:101),now:10.05,allowed:true)
 c.tick(state(changes,combat:o,targetChanges:targetChanges,at:10.075,tick:101),now:10.075,allowed:true)
 check(j()==(shouldJump ? 1:0),"jump reset "+label)
}
check(!SwordController.eligible(state(combat:["attackKey":"key.keyboard.q"]),now:10),"custom attack key not guessed")
do {
 let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
 c.begin(state(fall,combat:["fallDistance":0.4]),now:10);c.tick(state(fall,combat:["fallDistance":0.4]),now:10,allowed:true)
 c.tick(state(fall,combat:["fallDistance":0.4],targetChanges:["blocking":true],at:10.04),now:10.04,allowed:true)
 check(n()==0 && moves()==[true,false] && !c.suppressSprint,"shield raised during critical preparation restores movement")
}
do {
 let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
 c.begin(state(fall,combat:["fallDistance":0.4]),now:10);c.tick(state(fall,combat:["fallDistance":0.4]),now:10,allowed:true)
 var stopped=fall;stopped["sprinting"]=false
 c.tick(state(stopped,combat:["fallDistance":0.4],at:10.04,tick:101),now:10.04,allowed:true)
 c.tick(state(stopped,combat:["fallDistance":0.4],at:10.16,tick:103),now:10.16,allowed:true)
 check(n()==1 && moves()==[true,false] && !c.suppressSprint,"lost click acknowledgement cannot hold W released for450ms")
}
do {
 let(c,n,_,_)=rig();let rising:[String:Any] = ["ground":false,"velocity":[0.0,0.08,0.0]]
 c.begin(state(rising),now:10)
 c.tick(state(rising,at:10.06),now:10.06,allowed:true)
 check(n()==0,"brief apex wait")
 c.tick(state(rising,at:10.17,tick:103),now:10.17,allowed:true)
 check(n()==1,"apex wait bounded even unusual gravity")
}
do {let(c,_,j,_)=rig();c.begin(state(combat:["cooldown":0.4]),now:10);c.tick(state(combat:["cooldown":0.4,"hurtTime":10,"jumpUsable":false],at:10.05,tick:101),now:10.05,allowed:true);check(j()==0,"conflicting jump key never synthesized")}
do {
 let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
 c.begin(state(fall,combat:["fallDistance":0.4,"cooldown":0.84]),now:10)
 c.tick(state(fall,combat:["fallDistance":0.4,"cooldown":0.84]),now:10,allowed:true)
 check(n()==0 && moves()==[true],"prepare falling critical one tick before threshold")
 var stopped=fall;stopped["sprinting"]=false
 c.tick(state(stopped,combat:["fallDistance":0.5,"cooldown":0.92],at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==1,"falling critical window does not wait for full recharge")
}
do {let(c,n,_,_)=rig();c.begin(state(combat:["cooldown":0.92]),now:10);c.tick(state(combat:["cooldown":0.92]),now:10,allowed:true);check(n()==0,"ordinary close grounded attack still waits full charge")}
do {
 let(c,n,_,_)=rig();let s=state()
 c.noteMotion(s,now:10.01);c.begin(s,now:10.01);c.tick(s,now:10.01,allowed:true)
 check(n()==0,"motion before left-down rejects the already-observed ray")
 for i in 2...8 {c.noteMotion(s,now:10+Double(i)*0.008)}
 c.tick(state(at:10.05,tick:101),now:10.067,allowed:true)
 check(n()==1,"continuous high-polling mouse accepts the next fresh game sample")
}
do {
 let(c,n,_,_)=rig();c.begin(state(targetChanges:nil),now:10);c.noteMotion(state(targetChanges:nil),now:10.01)
 c.tick(state(targetChanges:nil,at:10.05,tick:101),now:10.06,allowed:true)
 check(n()==0,"new frame while aiming at air still cannot attack")
}
check(SwordController.actionKey("key.keyboard.left.control")==nil,"app Control cannot be used as an injected jump or forward key")
do {let(c,n,_,moves)=rig();let late:[String:Any] = ["ground":false,"velocity":[0.0,-0.445,0.0]];c.begin(state(late,combat:["fallDistance":1.1,"critTicks":0]),now:10);c.tick(state(late,combat:["fallDistance":1.1,"critTicks":0]),now:10,allowed:true);check(n()==1 && moves().isEmpty,"last-tick landing cannot spend a tick releasing W for an unavailable crit")}
do {let(c,n,_,_)=rig();let late:[String:Any] = ["ground":false,"velocity":[0.0,-0.445,0.0]];c.begin(state(late,combat:["fallDistance":1.1,"critTicks":0,"cooldown":0.92]),now:10);c.tick(state(late,combat:["fallDistance":1.1,"critTicks":0,"cooldown":0.92]),now:10,allowed:true);check(n()==0,"late landing does not use the reduced critical cooldown threshold")}
do {
 let(c,n,j,_)=rig();c.begin(state(at:20),now:20);c.tick(state(at:20),now:20,allowed:true)
 c.tick(state(combat:["hurtTime":10],at:20.04,tick:100),now:20.04,allowed:true)
 check(n()==1 && j()==1,"fresh received hit is not delayed behind our own click acknowledgement")
 c.tick(state(combat:["hurtTime":10],at:20.06,tick:100),now:20.06,allowed:true)
 check(j()==1,"repeated same damage snapshot cannot repeat jump response")
}
do {
 var toggle=SwordSwitch()
 check(!toggle.canRun(state(at:10),now:10,allowed:true),"new session never auto-arms from old held-left preference")
 check(toggle.key(down:true,repeated:false,gameplay:true,modified:false,now:10) && toggle.enabled,"backslash arms sword session")
 check(toggle.key(down:true,repeated:true,gameplay:true,modified:false,now:10.1) && toggle.enabled,"held hotkey repeat cannot turn session off")
 check(toggle.key(down:true,repeated:false,gameplay:true,modified:false,now:10.2) && toggle.enabled,"duplicate key-down cannot toggle twice")
 check(toggle.key(down:false,repeated:false,gameplay:false,modified:false,now:10.3),"owned key-up is consumed even after focus changes")
 check(!toggle.key(down:true,repeated:false,gameplay:false,modified:false,now:10.4) && toggle.enabled,"backslash typed in chat cannot toggle session")
 check(!toggle.key(down:true,repeated:false,gameplay:true,modified:true,now:10.5) && toggle.enabled,"system shortcut remains native")
 check(toggle.key(down:true,repeated:false,gameplay:true,modified:false,now:10.6) && !toggle.enabled,"second physical press disables")
}
do {
 var toggle=SwordSwitch();toggle.setEnabled(true,now:20)
 let(c,n,_,_)=rig()
 let notReady=state(["active":false],at:20.01)
 check(!toggle.canRun(notReady,now:20.01,allowed:true),"unready initial observation pauses without losing switch")
 let ready=state(["leftDown":false],at:20.1)
 check(toggle.canRun(ready,now:20.1,allowed:true),"fresh state can start without a new left press")
 if toggle.canRun(ready,now:20.1,allowed:true) {c.begin(ready,now:20.1);c.tick(ready,now:20.1,allowed:true)}
 check(n()==1,"switch-on plus manual aim attacks with left mouse completely released")
 check(!toggle.canRun(ready,now:20.3,allowed:true),"stale target cannot attack")
 check(!toggle.canRun(state(at:20.3),now:20.3,allowed:false),"focus loss pauses active switch")
  check(!toggle.canRun(state(at:20.3,item:"minecraft:stone"),now:20.3,allowed:true),"unsupported main hand pauses active switch")
  check(toggle.canRun(state(at:20.3,item:"minecraft:air"),now:20.3,allowed:true),"empty hand remains supported by the melee switch")
 check(toggle.canRun(state(["rightDown":true],at:20.3),now:20.3,allowed:true),"right button never disables independent automatic left switch")
 toggle.pause(now:20.4)
 check(!toggle.canRun(state(at:20.45),now:20.45,allowed:true),"queued pre-menu or slot-change snapshot is not adopted")
 check(toggle.canRun(state(at:20.5),now:20.5,allowed:true),"new eligible gameplay resumes after menu or slot change")
 toggle.setEnabled(false,now:20.6);c.cancel();c.tick(state(at:21),now:21,allowed:toggle.enabled)
 check(n()==1,"switch off cannot schedule another attack")
}
do {
 let(c,n,_,_)=rig();c.begin(state(),now:10);c.tick(state(),now:10,allowed:true)
 c.tick(state(at:10.5,tick:110),now:10.5,allowed:true)
 check(c.requiresRearm && !c.held && n()==1,"missing click acknowledgement requests an explicit rearm, not an automatic retry loop")
}
for item in ["diamond_sword","netherite_sword","wooden_axe","diamond_axe","air"] {
 let s=state(item:"minecraft:"+item);let(c,n,_,_)=rig();c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 check(n()==1,"armed supported main hand "+item)
}
for item in ["diamond_pickaxe","stone","respawn_anchor","glowstone","shield","cooked_beef","bow","mace"] {
 let s=state(item:"minecraft:"+item);let(c,n,_,_)=rig();c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 check(n()==0 && !c.held,"excluded main hand "+item)
}
for item in ["diamond_sword","diamond_axe","air"] {
 let(c,n,_,_)=rig();let s=state(combat:["canDisableShield":true],targetChanges:["blocking":true],item:"minecraft:"+item)
 c.begin(s,now:10);c.tick(s,now:10,allowed:true)
 check(n()==(item=="diamond_axe" ? 1:0),"shield break restricted to axe "+item)
}
do {
 let(c,n,_,_)=rig();let s=state(combat:["canDisableShield":false],targetChanges:["blocking":true],item:"minecraft:diamond_axe")
 c.begin(s,now:10);c.tick(s,now:10,allowed:true);check(n()==0,"axe without native disable capability cannot assume a shield break")
 c.tick(state(combat:["canDisableShield":true,"cooldown":0.6,"delayTicks":20.0],targetChanges:["blocking":true],at:10.1,item:"minecraft:diamond_axe"),now:10.1,allowed:true)
 check(n()==0,"axe shield hit waits own cooldown rather than sword interval")
 c.tick(state(combat:["canDisableShield":true],targetChanges:["blocking":false],at:10.2,item:"minecraft:diamond_axe"),now:10.2,allowed:true)
 check(n()==1,"unshielded or back-facing target returns to damage timing")
}
do {
 let(c,n,_,_)=rig();c.begin(state(),now:10)
 c.tick(state(at:10.1,item:"minecraft:diamond_axe"),now:10.1,allowed:true)
 check(n()==0 && !c.held,"same-slot weapon replacement invalidates pending sword decision")
}
for manual in [false,true] {
 let(c,n,j,moves)=rig();c.begin(state(combat:["cooldown":0.4]),now:10)
 c.tick(state(combat:["cooldown":0.4,"hurtTime":10,"jumpDown":manual],at:10.05,tick:101),now:10.05,allowed:true)
 let rise:[String:Any] = ["ground":false,"velocity":[0.0,0.08,0.0]]
 c.tick(state(rise,combat:["hurtTime":7],at:10.2,tick:104),now:10.2,allowed:true)
 check(n()==1,"reset jump does not wait at apex: manual=\(manual)")
 check(j()==(manual ? 0:1) && moves().isEmpty,"reset jump preserves manual input and forward momentum")
}
do {
 let(c,n,_,moves)=rig();c.begin(state(combat:["cooldown":0.4]),now:10)
 c.tick(state(combat:["cooldown":0.4,"hurtTime":10],at:10.05,tick:101),now:10.05,allowed:true)
 let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
 c.tick(state(fall,combat:["hurtTime":5,"fallDistance":0.4],at:10.3,tick:106),now:10.3,allowed:true)
 check(n()==1 && moves().isEmpty && !c.suppressSprint,"defensive reset flight does not release W for a forced crit")
}
for change in [["active":false]] {
 let s=state(change)
 check(!SwordController.eligible(s,now:10),"uncaptured or inactive game cannot arm")
 let(c,n,_,_)=rig();c.begin(state(combat:["cooldown":0.4]),now:10)
 c.tick(state(change,at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==0 && !c.held,"loss of gameplay capture cancels an armed controller")
}
do {
 let(c,n,_,_)=rig();c.begin(state(combat:["cooldown":0.4]),now:10)
 c.tick(state(combat:["attackKey":"key.keyboard.q"],at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==0 && !c.held,"changed attack binding cannot receive a stale left-click decision")
}
do {
 let(c,n,_,moves)=rig();let fall:[String:Any] = ["ground":false,"velocity":[0.0,-0.15,0.0]]
 c.begin(state(fall,combat:["fallDistance":0.4]),now:10)
 c.tick(state(fall,combat:["fallDistance":0.4]),now:10,allowed:true)
 var uncaptured=fall;uncaptured["active"]=false
 c.tick(state(uncaptured,combat:["fallDistance":0.5],at:10.05,tick:101),now:10.05,allowed:true)
 check(n()==0 && !c.held && moves()==[true,false] && !c.suppressSprint,"capture loss releases critical preparation without an attack")
}
print("Combat checks \(passed+failed), passed \(passed), failed \(failed)");exit(failed==0 ? 0:1)
