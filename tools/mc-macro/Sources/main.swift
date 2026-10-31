import AppKit
import ApplicationServices
import Carbon.HIToolbox

let eventMarker: Int64 = 0x4D434D4143524F

final class MacroApp: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var statusItem: NSStatusItem!
    var statusLabel = NSTextField(wrappingLabelWithString: "")
    var targetLabel = NSTextField(wrappingLabelWithString: "")
    var permissionControls: NSStackView?
    var bridgePermissionControls: NSStackView?
    var permissionsLabel = NSTextField(wrappingLabelWithString: "")
    var minimum = NSTextField(string: "15")
    var maximum = NSTextField(string: "20")
    var sprint = PanelSwitch("疾跑")
    var sprintKey = NSPopUpButton()
    var targetPicker = NSPopUpButton()
    let clickSwitch = PanelSwitch("连点")
    var clickStateLabel = NSTextField(labelWithString: "")
    var bridgeStateLabel = NSTextField(labelWithString: "")
    let rangeRail = RangeRail()
    let levelChoice = BridgeChoice("平搭",target:nil,action:nil)
    let risingChoice = BridgeChoice("上搭",target:nil,action:nil)
    var settingsButton:PanelButton!
    let preferences = NSPopover()
    let diagnosticLabel = NSTextField(wrappingLabelWithString: "")
    var policy = MacroPolicy()
    let hardwareMouse = HardwareMouse()
    var tap: CFMachPort?
    var tapSource: CFRunLoopSource?
    var clickTimers: [MacroMouseButton: Timer] = [:]
    var releaseTimers: [MacroMouseButton: Timer] = [:]
    var refreshTimer: Timer?
    var watchdog: Timer?
    var emittedDown = Set<MacroMouseButton>()
    var rhythms: [MacroMouseButton: ClickRhythm] = [:]
    var rhythmRandom = SystemRandomNumberGenerator()
    var sprintOwned = false
    var ownedSprintCode: CGKeyCode = 59
    var sprintRenewal = SprintRenewal()
    var sessionSuspended = false
    var terminationSignal: DispatchSourceSignal?
    var targetPIDs = Set<pid_t>()
    var detectionCache: [pid_t: Bool] = [:]
    var detectionPending = Set<pid_t>()
    var manualPID: pid_t?
    var boundHotkey: CGKeyCode = 50
    var recordingHotkey = false
    var hotkeyButton: NSButton!
    var cpsMin = 15.0
    var cpsMax = 20.0
    var notice = "已关闭。进入游戏后按 ` 开启。"
    var suppressedKeys = Set<CGKeyCode>()
    var bridgeManualInput = BridgeManualInputGate()
    let source = CGEventSource(stateID: .privateState)
    let f3Capture = F3Capture()
    let telly = TellyController()
    let gameTelemetry = GameTelemetry()
    let autoToolEnabled = PanelSwitch("自动工具")
    let supplyEnabled = PanelSwitch("同种补料")
    var autoToolPress = AutoToolPress()
    var bridgeSupply = BridgeSupplyPolicy()
    var supplyPending:(slot:Int,identity:String,time:Double)?
    let inventoryInputEpoch = BridgeInputEpoch()
    var bridgeRuntime:GameTelemetry.Runtime?
    var bridgeRuntimeChecked=false
    var bridgeWorldPreview:BridgeWorldState?
    var bridgeUIAt=0.0
    let bridgeInputQueue = DispatchQueue(label:"local.mc-macro.bridge-input",qos:.userInteractive)
    let bridgeInputEpoch = BridgeInputEpoch()
    var bridgeModifiers = BridgeModifiers()
    var bridgeChatOpen=false
    var bridgeMode = BridgeMode.level
    var bridgeModePicker = NSPopUpButton()
    var bridgeTimer: Timer?
    var bridgeAccessCheckedAt = -Double.infinity
    var bridgeAccessAllowed = false
    var bridgeWindow: NSWindow?
    var bridgeEnabled = PanelSwitch("Telly 搭路")
    var bridgeStatus = NSTextField(wrappingLabelWithString: "")
    var bridgeConfigPending = false
    var bridgeConfigPID: pid_t?
    var bridgeConfigAt = 0.0
    var bridgeDiagnosticUntil = 0.0
    var bridgePreview: F3Pose?
    let bridgeTraceEnabled = ProcessInfo.processInfo.environment["MC_MACRO_TRACE"] == "1"
    var bridgeTraceTick = -1
    var bridgeTraceMessage = ""

    func traceBridge(_ line: String) {
        guard bridgeTraceEnabled, let data=(String(format:"%.3f ",ProcessInfo.processInfo.systemUptime)+line+"\n").data(using:.utf8) else{return}
        FileHandle.standardOutput.write(data)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Future local updates can stop the running app while releasing owned input.
        signal(SIGTERM, SIG_IGN)
        let termination = DispatchSource.makeSignalSource(signal: SIGTERM, queue: .main)
        termination.setEventHandler { [weak self] in self?.quit() }
        termination.resume()
        terminationSignal = termination
        source?.localEventsSuppressionInterval = 0
        loadSettings()
        buildWindow()
        buildMenu()
        bridgeMode=BridgeMode(rawValue:UserDefaults.standard.string(forKey:"bridgeMode") ?? "level") ?? .level
        telly.forwardPitch=45;telly.risePerJump=bridgeMode.rise;telly.coordinateMovement=true
        gameTelemetry.onState = { [weak self] state,error in
            guard let self else{return}
            self.bridgeWorldPreview=state
            self.observeInventory(state)
            if self.bridgeDiagnosticUntil>0,let state {
                self.bridgePreview=state.pose;self.bridgeDiagnosticUntil=0
                self.telly.stop("游戏状态读取成功；本次没有移动或点击。")
                self.gameTelemetry.stop();self.updateBridgeUI()
            } else if self.telly.active,self.telly.phase != .idle, state?.hasGeometry != false {
                self.telly.observeWorld(state,error:error,now:ProcessInfo.processInfo.systemUptime)
                if let state, ProcessInfo.processInfo.environment["MC_MACRO_FRAME_TRACE"]=="1" {
                    func block(_ b:F3Block?)->Any {b.map{[$0.x,$0.y,$0.z]} ?? NSNull()}
                    let record:[String:Any] = ["tick":state.tick,"ticksDue":state.ticksDue ?? -1,"headYaw":state.headYaw ?? state.pose.yaw,"eyeHeight":state.eyeHeight,"p":[state.pose.x,state.pose.y,state.pose.z],"r":[state.renderPose.x,state.renderPose.y,state.renderPose.z],"angle":[state.pose.yaw,state.pose.pitch],"v":[state.velocity.0,state.velocity.1,state.velocity.2],"cache":block(state.pose.looking),"face":state.face ?? "", "logical":block(state.useHit),"logical_face":state.useFace ?? "", "delay":state.clickDelay,"down":state.useDown,"ground":state.onGround,"sprint":state.sprinting ?? false,"solid":state.solid.map{[$0.x,$0.y,$0.z]}]
                    if let data=try? JSONSerialization.data(withJSONObject:record,options:[.sortedKeys]),let text=String(data:data,encoding:.utf8) {self.traceBridge("FRAME "+text)}
                }
                if let state,state.tick != self.bridgeTraceTick {
                    self.bridgeTraceTick=state.tick
                    self.traceBridge("TELE tick=\(state.tick) delay=\(state.clickDelay) useDown=\(state.useDown) cache=\(String(describing:state.pose.looking)),\(state.face ?? "nil") logical=\(String(describing:state.useHit)),\(state.useFace ?? "nil") velocity=\(state.velocity) sprint=\(String(describing:state.sprinting))")
                    self.traceBridge(String(format:"POSE %.4f %.4f %.4f yaw %.2f pitch %.2f ground %@ ",state.pose.x,state.pose.y,state.pose.z,state.pose.yaw,state.pose.pitch,String(state.onGround))+self.telly.diagnostic)
                }
            }
        }
        telly.key = { [weak self] code, down in self?.postBridgeKey(code, down: down) }
        telly.mouse = { [weak self] down in
            guard let self, !down || self.isTargetFront() else { return }
            self.postBridgeMouse(down: down)
        }
        telly.move = { [weak self] x,y in self?.postBridgeMove(x: x, y: y) }
        telly.trace = { [weak self] line in self?.traceBridge(line) }
        telly.cancelPendingInput = { [weak self] in self?.bridgeInputEpoch.invalidate() }
        telly.supplyReady = { [weak self] state in self?.prepareBridgeSupply(state) ?? false }
        telly.placementSupplyReady = { [weak self] in self?.preparePlacementSupply() ?? false }
        autoToolEnabled.state = UserDefaults.standard.object(forKey:"autoToolEnabled") as? Bool == false ? .off:.on
        supplyEnabled.state = UserDefaults.standard.object(forKey:"sameBlockSupply") as? Bool == false ? .off:.on
        for control in [autoToolEnabled,supplyEnabled] {control.target=self;control.action=#selector(inventorySettingsChanged)}
        bridgeEnabled.state = UserDefaults.standard.object(forKey: "bridgeEnabled") as? Bool == false ? .off : .on
        bridgeEnabled.target = self
        bridgeEnabled.action = #selector(bridgeChanged)
        refreshTargets()
        hardwareMouse.onChange = { [weak self] button, down in self?.hardwareChanged(button, down: down) }
        if CGPreflightListenEventAccess() { hardwareMouse.start() }
        _ = installTap()
        NSWorkspace.shared.notificationCenter.addObserver(self, selector: #selector(frontChanged),
            name: NSWorkspace.didActivateApplicationNotification, object: nil)
        NSWorkspace.shared.notificationCenter.addObserver(self, selector: #selector(sleeping),
            name: NSWorkspace.willSleepNotification, object: nil)
        NSWorkspace.shared.notificationCenter.addObserver(self, selector: #selector(sleeping),
            name: NSWorkspace.sessionDidResignActiveNotification, object: nil)
        DistributedNotificationCenter.default().addObserver(self, selector: #selector(sleeping),
            name: NSNotification.Name("com.apple.screenIsLocked"), object: nil)
        DistributedNotificationCenter.default().addObserver(self, selector: #selector(awake),
            name: NSNotification.Name("com.apple.screenIsUnlocked"), object: nil)
        NSWorkspace.shared.notificationCenter.addObserver(self, selector: #selector(awake),
            name: NSWorkspace.didWakeNotification, object: nil)
        NSWorkspace.shared.notificationCenter.addObserver(self, selector: #selector(awake),
            name: NSWorkspace.sessionDidBecomeActiveNotification, object: nil)
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in
            // Discovery and permission-label refresh take a whole game tick
            // on this host. The active bridge already has a bound PID and
            // independently checks focus, tap health and AX every 500 ms.
            // Resume maintenance after R finishes; never stall a live turn.
            guard self?.telly.active != true else {return}
            let auditStart=ProcessInfo.processInfo.systemUptime
            if let self, AXIsProcessTrusted(), CGPreflightListenEventAccess() {
                self.hardwareMouse.start()
                _ = self.installTap()
            }
            let permissionEnd=ProcessInfo.processInfo.systemUptime
            self?.refreshTargets()
            let targetsEnd=ProcessInfo.processInfo.systemUptime
            self?.updateUI()
            self?.traceBridge("LOOP refresh permissions_ms=\((permissionEnd-auditStart)*1000) targets_ms=\((targetsEnd-permissionEnd)*1000) ui_ms=\((ProcessInfo.processInfo.systemUptime-targetsEnd)*1000)")
        }
        watchdog = Timer.scheduledTimer(withTimeInterval: 0.025, repeats: true) { [weak self] _ in
            guard let self else { return }
            self.hardwareMouse.refresh()
            self.serviceEnabledMode()
        }
        bridgeTimer = Timer(timeInterval: 0.008, repeats: true) { [weak self] _ in self?.serviceBridge() }
        RunLoop.main.add(bridgeTimer!, forMode: .common)
        updateUI()
        traceBridge("START version=1.9.3 AX=\(AXIsProcessTrusted()) input=\(CGPreflightListenEventAccess())")
        if ProcessInfo.processInfo.environment["MC_MACRO_BACKGROUND"] != "1" {
            window.makeKeyAndOrderFront(nil)
            NSApp.activate(ignoringOtherApps: true)
        }
    }

    func loadSettings() {
        let defaults = UserDefaults.standard
        let lo = defaults.object(forKey: "minimum") as? Double ?? 15
        let hi = defaults.object(forKey: "maximum") as? Double ?? 20
        if MacroPolicy.validRange(lo, hi) { cpsMin = lo; cpsMax = hi }
        minimum.stringValue = String(format: "%g", cpsMin)
        maximum.stringValue = String(format: "%g", cpsMax)
        boundHotkey = CGKeyCode(defaults.object(forKey: "hotkey") as? Int ?? 50)
    }

    func buildWindow() { buildDashboard() }

    func buildMenu() {
        let mainMenu = NSMenu()
        let root = NSMenuItem()
        mainMenu.addItem(root)
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "退出 mcPvPmax", action: #selector(quit), keyEquivalent: "q").target = self
        root.submenu = appMenu
        let editRoot=NSMenuItem(title:"编辑",action:nil,keyEquivalent:"")
        let edit=NSMenu(title:"编辑")
        for (title,selector,key) in [("撤销",Selector(("undo:")),"z"),("剪切",#selector(NSText.cut(_:)),"x"),("复制",#selector(NSText.copy(_:)),"c"),("粘贴",#selector(NSText.paste(_:)),"v"),("全选",#selector(NSText.selectAll(_:)),"a")] {
            edit.addItem(withTitle:title,action:selector,keyEquivalent:key)
        }
        editRoot.submenu=edit;mainMenu.addItem(editRoot)
        NSApp.mainMenu = mainMenu
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        let menu = NSMenu()
        menu.addItem(withTitle: "显示面板", action: #selector(showSettings), keyEquivalent: "").target = self
        menu.addItem(withTitle: "立即停止", action: #selector(emergencyStop), keyEquivalent: "").target = self
        menu.addItem(.separator())
        menu.addItem(withTitle: "退出", action: #selector(quit), keyEquivalent: "").target = self
        statusItem.menu = menu
    }

    func commandLine(_ pid: pid_t) -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/ps")
        process.arguments = ["-p", String(pid), "-o", "command="]
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = FileHandle.nullDevice
        do {
            try process.run()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            process.waitUntilExit()
            return String(data: data, encoding: .utf8) ?? ""
        } catch { return "" }
    }

    func refreshTargets() {
        let apps = NSWorkspace.shared.runningApplications.filter {
            let name = ($0.localizedName ?? "").lowercased()
            return name.contains("java") || name.contains("minecraft") || name.contains("lunar") ||
                ($0.bundleIdentifier ?? "").lowercased().contains("minecraft")
        }
        var detected = Set<pid_t>()
        let livePIDs = Set(apps.map { $0.processIdentifier })
        detectionCache = detectionCache.filter { livePIDs.contains($0.key) }
        for app in apps {
            let pid = app.processIdentifier
            // Retry transient negatives off the input thread. Waiting for ps
            // on the main run loop can delay a placement by an entire tick.
            if detectionCache[pid] != true,!detectionPending.contains(pid) {
                detectionPending.insert(pid)
                let name=app.localizedName ?? "",bundle=app.bundleIdentifier ?? ""
                DispatchQueue.global(qos:.utility).async { [weak self] in
                    guard let self else{return}
                    let matched=MacroPolicy.looksLikeMinecraft(name:name,bundle:bundle,command:self.commandLine(pid))
                    DispatchQueue.main.async {
                        self.detectionPending.remove(pid)
                        guard NSRunningApplication(processIdentifier:pid) != nil else{return}
                        self.detectionCache[pid]=matched
                        if matched {self.targetPIDs.insert(pid)}
                        self.updateUI()
                    }
                }
            }
            if detectionCache[pid] == true {
                detected.insert(app.processIdentifier)
            }
        }
        targetPIDs = detected
        var choices: [(String, Int)] = [("自动识别 Minecraft", 0)]
        for app in apps.sorted(by: { $0.processIdentifier < $1.processIdentifier }) {
            choices.append(("\(app.localizedName ?? "游戏") · \(app.processIdentifier)", Int(app.processIdentifier)))
        }
        if targetPicker.itemTitles != choices.map({ $0.0 }) {
            targetPicker.removeAllItems()
            for (title, pid) in choices {
                targetPicker.addItem(withTitle: title)
                targetPicker.lastItem?.tag = pid
            }
        }
        if let pid = manualPID {
            if targetPicker.itemArray.contains(where: { $0.tag == Int(pid) }) {
                targetPicker.selectItem(withTag: Int(pid))
            } else {
                manualPID = nil
                stop("绑定的游戏已退出，已关闭。")
            }
        }
    }

    func isTargetFront() -> Bool {
        guard let front = NSWorkspace.shared.frontmostApplication else { return false }
        let pid = front.processIdentifier
        return manualPID.map { $0 == pid } ?? targetPIDs.contains(pid)
    }

    @objc func selectTarget() {
        stop("已切换目标，进入游戏后按快捷键开启。")
        let pid = targetPicker.selectedItem?.tag ?? 0
        manualPID = pid == 0 ? nil : pid_t(pid)
        updateUI()
    }

    @objc func frontChanged() {
        cancelInventoryActions()
        let active = isTargetFront()
        if !active { telly.stop("已切出游戏，搭路停止。松开 R 后重新开始。"); f3Capture.reset() }
        if policy.enabled && active { policy.targetActive = false; serviceEnabledMode() }
        else {
            policy.targetActive = active
            if policy.enabled { suspend("已暂停：已切出游戏，总开关仍开启，返回后自动就绪。") }
        }
    }

    @objc func sleeping() { sessionSuspended = true; telly.stop("锁屏或睡眠，搭路已停止。"); suspend("已暂停：锁屏或睡眠，总开关保留。") }
    @objc func awake() { sessionSuspended = false; serviceEnabledMode() }

    @discardableResult func installTap() -> Bool {
        if tap != nil { return true }
        guard AXIsProcessTrusted() else { return false }
        let types: [CGEventType] = [.mouseMoved, .leftMouseDown, .leftMouseUp, .leftMouseDragged,
                                   .rightMouseDown, .rightMouseUp, .rightMouseDragged,
                                   .otherMouseDown, .otherMouseUp, .otherMouseDragged, .scrollWheel,
                                   .keyDown, .keyUp, .flagsChanged]
        let mask = types.reduce(CGEventMask(0)) { $0 | (CGEventMask(1) << $1.rawValue) }
        tap = CGEvent.tapCreate(tap: .cgSessionEventTap, place: .headInsertEventTap, options: .defaultTap,
            eventsOfInterest: mask, callback: { _, type, event, info in
                guard let info else { return Unmanaged.passUnretained(event) }
                let owner = Unmanaged<MacroApp>.fromOpaque(info).takeUnretainedValue()
                return owner.handle(type, event)
            }, userInfo: Unmanaged.passUnretained(self).toOpaque())
        guard let tap else { return false }
        tapSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetMain(), tapSource, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)
        return true
    }

    func handle(_ type: CGEventType, _ event: CGEvent) -> Unmanaged<CGEvent>? {
        if type == .tapDisabledByTimeout || type == .tapDisabledByUserInput {
            suspend("输入监听中断，正在恢复，总开关保留。")
            if let tap { CGEvent.tapEnable(tap: tap, enable: true) }
            return Unmanaged.passUnretained(event)
        }
        if event.getIntegerValueField(.eventSourceUserData) == eventMarker { return Unmanaged.passUnretained(event) }
        if event.getIntegerValueField(.eventSourceUnixProcessID) == Int64(getpid()) { return Unmanaged.passUnretained(event) }
        let code = CGKeyCode(event.getIntegerValueField(.keyboardEventKeycode))
        if type == .keyUp && code == 15 && (telly.held || telly.restartRequiresRelease) {
            traceBridge("R up")
            telly.release(); f3Capture.reset(); return nil
        }
        if type == .keyUp && suppressedKeys.remove(code) != nil { return nil }
        let manualInput:BridgeManualInputGate.Input?
        switch type {
        case .keyDown,.keyUp:manualInput = .key(code,type == .keyDown)
        case .flagsChanged:manualInput = .modifier
        case .mouseMoved:manualInput = .motion(event.getIntegerValueField(.mouseEventDeltaX),event.getIntegerValueField(.mouseEventDeltaY))
        case .leftMouseDown,.rightMouseDown,.otherMouseDown,.leftMouseUp,.rightMouseUp,.otherMouseUp:
            manualInput = .button(event.getIntegerValueField(.mouseEventButtonNumber),[CGEventType.leftMouseDown,.rightMouseDown,.otherMouseDown].contains(type))
        case .leftMouseDragged,.rightMouseDragged,.otherMouseDragged:
            manualInput = .drag(event.getIntegerValueField(.mouseEventButtonNumber))
        case .scrollWheel:manualInput = .scroll
        default:manualInput=nil
        }
        if let manualInput,bridgeManualInput.consume(manualInput,duringFinish:false) {return nil}
        let active = isTargetFront()
        policy.targetActive = active
        if policy.enabled && !active { suspend("已切出游戏，暂停输入，总开关保留。") }
        guard active else { return Unmanaged.passUnretained(event) }
        if type == .keyDown || type == .scrollWheel || type == .rightMouseDown || type == .leftMouseUp || event.flags.contains(.maskCommand) {
            autoToolPress.cancel();if !telly.active {inventoryInputEpoch.invalidate()}
        }
        // System shortcuts/focus loss remain immediate safety stops. Ordinary
        // manual play requests a landing first, before menus or movement can
        // invalidate the current placement ray and landing prediction.
        if event.flags.contains(.maskCommand),telly.phase != .idle {
            telly.stop("系统快捷键期间已释放搭路输入。松开 R 后重新开始。")
            return Unmanaged.passUnretained(event)
        }
        let bridgeControlKey=(type == .keyDown || type == .keyUp) &&
            (code==15 || (code==17 && !telly.manualFinishRequested))
        if telly.phase != .idle,!bridgeControlKey,let manualInput,manualInput.hasIntent {
            if !telly.manualFinishRequested {
                traceBridge("INPUT_FINISH type=\(type.rawValue) pid=\(event.getIntegerValueField(.eventSourceUnixProcessID)) code=\(code) dx=\(event.getIntegerValueField(.mouseEventDeltaX)) dy=\(event.getIntegerValueField(.mouseEventDeltaY)) phase=\(telly.phase)")
                telly.requestManualFinish()
            }
            if bridgeManualInput.consume(manualInput,duringFinish:telly.finishing) {return nil}
        }
        if type == .keyDown && bridgeEnabled.state == .on {
            if bridgeChatOpen {
                if code==36 || code==53 {bridgeChatOpen=false}
                return Unmanaged.passUnretained(event)
            }
            if code==44 {
                bridgeChatOpen=true
                if telly.active {telly.stop("已打开聊天，搭路已停止。")}
                return Unmanaged.passUnretained(event)
            }
        }
        if type == .keyDown && code == 17 && bridgeEnabled.state == .on && !event.flags.contains(.maskCommand) {
            if event.getIntegerValueField(.keyboardEventAutorepeat)==0 {setBridgeMode(bridgeMode.next)}
            suppressedKeys.insert(code)
            return nil
        }
        if type == .keyDown && code == 15 && bridgeEnabled.state == .on {
            traceBridge("R down repeat=\(event.getIntegerValueField(.keyboardEventAutorepeat))")
            if event.flags.contains(.maskCommand) { return Unmanaged.passUnretained(event) }
            if event.getIntegerValueField(.keyboardEventAutorepeat) == 0 {
                cancelClicks(); releaseSprint()
                if sprintKey.indexOfSelectedItem == 1 {
                    telly.stop("R 已用作疾跑键，请先改用左 Control 再搭路。")
                } else {
                    bridgeDiagnosticUntil = 0; bridgePreview = nil
                    if telly.phase == .idle && !telly.restartRequiresRelease {bridgeSupply.reset();supplyPending=nil}
                    gameTelemetry.needsGeometry=true
                    telly.press(now: ProcessInfo.processInfo.systemUptime)
                }
            }
            return nil
        }
        if type == .keyDown {
            if code == boundHotkey {
                if event.getIntegerValueField(.keyboardEventAutorepeat) == 0 {
                    if policy.enabled { stop("已关闭。") } else { start() }
                }
                suppressedKeys.insert(code)
                return nil
            }
            // Release before Cmd-Tab / Cmd-Q / other system shortcuts leave the game.
            if policy.enabled && event.flags.contains(.maskCommand) { suspend("系统快捷键期间暂停，总开关保留。") }
        }
        guard policy.enabled else { return Unmanaged.passUnretained(event) }
        switch type {
        case .flagsChanged:
            if sprintOwned && sprintRenewal.isDown && ownedSprintCode == 59 {
                event.flags = CGEventFlags(rawValue: SprintModifier.flags(event.flags.rawValue, down: true))
            }
        case .leftMouseDown, .rightMouseDown:
            let button: MacroMouseButton = type == .leftMouseDown ? .left : .right
            if policy.mayClick(button), hardwareMouse.isDown(button), clickTimers[button] == nil { click(button) }
            return nil
        case .leftMouseUp, .rightMouseUp:
            let button: MacroMouseButton = type == .leftMouseUp ? .left : .right
            // Synthetic up events must not change physical hold state.
            if !hardwareMouse.isDown(button) { hardwareChanged(button, down: false) }
            return nil
        case .leftMouseDragged, .rightMouseDragged:
            if policy.mayClick(type == .leftMouseDragged ? .left : .right) {
                event.type = .mouseMoved
                event.flags.remove(.maskControl)
            }
        default: break
        }
        return Unmanaged.passUnretained(event)
    }

    func start() {
        cancelInventoryActions()
        guard isTargetFront(), AXIsProcessTrusted(), let tap, CGEvent.tapIsEnabled(tap: tap) else {
            notice = "无法开启：请先授权并检查输入监听。"; updateUI(); return
        }
        hardwareMouse.start()
        policy.physicalLeftHeld = false // A fresh physical press is required after every enable.
        policy.physicalRightHeld = false
        policy.targetActive = true
        policy.menuPaused = false
        policy.enabled = true
        notice = hardwareMouse.connected ? "已就绪：按住才连点，总开关持续开启。" : "已启用疾跑；鼠标硬件未连接，连点暂停。"
        if sprint.state == .on { pressSprint() }
        updateUI()
    }

    func stop(_ reason: String) {
        cancelInventoryActions()
        if recordingHotkey {recordingHotkey=false;hotkeyButton.title=hotkeyTitle()}
        telly.stop("搭路已停止。松开 R 后可重新开始。")
        policy.stop()
        cancelClicks()
        releaseSprint()
        notice = reason
        updateUI()
    }

    func suspend(_ reason: String) {
        cancelInventoryActions()
        telly.stop("搭路已暂停。松开 R 后可重新开始。")
        policy.suspend()
        cancelClicks()
        releaseSprint()
        if policy.enabled { notice = reason; updateUI() }
    }

    func serviceEnabledMode() {
        guard !telly.active else { return }
        guard policy.enabled else { return }
        let active = isTargetFront()
        let wasActive = policy.targetActive
        policy.targetActive = active
        guard active, !sessionSuspended, AXIsProcessTrusted(), !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand) else {
            if wasActive || sprintOwned || !clickTimers.isEmpty { suspend("暂时暂停输入，总开关保留。") }
            return
        }
        policy.menuPaused = false
        if let tap, !CGEvent.tapIsEnabled(tap: tap) { CGEvent.tapEnable(tap: tap, enable: true) }
        if sprint.state == .on {
            if !sprintOwned { pressSprint() }
            else if let down = sprintRenewal.advance(now: ProcessInfo.processInfo.systemUptime) { postSprint(down: down) }
        }
        // Reconcile with hardware after loading/respawn or a transient listener reset.
        // Keeping the mode enabled never permits clicks when the hardware is up.
        policy.reconcileHardware(left: hardwareMouse.isDown(.left) && !bridgeManualInput.suppressesButton(0),
                                 right: hardwareMouse.isDown(.right) && !bridgeManualInput.suppressesButton(1))
        for button in MacroMouseButton.allCases {
            if policy.mayClick(button, hardwareDown: hardwareMouse.isDown(button)) {
                if clickTimers[button] == nil { click(button) }
            } else { cancelClicks(button) }
        }
        if !wasActive { notice = "已自动恢复就绪：按住鼠标才连点。"; updateUI() }
    }

    func click(_ button: MacroMouseButton) {
        clickTimers.removeValue(forKey: button)?.invalidate()
        guard policy.mayClick(button, hardwareDown: hardwareMouse.isDown(button)), isTargetFront(), AXIsProcessTrusted() else {
            cancelClicks(button); return
        }
        let started = ProcessInfo.processInfo.systemUptime
        var rhythm = rhythms[button] ?? ClickRhythm()
        let beat = rhythm.next(minimum: cpsMin, maximum: cpsMax, using: &rhythmRandom)
        rhythms[button] = rhythm
        releaseMouse(button)
        postMouse(button, down: true)
        emittedDown.insert(button)
        releaseTimers.removeValue(forKey: button)?.invalidate()
        let release = Timer(timeInterval: beat.held, repeats: false) { [weak self] _ in
            self?.releaseMouse(button)
        }
        releaseTimers[button] = release
        RunLoop.main.add(release, forMode: .common)
        // Account for time spent posting events so it is not added to every interval.
        // Never send a burst of overdue clicks after a stalled run loop.
        let delay = max(0.001, beat.interval - (ProcessInfo.processInfo.systemUptime - started))
        let next = Timer(timeInterval: delay, repeats: false) { [weak self] _ in self?.click(button) }
        clickTimers[button] = next
        RunLoop.main.add(next, forMode: .common)
    }

    func hardwareChanged(_ button: MacroMouseButton, down: Bool) {
        if button == .left {
            if down {physicalToolPress()} else {autoToolPress.cancel();if !telly.active {inventoryInputEpoch.invalidate()}}
        }
        if !down {
            if button == .left { policy.physicalLeftHeld = false }
            else { policy.physicalRightHeld = false }
            cancelClicks(button)
            return
        }
        guard !telly.active, !bridgeManualInput.suppressesButton(button == .left ? 0:1), policy.enabled, !sessionSuspended, !policy.menuPaused, isTargetFront() else { return }
        if button == .left { policy.physicalLeftHeld = true }
        else { policy.physicalRightHeld = true }
        if clickTimers[button] == nil { click(button) }
    }

    func postMouse(_ button: MacroMouseButton, down: Bool) {
        let position = CGEvent(source: nil)?.location ?? .zero
        let type: CGEventType = button == .left ? (down ? .leftMouseDown : .leftMouseUp) : (down ? .rightMouseDown : .rightMouseUp)
        guard let event = CGEvent(mouseEventSource: source, mouseType: type,
                                  mouseCursorPosition: position, mouseButton: button == .left ? .left : .right) else { return }
        // Control must not turn these generated attacks into contextual/right clicks.
        event.flags = []
        event.setIntegerValueField(.mouseEventDeltaX, value: 0)
        event.setIntegerValueField(.mouseEventDeltaY, value: 0)
        event.setIntegerValueField(.mouseEventClickState, value: 1)
        event.setDoubleValueField(.mouseEventPressure, value: down ? 1 : 0)
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        event.post(tap: .cghidEventTap)
    }

    func releaseMouse(_ button: MacroMouseButton) {
        releaseTimers.removeValue(forKey: button)?.invalidate()
        if emittedDown.remove(button) != nil { postMouse(button, down: false) }
    }

    func cancelClicks(_ button: MacroMouseButton) {
        rhythms.removeValue(forKey: button)
        clickTimers.removeValue(forKey: button)?.invalidate()
        releaseMouse(button)
    }

    func cancelClicks() {
        for button in MacroMouseButton.allCases { cancelClicks(button) }
    }

    func pressSprint() {
        guard !sprintOwned, policy.enabled, !policy.menuPaused, isTargetFront() else { return }
        let code: CGKeyCode = sprintKey.indexOfSelectedItem == 0 ? 59 : 15
        // Do not take ownership of a sprint key the user is already holding.
        guard !CGEventSource.keyState(.hidSystemState, key: code) else { return }
        ownedSprintCode = code
        sprintOwned = true
        sprintRenewal.begin(now: ProcessInfo.processInfo.systemUptime)
        postSprint(down: true)
    }

    func postSprint(down: Bool) {
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: ownedSprintCode, keyDown: down) else { return }
        if ownedSprintCode == 59 {
            event.type = .flagsChanged
            event.flags = CGEventFlags(rawValue: SprintModifier.flags(CGEventSource.flagsState(.combinedSessionState).rawValue, down: down))
        }
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        event.post(tap: .cghidEventTap)
    }

    func releaseSprint() {
        if sprintOwned { postSprint(down: false); sprintOwned = false }
        sprintRenewal = SprintRenewal()
    }

    func updateUI() { guard window != nil else{return};updateDashboard() }

    func hotkeyTitle() -> String {
        let names:[UInt16:String]=[50:"`",0:"A",1:"S",2:"D",3:"F",4:"H",5:"G",6:"Z",7:"X",8:"C",9:"V",11:"B",13:"W",16:"Y",18:"1",19:"2",20:"3",21:"4",22:"6",23:"5",25:"9",26:"7",28:"8",29:"0",31:"O",32:"U",34:"I",35:"P",37:"L",38:"J",40:"K",45:"N",46:"M",48:"⇥",49:"␣"]
        return names[boundHotkey] ?? "\(boundHotkey)"
    }

    @objc func saveSettings() {
        guard let lo = Double(minimum.stringValue), let hi = Double(maximum.stringValue), MacroPolicy.validRange(lo, hi) else {
            notice = "设置未保存：请输入 1–40 的 CPS，且下限不能大于上限。"; updateUI(); return
        }
        stop("设置已保存，进入游戏后按快捷键开启。")
        cpsMin = lo; cpsMax = hi
        UserDefaults.standard.set(lo, forKey: "minimum")
        UserDefaults.standard.set(hi, forKey: "maximum")
    }

    @objc func sprintChanged() {
        stop("疾跑设置已更新，进入游戏后按快捷键开启。")
        UserDefaults.standard.set(sprint.state == .on, forKey: "sprint")
        UserDefaults.standard.set(sprintKey.indexOfSelectedItem, forKey: "sprintKey")
    }

    @objc func recordKey() {
        stop("请按新的开关键，Esc 取消。")
        recordingHotkey = true
        window.makeFirstResponder(nil)
        hotkeyButton.title = "…"
        updateUI()
    }

    @objc func requestPermissions() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(options)
        _ = CGRequestListenEventAccess()
        if CGPreflightListenEventAccess() { hardwareMouse.start() }
        if installTap() { notice = "监听已连接，进入游戏后按快捷键开启。" }
        else { notice = "请在系统设置中授权；若仍无法连接，请完全退出后重新打开。" }
        updateUI()
    }

    @objc func openAccessibility() { openPrivacy("Privacy_Accessibility") }
    @objc func openInputMonitoring() { openPrivacy("Privacy_ListenEvent") }
    func openPrivacy(_ pane: String) {
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?\(pane)") { NSWorkspace.shared.open(url) }
    }
    @objc func showSettings() { window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true) }
    @objc func emergencyStop() { stop("已手动停止。") }
    @objc func quit() { stop("已退出。"); NSApp.terminate(nil) }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { false }
    func applicationWillTerminate(_ notification: Notification) {
        telly.stop("已退出。"); gameTelemetry.stop(); f3Capture.reset()
        policy.stop(); cancelClicks(); releaseSprint()
        hardwareMouse.stop()
        if let tap { CGEvent.tapEnable(tap: tap, enable: false); CFMachPortInvalidate(tap) }
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let delegate = MacroApp()
app.delegate = delegate
app.run()
