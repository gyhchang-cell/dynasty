import Foundation

struct F3Block: Hashable { let x: Int; let y: Int; let z: Int }

struct F3Pose {
    let x: Double
    let y: Double
    let z: Double
    let yaw: Double
    let pitch: Double
    let time: TimeInterval // Capture start, not OCR completion.
    var looking: F3Block? = nil

    static func parse(_ text: String, time: TimeInterval) -> F3Pose? {
        let text = text.replacingOccurrences(of: "−", with: "-").replacingOccurrences(of: "，", with: ",")
        let lower = text.lowercased()
        guard !["you died", "respawn", "game menu", "back to game", "返回游戏", "重新生成", "你死了"].contains(where: lower.contains) else { return nil }
        let number = #"(-?\d{1,9}(?:[.,]\d{1,6})?)"#
        func values(_ pattern: String) -> [Double]? {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]),
                  let match = regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)) else { return nil }
            var result: [Double] = []
            for i in 1..<match.numberOfRanges {
                guard let range = Range(match.range(at: i), in: text),
                      let value = Double(text[range].replacingOccurrences(of: ",", with: ".")), value.isFinite else { return nil }
                result.append(value)
            }
            return result
        }
        guard let xyz = values(#"\bX\s*Y\s*Z\s*:\s*"# + number + #"\s*/\s*"# + number + #"\s*/\s*"# + number),
              let angle = values(#"(?:Facing|朝向)[^\n]*?\(\s*"# + number + #"\s*/\s*"# + number + #"\s*\)"#),
              abs(xyz[0]) <= 30_000_000, (-128...4096).contains(xyz[1]), abs(xyz[2]) <= 30_000_000,
              abs(angle[0]) <= 360, abs(angle[1]) <= 90 else { return nil }
        var pose = F3Pose(x: xyz[0], y: xyz[1], z: xyz[2], yaw: angle[0], pitch: angle[1], time: time)
        if let target = values(#"Looking\s+at\s*:\s*(-?\d{1,8})\s+(-?\d{1,5})\s+(-?\d{1,8})"#),
           abs(target[0]) <= 30_000_000, (-128...4096).contains(target[1]), abs(target[2]) <= 30_000_000 {
            pose.looking = F3Block(x:Int(target[0]),y:Int(target[1]),z:Int(target[2]))
        }
        return pose
    }

    static func angle(_ value: Double) -> Double {
        var value = value.truncatingRemainder(dividingBy: 360)
        if value > 180 { value -= 360 }
        if value < -180 { value += 360 }
        return value
    }
}

struct TellyGameConfig {
    let sensitivity: Double
    let invertY: Bool
    let forward: UInt16
    let left: UInt16
    let right: UInt16
    let back: UInt16
    let sneak: UInt16
    let jump: UInt16
    let sprint: UInt16
    let path: String
    var degreesPerCount: Double { pow(sensitivity * 0.6 + 0.2, 3) * 8 * 0.15 }

    static func gameDirectory(command: String) -> String? {
        let pattern = #"(?:^|\s)--gameDir\s+(.+?)(?=\s+--[a-zA-Z]|$)"#
        guard let regex = try? NSRegularExpression(pattern: pattern),
              let match = regex.firstMatch(in: command, range: NSRange(command.startIndex..., in: command)),
              let range = Range(match.range(at: 1), in: command) else { return nil }
        let raw = String(command[range]).trimmingCharacters(in: .whitespacesAndNewlines)
            .trimmingCharacters(in: CharacterSet(charactersIn: "\"'"))
            .replacingOccurrences(of: #"\ "#, with: " ")
        return raw.hasPrefix("/") ? raw : nil
    }

    static func parse(_ text: String, path: String) -> TellyGameConfig? {
        let pairs = text.split(whereSeparator: \.isNewline).compactMap { line -> (String,String)? in
            let parts = line.split(separator: ":", maxSplits: 1, omittingEmptySubsequences: false)
            return parts.count == 2 ? (String(parts[0]), String(parts[1]).trimmingCharacters(in: .whitespaces)) : nil
        }
        let fields = Dictionary(pairs, uniquingKeysWith: { _, last in last })
        guard let sensitivity = Double(fields["mouseSensitivity"] ?? ""), sensitivity.isFinite, (0...1).contains(sensitivity),
              fields["smoothCamera"] != "true" else { return nil }
        // LWJGL physical key codes to macOS physical key codes; reject unsupported bindings.
        let map: [Int:UInt16] = [16:12,17:13,18:14,19:15,20:17,21:16,22:32,23:34,24:31,25:35,
            30:0,31:1,32:2,33:3,34:5,35:4,36:38,37:40,38:37,44:6,45:7,46:8,47:9,48:11,49:45,50:46,
            57:49,29:59,157:62,42:56,54:60,56:58,184:61]
        func binding(_ name: String) -> UInt16? {
            guard let raw = Int(fields["key_key." + name] ?? "") else { return nil }
            return map[raw]
        }
        guard let forward = binding("forward"), let back = binding("back"), let jump = binding("jump"), let sprint = binding("sprint"),
              ![forward, back, jump, sprint].contains(where:{[15,17].contains($0)}), Set([forward,back,jump,sprint]).count == 4 else { return nil }
        let left=binding("left") ?? 0, right=binding("right") ?? 2, sneak=binding("sneak") ?? 56
        guard ![left,right,sneak].contains(where:{[15,17].contains($0)}), Set([forward,back,left,right,sneak,jump,sprint]).count==7 else{return nil}
        return TellyGameConfig(sensitivity: sensitivity, invertY: fields["invertYMouse"] == "true", forward: forward, left:left, right:right, back: back, sneak:sneak, jump: jump, sprint: sprint, path: path)
    }
}

struct F3Track {
    private(set) var latest: F3Pose?
    private(set) var stable = 0
    mutating func accept(_ pose: F3Pose, now: TimeInterval) -> Bool {
        guard now - pose.time >= 0, now - pose.time < 0.25 else { return false }
        if let previous = latest {
            let dt = pose.time - previous.time
            guard dt > 0, hypot(pose.x - previous.x, pose.z - previous.z) <= max(0.7, (dt+0.05) * 12), abs(pose.y - previous.y) <= max(0.5, dt * 14) else {
                latest = nil; stable = 0; return false
            }
            stable = abs(pose.y - previous.y) < 0.015 && hypot(pose.x - previous.x, pose.z - previous.z) < 0.025 ? stable + 1 : 0
        }
        latest = pose
        return true
    }
    func fresh(now: TimeInterval) -> F3Pose? {
        guard let latest, now - latest.time <= 0.25 else { return nil }
        return latest
    }
}

// A fixed ray through the actual start position. DDA chooses connected grid
// cells for diagonal headings; face points stay inside the chosen face.
struct TellyRoute {
    let x: Double, z: Double, yaw: Double
    var ux: Double { -sin(yaw * .pi/180) }
    var uz: Double { cos(yaw * .pi/180) }
    func along(_ bx: Double, _ bz: Double) -> Double { (bx-x)*ux+(bz-z)*uz }
    func cross(_ bx: Double, _ bz: Double) -> Double { (bx-x)*uz-(bz-z)*ux }
    func runway(on block:F3Block) -> ClosedRange<Double>? {
        var entry = -Double.infinity, exit = Double.infinity
        for (origin,direction,lower) in [(x,ux,Double(block.x)),(z,uz,Double(block.z))] {
            if abs(direction)<1e-8 {
                guard origin>=lower-0.20 && origin<=lower+1.20 else {return nil}
            } else {
                let a=(lower-origin)/direction,b=(lower+1-origin)/direction
                entry=max(entry,min(a,b));exit=min(exit,max(a,b))
            }
        }
        guard entry.isFinite,exit.isFinite,exit-entry>0.45 else {return nil}
        return entry...exit
    }
    func next(after block: F3Block) -> TellyPlacement {
        let tx = abs(ux)<1e-8 ? Double.infinity : (Double(block.x)+(ux>0 ? 1:0)-x)/ux
        let tz = abs(uz)<1e-8 ? Double.infinity : (Double(block.z)+(uz>0 ? 1:0)-z)/uz
        if tx <= tz {
            let direction = ux>0 ? 1 : -1
            return TellyPlacement(support:block,result:F3Block(x:block.x+direction,y:block.y,z:block.z),axis:0,sign:direction,
                x:Double(block.x)+(direction>0 ? 1:0),y:Double(block.y)+0.65,
                z:max(Double(block.z)+0.12,min(Double(block.z)+0.88,z+uz*tx)))
        }
        let direction = uz>0 ? 1 : -1
        return TellyPlacement(support:block,result:F3Block(x:block.x,y:block.y,z:block.z+direction),axis:2,sign:direction,
            x:max(Double(block.x)+0.12,min(Double(block.x)+0.88,x+ux*tz)),y:Double(block.y)+0.65,
            z:Double(block.z)+(direction>0 ? 1:0))
    }
    func candidates(after block:F3Block)->[TellyPlacement] {
        let preferred=next(after:block)
        var choices=[preferred]
        let axis=preferred.axis==0 ? 2:0,component=axis==0 ? ux:uz
        guard abs(component)>0.001 else{return choices}
        let sign=component>0 ? 1:-1
        let result=F3Block(x:block.x+(axis==0 ? sign:0),y:block.y,z:block.z+(axis==2 ? sign:0))
        guard abs(cross(Double(result.x)+0.5,Double(result.z)+0.5))<=0.9 else{return choices}
        choices.append(TellyPlacement(support:block,result:result,axis:axis,sign:sign,
            x:Double(block.x)+(axis==0 ? (sign>0 ? 1:0):0.5),y:Double(block.y)+0.65,
            z:Double(block.z)+(axis==2 ? (sign>0 ? 1:0):0.5)))
        return choices
    }
    func exposedCandidates(after block:F3Block,from pose:F3Pose)->[TellyPlacement] {
        // A small deviation from a cardinal heading adds a lateral DDA
        // candidate. That face cannot be targeted from inside its half-space,
        // even when its apparent yaw requires a shorter camera turn.
        candidates(after:block).filter { $0.isExposed(from:pose) }
    }
    func frontSupport(from block:F3Block,solid:Set<F3Block>)->F3Block {
        var front=block
        for _ in 0..<16 {
            let next=next(after:front).result
            guard solid.contains(next) else {break}
            front=next
        }
        return front
    }
}
struct TellyPlacement {
    let support: F3Block, result: F3Block
    let axis: Int, sign: Int
    let x: Double, y: Double, z: Double
    func isExposed(from pose:F3Pose)->Bool {
        if axis==1 {return pose.y+1.62>y+0.03}
        return ((axis==0 ? pose.x-x:pose.z-z)*Double(sign))>0.03
    }
    func horizontalPoint(from pose:F3Pose,inset:Double=0.01)->(x:Double,z:Double) {
        guard axis != 1 else{return (x,z)}
        let r=pose.yaw * .pi/180,dx = -sin(r),dz=cos(r)
        let component=axis==0 ? dx:dz
        let t=abs(component)>0.001 ? ((axis==0 ? x-pose.x:z-pose.z)/component) : -1
        let px=t>0 ? pose.x+dx*t:pose.x,pz=t>0 ? pose.z+dz*t:pose.z
        return (axis==0 ? x:max(Double(support.x)+inset,min(Double(support.x)+1-inset,px)),
                axis==2 ? z:max(Double(support.z)+inset,min(Double(support.z)+1-inset,pz)))
    }
    // A use-item click recalculates the ray at logical position (partial=1).
    // Rendering uses an interpolated eye position; those rays need not agree.
    func isVisibleFace(from pose: F3Pose, eyeHeight:Double=1.62) -> Bool {
        guard let hit=BridgeRay.intersection(block:support,pose:pose,eyeHeight:eyeHeight) else{return false}
        return hit.axis==axis && hit.sign==sign
    }
}
struct BridgeRay {
    struct Hit { let block:F3Block;let axis:Int;let sign:Int;let distance:Double }
    static func intersection(block:F3Block,pose:F3Pose,eyeHeight:Double=1.62) -> Hit? {
        let yaw=pose.yaw * .pi/180, pitch=pose.pitch * .pi/180
        let origin=[pose.x,pose.y+eyeHeight,pose.z]
        let ray=[-sin(yaw)*cos(pitch),-sin(pitch),cos(yaw)*cos(pitch)]
        let lower=[Double(block.x),Double(block.y),Double(block.z)]
        var enter = -Double.infinity, leave = Double.infinity, faceAxis = -1, faceSign = 0
        for i in 0..<3 {
            if abs(ray[i]) < 1e-9 {
                if origin[i]<lower[i] || origin[i]>lower[i]+1 { return nil }
                continue
            }
            let a=(lower[i]-origin[i])/ray[i], b=(lower[i]+1-origin[i])/ray[i]
            let near=min(a,b), far=max(a,b)
            if near>enter { enter=near; faceAxis=i; faceSign=ray[i]>0 ? -1:1 }
            leave=min(leave,far)
        }
        guard enter>=0,enter<=leave,enter<4.5 else{return nil}
        return Hit(block:block,axis:faceAxis,sign:faceSign,distance:enter)
    }
    static func first(in blocks:Set<F3Block>,pose:F3Pose)->Hit? {
        blocks.compactMap{intersection(block:$0,pose:pose)}.min{$0.distance<$1.distance}
    }
}
