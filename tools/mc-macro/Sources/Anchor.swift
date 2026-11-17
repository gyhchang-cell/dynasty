import Foundation

struct AnchorCell {
    let id:String, full:Bool, replaceable:Bool, charge:Int, pending:Bool
}
struct AnchorCells:Sequence {
    let values:[F3Block:AnchorCell],bounds:[Int]?
    static let air=AnchorCell(id:"minecraft:air",full:false,replaceable:true,charge:-1,pending:false)
    subscript(_ b:F3Block)->AnchorCell? {
        if let value=values[b] {return value}
        guard let v=bounds,b.x>=v[0],b.x<=v[1],b.y>=v[2],b.y<=v[3],b.z>=v[4],b.z<=v[5] else{return nil}
        return Self.air
    }
    func makeIterator()->Dictionary<F3Block,AnchorCell>.Iterator {values.makeIterator()}
}
struct AnchorItem:Decodable {let slot:Int,id:String,count:Int,full:Bool}
struct AnchorHit:Decodable {let pos:[Int],face:String,point:[Double]}
struct AnchorState {
    let time:Double,world:Int,tick:Int,dimension:String,active:Bool,singleplayer:Bool
    var position:[Double],eye:[Double]
    let velocity:[Double],yaw:Double,pitch:Double,sensitivity:Double,range:Double
    let ground:Bool,sneaking:Bool,using:Bool,mouseReady:Bool,health:Double,selected:Int,offhand:String,useKey:String
    let slots:[AnchorItem],keys:[String],triggerBindings:[String],hit:AnchorHit?
    let sprint:SprintObservation?
    let combat:SwordObservation?
    let rightDown:Bool
    let movementKeys:[String],movementUsable:Bool,movementDown:Bool
    let cells:AnchorCells
    static func parse(_ d:[String:Any],now:Double)->AnchorState? {
        func vector(_ key:String)->[Double]? {guard let v=d[key] as? [Double],v.count==3,v.allSatisfy(\.isFinite) else{return nil};return v}
        guard let age=d["age"] as? Double,(0...0.15).contains(age),let world=d["world"] as? Int,let tick=d["tick"] as? Int,
              let dimension=d["dimension"] as? String,let p=vector("position"),let eye=vector("eye"),let v=vector("velocity"),
              let yaw=d["yaw"] as? Double,let pitch=d["pitch"] as? Double,yaw.isFinite,(-90...90).contains(pitch),
              let sensitivity=d["sensitivity"] as? Double,(0...1).contains(sensitivity),let range=d["range"] as? Double,(0...6).contains(range),
              let selected=d["selected"] as? Int,(0..<9).contains(selected),let keys=d["keys"] as? [String],keys.count==9,
              let itemData=try? JSONSerialization.data(withJSONObject:d["slots"] ?? []),let slots=try? JSONDecoder().decode([AnchorItem].self,from:itemData),
              slots.count==9,Set(slots.map(\.slot))==Set(0..<9),let rows=d["cells"] as? [[Any]],rows.count<=2197 else{return nil}
        var cells:[F3Block:AnchorCell]=[:]
        let palette=d["palette"] as? [String] ?? []
        for row in rows {
            guard [6,8].contains(row.count),let x=row[0] as? Int,let y=row[1] as? Int,let z=row[2] as? Int else{return nil}
            let cell:AnchorCell
            if row.count==8 {
                guard let id=row[3] as? String,let full=row[4] as? Bool,let replace=row[5] as? Bool,let charge=row[6] as? Int,let pending=row[7] as? Bool else{return nil}
                cell=AnchorCell(id:id,full:full,replaceable:replace,charge:charge,pending:pending)
            } else {
                guard let index=row[3] as? Int,palette.indices.contains(index),let flags=row[4] as? Int,(0...7).contains(flags),let charge=row[5] as? Int else{return nil}
                cell=AnchorCell(id:palette[index],full:flags&1 != 0,replaceable:flags&2 != 0,charge:charge,pending:flags&4 != 0)
            }
            cells[F3Block(x:x,y:y,z:z)]=cell
        }
        let bounds=d["volume"] as? [Int]
        if let b=bounds {guard b.count==6,b[1]>=b[0],b[3]>=b[2],b[5]>=b[4],b[1]-b[0]<=12,b[3]-b[2]<=12,b[5]-b[4]<=12 else{return nil}}
        let hit=(d["hit"] as? [String:Any]).flatMap{try? JSONSerialization.data(withJSONObject:$0)}.flatMap{try? JSONDecoder().decode(AnchorHit.self,from:$0)}
        return AnchorState(time:now-age,world:world,tick:tick,dimension:dimension,active:d["active"] as? Bool ?? false,singleplayer:d["singleplayer"] as? Bool ?? false,
            position:p,eye:eye,velocity:v,yaw:yaw,pitch:pitch,sensitivity:sensitivity,range:range,
            ground:d["ground"] as? Bool ?? false,sneaking:d["sneaking"] as? Bool ?? true,using:d["using"] as? Bool ?? true,mouseReady:d["mouseReady"] as? Bool ?? false,health:d["health"] as? Double ?? 0,
            selected:selected,offhand:d["offhand"] as? String ?? "",useKey:d["useKey"] as? String ?? "",slots:slots,keys:keys,triggerBindings:d["triggerBindings"] as? [String] ?? ["unknown"],hit:hit,sprint:SprintObservation.parse(d,time:now-age,world:world),combat:SwordObservation.parse(d["combat"]),rightDown:d["rightDown"] as? Bool ?? false,movementKeys:d["movementKeys"] as? [String] ?? [],movementUsable:d["movementUsable"] as? Bool ?? false,movementDown:d["movementDown"] as? Bool ?? true,cells:AnchorCells(values:cells,bounds:bounds))
    }
    func fresh(_ now:Double)->Bool {now>=time && now-time<0.15 && active}
    func positioned(_ p:[Double])->AnchorState {
        var copy=self;copy.position=p;copy.eye=zip(eye,zip(p,position)).map{$0.0+$0.1.0-$0.1.1};return copy
    }
}

