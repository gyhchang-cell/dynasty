import Foundation

enum MeleeMainHand:Equatable {
    case sword,axe,empty,other,unknown
    static func classify(_ item:AnchorItem?)->Self {
        guard let item,item.count>=0 else{return .unknown}
        if item.id=="minecraft:air" {return item.count==0 ? .empty:.unknown}
        guard item.count>0 else{return .unknown}
        if item.id.hasSuffix("_sword") {return .sword}
        if item.id.hasSuffix("_axe") {return .axe}
        return .other
    }
    var label:String {
        switch self {case .sword:return "剑";case .axe:return "斧";case .empty:return "空手";case .other:return "其他物品";case .unknown:return "未知物品"}
    }
    var supported:Bool {self == .sword || self == .axe || self == .empty}
}

enum MeleeReadiness {
    static func item(_ s:AnchorState)->AnchorItem? {s.slots.first{$0.slot==s.selected}}
    static func problem(_ s:AnchorState?,now:Double)->String? {
        guard let s else{return "等待游戏数据连接"}
        guard now.isFinite,s.time.isFinite,now>=s.time,now-s.time<=0.10 else{return "游戏读数已过期 · 等待重连"}
        let hand=MeleeMainHand.classify(item(s)),prefix="已识别\(hand.label)"
        guard s.active else{return "\(prefix) · 菜单或失焦暂停"}
        guard hand != .unknown else{return "主手数据无效 · 等待新读数"}
        guard hand.supported else{return "当前为其他物品 · 自动攻击暂停"}
        guard let c=s.combat else{return "\(prefix) · 战斗读数缺失"}
        guard c.attackKey=="key.mouse.left" else{return "\(prefix) · 攻击键需设为鼠标左键"}
        // active already includes the game's mouse-grab/menu checks. mouseReady
        // is !ignoreFirstMove (camera calibration), NOT proof of mouse capture.
        return nil
    }
    static func allowsClicker(_ s:AnchorState?,now:Double,after:Double)->Bool {
        guard problem(s,now:now)==nil,let s,s.time>=after,!s.using,!s.rightDown else{return false}
        return MeleeMainHand.classify(item(s)) == .sword
    }
}

struct SwordTarget:Decodable {
    let id:Int,distance:Double,range:Double,valid:Bool,hurtTime:Int,ground:Bool,blocking:Bool
    var reachable:Bool {valid && distance.isFinite && range.isFinite && distance>=0 && distance<range-0.015}
}
struct SwordObservation:Decodable {
    let cooldown:Double,delayTicks:Double,attackKey:String,jumpKey:String,forwardKey:String
    let jumpDown:Bool,forwardDown:Bool,jumpUsable:Bool,forwardUsable:Bool,hurtTime:Int,fallDistance:Double,critEnvironment:Bool,attacker:Int,safeJump:Bool
    let target:SwordTarget?
    let movementKeys:[String]?
    let critTicks:Int?
    let canDisableShield:Bool?
    static func parse(_ value:Any?)->SwordObservation? {
        guard let value,JSONSerialization.isValidJSONObject(value),let data=try? JSONSerialization.data(withJSONObject:value),
              let s=try? JSONDecoder().decode(Self.self,from:data),s.cooldown.isFinite,(0...1).contains(s.cooldown),
              s.delayTicks.isFinite,(1...200).contains(s.delayTicks),s.fallDistance.isFinite else{return nil}
        return s
    }
}

