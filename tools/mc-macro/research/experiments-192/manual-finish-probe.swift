import AppKit
import ApplicationServices

// Native input only; observes the candidate's trace to interrupt a real flight.
let env=ProcessInfo.processInfo.environment
let pid=Int32(env["MC_TEST_PID"]!)!
let logURL=URL(fileURLWithPath:env["MC_TEST_APP_LOG"]!)
let kind=env["TEST_MANUAL_KIND"] ?? "mouse"
let wantedPhase=env["TEST_MANUAL_PHASE"] ?? "flight"
let seconds=Double(CommandLine.arguments[1])!
let source=CGEventSource(stateID:.hidSystemState)
var manualDown=false
func key(_ code:UInt16,_ down:Bool,_ repeated:Bool=false) {
    let event=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:down)!
    event.flags=[];event.setIntegerValueField(.keyboardEventAutorepeat,value:repeated ? 1:0)
    event.post(tap:.cghidEventTap)
}
func mouse(_ down:Bool) {
    let event=CGEvent(mouseEventSource:source,mouseType:down ? .rightMouseDown:.rightMouseUp,
                      mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.right)!
    event.flags=[];event.post(tap:.cghidEventTap)
}
func inject() {
    manualDown=true
    if kind=="mouse" || kind=="combo" {
        let e=CGEvent(mouseEventSource:source,mouseType:.mouseMoved,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left)!
        e.setIntegerValueField(.mouseEventDeltaX,value:90);e.setIntegerValueField(.mouseEventDeltaY,value:40)
        e.post(tap:.cghidEventTap)
    }
    if kind=="key" || kind=="combo" {key(13,true)}
    if kind=="button" || kind=="combo" {mouse(true)}
    if kind=="inventory" {key(14,true)}
    if kind=="combo" {
        let e=CGEvent(scrollWheelEvent2Source:source,units:.line,wheelCount:1,wheel1:1,wheel2:0,wheel3:0)!
        e.post(tap:.cghidEventTap)
    }
}
func releaseManual() {
    guard manualDown else {return}
    manualDown=false
    if kind=="key" || kind=="combo" {key(13,false)}
    if kind=="button" || kind=="combo" {mouse(false)}
    if kind=="inventory" {key(14,false)}
}
func run() throws {
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier==pid else {fatalError("not foreground")}
    let handle=try FileHandle(forReadingFrom:logURL);try handle.seekToEnd();defer {try? handle.close()}
    var pending="",lastPose="",stages=Set<String>()
    var interruption:Double?,finishes=0,contacts=0,lastGround:Bool?
    let minimumContacts=Int(env["TEST_MANUAL_MIN_CONTACTS"] ?? "0")!
    let began=ProcessInfo.processInfo.systemUptime
    key(15,true);defer {key(15,false);releaseManual()}
    while ProcessInfo.processInfo.systemUptime-began<seconds {
        guard NSWorkspace.shared.frontmostApplication?.processIdentifier==pid else {print("foreground changed");return}
        let elapsed=ProcessInfo.processInfo.systemUptime-began
        pending+=String(decoding:try handle.readToEnd() ?? Data(),as:UTF8.self)
        let lines=pending.components(separatedBy:"\n");pending=lines.last ?? ""
        for line in lines.dropLast() {
            if line.contains(" POSE ") {
                lastPose=line
                let ground=line.contains(" ground true ")
                if lastGround==false && ground {contacts+=1}
                lastGround=ground
            }
            if line.contains(" FINISH ") {finishes+=1;print("FINISH",elapsed,line)}
        }
        if interruption==nil,elapsed>0.5,contacts>=minimumContacts,lastPose.contains("phase="+wantedPhase),
           (wantedPhase != "flight" || lastPose.contains(" ground false ")) {
            print("INJECT",kind,elapsed,"contacts",contacts,lastPose);inject();interruption=elapsed
        }
        if let interruption {
            let since=elapsed-interruption
            func once(_ name:String,_ threshold:Double,_ body:()->Void) {
                if since>=threshold,!stages.contains(name) {stages.insert(name);body()}
            }
            once("repeat",0.12) {key(15,true,true)}
            if env["TEST_MANUAL_EARLY_REPRESS"]=="1" {
                once("early-up",0.04) {key(15,false)}
                once("early-down",0.08) {key(15,true)}
            }
            once("repeat2",1.0) {key(15,true,true);if kind=="key" || kind=="combo" {key(13,true,true)}}
            once("manual-up",1.3) {releaseManual()}
            once("fresh-up",2.0) {key(15,false);print("FRESH_R_UP",elapsed,"finishes",finishes)}
            once("fresh-down",2.2) {
                guard finishes==1 else {print("NO_RESTART unexpected finish count",finishes);return}
                key(15,true);print("FRESH_R_DOWN",elapsed)
            }
        }
        Thread.sleep(forTimeInterval:0.005)
    }
    print("R released",ProcessInfo.processInfo.systemUptime-began,"injected",interruption != nil)
}
do {try run()} catch {key(15,false);releaseManual();print(error);exit(1)}
