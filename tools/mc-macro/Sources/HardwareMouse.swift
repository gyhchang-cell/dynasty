import Foundation
import IOKit.hid

/// Reads physical HID button values; Quartz-generated clicks cannot hold this gate open.
final class HardwareMouse {
    var onChange: ((MacroMouseButton, Bool) -> Void)?
    private var manager: IOHIDManager?
    private var elements: [UInt: [MacroMouseButton: [IOHIDElement]]] = [:]
    private var last: [MacroMouseButton: Bool] = [:]
    var connected: Bool { manager != nil && !elements.isEmpty }

    func start() {
        guard manager == nil else { return }
        let hid = IOHIDManagerCreate(kCFAllocatorDefault, IOOptionBits(kIOHIDOptionsTypeNone))
        let matches: [[String: Int]] = [
            [kIOHIDDeviceUsagePageKey: 1, kIOHIDDeviceUsageKey: 2],
            [kIOHIDDeviceUsagePageKey: 1, kIOHIDDeviceUsageKey: 1],
            [kIOHIDDeviceUsagePageKey: 13, kIOHIDDeviceUsageKey: 5]
        ]
        IOHIDManagerSetDeviceMatchingMultiple(hid, matches as CFArray)
        IOHIDManagerSetInputValueMatching(hid, [kIOHIDElementUsagePageKey: 9] as CFDictionary)
        let context = Unmanaged.passUnretained(self).toOpaque()
        IOHIDManagerRegisterDeviceMatchingCallback(hid, { context, result, _, device in
            guard let context, result == kIOReturnSuccess else { return }
            Unmanaged<HardwareMouse>.fromOpaque(context).takeUnretainedValue().add(device)
        }, context)
        IOHIDManagerRegisterDeviceRemovalCallback(hid, { context, _, _, device in
            guard let context else { return }
            let owner = Unmanaged<HardwareMouse>.fromOpaque(context).takeUnretainedValue()
            owner.elements.removeValue(forKey: owner.id(device))
            owner.refresh()
        }, context)
        IOHIDManagerRegisterInputValueCallback(hid, { context, result, _, _ in
            guard let context else { return }
            let owner = Unmanaged<HardwareMouse>.fromOpaque(context).takeUnretainedValue()
            if result == kIOReturnSuccess { owner.refresh() }
            else { owner.releaseAll() }
        }, context)
        IOHIDManagerScheduleWithRunLoop(hid, CFRunLoopGetMain(), CFRunLoopMode.commonModes.rawValue)
        let result = IOHIDManagerOpen(hid, IOOptionBits(kIOHIDOptionsTypeNone))
        guard result == kIOReturnSuccess else {
            IOHIDManagerUnscheduleFromRunLoop(hid, CFRunLoopGetMain(), CFRunLoopMode.commonModes.rawValue)
            return
        }
        manager = hid
        if let devices = IOHIDManagerCopyDevices(hid) as? Set<IOHIDDevice> {
            for device in devices { add(device) }
        }
    }

    private func id(_ device: IOHIDDevice) -> UInt {
        UInt(bitPattern: Unmanaged.passUnretained(device).toOpaque())
    }

    private func add(_ device: IOHIDDevice) {
        guard let values = IOHIDDeviceCopyMatchingElements(device,
            [kIOHIDElementUsagePageKey: 9] as CFDictionary, IOOptionBits(kIOHIDOptionsTypeNone)) as? [IOHIDElement] else { return }
        var buttons: [MacroMouseButton: [IOHIDElement]] = [:]
        for element in values {
            let usage = IOHIDElementGetUsage(element)
            guard usage == 1 || usage == 2, IOHIDElementGetType(element) == kIOHIDElementTypeInput_Button else { continue }
            buttons[usage == 1 ? .left : .right, default: []].append(element)
        }
        if !buttons.isEmpty { elements[id(device)] = buttons }
        // Baseline only: connecting a held mouse must not trigger the macro.
        for button in MacroMouseButton.allCases { last[button] = isDown(button) }
    }

    func isDown(_ button: MacroMouseButton) -> Bool {
        let storage = UnsafeMutablePointer<Unmanaged<IOHIDValue>>.allocate(capacity: 1)
        defer { storage.deallocate() }
        for buttons in elements.values {
            for element in buttons[button] ?? [] {
                if IOHIDDeviceGetValue(IOHIDElementGetDevice(element), element, storage) == kIOReturnSuccess,
                   IOHIDValueGetIntegerValue(storage.pointee.takeUnretainedValue()) != 0 { return true }
            }
        }
        return false
    }

    func refresh() {
        for button in MacroMouseButton.allCases {
            let down = isDown(button)
            if down != (last[button] ?? false) {
                last[button] = down
                onChange?(button, down)
            }
        }
    }

    private func releaseAll() {
        for button in MacroMouseButton.allCases { last[button] = false; onChange?(button, false) }
    }

    func stop() {
        if let manager {
            IOHIDManagerUnscheduleFromRunLoop(manager, CFRunLoopGetMain(), CFRunLoopMode.commonModes.rawValue)
            IOHIDManagerClose(manager, IOOptionBits(kIOHIDOptionsTypeNone))
        }
        manager = nil
        elements.removeAll()
        releaseAll()
    }
}
