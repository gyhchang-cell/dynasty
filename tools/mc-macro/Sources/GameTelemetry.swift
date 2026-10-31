import Foundation
import Darwin

struct BridgeWorldState {
    let pose: F3Pose
    let renderPose: F3Pose
    let previousPose: F3Pose
    let velocity: (Double,Double,Double) // Blocks per game tick, read from vanilla.
    let onGround: Bool
    let flying: Bool
    let hasBlocks: Bool
    let world: Int
    let tick: Int
    let face: String?
    let solid: Set<F3Block>
    let useHit:F3Block?
    let useFace:String?
    let useDown:Bool
    let clickDelay:Int
    let eyeHeight:Double
    var ticksDue:Int?=nil
    var headYaw:Double?=nil
    var sprinting:Bool?=nil
    var controlDown:Bool?=nil
    var collisionBoxes:[BridgeCollisionBox]?=nil
    var inventory:HotbarSnapshot?=nil
    var hasGeometry:Bool=true
    var obstacles:[BridgeCollisionBox] {collisionBoxes ?? solid.map{BridgeCollisionBox(minX:Double($0.x),minY:Double($0.y),minZ:Double($0.z),maxX:Double($0.x+1),maxY:Double($0.y+1),maxZ:Double($0.z+1))}}
}

struct BridgeCollisionBox {
    let minX:Double,minY:Double,minZ:Double,maxX:Double,maxY:Double,maxZ:Double
    func intersectsBody(from a:F3Pose,to b:F3Pose)->Bool {
        let e=0.00001
        return max(a.x,b.x)+0.30>minX+e && min(a.x,b.x)-0.30<maxX-e &&
            max(a.z,b.z)+0.30>minZ+e && min(a.z,b.z)-0.30<maxZ-e &&
            max(a.y,b.y)+1.80>minY+e && min(a.y,b.y)<maxY-e
    }
}

// Diagnostic samples only. Do not deny the established bridge controller
// on an FPS threshold; the separately tested low-FPS strategy is not shipped.
struct BridgeTiming {
    private var samples:[(time:Double,interval:Double)]=[]
    private var lastTime:Double?
    mutating func observe(_ state:BridgeWorldState) {
        let t=state.pose.time
        if let previous=lastTime,t>previous {
            samples.append((t,t-previous));samples.removeAll{$0.time<t-0.5}
        }
        lastTime=t
    }
    var frameInterval:Double {
        let values=samples.map(\.interval).sorted()
        guard !values.isEmpty else{return 1.0/60}
        return values[min(values.count-1,Int(Double(values.count)*0.9))]
    }
}

enum BridgeClearance {
    static func walkingBlocked(_ state:BridgeWorldState,yaw:Double)->Bool {
        let r=yaw * .pi/180,p=state.pose
        let next=F3Pose(x:p.x+state.velocity.0*2-sin(r)*0.25,y:p.y,z:p.z+state.velocity.2*2+cos(r)*0.25,yaw:yaw,pitch:p.pitch,time:p.time)
        return state.obstacles.contains{$0.intersectsBody(from:p,to:next)}
    }
    static func jumpBlocked(_ state:BridgeWorldState,yaw:Double,rise:Int)->Bool {
        let r=yaw * .pi/180,ux = -sin(r),uz=cos(r)
        var p=state.pose,dx=state.velocity.0+ux*0.2,dz=state.velocity.2+uz*0.2,dy=0.42
        let landingY=p.y+Double(rise)
        for tick in 0..<13 {
            let accel=tick==0 ? 0.1274:0.026
            dx+=ux*accel;dz+=uz*accel
            let next=F3Pose(x:p.x+dx,y:p.y+dy,z:p.z+dz,yaw:yaw,pitch:p.pitch,time:p.time+0.05)
            if state.obstacles.contains(where:{box in
                if box.maxY<=state.pose.y+0.00001 {return false}
                // Landing from above on an allowed-height support is not a
                // head or wall collision. Rising targets may be one higher.
                if dy<0,p.y>=box.maxY-0.00001,box.maxY<=landingY+0.00001 {return false}
                return box.intersectsBody(from:p,to:next)
            }) {return true}
            if dy<0,next.y<=landingY {return false}
            p=next;dx *= tick==0 ? 0.546:0.91;dz *= tick==0 ? 0.546:0.91;dy=(dy-0.08)*0.98
        }
        return false
    }
}