struct AnchorRay {
    let point:[Double],face:String
    static let directions:[String:(Int,Int,Int)]=["UP":(0,1,0),"DOWN":(0,-1,0),"WEST":(-1,0,0),"EAST":(1,0,0),"NORTH":(0,0,-1),"SOUTH":(0,0,1)]
    static func distance(_ a:[Double],_ b:[Double])->Double {sqrt(zip(a,b).reduce(0){$0+pow($1.0-$1.1,2)})}
    static func crosses(_ from:[Double],_ to:[Double],_ block:F3Block)->Bool {
        let low=[Double(block.x)-0.02,Double(block.y)-0.02,Double(block.z)-0.02]
        var near=0.0,far=1.0
        for i in 0..<3 {
            let delta=to[i]-from[i]
            if abs(delta)<1e-9 {if from[i]<=low[i] || from[i]>=low[i]+1.04 {return false};continue}
            let a=(low[i]-from[i])/delta,b=(low[i]+1.04-from[i])/delta
            near=max(near,min(a,b));far=min(far,max(a,b))
        }
        return near<far-1e-6 && far>1e-6 && near<1-1e-6
    }
    static func visible(_ block:F3Block,state s:AnchorState,topOnly:Bool=false,extraBlocks:[F3Block]=[],requiredFace:String?=nil)->AnchorRay? {
        let low=[Double(block.x),Double(block.y),Double(block.z)]
        for face in ["UP","NORTH","SOUTH","WEST","EAST","DOWN"] {
            if topOnly && face != "UP" {continue}
            if let requiredFace,face != requiredFace {continue}
            let offset=directions[face]!,axis=offset.0 != 0 ? 0:offset.1 != 0 ? 1:2
            let sign=[offset.0,offset.1,offset.2][axis],plane=low[axis]+(sign>0 ? 1:0)
            guard (s.eye[axis]-plane)*Double(sign)>1e-5 else{continue}
            let closest=(0..<3).map{max(low[$0]+0.06,min(low[$0]+0.94,s.eye[$0]))}
            // Preserve the proven center aim when it is reachable. Use nearer
            // points only as needed, with clearance around intervening blocks.
            var points=[[Double]]()
            for blend in [1.0,0.65,0.35,0.0] {
                var point=(0..<3).map{closest[$0]+(low[$0]+0.5-closest[$0])*blend};point[axis]=plane;points.append(point)
            }
            // Edge peeks are a fallback. Keep the established center ray first.
            let other=(0..<3).filter{$0 != axis}
            for u in [0.06,0.94] {for v in [0.5,0.06,0.94] {
                var point=low;point[axis]=plane;point[other[0]]+=u;point[other[1]]+=v;points.append(point)
            }}
            for point in points {
                guard distance(s.eye,point)<s.range-0.015 else{continue}
                let blocked=s.cells.contains{at,cell in at != block && cell.full && crosses(s.eye,point,at)} || extraBlocks.contains{$0 != block && crosses(s.eye,point,$0)}
                if !blocked {return AnchorRay(point:point,face:face)}
            }
        }
        return nil
    }
}

