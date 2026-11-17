import Foundation
import Darwin

final class ModernTelemetry {
    private let queue=DispatchQueue(label:"local.mc-macro.modern-reader",qos:.userInteractive)
    private var reader:DispatchSourceRead?,descriptor:Int32 = -1,generation=0,sequence=0
    private var watchdog:Timer?,lastPacketAt=0.0,connectedAt=0.0
    private(set) var pid:pid_t?
    private(set) var sessionID=0
    var onState:(AnchorState?,String)->Void={_,_ in}
    // Injectable transport launcher permits a real UDP integration test without
    // attaching to any running game. Production retains the existing local path.
    var launchAttach:(URL,[String],@escaping (Int32?)->Void)->Void = {java,args,completion in
        DispatchQueue.global(qos:.userInitiated).async {
            let task=Process();task.executableURL=java;task.arguments=args
            task.standardOutput=FileHandle.nullDevice;task.standardError=FileHandle.nullDevice
            do {try task.run();task.waitUntilExit();completion(task.terminationStatus)}
            catch {completion(nil)}
        }
    }
    func start(pid:pid_t,resources:URL)throws {
        stop();generation+=1;let epoch=generation
        let directory=resources.appendingPathComponent("modern")
        guard let data=try? Data(contentsOf:directory.appendingPathComponent("runtime.json")),
              let meta=try? JSONSerialization.jsonObject(with:data) as? [String:String],let name=meta["agentJar"],
              name.hasPrefix("modern-agent-"),name.hasSuffix(".jar"),!name.contains("/"),let java=meta["java"],FileManager.default.isExecutableFile(atPath:java) else{throw AnchorFailure(reason:"未找到高版本组件或 Java 25")}
        let fd=socket(AF_INET,SOCK_DGRAM,0);guard fd>=0 else{throw POSIXError(.ENOTSOCK)}
        var address=sockaddr_in();address.sin_len=UInt8(MemoryLayout<sockaddr_in>.size);address.sin_family=sa_family_t(AF_INET);address.sin_addr.s_addr=inet_addr("127.0.0.1")
        let bound=withUnsafePointer(to:&address){$0.withMemoryRebound(to:sockaddr.self,capacity:1){Darwin.bind(fd,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
        guard bound==0 else{Darwin.close(fd);throw POSIXError(.EADDRNOTAVAIL)}
        var length=socklen_t(MemoryLayout<sockaddr_in>.size)
        _=withUnsafeMutablePointer(to:&address){$0.withMemoryRebound(to:sockaddr.self,capacity:1){getsockname(fd,$0,&length)}}
        _=fcntl(fd,F_SETFL,O_NONBLOCK)
        let token=UUID().uuidString,port=UInt16(bigEndian:address.sin_port)
        self.pid=pid;descriptor=fd;sequence=0;sessionID+=1
        connectedAt=ProcessInfo.processInfo.systemUptime;lastPacketAt=connectedAt
        onState(nil,"正在连接游戏数据")
        var savedAt=0.0
        let source=DispatchSource.makeReadSource(fileDescriptor:fd,queue:queue)
        source.setEventHandler { [weak self] in
            var bytes=[UInt8](repeating:0,count:65535),remote=sockaddr_in(),newest:[String:Any]?,peer=sockaddr_in()
            while true {
                var size=socklen_t(MemoryLayout<sockaddr_in>.size)
                let count=withUnsafeMutablePointer(to:&remote){$0.withMemoryRebound(to:sockaddr.self,capacity:1){recvfrom(fd,&bytes,bytes.count,0,$0,&size)}}
                if count<=0 {break}
                guard remote.sin_addr.s_addr==inet_addr("127.0.0.1"),let packet=try? JSONSerialization.jsonObject(with:Data(bytes.prefix(count))) as? [String:Any],packet["token"] as? String==token,
                      let seq=packet["seq"] as? Int,seq>(newest?["seq"] as? Int ?? 0) else{continue}
                newest=packet;peer=remote
            }
            guard let packet=newest else{return}
            token.withCString {buf in _=withUnsafePointer(to:&peer){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(fd,buf,strlen(buf),0,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}}
            let received=ProcessInfo.processInfo.systemUptime
            if received-savedAt>0.1,let path=ProcessInfo.processInfo.environment["MC_ANCHOR_DIAGNOSTIC_PATH"] {
                var diagnostic=packet;diagnostic.removeValue(forKey:"token");diagnostic["received"]=received
                if let data=try? JSONSerialization.data(withJSONObject:diagnostic,options:[.sortedKeys]) {try? data.write(to:URL(fileURLWithPath:path),options:.atomic)}
                savedAt=received
            }
            DispatchQueue.main.async {
                guard let self,self.generation==epoch,let seq=packet["seq"] as? Int,seq>self.sequence else{return}
                self.sequence=seq;self.lastPacketAt=received
                let state=AnchorState.parse(packet,now:received)
                let error=packet["error"] as? String
                self.onState(state,error ?? (state==nil ? (packet["slots"]==nil ? "等待进入世界":"游戏读数格式不匹配") : ""))
            }
        }
        source.setCancelHandler{Darwin.close(fd)};reader=source;source.resume()
        let args=["-Djava.awt.headless=true","--add-modules","jdk.attach","-cp",resources.appendingPathComponent("telemetry/attach").path,"local.mcmacro.Attach",String(pid),directory.appendingPathComponent(name).path,"\(port),\(token)"]
        launchAttach(URL(fileURLWithPath:java),args) { [weak self] status in
            if status != 0 {
                DispatchQueue.main.async { [weak self] in
                    guard let self,self.generation==epoch else{return};self.stop()
                    self.onState(nil,status.map{"游戏组件连接失败（退出码 \($0)）"} ?? "无法启动游戏读数组件")
                }
            }
        }
        let timer=Timer(timeInterval:0.25,repeats:true) { [weak self] _ in
            guard let self,self.generation==epoch else{return}
            let now=ProcessInfo.processInfo.systemUptime
            let expired=self.sequence==0 ? now-self.connectedAt>3 : now-self.lastPacketAt>1
            guard expired else{return}
            let message=self.sequence==0 ? "游戏读数未连接 · 正在重试":"游戏读数中断 · 正在重连"
            self.stop();self.onState(nil,message)
        }
        watchdog=timer;RunLoop.main.add(timer,forMode:.common)
    }
    func stop() {generation+=1;watchdog?.invalidate();watchdog=nil;reader?.cancel();reader=nil;descriptor = -1;pid=nil}
}
