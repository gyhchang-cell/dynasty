import Foundation

// Experimental native-input controller with read-only vanilla state or F3 fallback.
// Never substitute a timer loop for missing observations.
final class TellyController {
    enum Phase { case idle, preparing, calibrating, probing, aligning, centering, backing, runup, takeoff, flight, landing, blocked }
    private var blockedReason = ""
    private(set) var held = false
    private(set) var finishing = false
    var active: Bool {held || finishing}
    private var finishAt = 0.0
    private(set) var phase = Phase.idle
    private(set) var message = "按住 R 搭路；松开后完成本跳、落地回正再停。"
    private(set) var track = F3Track()
    var key: (UInt16, Bool) -> Void = { _,_ in }
    var mouse: (Bool) -> Void = { _ in }
    var move: (Int64, Int64) -> Void = { _,_ in }
    var cancelPendingInput: () -> Void = {}
    var trace:(String)->Void = {_ in}
    var config: TellyGameConfig?
    private var ownedKeys = Set<UInt16>()
    private var mouseDown = false
    private var clickTimer: Timer?
    private var releaseTimer: Timer?
    private var placing = false
    private var minimumCPS = 15.0
    private var maximumCPS = 20.0
    private var rhythm = ClickRhythm()
    private var random = SystemRandomNumberGenerator()
    private var startedAt = 0.0
    private var phaseAt = 0.0
    private var anchor: F3Pose?
    private var heading = 0.0
    private var gainX = 0.0
    private var gainY = 0.0
    private var calibratedSensitivity = 0.0
    private var calibrationPose: F3Pose?
    private var calibrationSentAt = 0.0
    private var lastAimAt = 0.0
    private var lastUsedPose = -1.0
    private var airborne = false
    private var turn: RelativeMouseTurn?
    private var follower: RelativeMouseFollower?
    private var turnEndedAt = 0.0
    private var pendingAimPose: F3Pose?
    private var pendingAimSince=0.0
    private var expectedYaw=0.0, expectedPitch=0.0
    private var issuedTurnYaw=0.0, issuedTurnPitch=0.0
    private var turnOriginYaw=0.0,turnOriginPitch=0.0
    private var pendingPlacements = [(TellyPlacement,Double)]()
    private var poseHistory = [F3Pose]()
    private var vx = 0.0, vy = 0.0, vz = 0.0
    private var support: F3Block?
    private var observed = Set<F3Block>()
    private var route: TellyRoute?
    private var groundY = 0.0
    private var flightFloor = 0
    private var placement: TellyPlacement?
    private var probeCandidates = [F3Block]()
    private var probeIndex = 0
    private var probeAt = 0.0
    private var lastPlacementAt = 0.0
    private var launchAt = 0.0
    private var lastGateTick = -1
    private var lastClickTick = -1
    private var jumpPlacements = 0
    private var activeRise=0
    private var plannedRise=0
    private var jumpIndex=0
    private var launched=false
    private var runwayStart=0.0, runwayEnd=0.0, backingSign=0.0
    var prepareRunup=true
    private var worldState: BridgeWorldState?
    var forwardPitch = 0.0
    var risePerJump = 0
    var coordinateMovement = false
    private var centered=false
    private var centerSettling=false
    private var landingCoast=false
    private var flightCoast=false
    static func openingHeading(_ yaw:Double)->Double {
        let normalized=F3Pose.angle(yaw)
        let cardinal=F3Pose.angle((normalized/90).rounded()*90)
        return abs(F3Pose.angle(normalized-cardinal))<=5 ? cardinal:normalized
    }
    var diagnostic:String {
        let forecast=worldState.flatMap{BridgeLandingForecast.predict($0,height:Double(flightFloor+1),yaw:heading)}
        return "phase=\(phase) count=\(jumpPlacements) support=\(String(describing:support)) pending=\(pendingPlacements.map{$0.0.result}) landing=\(String(describing:forecast))"
    }

    func observeWorld(_ state: BridgeWorldState?, error: String, now: Double) {
        guard let state else { observe(nil,error:error,now:now); return }
        if let previous=worldState, previous.world != state.world { stop("世界已切换，已释放搭路输入。"); return }
        guard !state.flying, state.hasBlocks else { stop("请关闭飞行并手持完整方块。"); return }
        observe(state.pose,error:error,now:now)
        worldState=state
        vx=state.velocity.0*20;vy=state.velocity.1*20;vz=state.velocity.2*20
        observed.formUnion(state.solid)
    }
    private func canPlace(_ target: TellyPlacement, pose: F3Pose) -> Bool {
        if let state=worldState {
            let b=target.result
            let occupied=pose.x+0.30>Double(b.x) && pose.x-0.30<Double(b.x)+1 && pose.z+0.30>Double(b.z) && pose.z-0.30<Double(b.z)+1 && pose.y<Double(b.y)+1 && pose.y+1.8>Double(b.y)
            guard !occupied,state.solid.contains(target.support), !state.solid.contains(target.result) else{return false}
            // During ascent the integrated server may still have the previous
            // tick's lower body position. Do not click a new top block at the
            // first 1.001-height frame, where placement is still obstructed.
            if target.axis==1,state.velocity.1>0,pose.y<Double(b.y)+1.12 {return false}
            let turning=turn != nil || pendingAimPose != nil
            let commanded=F3Pose(x:pose.x,y:pose.y,z:pose.z,yaw:turning ? issuedTurnYaw : follower?.yaw ?? pose.yaw,pitch:turning ? issuedTurnPitch : follower?.pitch ?? pose.pitch,time:pose.time)
            let face=target.axis==1 ? "up" : target.axis==0 ? (target.sign>0 ? "east":"west") : (target.sign>0 ? "south":"north")
            let next=F3Pose(x:pose.x+state.velocity.0,y:pose.y+(state.onGround ? 0:state.velocity.1),z:pose.z+state.velocity.2,yaw:commanded.yaw,pitch:commanded.pitch,time:pose.time+0.05)
            let observedHit=state.useHit==target.support && state.useFace?.lowercased()==face
            let currentHit=target.isVisibleFace(from:pose,eyeHeight:state.eyeHeight)
            let commandHit=target.isVisibleFace(from:commanded,eyeHeight:state.eyeHeight)
            let nextHit=target.axis != 1 || target.isVisibleFace(from:next,eyeHeight:state.eyeHeight)
            if ProcessInfo.processInfo.environment["MC_MACRO_GATE_TRACE"]=="1",lastGateTick != state.tick {
                lastGateTick=state.tick
                trace("GATE tick=\(state.tick) face=\(face) observed=\(observedHit) current=\(currentHit) command=\(commandHit) next=\(nextHit) view=\(commanded.yaw),\(commanded.pitch) target=\(target.result)")
            }
            return observedHit && currentHit && commandHit && nextHit
        }
        return pose.looking==target.support && target.isVisibleFace(from:pose)
    }

