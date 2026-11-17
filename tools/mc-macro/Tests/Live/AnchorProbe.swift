import AppKit
import ApplicationServices
import Carbon
import Vision
let pid=Int32(ProcessInfo.processInfo.environment["MC_TEST_PID"] ?? "0")!
let args=CommandLine.arguments
let root="/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/anchor-singleplayer"
func pause(_ t:Double) {RunLoop.current.run(until:Date(timeIntervalSinceNow:t))}
func key(_ c:UInt16,_ down:Bool) {let e=CGEvent(keyboardEventSource:nil,virtualKey:c,keyDown:down)!;e.flags=[];e.postToPid(pid)}
func tap(_ c:UInt16) {key(c,true);pause(0.025);key(c,false);pause(0.06)}
func windows()->[[String:Any]] {(CGWindowListCopyWindowInfo([.optionOnScreenOnly],kCGNullWindowID) as? [[String:Any]] ?? []).filter{($0[kCGWindowOwnerPID as String] as? Int)==Int(pid) && ($0[kCGWindowLayer as String] as? Int)==0}}
func snapshot() {
    guard let w=windows().first,let id=w[kCGWindowNumber as String] as? Int else{return}
    let p=Process();p.executableURL=URL(fileURLWithPath:"/usr/sbin/screencapture");p.arguments=["-x","-o","-l",String(id),root+"/raw.png"];try? p.run();p.waitUntilExit()
    print("snapshot",id,"front",NSWorkspace.shared.frontmostApplication?.processIdentifier ?? 0)
}
guard pid>0 else{exit(2)}
if args[1]=="background-key" {
    let code=UInt16(args[2])!,seconds=Double(args[3])!
    for down in [true,false] {
        let e=CGEvent(keyboardEventSource:nil,virtualKey:code,keyDown:down)!;e.flags=[]
        e.setIntegerValueField(.eventSourceUserData,value:0x4D434D4143524F);e.postToPid(pid)
        if down {pause(min(5,max(0,seconds)))}
    }
    exit(0)
}
if args[1]=="background-left" {
    for type in [CGEventType.leftMouseDown,.leftMouseUp] {
        let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left)!
        e.flags=[];e.setIntegerValueField(.mouseEventClickState,value:1);e.setIntegerValueField(.eventSourceUserData,value:0x4D434D4143524F);e.postToPid(pid);pause(0.025)
    }
    exit(0)
}
if args[1]=="snapshot" {snapshot();exit(0)}
if args[1]=="ocr" {
 snapshot()
 let im=NSImage(contentsOfFile:root+"/raw.png")!.cgImage(forProposedRect:nil,context:nil,hints:nil)!
 let r=VNRecognizeTextRequest();r.recognitionLevel = .accurate;try! VNImageRequestHandler(cgImage:im).perform([r])
 let bounds=windows().first![kCGWindowBounds as String] as! [String:Double]
 for t in r.results ?? [] {let b=t.boundingBox;print(t.topCandidates(1).first!.string,String(format:"x=%.0f y=%.0f",b.midX*bounds["Width"]!,(1-b.midY)*bounds["Height"]!))}
 exit(0)
}
if NSWorkspace.shared.frontmostApplication?.processIdentifier != pid {
_ = NSRunningApplication(processIdentifier:pid)?.activate(options:[.activateAllWindows])
let ax=AXUIElementCreateApplication(pid);AXUIElementSetAttributeValue(ax,kAXFrontmostAttribute as CFString,kCFBooleanTrue)
var value:CFTypeRef?
AXUIElementCopyAttributeValue(ax,kAXWindowsAttribute as CFString,&value)
if let window=(value as? [AXUIElement])?.first {AXUIElementPerformAction(window,kAXRaiseAction as CFString)}
pause(0.5)
}
guard NSWorkspace.shared.frontmostApplication?.processIdentifier==pid else{print("CANCEL foreground");exit(3)}
switch args[1] {
case "resume":
    snapshot()
    if let image=NSImage(contentsOfFile:root+"/raw.png")?.cgImage(forProposedRect:nil,context:nil,hints:nil) {
        let request=VNRecognizeTextRequest();request.recognitionLevel = .accurate
        try? VNImageRequestHandler(cgImage:image).perform([request])
        let text=(request.results ?? []).compactMap{$0.topCandidates(1).first?.string}.joined(separator:" ")
        if text.contains("Back to Game") || text.contains("Game Menu") {tap(53)}
    }
case "click":
    let w=windows().first!,b=w[kCGWindowBounds as String] as! [String:Double]
    let point=CGPoint(x:b["X"]!+Double(args[2])!,y:b["Y"]!+Double(args[3])!)
    CGWarpMouseCursorPosition(point)
    CGEvent(mouseEventSource:nil,mouseType:.mouseMoved,mouseCursorPosition:point,mouseButton:.left)?.post(tap:.cghidEventTap);pause(0.12)
    for type in [CGEventType.leftMouseDown,.leftMouseUp] {let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:point,mouseButton:.left)!;e.flags=[];e.setIntegerValueField(.mouseEventClickState,value:1);e.post(tap:.cghidEventTap);pause(0.05)}
