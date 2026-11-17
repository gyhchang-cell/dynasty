import Foundation
// Historical 1.10.3 tests only. Right-button ownership was withdrawn by the
// user's newer instruction; this file is not an active regression suite.
var checks=0,failures=0
func check(_ ok:Bool,_ label:String) {checks+=1;if !ok {failures+=1;print("FAIL "+label)}}
let fixture=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
func state(_ changes:[String:Any]=[:],at:Double=10,tick:Int=100,item:String="minecraft:diamond_sword")->AnchorState {
    var d=fixture;d["age"]=0.0;d["active"]=true;d["using"]=false;d["rightDown"]=false;d["ground"]=true
    d["selected"]=0;d["tick"]=tick;d["useKey"]="key.mouse.right";d["offhand"]="minecraft:shield"
    var slots=d["slots"] as! [[String:Any]];slots[0]["id"]=item;slots[0]["count"]=item=="minecraft:air" ? 0:1;d["slots"]=slots
    var c=d["combat"] as! [String:Any];c["cooldown"]=1.0;c["hurtTime"]=0;c["attackKey"]="key.mouse.left"
    c["target"]=["id":42,"distance":2.4,"range":3.0,"valid":true,"hurtTime":0,"ground":true,"blocking":false]
    d["combat"]=c;for(k,v) in changes {d[k]=v}
    return AnchorState.parse(d,now:at)!
}
for item in ["diamond_sword","diamond_axe","air"] {
    for usage in [["rightDown":true],["using":true],["rightDown":true,"using":true]] {
        let s=state(usage,item:"minecraft:"+item)
        check(SwordController.eligible(s,now:10),"armed melee can resolve use state for "+item)
        var toggle=SwordSwitch();toggle.setEnabled(true,now:9)
        check(toggle.canRun(s,now:10,allowed:true),"toggle remains runnable without a new left press")
        check(!MeleeReadiness.allowsClicker(s,now:10,after:9),"ordinary hold clicker still respects manual right use")
    }
}
func rig()->(SwordController,()->Int,()->Int) {
    let c=SwordController();var clicks=0,releases=0
    c.click={clicks+=1};c.releaseUse={releases+=1;return true}
    return (c,{clicks},{releases})
}
for item in ["diamond_sword","diamond_axe","air"] {
    for usage in [["rightDown":true],["using":true],["rightDown":true,"using":true]] {
        let (c,n,r)=rig(),s=state(usage,item:"minecraft:"+item)
        c.begin(s,now:10);c.tick(s,now:10,allowed:true)
        check(c.held && r()==1 && n()==0,"release use before attacking "+item)
        c.tick(s,now:10.02,allowed:true)
        check(r()==1 && n()==0,"same snapshot never repeats release or attack")
        c.tick(state(at:10.03,tick:100,item:"minecraft:"+item),now:10.03,allowed:true)
        check(n()==0,"same game tick cannot acknowledge use completion")
        c.tick(state(at:10.05,tick:101,item:"minecraft:"+item),now:10.05,allowed:true)
        check(n()==1 && r()==1,"confirmed release resumes automatically without left press "+item)
        c.tick(state(at:10.06,tick:101,item:"minecraft:"+item),now:10.06,allowed:true)
        check(n()==1,"post-release attack still waits for cooldown acknowledgement")
    }
}
do {
    let(c,n,r)=rig();let s=state(["using":true,"rightDown":true])
    c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    for i in 1...10 {
        let t=10+Double(i)*0.05
        c.tick(state(["using":true,"rightDown":true],at:t,tick:100+i),now:t,allowed:true)
    }
    check(r()==3 && n()==0 && c.held,"release retries bounded at three, never blind attacks")
    c.tick(state(["using":true],at:10.65,tick:113),now:10.65,allowed:true)
    check(c.requiresRearm && !c.held && n()==0,"failed native release reports failure rather than hanging indefinitely")
    check(c.message.contains("未生效") && !c.message.contains("使用物品中"),"failure has actionable explanation")
}
do {
    let(c,n,r)=rig();c.releaseUse={false};let s=state(["rightDown":true])
    c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    check(c.requiresRearm && !c.held && n()==0 && r()==0,"input delivery refusal cannot masquerade as successful release")
}
for changed in [["active":false],["selected":1],["world":987654]] {
    let(c,n,r)=rig();c.begin(state(["using":true]),now:10)
    c.tick(state(changed,at:10.02),now:10.02,allowed:true)
    check(!c.held && n()==0 && r()==0,"menu/slot/world transition cancels before right release")
}
for (allowed,time) in [(false,10.01),(true,10.2)] {
    let(c,n,r)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:time,allowed:allowed)
    check(!c.held && n()==0 && r()==0,"stale or unfocused state cannot release user input")
}
do {
    let(c,n,r)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    c.cancel();c.tick(state(at:10.1,tick:102),now:10.1,allowed:true)
    check(n()==0 && r()==1,"off cancels release-to-attack transition")
    c.begin(state(at:10.2,tick:104),now:10.2);c.tick(state(at:10.2,tick:104),now:10.2,allowed:true)
    check(n()==1,"later explicit rearm does not retain old pending release")
}
do {
    let(c,n,r)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    c.tick(state(at:10.7,tick:114),now:10.7,allowed:true)
    check(c.requiresRearm && n()==0 && r()==1,"late clear state cannot conceal expired release handshake")
}
for item in ["stone","golden_apple","respawn_anchor","diamond_pickaxe"] {
    let(c,n,r)=rig();let s=state(["using":true],item:"minecraft:"+item)
    c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    check(!c.held && n()==0 && r()==0,"other held items retain native use: "+item)
}
do {
    let s=state(["using":true,"useKey":"key.keyboard.q"])
    check(!SwordController.eligible(s,now:10),"custom use binding never receives an invented right-release workaround")
}
do {
    var route=SwordRightInput()
    check(route.route(.down,priority:false) == .native,"off keeps right down native")
    check(route.route(.up,priority:false) == .native,"off keeps right up native")
    check(route.route(.down,priority:true) == .consume,"enabled melee suppresses use press")
    check(route.route(.drag,priority:true) == .motion,"right-held camera motion remains usable")
    check(route.route(.up,priority:true) == .consume && !route.paired,"suppressed right press has a paired release")
    check(route.route(.up,priority:false) == .native,"unowned release stays native")
    _=route.route(.down,priority:true)
    check(route.route(.drag,priority:false) == .consume,"held gesture cannot turn into menu drag after focus loss")
    check(route.route(.up,priority:false) == .consume,"disable or weapon change still consumes owned trailing up")
    check(route.route(.down,priority:false) == .native,"fresh press after disable is restored")
    _=route.route(.down,priority:true)
    check(route.route(.down,priority:false) == .native,"lost old release cannot swallow a new native gesture")
    check(route.route(.up,priority:false) == .native,"new native press-release remains paired")
    check(route.route(.drag,priority:true) == .motion && route.paired,"held-before-enable drag is converted to camera motion")
    check(route.route(.up,priority:false) == .consume,"held-before-enable gesture finishes without orphaning use")
}
print("Attack priority checks \(checks), failures \(failures)")
exit(failures==0 ? 0:1)