    func press(now: TimeInterval) {
        guard !held else { return }
        if finishing {held=true;finishing=false;message="R 搭路中；松开后完成本跳并回正。";return}
        held = true; phase = .preparing; startedAt = now; phaseAt = now;plannedRise=0
        track = F3Track(); worldState=nil;lastClickTick = -1;jumpIndex=0;centered=false;centerSettling=false; anchor = nil; lastUsedPose = -1; launched=false
        support = nil; route = nil; placement = nil; pendingPlacements.removeAll(); observed.removeAll(); pendingAimPose = nil; poseHistory.removeAll(); vx = 0; vy = 0; vz = 0
        message = "正在读取角色状态；站在完整方块上，朝搭桥方向，保持 R。"
    }

    func release(now:TimeInterval=ProcessInfo.processInfo.systemUptime) {
        guard held else{return}
        held=false
        if phase == .idle {return}
        if phase == .blocked {finishing=true;finishAt=now;return}
        if launched,worldState?.onGround == true,phase == .runup {
            // Repeated flat spans include a short grounded approach. Keep
            // edge protection while braking instead of releasing into drift.
            finishing=true;finishAt=now;phase = .landing;phaseAt=now
            if let config {keys([config.sneak])}
            message="R 已松开，正在落地回正并停稳。"
            return
        }
        if launched,worldState != nil,[Phase.takeoff,.flight,.landing].contains(phase) {
            finishing=true;finishAt=now
            message="R 已松开，正在完成本跳、落地并回正。"
        } else {stop("已停止搭路：R 已松开。")}
    }

    func stop(_ reason: String) {
        finishing=false
        phase = .idle
        turn=nil; follower=nil; pendingAimPose=nil; cancelPendingInput()
        for code in ownedKeys { key(code, false) }
        ownedKeys.removeAll()
        setPlacing(false)
        releaseTimer?.invalidate(); releaseTimer=nil
        if mouseDown { mouse(false); mouseDown=false }
        message = reason
    }

    func observe(_ pose: F3Pose?, error: String, now: TimeInterval) {
        guard active, phase != .idle else { return }
        guard let pose else {
            if phase != .preparing { stop(error.isEmpty ? "游戏读数失效，已停止；松开 R 后重新开始。" : error) }
            else if !error.isEmpty { message = error }
            return
        }
        if let old=poseHistory.last, abs(pose.x-old.x)+abs(pose.y-old.y)+abs(pose.z-old.z)>0.001 {
            let dt=max(0.05,(min(0.20,pose.time-old.time)/0.05).rounded()*0.05)
            vx=(pose.x-old.x)/dt;vy=(pose.y-old.y)/dt;vz=(pose.z-old.z)/dt
            poseHistory=[pose]
        } else if poseHistory.isEmpty { poseHistory=[pose] }
        else if let old=poseHistory.last,pose.time-old.time>0.15 {vx=0;vy=0;vz=0;poseHistory=[pose]}

        if !track.accept(pose, now: now), phase != .preparing {
            stop("读数超时或坐标突变，已停止；松开 R 后重新开始。")
        }
    }

    private func keys(_ desired: Set<UInt16>) {
        for code in ownedKeys.subtracting(desired) { key(code, false) }
        // Establish modifiers before movement, and jump after both.
        let additions=desired.subtracting(ownedKeys).sorted {
            func rank(_ c:UInt16)->Int {if c==config?.jump {return 2};return [56,58,59,60,61,62].contains(c) ? 0:1}
            return rank($0)==rank($1) ? $0<$1:rank($0)<rank($1)
        }
        for code in additions { key(code, true) }
        ownedKeys = desired
    }

    private func advanceTurn(pose: F3Pose, now: Double) {
        if var active=turn {
            let step=active.advance(now:now)
            turn=step.finished ? nil:active
            if step.x != 0 || step.y != 0 {
                let scale=config!.degreesPerCount/calibratedSensitivity
                issuedTurnYaw=F3Pose.angle(issuedTurnYaw+Double(step.x)*gainX*scale)
                issuedTurnPitch=max(-90,min(90,issuedTurnPitch+Double(step.y)*gainY*scale))
                move(step.x,step.y)
            }
            if step.finished { turnEndedAt=now }
        }
        if turn==nil, let previous=pendingAimPose {
            let moved=abs(F3Pose.angle(pose.yaw-previous.yaw))>0.1 || abs(pose.pitch-previous.pitch)>0.1
            let scale=config!.degreesPerCount/calibratedSensitivity
            let toleranceX=max(0.04,abs(gainX*scale)*0.51),toleranceY=max(0.04,abs(gainY*scale)*0.51)
            // Do not seed the face follower from a nearly complete turn while
            // its final counts are still in flight. That creates a persistent
            // angle offset and can place on the top instead of the side.
            if (moved && pose.time>turnEndedAt && abs(F3Pose.angle(pose.yaw-expectedYaw))<toleranceX && abs(pose.pitch-expectedPitch)<toleranceY) || now-turnEndedAt>0.14 { pendingAimPose=nil }
        }
    }
    private func aim(yaw: Double, pitch: Double, pose: F3Pose, now: TimeInterval, preferredYawSign:Double?=nil) -> Bool {
        guard turn==nil, pendingAimPose==nil, (worldState != nil || !mouseDown) else { return false }
        let baseYaw=follower?.yaw ?? pose.yaw, basePitch=follower?.pitch ?? pose.pitch
        let dyaw=RelativeMouseTurn.yawDelta(from:baseYaw,to:yaw,preferredSign:preferredYawSign), dpitch=pitch-basePitch
        if abs(dyaw)<0.8 && abs(dpitch)<0.8 { return true }
        guard pose.time != lastUsedPose else { return false }
        let scale=config.map{$0.degreesPerCount/calibratedSensitivity} ?? 1
        guard scale.isFinite,scale>0 else { return false }
        let x=Int64((dyaw/(gainX*scale)).rounded()),y=Int64((dpitch/(gainY*scale)).rounded())
        guard abs(x)<=40000,abs(y)<=40000 else {stop("转头校准值异常，已停止。");return false}
        if x != 0 || y != 0 {
            follower=nil
            let span=max(abs(dyaw),abs(dpitch))
            let duration=RelativeMouseTurn.duration(for:span)
            turn=RelativeMouseTurn(x:x,y:y,start:now,duration:duration)
            issuedTurnYaw=baseYaw;issuedTurnPitch=basePitch
            turnOriginYaw=baseYaw;turnOriginPitch=basePitch
            pendingAimPose=pose;pendingAimSince=now;lastAimAt=now;lastUsedPose=pose.time
            expectedYaw=F3Pose.angle(baseYaw+Double(x)*gainX*scale)
            expectedPitch=max(-90,min(90,basePitch+Double(y)*gainY*scale))
        }
        return false
    }
    private func followFace(yaw:Double,pitch:Double,pose:F3Pose,now:Double) {
        guard worldState != nil else {_ = aim(yaw:yaw,pitch:pitch,pose:pose,now:now);return}
        if var active=turn {
            // The player travels during a 112-ms turn. Update its destination
            // on the same curve instead of completing an obsolete aim then
            // spending another game tick correcting it after the turn.
            let scale=config!.degreesPerCount/calibratedSensitivity
            let dx=RelativeMouseTurn.yawDelta(from:turnOriginYaw,to:yaw,preferredSign:-1)
            let x=Int64((dx/(gainX*scale)).rounded()),y=Int64(((pitch-turnOriginPitch)/(gainY*scale)).rounded())
            guard abs(x)<=40000,abs(y)<=40000 else {stop("转向目标异常，已停止。");return}
            active.retarget(x:x,y:y);turn=active
            expectedYaw=F3Pose.angle(turnOriginYaw+Double(active.x)*gainX*scale)
            expectedPitch=max(-90,min(90,turnOriginPitch+Double(active.y)*gainY*scale))
            return
        }
        if let follower,abs(F3Pose.angle(yaw-follower.yaw))>35 {
            _ = aim(yaw:yaw,pitch:pitch,pose:pose,now:now,preferredYawSign:-1);return
        }
        if follower==nil {
            if pendingAimPose != nil {
                // Continue from counts already sent on the ordered input queue.
                // Waiting for the next 20-Hz observation creates a visible
                // pause. Clicks still require the actual observed use ray.
                follower=RelativeMouseFollower(yaw:issuedTurnYaw,pitch:issuedTurnPitch,now:now)
                pendingAimPose=nil
            } else if abs(F3Pose.angle(yaw-pose.yaw))<25 {
                follower=RelativeMouseFollower(yaw:pose.yaw,pitch:pose.pitch,now:now)
            } else {
                _ = aim(yaw:yaw,pitch:pitch,pose:pose,now:now,preferredYawSign:-1);return
            }
        }
        let scale=config!.degreesPerCount/calibratedSensitivity
        let delta=follower!.advance(yaw:yaw,pitch:pitch,now:now,gainX:gainX*scale,gainY:gainY*scale)
        if delta.0 != 0 || delta.1 != 0 {move(delta.0,delta.1)}
    }
    private func forwardKeys(pose: F3Pose, config: TellyGameConfig) -> Set<UInt16> {
        if coordinateMovement, let route {
            let correction=max(-35,min(35,route.cross(pose.x,pose.z)*65+(vx*route.uz-vz*route.ux)*8))
            // Relative motion and these keys share one ordered input queue.
            // Use the angle already issued, not the eventual turn target or
            // an older observed angle. A longer turn must not drain momentum.
            let yaw=(turn != nil || pendingAimPose != nil) ? issuedTurnYaw : follower?.yaw ?? pose.yaw
            return Self.directionKeys(yaw:yaw,heading:heading,correction:correction,config:config)
        }
        guard turn==nil, pendingAimPose==nil else { return [] }
        let difference=abs(F3Pose.angle(pose.yaw-heading))
        if difference<15 { return [config.forward,config.sprint] }
        if difference>165 { return [config.back] }
        return []
    }