case "key":tap(UInt16(args[2])!)
case "sword-toggle","sword-toggle-run","sword-toggle-context":
    func swordKey(_ down:Bool,_ repeated:Bool=false) {
        let e=CGEvent(keyboardEventSource:nil,virtualKey:42,keyDown:down)!;e.flags=[]
        e.setIntegerValueField(.keyboardEventAutorepeat,value:repeated ? 1:0)
        if NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {e.post(tap:.cghidEventTap)} else if !down {e.postToPid(pid)}
    }
    swordKey(true);pause(0.04);swordKey(false)
    if args[1]=="sword-toggle-run" {
        let end=Date(timeIntervalSinceNow:Double(args[2])!)
        while Date()<end && NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {pause(0.01)}
        swordKey(true);pause(0.04);swordKey(false);pause(0.7)
    }
    if args[1]=="sword-toggle-context" {
        func phase(_ label:String) {print("PHASE",label,ProcessInfo.processInfo.systemUptime)}
        phase("active");pause(0.8)
        phase("menu");tap(53);pause(0.25);swordKey(true);pause(0.04);swordKey(false);pause(0.25)
        phase("resume");tap(53);pause(0.8)
        phase("non-sword");tap(19);pause(0.45)
        phase("sword-again");tap(18);pause(0.8)
        phase("right-use")
        let point=CGEvent(source:nil)?.location ?? .zero
        for type in [CGEventType.rightMouseDown,.rightMouseUp] {
            let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:point,mouseButton:.right)!;e.flags=[]
            e.post(tap:.cghidEventTap);pause(type == .rightMouseDown ? 0.45:0.8)
        }
        phase("off");swordKey(true);pause(0.04);swordKey(false);pause(0.8)
    }
case "control":
    for down in [true,false] {
        let e=CGEvent(keyboardEventSource:nil,virtualKey:59,keyDown:down)!;e.type = .flagsChanged;e.flags=down ? .maskControl:[];e.post(tap:.cghidEventTap);pause(0.08)
    }
case "walk":
    key(13,true);pause(args.count>2 ? Double(args[2])! : 1.0);key(13,false);pause(0.2)
case "combat-jump","combat-walk":
    // Isolated singleplayer test: ordinary W, jump and held native left input.
    // Always release test-owned inputs, including on a foreground change.
    let duration=args.count>2 ? Double(args[2])!:0.8
    let point=CGEvent(source:nil)?.location ?? .zero
    func mouse(_ down:Bool) {
        let e=CGEvent(mouseEventSource:nil,mouseType:down ? .leftMouseDown:.leftMouseUp,mouseCursorPosition:point,mouseButton:.left)!
        e.flags=[];e.setIntegerValueField(.mouseEventClickState,value:1)
        if NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {e.post(tap:.cghidEventTap)} else if !down {e.postToPid(pid)}
    }
    func movement(_ code:UInt16,_ down:Bool) {
        let e=CGEvent(keyboardEventSource:nil,virtualKey:code,keyDown:down)!;e.flags=[]
        if NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {e.post(tap:.cghidEventTap)} else if !down {e.postToPid(pid)}
    }
    let attackDelay=args.count>3 ? Double(args[3])!:0
    movement(13,true)
    if args[1]=="combat-jump" {
        pause(0.12);movement(49,true)
        if attackDelay==0 {mouse(true)}
        pause(0.06);movement(49,false)
        if attackDelay>0 {pause(max(0,attackDelay-0.06));mouse(true)}
    } else {mouse(true)}
    let end=Date(timeIntervalSinceNow:max(0,duration-(args[1]=="combat-jump" ? max(0.06,attackDelay):0)))
    while Date()<end && NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {pause(0.01)}
    mouse(false);movement(13,false);pause(0.25)
