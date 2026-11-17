import AppKit
import ApplicationServices

enum SwordMouseBoundary {
    static func isNativeRight(_ type:CGEventType)->Bool {
        type == .rightMouseDown || type == .rightMouseUp || type == .rightMouseDragged
    }
    static func mayEmit(_ type:CGEventType)->Bool {
        type == .leftMouseDown || type == .leftMouseUp || type == .keyDown || type == .keyUp
    }
}

extension MacroApp {
    private static let swordModifiers:[UInt16:CGEventFlags]=[56:.maskShift,60:.maskShift,58:.maskAlternate,61:.maskAlternate]
    func configureSword() {
        // The old preference meant "allow held-left combat", not unattended
        // activation. Each launch starts off until the UI or backslash enables it.
        swordEnabled.state = .off
        swordEnabled.toolTip="\\ 独立开关；持剑、斧或空手自动左键出手，无需按左键。右键完全原生，不取消举盾，不修改使用键。游戏允许攻击后自动继续。手动瞄准。"
        swordEnabled.target=self;swordEnabled.action=#selector(swordChanged)
        sword.click = { [weak self] in self?.swordClick() }
        sword.jump = { [weak self] in self?.swordJump() }
        sword.forward = { [weak self] suppress in self?.swordForward(suppress) }
        sword.release = { [weak self] in self?.releaseSwordInput() }
        sword.trace = { [weak self] in self?.traceBridge("SWORD "+$0) }
    }
    @objc func swordChanged() {
        swordSwitch.setEnabled(swordEnabled.state == .on,now:ProcessInfo.processInfo.systemUptime)
        applySwordSwitch()
    }
    private func applySwordSwitch() {
        swordEnabled.state=swordSwitch.enabled ? .on:.off
        UserDefaults.standard.set(swordEnabled.state == .on,forKey:"swordEnabled")
        sword.cancel();cancelClicks();leftClickHold.cancel();policy.physicalLeftHeld=false
        cancelInventoryActions();serviceForceSprint();updateSwordUI()
        traceBridge("SWORD SWITCH enabled=\(swordSwitch.enabled)")
    }
    var swordAllowed:Bool {swordEnabled.state == .on && modernVersion=="26.1" && bridgeDiagnosticUntil<=ProcessInfo.processInfo.systemUptime && !sessionSuspended && isTargetFront() &&
        modernTelemetry.pid==NSWorkspace.shared.frontmostApplication?.processIdentifier && !anchor.active && !telly.active &&
        !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand) && (tap.map{CGEvent.tapIsEnabled(tap:$0)} ?? false)}
    func serviceSword() {
        let now=ProcessInfo.processInfo.systemUptime
        guard swordSwitch.enabled else {if sword.held {sword.cancel()};return}
        guard swordSwitch.canRun(anchorState,now:now,allowed:swordAllowed),let state=anchorState else {
            if sword.held {sword.cancel(MeleeReadiness.problem(anchorState,now:now) ?? "等待游戏状态")};return
        }
        if !sword.held {
            cancelClicks();leftClickHold.cancel();cancelInventoryActions()
            if let code=state.combat.flatMap({SprintGameConfig.binding($0.forwardKey)}) {swordForwardPhysical = swordForwardPhysical || CGEventSource.keyState(.hidSystemState,key:code)}
            sword.begin(state,now:now)
        }
        sword.preserveSprint=sprint.state == .on
        sword.tick(state,now:now,allowed:swordAllowed)
        if sword.requiresRearm {
            swordSwitch.setEnabled(false,now:now);swordEnabled.state = .off
            UserDefaults.standard.set(false,forKey:"swordEnabled");updateSwordUI()
        }
    }
    func updateSwordUI() {
        let now=ProcessInfo.processInfo.systemUptime
        if !swordSwitch.enabled {swordStatus.stringValue=sword.requiresRearm ? sword.message:"已关闭"}
        else if modernVersion != "26.1" {swordStatus.stringValue="需要 Java 26.1"}
        else if !AXIsProcessTrusted() {swordStatus.stringValue="辅助功能未授权 · 无法发送攻击"}
        else if !CGPreflightListenEventAccess() {swordStatus.stringValue="输入监控未授权"}
        else if !isTargetFront() {swordStatus.stringValue="游戏不在前台 · 已暂停"}
        else if anchorState==nil,!anchorError.isEmpty {swordStatus.stringValue=anchorError}
        else if let reason=MeleeReadiness.problem(anchorState,now:now) {swordStatus.stringValue=reason}
        else if tap.map({CGEvent.tapIsEnabled(tap:$0)}) != true {swordStatus.stringValue="输入监听未连接 · 请重新检查权限"}
        else if let s=anchorState {swordStatus.stringValue="已识别\(MeleeMainHand.classify(MeleeReadiness.item(s)).label) · \(sword.message)"}
        swordStatus.toolTip=swordStatus.stringValue
    }
    // Runs before the legacy clicker; the toggle never consumes menu/chat text.
    func handleSword(_ type:CGEventType,_ event:CGEvent)->Bool {
        let now=ProcessInfo.processInfo.systemUptime
        // Every physical right event is passed through unchanged, on/off and in
        // menus alike. Updating the aim barrier does not own or cancel a gesture.
        if SwordMouseBoundary.isNativeRight(type) {
            if swordSwitch.enabled,isTargetFront() {sword.noteMotion(anchorState,now:now)}
            return false
        }
        let code=UInt16(event.getIntegerValueField(.keyboardEventKeycode))
        if (type == .keyDown || type == .keyUp),code==42,!recordingHotkey {
            let before=swordSwitch.enabled
            let consumed=swordSwitch.key(down:type == .keyDown,repeated:event.getIntegerValueField(.keyboardEventAutorepeat) != 0,
                gameplay:isTargetFront() && modernVersion=="26.1" && anchorState?.fresh(now)==true,
                modified:!event.flags.intersection([.maskCommand,.maskControl,.maskAlternate]).isEmpty,now:now)
            if consumed {if before != swordSwitch.enabled {applySwordSwitch()};return true}
        }
        if type == .mouseMoved || type == .leftMouseDragged {
            if swordEnabled.state == .on,isTargetFront() {sword.noteMotion(anchorState,now:now)}
            if sword.held,type == .leftMouseDragged {event.type = .mouseMoved}
        }
        if isTargetFront(),let key=anchorState?.combat.flatMap({SprintGameConfig.binding($0.forwardKey)}),code==key {
            if type == .keyDown {swordForwardPhysical=true}
            if type == .keyUp {swordForwardPhysical=false}
            if type == .flagsChanged,let mask=Self.swordModifiers[key] {swordForwardPhysical=event.flags.contains(mask)}
        }
        if type == .leftMouseUp,swordLeftConsumed {
            swordLeftConsumed=false;return true
        }
        if swordSwitch.enabled,isTargetFront() {
            if type == .keyDown,code==swordJumpKey {swordJumpKey=nil}
            if type == .flagsChanged,code==swordJumpKey,let mask=Self.swordModifiers[code],event.flags.contains(mask) {swordJumpKey=nil}
            if type == .scrollWheel {swordSwitch.pause(now:now);sword.cancel()}
            if type == .keyDown {
                let keys=anchorState?.combat?.movementKeys ?? ["w","a","s","d","space","left.shift","left.control"].map{"key.keyboard."+$0}
                let movement=Set(keys.compactMap{SprintGameConfig.binding($0)})
                if !movement.contains(code) {swordSwitch.pause(now:now);sword.cancel()}
            }
        }
        if type == .leftMouseDown,swordLeftConsumed {return true}
        guard type == .leftMouseDown,swordSwitch.canRun(anchorState,now:now,allowed:swordAllowed),!event.flags.contains(.maskCommand) else{return false}
        cancelClicks();leftClickHold.cancel();cancelInventoryActions()
        swordLeftConsumed=true;return true
    }
    private func swordEvent(_ event:CGEvent,up:Bool=false) {
        guard SwordMouseBoundary.mayEmit(event.type) else{return}
        guard let pid=up ? (swordInputPID ?? modernTelemetry.pid):modernTelemetry.pid,up || swordAllowed else{return}
        if !up {swordInputPID=pid}
        event.flags=[];event.setIntegerValueField(.eventSourceUserData,value:eventMarker)
        if [.keyDown,.keyUp].contains(event.type),let mask=Self.swordModifiers[UInt16(event.getIntegerValueField(.keyboardEventKeycode))] {
            let down=event.type == .keyDown;event.type = .flagsChanged;event.flags=down ? mask:[]
        }
        if event.type == .leftMouseDown || event.type == .leftMouseUp {
            event.setIntegerValueField(.mouseEventDeltaX,value:0);event.setIntegerValueField(.mouseEventDeltaY,value:0)
            if NSWorkspace.shared.frontmostApplication?.processIdentifier==pid {event.post(tap:.cghidEventTap)} else if up {event.postToPid(pid)}
        } else {event.postToPid(pid)}
    }
    func swordClick() {
        guard swordAllowed,let e=CGEvent(mouseEventSource:source,mouseType:.leftMouseDown,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left) else{return}
        e.setIntegerValueField(.mouseEventClickState,value:1);swordMouseDown=true;swordEvent(e)
        DispatchQueue.main.asyncAfter(deadline:.now()+0.014) { [weak self] in self?.releaseSwordMouse() }
    }
    private func releaseSwordMouse() {
        guard swordMouseDown else{return};swordMouseDown=false
        if let e=CGEvent(mouseEventSource:source,mouseType:.leftMouseUp,mouseCursorPosition:CGEvent(source:nil)?.location ?? .zero,mouseButton:.left) {swordEvent(e,up:true)}
    }
    func swordJump() {
        guard swordAllowed,let c=anchorState?.combat,let key=SwordController.actionKey(c.jumpKey),!c.jumpDown,
              !CGEventSource.keyState(.hidSystemState,key:key),let e=CGEvent(keyboardEventSource:source,virtualKey:key,keyDown:true) else{return}
        swordJumpKey=key;swordEvent(e)
        DispatchQueue.main.asyncAfter(deadline:.now()+0.065) { [weak self] in self?.releaseSwordJump() }
    }
    private func releaseSwordJump() {
        guard let key=swordJumpKey else{return};swordJumpKey=nil
        if let e=CGEvent(keyboardEventSource:source,virtualKey:key,keyDown:false) {swordEvent(e,up:true)}
    }
    func swordForward(_ suppress:Bool) {
        if suppress {
            guard swordAllowed,let c=anchorState?.combat,let key=SwordController.actionKey(c.forwardKey) else{return}
            serviceForceSprint();swordForwardKey=key
            if let e=CGEvent(keyboardEventSource:source,virtualKey:key,keyDown:false) {swordEvent(e,up:true)}
        } else if let key=swordForwardKey {
            swordForwardKey=nil
            if swordAllowed,swordForwardPhysical,let e=CGEvent(keyboardEventSource:source,virtualKey:key,keyDown:true) {swordEvent(e)}
        }
    }
    func releaseSwordInput() {releaseSwordMouse();releaseSwordJump();swordForward(false)}
}