    static func directionKeys(yaw:Double,heading:Double,correction:Double=0,config:TellyGameConfig)->Set<UInt16> {
        let difference=F3Pose.angle(yaw-heading-correction),angle=difference * .pi/180
        var desired=Set<UInt16>()
        if cos(angle)>0.383 {desired.insert(config.forward)}
        // Sprint-jump boost follows camera yaw. Never boost sideways during
        // the return just because W is one of two active direction keys.
        if abs(F3Pose.angle(yaw-heading))<12 {desired.insert(config.sprint)}
        if cos(angle)<(-0.383) {desired.insert(config.back)}
        if sin(angle)>0.383 {desired.insert(config.left)}
        if sin(angle)<(-0.383) {desired.insert(config.right)}
        return desired
    }

    func tick(now: TimeInterval, active: Bool, minimum: Double, maximum: Double) {
        guard self.active, phase != .idle else { return }
        guard active else { stop("游戏失去前台或权限不可用，已停止搭路。"); return }
        if finishing,now-finishAt>1.5 {stop("未能及时确认安全落地，已释放输入。");return}
        minimumCPS = minimum; maximumCPS = maximum
        guard let config else {
            if phase != .preparing { stop("游戏配置已失效，已停止输入。"); return }
            if now - startedAt > 5 { stop("无法读取当前游戏的灵敏度／键位配置，已停止。") }
            return
        }
        guard let pose = track.fresh(now: now) else {
            if phase == .preparing {
                if now - startedAt > 8 { stop("未及时读到游戏状态；松开 R 后重新开始。") }
            } else { stop("状态延迟超过 250 毫秒，已停止输入。") }
            return
        }
        advanceTurn(pose:pose,now:now)
        if let anchor {
            let r = heading * .pi / 180
            let cross = (pose.x-anchor.x)*cos(r) + (pose.z-anchor.z)*sin(r)
            if (phase != .centering && abs(cross) > 0.65) || pose.y < groundY - 0.12 || pose.y > groundY + 1.6 {
                stop("已偏离路线或落空，停止搭路。请重新站位。")
                return
            }
        }
        switch phase {
        case .idle: break
        case .blocked:
            keys([config.sneak])
            if let state=worldState,state.onGround,hypot(state.velocity.0,state.velocity.2)<0.002 {
                stop(blockedReason)
            }
        case .preparing:
            guard track.stable >= 2 else { return }
            if let state=worldState, !state.onGround {message="等待人物实际落地；尚未开始移动。";return}
            guard abs(pose.y - pose.y.rounded()) < 0.04 else { stop("起点不是完整方块高度，已停止。"); return }
            if let state=worldState,BridgeClearance.jumpBlocked(state,yaw:pose.yaw,rise:0) {
                blockJump(config:config,now:now);return
            }
            // Correct a small opening error before it crosses a block column.
            // The normal continuous mouse turn performs this once at start.
            heading = Self.openingHeading(pose.yaw)
            groundY = pose.y
            route = TellyRoute(x:pose.x,z:pose.z,yaw:heading)
            // Stationary calibration verifies the actual macOS -> game mouse mapping.
            // It must succeed before a single movement/jump key is pressed.
            anchor = pose; calibrationPose = pose
            let yCount: Int64 = (pose.pitch > 65 ? -20 : 20) * (config.invertY ? -1 : 1)
            calibrationYCount = yCount
            move(32, yCount)
            calibrationSentAt = now; lastAimAt = now
            phase = .calibrating; phaseAt = now
            message = "正在原地校准转头；未开始移动。"
        case .calibrating:
            guard pose.time > calibrationSentAt + 0.02, let reference = calibrationPose else { return }
            let dx = F3Pose.angle(pose.yaw-reference.yaw), dy = pose.pitch-reference.pitch
            if abs(dx) < 0.1 || abs(dy) < 0.1 {
                if now - phaseAt > 1.5 { stop("游戏未正确接收模拟转头，已停止；未开始移动。") }
                else if now-calibrationSentAt > 0.20 {
                    calibrationPose = pose; move(32, calibrationYCount)
                    calibrationSentAt = now; lastAimAt = now
                }
                return
            }
            gainX = dx / 32; gainY = dy / Double(calibrationYCount)
            guard (0.005...5).contains(abs(gainX)), (0.005...5).contains(abs(gainY)) else { stop("鼠标校准失败，已停止。"); return }
            calibratedSensitivity = config.degreesPerCount
            probeCandidates = []
            for bx in Int(floor(pose.x-0.29))...Int(floor(pose.x+0.29)) {
                for bz in Int(floor(pose.z-0.29))...Int(floor(pose.z+0.29)) {
                    probeCandidates.append(F3Block(x:bx,y:Int(groundY.rounded())-1,z:bz))
                }
            }
            probeCandidates.sort { hypot(Double($0.x)+0.5-pose.x,Double($0.z)+0.5-pose.z) < hypot(Double($1.x)+0.5-pose.x,Double($1.z)+0.5-pose.z) }
            probeIndex=0; probeAt=now
            if let state=worldState, let under=probeCandidates.first(where:{state.solid.contains($0)}) {
                support=under;observed.insert(under);phase = .aligning;phaseAt=now
            } else {phase = .probing; phaseAt = now}
            message = "转头校准完成；正在读取起点方块。"
        case .probing:
            keys([])
            guard now - phaseAt < 2 else { stop("未读到 F3 的 Looking at 起点方块，未开始移动。"); return }
            if now-probeAt>0.4 { probeIndex+=1; probeAt=now }
            guard probeIndex<probeCandidates.count else { stop("未确认脚下的完整支撑方块，未开始移动。"); return }
            let candidate=probeCandidates[probeIndex]
            let dx=Double(candidate.x)+0.5-pose.x, dz=Double(candidate.z)+0.5-pose.z
            let yaw=atan2(-dx,dz)*180 / .pi
            let pitch=atan2(pose.y+1.62-Double(candidate.y)-1,hypot(dx,dz))*180 / .pi
            if aim(yaw:yaw,pitch:min(88,pitch),pose:pose,now:now), let target=pose.looking,
               probeCandidates.contains(target) {
                support=target; observed.insert(target)
                phase = .aligning; phaseAt = now
                message = "已读取起点方块；正在对准起跳方向。"
            }
        case .aligning:
            keys([])
            guard now - phaseAt < 1.5 else { stop("无法及时对准起跳方向，已停止。"); return }
            if aim(yaw: heading, pitch: forwardPitch, pose: pose, now: now) {
                guard abs(pose.y - groundY) < 0.06 else { stop("未确认回到起始高度，已停止。"); return }
                if !launched,worldState != nil,!centered {
                    phase = .centering;phaseAt=now;message="正在潜行调整到支撑方块内，保留原朝向。";return
                }
                if !launched && prepareRunup, let route, let support, let runway=route.runway(on:support) {
                    runwayStart=runway.lowerBound+0.20
                    // Corner crossings require two face-connected cells. Begin
                    // the first jump earlier so the launch tick does not carry
                    // both coordinates beyond the starting block's corner.
                    runwayEnd=runway.upperBound+0.23-0.55*2*abs(route.ux*route.uz)
                    let at=route.along(pose.x,pose.z)
                    backingSign=runwayStart>at ? 1:-1
                    key(config.sprint,false)
                    phase = .backing;phaseAt=now
                    keys(backingSign>0 ? [config.forward]:[config.back])
                    message="正在确认范围内调整助跑起点；松开 R 停止。"
                } else { beginJump(config:config,pose:pose,now:now) }
            }
        case .centering:
            guard let support,let state=worldState,state.onGround,state.solid.contains(support),now-phaseAt<2.5 else {stop("起点支撑或站位已变化，停止调整。");return}
            let dx=Double(support.x)+0.5-pose.x,dz=Double(support.z)+0.5-pose.z
            if BridgeClearance.walkingBlocked(state,yaw:atan2(-dx,dz)*180 / .pi) {blockJump(config:config,now:now);return}
            let coastX=pose.x+state.velocity.0/(1-0.546),coastZ=pose.z+state.velocity.2/(1-0.546)
            if abs(coastX-Double(support.x)-0.5)<0.045,abs(coastZ-Double(support.z)-0.5)<0.045 {centerSettling=true}
            if centerSettling {
                keys([config.sneak])
                if hypot(state.velocity.0,state.velocity.2)>0.002 {return}
                if abs(dx)<0.08,abs(dz)<0.08 {
                    keys([]);centered=true;anchor=pose;route=TellyRoute(x:pose.x,z:pose.z,yaw:heading);phase = .aligning;phaseAt=now;return
                }
                centerSettling=false
            }
            let angle=(pose.yaw-atan2(-dx,dz)*180 / .pi) * .pi/180
            var desired:Set<UInt16>=[config.sneak]
            if cos(angle)>0.383 {desired.insert(config.forward)}
            if cos(angle)<(-0.383) {desired.insert(config.back)}
            if sin(angle)>0.383 {desired.insert(config.left)}
            if sin(angle)<(-0.383) {desired.insert(config.right)}
            keys(desired)
        case .backing:
            guard let route else {return}
            if let state=worldState,state.onGround,BridgeClearance.walkingBlocked(state,yaw:heading+(backingSign<0 ? 180:0)) {blockJump(config:config,now:now);return}
            if now-phaseAt>2 {stop("无法完成起步调整，已停止。");return}
            let at=route.along(pose.x,pose.z)
            if (runwayStart-at)*backingSign<=0.06 {
                phase = .runup;phaseAt=now;keys([config.forward,config.sprint])
            } else {keys(backingSign>0 ? [config.forward]:[config.back])}
        case .runup:
            guard let route else {return}
            if let state=worldState,state.onGround,
               BridgeClearance.walkingBlocked(state,yaw:heading) || BridgeClearance.jumpBlocked(state,yaw:heading,rise:jumpIndex==0 ? 0:plannedRise) {
                blockJump(config:config,now:now);return
            }
            if !launched,let state=worldState,let support {
                // A server spawn is a platform, not an isolated test block.
                // Follow its connected bridge-line support to the real edge;
                // jumping from the first cell leaves the usable side hidden
                // until most of the first flight has already elapsed.
                let front=route.frontSupport(from:support,solid:state.solid)
                if let runway=route.runway(on:front) {
                    self.support=front
                    runwayEnd=runway.upperBound+0.23-0.55*2*abs(route.ux*route.uz)
                }
            }
            advanceRunup(config:config,pose:pose,now:now)
            if phase == .runup,now-phaseAt>2 {stop("助跑没有前进，已停止。")}
        case .takeoff:
            let dt = now - phaseAt
            var movement=forwardKeys(pose:pose,config:config)
            if worldState != nil ? !airborne : dt < 0.075 {movement.insert(config.jump)}
            keys(movement)
            if pose.y > groundY + 0.15 { airborne = true }
            if (worldState != nil || dt >= 0.045) && airborne {
                keys([]); phase = .flight; phaseAt = now
            } else {
                if dt>0.35 {stop("没有识别到实际起跳，已停止。")}
                return
            }
            fallthrough
        case .flight:
            keys(finishing ? [config.sneak] : flightCoast ? []:forwardKeys(pose:pose,config:config))
            if let state=worldState {
                while let first=pendingPlacements.first, state.solid.contains(first.0.result) {observed.insert(first.0.result);support=first.0.result;jumpPlacements+=1;pendingPlacements.removeFirst()}
                if let first=pendingPlacements.first,state.tick>lastClickTick,!state.solid.contains(first.0.result),
                   (state.clickDelay==4 && now-first.1>0.08) || (state.clickDelay<3 && now-first.1>=1/maximumCPS) {
                    // Vanilla consumed this right press, but no block appeared.
                    // Re-aim now; holding the stale angle for 160 ms loses the
                    // remaining placement window on a diagonal jump.
                    support=first.0.support;pendingPlacements.removeAll()
                }
            }
            if let target=pose.looking, let index=pendingPlacements.firstIndex(where:{$0.0.result==target}) {
                for entry in pendingPlacements.prefix(index+1) { observed.insert(entry.0.result) }
                pendingPlacements.removeFirst(index+1)
            }
            if let first=pendingPlacements.first, now-first.1>0.16 {
                self.support=first.0.support; pendingPlacements.removeAll()
            }
            guard var support, let route else { stop("缺少已观测的支撑方块，已停止。"); return }
            if let target=pose.looking, (support.y...flightFloor).contains(target.y),
               abs(target.x-support.x)+abs(target.z-support.z)<=2,
               route.along(Double(target.x)+0.5,Double(target.z)+0.5) >= route.along(Double(support.x)+0.5,Double(support.z)+0.5)-0.02,
               abs(route.cross(Double(target.x)+0.5,Double(target.z)+0.5))<1.1 {
                support=target; self.support=target; observed.insert(target)
            }
            let remaining=max(0,0.65-(now-launchAt))
            let ticks=remaining/0.05
            let drift=0.05*0.91*(1-pow(0.91,ticks))/(1-0.91)
            let forecast=worldState.flatMap{BridgeLandingForecast.predict($0,height:Double(flightFloor+1),yaw:heading)}
            // Reserve support after the landing tick's horizontal movement.
            // Y collision alone can report onGround even though that same
            // tick's momentum carries the body completely beyond the block.
            let landX=forecast?.x ?? pose.x+vx*drift, landZ=forecast?.z ?? pose.z+vz*drift
            func covered(_ x:Double,_ z:Double)->F3Block? {
                (worldState?.solid ?? observed).filter{$0.y==flightFloor && x>Double($0.x)-0.22 && x<Double($0.x)+1.22 && z>Double($0.z)-0.22 && z<Double($0.z)+1.22}
                    .max(by:{route.along(Double($0.x)+0.5,Double($0.z)+0.5)<route.along(Double($1.x)+0.5,Double($1.z)+0.5)})
            }
            let drivenLanding=covered(landX,landZ)
            let coastForecast=worldState.flatMap{BridgeLandingForecast.predict($0,height:Double(flightFloor+1),yaw:heading,acceleration:0)}
            let coastLanding=coastForecast.flatMap{covered($0.x,$0.z)}
            if let forecast,forecast.seconds>0 {
                // Include native click consumption, observed confirmation and
                // the return turn; do not accelerate past the last placeable
                // face while waiting for its final click.
                let xs=Int(floor(forecast.supportX-0.28))...Int(floor(forecast.supportX+0.28))
                let zs=Int(floor(forecast.supportZ-0.28))...Int(floor(forecast.supportZ+0.28))
                let cells=xs.flatMap{x in zs.map{z in abs(x-support.x)+abs(z-support.z)+max(0,flightFloor-support.y)}}.min() ?? 0
                // The opening span needs the same confirmation and return
                // budget as every later span. Its old 25-ms exception let the
                // player pass the third block before a fourth was confirmed.
                // Release acceleration in time; never reverse ordinary jumps.
                if forecast.needsCoast(remainingCells:cells,cps:maximumCPS,returnTime:RelativeMouseTurn.maximumDuration) {flightCoast=true;keys(finishing ? [config.sneak]:[])}
            }
            let confirmedLanding=worldState.map{$0.onGround && abs(pose.y-Double(flightFloor+1))<0.03} ?? false
            let groundedSupport=worldState.flatMap {state in
                BridgeLandingForecast.standingSupport(state,floor:flightFloor).max {
                    route.along(Double($0.x)+0.5,Double($0.z)+0.5)<route.along(Double($1.x)+0.5,Double($1.z)+0.5)
                }
            }
            // A vertical collision is evaluated before horizontal movement.
            // Only an actual support still under the post-movement body may
            // interrupt placement; an imminent Y collision is insufficient.
            let contactSupport=groundedSupport
            let recovery=jumpPlacements>=(jumpIndex==1 ? 4:activeRise==0 ? 3:2) && (forecast?.seconds ?? 1)<=0.12
            if (contactSupport != nil || jumpPlacements>=4 || recovery || confirmedLanding) && now-lastPlacementAt>(worldState == nil ? 0.055:0),
               let landing=contactSupport ?? drivenLanding ?? coastLanding {
                landingCoast=finishing || flightCoast || drivenLanding==nil
                self.support=landing
                // An actual edge contact overrides the wider airborne safety
                // margin and placement quota. Protect it in this same update;
                // one more unbraked game tick can carry the body off the face.
                setPlacing(false); keys(finishing || contactSupport != nil ? [config.sneak]:[]); phase = .landing; phaseAt=now
                _ = aim(yaw:heading,pitch:forwardPitch,pose:pose,now:now,preferredYawSign:1)
                return
            }
            let target: TellyPlacement
            if let state=worldState,let pending=pendingPlacements.first {
                if activeRise>0,state.tick>lastClickTick,state.clickDelay==4,now-pending.1>0.024 {
                    // The native press was consumed. Begin the next face's
                    // smooth approach during server confirmation latency, but
                    // keep clicks blocked until that block is observed solid.
                    target=route.next(after:pending.0.result)
                } else {target=pending.0}
            } else if support.y < flightFloor {
                target = TellyPlacement(support:support,result:F3Block(x:support.x,y:support.y+1,z:support.z),axis:1,sign:1,
                    x:Double(support.x)+0.5,y:Double(support.y)+1,z:Double(support.z)+0.5)
            } else {
                let exposed=route.exposedCandidates(after:support,from:pose)
                let choices=exposed.isEmpty ? [route.next(after:support)]:exposed
                func cost(_ choice:TellyPlacement)->Double {
                    if canPlace(choice,pose:pose){return -1000}
                    if choice.isVisibleFace(from:pose,eyeHeight:worldState?.eyeHeight ?? 1.62){return -500}
                    let point=choice.horizontalPoint(from:pose)
                    return abs(F3Pose.angle(atan2(pose.x-point.x,point.z-pose.z)*180 / .pi-pose.yaw))
                }
                target=choices.min(by:{cost($0)<cost($1)})!
            }
            placement = target
            // Aim through the centre of the moving placement window rather
            // than waiting until the ray has already fallen off its face.
            let predicted: F3Pose
            if let state=worldState {
                // The render position advances every frame between game
                // ticks. Lead it by two ticks rather than snapping the aim to
                // each newly received logical position every 50 ms.
                let lead=2.0
                predicted=F3Pose(x:state.renderPose.x+state.velocity.0*lead,y:state.renderPose.y+state.velocity.1*lead,z:state.renderPose.z+state.velocity.2*lead,yaw:pose.yaw,pitch:pose.pitch,time:pose.time,looking:pose.looking)
            } else {predicted=projected(pose,now:now,extra:target.axis == 1 ? 0.035:0.075)}
            let projection=(Double(target.support.x)+0.5-predicted.x)*route.ux+(Double(target.support.z)+0.5-predicted.z)*route.uz
            let sweep=8*cos(.pi*max(0,min(1,(now-launchAt-0.10)/0.26)))
            let lateral=max(0,-projection)*tan(sweep * .pi/180)
            let topX=max(Double(target.support.x)+0.15,min(Double(target.support.x)+0.85,predicted.x+route.ux*projection+route.uz*lateral))
            let topZ=max(Double(target.support.z)+0.15,min(Double(target.support.z)+0.85,predicted.z+route.uz*projection-route.ux*lateral))
            // Continue sweeping across the usable face throughout placement;
            // its geometric inset bounds the motion, rather than locking yaw
            // to the bridge axis or adding unrelated random jitter.
            let sweeping=F3Pose(x:predicted.x,y:predicted.y,z:predicted.z,yaw:heading+180+sweep,pitch:predicted.pitch,time:predicted.time)
            let sidePoint=target.horizontalPoint(from:sweeping,inset:0.15)
            let faceX=worldState != nil ? (target.axis==1 ? topX:sidePoint.x):target.x
            let faceZ=worldState != nil ? (target.axis==1 ? topZ:sidePoint.z):target.z
            let dx=faceX-predicted.x, dz=faceZ-predicted.z
            let aimYaw=atan2(-dx,dz)*180 / .pi
            let eyeHeight=worldState?.eyeHeight ?? 1.62
            var aimPitch=atan2(predicted.y+eyeHeight-target.y,hypot(dx,dz))*180 / .pi
            if worldState != nil,target.axis != 1 {
                let currentPoint=target.horizontalPoint(from:pose)
                let distance=hypot(currentPoint.x-pose.x,currentPoint.z-pose.z)
                let low=atan2(pose.y+eyeHeight-Double(target.support.y)-0.80,distance)*180 / .pi
                let high=atan2(pose.y+eyeHeight-Double(target.support.y)-0.20,distance)*180 / .pi
                aimPitch=max(low,min(high,aimPitch))
            }
            let awaitingPlacement=worldState != nil && !pendingPlacements.isEmpty
            let ready=canPlace(target,pose:pose)
            // A valid face permits a click during the turn. It must not
            // abruptly cancel that turn's velocity and restart a new servo.
            // A queued native click may not be consumed until the next game
            // tick. Keep its same face aligned as the player moves; freeze the
            // target, not a now-stale camera angle.
            if target.axis == 1 || (target.axis == 0 ? (predicted.x-target.x)*Double(target.sign) : (predicted.z-target.z)*Double(target.sign))>0.03 {
                followFace(yaw:aimYaw,pitch:min(88,aimPitch),pose:pose,now:now)
            }
            if phase == .idle { return }
            setPlacing(!awaitingPlacement && (worldState != nil || (turn==nil && pendingAimPose==nil)) && ready)
            let landingY=Double(flightFloor+1)
            if worldState==nil && airborne && abs(pose.y-landingY)<0.045 && vy<=0.2 {
                let under=F3Block(x:Int(floor(pose.x)),y:flightFloor,z:Int(floor(pose.z)))
                let touching=observed.contains { $0.y==flightFloor && pose.x+0.29>Double($0.x) && pose.x-0.29<Double($0.x)+1 && pose.z+0.29>Double($0.z) && pose.z-0.29<Double($0.z)+1 }
                guard touching else { return }
                setPlacing(false); keys([]); groundY=landingY
                if observed.contains(under) { self.support=under }
                phase = .aligning; phaseAt=now
            } else if now-phaseAt>0.85 { stop("没有及时识别到落地，已停止。") }
        case .landing:
            setPlacing(false)
            let facingForward=aim(yaw:heading,pitch:forwardPitch,pose:pose,now:now,preferredYawSign:1)
            let waitingOnGround=worldState?.onGround == true
            keys(finishing || waitingOnGround ? [config.sneak] : landingCoast ? [] : coordinateMovement ? forwardKeys(pose:pose,config:config) : (facingForward ? [config.forward,config.sprint]:[]))
            let landingY=Double(flightFloor+1)
            if let state=worldState {
                if pose.y<landingY-0.1 || now-phaseAt>0.8 {stop("未落在本次桥面，已停止。");return}
                if finishing {
                    if state.onGround,facingForward,hypot(state.velocity.0,state.velocity.2)<0.003 {
                        stop("本跳已完成，已落地并回正。")
                    }
                    return
                }
                if activeRise != risePerJump && !state.onGround {return}
                let forecast=BridgeLandingForecast.predict(state,height:landingY,yaw:heading,acceleration:landingCoast ? 0:0.02)
                let near=state.onGround || (forecast?.seconds ?? 1)<=0.05
                if facingForward,near, let landed=state.solid.filter({
                    $0.y==flightFloor && (state.onGround ? pose.x : forecast?.supportX ?? pose.x)+0.299>Double($0.x) && (state.onGround ? pose.x : forecast?.supportX ?? pose.x)-0.299<Double($0.x)+1 &&
                    (state.onGround ? pose.z : forecast?.supportZ ?? pose.z)+0.299>Double($0.z) && (state.onGround ? pose.z : forecast?.supportZ ?? pose.z)-0.299<Double($0.z)+1
                }).max(by:{route!.along(Double($0.x)+0.5,Double($0.z)+0.5)<route!.along(Double($1.x)+0.5,Double($1.z)+0.5)}) {
                    support=landed;groundY=landingY;pendingPlacements.removeAll()
                    // Commit the next mode together with its runway. A T
                    // press after approach begins is for the following cycle;
                    // changing height alone here leaves the wrong launch edge.
                    plannedRise=risePerJump
                    if let runway=route?.runway(on:landed) {
                        // Use the confirmed front edge for each takeoff. An
                        // immediate jump from the middle wastes half a block
                        // and repeats progressively shorter spans.
                        runwayEnd=runway.upperBound+(plannedRise>0 ? 0.05:0.23)-0.55*2*abs(route!.ux*route!.uz)
                        if activeRise>0 && plannedRise==0 {
                            // Rising landings can already overhang the edge
                            // with little speed. Rebuild a full runway before
                            // the first level span after a mode change.
                            runwayStart=runway.lowerBound+0.20
                            backingSign=runwayStart>route!.along(pose.x,pose.z) ? 1:-1
                            key(config.sprint,false)
                            phase = .backing;phaseAt=now
                            keys(backingSign>0 ? [config.forward]:[config.back])
                        } else {
                            phase = .runup;phaseAt=now
                            // Do not issue an unopposed W tick at the edge.
                            // Return completion can arrive immediately before
                            // physics; decide the jump in this same update.
                            advanceRunup(config:config,pose:pose,now:now)
                        }
                    } else {beginJump(config:config,pose:pose,now:now)}
                }
                return
            }
            if facingForward && pose.y>=landingY && pose.y<landingY+0.04 && vy<0,
               let landed=observed.first(where:{ $0.y==flightFloor && pose.x+0.29>Double($0.x) && pose.x-0.29<Double($0.x)+1 && pose.z+0.29>Double($0.z) && pose.z-0.29<Double($0.z)+1 }) {
                support=landed;groundY=landingY;pendingPlacements.removeAll()
                beginJump(config:config,pose:pose,now:now);return
            }
            if abs(pose.y-landingY)<0.002 && vy<=0.2 {
                let candidates=observed.union(pendingPlacements.map{$0.0.result})
                let touching=candidates.filter { $0.y==flightFloor && pose.x+0.29>Double($0.x) && pose.x-0.29<Double($0.x)+1 && pose.z+0.29>Double($0.z) && pose.z-0.29<Double($0.z)+1 }
                guard let route, let landed=touching.max(by:{ route.along(Double($0.x)+0.5,Double($0.z)+0.5)<route.along(Double($1.x)+0.5,Double($1.z)+0.5) }) else { stop("落地位置缺少方块确认，已停止。"); return }
                observed.insert(landed); support=landed; groundY=landingY
                pendingPlacements.removeAll(); phase = .aligning; phaseAt=now
            } else if pose.y<landingY-0.1 || now-phaseAt>0.8 { stop("未落在本次桥面，已停止。") }
        }
    }
    private func advanceRunup(config:TellyGameConfig,pose:F3Pose,now:Double) {
        guard let route else{return}
        let speed=max(0,vx*route.ux+vz*route.uz)
        if route.along(pose.x,pose.z)+speed*0.07>=runwayEnd {
            beginJump(config:config,pose:pose,now:now)
        } else {keys([config.forward,config.sprint])}
    }
    private func beginJump(config:TellyGameConfig,pose:F3Pose,now:Double) {
        if let state=worldState,state.onGround,BridgeClearance.jumpBlocked(state,yaw:heading,rise:jumpIndex==0 ? 0:plannedRise) {
            blockJump(config:config,now:now);return
        }
        phase = .takeoff;phaseAt=now;launchAt=now;jumpPlacements=0;airborne=false;launched=true;flightCoast=false
        // The opening span stays level to use the full flight window; later
        // cycles rise one block. A raised first landing cuts ~200 ms of air.
        activeRise=jumpIndex==0 ? 0:(worldState == nil ? risePerJump:plannedRise)
        flightFloor=(support?.y ?? Int(pose.y)-1)+activeRise
        jumpIndex+=1
        var desired=forwardKeys(pose:pose,config:config)
        desired.insert(config.jump);keys(desired)
        message="R 搭路中；松开后完成本跳并回正。"
    }
    private func blockJump(config:TellyGameConfig,now:Double) {
        // Only called while supported. Keep edge protection until residual
        // horizontal motion has stopped; releasing every key here can drift
        // off a narrow starting block.
        setPlacing(false);turn=nil;follower=nil;pendingAimPose=nil;cancelPendingInput()
        keys([config.sneak]);phase = .blocked;phaseAt=now
        blockedReason="前方或头顶空间不足，已在支撑处停稳；移开障碍后重新按 R。"
        message="前方或头顶有障碍，正在原地停稳。"
    }
    private func setPlacing(_ enabled: Bool) {
        guard enabled != placing else { return }
        placing = enabled
        if enabled { clickCycle() }
        else {
            clickTimer?.invalidate(); clickTimer = nil
        }
    }
    private func clickCycle() {
        guard placing, active, phase == .flight, track.fresh(now: ProcessInfo.processInfo.systemUptime) != nil else { setPlacing(false); return }
        let began = ProcessInfo.processInfo.systemUptime
        if began-lastPlacementAt < 1/maximumCPS {
            let retry=Timer(timeInterval:1/maximumCPS-(began-lastPlacementAt),repeats:false) { [weak self] _ in self?.clickCycle() }
            clickTimer=retry; RunLoop.main.add(retry,forMode:.common); return
        }
        let beat = rhythm.next(minimum: minimumCPS, maximum: maximumCPS, using: &random)
        let now = ProcessInfo.processInfo.systemUptime
        var emitted=false
        if let pose=track.fresh(now:now), let placement,
           pendingPlacements.count < 3,
           (worldState == nil || (worldState!.tick != lastClickTick && pendingPlacements.isEmpty)),
           (worldState != nil || (turn==nil && pendingAimPose==nil)),
           canPlace(placement,pose:pose) {
            if mouseDown { mouse(false) }
            trace("PLACE tick=\(worldState?.tick ?? -1) xyz=\(pose.x),\(pose.y),\(pose.z) view=\(pose.yaw),\(pose.pitch) command=\(follower?.yaw ?? issuedTurnYaw),\(follower?.pitch ?? issuedTurnPitch) target=\(placement.result) face=\(placement.axis),\(placement.sign)")
            mouse(true); mouseDown = true
            if !pendingPlacements.contains(where:{$0.0.result==placement.result}) {pendingPlacements.append((placement,now))}
            if worldState==nil {support=placement.result;jumpPlacements+=1}
            lastPlacementAt=now;lastClickTick=worldState?.tick ?? -1
            emitted=true
        }
        if emitted {
            releaseTimer?.invalidate()
            let release = Timer(timeInterval: min(0.020,beat.interval*0.4), repeats: false) { [weak self] _ in
                guard let self, self.mouseDown else { return }
                self.mouse(false); self.mouseDown = false
            }
            releaseTimer = release; RunLoop.main.add(release, forMode: .common)
        }
        // A delayed block confirmation is not a click. Retry the observation
        // promptly instead of losing another complete CPS interval.
        let delay = emitted ? max(0.001, beat.interval - (ProcessInfo.processInfo.systemUptime - began)) : 0.004
        let next = Timer(timeInterval: delay, repeats: false) { [weak self] _ in self?.clickCycle() }
        clickTimer = next; RunLoop.main.add(next, forMode: .common)
    }
    private func projected(_ pose: F3Pose, now: Double, extra: Double) -> F3Pose {
        let dt=min(0.16,max(0,now-pose.time)+extra)
        return F3Pose(x:pose.x+vx*dt,y:min(groundY+1.249,pose.y+(vy-0.8)*dt-16*dt*dt),z:pose.z+vz*dt,yaw:pose.yaw,pitch:pose.pitch,time:pose.time,looking:pose.looking)
    }
    private var calibrationYCount: Int64 = 20
}

