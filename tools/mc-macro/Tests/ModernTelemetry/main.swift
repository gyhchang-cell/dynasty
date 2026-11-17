import Foundation
import Darwin

var checks=0,failures=0
func check(_ value:Bool,_ label:String) {checks+=1;if !value {failures+=1;print("FAIL "+label)}}
func pump(_ seconds:Double) {
    let until=Date().addingTimeInterval(seconds)
    while Date()<until {RunLoop.main.run(until:min(until,Date().addingTimeInterval(0.01)))}
}
let fixture=try! JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1]))) as! [String:Any]
let resources=URL(fileURLWithPath:CommandLine.arguments[2])
let peer=socket(AF_INET,SOCK_DGRAM,0)
guard peer>=0 else{fatalError("test socket")}
var local=sockaddr_in();local.sin_len=UInt8(MemoryLayout<sockaddr_in>.size);local.sin_family=sa_family_t(AF_INET);local.sin_addr.s_addr=inet_addr("127.0.0.1")
let bound=withUnsafePointer(to:&local){$0.withMemoryRebound(to:sockaddr.self,capacity:1){Darwin.bind(peer,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
guard bound==0 else{fatalError("test bind")}
var endpoint=sockaddr_in(),token="",launches=0
var callbacks:[(Int32?)->Void]=[]
let reader=ModernTelemetry()
reader.launchAttach={_,args,completion in
    launches+=1;callbacks.append(completion)
    let values=args.last!.split(separator:",");token=String(values[1])
    endpoint=sockaddr_in();endpoint.sin_len=UInt8(MemoryLayout<sockaddr_in>.size)
    endpoint.sin_family=sa_family_t(AF_INET);endpoint.sin_addr.s_addr=inet_addr("127.0.0.1")
    endpoint.sin_port=UInt16(values[0])!.bigEndian
    completion(0)
}
var received:[AnchorState]=[],messages:[String]=[]
reader.onState={state,message in if let state {received.append(state)};messages.append(message)}
func send(_ sequence:Int,token override:String?=nil,endpoint address:sockaddr_in?=nil,changes:[String:Any]=[:]) {
    var packet=fixture;packet["active"]=true;packet["age"]=0.0;packet["token"]=override ?? token;packet["seq"]=sequence
    for (key,value) in changes {packet[key]=value}
    let data=try! JSONSerialization.data(withJSONObject:packet)
    var destination=address ?? endpoint
    let sent=data.withUnsafeBytes {bytes in
        withUnsafePointer(to:&destination){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(peer,bytes.baseAddress,data.count,0,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}
    }
    check(sent==data.count,"test datagram sent")
    pump(0.07)
}
try! reader.start(pid:12345,resources:resources)
let session1=reader.sessionID,token1=token
check(launches==1 && reader.pid==12345,"launches injected test transport, not Java")
send(1,token:"wrong-session")
check(received.isEmpty,"unauthenticated packet rejected")
send(1)
check(received.count==1,"valid first packet delivered")
send(1)
check(received.count==1,"duplicate sequence rejected")
send(2,changes:["active":false])
check(received.last?.active==false,"menu observation arrives without enabling gameplay")
send(3,changes:["age":0.8])
check(received.count==2 && messages.last?.contains("格式") == true,"expired observation cannot become a fresh sword")
send(4)
check(received.count==3,"fresh read recovers without restarting a valid session")
pump(1.35)
check(reader.pid==nil && messages.last?.contains("中断")==true,"stream stops after silence even after a successful first packet")
try! reader.start(pid:12345,resources:resources)
check(reader.sessionID>session1,"reconnection has a new identity")
let before=received.count
send(100,token:token1)
check(received.count==before,"old session packet cannot poison reconnected state")
send(1)
check(received.count==before+1,"new session sequence can restart at one")
callbacks[0](1);pump(0.05)
check(reader.pid==12345,"old attach completion cannot tear down new session")
reader.stop();pump(1.35)
check(reader.pid==nil,"explicit stop cancels watchdog")
reader.launchAttach={_,_,done in launches+=1;done(1)}
try! reader.start(pid:12345,resources:resources);pump(0.05)
check(reader.pid==nil && messages.last?.contains("退出码 1")==true,"attach nonzero exit surfaces immediately")
reader.launchAttach={_,_,done in launches+=1;done(nil)}
try! reader.start(pid:12345,resources:resources);pump(0.05)
check(reader.pid==nil && messages.last?.contains("无法启动")==true,"launcher failure surfaces immediately")
reader.launchAttach={_,_,done in launches+=1;done(0)}
try! reader.start(pid:12345,resources:resources);pump(3.3)
check(reader.pid==nil && messages.last?.contains("未连接")==true,"initial connection timeout remains bounded")
reader.stop();Darwin.close(peer)
print("Modern telemetry integration: \(checks) checks, \(failures) failures; local test UDP only, no game attach")
exit(failures==0 ? 0:1)