import Foundation

var checks=0
var failures=0
func expect(_ value:Bool,_ name:String) {checks+=1;if !value {failures+=1;print("FAIL \(name)")}}
func item(_ slot:Int,_ id:Int,_ score:Double=1,kind:String="tool",meta:Int=0,count:Int=1,identity:String?=nil)->HotbarItem {
    HotbarItem(slot:slot,itemID:id,metadata:meta,count:count,identity:identity ?? "\(id):\(meta):none",kind:kind,fullBlock:kind=="block",score:score)
}
func snapshot(_ slots:[HotbarItem],selected:Int=0,hit:String="block",block:Int=121,hardness:Double=3,target:[Int]?=[1,79,2],age:Double=0)->HotbarSnapshot {
    HotbarSnapshot(selected:selected,hitKind:hit,blockID:block,hardness:hardness,target:target,slots:slots,keys:Array(2...10),blockedKeys:[16,18,20,17,30,31,32,57,42,29,-100,-99],age:age)
}
let sword=item(0,267,1,kind:"sword"),pick=item(6,278,26.666),axe=item(3,279),shears=item(8,359)
let endStone=snapshot([sword,pick,axe,shears])
expect(SwordClickEligibility.allows(endStone,sampledAt:100,now:100.05),"Selected sword allows clicking")
for id in [267,268,272,276,283] {
    expect(SwordClickEligibility.allows(snapshot([item(4,id,kind:"sword")],selected:4),sampledAt:100,now:100),"All vanilla sword materials, moved hotbar slot \(id)")
}
for (id,kind) in [(346,"other"),(261,"other"),(322,"other"),(35,"block"),(278,"tool")] {
    expect(!SwordClickEligibility.allows(snapshot([item(0,id,kind:kind),item(4,276,kind:"sword")]),sampledAt:100,now:100),"Non-sword blocks macro even with another sword in hotbar \(id)")
}
expect(!SwordClickEligibility.allows(snapshot([]),sampledAt:100,now:100),"Empty hand never autoclicks")
expect(!SwordClickEligibility.allows(nil,sampledAt:100,now:100),"Absent inventory never autoclicks")
expect(!SwordClickEligibility.allows(endStone,sampledAt:100,now:100.101),"Stale world observation stops clicks")
expect(!SwordClickEligibility.allows(snapshot([sword],age:0.06),sampledAt:100,now:100.05),"Combined packet and inventory age stops clicks")
expect(!SwordClickEligibility.allows(endStone,sampledAt:101,now:100),"Future observation rejected")
expect(!SwordClickEligibility.allows(endStone,sampledAt:.nan,now:100),"Nonfinite observation rejected")
expect(!SwordClickEligibility.allows(snapshot([sword,sword]),sampledAt:100,now:100),"Malformed duplicate inventory rejected")
expect(AutoToolPolicy.choose(endStone)?.slot==6,"Detect moved pickaxe by actual slot")
expect(AutoToolPolicy.choose(snapshot([sword,item(3,279,8),pick],block:5,hardness:2))?.slot==6,"Use observed score, not guessed item rank")
let wool=snapshot([sword,item(6,278),item(8,359,5)],block:35,hardness:0.8)
expect(AutoToolPolicy.choose(wool)?.slot==8,"Wool chooses shears")
expect(AutoToolPolicy.choose(snapshot([sword,pick],selected:6,block:26,hardness:0.2))?.slot==0,"Beds deliberately choose sword")
expect(AutoToolPolicy.choose(snapshot([pick],selected:6,block:26,hardness:0.2))==nil,"No sword: do not guess")
expect(AutoToolPolicy.choose(snapshot([sword,pick],block:26))==nil,"Already holding sword")
expect(AutoToolPolicy.choose(snapshot([sword,pick],hit:"entity"))==nil,"Entity in front of a block must never trigger")
expect(AutoToolPolicy.choose(snapshot([sword,pick],hit:"miss"))==nil,"Air never triggers")
expect(AutoToolPolicy.choose(snapshot([sword,pick],hit:"unknown"))==nil,"Unknown target never triggers")
expect(AutoToolPolicy.choose(snapshot([sword,pick],hardness:-1))==nil,"Unbreakable blocks do not select a tool")
expect(AutoToolPolicy.choose(snapshot([sword,pick],block:46,hardness:0))==nil,"TNT needs no swap")
expect(AutoToolPolicy.choose(snapshot([pick],selected:6))==nil,"Do not switch away from current best tool")
expect(AutoToolPolicy.choose(snapshot([item(6,278,1)]))==nil,"No effective improvement: leave selection")
expect(AutoToolPolicy.choose(snapshot([pick],selected:2))?.slot==6,"Empty hand supported")
expect(!snapshot([sword,sword]).valid,"Reject duplicate slots")
expect(!snapshot([item(9,278)]).valid,"Reject out of range slots")
expect(!snapshot([item(0,278,.nan)]).valid,"Reject NaN scores")
expect(!snapshot([sword],age:0.2).valid,"Reject stale inventory")
expect(HotbarKeys.native(2)==18 && HotbarKeys.native(10)==25,"Map 1 and 9 physical keys")
expect(HotbarKeys.native(-100)==nil,"Unsupported mouse bindings do not become keys")
func bindingSnapshot(key:Int,blocked:[Int],duplicate:Bool=false)->HotbarSnapshot {
    var keys=Array(2...10);keys[6]=key;if duplicate {keys[4]=key}
    return HotbarSnapshot(selected:0,hitKind:"block",blockID:121,hardness:3,target:[1,79,2],slots:[sword,pick],keys:keys,blockedKeys:blocked,age:0)
}
expect(HotbarKeys.selection(6,in:bindingSnapshot(key:18,blocked:[18]),reserved:[])==nil,"E-bound hotbar conflicts with inventory")
expect(HotbarKeys.selection(6,in:bindingSnapshot(key:16,blocked:[16]),reserved:[])==nil,"Q-bound hotbar conflicts with drop")
expect(HotbarKeys.selection(6,in:bindingSnapshot(key:8,blocked:[]),reserved:[26])==nil,"Macro hotkey conflicts are rejected")
expect(HotbarKeys.selection(6,in:bindingSnapshot(key:8,blocked:[],duplicate:true),reserved:[])==nil,"Duplicate hotbar bindings rejected")
expect(HotbarKeys.selection(6,in:bindingSnapshot(key:33,blocked:[16,18]),reserved:[])==3,"Unconflicted remapped hotbar key allowed")

