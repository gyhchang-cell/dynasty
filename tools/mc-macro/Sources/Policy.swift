import Foundation

// Invalidates queued input without delaying key/button releases.
final class BridgeInputEpoch {
    enum Decision {case send, cancelled, expired}
    private let lock = NSLock()
    private var value: UInt64 = 0
    func snapshot() -> UInt64 { lock.lock(); defer { lock.unlock() }; return value }
    func invalidate() { lock.lock(); value &+= 1; lock.unlock() }
    func accepts(_ token: UInt64) -> Bool { lock.lock(); defer { lock.unlock() }; return value == token }
    func authorize(_ token:UInt64,queuedAt:Double,now:Double)->Decision {
        lock.lock();defer{lock.unlock()}
        guard value==token else{return .cancelled}
        guard now>=queuedAt,now-queuedAt<=0.080 else {
            value &+= 1
            return .expired
        }
        return .send
    }
}

// Every event in a bridge sequence carries its held modifier state. LWJGL
// updates modifiers from mouse/key flags too, so flags=[] can release sprint.
enum BridgeMode:String,CaseIterable {
    case level, rising
    var title:String {self == .level ? "平桥（保持高度）":"Speed Telly（逐跳升高）"}
    var rise:Int {self == .level ? 0:1}
    var next:BridgeMode {self == .level ? .rising:.level}
}

// Consume conflicting manual input only while a committed jump is finishing.
// Remember swallowed downs so their repeats/ups cannot leak after landing.
// Inputs are never replayed: a fresh press is required after the handoff.
struct BridgeManualInputGate {
    enum Input {
        case key(UInt16, Bool), modifier, motion(Int64, Int64)
        case button(Int64, Bool), drag(Int64), scroll
        var hasIntent:Bool {
            if case let .motion(x,y)=self {return x != 0 || y != 0}
            return true
        }
    }
    private var keys=Set<UInt16>()
    private var buttons=Set<Int64>()
    func suppressesButton(_ number:Int64)->Bool {buttons.contains(number)}
    mutating func consume(_ input:Input,duringFinish:Bool)->Bool {
        switch input {
        case let .key(code,down):
            if down {if duringFinish {keys.insert(code)};return duringFinish || keys.contains(code)}
            return keys.remove(code) != nil || duringFinish
        case let .button(number,down):
            if down {if duringFinish {buttons.insert(number)};return duringFinish || buttons.contains(number)}
            return buttons.remove(number) != nil || duringFinish
        case let .drag(number):return duringFinish || buttons.contains(number)
        default:return duringFinish
        }
    }
}

struct BridgeModifiers {
    private(set) var flags:UInt64=0
    mutating func update(code:UInt16,down:Bool)->Bool {
        let spec:(UInt64,UInt64,UInt64)
        switch code {
        case 59: spec=(1<<18,1,0x2000)
        case 62: spec=(1<<18,0x2000,1)
        case 56: spec=(1<<17,2,4)
        case 60: spec=(1<<17,4,2)
        case 58: spec=(1<<19,0x20,0x40)
        case 61: spec=(1<<19,0x40,0x20)
        default:return false
        }
        if down {flags |= spec.0|spec.1}
        else {flags &= ~spec.1;if flags & spec.2 == 0 {flags &= ~spec.0}}
        return true
    }
}

enum MacroMouseButton: CaseIterable { case left, right }

struct MacroPolicy {
    var enabled = false
    var physicalLeftHeld = false
    var physicalRightHeld = false
    var targetActive = false
    var menuPaused = false
    var mayClick: Bool { enabled && targetActive && !menuPaused && physicalLeftHeld }
    func mayClick(_ button: MacroMouseButton) -> Bool {
        enabled && targetActive && !menuPaused && (button == .left ? physicalLeftHeld : physicalRightHeld)
    }
    func mayClick(_ button: MacroMouseButton, hardwareDown: Bool) -> Bool {
        hardwareDown && mayClick(button)
    }

    mutating func stop() {
        enabled = false
        physicalLeftHeld = false
        physicalRightHeld = false
        menuPaused = false
    }

    mutating func suspend() {
        physicalLeftHeld = false
        physicalRightHeld = false
    }

    mutating func reconcileHardware(left: Bool, right: Bool) {
        physicalLeftHeld = enabled && targetActive && left
        physicalRightHeld = enabled && targetActive && right
    }

    static func validRange(_ minimum: Double, _ maximum: Double) -> Bool {
        minimum.isFinite && maximum.isFinite && minimum >= 1 && maximum <= 40 && minimum <= maximum
    }

    static func interval(cps: Double) -> TimeInterval { 1 / cps }

    static func looksLikeMinecraft(name: String, bundle: String, command: String) -> Bool {
        let name = name.lowercased()
        let bundle = bundle.lowercased()
        let command = command.lowercased()
        // Launchers are deliberately excluded: a launcher must never receive macros.
        if name.contains("launcher") || bundle.contains("launcher") { return false }
        if bundle.hasPrefix("com.mojang.minecraftpe") { return true }
        let gameEntrypoints = ["net.minecraft.client.main.main", "net.minecraft.launchwrapper.launch",
            "net.fabricmc.loader.impl.launch.knot.knotclient", "cpw.mods.bootstraplauncher.bootstraplauncher",
            "cpw.mods.modlauncher.launcher", "net.minecraft.client.minecraft", "com.moonsworth.lunar"]
        return gameEntrypoints.contains { command.contains($0) }
    }
}

enum SprintModifier {
    // LWJGL 2 checks the device-specific left Control bit, not just the generic flag.
    static let genericControl: UInt64 = 1 << 18
    static let leftControl: UInt64 = 0x1
    static let rightControl: UInt64 = 0x2000
    static func flags(_ current: UInt64, down: Bool) -> UInt64 {
        if down { return current | genericControl | leftControl }
        let released = current & ~leftControl
        return released & rightControl == 0 ? released & ~genericControl : released
    }
}

// A repeated down may be discarded by the game's keyboard state cache. Renew
// with a distinct up/down edge, leaving several game ticks to observe the up.
struct SprintRenewal {
    private(set) var isDown = false
    private var deadline: TimeInterval?

    mutating func begin(now: TimeInterval) {
        isDown = true
        deadline = now + 0.8
    }

    mutating func advance(now: TimeInterval) -> Bool? {
        guard let deadline, now >= deadline else { return nil }
        isDown.toggle()
        self.deadline = now + (isDown ? 0.8 : 0.075)
        return isDown
    }
}

struct ClickRhythm {
    private var position = 0.5
    private var target = 0.5
    private var remaining = 0

    struct Beat {
        let interval: TimeInterval
        let held: TimeInterval
    }

    mutating func next<R: RandomNumberGenerator>(minimum: Double, maximum: Double, using rng: inout R) -> Beat {
        precondition(MacroPolicy.validRange(minimum, maximum))
        if remaining == 0 {
            target = Double.random(in: 0...1, using: &rng)
            remaining = Int.random(in: 6...22, using: &rng)
        }
        remaining -= 1
        position += (target - position) * 0.22
        let localVariation = Double.random(in: -0.08...0.08, using: &rng)
        let fraction = min(1, max(0, position + localVariation))
        let cps = minimum + (maximum - minimum) * fraction
        let interval = 1 / cps
        // Vary press duration independently; always leave an up phase.
        let held = interval * Double.random(in: 0.28...0.58, using: &rng)
        return Beat(interval: interval, held: held)
    }
}