// Cumulative integer counts preserve the exact calibrated angle. Both axes use
// one cosine-ramped cruise profile. Its long, even middle avoids the high
// midpoint speed of a short minimum-jerk flick; both ends accelerate smoothly.
// Cancellation drops all unissued counts immediately.
struct RelativeMouseTurn {
    static let maximumDuration=0.112
    static func duration(for span:Double)->Double {max(0.032,min(maximumDuration,0.032+abs(span)/180*0.080))}
    // Near a half turn, tiny aim errors must not randomly choose the other
    // side. Placement sweeps left, returning sweeps right. Small face tracking
    // corrections still take the shortest path; never turn a full circle.
    static func yawDelta(from:Double,to:Double,preferredSign:Double?)->Double {
        let delta=F3Pose.angle(to-from)
        guard abs(delta)>=150,let sign=preferredSign,sign*delta<0 else{return delta}
        return delta+(sign<0 ? -360:360)
    }
    private(set) var x:Int64,y:Int64
    let start: Double,duration:Double
    private var emittedX:Int64=0,emittedY:Int64=0
    private var sampledAt:Double
    private var segment: (start:Double,x:Double,y:Double,vx:Double,vy:Double)?
    init(x: Int64,y: Int64,start: Double,duration: Double) {
        self.x=x;self.y=y;self.start=start;self.duration=max(0.001,duration);sampledAt=start
    }
    mutating func retarget(x:Int64,y:Int64) {
        guard x != self.x || y != self.y else{return}
        // Keep the current position AND velocity when the face moves. Scaling
        // the whole old curve by a new endpoint teleports its intermediate
        // position. Leave the final braking interval intact; the follower
        // takes over any newer face target immediately after this turn.
        guard start+duration-sampledAt>0.024 else{return}
        let state=sample(now:sampledAt)
        let remaining=start+duration-sampledAt
        func feasible(_ target:Int64,_ old:Int64,_ position:Double,_ velocity:Double)->Int64 {
            let distance=Double(target)-position
            // A zero-end-velocity Hermite segment is monotone when its
            // starting speed is no more than three times the average speed.
            // Defer an abrupt inward target change instead of overshooting
            // and reversing at the end of a turn.
            guard abs(velocity)<0.001 || (velocity*distance>0 && abs(velocity)*remaining<=3*abs(distance)) else{return old}
            return target
        }
        let acceptedX=feasible(x,self.x,state.x,state.vx),acceptedY=feasible(y,self.y,state.y,state.vy)
        guard acceptedX != self.x || acceptedY != self.y else{return}
        segment=(sampledAt,state.x,state.y,state.vx,state.vy)
        self.x=acceptedX;self.y=acceptedY
    }
    private func sample(now:Double)->(x:Double,y:Double,vx:Double,vy:Double) {
        if let segment {
            let remaining=max(0.001,start+duration-segment.start)
            let u=max(0,min(1,(now-segment.start)/remaining))
            func hermite(_ from:Double,_ velocity:Double,_ to:Double)->(Double,Double) {
                let a=2*from-2*to+velocity*remaining,b = -3*from+3*to-2*velocity*remaining,c=velocity*remaining
                return (((a*u+b)*u+c)*u+from, (3*a*u*u+2*b*u+c)/remaining)
            }
            let sx=hermite(segment.x,segment.vx,Double(x)),sy=hermite(segment.y,segment.vy,Double(y))
            return (sx.0,sy.0,sx.1,sy.1)
        }
        let t=max(0,min(1,(now-start)/duration)),ramp=0.18
        func rampStart(_ u:Double)->Double {(u-ramp / .pi*sin(.pi*u/ramp))/(2*(1-ramp))}
        let f=t<ramp ? rampStart(t) : t>1-ramp ? 1-rampStart(1-t) : (t-ramp/2)/(1-ramp)
        let speed=(t<ramp ? (1-cos(.pi*t/ramp))/2 : t>1-ramp ? (1-cos(.pi*(1-t)/ramp))/2 : 1)/(1-ramp)/duration
        return (Double(x)*f,Double(y)*f,Double(x)*speed,Double(y)*speed)
    }
    mutating func advance(now: Double) -> (x:Int64,y:Int64,finished:Bool) {
        let state=sample(now:now);sampledAt=max(sampledAt,min(start+duration,now))
        let cumulativeX=Int64(state.x.rounded()),cumulativeY=Int64(state.y.rounded())
        let result=(cumulativeX-emittedX,cumulativeY-emittedY,now>=start+duration)
        emittedX=cumulativeX;emittedY=cumulativeY
        return result
    }

}

