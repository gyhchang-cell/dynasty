import Foundation
let path=CommandLine.arguments[1]
let source=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:path))) as! [String:Any]
var cases:[[String:Any]]=[]
for level in 0...2 {
 var d=source;d["age"]=0.0;d["active"]=true;d["mouseReady"]=true
 d["movementUsable"]=true;d["movementDown"]=false;d["movementKeys"]=["key.keyboard.w","key.keyboard.s","key.keyboard.a","key.keyboard.d"]
 d["position"]=[0.5,65.0,0.5];d["eye"]=[0.5,66.62,0.5];d["velocity"]=[0.0,0.0,0.0]
 d["volume"]=[-5,5,60,70,-5,5];d["palette"]=["minecraft:obsidian","minecraft:stone"]
 var cells:[[Any]]=[]
 for x in -5...5 {for z in -5...5 {cells.append([x,64,z,0,1,-1])}}
 if level==1 {cells.append([0,65,3,1,1,-1])}
 if level==2 {for y in 65...67 {cells.append([0,y,4,1,1,-1])}}
 d["cells"]=cells
 d["hit"]=level==2 ? ["pos":[0,67,4],"face":"NORTH","point":[0.5,67.1,4.0]]:["pos":[0,64+level,3],"face":"UP","point":[0.5,Double(65+level),3.5]]
 let state=AnchorState.parse(d,now:10)!,started=ProcessInfo.processInfo.systemUptime
 do {
  let p=try AnchorPlan.make(state,now:10),ms=(ProcessInfo.processInfo.systemUptime-started)*1000
  let result:[String:Any]=["level":level,"success":true,"position":p.origin,"move":AnchorRay.distance(p.origin,p.triggerOrigin),"steps":p.placements.map{["block":[$0.block.x,$0.block.y,$0.block.z],"support":[$0.support.x,$0.support.y,$0.support.z],"face":$0.face] as [String:Any]},"planning_ms":ms]
  cases.append(result);print(result)
 } catch {cases.append(["level":level,"success":false,"reason":String(describing:error)]);print(level,error)}
 let data=try! JSONSerialization.data(withJSONObject:d,options:[.prettyPrinted,.sortedKeys]);try! data.write(to:URL(fileURLWithPath:"research/high-anchor-20261103/fixture-\(level).json"))
}
let data=try! JSONSerialization.data(withJSONObject:cases,options:[.prettyPrinted,.sortedKeys]);try! data.write(to:URL(fileURLWithPath:"research/high-anchor-20261103/planner-results.json"))