case "move":
    let e=CGEvent(mouseEventSource:nil,mouseType:.mouseMoved,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left)!
    e.flags=[];e.setIntegerValueField(.mouseEventDeltaX,value:0);e.setIntegerValueField(.mouseEventDeltaY,value:100)
    if args[2]=="twice" {e.postToPid(pid);pause(0.1);e.postToPid(pid)} else if args[2]=="drag" {e.type = .rightMouseDragged;e.postToPid(pid)} else if args[2]=="repeat" {for _ in 0..<5 {e.post(tap:.cghidEventTap);pause(0.08)}} else if args[2]=="offset" {e.location=CGPoint(x:e.location.x,y:e.location.y+100);e.post(tap:.cgSessionEventTap)} else if args[2]=="window" {
        e.setIntegerValueField(.eventTargetUnixProcessID,value:Int64(pid))
        e.setIntegerValueField(.mouseEventWindowUnderMousePointer,value:Int64(windows().first![kCGWindowNumber as String] as! Int))
        e.postToPid(pid)
    } else if args[2]=="private" {
        let source=CGEventSource(stateID:.privateState)!;source.localEventsSuppressionInterval=0
        let other=CGEvent(mouseEventSource:source,mouseType:.mouseMoved,mouseCursorPosition:e.location,mouseButton:.left)!
        other.flags = .maskNonCoalesced;other.setIntegerValueField(.mouseEventDeltaX,value:0);other.setIntegerValueField(.mouseEventDeltaY,value:100);other.postToPid(pid)
    } else if args[2]=="noncoalesced" {e.flags = .maskNonCoalesced;e.postToPid(pid)} else if args[2]=="pid" {e.postToPid(pid)} else {e.post(tap:args[2]=="hid" ? .cghidEventTap:.cgSessionEventTap)}
    pause(0.3)
case "text","command":
    if args[1]=="command" {tap(44);pause(0.1)}
    let text=args[2].hasPrefix("/") && args[1]=="command" ? String(args[2].dropFirst()):args[2]
    for character in text.utf16 {var units=[character];let e=CGEvent(keyboardEventSource:nil,virtualKey:0,keyDown:true)!;e.keyboardSetUnicodeString(stringLength:1,unicodeString:&units);e.postToPid(pid);key(0,false);pause(0.003)}
    if args[1]=="command" {tap(36)}
case "aim-hold":
    let point=CGEvent(source:nil)?.location ?? .zero
    for type in [CGEventType.leftMouseDown,.leftMouseUp] {
        let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:point,mouseButton:.left)!;e.flags=[];e.setIntegerValueField(.mouseEventClickState,value:1);e.post(tap:.cghidEventTap)
        if type == .leftMouseDown {
            let end=Date(timeIntervalSinceNow:2);var step=0
            while Date()<end && NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {
                let move=CGEvent(mouseEventSource:nil,mouseType:.leftMouseDragged,mouseCursorPosition:point,mouseButton:.left)!
                move.flags = .maskNonCoalesced;move.setIntegerValueField(.mouseEventDeltaX,value:step%2==0 ? 1:-1);move.setIntegerValueField(.mouseEventDeltaY,value:0);move.post(tap:.cghidEventTap);step+=1;pause(0.008)
            }
        }
    }
    pause(0.3)
case "trigger","left":
    let point=CGEvent(source:nil)?.location ?? .zero
    let types:[CGEventType]=args[1]=="left" ? [.leftMouseDown,.leftMouseUp]:[.rightMouseDown,.rightMouseUp]
    for (index,type) in types.enumerated() {
        guard NSWorkspace.shared.frontmostApplication?.processIdentifier==pid else{print("CANCEL foreground");exit(3)}
        let e=CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:point,mouseButton:args[1]=="left" ? .left:.right)!;e.flags=[];e.setIntegerValueField(.mouseEventClickState,value:1);e.post(tap:.cghidEventTap);pause(index == 0 ? (args.count>2 ? Double(args[2])! : 0.06):2)
    }
default:break
}
pause(0.2);snapshot()