// The physical backslash key and the UI control share one session switch.
// Input repeats never toggle twice; menu typing stays native. Fresh gameplay
// observations can resume after a menu/slot transition without another click.
struct SwordSwitch {
    private(set) var enabled=false,keyHeld=false
    private(set) var resumeAfter = -Double.infinity
    mutating func setEnabled(_ value:Bool,now:Double) {enabled=value;resumeAfter=now}
    mutating func pause(now:Double) {resumeAfter=max(resumeAfter,now+0.075)}
    mutating func key(down:Bool,repeated:Bool,gameplay:Bool,modified:Bool,now:Double)->Bool {
        if !down {let consumed=keyHeld;keyHeld=false;return consumed}
        if keyHeld {return true}
        guard gameplay,!modified else{return false}
        keyHeld=true
        if !repeated {setEnabled(!enabled,now:now)}
        return true
    }
    func canRun(_ s:AnchorState?,now:Double,allowed:Bool)->Bool {
        enabled && allowed && s.map{$0.time>resumeAfter}==true && SwordController.eligible(s,now:now)
    }
}

// No target acquisition, camera writes, or game-state writes. The session
// switch owns activation; this controller owns only an eligible combat interval.
final class SwordController {
    static func actionKey(_ raw:String)->UInt16? {
        guard let key=SprintGameConfig.binding(raw),![59,62].contains(key) else{return nil}
        return key // Control is reserved for the app's independent sprint switch.
    }
    var preserveSprint=false
    private(set) var held=false,suppressSprint=false,requiresRearm=false
    private(set) var message="等待剑、斧或空手"
    var click:()->Void={},jump:()->Void={},forward:(Bool)->Void={_ in},release:()->Void={}
    var trace:(String)->Void={_ in}
    private var world=0,slot=0,lastHurt=0,lastJumpTick = -1000,weaponID=""
    private var criticalAt:Double?,criticalTried=false,attackAt:Double?,attackTick=0
    private var forwardSuppressed=false,recoverUntil=0.0,lastSample = -Double.infinity
    private var holdBegan=0.0,apexWaitAt:Double?
    private var decisionTarget:Int?
    private var motionAfter = -Double.infinity
    private var incomingTick = -1000,incomingTarget = -1,resetFlightUntil = -1000
    private var nativeUseSample = -Double.infinity,nativeUseTick = -1
    func noteMotion(_ observed:AnchorState?,now:Double) {
        // Invalidate the sample already available when input arrived. Requiring
        // every sample to be newer than the latest HID event would starve combat
        // with a continuously moving 125/1000-Hz mouse and a slower game frame.
        motionAfter=max(motionAfter,observed?.time ?? now)
    }
    static func supportedItem(_ item:AnchorItem?)->Bool {
        MeleeMainHand.classify(item).supported
    }
    static func eligible(_ s:AnchorState?,now:Double)->Bool {
        MeleeReadiness.problem(s,now:now)==nil
    }
    func begin(_ s:AnchorState,now:Double) {
        guard !held,Self.eligible(s,now:now) else{return}
        if world != s.world {lastJumpTick = -1000}
        held=true;requiresRearm=false;world=s.world;slot=s.selected;lastHurt=s.combat!.hurtTime;lastSample = -Double.infinity
        weaponID=s.slots.first(where:{$0.slot==slot})!.id
        holdBegan=now;criticalTried=false;attackAt=nil;criticalAt=nil;apexWaitAt=nil;recoverUntil=0;message="等待出手"
        incomingTick = -1000;incomingTarget = -1;resetFlightUntil = -1000
        nativeUseSample = -.infinity;nativeUseTick = -1
        decisionTarget=nil
        trace("HOLD world=\(world) slot=\(slot)")
    }
    func cancel(_ reason:String="等待剑、斧或空手") {
        let wasHeld=held;held=false;attackAt=nil;criticalAt=nil;suppressSprint=false;recoverUntil=0
        nativeUseSample = -.infinity;nativeUseTick = -1
        decisionTarget=nil;apexWaitAt=nil
        restoreForward();release();message=reason
        if wasHeld {trace("END "+reason)}
    }
    private func restoreForward() {if forwardSuppressed {forwardSuppressed=false;forward(false)}}
    func tick(_ s:AnchorState?,now:Double,allowed:Bool,aimAfter:Double = -.infinity) {
        guard held else{return}
        guard allowed,let s,s.fresh(now),now-s.time<=0.10,s.world==world,s.selected==slot,
              let c=s.combat,c.attackKey=="key.mouse.left",Self.supportedItem(s.slots.first(where:{$0.slot==slot})),
              s.slots.first(where:{$0.slot==slot})?.id==weaponID else {cancel("等待游戏状态");return}
        // Right-button state does not belong to this controller. Do not release,
        // intercept or rebind it. Actual game item use may consume left clicks;
        // defer only while that observed state lasts and resume automatically.
        if s.using {
            attackAt=nil;criticalAt=nil;criticalTried=false;apexWaitAt=nil;recoverUntil=0
            decisionTarget=nil
            restoreForward();suppressSprint=false
            nativeUseSample=max(nativeUseSample,s.time);nativeUseTick=max(nativeUseTick,s.tick)
            lastSample=max(lastSample,s.time);lastHurt=c.hurtTime
            incomingTick = -1000;incomingTarget = -1;resetFlightUntil = -1000
            message="右键保持原生 · 自动左键待命";return
        }
        if nativeUseTick>=0 {
            guard s.time>nativeUseSample,s.tick>nativeUseTick else {message="等待游戏恢复左键攻击";return}
            nativeUseSample = -.infinity;nativeUseTick = -1
        }
        // Damage timing is independent of our own attack acknowledgement.
        // A fresh incoming hit can arrive in that short interval too.
        let newHurt=c.hurtTime>lastHurt;lastHurt=c.hurtTime
        if s.time>max(aimAfter,motionAfter),let target=c.target,target.reachable {
        if newHurt,c.hurtTime>=9,c.attacker==target.id {
            incomingTick=s.tick;incomingTarget=target.id
        }
        // Only a newly observed close-range hit by this target, while still on
        // supported ground. Never predict a hit merely from an opponent's swing.
        if newHurt,c.hurtTime>=9,c.attacker==target.id,c.safeJump,!c.jumpDown,!s.sneaking,c.forwardDown,s.sprint?.sprinting==true,
           s.ground,c.jumpUsable,s.tick-lastJumpTick>=8,now-holdBegan>0.025,Self.actionKey(c.jumpKey) != nil {
            lastJumpTick=s.tick;resetFlightUntil=s.tick+12;jump();trace("JUMP_RESET tick=\(s.tick) hurt=\(c.hurtTime)")
        }
        // A manual jump close to the received hit belongs to the same defensive
        // exchange. Preserve its forward momentum rather than forcing a crit.
        if s.tick>=incomingTick,s.tick-incomingTick<=2,incomingTarget==target.id,
           c.forwardDown,(c.jumpDown || (!s.ground && s.velocity[1]>0)) {
            resetFlightUntil=max(resetFlightUntil,incomingTick+12)
        }
        }
        if let at=attackAt {
            if now-at>=0.10 {restoreForward();suppressSprint=false}
            // Do not schedule another attack from unchanged pre-click snapshots.
            if s.tick>attackTick,c.cooldown<0.85 {attackAt=nil;recoverUntil=now+0.025;restoreForward();trace("ACK tick=\(s.tick)")}
            else if now-at>0.45 {cancel("攻击未确认 · 重新开启后重试");requiresRearm=true;return}
            else {return}
        }
        if now>=recoverUntil,criticalAt==nil {suppressSprint=false}
        guard s.time>lastSample else{return};lastSample=s.time
        if s.ground {criticalTried=false;apexWaitAt=nil}
        guard s.time>max(aimAfter,motionAfter),let target=c.target,target.reachable else {
            criticalAt=nil;apexWaitAt=nil;decisionTarget=nil
            restoreForward();suppressSprint=false;message="等待准星命中";return
        }
        // Optional movement preparation belongs to one continuous aim episode.
        // A new target must not inherit the old target's W release or apex timer.
        if let previous=decisionTarget,previous != target.id {
            criticalAt=nil;apexWaitAt=nil;restoreForward();suppressSprint=false
            trace("PREP_CANCEL target_changed tick=\(s.tick)")
        }
        decisionTarget=target.id
        let shieldBreak=target.blocking && weaponID.hasSuffix("_axe") && c.canDisableShield==true
        guard !target.blocking || shieldBreak else {
            criticalAt=nil;apexWaitAt=nil;restoreForward();suppressSprint=false;message="等待有效命中";return
        }
        let escaping=target.distance>target.range-0.18
        let recentIncoming=incomingTarget==target.id && s.tick>=incomingTick && s.tick-incomingTick<=2
        if criticalAt != nil && (preserveSprint || escaping || recentIncoming) {
            criticalAt=nil;apexWaitAt=nil;restoreForward();suppressSprint=false
            trace("PREP_CANCEL \(escaping ? "range_edge":"received_hit") tick=\(s.tick)")
        }
        let resetting = !s.ground && s.tick<=resetFlightUntil && target.id==incomingTarget
        let falling = !s.ground && s.velocity[1] < -0.03 && c.fallDistance>0 && c.critEnvironment
        let criticalWindow=falling && (c.critTicks ?? 0)>=(s.sprint?.sprinting==true ? 2:1)
            && (!resetting || s.sprint?.sprinting != true)
        // Vanilla enables strong/critical attacks above .9, not only at 1.0.
        // A falling window can close before full charge. Keep a small margin.
        // Falling alone does not make a critical hit: sprint must actually be
        // off. Failed preparation must not turn into a weak ordinary attack.
        let threshold=criticalWindow && s.sprint?.sprinting==false ? 0.92:(escaping ? 0.94:0.999)
        let ready=c.cooldown+1e-6>=threshold
        // Prefer an already available falling crit, but never stop pursuing an
        // escaping target or keep W released waiting for an impossible crit.
        if !preserveSprint,criticalWindow,!escaping,!recentIncoming,c.cooldown+1e-6>=max(0.75,0.92-1/c.delayTicks),target.hurtTime<=1,
           s.sprint?.sprinting==true,!criticalTried,criticalAt==nil,
           c.forwardDown,c.forwardUsable,Self.actionKey(c.forwardKey) != nil {
            criticalTried=true;criticalAt=now;suppressSprint=true;forwardSuppressed=true;forward(true)
            trace("CRIT_PREP tick=\(s.tick)");return
        }
        if let at=criticalAt {
            if !criticalWindow {criticalAt=nil;restoreForward();suppressSprint=false}
            else {
            if (s.sprint?.sprinting==true || !ready || target.hurtTime>0),now-at<0.10 {return}
            criticalAt=nil
            if !ready || target.hurtTime>0 || s.sprint?.sprinting != false {restoreForward();suppressSprint=false}
            }
        }
        guard target.hurtTime==0 else {message="等待有效命中";return}
        guard ready else {message="攻击恢复中";return}
        // Preserve the player's jump: near the apex, wait at most two game ticks
        // for descent when there is room. No mandatory jump or fixed combo loop.
        if !resetting,!recentIncoming,!s.ground,c.critEnvironment,s.velocity[1]>0,s.velocity[1]<0.12,!escaping,target.ground,now-holdBegan>0.05 {
            if apexWaitAt==nil {apexWaitAt=now}
            if now-(apexWaitAt ?? now)<0.10 {message="等待下落窗口";return}
        }
        apexWaitAt=nil
        click();attackAt=now;attackTick=s.tick;message="出手"
        trace(String(format:"ATTACK tick=%d target=%d cooldown=%.3f distance=%.3f criticalWindow=%@ sprint=%@ shieldBreak=%@ resetFlight=%@",s.tick,target.id,c.cooldown,target.distance,String(criticalWindow && s.sprint?.sprinting==false),String(s.sprint?.sprinting==true),String(shieldBreak),String(resetting)))
    }
}
