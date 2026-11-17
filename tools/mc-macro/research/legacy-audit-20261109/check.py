from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[2]; out=r/'.build/candidates/legacy-audit-20261109';out.mkdir(parents=True,exist_ok=True)
body=r'''
_ = NSApplication.shared
let app=MacroApp()
let pid=NSWorkspace.shared.frontmostApplication!.processIdentifier
app.manualPID=pid;app.gameTelemetry.pid=pid
app.clickObservationSession=app.gameTelemetry.sessionID
app.policy.enabled=true;app.policy.targetActive=true
var failures=0
func check(_ ok:Bool,_ label:String) {if !ok {failures+=1;print("FAIL "+label)}}
func sample(_ age:Double,world:Int=1)->BridgeWorldState {
 let p=F3Pose(x:0,y:64,z:0,yaw:0,pitch:0,time:ProcessInfo.processInfo.systemUptime-age)
 let item=HotbarItem(slot:0,itemID:276,metadata:0,count:1,identity:"sword",kind:"sword",fullBlock:false,score:1)
 let inv=HotbarSnapshot(selected:0,hitKind:"miss",blockID:nil,hardness:nil,target:nil,slots:[item],keys:Array(2...10),blockedKeys:[],age:0)
 return BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,0,0),onGround:true,flying:false,hasBlocks:false,world:world,tick:1,face:nil,solid:[],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62,inventory:inv)
}
func fresh(){app.bridgeWorldPreview=sample(0);app.refreshClickContext()}
fresh();app.leftClickHold.begin(eligible:true)
app.bridgeWorldPreview=sample(0.16);app.refreshClickContext()
check(!app.policy.swordReady && app.clickTimers.isEmpty,"stale sample cannot emit")
check(app.leftClickHold.permitsClicks,"short gap preserves press")
fresh();check(app.policy.swordReady && app.leftClickHold.permitsClicks,"fresh sample resumes same hold")
app.bridgeWorldPreview=nil;app.refreshClickContext();fresh()
check(!app.leftClickHold.permitsClicks,"menu cannot resume previous press")
app.leftClickHold.begin(eligible:true);app.bridgeWorldPreview=sample(0.30);app.refreshClickContext();fresh()
check(!app.leftClickHold.permitsClicks,"long outage requires fresh press")
app.leftClickHold.begin(eligible:true);app.bridgeWorldPreview=sample(0,world:2);app.refreshClickContext()
check(!app.leftClickHold.permitsClicks,"world change cancels")
app.leftClickHold.begin(eligible:false);app.bridgeWorldPreview=sample(0.16,world:2);app.refreshClickContext();fresh()
check(!app.leftClickHold.permitsClicks,"native GUI drag is never adopted")
print("Legacy integration: 7 checks, failures=\(failures); no input posted")
exit(failures==0 ? 0:1)
'''
main=(r/'Sources/main.swift').read_text().split('let app = NSApplication.shared\n')[0]
(out/'main.swift').write_text(main+body)
# Only relax the setter's visibility in a test copy; no socket, event tap or game attach.
(out/'GameTelemetry.swift').write_text((r/'Sources/GameTelemetry.swift').read_text().replace('private(set) var pid:pid_t?','var pid:pid_t?'))
base=['swiftc','-sdk','/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk','-vfsoverlay',str(r/'.build/sdk-overlay.json')]
src=[p for p in (r/'Sources').glob('*.swift') if p.name not in ['main.swift','GameTelemetry.swift','InventoryIntegration.swift']]
for label,inventory in [('before',r/'.build/backups/legacy-audit-20261109/InventoryIntegration.swift'),('after',r/'Sources/InventoryIntegration.swift')]:
 exe=out/label
 subprocess.run(base+list(map(str,src+[inventory,out/'GameTelemetry.swift',out/'main.swift']))+['-o',str(exe)]+sum((['-framework',x] for x in ['AppKit','ApplicationServices','Carbon','IOKit','Vision','ScreenCaptureKit']),[]),check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(out/(label+'.log')).write_text(p.stdout+p.stderr);print(label,p.returncode,p.stdout,flush=True)
 if label=='after':assert p.returncode==0
