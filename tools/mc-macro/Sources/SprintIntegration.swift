import AppKit
import ApplicationServices

extension MacroApp {
    func configureForceSprint() {
        forceSprint.key = { [weak self] code,down in self?.postForceSprint(code:code,down:down) }
        forceSprint.trace = { [weak self] line in self?.traceBridge("SPRINT "+line) }
    }
    var wantsSprintObservation:Bool {modernVersion == "26.1" && (sprint.state == .on || forceSprint.needsObservation) && !sessionSuspended && isTargetFront()}
    func serviceForceSprint() {
        let now=ProcessInfo.processInfo.systemUptime
        let foreground=NSWorkspace.shared.frontmostApplication?.processIdentifier
        guard bridgeDiagnosticUntil<=now,!sessionSuspended,isTargetFront(),!CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand),
              tap.map({CGEvent.tapIsEnabled(tap:$0)}) == true else {forceSprint.pause();releaseSprint();sprintTelemetry.stop();sprintCaptureAt=nil;sprintCapture.pause(now:now);return}
        guard let foreground else{return}
        prepareBridgeConfig(pid:foreground,now:now)
        if modernVersion == "26.1",modernTelemetry.pid==foreground {
            sprintTelemetry.stop()
            releaseSprint()
            let fresh=modernVersion=="26.1" && modernTelemetry.pid==foreground && anchorState?.fresh(now)==true
            let observation=anchorState?.sprint
            let code=observation.flatMap{SprintGameConfig.binding($0.key)}
            let physical=code.map{![UInt16(59),62].contains($0) && CGEventSource.keyState(.hidSystemState,key:$0)} ?? false
            forceSprint.tick(observation,now:now,enabled:sprint.state == .on && !anchor.repositioning,allowed:fresh,physicalDown:physical)
        } else {
            // All other Java clients share the native input path. Read their
            // logical key state instead of assuming version-specific player names.
            releaseSprint()
            guard bridgeConfigPID==foreground,let config=sprintGameConfig,let code=config.key,
                  !config.menuKeys.contains(code) else {forceSprint.pause();return}
            if sprintTelemetry.expired(now:now) {sprintTelemetry.stop()}
            if sprintTelemetry.pid != foreground,now-sprintAttachAt>3,let runtime=bridgeRuntime,
               let jar=Bundle.main.resourceURL?.appendingPathComponent("telemetry/sprint-agent.jar") {
                sprintAttachAt=now
                try? sprintTelemetry.start(pid:foreground,java:URL(fileURLWithPath:runtime.java),classes:runtime.classes,jar:jar)
            }
            guard sprintTelemetry.pid==foreground,let down=sprintTelemetry.down,
                  now-sprintTelemetry.time<0.15 else {forceSprint.pause();sprintCaptureAt=nil;sprintCapture.pause(now:now);return}
            if !sprintTelemetry.captured {sprintCaptureAt=nil}
            if sprintTelemetry.captured,sprintCaptureAt==nil {
                sprintCaptureAt=now;bridgeConfigAt=0
                prepareBridgeConfig(pid:foreground,now:now)
            }
            let capture=sprintCapture.allows(enabled:true,focused:true,captured:sprintTelemetry.captured,
                                             blocked:anchor.active || telly.active,now:now)
            if let capturedAt=sprintCaptureAt,bridgeConfigAt<capturedAt,!bridgeConfigPending {
                bridgeConfigAt=0;prepareBridgeConfig(pid:foreground,now:now)
            }
            // A menu may have rebound the key. Refresh options after capture
            // returns and wait for that read before sending any native input.
            guard capture,let capturedAt=sprintCaptureAt,bridgeConfigAt>=capturedAt else{forceSprint.pause();return}
            // Preserve the raw game's binding; physical-to-native conversion
            // remains centralized in SprintGameConfig.
            let raw=config.rawKey ?? ""
            let observation=SprintObservation(time:sprintTelemetry.time,world:Int(foreground),key:raw,toggle:sprintTelemetry.toggle,down:down,sprinting:false)
            forceSprint.tick(observation,now:now,enabled:sprint.state == .on,allowed:true,
                             physicalDown:![UInt16(59),62].contains(code) && CGEventSource.keyState(.hidSystemState,key:code))
        }
    }
    func postForceSprint(code:UInt16,down:Bool) {
        let pid:pid_t?
        if down {
            guard isTargetFront(),!sessionSuspended,let target=bridgeConfigPID,
                  NSWorkspace.shared.frontmostApplication?.processIdentifier==target else{return}
            pid=target;forceSprintPID=target
        } else {pid=forceSprintPID}
        guard let pid,let event=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:down) else{return}
        let masks:[UInt16:CGEventFlags]=[59:.maskControl,62:.maskControl,56:.maskShift,60:.maskShift,58:.maskAlternate,61:.maskAlternate]
        event.flags=[]
        if let mask=masks[code] {event.type = .flagsChanged;if down {event.flags=mask.union(CGEventFlags(rawValue:code==59 ? 1:(code==62 ? 0x2000:0)))}}
        event.setIntegerValueField(.eventSourceUserData,value:eventMarker)
        event.postToPid(pid)
    }
    // A Control press belongs to the app only while gameplay is active.
    // Swallow its paired release even if focus changes, and ignore our marked events.
    func handleSprintControl(_ type:CGEventType,_ event:CGEvent)->Bool {
        guard type == .flagsChanged,[Int64(59),62].contains(event.getIntegerValueField(.keyboardEventKeycode)) else{return false}
        if !event.flags.contains(.maskControl) {
            let consumed=controlSprintSuppressed;controlSprintHeld=false;controlSprintSuppressed=false;return consumed
        }
        guard !controlSprintHeld else{return controlSprintSuppressed}
        controlSprintHeld=true
        let now=ProcessInfo.processInfo.systemUptime
        let ready=(modernVersion=="26.1" && anchorState?.fresh(now)==true) ||
            (bridgeWorldPreview.map{now-$0.pose.time<0.15} ?? false) ||
            (bridgeConfigPID==NSWorkspace.shared.frontmostApplication?.processIdentifier && sprintGameConfig?.key != nil && sprintTelemetry.pid==bridgeConfigPID && sprintTelemetry.captured && now-sprintTelemetry.time<0.15)
        guard isTargetFront(),ready,!telly.active,!event.flags.contains(.maskCommand),!event.flags.contains(.maskAlternate) else{return false}
        controlSprintSuppressed=true
        sprint.state=sprint.state == .on ? .off:.on;sprintChanged()
        traceBridge("SPRINT CONTROL enabled=\(sprint.state == .on)");return true
    }
    func updateSprintUI() {
        let modern=modernVersion == "26.1"
        sprintKey.isHidden=true
        let fresh=ProcessInfo.processInfo.systemUptime-sprintTelemetry.time<0.15
        let generic = !fresh || sprintTelemetry.down == nil ? "等待疾跑连接":(!sprintTelemetry.captured ? "已暂停":forceSprint.message)
        sprintStateLabel.stringValue="⌃ · "+(sprint.state == .off ? "已关闭":(modern ? forceSprint.message:generic))
        sprint.toolTip="Control 独立切换强制疾跑；按当前实例键位及按住/切换设置维持疾跑请求；受游戏原生规则限制。"
    }
}
