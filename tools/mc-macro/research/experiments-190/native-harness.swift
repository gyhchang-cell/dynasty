import AppKit
import ApplicationServices
let pid: pid_t = Int32(ProcessInfo.processInfo.environment["MC_TEST_PID"] ?? "75548") ?? 75548
let marker: Int64 = 0x4D434D4143524F
let source=CGEventSource(stateID:.privateState)
source?.localEventsSuppressionInterval=0
let inputQueue=DispatchQueue(label:"test.input",qos:.userInteractive)
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

let engine = TellyController()
let camera = GameTelemetry()
engine.coordinateMovement=ProcessInfo.processInfo.environment["TEST_MOVEMENT"]=="1"
engine.forwardPitch=Double(ProcessInfo.processInfo.environment["TEST_PITCH"] ?? "0") ?? 0
engine.risePerJump=Int(ProcessInfo.processInfo.environment["TEST_RISE"] ?? "0") ?? 0

let game = NSRunningApplication(processIdentifier:pid)!
let start = ProcessInfo.processInfo.systemUptime
let seconds = Double(CommandLine.arguments.dropFirst().first ?? "8") ?? 8
let optionsPath=ProcessInfo.processInfo.environment["MC_TEST_OPTIONS"] ?? "/Users/a15356015027/Public/.minecraft/options.txt"
let options = try! String(contentsOfFile:optionsPath,encoding:.utf8)
engine.config = TellyGameConfig.parse(options,path:optionsPath)

