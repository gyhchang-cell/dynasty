// Appended to the production MacroApp declarations by the test runner.
// The production NSApplication launch / event tap / timers are NOT run.
var checks=0,failures=0
func check(_ ok:Bool,_ name:String) {checks+=1;if !ok {failures+=1;print("FAIL "+name)}}
_ = NSApplication.shared
let owner=MacroApp()
let initial=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
let front=NSWorkspace.shared.frontmostApplication?.processIdentifier
var generatedInputs=0
owner.sword.click={generatedInputs+=1};owner.sword.jump={generatedInputs+=1};owner.sword.forward={_ in generatedInputs+=1}
owner.sword.release={};owner.sword.trace={_ in}
func sample(active:Bool,item:String="minecraft:diamond_sword")->AnchorState {
    var d=initial;d["age"]=0.0;d["active"]=active;d["using"]=false;d["rightDown"]=false;d["selected"]=0
    var slots=d["slots"] as! [[String:Any]];slots[0]["id"]=item;slots[0]["count"]=item=="minecraft:air" ? 0:1;d["slots"]=slots
    return AnchorState.parse(d,now:ProcessInfo.processInfo.systemUptime)!
}
func event(_ type:CGEventType,flags:CGEventFlags)->CGEvent {
    let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:CGPoint(x:321,y:234),mouseButton:.right)!
    e.flags=flags;e.setIntegerValueField(.eventSourceUnixProcessID,value:0)
    e.setIntegerValueField(.mouseEventDeltaX,value:7);e.setIntegerValueField(.mouseEventDeltaY,value:-3)
    e.setIntegerValueField(.mouseEventClickState,value:1)
    return e
}
let types:[CGEventType]=[.rightMouseDown,.rightMouseUp,.rightMouseDragged]
for enabled in [false,true] {for focused in [false,true] {for active in [false,true] {
    owner.sword.cancel();owner.manualPID=focused ? front:pid_t(-1)
    owner.modernVersion="26.1";owner.anchorState=sample(active:active)
    owner.swordSwitch.setEnabled(enabled,now:ProcessInfo.processInfo.systemUptime-1)
    owner.swordEnabled.state=enabled ? .on:.off
    if enabled,let s=owner.anchorState {owner.sword.begin(s,now:ProcessInfo.processInfo.systemUptime)}
    let flagCases:[CGEventFlags]=[[],.maskShift,.maskCommand]
    for type in types {for flags in flagCases {
        let e=event(type,flags:flags),before=e.copy()!,held=owner.sword.held
        check(!owner.handleSword(type,e),"sword handler does not consume right \(type.rawValue)")
        check(e.type==before.type && e.flags==before.flags && e.location==before.location &&
              e.getIntegerValueField(.mouseEventDeltaX)==7 && e.getIntegerValueField(.mouseEventDeltaY)==(-3) &&
              e.getIntegerValueField(.mouseEventButtonNumber)==1,"right event type/flags/button/motion are unchanged")
        check(owner.sword.held==held && owner.swordSwitch.enabled==enabled,"right event does not cancel or toggle auto-left")
    }}
}}}
// Exercise the entire event handler in idle/non-bridge/non-anchor melee states.
owner.anchorEnabled.state = .off;owner.bridgeEnabled.state = .off
owner.swordSwitch.setEnabled(true,now:ProcessInfo.processInfo.systemUptime-1);owner.swordEnabled.state = .on
owner.manualPID=front;owner.modernVersion="26.1"
for item in ["minecraft:diamond_sword","minecraft:diamond_axe","minecraft:golden_apple"] {
    owner.anchorState=sample(active:true,item:item)
    for clicking in [false,true] {
        owner.policy.enabled=clicking
        for type in types {
            let e=event(type,flags:.maskShift)
            let result=owner.handle(type,e)?.takeUnretainedValue()
            check(result != nil && result === e,"full handler passes original right event with clicker=\(clicking)")
            check(e.type==type && e.flags == .maskShift && e.getIntegerValueField(.mouseEventButtonNumber)==1,"full handler leaves right event unmodified")
        }
    }
}
check(generatedInputs==0,"right-event tests generated no combat input")
print("Right integration: \(checks) checks, \(failures) failures; synthetic events only, no event posting or game access")
exit(failures==0 ? 0:1)