private struct TelemetryPacket: Decodable {
    let token: String
    let seq: Int
    let active: Bool
    let age: Double
    let world: Int?
    let tick: Int?
    let partial: Double?
    let ground: Bool?
    let flying: Bool?
    let blocks: Bool?
    let v: [Double]?
    let hit: [Int]?
    let face: String?
    let solid: [[Int]]?
    let useHit:[Int]?
    let useFace:String?
    let useDown:Bool?
    let clickDelay:Int?
    let eyeHeight:Double?
    let ticksDue:Int?
    let headYaw:Double?
    let sprinting:Bool?
    let controlDown:Bool?
    let collisions:[[Double]]?
    let inventory:OptionalObservation<HotbarSnapshot>?
    let geometry:Bool?
    func state(received: Double) -> BridgeWorldState? {
        guard active, age.isFinite, (0...0.10).contains(age), let v, v.count==11, v.allSatisfy(\.isFinite),
              abs(v[0])<=30_000_000, abs(v[2])<=30_000_000, (-128...4096).contains(v[1]),
              abs(v[7])<=90, let world, let tick, let ground, let flying, let blocks,
              let solid, solid.count<=648, solid.allSatisfy({$0.count==3}),
              let collisions,collisions.count<=2048,collisions.allSatisfy({$0.count==6 && $0.allSatisfy(\.isFinite) && $0[0]<=$0[3] && $0[1]<=$0[4] && $0[2]<=$0[5]}) else {return nil}
        let target=hit.flatMap{$0.count==3 ? F3Block(x:$0[0],y:$0[1],z:$0[2]):nil}
        let t=max(0,min(1,partial ?? 1))
        return BridgeWorldState(pose:F3Pose(x:v[0],y:v[1],z:v[2],yaw:F3Pose.angle(v[6]),pitch:v[7],time:received-age,looking:target),
            renderPose:F3Pose(x:v[8]+(v[0]-v[8])*t,y:v[9]+(v[1]-v[9])*t,z:v[10]+(v[2]-v[10])*t,yaw:F3Pose.angle(v[6]),pitch:v[7],time:received-age,looking:target),
            previousPose:F3Pose(x:v[8],y:v[9],z:v[10],yaw:F3Pose.angle(v[6]),pitch:v[7],time:received-age,looking:target),
            velocity:(v[3],v[4],v[5]),onGround:ground,flying:flying,hasBlocks:blocks,world:world,tick:tick,face:face,
            solid:Set(solid.map{F3Block(x:$0[0],y:$0[1],z:$0[2])}),
            useHit:useHit.flatMap{$0.count==3 ? F3Block(x:$0[0],y:$0[1],z:$0[2]):nil},useFace:useFace,useDown:useDown ?? false,clickDelay:clickDelay ?? 0,eyeHeight:eyeHeight ?? 1.62,ticksDue:ticksDue,headYaw:headYaw.map(F3Pose.angle),sprinting:sprinting,controlDown:controlDown,
            collisionBoxes:collisions.map{BridgeCollisionBox(minX:$0[0],minY:$0[1],minZ:$0[2],maxX:$0[3],maxY:$0[4],maxZ:$0[5])},
            inventory:inventory?.value.flatMap{$0.valid ? $0:nil},hasGeometry:geometry ?? true)
    }
}

// Authenticated loopback datagrams only; no external network, state files, or
// screenshots. The Java component stops three seconds after the reader exits.
final class GameTelemetry {
    struct Runtime {
        let java:String,classes:String,jar:String
        static func locate(resources:URL)->Runtime? {
            let directory=resources.appendingPathComponent("telemetry")
            guard let data=try? Data(contentsOf:directory.appendingPathComponent("runtime.json")),
                  let manifest=try? JSONSerialization.jsonObject(with:data) as? [String:String],
                  let name=manifest["agentJar"],name.hasPrefix("state-agent-"),name.hasSuffix(".jar"),!name.contains("/") else{return nil}
            for version in ["21","17","11","9"] {
                let task=Process(),pipe=Pipe()
                task.executableURL=URL(fileURLWithPath:"/usr/libexec/java_home");task.arguments=["-v",version]
                task.standardOutput=pipe;task.standardError=FileHandle.nullDevice
                guard (try? task.run()) != nil else{continue}
                task.waitUntilExit()
                let home=String(decoding:pipe.fileHandleForReading.readDataToEndOfFile(),as:UTF8.self).trimmingCharacters(in:.whitespacesAndNewlines)
                let java=home+"/bin/java"
                if task.terminationStatus==0,FileManager.default.isExecutableFile(atPath:java) {
                    return Runtime(java:java,classes:directory.appendingPathComponent("attach").path,jar:directory.appendingPathComponent(name).path)
                }
            }
            return nil
        }
    }
    private let attachQueue=DispatchQueue(label:"local.mc-macro.attach",qos:.userInitiated)

