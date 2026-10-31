import AppKit
import ApplicationServices

extension MacroApp {
    var wantsToolObservation: Bool {
        autoToolEnabled.state == .on && !policy.enabled && !sessionSuspended && isTargetFront()
    }

    @objc func inventorySettingsChanged() {
        UserDefaults.standard.set(autoToolEnabled.state == .on, forKey:"autoToolEnabled")
        UserDefaults.standard.set(supplyEnabled.state == .on, forKey:"sameBlockSupply")
        cancelInventoryActions()
        updateUI()
    }

    func cancelInventoryActions() {
        autoToolPress.cancel();inventoryInputEpoch.invalidate()
        supplyPending=nil
    }

    func physicalToolPress() {
        let now=ProcessInfo.processInfo.systemUptime
        guard wantsToolObservation, !telly.active, telly.phase == .idle,
              !bridgeManualInput.suppressesButton(0), !bridgeChatOpen,
              !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand),
              let state=bridgeWorldPreview, let inventory=state.inventory,
              now-state.pose.time >= 0, now-state.pose.time+inventory.age <= 0.10 else {return}
        autoToolPress.begin(now:now,world:state.world,inventory:inventory)
    }

    func observeInventory(_ state:BridgeWorldState?) {
        guard let state, let inventory=state.inventory else {autoToolPress.cancel();inventoryInputEpoch.invalidate();return}
        let now=ProcessInfo.processInfo.systemUptime
        if let choice=autoToolPress.update(now:now,sampledAt:state.pose.time-inventory.age,
            world:state.world,inventory:inventory,enabled:wantsToolObservation && !bridgeChatOpen,
            clicking:policy.enabled,bridging:telly.active || telly.phase != .idle,
            physicalDown:hardwareMouse.isDown(.left)) {
            if sendHotbarSelection(choice.slot, inventory:inventory, forBridge:false) {
                traceBridge("TOOL slot=\(choice.slot) item=\(choice.itemID) block=\(inventory.blockID ?? -1)")
            }
        }
    }

    func prepareBridgeSupply(_ state:BridgeWorldState) -> Bool {
        guard supplyEnabled.state == .on else {return true}
        let now=ProcessInfo.processInfo.systemUptime
        guard let inventory=state.inventory, now-state.pose.time+inventory.age <= 0.10 else {
            telly.requestSupplyFinish();return false
        }
        if let pending=supplyPending {
            if inventory.selected == pending.slot,
               inventory.current?.identity == pending.identity,
               state.pose.time-inventory.age > pending.time {
                supplyPending=nil
            } else {
                if now-pending.time > 0.25 {supplyPending=nil;telly.requestSupplyFinish()}
                return false
            }
        }
        switch bridgeSupply.evaluate(inventory,grounded:true,selectable:selectableSlots(inventory)) {
        case .ready:return true
        case .select(let slot):
            // This preflight path waits for actual support before selecting.
            // Airborne emergency replenishment is handled before placement.
            guard state.onGround else {return false}
            guard let identity=bridgeSupply.identity,
                  sendHotbarSelection(slot,inventory:inventory,forBridge:true) else {
                telly.requestSupplyFinish();return false
            }
            supplyPending=(slot,identity,now)
            traceBridge("SUPPLY slot=\(slot) same_material=true")
            return false
        case .insufficient,.invalid:
            telly.requestSupplyFinish();return false
        }
    }

    func preparePlacementSupply()->Bool {
        guard supplyEnabled.state == .on else{return true}
        let now=ProcessInfo.processInfo.systemUptime
        guard let state=bridgeWorldPreview,let inventory=state.inventory,
              now-state.pose.time+inventory.age<=0.10 else{return false}
        if let pending=supplyPending {
            if inventory.selected==pending.slot,inventory.current?.identity==pending.identity,
               state.pose.time-inventory.age>pending.time {supplyPending=nil}
            else if now-pending.time>0.10 {supplyPending=nil}
            else {return false}
        }
        switch bridgeSupply.beforePlacement(inventory,selectable:selectableSlots(inventory)) {
        case .ready:return true
        case .select(let slot):
            guard let identity=bridgeSupply.identity,
                  sendHotbarSelection(slot,inventory:inventory,forBridge:true,allowAirborne:true) else{return (inventory.current?.count ?? 0)>1}
            supplyPending=(slot,identity,now)
            traceBridge("SUPPLY slot=\(slot) same_material=true emergency=true")
            return false
        case .insufficient,.invalid:return false
        }
    }

    func selectableSlots(_ inventory:HotbarSnapshot)->Set<Int> {
        var reserved:Set<UInt16>=[15,17,boundHotkey]
        if let c=telly.config {reserved.formUnion([c.forward,c.back,c.left,c.right,c.sneak,c.jump,c.sprint])}
        return Set((0..<9).filter {slot in
            guard let key=HotbarKeys.selection(slot,in:inventory,reserved:reserved) else{return false}
            return !CGEventSource.keyState(.hidSystemState,key:key)
        })
    }

    @discardableResult func sendHotbarSelection(_ slot:Int,inventory:HotbarSnapshot,forBridge:Bool,allowAirborne:Bool=false)->Bool {
        guard inventory.valid,(0..<9).contains(slot),slot != inventory.selected,
              let code=HotbarKeys.selection(slot,in:inventory,reserved:[15,17,boundHotkey]),
              isTargetFront(), !sessionSuspended, bridgeAccessAllowed,
              !CGEventSource.keyState(.hidSystemState,key:code),
              let origin=bridgeWorldPreview,
              let pid=bridgeConfigPID, NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else {return false}
        if let config=telly.config,
           [config.forward,config.back,config.left,config.right,config.sneak,config.jump,config.sprint].contains(code) {return false}
        guard !CGEventSource.flagsState(.combinedSessionState).contains(.maskCommand) else {return false}
        let gate=inventoryInputEpoch, token=gate.snapshot()
        let bridgeGate=bridgeInputEpoch, bridgeToken=bridgeGate.snapshot()
        let began=ProcessInfo.processInfo.systemUptime
        let session=gameTelemetry.sessionID
        bridgeInputQueue.async { [weak self] in
            guard let self,gate.accepts(token),(!forBridge || bridgeGate.accepts(bridgeToken)),
                  NSWorkspace.shared.frontmostApplication?.processIdentifier==pid,
                  ProcessInfo.processInfo.systemUptime-began < 0.075 else {return}
            // Revalidate the current ray/GUI and selected stack at delivery,
            // not just when the input was scheduled.
            DispatchQueue.main.sync {
                guard gate.accepts(token),!self.sessionSuspended,self.isTargetFront(),
                      let state=self.bridgeWorldPreview,let latest=state.inventory,
                      state.world==origin.world,self.gameTelemetry.pid==pid,self.gameTelemetry.sessionID==session,
                      ProcessInfo.processInfo.systemUptime-state.pose.time+latest.age<=0.10,
                      latest.selected==inventory.selected,
                      HotbarKeys.selection(slot,in:latest,reserved:[15,17,self.boundHotkey])==code,
                      latest.slots.first(where:{$0.slot==slot})?.identity==inventory.slots.first(where:{$0.slot==slot})?.identity,
                      !CGEventSource.keyState(.hidSystemState,key:code),
                      ProcessInfo.processInfo.systemUptime-began<0.075 else {return}
                if forBridge {
                    guard self.telly.active,(state.onGround || (allowAirborne && self.telly.phase == .flight)),bridgeGate.accepts(bridgeToken) else{return}
                } else {
                    guard self.wantsToolObservation,!self.telly.active,self.hardwareMouse.isDown(.left),
                          latest.hitKind=="block",latest.target==inventory.target,latest.blockID==inventory.blockID else{return}
                }
                let physical=CGEventSource.flagsState(.hidSystemState)
                guard !physical.contains(.maskCommand) else{return}
                let flags=forBridge ? physical.union(CGEventFlags(rawValue:self.bridgeModifiers.flags)) : physical
                guard let down=CGEvent(keyboardEventSource:self.source,virtualKey:code,keyDown:true),
                      let up=CGEvent(keyboardEventSource:self.source,virtualKey:code,keyDown:false) else {return}
                // Validation, cancellation and pulse delivery share the main queue.
                for event in [down,up] {
                    event.flags=flags
                    event.setIntegerValueField(.eventSourceUserData,value:eventMarker)
                    event.postToPid(pid)
                }
            }
        }
        return true
    }
}
