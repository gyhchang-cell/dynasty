import Foundation
import Darwin
let reader=SprintTelemetry();var checks=0
func check(_ b:Bool,_ label:String){checks+=1;if !b {fatalError(label)}}
var arguments:[String]=[],launcherResult:((Int32)->Void)?
reader.launch={_,args,result in arguments=args;launcherResult=result}
let start=ProcessInfo.processInfo.systemUptime
try reader.start(pid:123,java:URL(fileURLWithPath:"/not-launched"),classes:"unused",jar:URL(fileURLWithPath:"/unused.jar"))
let pair=arguments.last!.split(separator:",");let token=String(pair[1]);let port=UInt16(pair[0])!
check(reader.pid==123 && reader.down==nil,"new session awaits state")
let fd=socket(AF_INET,SOCK_DGRAM,0);defer{Darwin.close(fd)}
var address=sockaddr_in();address.sin_len=UInt8(MemoryLayout<sockaddr_in>.size);address.sin_family=sa_family_t(AF_INET);address.sin_addr.s_addr=inet_addr("127.0.0.1");address.sin_port=port.bigEndian
func send(_ text:String){let bytes=Array(text.utf8);_=bytes.withUnsafeBytes{buf in withUnsafePointer(to:&address){$0.withMemoryRebound(to:sockaddr.self,capacity:1){sendto(fd,buf.baseAddress,bytes.count,0,$0,socklen_t(MemoryLayout<sockaddr_in>.size))}}};RunLoop.main.run(until:Date(timeIntervalSinceNow:0.02))}
send("wrong\t1\t1\t1\t1");check(reader.down==nil,"wrong session ignored")
send(token+"\t1\t1\t1\t1");check(reader.down==true && reader.captured && reader.toggle,"logical toggle and capture state received")
send(token+"\t1\t0\t1\t1");check(reader.down==true,"old sequence rejected")
send(token+"\t2\t0\t0\t0");check(reader.down==false,"cleared game toggle received")
send(token+"\t3\tunknown\t0\t0");check(reader.down==nil,"unsupported registry cannot cause toggle pulses")
check(reader.expired(now:start+4),"stalled session expires")
reader.stop();check(reader.pid==nil && reader.down==nil,"stop invalidates all old state")
try reader.start(pid:456,java:URL(fileURLWithPath:"/unused"),classes:"unused",jar:URL(fileURLWithPath:"/unused.jar"))
launcherResult?(1);RunLoop.main.run(until:Date(timeIntervalSinceNow:0.02));check(reader.pid==nil,"attach failure clears session")
print("Sprint transport checks \(checks), failed 0; loopback only, no game attach")