struct AnchorPlan {
    static func shieldMaterial(_ id:String)->Bool {
        guard id.hasPrefix("minecraft:") else{return false}
        let name=String(id.dropFirst(10))
        let inert:Set<String>=["stone","cobblestone","end_stone","deepslate","cobbled_deepslate","dirt","coarse_dirt","rooted_dirt","grass_block","netherrack","glass","tuff","calcite","andesite","diorite","granite","polished_andesite","polished_diorite","polished_granite","blackstone","polished_blackstone","smooth_stone","sandstone","red_sandstone","quartz_block","smooth_quartz","prismarine","dark_prismarine","bricks","obsidian","crying_obsidian"]
        return inert.contains(name) || ["_planks","_wool","_concrete","_terracotta","_stained_glass","_bricks","_log","_wood","_stem","_hyphae"].contains(where:{name.hasSuffix($0)})
    }
    static func shieldSlot(_ items:[AnchorItem])->AnchorItem? {
        items.filter{$0.count>0 && $0.full && shieldMaterial($0.id)}.sorted {
            let a=$0.id.contains("obsidian") ? 1:0,b=$1.id.contains("obsidian") ? 1:0
            return a==b ? $0.slot<$1.slot:a<b
        }.first
    }
    struct Placement {let block:F3Block,support:F3Block,face:String}
    let anchor:F3Block,shield:F3Block,shieldSupport:F3Block,shieldFace:String
    let placements:[Placement],triggerOrigin:[Double]
    let anchorSlot:Int,glowSlot:Int,shieldSlot:Int,detonateSlot:Int
    let shieldID:String,world:Int,yaw:Double,pitch:Double
    var origin:[Double]
    let reuseShield:Bool,shieldFirst:Bool
    static func shieldsBody(anchor:F3Block,shield:F3Block,position:[Double])->Bool {
        let source=[Double(anchor.x)+0.5,Double(anchor.y)+0.5,Double(anchor.z)+0.5]
        let lower=[Double(shield.x)+0.01,Double(shield.y)+0.01,Double(shield.z)+0.01]
        let upper=[Double(shield.x+1)-0.01,Double(shield.y+1)-0.01,Double(shield.z+1)-0.01]
        // The standing body must lie inside the solid block's blast shadow.
        // A ray merely touching an edge/corner is not sufficient shielding.
        for x in [-0.31,0.31] {for y in [0.01,1.81] {for z in [-0.31,0.31] {
            let end=[position[0]+x,position[1]+y,position[2]+z]
            var near=0.0,far=1.0
            for i in 0..<3 {
                let delta=end[i]-source[i]
                if abs(delta)<1e-9 {if source[i]<lower[i] || source[i]>upper[i] {return false};continue}
                let a=(lower[i]-source[i])/delta,b=(upper[i]-source[i])/delta
                near=max(near,min(a,b));far=min(far,max(a,b))
            }
            if near>=far || far<=0 || near>=1 {return false}
        }}}
        return true
    }
    static func walkable(_ s:AnchorState,from:[Double],to:[Double],anchor:F3Block)->Bool {
        guard abs(from[1]-to[1])<0.01 else{return false}
        let steps=max(1,Int(ceil(hypot(to[0]-from[0],to[2]-from[2])/0.04)))
        for i in 0...steps {
            let t=Double(i)/Double(steps),x=from[0]+(to[0]-from[0])*t,z=from[2]+(to[2]-from[2])*t
            for bx in Int(floor(x-0.31))...Int(floor(x+0.31)) {for bz in Int(floor(z-0.31))...Int(floor(z+0.31)) {
                let foot=F3Block(x:bx,y:Int(floor(to[1]-0.02)),z:bz)
                guard let support=s.cells[foot],support.full,!support.pending,
                      Self.shieldMaterial(support.id) || support.id=="minecraft:bedrock" else{return false}
                for by in Int(floor(to[1]+0.01))...Int(floor(to[1]+1.81)) {
                    let at=F3Block(x:bx,y:by,z:bz)
                    guard at != anchor,let cell=s.cells[at],!cell.pending,["minecraft:air","minecraft:cave_air","minecraft:void_air"].contains(cell.id) else{return false}
                }
            }}
        }
        return true
    }
    func usableAt(_ s:AnchorState)->Bool {
        guard Self.shieldsBody(anchor:anchor,shield:shield,position:s.position),
              AnchorRay.visible(anchor,state:s,extraBlocks:placements.map(\.block)+[shield]) != nil else{return false}
        var extra=[anchor]
        for step in placements {
            guard AnchorRay.visible(step.support,state:s,extraBlocks:extra,requiredFace:step.face) != nil else{return false}
            extra.append(step.block)
        }
        return true
    }
    static func make(_ original:AnchorState,now:Double)throws->AnchorPlan {
        let s=original
        func fail(_ reason:String)throws->Never {throw AnchorFailure(reason:reason)}
        guard s.fresh(now),s.ground,!s.sneaking,!s.using else{try fail("需落地、关闭菜单并松开潜行/使用键")}
        guard ["minecraft:overworld","minecraft:the_end"].contains(s.dimension) else{try fail("当前维度不支持引爆")}
        guard s.useKey=="key.mouse.right",Set(s.keys).count==9,s.keys.allSatisfy({SprintGameConfig.binding($0) != nil}) else{try fail("快捷栏或右键绑定不支持")}
        guard s.offhand != "minecraft:glowstone" else{try fail("请先移走副手荧石")}
        guard let h=s.hit,h.pos.count==3,h.point.count==3,h.point.allSatisfy(\.isFinite),let offset=AnchorRay.directions[h.face] else{try fail("准星未命中可放置的方块表面")}
        guard AnchorRay.distance(s.eye,h.point)<=s.range+0.01 else{try fail("放置位置超出游戏交互距离")}
        let base=F3Block(x:h.pos[0],y:h.pos[1],z:h.pos[2])
        let a=s.cells[base]?.replaceable==true ? base:F3Block(x:base.x+offset.0,y:base.y+offset.1,z:base.z+offset.2)
        guard s.cells[a]?.replaceable==true,s.cells[a]?.pending==false else{try fail("锚位置被占用或尚未确认")}
        func slot(_ id:String)->Int? {s.slots.first{$0.id==id && $0.count>0}?.slot}
        guard let anchorSlot=slot("minecraft:respawn_anchor"),let glow=slot("minecraft:glowstone") else{try fail("快捷栏缺少重生锚或荧石")}
        let material=Self.shieldSlot(s.slots)
        let detonate=s.slots.first{$0.id.hasSuffix("_sword") && $0.count>0}?.slot ?? s.slots.first{$0.id=="minecraft:air"}?.slot ?? material?.slot ?? anchorSlot
        var candidates:[F3Block]=[]
        for radius in 1...2 {for dy in [0,-1,1] {for x in -radius...radius {for z in -radius...radius where max(abs(x),abs(z))==radius {
            candidates.append(F3Block(x:a.x+x,y:a.y+dy,z:a.z+z))
        }}}}
        func choose(_ s:AnchorState,foundations:Bool)->AnchorPlan? {
            guard AnchorRay.visible(a,state:s) != nil else{return nil}
            func reusable(_ b:F3Block)->Bool {s.cells[b]?.full==true && s.cells[b]?.pending==false && (Self.shieldMaterial(s.cells[b]?.id ?? "") || s.cells[b]?.id=="minecraft:bedrock")}
            func overlap(_ b:F3Block)->Bool {s.position[0]+0.31>Double(b.x) && s.position[0]-0.31<Double(b.x+1) && s.position[2]+0.31>Double(b.z) && s.position[2]-0.31<Double(b.z+1) && s.position[1]+1.81>Double(b.y) && s.position[1]<Double(b.y+1)}
            func support(_ b:F3Block,_ extra:[F3Block])->(F3Block,String)? {
                for face in ["UP","NORTH","SOUTH","WEST","EAST","DOWN"] {
                    let d=AnchorRay.directions[face]!,at=F3Block(x:b.x-d.0,y:b.y-d.1,z:b.z-d.2)
                    if (at==a ? foundations:(reusable(at) || extra.contains(at))),
                       AnchorRay.visible(at,state:s,extraBlocks:extra+[a],requiredFace:face) != nil {return (at,face)}
                }
                return nil
            }
            func steps(_ b:F3Block,_ budget:Int)->[Placement]? {
                guard b != a,!overlap(b),s.cells[b]?.replaceable==true,s.cells[b]?.pending==false else{return nil}
                if let (at,face)=support(b,[]) {return [Placement(block:b,support:at,face:face)]}
                guard budget>1 else{return nil}
                let below=F3Block(x:b.x,y:b.y-1,z:b.z)
                guard let prior=steps(below,budget-1),let (at,face)=support(b,prior.map(\.block)) else{return nil}
                return prior+[Placement(block:b,support:at,face:face)]
            }
            for b in candidates {
                guard !overlap(b),Self.shieldsBody(anchor:a,shield:b,position:s.position) else{continue}
                let reuse=reusable(b),placements:[Placement]
                if reuse {placements=[]}
                else {guard let material,let list=steps(b,foundations ? 3:1),list.count<=material.count else{continue};placements=list}
                guard AnchorRay.visible(a,state:s,extraBlocks:placements.map(\.block)+[b]) != nil else{continue}
                let last=placements.last
                return AnchorPlan(anchor:a,shield:b,shieldSupport:last?.support ?? b,shieldFace:last?.face ?? "UP",placements:placements,triggerOrigin:original.position,anchorSlot:anchorSlot,glowSlot:glow,shieldSlot:material?.slot ?? anchorSlot,detonateSlot:detonate,shieldID:reuse ? s.cells[b]!.id:material!.id,world:s.world,yaw:original.yaw,pitch:original.pitch,origin:s.position,reuseShield:reuse,shieldFirst:placements.contains{$0.support==a})
            }
            return nil
        }
        // Successful original placements keep priority and need no movement.
        if let p=choose(s,foundations:false) {return p}
        if let p=choose(s,foundations:true) {return p}
        let keyCodes=s.movementKeys.compactMap{SprintGameConfig.binding($0)}
        guard s.movementUsable,!s.movementDown,keyCodes.count==4,Set(keyCodes).count==4,
              keyCodes.allSatisfy({![UInt16(59),62,56,60,58,61].contains($0)}),hypot(s.velocity[0],s.velocity[2])<0.03 else{try fail("当前地形无法原地遮挡 · 挪位需要松开移动键")}
        // Search by increasing displacement, only over known supported floor.
        var offsets:[(Int,Int)]=[]
        for x in -15...15 {for z in -15...15 where x*x+z*z>0 && x*x+z*z<=225 {offsets.append((x,z))}}
        offsets.sort {lhs,rhs in
            let left=lhs.0*lhs.0+lhs.1*lhs.1,right=rhs.0*rhs.0+rhs.1*rhs.1
            if left != right {return left<right}
            if lhs.0 != rhs.0 {return lhs.0<rhs.0}
            return lhs.1<rhs.1
        }
        for (x,z) in offsets {
            let point=[s.position[0]+Double(x)*0.05,s.position[1],s.position[2]+Double(z)*0.05]
            guard Self.walkable(s,from:s.position,to:point,anchor:a) else{continue}
            if let p=choose(s.positioned(point),foundations:true) {return p}
        }
        try fail("附近没有可遮挡且能触及锚的位置")
    }
}
struct AnchorFailure:Error {let reason:String}