func decision(clicking:Bool=false,bridging:Bool=false,down:Bool=true,enabled:Bool=true,
              time:Double=1.04,world:Int=7,inventory:HotbarSnapshot=endStone)->HotbarItem? {
    var p=AutoToolPress();p.begin(now:1,world:7,inventory:endStone)
    return p.update(now:time,sampledAt:1.02,world:world,inventory:inventory,enabled:enabled,clicking:clicking,bridging:bridging,physicalDown:down)
}
expect(decision()?.slot==6,"Fresh post-press observation permits one selection")
expect(decision(clicking:true)==nil,"Master ON forbids tool selection even while mouse held")
expect(decision(bridging:true)==nil,"Bridge owns inputs")
expect(decision(down:false)==nil,"Physical release cancels")
expect(decision(enabled:false)==nil,"Disabled feature cancels")
expect(decision(time:1.3)==nil,"Stale observation cannot select a tool")
expect(decision(world:8)==nil,"World change cancels")
expect(decision(inventory:snapshot([sword,pick],hit:"entity"))==nil,"New entity hit cancels pending press")
expect(decision(inventory:snapshot([sword,pick],target:[2,79,2]))==nil,"Target motion cancels old press")
var press=AutoToolPress();press.begin(now:1,world:7,inventory:endStone)
expect(press.update(now:1.01,sampledAt:0.99,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Wait for new observation")
expect(press.update(now:1.04,sampledAt:1.02,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)?.slot==6,"Next fresh observation accepted")
expect(press.update(now:1.05,sampledAt:1.03,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Holding cannot spawn repeated tasks")

// Replay a single uninterrupted hardware press across several mined layers.
func held(_ p:inout AutoToolPress,_ time:Double,_ sample:HotbarSnapshot,down:Bool=true,
          enabled:Bool=true,clicking:Bool=false,bridging:Bool=false,world:Int=7)->HotbarItem? {
    p.update(now:time,sampledAt:time-0.005,world:world,inventory:sample,
             enabled:enabled,clicking:clicking,bridging:bridging,physicalDown:down)
}
let woodAfterStone=snapshot([sword,item(6,278),item(3,279,8),shears],selected:6,block:5,target:[1,79,3])
let woolAfterWood=snapshot([sword,item(6,278),axe,item(8,359,5)],selected:3,block:35,target:[1,79,4])
let bedAfterWool=snapshot([sword,item(6,278),axe,shears],selected:8,block:26,target:[1,79,5])
var continuous=AutoToolPress();continuous.begin(now:10,world:7,inventory:endStone)
expect(held(&continuous,10.03,endStone)?.slot==6,"Held mining starts with pickaxe")
expect(held(&continuous,12,woodAfterStone)==nil,"Wait for a fresh confirmation of the new block")
expect(held(&continuous,12.05,woodAfterStone)?.slot==3,"Same press: mined stone reveals wood, choose axe")
expect(held(&continuous,14,woolAfterWood)==nil,"Confirm next wool target")
expect(held(&continuous,14.05,woolAfterWood)?.slot==8,"Same press: wood reveals wool, choose shears")
expect(held(&continuous,16,bedAfterWool)==nil,"Confirm next bed target")
expect(held(&continuous,16.05,bedAfterWool)?.slot==0,"Same press: wool reveals bed, choose sword")
let air=snapshot([sword,pick],hit:"miss",target:nil)
let entity=snapshot([sword,pick],hit:"entity",target:nil)
expect(held(&continuous,17,air)==nil,"Air gap never switches")
expect(held(&continuous,18,entity)==nil,"Entity crossing never switches")
expect(held(&continuous,19,endStone)==nil,"Reconfirm after entity/air gap")
expect(held(&continuous,19.05,endStone)?.slot==6,"Still-held mining resumes after air and entity gaps")
expect(held(&continuous,19.07,endStone)==nil,"Do not repeat an unconfirmed queued selection immediately")
expect(held(&continuous,19.20,endStone)?.slot==6,"Retry a dropped selection while still held")
let correctPick=snapshot([sword,pick],selected:6)
expect(held(&continuous,19.25,correctPick)==nil,"Confirmed correct tool stops redundant selection")
expect(held(&continuous,40,correctPick)==nil,"Long mining hold with correct tool remains quiet")
let replacedInPlace=snapshot([sword,item(6,278),item(3,279,8)],selected:6,block:5,target:[1,79,2])
expect(held(&continuous,41,replacedInPlace)==nil,"Block type changes at same coordinates require confirmation")
expect(held(&continuous,41.05,replacedInPlace)?.slot==3,"Same coordinates with different material reselects tool")
expect(continuous.update(now:41.3,sampledAt:41,world:7,inventory:replacedInPlace,
                        enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Delayed telemetry must not switch tools")
expect(held(&continuous,41.35,endStone)==nil,"Reconfirm fresh target after delayed telemetry")
expect(held(&continuous,41.4,endStone)?.slot==6,"Still-held mining resumes after transient telemetry delay")
expect(continuous.update(now:41.41,sampledAt:41.35,world:7,inventory:replacedInPlace,
                        enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Out-of-order observation cannot revert current target")
expect(held(&continuous,42,replacedInPlace,down:false)==nil,"Physical release ends continuous session")
expect(held(&continuous,43,endStone)==nil,"Observation alone cannot rearm after release")
for reason in 0..<4 {
    var cancelled=AutoToolPress();cancelled.begin(now:50,world:7,inventory:endStone)
    _=held(&cancelled,50.03,endStone)
    expect(held(&cancelled,50.1,woodAfterStone,enabled:reason != 0,clicking:reason == 1,
                bridging:reason == 2,world:reason == 3 ? 8:7)==nil,"Cancel active hold for disabled/master/bridge/world change \(reason)")
    expect(held(&cancelled,51,endStone)==nil,"Cancelled hold needs fresh physical press \(reason)")
}
var unarmed=AutoToolPress()
expect(held(&unarmed,60,endStone)==nil,"Synthetic/down flag without real press cannot arm")
unarmed.begin(now:60,world:7,inventory:entity)
expect(held(&unarmed,60.05,endStone)==nil,"Press that began on an entity does not arm mining")

func woolStack(_ slot:Int,_ count:Int,_ meta:Int=14,_ identity:String?=nil)->HotbarItem {item(slot,35,kind:"block",meta:meta,count:count,identity:identity)}
var supply=BridgeSupplyPolicy()
expect(supply.evaluate(snapshot([woolStack(0,64)]),grounded:true) == .ready,"Full stack preserves normal bridge")
expect(supply.evaluate(snapshot([woolStack(0,4),woolStack(4,64)]),grounded:true) == .select(4),"Select same-colour reserve before next launch")
expect(supply.evaluate(snapshot([woolStack(0,4),woolStack(4,64,11)]),grounded:true) == .insufficient,"Different wool colour forbidden")
expect(supply.evaluate(snapshot([woolStack(0,4),item(4,5,kind:"block",count:64)]),grounded:true) == .insufficient,"Wood cannot replace wool")
expect(supply.evaluate(snapshot([woolStack(0,4),woolStack(4,64,14,"35:14:renamed")]),grounded:true) == .insufficient,"NBT-distinct block is not substituted")
expect(supply.evaluate(snapshot([woolStack(0,4),woolStack(4,4)]),grounded:true) == .insufficient,"Do not rely on midair restock to pool small stacks")
expect(supply.evaluate(snapshot([woolStack(4,64)],selected:4),grounded:true) == .ready,"Confirmed selection permits continuation")
expect(supply.evaluate(snapshot([woolStack(4,64,11)],selected:4),grounded:true) == .invalid,"Mid-run material change rejected")
supply.reset()
expect(supply.evaluate(snapshot([woolStack(4,64,11)],selected:4),grounded:true) == .ready,"Fresh R can choose a different bridge material")
supply.reset();_ = supply.evaluate(snapshot([woolStack(0,64)]),grounded:true)
expect(supply.beforePlacement(snapshot([woolStack(0,1)])) == .insufficient,"Never spend the last held block midair")
expect(supply.beforePlacement(snapshot([woolStack(0,2),woolStack(4,64)])) == .select(4),"Exceptional extra placements can request same-material reserve")
expect(supply.beforePlacement(snapshot([woolStack(0,1),woolStack(4,64,11)])) == .insufficient,"Emergency never substitutes another colour")
expect(supply.beforePlacement(snapshot([woolStack(0,3)])) == .ready,"Normal placement proceeds without changed timing")
let malformed=Data("{\"selected\":\"bad\"}".utf8)
expect((try? JSONDecoder().decode(OptionalObservation<HotbarSnapshot>.self,from:malformed))?.value==nil,"Invalid inventory is isolated from base telemetry")
print("\(failures == 0 ? "PASS":"FAIL") \(checks) inventory and physical-input policy checks; \(failures) failures")
if failures>0 {exit(1)}
