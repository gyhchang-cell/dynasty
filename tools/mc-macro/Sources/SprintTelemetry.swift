import Foundation
import Darwin

// Only logical key state is needed for unknown versions. A hold/toggle setting
// alone is insufficient: repeated blind pulses would switch toggle sprint off.
final class SprintTelemetry {
    private(set) var pid:pid_t?
    private(set) var down:Bool?
    private(set) var captured=false,toggle=false
    private(set) var time = -Double.infinity
    private var socketFD:Int32 = -1, reader:DispatchSourceRead?,epoch=0,sequence=0
    private var started=0.0
    var launch:(URL,[String],@escaping(Int32)->Void)->Void = {java,args,done in
        DispatchQueue.global(qos:.utility).async {
            let task=Process();task.executableURL=java;task.arguments=args
            task.standardOutput=FileHandle.nullDevice;task.standardError=FileHandle.nullDevice
            do {try task.run();task.waitUntilExit();done(task.terminationStatus)}catch{done(-1)}
        }
    }
    func stop() {epoch+=1;reader?.cancel();reader=nil;socketFD = -1;pid=nil;down=nil;captured=false;toggle=false;time = -.infinity}
    func expired(now:Double)->Bool {pid != nil && now-max(started,time)>3}
    func start(pid:pid_t,java:URL,classes:String,jar:URL)throws {
        stop();let generation=epoch
        let fd=socket(AF_INET,SOCK_DGRAM,0);guard fd>=0 else{throw POSIXError(.ENOTSOCK)}
        var addr=sockaddr_in();addr.sin_len=UInt8(MemoryLayout<sockaddr_in>.size);addr.sin_family=sa_family_t(AF_INET);addr.sin_addr.s_addr=inet_addr("127.0.0.1")
        let bound=withUnsafePointer(to:&addr){$0.withMemoryRebound(to:sockaddr.self,capacity:1){Darwin.bind(fd,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
        guard bound==0 else{Darwin.close(fd);throw POSIXError(.EADDRINUSE)}
        var len=socklen_t(MemoryLayout<sockaddr_in>.size)
        _=withUnsafeMutablePointer(to:&addr){$0.withMemoryRebound(to:sockaddr.self,capacity:1){getsockname(fd,$0,&len)}}
        _=fcntl(fd,F_SETFL,O_NONBLOCK)
        self.pid=pid;socketFD=fd;sequence=0;started=ProcessInfo.processInfo.systemUptime
        let token=UUID().uuidString
        let source=DispatchSource.makeReadSource(fileDescriptor:fd,queue:.main)
        source.setEventHandler { [weak self] in
            guard let self,self.epoch==generation else{return}
            var bytes=[UInt8](repeating:0,count:256),remote=sockaddr_in()
            while true {
                var size=socklen_t(MemoryLayout<sockaddr_in>.size)
                let count=withUnsafeMutablePointer(to:&remote){$0.withMemoryRebound(to:sockaddr.self,capacity:1){recvfrom(fd,&bytes,bytes.count,0,$0,&size)}}
                guard count>0 else{break}
                let parts=String(decoding:bytes.prefix(count),as:UTF8.self).split(separator:"\t")
                guard remote.sin_addr.s_addr==inet_addr("127.0.0.1"),parts.count==5,parts[0]==token,let seq=Int(parts[1]),seq>self.sequence else{continue}
                self.sequence=seq;self.down=parts[2]=="1" ? true:(parts[2]=="0" ? false:nil);self.captured=parts[3]=="1";self.toggle=parts[4]=="1";self.time=ProcessInfo.processInfo.systemUptime
                token.withCString{buf in _=withUnsafePointer(to:&remote){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(fd,buf,strlen(buf),0,$0,size)}}}
            }
        }
        source.setCancelHandler{Darwin.close(fd)};reader=source;source.resume()
        launch(java,["-Djava.awt.headless=true","--add-modules","jdk.attach","-cp",classes,"local.mcmacro.Attach",String(pid),jar.path,"\(UInt16(bigEndian:addr.sin_port)),\(token)"]) { [weak self] status in
            DispatchQueue.main.async{guard let self,self.epoch==generation,status != 0 else{return};self.stop()}
        }
    }
}
