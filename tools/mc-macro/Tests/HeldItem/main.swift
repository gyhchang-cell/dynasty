import Foundation

var checks=0,failures=0
func check(_ value:Bool,_ name:String) {checks+=1;if !value {failures+=1;print("FAIL "+name)}}
let original=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
func state(_ changes:[String:Any]=[:],item:String="minecraft:diamond_sword",combat:Bool=true)->AnchorState {
    var d=original;d["age"]=0.0;d["active"]=true;d["mouseReady"]=false;d["using"]=false;d["rightDown"]=false;d["selected"]=0
    var slots=d["slots"] as! [[String:Any]];slots[0]["id"]=item;slots[0]["count"]=item=="minecraft:air" ? 0:1;d["slots"]=slots
    if !combat {d.removeValue(forKey:"combat")}
    for (key,value) in changes {d[key]=value}
    return AnchorState.parse(d,now:10)!
}
for item in ["diamond_sword","netherite_sword","diamond_axe","air"] {
    check(SwordController.eligible(state(item:"minecraft:"+item),now:10),"stationary captured gameplay supports "+item)
}
check(!SwordController.eligible(state(["active":false]),now:10),"inactive/menu remains protected")
for change in [["using":true],["rightDown":true]] {
    check(SwordController.eligible(state(change),now:10),"explicit melee can resolve right use")
    check(!MeleeReadiness.allowsClicker(state(change),now:10,after:9),"ordinary clicker does not interrupt item use")
}
check(!SwordController.eligible(state(),now:10.2),"stale sword remains blocked")
check(!SwordController.eligible(state(combat:false),now:10),"missing combat never permits attack")
check(!SwordController.eligible(state(item:"minecraft:stone"),now:10),"nonweapon remains blocked")
check(MeleeReadiness.problem(state(combat:false),now:10)=="已识别剑 · 战斗读数缺失","missing combat is not mislabeled as no sword")
check(MeleeReadiness.problem(state(["active":false]),now:10)=="已识别剑 · 菜单或失焦暂停","menu keeps observed item identity separate")
check(MeleeReadiness.allowsClicker(state(),now:10,after:9),"modern sword clicker uses modern state")
check(!MeleeReadiness.allowsClicker(state(),now:10,after:10.01),"pre-slot-change observation cannot click")
for item in ["diamond_axe","air","stone","diamond_pickaxe"] {
    check(!MeleeReadiness.allowsClicker(state(item:"minecraft:"+item),now:10,after:9),"legacy clicker still sword-only: "+item)
}
check(MeleeReadiness.problem(state(),now:10.2)?.contains("过期")==true,"stale data correctly labeled")
check(MeleeReadiness.problem(nil,now:10)?.contains("连接")==true,"missing connection correctly labeled")
var clicks=0
let c=SwordController();c.click={clicks+=1}
c.begin(state(["ground":true]),now:10);c.tick(state(["ground":true]),now:10,allowed:true)
check(clicks==1,"actual controller can attack without a post-focus camera move")
for slot in 0..<9 {
    var slots=original["slots"] as! [[String:Any]]
    for i in slots.indices {slots[i]["id"]="minecraft:air";slots[i]["count"]=0}
    slots[slot]["id"]="minecraft:diamond_sword";slots[slot]["count"]=1
    let s=state(["slots":slots,"selected":slot])
    check(MeleeMainHand.classify(MeleeReadiness.item(s)) == .sword,"actual selected slot \(slot) identifies sword")
    check(SwordController.eligible(s,now:10),"sword remains eligible in moved hotbar slot \(slot)")
}
check(MeleeMainHand.classify(AnchorItem(slot:0,id:"minecraft:air",count:1,full:false)) == .unknown,"malformed air stack not empty hand")
do {
    var elapsed=0.0,accepted=0
    for _ in 0..<12000 {
        elapsed+=0.05
        var packet=original;packet["age"]=0.0;packet["active"]=true;packet["mouseReady"]=false
        packet["using"]=false;packet["rightDown"]=false
        if let s=AnchorState.parse(packet,now:10+elapsed),SwordController.eligible(s,now:10+elapsed) {accepted+=1}
    }
    check(accepted==12000,"600 simulated seconds of stationary fresh sword observations remain eligible")
}
print("Held item checks \(checks), failures \(failures)")
exit(failures==0 ? 0:1)