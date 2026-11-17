import Foundation
var checks=0,failures=0
func check(_ v:Bool,_ label:String) {checks+=1;if !v {failures+=1;print("FAIL "+label)}}
func state(_ t:Double,_ toggle:Bool=false,_ down:Bool=false,_ running:Bool=false,_ key:String="key.keyboard.left.control",_ world:Int=1)->SprintObservation {
    SprintObservation(time:t,world:world,key:key,toggle:toggle,down:down,sprinting:running)
}
let c=ForceSprintController();var events:[String]=[]
c.key={events.append("\($0):\($1)")}
c.tick(state(1),now:1,enabled:true,allowed:true)
check(events==["59:false","59:true"],"hold starts with a clean press")
c.tick(state(1.05,false,true,true),now:1.05,enabled:true,allowed:true)
check(events.count==2,"healthy sprint never pulses")
c.tick(state(1.12),now:1.12,enabled:true,allowed:true)
check(events.suffix(2)==["59:false","59:true"] && events.count==4,"lost game key restored")
c.tick(state(1.2,false,true),now:1.2,enabled:false,allowed:true)
check(c.ownedKey==nil && events.last=="59:false","disabling releases held input")
c.tick(state(2),now:2,enabled:true,allowed:true)
c.tick(state(2.1,false,true),now:2.1,enabled:true,allowed:false)
check(c.ownedKey==nil,"focus loss releases owned key")
c.tick(state(3),now:3,enabled:true,allowed:true)
c.tick(state(3),now:3.2,enabled:true,allowed:true)
check(c.ownedKey==nil,"stale readout releases owned key")
c.tick(state(4,false,false,false,"key.keyboard.r"),now:4,enabled:true,allowed:true)
check(c.ownedKey==15,"custom sprint key supported")
c.tick(state(4.2,false,false,false,"key.keyboard.left.control"),now:4.2,enabled:true,allowed:true)
check(events.suffix(3)==["15:false","59:false","59:true"],"binding change releases old key first")
c.tick(state(4.3,false,false,false,"key.keyboard.escape"),now:4.3,enabled:true,allowed:true)
check(c.ownedKey==nil,"menu binding cannot be held")
c.tick(state(5),now:5,enabled:true,allowed:true,physicalDown:true)
check(c.ownedKey==nil,"manual custom-key ownership is respected")
events=[]
c.tick(state(6,true),now:6,enabled:true,allowed:true)
check(events==["59:false","59:true"],"toggle mode presses once")
c.tick(state(6.03,true,true),now:6.03,enabled:true,allowed:true)
check(c.ownedKey==nil && events.count==3,"toggle mode releases physical input")
for t in [6.1,6.2,6.5,7.0] {c.tick(state(t,true,true,false),now:t,enabled:true,allowed:true)}
check(events.count==3,"standing or blocked with toggle on never flips it off")
c.tick(state(7.1,true,true),now:7.1,enabled:false,allowed:true)
check(events.suffix(2)==["59:false","59:true"],"disable clears owned toggle")
c.tick(state(7.14,true,false),now:7.14,enabled:false,allowed:true)
check(!c.needsObservation,"toggle clear acknowledged")
events=[]
c.tick(state(8,true),now:8,enabled:true,allowed:true)
for t in [8.03,8.08,8.15,8.3] {c.tick(state(t,true),now:t,enabled:true,allowed:true)}
check(events.count==3,"unconfirmed toggle is not spammed")
c.tick(state(8.32,true,true),now:8.32,enabled:true,allowed:true)
check(events.count==3,"late acknowledgement does not double toggle")
c.pause();events=[]
c.tick(state(9,true,true),now:9,enabled:true,allowed:true)
check(events.isEmpty,"menu-return restored toggle needs no extra keypress")
c.tick(state(9.1,true,false),now:9.1,enabled:true,allowed:true)
check(events.count==2,"menu/world reset re-enables cleared toggle")
c.pause();events=[]
c.tick(state(10,false,false,false,"key.keyboard.left.control",2),now:10,enabled:true,allowed:true)
check(c.ownedKey==59,"new world resumes hold mode")
c.tick(nil,now:10.1,enabled:true,allowed:true)
check(c.ownedKey==nil,"missing readout cannot leave key held")
for raw in ["29","157","key.keyboard.left.control","key.keyboard.right.control","key.keyboard.v"] {
 let cfg=SprintGameConfig.parse("key_key.sprint:\(raw)\nkey_key.inventory:key.keyboard.e\ntoggleSprint:true")
 check(cfg.rawKey==raw && cfg.key != nil && cfg.toggle,"cross-version binding \(raw)")
}
check(SprintGameConfig.parse("key_key.sprint:key.keyboard.e\nkey_key.inventory:key.keyboard.e").key==nil,"inventory conflict rejected")
var capture=SprintContext()
check(!capture.allows(enabled:true,focused:true,captured:true,blocked:false,now:1),"capture must settle")
check(capture.allows(enabled:true,focused:true,captured:true,blocked:false,now:1.1),"stable gameplay capture resumes")
check(!capture.allows(enabled:true,focused:true,captured:false,blocked:false,now:1.11),"menu cursor releases input")
check(!capture.allows(enabled:true,focused:false,captured:true,blocked:false,now:1.2),"other foreground window pauses")
check(!capture.allows(enabled:true,focused:true,captured:true,blocked:false,now:1.3),"focus return needs fresh stable capture")
check(capture.allows(enabled:true,focused:true,captured:true,blocked:false,now:1.4),"focus return resumes")
print("Force sprint checks \(checks), failed \(failures)");exit(failures==0 ? 0:1)