var modifiers=BridgeModifiers()
var injectedKeys=Set<UInt16>()
var rightHeld=false
var initialHeading:Double?
var finalState:BridgeWorldState?
func eventKey(_ code: UInt16, _ down: Bool) {
 if down {injectedKeys.insert(code)} else {injectedKeys.remove(code)}
 let e = CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:down)!
 if modifiers.update(code:code,down:down) {e.type = .flagsChanged}
 e.flags=CGEventFlags(rawValue:modifiers.flags)
  inputQueue.async { e.postToPid(pid) }
 print(String(format:"%.3f key %d %@",ProcessInfo.processInfo.systemUptime-start,code,down ? "down":"up"))
}
engine.trace = { print(String(format:"%.3f ",ProcessInfo.processInfo.systemUptime-start)+$0) }
engine.key = eventKey
var testClickIndex=0
engine.mouse = { down in
 rightHeld=down
 if down {
  testClickIndex+=1
  if Int(ProcessInfo.processInfo.environment["TEST_SKIP_CLICK"] ?? "")==testClickIndex {print("INJECT skipped click",testClickIndex);return}
 }
 let e = CGEvent(mouseEventSource:source,mouseType:down ? .rightMouseDown:.rightMouseUp,mouseCursorPosition:CGEvent(source:nil)!.location,mouseButton:.right)!
 e.flags=CGEventFlags(rawValue:modifiers.flags);e.setIntegerValueField(.mouseEventDeltaX,value:0);e.setIntegerValueField(.mouseEventDeltaY,value:0);e.setIntegerValueField(.mouseEventClickState,value:1);e.setDoubleValueField(.mouseEventPressure,value:down ? 1 : 0);inputQueue.async { if ProcessInfo.processInfo.environment["TEST_PID_MOUSE"]=="1" {e.postToPid(pid)} else {e.post(tap:.cgSessionEventTap)} }
 if down { print(String(format:"%.3f CLICK",ProcessInfo.processInfo.systemUptime-start)) }
}
engine.move = { x,y in
 let e = CGEvent(mouseEventSource:source,mouseType:.mouseMoved,mouseCursorPosition:CGEvent(source:nil)!.location,mouseButton:.left)!
 e.flags=CGEventFlags(rawValue:modifiers.flags).union(.maskNonCoalesced);e.setIntegerValueField(.mouseEventDeltaX,value:x);e.setIntegerValueField(.mouseEventDeltaY,value:y);inputQueue.async { if ProcessInfo.processInfo.environment["TEST_GLOBAL_MOVE"]=="1" {e.post(tap:.cgSessionEventTap)} else {e.postToPid(pid)} }
 print(String(format:"%.3f move %d %d",ProcessInfo.processInfo.systemUptime-start,x,y))
}
print("permissions",AXIsProcessTrusted(),CGPreflightScreenCaptureAccess())
if let n=Int64(ProcessInfo.processInfo.environment["TEST_YAW_NUDGE_COUNTS"] ?? "") {engine.move(n,0);inputQueue.sync{}}
engine.press(now:start)
var measuredTiming=BridgeTiming()
var lastTick = -1
var known=Set<F3Block>()
camera.onState={ state,error in
 if let s=state {
  measuredTiming.observe(s)
  if initialHeading==nil {initialHeading=TellyController.openingHeading(s.pose.yaw)}
  finalState=s
  let p=s.pose
  if s.tick != lastTick {
   print(String(format:"%.3f pose %.4f %.4f %.4f yaw %.2f pitch %.2f ground %@ v %.3f %.3f %.3f face %@ target %@",ProcessInfo.processInfo.systemUptime-start,p.x,p.y,p.z,p.yaw,p.pitch,String(s.onGround),s.velocity.0,s.velocity.1,s.velocity.2,s.face ?? "nil",String(describing:p.looking)))
   print("USE",String(format:"%.3f",ProcessInfo.processInfo.systemUptime-start),s.useDown,s.clickDelay,s.eyeHeight,String(describing:s.useHit),s.useFace ?? "nil","sprint",s.sprinting as Any,"control",s.controlDown as Any)
   print("PLAN",String(format:"%.3f",ProcessInfo.processInfo.systemUptime-start),engine.diagnostic,"frameP90",measuredTiming.frameInterval)
   lastTick=s.tick
  }
  let added=s.solid.subtracting(known).filter{$0.y>70}
  if !added.isEmpty {print("BLOCKS",String(format:"%.3f",ProcessInfo.processInfo.systemUptime-start),added)}
  known.formUnion(s.solid)
 }
 if let delay=Double(ProcessInfo.processInfo.environment["TEST_DELAY_MS"] ?? ""),delay>0 {
 DispatchQueue.main.asyncAfter(deadline:.now()+delay/1000) {engine.observeWorld(state,error:error,now:ProcessInfo.processInfo.systemUptime)}
 } else {engine.observeWorld(state,error:error,now:ProcessInfo.processInfo.systemUptime)}
}
try camera.start(pid:pid,java:"/Users/a15356015027/Library/Java/JavaVirtualMachines/ms-21.0.12.1/Contents/Home/bin/java",classes:"/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/telemetry/attach",jar:ProcessInfo.processInfo.environment["MC_TEST_AGENT"] ?? "/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/telemetry/state-agent.jar")
var lastMessage=""
var released=false
var idleAt:Double?
var lastPhase=engine.phase
var phaseStarted=ProcessInfo.processInfo.systemUptime
let releasePhase=ProcessInfo.processInfo.environment["TEST_RELEASE_PHASE"]
let releaseDelay=Double(ProcessInfo.processInfo.environment["TEST_RELEASE_DELAY"] ?? "0") ?? 0
var testModeEvents=Set<Int>()
let timer = Timer.scheduledTimer(withTimeInterval:0.008,repeats:true) { _ in
 let now=ProcessInfo.processInfo.systemUptime
 if ProcessInfo.processInfo.environment["TEST_SWITCH"]=="1" {
  for t in [3,7] where now-start>=Double(t) && !testModeEvents.contains(t) {
   engine.risePerJump=t==3 ? 1:0;testModeEvents.insert(t);print("MODE",engine.risePerJump)
  }
 }
 if engine.phase != lastPhase {lastPhase=engine.phase;phaseStarted=now}
 let phaseReady=releasePhase == nil || (String(describing:engine.phase)==releasePhase! && now-phaseStarted>=releaseDelay)
 if now-start>seconds && phaseReady && !released {released=true;print("RELEASE",now-start,"phase",engine.phase);engine.release()}
 if engine.phase == .idle && idleAt == nil {idleAt=now; print("STOPPED",now-start,engine.message)}
 if (idleAt.map{now-$0>0.6} ?? false) || now-start>seconds+4 {
  print("END",String(format:"%.3f",now-start),engine.message)
  engine.stop(engine.message);camera.stop();inputQueue.sync{}
  if let state=finalState,let heading=initialHeading {
   let yawError=abs(F3Pose.angle(state.pose.yaw-heading))
   let pitchError=abs(state.pose.pitch-engine.forwardPitch)
   let checks:[String:Any] = ["grounded":state.onGround,"yaw_error_degrees":yawError,
      "pitch_error_degrees":pitchError,"keys_released":injectedKeys.isEmpty,"right_released":!rightHeld,
      "pose_age_ms":(now-state.pose.time)*1000,
      "safe_aligned_finish":state.onGround && yawError<1 && pitchError<1 && injectedKeys.isEmpty && !rightHeld]
   if let data=try? JSONSerialization.data(withJSONObject:checks,options:[.sortedKeys]),let json=String(data:data,encoding:.utf8) {print("FINAL_CHECK",json)}
  }
  print("FINAL",engine.message); exit(0)
 }
 let active = NSWorkspace.shared.frontmostApplication?.processIdentifier == pid
 engine.tick(now:now,active:active,minimum:15,maximum:Double(ProcessInfo.processInfo.environment["TEST_CPS_MAX"] ?? "18") ?? 18)
 if engine.message != lastMessage { print("STATE",engine.message);lastMessage=engine.message }
}
RunLoop.main.run()