    private let queue=DispatchQueue(label:"local.mc-macro.telemetry",qos:.userInteractive)
    private var reader: DispatchSourceRead?
    private var descriptor:Int32 = -1
    private var peer: sockaddr_in?
    private var token=""
    private var sequence=0
    private var generation=0
    var sessionID:Int {generation}
    private(set) var pid:pid_t?
    var needsGeometry=true
    var onState: (BridgeWorldState?,String)->Void = {_,_ in}

    func start(pid:pid_t,java:String,classes:String,jar:String) throws {
        stop();generation+=1
        let epoch=generation
        let fd=socket(AF_INET,SOCK_DGRAM,0)
        guard fd>=0 else {throw POSIXError(.ENOTSOCK)}
        var address=sockaddr_in();address.sin_len=UInt8(MemoryLayout<sockaddr_in>.size);address.sin_family=sa_family_t(AF_INET)
        address.sin_addr.s_addr=inet_addr("127.0.0.1")
        let bound=withUnsafePointer(to:&address){$0.withMemoryRebound(to:sockaddr.self,capacity:1){Darwin.bind(fd,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
        guard bound==0 else {Darwin.close(fd);throw POSIXError(.EADDRNOTAVAIL)}
        var length=socklen_t(MemoryLayout<sockaddr_in>.size)
        _=withUnsafeMutablePointer(to:&address){$0.withMemoryRebound(to:sockaddr.self,capacity:1){getsockname(fd,$0,&length)}}
        _=fcntl(fd,F_SETFL,O_NONBLOCK)
        self.pid=pid;descriptor=fd;sequence=0;token=UUID().uuidString
        let sessionToken=token, port=UInt16(bigEndian:address.sin_port)
        let source=DispatchSource.makeReadSource(fileDescriptor:fd,queue:queue)
        source.setEventHandler { [weak self] in
            var newest:TelemetryPacket?,newestPeer=sockaddr_in(),remote=sockaddr_in()
            var bytes=[UInt8](repeating:0,count:65535)
            while true {
                var size=socklen_t(MemoryLayout<sockaddr_in>.size)
                let count=withUnsafeMutablePointer(to:&remote){ptr in ptr.withMemoryRebound(to:sockaddr.self,capacity:1){recvfrom(fd,&bytes,bytes.count,0,$0,&size)}}
                if count<=0 {break}
                guard remote.sin_addr.s_addr==inet_addr("127.0.0.1"),
                    let packet=try? JSONDecoder().decode(TelemetryPacket.self,from:Data(bytes.prefix(count))),packet.token==sessionToken else {continue}
                if packet.seq > (newest?.seq ?? 0) { newest=packet;newestPeer=remote }
            }
            guard let packet=newest else {return}
            let received=ProcessInfo.processInfo.systemUptime
            let authenticatedPeer=newestPeer
            DispatchQueue.main.async {
                guard let self,self.generation==epoch,packet.seq>self.sequence else {return}
                self.sequence=packet.seq;self.peer=authenticatedPeer
                var peer=authenticatedPeer
                (sessionToken+(self.needsGeometry ? " FULL":" LIGHT")).withCString {bytes in
                    _=withUnsafePointer(to:&peer){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(fd,bytes,strlen(bytes),0,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
                }
                let state=packet.state(received:received)
                self.onState(state,state==nil ? "游戏菜单、角色状态或读数不可用。":"")
            }
        }
        source.setCancelHandler {Darwin.close(fd)}
        reader=source;source.resume()
        attachQueue.async { [weak self] in
            guard DispatchQueue.main.sync(execute:{self?.generation==epoch}) else{return}
            let command=Process();command.executableURL=URL(fileURLWithPath:java)
            command.arguments=["-Djava.awt.headless=true","--add-modules","jdk.attach","-cp",classes,"local.mcmacro.Attach",String(pid),jar,"\(port),\(sessionToken)"]
            command.standardOutput=FileHandle.nullDevice;command.standardError=FileHandle.nullDevice
            do {try command.run();command.waitUntilExit()}
            catch {DispatchQueue.main.async {guard let self,self.generation==epoch else{return};self.onState(nil,"本地读数组件未启动。")}}
            // Only authenticated state confirms attachment. In particular, a JDK
            // 21 attaching to JRE 8 can report code 0 as an AgentLoadException.
            DispatchQueue.main.asyncAfter(deadline:.now()+2) {
                guard let self,self.generation==epoch,self.sequence==0 else{return}
                self.stop();self.onState(nil,"未收到游戏读数，已停止连接。")
            }
        }
    }
    func stop() {
        generation+=1
        if descriptor>=0,var peer {
            ("STOP "+token).withCString { bytes in
                _=withUnsafePointer(to:&peer){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(descriptor,bytes,strlen(bytes),0,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
            }
        }
        reader?.cancel();reader=nil;descriptor = -1;peer=nil;pid=nil
    }
}

// Vanilla airborne integration, used only to choose a conservative landing
// target. Actual block occupancy and onGround still confirm every landing.
struct BridgeLandingForecast {
    let x:Double,z:Double,supportX:Double,supportZ:Double,seconds:Double
    static func standingSupport(_ state:BridgeWorldState,floor:Int)->Set<F3Block> {
        guard state.onGround,abs(state.pose.y-Double(floor+1))<0.03 else {return []}
        return state.solid.filter {
            $0.y==floor && state.pose.x+0.299999>Double($0.x) && state.pose.x-0.299999<Double($0.x)+1 &&
            state.pose.z+0.299999>Double($0.z) && state.pose.z-0.299999<Double($0.z)+1
        }
    }
    func imminentSupport(_ state:BridgeWorldState,floor:Int)->Set<F3Block> {
        guard seconds>0,seconds<=0.051 else {return []}
        return state.solid.filter {
            $0.y==floor && supportX+0.299999>Double($0.x) && supportX-0.299999<Double($0.x)+1 &&
            supportZ+0.299999>Double($0.z) && supportZ-0.299999<Double($0.z)+1
        }
    }
    // Native clicks are consumed on game ticks, and the resulting solid block
    // is observed afterwards. A CPS interval alone is not the available flight
    // budget: leave time for confirmation and the camera's forward return.
    func needsCoast(remainingCells:Int,cps:Double,returnTime:Double)->Bool {
        guard remainingCells>0 else{return false}
        return Double(remainingCells)/max(1,cps)+0.10+returnTime>=seconds
    }
    static func predict(_ state:BridgeWorldState,height:Double,yaw:Double,acceleration:Double=0.02)->BridgeLandingForecast? {
        if state.onGround,abs(state.pose.y-height)<0.03 {return BridgeLandingForecast(x:state.pose.x,z:state.pose.z,supportX:state.previousPose.x,supportZ:state.previousPose.z,seconds:0)}
        var x=state.pose.x,y=state.pose.y,z=state.pose.z
        var dx=state.velocity.0,dy=state.velocity.1,dz=state.velocity.2
        let r=yaw * .pi/180
        for step in 1...20 {
            dx += -sin(r)*acceleration;dz += cos(r)*acceleration
            let collisionX=x,collisionZ=z
            x+=dx;z+=dz
            let nextY=y+dy
            if dy<0,y>=height,nextY<=height {return BridgeLandingForecast(x:x,z:z,supportX:collisionX,supportZ:collisionZ,seconds:Double(step)*0.05)}
            y=nextY;dx*=0.91;dz*=0.91;dy=(dy-0.08)*0.98
        }
        return nil
    }
}

// Correct only the cross-track component of a short coasting landing.
// Candidate blocks may include an in-flight placement plan; the controller
// still requires observed solid support before declaring a landing or return.
enum BridgeLateralLanding {
    static func direction(_ state:BridgeWorldState,floor:Int,heading:Double,targets:Set<F3Block>)->Double? {
        guard !state.onGround,let coast=BridgeLandingForecast.predict(state,height:Double(floor+1),yaw:heading,acceleration:0),coast.seconds>0,coast.seconds<=0.201 else{return nil}
        func margin(_ forecast:BridgeLandingForecast,_ b:F3Block)->Double {
            min(forecast.x-Double(b.x)+0.28,Double(b.x+1)+0.28-forecast.x,
                forecast.z-Double(b.z)+0.28,Double(b.z+1)+0.28-forecast.z)
        }
        let targets=targets.filter{$0.y==floor}
        guard !targets.contains(where:{margin(coast,$0)>=0}) else{return nil}
        var best:(yaw:Double,margin:Double)?
        for yaw in [heading-90,heading+90] {
            guard let forecast=BridgeLandingForecast.predict(state,height:Double(floor+1),yaw:yaw,acceleration:0.02) else{continue}
            for b in targets where margin(forecast,b)>=0.005 {
                let m=margin(forecast,b)
                if best==nil || m>best!.margin {best=(yaw,m)}
            }
        }
        return best?.yaw
    }
}
