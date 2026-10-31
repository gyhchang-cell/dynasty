import AppKit
import ApplicationServices

extension MacroApp {
    @objc func showBridgeSettings() { showSettings() }

    func setBridgeMode(_ mode:BridgeMode) {
        bridgeMode=mode;telly.risePerJump=mode.rise
        UserDefaults.standard.set(mode.rawValue,forKey:"bridgeMode")
        bridgeModePicker.selectItem(at:mode == .level ? 0:1)
        traceBridge("MODE "+mode.rawValue+" nextJump="+String(telly.active))
        updateBridgeUI()
    }
    @objc func bridgeModeChanged() {setBridgeMode(bridgeModePicker.indexOfSelectedItem==0 ? .level:.rising)}

    @objc func bridgeChanged() {
        UserDefaults.standard.set(bridgeEnabled.state == .on, forKey: "bridgeEnabled")
        telly.stop("搭路设置已更新，松开 R 后重新开始。")
        gameTelemetry.stop(); f3Capture.reset(); updateBridgeUI()
    }
    @objc func stopBridge() { telly.stop("已手动停止搭路，松开 R 后重新开始。"); gameTelemetry.stop(); updateBridgeUI() }
    @objc func testBridgeReading() {
        telly.stop("读取测试：请在 15 秒内切回游戏；不会移动或点击。")
        bridgeDiagnosticUntil = ProcessInfo.processInfo.systemUptime + 15
        bridgePreview = nil; bridgeWorldPreview=nil; gameTelemetry.stop(); f3Capture.reset(); updateBridgeUI()
    }
    @objc func requestScreenPermission() {
        _ = CGRequestScreenCaptureAccess()
        updateBridgeUI()
    }
    @objc func openScreenPermission() { openPrivacy("Privacy_ScreenCapture") }

    func updateBridgeUI() { updateBridgeDashboard() }

