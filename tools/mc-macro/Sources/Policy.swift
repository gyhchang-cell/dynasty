import Foundation

enum MacroMouseButton: CaseIterable { case left, right }

struct MacroPolicy {
    var enabled = false
    var physicalLeftHeld = false
    var physicalRightHeld = false
    var targetActive = false
    var mayClick: Bool { enabled && targetActive && physicalLeftHeld }
    func mayClick(_ button: MacroMouseButton) -> Bool {
        enabled && targetActive && (button == .left ? physicalLeftHeld : physicalRightHeld)
    }
    func mayClick(_ button: MacroMouseButton, hardwareDown: Bool) -> Bool {
        hardwareDown && mayClick(button)
    }

    mutating func stop() {
        enabled = false
        physicalLeftHeld = false
        physicalRightHeld = false
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
