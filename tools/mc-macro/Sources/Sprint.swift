import Foundation

// Sprint uses the current instance's binding, independently of inventory or
// the 1.8.9 telemetry mappings. Never infer a binding from a different instance.
struct SprintGameConfig: Equatable {
    var rawKey:String?=nil
    let key: UInt16?
    let modern: Bool
    let toggle: Bool
    let menuKeys: Set<UInt16>

    var usable: Bool { key != nil && !toggle }
    var keyTitle: String {
        guard let key else { return "未识别键位" }
        return [59:"Control",62:"右 Control",56:"Shift",60:"右 Shift",58:"Option",61:"右 Option",15:"R" ][key]
            ?? Self.letters.first(where:{$0.value==key})?.key.uppercased() ?? "键 \(key)"
    }
    static let letters: [String:UInt16] = ["a":0,"s":1,"d":2,"f":3,"h":4,"g":5,"z":6,"x":7,"c":8,"v":9,"b":11,"q":12,"w":13,"e":14,"r":15,"y":16,"t":17,"o":31,"u":32,"i":34,"p":35,"l":37,"j":38,"k":40,"n":45,"m":46]
    static func binding(_ raw: String?) -> UInt16? {
        guard let raw else { return nil }
        if raw.hasPrefix("key.keyboard.") {
            let name=String(raw.dropFirst("key.keyboard.".count))
            if let key=letters[name] {return key}
            let named: [String:UInt16] = ["left.control":59,"right.control":62,"left.shift":56,"right.shift":60,
                "left.alt":58,"right.alt":61,"space":49,"tab":48,"escape":53,"enter":36,"slash":44,
                "grave.accent":50,"0":29,"1":18,"2":19,"3":20,"4":21,"5":23,"6":22,"7":26,"8":28,"9":25,
                "f1":122,"f2":120,"f3":99,"f4":118,"f5":96,"f6":97,"f7":98,"f8":100,"f9":101,"f10":109,"f11":103,"f12":111]
            return named[name]
        }
        guard let code=Int(raw) else {return nil}
        let legacy: [Int:UInt16] = [16:12,17:13,18:14,19:15,20:17,21:16,22:32,23:34,24:31,25:35,
            30:0,31:1,32:2,33:3,34:5,35:4,36:38,37:40,38:37,44:6,45:7,46:8,47:9,48:11,49:45,50:46,
            57:49,29:59,157:62,42:56,54:60,56:58,184:61,1:53,15:48,28:36,53:44,
            2:18,3:19,4:20,5:21,6:23,7:22,8:26,9:28,10:25,11:29]
        return legacy[code]
    }
    static func parse(_ text: String) -> SprintGameConfig {
        let pairs=text.split(whereSeparator:\.isNewline).compactMap {line -> (String,String)? in
            let parts=line.split(separator:":",maxSplits:1,omittingEmptySubsequences:false)
            return parts.count==2 ? (String(parts[0]),String(parts[1]).trimmingCharacters(in:.whitespaces)):nil
        }
        let fields=Dictionary(pairs,uniquingKeysWith:{_,last in last})
        let menus=Set([UInt16(53)]+["inventory","chat","command"].compactMap{binding(fields["key_key."+$0])})
        let key=binding(fields["key_key.sprint"])
        return SprintGameConfig(rawKey:fields["key_key.sprint"],key:key.flatMap{menus.contains($0) ? nil:$0},
            modern:fields.contains{$0.key.hasPrefix("key_key.") && $0.value.hasPrefix("key.")},
            toggle:fields["toggleSprint"]=="true",menuKeys:menus)
    }
}

// The pointer is captured during modern Minecraft gameplay and visible in
// menus. Require a stable capture before resuming after menu/focus changes.
// No held item or mouse-button state participates in this decision.
struct SprintContext {
    private var capturedSince: Double?
    private var resumeAfter=0.0
    mutating func pause(now: Double) { capturedSince=nil;resumeAfter=now+0.15 }
    mutating func allows(enabled: Bool, focused: Bool, captured: Bool, blocked: Bool, now: Double) -> Bool {
        guard enabled,focused,captured,!blocked else {capturedSince=nil;return false}
        if capturedSince==nil {capturedSince=now}
        return now>=resumeAfter && now-(capturedSince ?? now)>=0.08
    }
}

struct SprintObservation {
    let time:Double,world:Int,key:String,toggle:Bool,down:Bool,sprinting:Bool
    static func parse(_ d:[String:Any],time:Double,world:Int)->SprintObservation? {
        guard let key=d["sprintKey"] as? String,let toggle=d["toggleSprint"] as? Bool,
              let down=d["sprintKeyDown"] as? Bool,let running=d["sprinting"] as? Bool else{return nil}
        return SprintObservation(time:time,world:world,key:key,toggle:toggle,down:down,sprinting:running)
    }
}

final class ForceSprintController {
    var key:(UInt16,Bool)->Void={_,_ in}
    var trace:(String)->Void={_ in}
    private(set) var message="待命"
    private(set) var ownedKey:UInt16?
    private(set) var managesToggle=false
    private var binding:String?,toggle:Bool?,world:Int?
    private var pulse:(desired:Bool,at:Double)?
    private var lastPress = -Double.infinity
    var needsObservation:Bool {managesToggle || ownedKey != nil || pulse != nil}
    func pause() {release();pulse=nil;binding=nil;toggle=nil;world=nil;lastPress = -Double.infinity;message="已暂停"}
    private func release() {if let code=ownedKey {key(code,false);ownedKey=nil}}
    func tick(_ s:SprintObservation?,now:Double,enabled:Bool,allowed:Bool,physicalDown:Bool=false) {
        guard allowed,let s,now>=s.time,now-s.time<0.15,
              let code=SprintGameConfig.binding(s.key),![53,36,48,50].contains(code) else {pause();return}
        if binding != s.key || toggle != s.toggle || world != s.world {
            release();pulse=nil;lastPress = -Double.infinity
            binding=s.key;toggle=s.toggle;world=s.world
        }
        if s.toggle {
            if enabled {managesToggle=true}
            guard enabled || managesToggle else {message="已关闭";return}
            if let p=pulse {
                if now-p.at>=0.025 {release()}
                if ownedKey==nil,s.time>p.at,s.down==p.desired {pulse=nil}
                else if now-p.at<0.4 {return}
                else {release();pulse=nil}
            }
            if s.down != enabled {
                guard !physicalDown,now-lastPress>=0.15 else{return}
                // Reset native key ownership before each isolated toggle press.
                key(code,false);key(code,true);ownedKey=code
                pulse=(enabled,now);lastPress=now;trace("TOGGLE \(enabled)")
            } else if !enabled {managesToggle=false}
        } else {
            managesToggle=false;pulse=nil
            guard enabled else{release();message="已关闭";return}
            if ownedKey==nil {
                guard !physicalDown else{return}
                key(code,false);key(code,true);ownedKey=code;lastPress=now;trace("HOLD \(code)")
            } else if !s.down,s.time>lastPress,now-lastPress>=0.10 {
                key(code,false);key(code,true);lastPress=now;trace("RESTORE \(code)")
            }
        }
        message=enabled ? (s.sprinting ? "疾跑中":(s.down ? "已开启":"正在恢复")):"已关闭"
    }
}