final class AnchorController {
    enum Phase:String {case idle,awaitPlacement,reposition,charge,shield,detonate,restore}
    private(set) var phase=Phase.idle
    private(set) var message="待命 · 右键放锚"
    private(set) var failure:String?
    private(set) var plan:AnchorPlan?
    var active:Bool {phase != .idle}
    var select:(UInt16)->Void={_ in},click:()->Void={},move:(Int,Int)->Void={_,_ in},release:()->Void={},trace:(String)->Void={_ in}
    var movement:(Set<UInt16>)->Void={_ in}
    var repositioning:Bool {phase == .reposition}
    private var began=0.0,phaseBegan=0.0,lastAction = -Double.infinity,lastMove = -Double.infinity
    private var issued=false,selectedSlot:Int?,lastState:Double = -Double.infinity
    private var issuedAt:Double?,sawPrediction=false
    private var pendingAim:(Double,Double)?
    private var primedMouse=false
    private var oldSlot=0,lastClick = -Double.infinity
    private var preparedPhase:Phase?
    private var shieldIndex=0,pulseUntil:Double?,settleUntil=0.0
    func start(_ s:AnchorState,now:Double) {
        guard !active else{return}
        failure=nil
        do {plan=try AnchorPlan.make(s,now:now)} catch {message=(error as? AnchorFailure)?.reason ?? "位置不可用";failure=message;trace("REJECT \(message) hit=\(String(describing:s.hit)) eye=\(s.eye) range=\(s.range)");return}
        oldSlot=s.selected;began=now;lastState = -Double.infinity;lastAction = -Double.infinity;lastMove = -Double.infinity;pendingAim=nil;primedMouse=false;lastClick = -Double.infinity;preparedPhase=nil;shieldIndex=0;pulseUntil=nil;settleUntil=0
        transition(.awaitPlacement,now);trace("BEGIN world=\(s.world) anchor=\(plan!.anchor) shield=\(plan!.shield) yaw=\(s.yaw) pitch=\(s.pitch)")
    }
    func stop(_ text:String) {guard active else{return};phase = .idle;plan=nil;release();message=text;failure=text;trace("STOP "+text)}
    private func recover(_ reason:String,_ now:Double) {
        // A server rejection must not strand the player looking down with
        // glowstone selected. No more use actions; retain the original view/slot.
        failure=reason;release();transition(.restore,now);trace("ABORT "+reason)
    }
    private func transition(_ next:Phase,_ now:Double) {
        if preparedPhase != next {selectedSlot=nil}
        phase=next;phaseBegan=now;issued=false;issuedAt=nil;sawPrediction=false;message=[Phase.awaitPlacement:"等待放锚",.reposition:"调整站位",.charge:"充能",.shield:"遮挡",.detonate:"引爆",.restore:"回正"][next] ?? "待命"
        trace(String(format:"PHASE %@ %.3f",next.rawValue,now-began))
    }
    func tick(_ s:AnchorState?,now:Double,allowed:Bool) {
        guard active,let p=plan else{return}
        guard allowed,let s,s.fresh(now),s.world==p.world else{stop("已停止 · 游戏状态变化");return}
        if (phase != .restore && now-began>=4) || now-(issuedAt ?? phaseBegan)>=1.2 {
            if phase == .restore {stop("已停止 · 回正超时")}
            else {recover("已停止 · 等待操作确认超时",now)}
            return
        }
        // Once the last native use was sent, recoil cannot make another use
        // unsafe: there will be none. Still finish confirmation and restoration.
        let needsFixedPosition=phase != .restore && phase != .reposition && !(phase == .detonate && issued)
        let origin=phase == .awaitPlacement ? p.triggerOrigin:p.origin
        guard !needsFixedPosition || (hypot(s.position[0]-origin[0],s.position[2]-origin[2])<0.28 && abs(s.position[1]-origin[1])<0.2),!s.sneaking,!s.using else{stop("已停止 · 位置或使用状态变化");return}
        guard s.time>lastState else{return};lastState=s.time
        if !s.mouseReady {
            // Vanilla ignores this first nonzero cursor callback after a menu.
            // Zero motion is filtered by GLFW, so wait for the read-only flag
            // to clear before issuing or calculating any actual camera turn.
            if !primedMouse {primedMouse=true;move(1,0);trace("PRIME mouse")};return
        }
        let anchor=s.cells[p.anchor],shield=s.cells[p.shield]
        if phase == .reposition {steer(s,plan:p,now:now);return}
        if phase == .awaitPlacement {
            // Placement stays native. Once its client result exists we may
            // prepare the next slot/view, but never charge before confirmation.
            guard anchor?.id=="minecraft:respawn_anchor",anchor?.charge==0 else{return}
            if anchor?.pending != false {
                if now-began>=0.04,AnchorRay.distance(p.triggerOrigin,p.origin)<0.01 {_=prepare(p.shieldFirst ? .shield:.charge,plan:p,state:s,now:now)}
                return
            }
            if AnchorRay.distance(p.triggerOrigin,p.origin)>0.01 {transition(.reposition,now);steer(s,plan:p,now:now);return}
            transition(p.shieldFirst ? .shield:.charge,now)
        }
        if phase == .restore {
            if aim(yaw:p.yaw,pitch:p.pitch,state:s,now:now) {
                if s.selected != oldSlot,selectedSlot != oldSlot,let key=SprintGameConfig.binding(s.keys[oldSlot]) {select(key);selectedSlot=oldSlot;lastAction=now;return}
                guard s.selected==oldSlot else{return}
                let duration=now-began;phase = .idle;plan=nil;release()
                if let reason=failure {message=reason+" · 已回正";failure=message;trace("RECOVERED "+reason)}
                else {message=String(format:"完成 · %.2f 秒",duration);trace(String(format:"SUCCESS %.3f yaw=%.3f pitch=%.3f health=%.1f",duration,s.yaw,s.pitch,s.health))}
            };return
        }
        if issued {
            let cell=phase == .shield ? s.cells[p.placements[shieldIndex].block]:anchor
            if cell?.pending==true {sawPrediction=true}
            if phase == .charge || phase == .shield {
                if anchor?.pending==false,anchor?.id != "minecraft:respawn_anchor" {recover("已停止 · 锚已被移除",now);return}
            }
            let done:Bool
            switch phase {
            case .charge:done=anchor?.id=="minecraft:respawn_anchor" && (anchor?.charge ?? 0)>0 && anchor?.pending==false
            case .shield:done=cell?.id==p.shieldID && cell?.full==true && cell?.pending==false
            case .detonate:done=anchor?.replaceable==true && anchor?.pending==false
            default:done=false
            }
            if done,now-(issuedAt ?? lastAction)>0.015 {
                if phase == .shield,shieldIndex+1<p.placements.count {shieldIndex+=1;transition(.shield,now)}
                else {transition(phase == .charge ? (p.reuseShield || p.shieldFirst ? .detonate:.shield):phase == .shield ? (p.shieldFirst ? .charge:.detonate):.restore,now)}
            } else {
                let predictedEffect = phase == .charge ? ((anchor?.charge ?? 0)>0):phase == .shield ? (cell?.id==p.shieldID && cell?.full==true && shieldIndex+1==p.placements.count):false
                if predictedEffect,cell?.pending==true {
                    _=prepare(phase == .charge ? (p.reuseShield || p.shieldFirst ? .detonate:.shield):(p.shieldFirst ? .charge:.detonate),plan:p,state:s,now:now)
                }
                if !done,sawPrediction,cell?.pending==false {
                    let reason=phase == .charge ? "充能被回退":phase == .shield ? "挡块被回退":"引爆未确认"
                    recover("已停止 · "+reason,now)
                }
                return
            }
        }
        if phase == .restore {return}
        if anchor?.id != "minecraft:respawn_anchor" {recover("已停止 · 锚已变化",now);return}
        if phase == .detonate {
            guard shield?.id==p.shieldID,shield?.full==true,shield?.pending==false,(anchor?.charge ?? 0)>0,s.offhand != "minecraft:glowstone",AnchorPlan.shieldsBody(anchor:p.anchor,shield:p.shield,position:s.position) else{recover("已停止 · 未确认遮挡或充能",now);return}
        }
        guard prepare(phase,plan:p,state:s,now:now),now-lastClick>=0.020 else{return}
        click();issued=true;issuedAt=now;sawPrediction=false;lastAction=now;lastClick=now;trace(String(format:"CLICK %@ %.3f tick=%d",phase.rawValue,now-began,s.tick))
    }
    private func steer(_ s:AnchorState,plan p:AnchorPlan,now:Double) {
        guard s.cells[p.anchor]?.id=="minecraft:respawn_anchor",s.cells[p.anchor]?.charge==0,s.cells[p.anchor]?.pending==false,
              s.ground,abs(s.position[1]-p.triggerOrigin[1])<0.05,
              hypot(s.position[0]-p.triggerOrigin[0],s.position[2]-p.triggerOrigin[2])<0.95,
              AnchorPlan.walkable(s,from:p.triggerOrigin,to:s.position,anchor:p.anchor) else{movement([]);recover("已停止 · 挪位路径变化",now);return}
        let valid=p.usableAt(s),speed=hypot(s.velocity[0],s.velocity[2])
        if let until=pulseUntil {
            // Ordinary supported blocks use ground friction .6*.91. Include
            // the remaining coast before deciding whether to release a pulse.
            // Ice/slime/honey are excluded by walkable, never treated as stone.
            let coast=[s.position[0]+s.velocity[0]*2.2,s.position[1],s.position[2]+s.velocity[2]*2.2]
            let stoppingPoint=p.usableAt(s.positioned(coast)) && AnchorPlan.walkable(s,from:s.position,to:coast,anchor:p.anchor)
            if now>=until || valid || stoppingPoint {movement([]);pulseUntil=nil;settleUntil=now+0.10}
            return
        }
        // A narrow edge peek can be lost to a few centimeters of residual
        // motion between telemetry, native input and the next game tick.
        guard now>=settleUntil,speed<0.025 else{return}
        if valid {
            guard speed<0.001 else{return}
            movement([]);var adjusted=p;adjusted.origin=s.position;plan=adjusted
            transition(p.shieldFirst ? .shield:.charge,now);trace(String(format:"MOVED %.3f",AnchorRay.distance(p.triggerOrigin,s.position)));return
        }
        let dx=p.origin[0]-s.position[0],dz=p.origin[2]-s.position[2],distance=hypot(dx,dz)
        guard distance>0.02,s.movementUsable,s.movementKeys.count==4 else{recover("已停止 · 站位未能确认",now);return}
        let theta=s.yaw * .pi / 180,f = -sin(theta)*dx+cos(theta)*dz,r = -cos(theta)*dx-sin(theta)*dz
        let limit=max(abs(f),abs(r))*0.45
        var directions:[Int]=[]
        if abs(f)>=limit {directions.append(f>0 ? 0:1)}
        if abs(r)>=limit {directions.append(r>0 ? 3:2)}
        let codes=Set(directions.compactMap{SprintGameConfig.binding(s.movementKeys[$0])})
        let future=[s.position[0]+dx/distance*0.42,s.position[1],s.position[2]+dz/distance*0.42]
        guard !codes.isEmpty,AnchorPlan.walkable(s,from:s.position,to:future,anchor:p.anchor) else{recover("已停止 · 挪位余量不足",now);return}
        pulseUntil=now+0.055;movement(codes)
    }
    private func prepare(_ phase:Phase,plan p:AnchorPlan,state s:AnchorState,now:Double)->Bool {
        if preparedPhase != phase {selectedSlot=nil;preparedPhase=phase}
        let slot=phase == .charge ? p.glowSlot:phase == .shield ? p.shieldSlot:p.detonateSlot
        let item=s.slots.first{$0.slot==slot}
        let expected=phase == .charge ? "minecraft:glowstone":phase == .shield ? p.shieldID:nil
        if let expected,item?.id != expected || (item?.count ?? 0)<1 {recover("已停止 · 材料已变化",now);return false}
        if phase == .detonate,item?.id=="minecraft:glowstone" {recover("已停止 · 引爆物品变化",now);return false}
        if s.selected != slot {
            if selectedSlot != slot,let key=SprintGameConfig.binding(s.keys[slot]) {select(key);selectedSlot=slot;lastAction=now}
        }
        let step=phase == .shield ? p.placements[shieldIndex]:nil
        if step?.support==p.anchor,s.cells[p.anchor]?.charge != 0 {recover("已停止 · 锚已被提前充能",now);return false}
        let target=step?.support ?? p.anchor
        let hitValid=s.hit.map{$0.pos==[target.x,target.y,target.z] && (step==nil || $0.face==step!.face) && $0.point.count==3 && AnchorRay.distance(s.eye,$0.point)<s.range} ?? false
        let aimed:Bool
        if hitValid,pendingAim==nil {aimed=true}
        else {
            guard let ray=AnchorRay.visible(target,state:s,requiredFace:step?.face) else{recover("已停止 · 目标被挡住或超出交互距离",now);return false}
            let dx=ray.point[0]-s.eye[0],dy=ray.point[1]-s.eye[1],dz=ray.point[2]-s.eye[2]
            aimed=aim(yaw:atan2(-dx,dz)*180 / .pi,pitch:-atan2(dy,hypot(dx,dz))*180 / .pi,state:s,now:now)
        }
        return active && aimed && s.selected==slot && s.time>lastAction && hitValid
    }
    private func aim(yaw:Double,pitch:Double,state s:AnchorState,now:Double)->Bool {
        let degrees=pow(s.sensitivity*0.6+0.2,3)*1.2
        if let pending=pendingAim {
            // A render frame may not have consumed the previous relative input.
            // Never apply the same correction twice or click with motion in flight.
            guard abs(F3Pose.angle(s.yaw-pending.0))<max(0.3,degrees),abs(s.pitch-pending.1)<max(0.3,degrees) else {
                if now-lastMove>0.3 {stop("已停止 · 视角移动未确认")};return false
            }
            pendingAim=nil
        }
        let dx=F3Pose.angle(yaw-s.yaw),dy=pitch-s.pitch
        if abs(dx)<=max(0.12,degrees*0.55),abs(dy)<=max(0.12,degrees*0.55) {return true}
        guard now-lastMove>=0.008 else{return false}
        // Bound each relative motion; feedback corrects to the live hit ray.
        let x=Int((max(-96,min(96,dx))/degrees).rounded()),y=Int((max(-64,min(64,dy))/degrees).rounded())
        pendingAim=(F3Pose.angle(s.yaw+Double(x)*degrees),max(-90,min(90,s.pitch+Double(y)*degrees)))
        move(x,y);lastMove=now;return false
    }
}
