import Foundation
import Darwin
let args=CommandLine.arguments
let reader=GameTelemetry()
reader.needsGeometry=false
var count=0
reader.onState={state,error in
 if let s=state {
  count+=1
  if let i=s.inventory, !s.hasGeometry {
   let info:[String:Any] = ["selected":i.selected,"hit":i.hitKind,"block":i.blockID ?? -1,"age":i.age,"geometry":s.hasGeometry,"choice":AutoToolPolicy.choose(i)?.slot ?? -1,"slots":i.slots.map{["slot":$0.slot,"id":$0.itemID,"meta":$0.metadata,"count":$0.count,"kind":$0.kind,"score":$0.score,"identity":$0.identity] as [String:Any]}]
   if let d=try? JSONSerialization.data(withJSONObject:info,options:[.sortedKeys]) {print(String(decoding:d,as:UTF8.self))}
   reader.stop();exit(0)
  }
  if count>150 {print("ERROR: no inventory after 150 observations");reader.stop();exit(2)}
 }
}
try reader.start(pid:Int32(args[1])!,java:"/Users/a15356015027/Library/Java/JavaVirtualMachines/ms-21.0.12.1/Contents/Home/bin/java",classes:"/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/telemetry/attach",jar:args[2])
DispatchQueue.main.asyncAfter(deadline:.now()+6){reader.stop();print("ERROR: timeout");exit(3)}
RunLoop.main.run()
