// Read-only event observation in the dedicated game; never posts input.
import AppKit
import ApplicationServices
let expectedPID=Int32(ProcessInfo.processInfo.environment["MC_TEST_PID"] ?? "0")!
guard expectedPID>0 else {exit(2)}
let callback:CGEventTapCallBack = {_,type,event,_ in
    if type == .mouseMoved && NSWorkspace.shared.frontmostApplication?.processIdentifier == expectedPID {
        print(String(format:"%.3f",ProcessInfo.processInfo.systemUptime),
              "pid",event.getIntegerValueField(.eventSourceUnixProcessID),
              "marker",event.getIntegerValueField(.eventSourceUserData),
              "dx",event.getDoubleValueField(.mouseEventDeltaX),
              "dy",event.getDoubleValueField(.mouseEventDeltaY))
        fflush(stdout)
    }
    return Unmanaged.passUnretained(event)
}
guard let tap=CGEvent.tapCreate(tap:.cghidEventTap,place:.headInsertEventTap,
    options:.listenOnly,eventsOfInterest:CGEventMask(1)<<CGEventType.mouseMoved.rawValue,
    callback:callback,userInfo:nil) else {print("No listen permission");exit(1)}
let source=CFMachPortCreateRunLoopSource(kCFAllocatorDefault,tap,0)!
CFRunLoopAddSource(CFRunLoopGetMain(),source,.commonModes)
let timer=Timer(timeInterval:20,repeats:false){_ in CFRunLoopStop(CFRunLoopGetMain())}
RunLoop.main.add(timer,forMode:.common)
print("Read-only mouse observation for20s; no game input")
fflush(stdout)
CFRunLoopRun()
CGEvent.tapEnable(tap:tap,enable:false)
