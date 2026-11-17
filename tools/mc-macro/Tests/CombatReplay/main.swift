import Foundation
let fixture=try JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
var output:[[String:Any]]=[]
for path in CommandLine.arguments.dropFirst(2) {
 let document=try JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:path))) as! [String:Any]
 let rows=document["samples"] as! [[String:Any]],log=document["log"] as? String ?? ""
 let lines=log.split(separator:"\n")
 let start=lines.first(where:{$0.contains("SWORD HOLD")}).flatMap{Double($0.split(separator:" ")[0])} ?? -.infinity
 let end=lines.first(where:{$0.contains("SWORD END")}).flatMap{Double($0.split(separator:" ")[0])} ?? .infinity
 var events:[[String:Any]]=[],stamp=0.0,tick=0,valid=0,last = -Double.infinity
 let controller=SwordController()
 controller.trace={events.append(["time":stamp,"tick":tick,"event":$0])}
 // Historical recordings omit inventory/cells. These are explicitly fixture
 // assumptions for sword-only controller replay, not reconstructed measurements.
 for row in rows {
  guard let now=row["received"] as? Double,now>=start,now<=end,now>last else{continue};last=now
  var d=fixture;row.forEach{d[$0.key]=$0.value}
  let selected=d["selected"] as! Int
  var slots=fixture["slots"] as! [[String:Any]]
  for i in slots.indices where slots[i]["slot"] as? Int == selected {slots[i]["id"]="minecraft:diamond_sword";slots[i]["count"]=1}
  d["slots"]=slots;d["cells"]=[[Any]]();d.removeValue(forKey:"hit")
  guard let s=AnchorState.parse(d,now:now) else{fatalError("Cannot parse historical sample")}
  stamp=now;tick=s.tick;valid+=1
  if !controller.held && !controller.requiresRearm {controller.begin(s,now:now)}
  controller.tick(s,now:now,allowed:true)
 }
 output.append(["file":path,"samples":valid,"events":events,"requiresRearm":controller.requiresRearm])
}
let data=try JSONSerialization.data(withJSONObject:output,options:[.prettyPrinted,.sortedKeys]);print(String(data:data,encoding:.utf8)!)
