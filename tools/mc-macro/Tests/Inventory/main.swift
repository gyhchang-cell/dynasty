import Foundation

var checks=0
func expect(_ value:Bool,_ name:String) {precondition(value,name);checks+=1}
func item(_ slot:Int,_ id:Int,_ score:Double=1,kind:String="tool",meta:Int=0,count:Int=1,identity:String?=nil)->HotbarItem {
    HotbarItem(slot:slot,itemID:id,metadata:meta,count:count,identity:identity ?? "\(id):\(meta):none",kind:kind,fullBlock:kind=="block",score:score)
}
func snapshot(_ slots:[HotbarItem],selected:Int=0,hit:String="block",block:Int=121,hardness:Double=3,target:[Int]?=[1,79,2],age:Double=0)->HotbarSnapshot {
    HotbarSnapshot(selected:selected,hitKind:hit,blockID:block,hardness:hardness,target:target,slots:slots,keys:Array(2...10),blockedKeys:[16,18,20,17,30,31,32,57,42,29,-100,-99],age:age)
}
let sword=item(0,267,1,kind:"sword"),pick=item(6,278,26.666),axe=item(3,279),shears=item(8,359)
let endStone=snapshot([sword,pick,axe,shears])
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
expect(decision(time:1.3)==nil,"Old press expires")
expect(decision(world:8)==nil,"World change cancels")
expect(decision(inventory:snapshot([sword,pick],hit:"entity"))==nil,"New entity hit cancels pending press")
expect(decision(inventory:snapshot([sword,pick],target:[2,79,2]))==nil,"Target motion cancels old press")
var press=AutoToolPress();press.begin(now:1,world:7,inventory:endStone)
expect(press.update(now:1.01,sampledAt:0.99,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Wait for new observation")
expect(press.update(now:1.04,sampledAt:1.02,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)?.slot==6,"Next fresh observation accepted")
expect(press.update(now:1.05,sampledAt:1.03,world:7,inventory:endStone,enabled:true,clicking:false,bridging:false,physicalDown:true)==nil,"Holding cannot spawn repeated tasks")

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
print("PASS \(checks) inventory and physical-input policy checks")
