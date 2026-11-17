import Foundation

var checks=0,failures=0
func check(_ ok:Bool,_ label:String) {checks+=1;if !ok {failures+=1;print("FAIL "+label)}}
let fixture=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
func state(_ changes:[String:Any]=[:],at:Double=10,tick:Int=100,item:String="minecraft:diamond_sword",charge:Double=1)->AnchorState {
    var d=fixture;d["age"]=0.0;d["active"]=true;d["using"]=false;d["rightDown"]=false;d["ground"]=true
    d["selected"]=0;d["tick"]=tick;d["useKey"]="key.mouse.right";d["offhand"]="minecraft:shield"
    var slots=d["slots"] as! [[String:Any]];slots[0]["id"]=item;slots[0]["count"]=item=="minecraft:air" ? 0:1;d["slots"]=slots
    var c=d["combat"] as! [String:Any];c["cooldown"]=charge;c["hurtTime"]=0;c["attackKey"]="key.mouse.left"
    c["target"]=["id":42,"distance":2.4,"range":3.0,"valid":true,"hurtTime":0,"ground":true,"blocking":false]
    d["combat"]=c;for(k,v) in changes {d[k]=v}
    return AnchorState.parse(d,now:at)!
}
func rig()->(SwordController,()->Int) {
    let c=SwordController();var clicks=0;c.click={clicks+=1};return(c,{clicks})
}
for item in ["diamond_sword","diamond_axe","air"] {
    let(c,n)=rig();let s=state(["rightDown":true],item:"minecraft:"+item)
    c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    check(n()==1 && c.held && !c.requiresRearm,"right button alone cannot block automatic left: "+item)
}
for right in [false,true] {
    let(c,n)=rig();let s=state(["using":true,"rightDown":right])
    c.begin(s,now:10)
    for i in 0..<30 {
        let t=10+Double(i)*0.05
        c.tick(state(["using":true,"rightDown":right],at:t,tick:100+i),now:t,allowed:true)
    }
    check(n()==0 && c.held && !c.requiresRearm,"manual use remains native without cancelling switch")
    c.tick(state(["rightDown":right],at:11.5,tick:130),now:11.5,allowed:true)
    check(n()==1 && c.held,"left resumes automatically when actual use ends, even if right remains held")
}
for binding in ["key.keyboard.q","key.mouse.middle","key.keyboard.f"] {
    check(SwordController.eligible(state(["using":true,"useKey":binding]),now:10),"melee activation does not dictate use binding: "+binding)
    let(c,n)=rig();let s=state(["rightDown":true,"useKey":binding]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    check(n()==1,"independent attack ignores use key mapping: "+binding)
}
do {
    let(c,n)=rig();c.begin(state(),now:10);c.tick(state(),now:10,allowed:true)
    check(n()==1,"initial automatic attack")
    c.tick(state(["using":true,"rightDown":true],at:10.05,tick:101),now:10.05,allowed:true)
    c.tick(state(["using":true,"rightDown":true],at:11,tick:120),now:11,allowed:true)
    check(c.held && !c.requiresRearm && n()==1,"manual use prevents false unacknowledged-attack shutdown")
    c.tick(state(at:11.05,tick:121),now:11.05,allowed:true)
    check(n()==2,"consumed attack does not need switch reset after manual use")
}
do {
    let(c,n)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    c.tick(state(at:10.02,tick:100),now:10.02,allowed:true)
    check(n()==0,"same game tick cannot falsely confirm native use ended")
    c.tick(state(at:10.05,tick:101,charge:0.3),now:10.05,allowed:true)
    check(n()==0,"resume still honors weapon cooldown")
    c.tick(state(at:10.7,tick:114),now:10.7,allowed:true)
    check(n()==1,"fresh fully charged observation resumes left attack")
}
for changes in [["active":false],["world":98765],["selected":1]] {
    let(c,n)=rig();c.begin(state(["using":true]),now:10)
    c.tick(state(changes,at:10.05,tick:101),now:10.05,allowed:true)
    check(n()==0 && !c.held,"native use does not bypass menu/world/slot cancellation")
}
for (allowed,time) in [(false,10.01),(true,10.2)] {
    let(c,n)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:time,allowed:allowed)
    check(n()==0 && !c.held,"native use does not bypass focus/freshness")
}
do {
    let(c,n)=rig();let s=state(["using":true]);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    c.cancel();c.tick(state(at:10.05,tick:101),now:10.05,allowed:true)
    check(n()==0,"switch off prevents resume after right release")
    c.begin(state(at:10.1,tick:102),now:10.1);c.tick(state(at:10.1,tick:102),now:10.1,allowed:true)
    check(n()==1,"explicit re-enable remains usable")
}
do {
    let(c,n)=rig();let s=state(["using":true]);c.begin(s,now:10)
    for i in 0..<12000 {let t=10+Double(i)*0.05;c.tick(state(["using":true],at:t,tick:100+i),now:t,allowed:true)}
    check(c.held && !c.requiresRearm && n()==0,"600 simulated seconds of native use does not force release or disable")
    c.tick(state(at:610,tick:12100),now:610,allowed:true)
    check(n()==1,"ending a long native use resumes without another switch press")
}
for item in ["stone","respawn_anchor","golden_apple","diamond_pickaxe"] {
    let(c,n)=rig();let s=state(["rightDown":true],item:"minecraft:"+item);c.begin(s,now:10);c.tick(s,now:10,allowed:true)
    check(!c.held && n()==0,"other items remain excluded: "+item)
}
print("Right independence checks \(checks), failures \(failures)")
exit(failures==0 ? 0:1)