// Continuous bounded relative-mouse servo for tracking a moving face. The
// command angle includes counts already queued, avoiding duplicate corrections
// while native mouse events are still in transit. Large turns use the separate
// ramped cruise curve. No absolute camera or game-state writes are used.
struct RelativeMouseFollower {
    private(set) var yaw:Double,pitch:Double
    private var time:Double
    private var yawSpeed=0.0,pitchSpeed=0.0
    private var continuousYaw:Double,continuousPitch:Double
    init(yaw:Double,pitch:Double,now:Double){
        self.yaw=yaw;self.pitch=pitch;continuousYaw=yaw;continuousPitch=pitch;time=now
    }
    mutating func advance(yaw targetYaw:Double,pitch targetPitch:Double,now:Double,gainX:Double,gainY:Double)->(Int64,Int64) {
        guard now>time else{return (0,0)}
        let dt=min(0.025,now-time);time=now
        // Critically damped position and velocity, integrated analytically.
        // A new face changes the target, not the current camera velocity.
        // Keep the fractional trajectory separate from emitted mouse counts
        // so quantization cannot repeatedly stop/restart the controller.
        let omega=100.0
        func advanceAxis(_ position:Double,_ velocity:Double,_ target:Double)->(Double,Double) {
            let error=position-target,c=velocity+omega*error,decay=exp(-omega*dt)
            let next=target+(error+c*dt)*decay
            let desired=(velocity-omega*c*dt)*decay
            let bounded=max(-1100,min(1100,max(velocity-45000*dt,min(velocity+45000*dt,desired))))
            let value=abs(bounded-desired)<0.0001 ? next : position+(velocity+bounded)*0.5*dt
            return (value,bounded)
        }
        let targetX=continuousYaw+F3Pose.angle(targetYaw-continuousYaw)
        (continuousYaw,yawSpeed)=advanceAxis(continuousYaw,yawSpeed,targetX)
        (continuousPitch,pitchSpeed)=advanceAxis(continuousPitch,pitchSpeed,max(-88,min(88,targetPitch)))
        continuousYaw=F3Pose.angle(continuousYaw);continuousPitch=max(-90,min(90,continuousPitch))
        let x=Int64((F3Pose.angle(continuousYaw-yaw)/gainX).rounded())
        let y=Int64(((continuousPitch-pitch)/gainY).rounded())
        yaw=F3Pose.angle(yaw+Double(x)*gainX);pitch=max(-90,min(90,pitch+Double(y)*gainY))
        return (x,y)
    }
}
