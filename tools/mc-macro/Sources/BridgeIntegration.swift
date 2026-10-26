import AppKit
import ApplicationServices

extension MacroApp {
    @objc func showBridgeSettings() {
        if let bridgeWindow { bridgeWindow.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true); return }
        let panel = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 570, height: 760),
                             styleMask: [.titled, .closable, .miniaturizable], backing: .buffered, defer: false)
        panel.title = "Speed Telly · 1.8.9 双模式版"
        panel.isReleasedWhenClosed = false; panel.center()
        let stack = NSStackView()
        stack.orientation = .vertical; stack.alignment = .leading; stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        panel.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo: panel.contentView!.leadingAnchor, constant: 26),
            stack.topAnchor.constraint(equalTo: panel.contentView!.topAnchor, constant: 24),
            stack.trailingAnchor.constraint(equalTo: panel.contentView!.trailingAnchor, constant: -26)])
        stack.addArrangedSubview(bridgeEnabled)
        bridgeModePicker.removeAllItems()
        bridgeModePicker.addItems(withTitles:BridgeMode.allCases.map(\.title))
        bridgeModePicker.selectItem(at:bridgeMode == .level ? 0:1)
        bridgeModePicker.target=self;bridgeModePicker.action=#selector(bridgeModeChanged)
        stack.addArrangedSubview(bridgeModePicker)
        addText("T 切换模式：平桥保持高度；Speed Telly 后续每跳升高一格。首段优先落稳，不强求四格；垫跳四格尚未启用。搭路中切换在下一轮准备时生效。启用此功能时 T 用于切换，聊天可用 / 打开后删除斜杠。",to:stack,small:true)
        addText("原版 Java 1.8.9：手持完整方块。按住 R 后校准，接近正方向（5° 内）会先轻微对正。松开 R 后完成本跳、落地回正再停止；头顶或前方受阻时停稳。无需开启连点总开关。", to: stack)
        addText("不需要 Forge 或 F3。助手读取本机游戏状态，所有动作仍通过鼠标和键盘完成。当前仍在验证不同起点和长时间连续搭路，请先在单人创造模式使用。", to: stack, small: true)
        stack.addArrangedSubview(button("测试状态读取（不移动，点击后切回游戏）", #selector(testBridgeReading)))
        bridgeStatus.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        bridgeStatus.widthAnchor.constraint(equalToConstant: 510).isActive = true
        stack.addArrangedSubview(bridgeStatus)
        addText("状态只在本机传递，不保存或上传画面。切出游戏、打开菜单或读数失效会停止本次搭路；松开 R 后可以重新开始。搭路时暂停原有连点／疾跑输入，原开关状态保留。", to: stack, small: true)
        stack.addArrangedSubview(button("立即停止", #selector(stopBridge)))
        bridgeWindow = panel; updateBridgeUI()
        panel.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true)
    }

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

    func updateBridgeUI() {
        bridgePermissionControls?.isHidden = true
        let fresh=bridgeWorldPreview.map{ProcessInfo.processInfo.systemUptime-$0.pose.time<0.25} ?? false
        var lines = ["模式：\(bridgeMode.title) · T 切换", "游戏状态：\(fresh ? "已连接" : "未连接／已停止")", telly.message]
        if let state=bridgeWorldPreview,fresh {lines.append("落地：\(state.onGround ? "是":"否") · 手持完整方块：\(state.hasBlocks ? "是":"否")") }
        if let config = telly.config { lines.append(String(format: "游戏灵敏度：%.1f%%（自动读取）", config.sensitivity * 200)) }
        if let pose = [telly.track.latest, bridgePreview].compactMap({ $0 }).max(by:{ $0.time<$1.time }) {
            lines.append(String(format: "XYZ %.3f / %.3f / %.3f\n朝向 %.1f / %.1f · 读数年龄 %.0f ms", pose.x,pose.y,pose.z,pose.yaw,pose.pitch, (ProcessInfo.processInfo.systemUptime-pose.time)*1000))
        }
        if let target = (bridgePreview ?? telly.track.latest)?.looking { lines.append("准星方块：\(target.x) / \(target.y) / \(target.z)") }
        bridgeStatus.stringValue = lines.joined(separator: "\n")
    }

    func serviceBridge() {
        let now=ProcessInfo.processInfo.systemUptime
        if telly.held && !CGEventSource.keyState(.hidSystemState,key:15) {telly.release()}
        if bridgeTraceMessage != telly.message {bridgeTraceMessage=telly.message;traceBridge("STATE "+telly.message)}
        if bridgeDiagnosticUntil>0 && now>bridgeDiagnosticUntil {
            bridgeDiagnosticUntil=0;telly.stop("状态读取超时，请确认正在运行原版 Java 1.8.9。");gameTelemetry.stop();updateBridgeUI()
        }
        let diagnostic=bridgeDiagnosticUntil>0
        guard diagnostic || (telly.active && telly.phase != .idle) else {
            if gameTelemetry.pid != nil {gameTelemetry.stop()}
            if f3Capture.running {f3Capture.reset()}
            return
        }
        if now-bridgeAccessCheckedAt>0.5 {bridgeAccessAllowed=AXIsProcessTrusted();bridgeAccessCheckedAt=now}
        let active=isTargetFront() && !sessionSuspended && bridgeAccessAllowed
            && !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand)
            && (tap.map{CGEvent.tapIsEnabled(tap:$0)} ?? false)
        guard active,let pid=NSWorkspace.shared.frontmostApplication?.processIdentifier else {
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
        bridgeInputQueue.async {
            guard release || (gate.accepts(token) && NSWorkspace.shared.frontmostApplication?.processIdentifier == pid) else { return }
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
        bridgeInputQueue.async {
            guard !down || (gate.accepts(token) && NSWorkspace.shared.frontmostApplication?.processIdentifier == pid) else { return }
            event.post(tap:.cgSessionEventTap)
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
