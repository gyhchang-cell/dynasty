import AppKit
import ApplicationServices

extension MacroApp {
    @objc func anchorChanged() {
        UserDefaults.standard.set(anchorEnabled.state == .on,forKey:"anchorEnabled")
        anchor.stop("已停止");updateAnchorUI()
    }
    func configureAnchor() {
        anchorEnabled.state=UserDefaults.standard.object(forKey:"anchorEnabled") as? Bool == false ? .off:.on
        anchorEnabled.target=self;anchorEnabled.action=#selector(anchorChanged)
        anchor.select = { [weak self] code in self?.anchorKey(code) }
        anchor.click = { [weak self] in self?.anchorClick() }
        anchor.move = { [weak self] x,y in self?.anchorMove(x,y) }
        anchor.movement = { [weak self] keys in self?.anchorMovement(keys) }
        anchor.release = { [weak self] in self?.releaseAnchorInput() }
        anchor.trace = { [weak self] text in self?.traceBridge("ANCHOR "+text) }
        modernTelemetry.onState = { [weak self] state,error in
            guard let self else{return};self.anchorState=state;self.anchorError=error
            if let state,let item=MeleeReadiness.item(state) {
                self.lastHandReport="最近主手：\(MeleeMainHand.classify(item).label) · 槽 \(state.selected+1)\n物品：\(item.id)"
                self.lastHandReportAt=state.time
            }
            self.refreshClickContext()
            self.anchor.tick(state,now:ProcessInfo.processInfo.systemUptime,allowed:self.anchorAllowed)
            self.serviceSword()
            self.serviceForceSprint()
            if self.bridgeDiagnosticUntil>0 {self.updateBridgeUI()}
        }
    }
    var anchorAllowed:Bool {anchorEnabled.state == .on && bridgeDiagnosticUntil<=ProcessInfo.processInfo.systemUptime && !sessionSuspended && isTargetFront() &&
        NSWorkspace.shared.frontmostApplication?.processIdentifier==modernTelemetry.pid && !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand) &&
        (tap.map{CGEvent.tapIsEnabled(tap:$0)} ?? false)}
    func serviceAnchor() {
        let now=ProcessInfo.processInfo.systemUptime
        guard isTargetFront(),!sessionSuspended,let pid=NSWorkspace.shared.frontmostApplication?.processIdentifier else {
            anchor.stop("已停止 · 游戏失焦");if modernTelemetry.pid != nil {modernTelemetry.stop();anchorState=nil};return
        }
        prepareBridgeConfig(pid:pid,now:now)
        // Keep the gameplay/menu observation available for Control even when
        // both features are switched off; otherwise the hotkey could not re-enable.
        guard modernVersion=="26.1",bridgeConfigPID==pid else {
            anchor.stop("已停止");if modernTelemetry.pid != nil {modernTelemetry.stop();anchorState=nil};return
        }
        if modernTelemetry.pid != pid,now-anchorAttachAt>3 {
            anchorAttachAt=now
            if let resources=Bundle.main.resourceURL {do {try modernTelemetry.start(pid:pid,resources:resources)} catch {
                anchorError=(error as? AnchorFailure)?.reason ?? "高版本组件启动失败"
            }}
        }
        anchor.tick(anchorState,now:now,allowed:anchorAllowed)
        if now-anchorUIAt>0.2 {anchorUIAt=now;updateAnchorUI();updateSprintUI();updateSwordUI()}
    }
    func updateAnchorUI() {
        if anchorEnabled.state != .on {anchorStatus.stringValue="已关闭"}
        else if modernVersion != "26.1" {anchorStatus.stringValue="Java 26.1 · 右键放锚"}
        else if anchor.active {anchorStatus.stringValue=anchor.message}
        else if let failure=anchor.failure {anchorStatus.stringValue=failure}
        else if anchorState?.fresh(ProcessInfo.processInfo.systemUptime) != true {anchorStatus.stringValue=anchorError.isEmpty ? "等待游戏":"等待连接"}
        else {anchorStatus.stringValue=anchor.message}
        anchorStatus.toolTip=anchorError.isEmpty ? anchor.message:anchorError
    }
    func observeAnchorPlacement() {
        guard anchorAllowed,!telly.active,let state=anchorState,AXIsProcessTrusted(),!hardwareMouse.isDown(.left) else{return}
        cancelClicks();releaseSprint();cancelInventoryActions()
        anchor.start(state,now:ProcessInfo.processInfo.systemUptime);updateAnchorUI()
        guard anchor.active else{return}
        anchorRightHeld=true;anchorNativeReleasePending=true
        // End only this native use press before Minecraft's held-use repeat.
        // The physical release is consumed independently from generated clicks.
        DispatchQueue.main.asyncAfter(deadline:.now()+0.040) { [weak self] in self?.releaseAnchorNativePress() }
    }
    func releaseAnchorNativePress() {
        guard anchorNativeReleasePending else{return};anchorNativeReleasePending=false
        if let e=CGEvent(mouseEventSource:source,mouseType:.rightMouseUp,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.right) {anchorEvent(e,up:true)}
    }
    private func anchorEvent(_ event:CGEvent,up:Bool=false) {
        guard let pid=up ? (anchorInputPID ?? modernTelemetry.pid):modernTelemetry.pid,up || anchorAllowed else{return}
        if !up {anchorInputPID=pid}
        event.flags=event.type == .mouseMoved ? .maskNonCoalesced:[];event.setIntegerValueField(.eventSourceUserData,value:eventMarker)
        if event.type == .rightMouseDown || event.type == .rightMouseUp {
            event.setIntegerValueField(.mouseEventDeltaX,value:0);event.setIntegerValueField(.mouseEventDeltaY,value:0)
            if NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {event.post(tap:.cghidEventTap)} else if up {event.postToPid(pid)}
        } else {event.postToPid(pid)}
    }
    func anchorKey(_ code:UInt16) {
        guard let e=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:true) else{return}
        anchorEvent(e);anchorHeldKeys.insert(code)
        DispatchQueue.main.asyncAfter(deadline:.now()+0.012) { [weak self] in
            guard let self,self.anchorHeldKeys.remove(code) != nil,let up=CGEvent(keyboardEventSource:self.source,virtualKey:code,keyDown:false) else{return};self.anchorEvent(up,up:true)
        }
    }
    func anchorMovement(_ keys:Set<UInt16>) {
        let desired=anchorAllowed ? keys:[]
        serviceForceSprint()
        for code in anchorMovementKeys.subtracting(desired) {if let e=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:false) {anchorEvent(e,up:true)}}
        for code in desired.subtracting(anchorMovementKeys) {if let e=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:true) {anchorEvent(e)}}
        anchorMovementKeys=desired;anchorMovementEpoch+=1;let epoch=anchorMovementEpoch
        if !desired.isEmpty {
            DispatchQueue.main.asyncAfter(deadline:.now()+0.075) { [weak self] in
                guard let self,self.anchorMovementEpoch==epoch else{return};self.anchorMovement([])
            }
        }
    }
    func anchorClick() {
        guard let e=CGEvent(mouseEventSource:source,mouseType:.rightMouseDown,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.right) else{return}
        e.setIntegerValueField(.mouseEventClickState,value:1);e.setDoubleValueField(.mouseEventPressure,value:1)
        anchorMouseDown=true;anchorEvent(e)
        DispatchQueue.main.asyncAfter(deadline:.now()+0.016) { [weak self] in self?.releaseAnchorMouse() }
    }
    func anchorMove(_ x:Int,_ y:Int) {
        guard let e=CGEvent(mouseEventSource:source,mouseType:.mouseMoved,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left) else{return}
        e.setIntegerValueField(.mouseEventDeltaX,value:Int64(x));e.setIntegerValueField(.mouseEventDeltaY,value:Int64(y));anchorEvent(e)
    }
    func releaseAnchorMouse() {
        guard anchorMouseDown else{return};anchorMouseDown=false
        if let e=CGEvent(mouseEventSource:source,mouseType:.rightMouseUp,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.right) {anchorEvent(e,up:true)}
    }
    func releaseAnchorInput() {
        anchorMovement([])
        releaseAnchorNativePress()
        releaseAnchorMouse();for code in anchorHeldKeys {if let e=CGEvent(keyboardEventSource:source,virtualKey:code,keyDown:false) {anchorEvent(e,up:true)}};anchorHeldKeys.removeAll()
    }
}
