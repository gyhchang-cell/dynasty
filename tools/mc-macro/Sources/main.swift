import AppKit
import ApplicationServices
import Carbon.HIToolbox

let eventMarker: Int64 = 0x4D434D4143524F

final class MacroApp: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var statusItem: NSStatusItem!
    var statusLabel = NSTextField(wrappingLabelWithString: "")
    var targetLabel = NSTextField(wrappingLabelWithString: "")
    var permissionsLabel = NSTextField(wrappingLabelWithString: "")
    var minimum = NSTextField(string: "15")
    var maximum = NSTextField(string: "20")
    var sprint = NSButton(checkboxWithTitle: "启用时保持疾跑（仅游戏前台）", target: nil, action: nil)
    var sprintKey = NSPopUpButton()
    var targetPicker = NSPopUpButton()
    var policy = MacroPolicy()
    let hardwareMouse = HardwareMouse()
    var tap: CFMachPort?
    var tapSource: CFRunLoopSource?
    var clickTimers: [MacroMouseButton: Timer] = [:]
    var releaseTimers: [MacroMouseButton: Timer] = [:]
    var refreshTimer: Timer?
    var watchdog: Timer?
    var emittedDown = Set<MacroMouseButton>()
    var sprintOwned = false
    var ownedSprintCode: CGKeyCode = 59
    var targetPIDs = Set<pid_t>()
    var detectionCache: [pid_t: Bool] = [:]
    var manualPID: pid_t?
    var boundHotkey: CGKeyCode = 50
    var recordingHotkey = false
    var hotkeyButton: NSButton!
    var cpsMin = 15.0
    var cpsMax = 20.0
    var notice = "已关闭。进入游戏后按 ` 开启。"
    var suppressedKeys = Set<CGKeyCode>()
    let source = CGEventSource(stateID: .privateState)

    func applicationDidFinishLaunching(_ notification: Notification) {
        source?.localEventsSuppressionInterval = 0
        loadSettings()
        buildWindow()
        buildMenu()
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
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in
            self?.refreshTargets()
            self?.updateUI()
        }
        watchdog = Timer.scheduledTimer(withTimeInterval: 0.025, repeats: true) { [weak self] _ in
            guard let self else { return }
            self.hardwareMouse.refresh()
            if self.policy.enabled && (!self.isTargetFront() || !AXIsProcessTrusted()) {
                self.stop("已暂停：离开游戏或权限失效。返回游戏后重新按快捷键开启。")
            }
        }
        updateUI()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
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

    func buildWindow() {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 570, height: 650),
                          styleMask: [.titled, .closable, .miniaturizable], backing: .buffered, defer: false)
        window.title = "MC 连点助手"
        window.center()
        window.isReleasedWhenClosed = false
        let stack = NSStackView()
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 10
        stack.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 26),
            stack.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -26),
            stack.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 24),
            stack.bottomAnchor.constraint(lessThanOrEqualTo: window.contentView!.bottomAnchor, constant: -16)
        ])
        let title = NSTextField(labelWithString: "MC 连点助手")
        title.font = .systemFont(ofSize: 25, weight: .bold)
        stack.addArrangedSubview(title)
        addText("仅在真实按住鼠标时连点；不按不点，松手即停。", to: stack)
        statusLabel.font = .systemFont(ofSize: 14, weight: .semibold)
        statusLabel.widthAnchor.constraint(equalToConstant: 510).isActive = true
        stack.addArrangedSubview(statusLabel)
        let range = NSStackView()
        range.spacing = 10
        range.addArrangedSubview(NSTextField(labelWithString: "CPS 范围"))
        for field in [minimum, maximum] {
            field.widthAnchor.constraint(equalToConstant: 65).isActive = true
            field.alignment = .center
        }
        range.addArrangedSubview(minimum)
        range.addArrangedSubview(NSTextField(labelWithString: "至"))
        range.addArrangedSubview(maximum)
        range.addArrangedSubview(button("保存设置", #selector(saveSettings)))
        stack.addArrangedSubview(range)
        addText("左右键各自使用此 CPS 范围；上下限相同即固定速度。", to: stack, small: true)
        hotkeyButton = button(hotkeyTitle(), #selector(recordKey))
        stack.addArrangedSubview(hotkeyButton)
        sprint.target = self
        sprint.action = #selector(sprintChanged)
        sprint.state = UserDefaults.standard.object(forKey: "sprint") as? Bool == false ? .off : .on
        stack.addArrangedSubview(sprint)
        sprintKey.addItems(withTitles: ["左 Control（游戏默认）", "R（需在游戏中把疾跑改为 R）"])
        sprintKey.selectItem(at: UserDefaults.standard.integer(forKey: "sprintKey") == 1 ? 1 : 0)
        sprintKey.target = self
        sprintKey.action = #selector(sprintChanged)
        stack.addArrangedSubview(sprintKey)
        addText("若 Control + 左键出现右键冲突，请选 R，并在游戏里同步修改疾跑键。游戏疾跑模式应设为“按住”。", to: stack, small: true)
        targetPicker.target = self
        targetPicker.action = #selector(selectTarget)
        targetPicker.widthAnchor.constraint(equalToConstant: 510).isActive = true
        stack.addArrangedSubview(targetPicker)
        targetLabel.font = .systemFont(ofSize: 12)
        targetLabel.widthAnchor.constraint(equalToConstant: 510).isActive = true
        stack.addArrangedSubview(targetLabel)
        addText("Esc 紧急停止；T、/、E 暂停。退出聊天或背包后，重新按快捷键开启。切出游戏、锁屏或睡眠后也需重新开启。", to: stack, small: true)
        permissionsLabel.font = .systemFont(ofSize: 12)
        stack.addArrangedSubview(permissionsLabel)
        let permissions = NSStackView()
        permissions.spacing = 8
        permissions.addArrangedSubview(button("检查并申请权限", #selector(requestPermissions)))
        permissions.addArrangedSubview(button("打开辅助功能", #selector(openAccessibility)))
        permissions.addArrangedSubview(button("打开输入监控", #selector(openInputMonitoring)))
        stack.addArrangedSubview(permissions)
        let actions = NSStackView()
        actions.spacing = 10
        actions.addArrangedSubview(button("立即停止", #selector(emergencyStop)))
        actions.addArrangedSubview(button("退出程序", #selector(quit)))
        stack.addArrangedSubview(actions)
    }

    func addText(_ text: String, to stack: NSStackView, small: Bool = false) {
        let label = NSTextField(wrappingLabelWithString: text)
        label.font = .systemFont(ofSize: small ? 12 : 14)
        if small { label.textColor = .secondaryLabelColor }
        label.widthAnchor.constraint(equalToConstant: 510).isActive = true
        stack.addArrangedSubview(label)
    }

    func button(_ title: String, _ selector: Selector) -> NSButton {
        NSButton(title: title, target: self, action: selector)
    }

    func buildMenu() {
        let mainMenu = NSMenu()
        let root = NSMenuItem()
        mainMenu.addItem(root)
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "退出 MC 连点助手", action: #selector(quit), keyEquivalent: "q").target = self
        root.submenu = appMenu
        NSApp.mainMenu = mainMenu
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        let menu = NSMenu()
        menu.addItem(withTitle: "显示设置", action: #selector(showSettings), keyEquivalent: "").target = self
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
            if detectionCache[pid] == nil {
                detectionCache[pid] = MacroPolicy.looksLikeMinecraft(name: app.localizedName ?? "", bundle: app.bundleIdentifier ?? "",
                                                                    command: commandLine(pid))
            }
            if detectionCache[pid] == true {
                detected.insert(app.processIdentifier)
            }
        }
        targetPIDs = detected
        var choices: [(String, Int)] = [("自动识别 Minecraft 游戏进程（推荐）", 0)]
        for app in apps.sorted(by: { $0.processIdentifier < $1.processIdentifier }) {
            choices.append(("手动绑定：\(app.localizedName ?? "游戏") · PID \(app.processIdentifier)", Int(app.processIdentifier)))
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
        policy.targetActive = isTargetFront()
        if policy.enabled && !policy.targetActive { stop("已暂停：已切出游戏。返回后按快捷键开启。") }
    }

    @objc func sleeping() { stop("已暂停：锁屏或睡眠。返回游戏后按快捷键开启。") }

    @discardableResult func installTap() -> Bool {
        if tap != nil { return true }
        guard AXIsProcessTrusted() else { return false }
        let types: [CGEventType] = [.leftMouseDown, .leftMouseUp, .leftMouseDragged,
                                   .rightMouseDown, .rightMouseUp, .rightMouseDragged,
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
            stop("输入监听中断，已停止。请重新开启。")
            if let tap { CGEvent.tapEnable(tap: tap, enable: true) }
            return Unmanaged.passUnretained(event)
        }
        if event.getIntegerValueField(.eventSourceUserData) == eventMarker { return Unmanaged.passUnretained(event) }
        if event.getIntegerValueField(.eventSourceUnixProcessID) == Int64(getpid()) { return Unmanaged.passUnretained(event) }
        let code = CGKeyCode(event.getIntegerValueField(.keyboardEventKeycode))
        if type == .keyUp && suppressedKeys.remove(code) != nil { return nil }
        if type == .keyDown && recordingHotkey && NSApp.isActive {
            if code == 53 { recordingHotkey = false; hotkeyButton.title = hotkeyTitle(); return nil }
            if [12, 14, 17, 44].contains(code) { notice = "请选其他键，T、E、/、Q 已保留。"; updateUI(); return nil }
            boundHotkey = code
            UserDefaults.standard.set(Int(code), forKey: "hotkey")
            recordingHotkey = false
            hotkeyButton.title = hotkeyTitle()
            suppressedKeys.insert(code)
            return nil
        }
        let active = isTargetFront()
        policy.targetActive = active
        if policy.enabled && !active { stop("已切出游戏，已停止。") }
        guard active else { return Unmanaged.passUnretained(event) }
        if type == .keyDown {
            if code == boundHotkey {
                if event.getIntegerValueField(.keyboardEventAutorepeat) == 0 {
                    if policy.enabled { stop("已关闭。") } else { start() }
                }
                suppressedKeys.insert(code)
                return nil
            }
            if policy.enabled && [53, 17, 14, 44].contains(code) {
                stop(code == 53 ? "Esc 紧急停止。" : "已暂停聊天／背包操作，完成后按快捷键重新开启。")
            }
            // Release before Cmd-Tab / Cmd-Q / other system shortcuts leave the game.
            if policy.enabled && event.flags.contains(.maskCommand) { stop("系统快捷键触发，已停止。") }
        }
        guard policy.enabled else { return Unmanaged.passUnretained(event) }
        switch type {
        case .flagsChanged:
            if sprintOwned && ownedSprintCode == 59 && !event.flags.contains(.maskControl) {
                event.flags.insert(.maskControl)
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
        guard isTargetFront(), AXIsProcessTrusted(), let tap, CGEvent.tapIsEnabled(tap: tap) else {
            notice = "无法开启：请先授权并检查输入监听。"; updateUI(); return
        }
        hardwareMouse.start()
        guard hardwareMouse.connected else {
            notice = "未连接到鼠标硬件。为避免自动连点，保持关闭；请检查输入监控权限并重启。"
            updateUI(); return
        }
        policy.physicalLeftHeld = false // A fresh physical press is required after every enable.
        policy.physicalRightHeld = false
        policy.targetActive = true
        policy.enabled = true
        notice = "已就绪：不按不点，真实按住哪一键才连点哪一键。"
        if sprint.state == .on { pressSprint() }
        updateUI()
    }

    func stop(_ reason: String) {
        policy.stop()
        cancelClicks()
        releaseSprint()
        notice = reason
        updateUI()
    }

    func click(_ button: MacroMouseButton) {
        clickTimers.removeValue(forKey: button)?.invalidate()
        guard policy.mayClick(button, hardwareDown: hardwareMouse.isDown(button)), isTargetFront(), AXIsProcessTrusted() else {
            cancelClicks(button); return
        }
        postMouse(button, down: true)
        emittedDown.insert(button)
        releaseTimers.removeValue(forKey: button)?.invalidate()
        let release = Timer(timeInterval: 0.007, repeats: false) { [weak self] _ in
            self?.releaseMouse(button)
        }
        releaseTimers[button] = release
        RunLoop.main.add(release, forMode: .common)
        let cps = Double.random(in: cpsMin...cpsMax)
        let next = Timer(timeInterval: MacroPolicy.interval(cps: cps), repeats: false) { [weak self] _ in self?.click(button) }
        clickTimers[button] = next
        RunLoop.main.add(next, forMode: .common)
    }

    func hardwareChanged(_ button: MacroMouseButton, down: Bool) {
        if !down {
            if button == .left { policy.physicalLeftHeld = false }
            else { policy.physicalRightHeld = false }
            cancelClicks(button)
            return
        }
        guard policy.enabled, isTargetFront() else { return }
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
        event.setIntegerValueField(.mouseEventClickState, value: 1)
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        event.post(tap: .cghidEventTap)
    }

    func releaseMouse(_ button: MacroMouseButton) {
        releaseTimers.removeValue(forKey: button)?.invalidate()
        if emittedDown.remove(button) != nil { postMouse(button, down: false) }
    }

    func cancelClicks(_ button: MacroMouseButton) {
        clickTimers.removeValue(forKey: button)?.invalidate()
        releaseMouse(button)
    }

    func cancelClicks() {
        for button in MacroMouseButton.allCases { cancelClicks(button) }
    }

    func pressSprint() {
        guard !sprintOwned, policy.enabled, isTargetFront() else { return }
        let code: CGKeyCode = sprintKey.indexOfSelectedItem == 0 ? 59 : 15
        // Do not take ownership of a sprint key the user is already holding.
        guard !CGEventSource.keyState(.hidSystemState, key: code) else { return }
        ownedSprintCode = code
        sprintOwned = true
        postSprint(down: true)
    }

    func postSprint(down: Bool) {
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: ownedSprintCode, keyDown: down) else { return }
        if ownedSprintCode == 59 {
            event.type = .flagsChanged
            var flags = CGEventSource.flagsState(.combinedSessionState)
            if down { flags.insert(.maskControl) } else { flags.remove(.maskControl) }
            event.flags = flags
        }
        event.setIntegerValueField(.eventSourceUserData, value: eventMarker)
        event.post(tap: .cghidEventTap)
    }

    func releaseSprint() {
        if sprintOwned { postSprint(down: false); sprintOwned = false }
    }

    func updateUI() {
        guard window != nil else { return }
        statusLabel.stringValue = notice
        statusLabel.textColor = policy.enabled ? .systemGreen : .labelColor
        statusItem?.button?.title = policy.enabled ? "MC ●" : "MC ○"
        let ids = targetPIDs.sorted().map(String.init).joined(separator: ", ")
        targetLabel.stringValue = manualPID.map { "已绑定游戏进程 \($0)，进程退出后需重新绑定。" } ??
            (targetPIDs.isEmpty ? "尚未识别到游戏。请先启动 Minecraft；识别失败时可手动选择 Java 游戏进程。" : "已识别游戏进程：\(ids)")
        permissionsLabel.stringValue = "辅助功能：\(AXIsProcessTrusted() ? "已授权" : "未授权")　输入监控：\(CGPreflightListenEventAccess() ? "已授权" : "未授权")　硬件：\(hardwareMouse.connected ? "已连接" : "未连接")"
    }

    func hotkeyTitle() -> String {
        "修改开关键：\(boundHotkey == 50 ? "`（数字 1 左侧）" : "物理键码 \(boundHotkey)")"
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
        if !installTap() { notice = "请先授予辅助功能权限，再修改快捷键。"; updateUI(); return }
        recordingHotkey = true
        hotkeyButton.title = "请按新键（Esc 取消）"
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