    func serviceBridge() {
        let now=ProcessInfo.processInfo.systemUptime
        if (telly.held || telly.restartRequiresRelease) && !CGEventSource.keyState(.hidSystemState,key:15) {telly.release()}
        if bridgeTraceMessage != telly.message {bridgeTraceMessage=telly.message;traceBridge("STATE "+telly.message)}
        if bridgeDiagnosticUntil>0 && now>bridgeDiagnosticUntil {
            bridgeDiagnosticUntil=0;telly.stop("状态读取超时，请确认正在运行原版 Java 1.8.9。");gameTelemetry.stop();updateBridgeUI()
        }
        let diagnostic=bridgeDiagnosticUntil>0
        let bridging=telly.active && telly.phase != .idle
        let tooling=wantsToolObservation
        gameTelemetry.needsGeometry=diagnostic || bridging
        guard diagnostic || bridging || tooling else {
            if gameTelemetry.pid != nil {gameTelemetry.stop()}
            if f3Capture.running {f3Capture.reset()}
            return
        }
        if now-bridgeAccessCheckedAt>0.5 {
            let began=ProcessInfo.processInfo.systemUptime
            bridgeAccessAllowed=AXIsProcessTrusted();bridgeAccessCheckedAt=now
            let elapsed=ProcessInfo.processInfo.systemUptime-began
            if elapsed>0.003 {traceBridge("LOOP ax_ms=\(elapsed*1000)")}
        }
        let active=isTargetFront() && !sessionSuspended && bridgeAccessAllowed
            && !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand)
            && (tap.map{CGEvent.tapIsEnabled(tap:$0)} ?? false)
        guard active,let pid=NSWorkspace.shared.frontmostApplication?.processIdentifier else {
            cancelInventoryActions()
            if !diagnostic {telly.stop("游戏不在前台或输入权限未就绪，已停止搭路。");gameTelemetry.stop()}
            return
        }
        prepareBridgeConfig(pid:pid,now:now)
        if let runtime=bridgeRuntime {
            if gameTelemetry.pid != pid {
                do {try gameTelemetry.start(pid:pid,java:runtime.java,classes:runtime.classes,jar:runtime.jar)}
                catch {telly.stop("无法启动本地状态读取，未开始移动。");bridgeDiagnosticUntil=0;updateBridgeUI();return}
            }
        } else if bridgeRuntimeChecked && !bridgeConfigPending {
            telly.stop("未找到状态组件或本机 JDK 9 以上环境，未开始移动。");bridgeDiagnosticUntil=0;updateBridgeUI();return
        }
        if telly.active {telly.tick(now:now,active:active && bridgeEnabled.state == .on,minimum:cpsMax,maximum:cpsMax)}
        if now-bridgeUIAt>0.25 {bridgeUIAt=now;updateBridgeUI()}
    }

    func prepareBridgeConfig(pid: pid_t, now: TimeInterval) {
        if bridgeConfigPID != pid { telly.config = nil }
        if !bridgeConfigPending && (bridgeConfigPID != pid || now - bridgeConfigAt > 2) {
            bridgeConfigPending = true
            let findRuntime = !bridgeRuntimeChecked
            bridgeRuntimeChecked=true
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                guard let self else { return }
                let directory = TellyGameConfig.gameDirectory(command: self.commandLine(pid))
                let runtime=findRuntime ? Bundle.main.resourceURL.flatMap{GameTelemetry.Runtime.locate(resources:$0)} : nil
                let path = directory.map { URL(fileURLWithPath: $0).appendingPathComponent("options.txt").path }
                let config = path.flatMap { path -> TellyGameConfig? in
                    guard let data = FileManager.default.contents(atPath: path) else { return nil }
                    return TellyGameConfig.parse(String(decoding: data, as: UTF8.self), path: path)
                }
                DispatchQueue.main.async {
                    self.bridgeConfigPending = false; self.bridgeConfigAt = ProcessInfo.processInfo.systemUptime
                    self.bridgeConfigPID = pid; self.telly.config = config
                    if findRuntime {self.bridgeRuntime=runtime}
                }
            }
        }
    }

    // Keep the established Java-targeted motion path. Session-tap mouse
    // motion changed camera delivery latency relative to the game tick.
    // Every queued input remains gated by the active game and input epoch.
    private func postBridgeEvent(_ event: CGEvent, release: Bool = false, session:Bool=false) {
        guard let pid=bridgeConfigPID else { return }
        let gate=bridgeInputEpoch, token=gate.snapshot()
        let queuedAt=ProcessInfo.processInfo.systemUptime
        bridgeInputQueue.async { [weak self] in
            guard release || (gate.accepts(token) && NSWorkspace.shared.frontmostApplication?.processIdentifier == pid) else { return }
            if !release {
                switch gate.authorize(token,queuedAt:queuedAt,now:ProcessInfo.processInfo.systemUptime) {
                case .send:break
                case .cancelled:return
                case .expired:
                    DispatchQueue.main.async {self?.telly.stop("系统输入排队超过安全时间，已取消剩余动作；恢复后重新按 R。");self?.gameTelemetry.stop()}
                    return
                }
            }
            if session {event.post(tap:.cgSessionEventTap)} else {event.postToPid(pid)}
        }
    }

    func postBridgeMouse(down: Bool) {
        guard !down || (isTargetFront() && !sessionSuspended) else { return }
        guard let event=CGEvent(mouseEventSource:source,mouseType:down ? .rightMouseDown:.rightMouseUp,
            mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.right) else { return }
        event.flags=CGEventFlags(rawValue:bridgeModifiers.flags)
        event.setIntegerValueField(.mouseEventDeltaX,value:0)
        event.setIntegerValueField(.mouseEventDeltaY,value:0)
        event.setIntegerValueField(.mouseEventClickState,value:1)
        event.setDoubleValueField(.mouseEventPressure,value:down ? 1:0)
        event.setIntegerValueField(.eventSourceUserData,value:eventMarker)
        guard let pid=bridgeConfigPID else { return }
        let gate=bridgeInputEpoch, token=gate.snapshot()
        let requested=ProcessInfo.processInfo.systemUptime
        bridgeInputQueue.async { [weak self] in
            guard !down || (gate.accepts(token) && NSWorkspace.shared.frontmostApplication?.processIdentifier == pid) else { return }
            if down {
                switch gate.authorize(token,queuedAt:requested,now:ProcessInfo.processInfo.systemUptime) {
                case .send:break
                case .cancelled:return
                case .expired:
                    DispatchQueue.main.async {self?.telly.stop("系统输入排队超过安全时间，已取消剩余动作；恢复后重新按 R。");self?.gameTelemetry.stop()}
                    return
                }
            }
            event.post(tap:.cgSessionEventTap)
            self?.traceBridge("POST mouse=\(down) queued_ms=\((ProcessInfo.processInfo.systemUptime-requested)*1000)")
        }
    }

    func postBridgeMove(x: Int64, y: Int64) {
        guard isTargetFront(), !sessionSuspended else { return }
        let position = CGEvent(source: nil)?.location ?? .zero
        guard let event = CGEvent(mouseEventSource: source, mouseType: .mouseMoved, mouseCursorPosition: position, mouseButton: .left) else { return }
        event.flags = CGEventFlags(rawValue:bridgeModifiers.flags).union(.maskNonCoalesced)
        event.setIntegerValueField(.mouseEventDeltaX, value: x)
        event.setIntegerValueField(.mouseEventDeltaY, value: y)
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        postBridgeEvent(event)
    }

    func postBridgeKey(_ code: UInt16, down: Bool) {
        guard !down || (isTargetFront() && !sessionSuspended) else { return }
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: down) else { return }
        if bridgeModifiers.update(code:code,down:down) {event.type = .flagsChanged}
        event.flags=CGEventFlags(rawValue:bridgeModifiers.flags)
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        postBridgeEvent(event, release: !down)
    }
}
