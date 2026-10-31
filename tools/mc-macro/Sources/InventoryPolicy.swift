import Foundation

// Local, read-only observations. Slots use Minecraft's zero-based hotbar index.
struct HotbarItem: Decodable, Equatable {
    let slot: Int
    let itemID: Int
    let metadata: Int
    let count: Int
    let identity: String
    let kind: String
    let fullBlock: Bool
    let score: Double
}

struct HotbarSnapshot: Decodable {
    let selected: Int
    let hitKind: String
    let blockID: Int?
    let hardness: Double?
    let target: [Int]?
    let slots: [HotbarItem]
    let keys: [Int]
    let blockedKeys: [Int]
    let age: Double
    var current: HotbarItem? { slots.first { $0.slot == selected } }
    var valid: Bool {
        (0..<9).contains(selected) && keys.count == 9 && blockedKeys.count <= 128 && slots.count <= 9 &&
        Set(slots.map(\.slot)).count == slots.count && age.isFinite && (0...0.10).contains(age) &&
        slots.allSatisfy { (0..<9).contains($0.slot) && $0.itemID > 0 && $0.metadata >= 0 &&
            (1...64).contains($0.count) && !$0.identity.isEmpty && $0.identity.count <= 256 &&
            $0.score.isFinite && $0.score >= 0 } &&
        (target == nil || target?.count == 3) && (hardness == nil || hardness!.isFinite)
    }
    func matches(_ item: HotbarItem, identity: String) -> Bool {
        item.kind == "block" && item.fullBlock && item.identity == identity
    }
}

// A malformed optional feature must never invalidate the established bridge packet.
struct OptionalObservation<T: Decodable>: Decodable {
    let value: T?
    init(from decoder: Decoder) throws { value = try? T(from: decoder) }
}

enum HotbarKeys {
    static func selection(_ slot:Int,in inventory:HotbarSnapshot,reserved:Set<UInt16>) -> UInt16? {
        guard inventory.valid,(0..<9).contains(slot),
              !inventory.blockedKeys.contains(inventory.keys[slot]),
              inventory.keys.filter({$0==inventory.keys[slot]}).count==1,
              let key=native(inventory.keys[slot]), !reserved.contains(key) else {return nil}
        return key
    }
    static func native(_ lwjgl: Int) -> UInt16? {
        let map: [Int: UInt16] = [2:18,3:19,4:20,5:21,6:23,7:22,8:26,9:28,10:25,
            16:12,17:13,18:14,19:15,20:17,21:16,22:32,23:34,24:31,25:35,
            30:0,31:1,32:2,33:3,34:5,35:4,36:38,37:40,38:37,
            44:6,45:7,46:8,47:9,48:11,49:45,50:46]
        return map[lwjgl]
    }
}

enum AutoToolPolicy {
    static func choose(_ inventory: HotbarSnapshot) -> HotbarItem? {
        guard inventory.valid, inventory.hitKind == "block", inventory.target?.count == 3,
              let block = inventory.blockID, block > 0,
              let hardness = inventory.hardness, hardness >= 0 else { return nil }
        if block == 26 { // User preference, not a claim that swords mine beds faster.
            if inventory.current?.kind == "sword" { return nil }
            return inventory.slots.first { $0.kind == "sword" }
        }
        guard hardness > 0 else { return nil } // Instant-break blocks need no tool swap.
        let baseline = inventory.current?.score ?? 1
        return inventory.slots.filter { $0.kind == "tool" || $0.kind == "sword" }
            .filter { $0.slot != inventory.selected && $0.score > baseline + 0.0001 }
            .sorted { abs($0.score-$1.score) > 0.0001 ? $0.score > $1.score : $0.slot < $1.slot }
            .first
    }
}

struct AutoToolPress {
    private var began: Double?
    private var world: Int?
    private var target: [Int]?
    mutating func cancel() { began = nil; world = nil; target = nil }
    mutating func begin(now: Double, world: Int, inventory: HotbarSnapshot) {
        cancel()
        guard inventory.valid, inventory.hitKind == "block", inventory.target?.count == 3 else { return }
        began = now; self.world = world; target = inventory.target
    }
    // One decision per genuine down edge, confirmed by a newer game observation.
    mutating func update(now: Double, sampledAt: Double, world: Int, inventory: HotbarSnapshot,
                         enabled: Bool, clicking: Bool, bridging: Bool, physicalDown: Bool) -> HotbarItem? {
        guard let began else { return nil }
        guard enabled, !clicking, !bridging, physicalDown, self.world == world,
              now >= began, now-began <= 0.18, now-sampledAt >= 0, now-sampledAt <= 0.10,
              inventory.valid, inventory.hitKind == "block", inventory.target == target else { cancel(); return nil }
        guard sampledAt > began else { return nil }
        defer { cancel() }
        return AutoToolPolicy.choose(inventory)
    }
}

enum BridgeSupplyDecision: Equatable {
    case ready, select(Int), insufficient, invalid
}

struct BridgeSupplyPolicy {
    // Reserve a whole jump before leaving support; do not switch stacks in midair.
    static let reserve = 6
    private(set) var identity: String?
    mutating func reset() { identity = nil }
    mutating func evaluate(_ inventory: HotbarSnapshot, grounded: Bool, selectable:Set<Int> = Set(0..<9)) -> BridgeSupplyDecision {
        guard inventory.valid, let current = inventory.current, current.kind == "block", current.fullBlock else { return .invalid }
        if identity == nil { identity = current.identity }
        guard let identity, inventory.matches(current, identity: identity) else { return .invalid }
        guard grounded else { return .ready }
        if current.count >= Self.reserve { return .ready }
        if let replacement = inventory.slots.filter({
            $0.slot != inventory.selected && selectable.contains($0.slot) && inventory.matches($0, identity: identity) && $0.count >= Self.reserve
        }).max(by: { $0.count < $1.count }) { return .select(replacement.slot) }
        return .insufficient
    }
    func beforePlacement(_ inventory:HotbarSnapshot,selectable:Set<Int> = Set(0..<9)) -> BridgeSupplyDecision {
        guard inventory.valid,let identity,let current=inventory.current,
              inventory.matches(current,identity:identity) else{return .invalid}
        if current.count>2 {return .ready}
        if let replacement=inventory.slots.filter({$0.slot != inventory.selected && selectable.contains($0.slot) &&
            inventory.matches($0,identity:identity) && $0.count>current.count}).max(by:{$0.count<$1.count}) {
            return .select(replacement.slot)
        }
        // Keep one block in hand while the flight controller finds/returns to
        // confirmed support. Never trigger its empty-hand stop in midair.
        return current.count>1 ? .ready:.insufficient
    }
}
