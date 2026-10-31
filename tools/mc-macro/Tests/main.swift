import Foundation

func check(_ condition: @autoclosure () -> Bool, _ message: String) {
    guard condition() else { fatalError(message) }
}
var p = MacroPolicy()
p.physicalLeftHeld = true
p.targetActive = true
check(!p.mayClick, "关闭时不能点击")
p.enabled = true
check(p.mayClick, "启用且游戏前台且按住时应点击")
p.targetActive = false
check(!p.mayClick, "游戏失焦不能点击")
p.targetActive = true
p.physicalLeftHeld = false
check(!p.mayClick, "松手不能点击")
p.physicalLeftHeld = true
p.physicalRightHeld = true
check(p.mayClick(.left) && p.mayClick(.right), "双键同时按住应同时连点")
check(!p.mayClick(.left, hardwareDown: false) && !p.mayClick(.right, hardwareDown: false), "硬件松手时即使旧状态仍为按住，也绝不能继续点击")
check(p.mayClick(.left, hardwareDown: true) && p.mayClick(.right, hardwareDown: true), "真实按住才允许双键点击")
p.physicalLeftHeld = false
check(!p.mayClick(.left) && p.mayClick(.right), "松开左键不应影响右键")
p.physicalLeftHeld = true
p.physicalRightHeld = false
check(p.mayClick(.left) && !p.mayClick(.right), "松开右键不应影响左键")
p.physicalRightHeld = true
p.targetActive = false
check(!p.mayClick(.left) && !p.mayClick(.right), "失焦应停止双键")
p.targetActive = true
p.stop()
check(!p.enabled && !p.physicalLeftHeld && !p.physicalRightHeld && !p.mayClick(.left) && !p.mayClick(.right), "停止必须清除双键状态")
p.enabled = true
p.physicalLeftHeld = true
p.suspend()
check(p.enabled && !p.physicalLeftHeld && !p.physicalRightHeld, "暂停仅释放按住状态，不能关闭总开关")
p.targetActive = true
p.physicalLeftHeld = true
p.menuPaused = true
check(!p.mayClick(.left, hardwareDown: true), "聊天背包期间禁止连点")
p.menuPaused = false
check(p.enabled && p.mayClick(.left, hardwareDown: true), "关闭菜单后恢复，不能要求重新开总开关")
p.stop()
check(!p.enabled, "手动关闭才关闭总开关")
p.enabled = true
p.targetActive = true
p.reconcileHardware(left: true, right: true)
p.suspend()
check(p.enabled && !p.mayClick(.left), "加载中释放输入但保留总开关")
p.reconcileHardware(left: true, right: true)
check(p.mayClick(.left) && p.mayClick(.right), "加载后仍真实按住双键时恢复，无需重新切换开关")
p.reconcileHardware(left: false, right: false)
check(p.enabled && !p.mayClick(.left) && !p.mayClick(.right), "恢复后鼠标松开不能点击")
p.stop()
p.reconcileHardware(left: true, right: true)
check(!p.enabled && !p.mayClick(.left) && !p.mayClick(.right), "手动关闭后硬件按住也不能重开")
// Model the game ignoring repeated downs after its input binding was cleared.
var renewal = SprintRenewal()
check(renewal.advance(now: 100) == nil, "未启用疾跑时不能发事件")
renewal.begin(now: 0)
var cachedDown = true
var gameBindingDown = false // World change / respawn clears the binding.
var recovered = 0
var recoveredAtReset = 0
for tick in 1...8000 {
    let now = Double(tick) * 0.025
    if tick % 120 == 0 { gameBindingDown = false; recoveredAtReset = recovered }
    if let down = renewal.advance(now: now) {
        if down != cachedDown {
            cachedDown = down
            gameBindingDown = down
            if down { recovered += 1 }
        }
    }
    // Every reset must recover within one renewal cycle, without toggling mode.
    if tick % 120 == 44 { check(recovered > recoveredAtReset, "游戏重置按键后需自动恢复疾跑") }
}
check(recovered > 150, "长时间运行必须持续生成新的疾跑按下边沿")
renewal = SprintRenewal()
check(!renewal.isDown && renewal.advance(now: 999) == nil, "停止后不能补发待执行的按下")
renewal.begin(now: 1000)
check(renewal.isDown && renewal.advance(now: 1000.5) == nil, "重新进入游戏后应立即按下并重新计时")
check(renewal.advance(now: 1001) == false, "恢复周期必须先松开")
check(renewal.advance(now: 1001.05) == nil, "松开和按下之间必须保留可观察间隔")
check(renewal.advance(now: 1001.1) == true, "松开后必须重新按下")
struct RhythmTestRandom: RandomNumberGenerator {
    var state: UInt64
    mutating func next() -> UInt64 {
        state &+= 0x9e3779b97f4a7c15
        var z = state
        z = (z ^ (z >> 30)) &* 0xbf58476d1ce4e5b9
        z = (z ^ (z >> 27)) &* 0x94d049bb133111eb
        return z ^ (z >> 31)
    }
}
var rng = RhythmTestRandom(state: 12345)
var rhythm = ClickRhythm()
var duration = 0.0
var priorCPS = 19.0
var sumProduct = 0.0
var sumSquare = 0.0
var shortestHold = 1.0
var longestHold = 0.0
for _ in 0..<100000 {
    let beat = rhythm.next(minimum: 18, maximum: 20, using: &rng)
    check(beat.interval >= 1.0 / 20 && beat.interval <= 1.0 / 18, "节奏变化不能超出所设 CPS 区间")
    check(beat.held > 0 && beat.held < beat.interval, "每周期必须既有按下也有释放阶段")
    duration += beat.interval
    let cps = 1 / beat.interval
    sumProduct += (priorCPS - 19) * (cps - 19)
    sumSquare += (cps - 19) * (cps - 19)
    priorCPS = cps
    shortestHold = min(shortestHold, beat.held)
    longestHold = max(longestHold, beat.held)
}
check(100000 / duration >= 18.9 && 100000 / duration <= 19.1, "长期平均不能因节奏算法而掉速")
check(sumProduct / sumSquare > 0.6, "相邻周期应有连续变化，不能仍是独立随机抽样")
check(longestHold > shortestHold * 1.5, "按下时长应有变化")
for range in [(1.0, 40.0), (15.0, 20.0), (39.0, 40.0), (18.0, 18.0)] {
    for _ in 0..<10000 {
        let beat = rhythm.next(minimum: range.0, maximum: range.1, using: &rng)
        check(beat.interval >= 1 / range.1 && beat.interval <= 1 / range.0, "所有合法范围均不能越界或插入停顿")
        if range.0 == range.1 { check(beat.interval == 1 / range.0, "固定 CPS 时必须保留固定间隔") }
    }
}
print(String(format: "节奏验证：100000 次计划点击平均 %.3f CPS，相邻周期相关系数 %.3f；另通过 40000 次边界测试。", 100000 / duration, sumProduct / sumSquare))
let ctrlDown = SprintModifier.flags(0, down: true)
check(ctrlDown & SprintModifier.leftControl != 0, "LWJGL 2 必须能识别左 Control 专用位")
check(ctrlDown & SprintModifier.genericControl != 0, "必须保留系统通用 Control 标记")
check(SprintModifier.flags(ctrlDown, down: false) == 0, "释放时清除左 Control 和通用标记")
let rightHeld = SprintModifier.genericControl | SprintModifier.rightControl
check(SprintModifier.flags(SprintModifier.flags(rightHeld, down: true), down: false) == rightHeld, "释放左 Control 不能清除右 Control")
check(SprintModifier.flags(1 << 17, down: true) & (1 << 17) != 0, "保留其他修饰键")
check(MacroPolicy.validRange(15, 20), "默认范围")
check(MacroPolicy.validRange(18, 18), "固定 CPS")
check(!MacroPolicy.validRange(20, 15), "拒绝倒置范围")
check(!MacroPolicy.validRange(.nan, 20), "拒绝 NaN")
check(!MacroPolicy.validRange(0, 20), "拒绝零值")
check(!MacroPolicy.validRange(15, .infinity), "拒绝无穷")
check(abs(MacroPolicy.interval(cps: 20) - 0.05) < 0.000001, "20 CPS 间隔")
check(!MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java -jar editor.jar"), "其他 Java 程序不能误认")
check(!MacroPolicy.looksLikeMinecraft(name: "Minecraft Launcher", bundle: "com.mojang.minecraftlauncher", command: ""), "启动器不能误认")
check(MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java net.minecraft.client.main.Main"), "原版检测")
check(MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java net.fabricmc.loader.impl.launch.knot.KnotClient"), "Fabric 检测")
print("通过：按住才点击、暂停保留总开关、菜单恢复、疾跑重触发与长期恢复、LWJGL 左 Control 标记及释放、CPS 校验、游戏识别。")

let f3Text = "Minecraft 1.8.9\nXYZ: -123.450 / 64.000 / 987.625\nFacing: north (Towards negative Z) (-179.9 / 72.0)"
let parsed = F3Pose.parse(f3Text, time: 10)!
check(parsed.x == -123.45 && parsed.y == 64 && parsed.z == 987.625 && parsed.yaw == -179.9 && parsed.pitch == 72, "F3 坐标与朝向必须准确解析")
check(F3Pose.parse(f3Text.replacingOccurrences(of: ".", with: ","), time: 10)?.x == -123.45, "支持小数逗号")
check(F3Pose.parse(f3Text + "\nRespawn", time: 10) == nil, "死亡菜单不得继续读取为可执行状态")
check(F3Pose.parse(f3Text.replacingOccurrences(of: "64.000", with: "99999.000"), time: 10) == nil, "异常坐标必须拒绝")
check(F3Pose.parse("XYZ: 1 / 2 / 3", time: 10) == nil, "缺少朝向不能补造读数")
check(F3Pose.angle(-359) == 1 && F3Pose.angle(359) == -1, "角度越过正负180需取短路径")
let optionText = "mouseSensitivity:0.74647886\ninvertYMouse:false\nkey_key.forward:17\nkey_key.back:31\nkey_key.jump:57\nkey_key.sprint:29"
let gameConfig = TellyGameConfig.parse(optionText, path: "/fixture/options.txt")!
check(gameConfig.forward == 13 && gameConfig.back == 1 && gameConfig.jump == 49 && gameConfig.sprint == 59, "自动读取游戏实际键位")
check(TellyGameConfig.parse(optionText.replacingOccurrences(of: "key_key.sprint:29", with: "key_key.sprint:19"), path: "") == nil, "R 疾跑键冲突时禁止开始搭路")
check(TellyGameConfig.gameDirectory(command: "java Main --gameDir /Users/test/My Minecraft --assetsDir /assets") == "/Users/test/My Minecraft", "支持带空格的游戏目录")
var tracking = F3Track()
check(tracking.accept(parsed, now: 10.1), "新读数可用")
check(tracking.fresh(now: 10.3) == nil, "过期读数必须失效")
check(!tracking.accept(F3Pose(x:10000,y:64,z:0,yaw:0,pitch:0,time:10.1),now:10.2), "传送或OCR跳变必须拒绝")
var bridge = TellyController()
bridge.config = gameConfig
bridge.prepareRunup = false
var bridgeEvents: [(UInt16,Bool)] = []
var bridgeMoves: [(Int64,Int64)] = []
bridge.key = { bridgeEvents.append(($0,$1)) }
bridge.move = { bridgeMoves.append(($0,$1)) }
func supply(_ y: Double = 64, yaw: Double = 0, pitch: Double = 0, looking: F3Block? = nil, at: Double) {
    bridge.observe(F3Pose(x:0.5,y:y,z:0.5,yaw:yaw,pitch:pitch,time:at,looking:looking),error:"",now:at+0.01)
    bridge.tick(now:at+0.01,active:true,minimum:15,maximum:18)
}
bridge.press(now:0)
supply(at:0.1); supply(at:0.2); supply(at:0.3)
check(bridge.phase == .calibrating && bridgeEvents.isEmpty && bridgeMoves.count == 1, "原地校准前不能产生移动输入")
bridge.observe(nil,error:"F3失效",now:0.4)
check(bridge.phase == .idle && bridgeEvents.isEmpty, "校准时F3失效必须停止")
bridge.release(); bridge.press(now:1)
supply(at:1.1); supply(at:1.2); supply(at:1.3); supply(yaw:8,pitch:5,at:1.4)
check(bridge.phase == .probing && bridgeEvents.isEmpty, "校准后先确认起点方块")
supply(yaw:0,pitch:88,looking:F3Block(x:0,y:63,z:0),at:1.45); supply(at:1.5)
check(bridge.phase == .takeoff && bridgeEvents.contains(where:{$0.0 == 49 && $0.1}), "朝向确认后才能起跳")
bridge.release()
for code in Set(bridgeEvents.filter{$0.1}.map{$0.0}) {
    check(bridgeEvents.last(where:{$0.0 == code})?.1 == false,"R松手必须释放每个代按键")
}
let afterRelease = bridgeEvents.count
bridge.tick(now:1.6,active:true,minimum:15,maximum:18)
check(bridgeEvents.count == afterRelease,"R松手后不得继续产生输入")
bridge.press(now:2)
supply(at:2.1); supply(at:2.2); supply(at:2.3); supply(yaw:8,pitch:5,at:2.4); supply(yaw:0,pitch:88,looking:F3Block(x:0,y:63,z:0),at:2.45); supply(at:2.5)
bridge.tick(now:2.51,active:false,minimum:15,maximum:18)
check(bridge.phase == .idle && bridgeEvents.last(where:{$0.0 == gameConfig.forward})?.1 == false,"失焦必须释放按键")
bridge.release(); bridge.press(now:3)
supply(at:3.1); supply(at:3.2); supply(at:3.3); supply(yaw:8,pitch:5,at:3.4); supply(yaw:0,pitch:88,looking:F3Block(x:0,y:63,z:0),at:3.45); supply(at:3.5)
bridge.tick(now:3.8,active:true,minimum:15,maximum:18)
check(bridge.phase == .idle,"无新读数超过250毫秒必须停止")
print("通过：F3解析、自动配置、坐标跳变/过期拒绝、原地校准门槛、R松手与失焦释放。")

check(F3Pose.parse(f3Text + "\nLooking at: -124 63 986", time:10)?.looking == F3Block(x:-124,y:63,z:986),"读取准星实际方块坐标")
for yaw in stride(from:-180.0,to:180.0,by:5) {
    let route=TellyRoute(x:0.95,z:0.95,yaw:yaw)
    var block=F3Block(x:0,y:63,z:0)
    for _ in 0..<40 {
        let step=route.next(after:block)
        check(abs(step.result.x-block.x)+abs(step.result.z-block.z)==1 && step.result.y==63,"斜向路线必须保持面连接，不能跳过角落")
        check(route.along(Double(step.result.x)+0.5,Double(step.result.z)+0.5)>route.along(Double(block.x)+0.5,Double(block.z)+0.5),"每一步必须沿原始视线向前")
        check(step.x>=Double(block.x) && step.x<=Double(block.x)+1 && step.z>=Double(block.z) && step.z<=Double(block.z)+1,"瞄准点必须位于真实方块表面")
        block=step.result
    }
}
let side=TellyRoute(x:0.5,z:0.5,yaw:0).next(after:F3Block(x:0,y:63,z:0))
check(side.isVisibleFace(from:F3Pose(x:0.5,y:64,z:2,yaw:180,pitch:60,time:0)),"侧面射线应允许向前放块")
check(!side.isVisibleFace(from:F3Pose(x:0.5,y:64,z:1.2,yaw:180,pitch:80,time:0)),"打到顶部的射线不能误判为向前放块")
for (x,z,yaw) in [(0.5,0.5,0.0),(0.5,0.99,33.0),(0.99,0.99,45.0),(1.15,1.15,135.0),(-0.02,-0.02,-37.0)] {
    let test=TellyController(); test.config=gameConfig; test.prepareRunup=false
    let block=F3Block(x:x<0 ? -1:0,y:63,z:z<0 ? -1:0)
    var viewYaw=yaw, viewPitch=0.0, jumped=false
    test.move = { dx,dy in viewYaw=F3Pose.angle(viewYaw+Double(dx)*gameConfig.degreesPerCount);viewPitch=max(-90,min(90,viewPitch+Double(dy)*gameConfig.degreesPerCount)) }
    test.key = { code,down in if code==gameConfig.jump && down { jumped=true } }
    test.press(now:10)
    for i in 1...180 {
        let time=10+Double(i)*0.025
        var pose=F3Pose(x:x,y:64,z:z,yaw:viewYaw,pitch:viewPitch,time:time)
        let top=TellyPlacement(support:block,result:F3Block(x:block.x,y:64,z:block.z),axis:1,sign:1,x:Double(block.x)+0.5,y:64,z:Double(block.z)+0.5)
        if top.isVisibleFace(from:pose) { pose.looking=block }
        test.observe(pose,error:"",now:time+0.005)
        test.tick(now:time+0.005,active:true,minimum:15,maximum:18)
        if jumped { break }
    }
    check(jumped,"中心、边缘、角落、悬边和斜视角必须找到脚下支撑后起跳：\(x),\(z),\(yaw)：\(test.message)")
    test.release()
}
print("通过：72个朝向的2880段面连接路线、侧面/顶面射线区分、中心/边缘/角落/悬边起点校准。")

for (x,y) in [(Int64(554),Int64(216)),(-554,-216),(554,-216),(3,1),(0,216)] {
    var curve=RelativeMouseTurn(x:x,y:y,start:0,duration:0.068)
    var sumX:Int64=0,sumY:Int64=0,largest:Int64=0
    for i in 0...12 {
        let step=curve.advance(now:Double(i)*0.008)
        sumX+=step.x;sumY+=step.y;largest=max(largest,abs(step.x))
        check(step.x*x>=0 && step.y*y>=0,"平滑转向不能反向抖动")
    }
    check(sumX==x && sumY==y,"曲线终点必须精确累加到校准计数")
    if abs(x)>100 {check(largest<abs(x)/2,"回头必须分为连续位移，不能单次跳角度")}
    let end=curve.advance(now:1)
    check(end.x==0 && end.y==0 && end.finished,"曲线结束后不得补发移动")
}
let cancelled=TellyController();cancelled.config=gameConfig
var curveMoves=0,cancellations=0
cancelled.move={_,_ in curveMoves+=1};cancelled.cancelPendingInput={cancellations+=1}
cancelled.press(now:20)
for t in [20.1,20.2,20.3] {
    cancelled.observe(F3Pose(x:0.5,y:64,z:0.5,yaw:0,pitch:0,time:t),error:"",now:t)
    cancelled.tick(now:t,active:true,minimum:15,maximum:18)
}
let phaseBeforeRepeat=cancelled.phase,movesBeforeRepeat=curveMoves
cancelled.press(now:20.31)
check(cancelled.phase==phaseBeforeRepeat && curveMoves==movesBeforeRepeat,"重复R按下不能创建第二轮任务")
for t in [20.4,20.41,20.42,20.43] {
    cancelled.observe(F3Pose(x:0.5,y:64,z:0.5,yaw:8,pitch:5,time:t),error:"",now:t)
    cancelled.tick(now:t,active:true,minimum:15,maximum:18)
}
check(curveMoves>movesBeforeRepeat,"停止测试必须覆盖正在进行的转向")
cancelled.release();let stoppedMoves=curveMoves
for i in 1...30 {cancelled.tick(now:20.43+Double(i)*0.01,active:true,minimum:15,maximum:18)}
check(curveMoves==stoppedMoves && cancellations>0,"R松手立即取消尚未发出的转向并使输入队列失效")
let inputEpoch=BridgeInputEpoch(),oldEpoch=inputEpoch.snapshot()
inputEpoch.invalidate()
check(!inputEpoch.accepts(oldEpoch) && inputEpoch.accepts(inputEpoch.snapshot()),"停止后拒绝旧任务排队输入，新任务独立")
print("通过：同步双轴平滑转向、计数精确终点、R重复抑制、转向中松手取消、旧输入队列作废。")

var quantized=F3Track()
check(quantized.accept(F3Pose(x:0,y:64,z:0,yaw:0,pitch:0,time:30),now:30),"量化读数初始化")
check(quantized.accept(F3Pose(x:0,y:64,z:0,yaw:0,pitch:0,time:30.02),now:30.02),"同一游戏刻重复帧")
check(quantized.accept(F3Pose(x:0,y:64.42,z:0.457,yaw:0,pitch:0,time:30.036),now:30.036),"疾跑跳跃的一刻位移不能因屏幕高帧率误判为传送")
check(!quantized.accept(F3Pose(x:12,y:64,z:12,yaw:0,pitch:0,time:30.05),now:30.05),"真正的坐标突变仍须停止")
for yaw in stride(from:-180.0,to:180.0,by:5) {
    let route=TellyRoute(x:0.5,z:0.5,yaw:yaw)
    guard let runway=route.runway(on:F3Block(x:0,y:63,z:0)) else {fatalError("完整方块中心必须有可用助跑范围")}
    for t in [runway.lowerBound+0.01,runway.upperBound-0.01] {
        let x=route.x+route.ux*t,z=route.z+route.uz*t
        check(x>=0 && x<=1 && z>=0 && z<=1,"助跑规划必须位于确认的方块内")
    }
}
let runner=TellyController();runner.config=gameConfig
var runKeys=[(UInt16,Bool)]()
runner.key={runKeys.append(($0,$1))}
runner.press(now:40)
for (t,yaw,pitch,target) in [(40.1,0.0,0.0,false),(40.2,0,0,false),(40.3,0,0,false),(40.4,8,5,false),(40.45,0,88,true),(40.5,0,0,false)] {
    runner.observe(F3Pose(x:0.5,y:64,z:0.5,yaw:yaw,pitch:pitch,time:t,looking:target ? F3Block(x:0,y:63,z:0):nil),error:"",now:t+0.01)
    runner.tick(now:t+0.01,active:true,minimum:15,maximum:18)
}
check(runner.phase == .backing,"校准后先调整助跑起点")
runner.release()
for code in Set(runKeys.filter{$0.1}.map{$0.0}) {check(runKeys.last(where:{$0.0==code})?.1==false,"助跑中松手同样释放全部代按键")}
print("通过：游戏刻位移量化、72个方向的助跑范围、助跑期间松手释放。")

// Regression: the rendered hit can be a top face while the logical use ray
// hits the side. Never mix those two eye positions for a placement decision.
let rayBlock=F3Block(x:0,y:79,z:0)
let logicalEye=F3Pose(x:0.5,y:81.249,z:2,yaw:180,pitch:73,time:0)
let renderedEye=F3Pose(x:0.5,y:81.249,z:1.7,yaw:180,pitch:73,time:0)
check(BridgeRay.intersection(block:rayBlock,pose:logicalEye)?.axis==2,"逻辑射线应命中侧面")
check(BridgeRay.intersection(block:rayBlock,pose:renderedEye)?.axis==1,"插值画面可能命中顶面，不能冒充点击射线")
let obstacle=F3Block(x:0,y:81,z:1)
let blockedEye=F3Pose(x:0.5,y:81,z:3,yaw:180,pitch:45,time:0)
check(BridgeRay.first(in:[rayBlock,obstacle],pose:blockedEye)?.block==obstacle,"射线必须取最近障碍，不能穿过方块放置")
var follower=RelativeMouseFollower(yaw:179,pitch:45,now:0)
var emittedX:Int64=0,emittedY:Int64=0
for i in 1...125 {
    let delta=follower.advance(yaw:-170,pitch:75,now:Double(i)*0.008,gainX:0.326,gainY:-0.326)
    check(abs(Double(delta.0)*0.326)<=10 && abs(Double(delta.1)*0.326)<=10,"连续跟随每步不能跳过速度上限")
    emittedX+=delta.0;emittedY+=delta.1
}
check(abs(F3Pose.angle(follower.yaw+170))<0.2 && abs(follower.pitch-75)<0.2,"连续跟随应收敛到目标")
check(abs(Double(emittedX)*0.326-11)<0.2 && abs(Double(emittedY)*(-0.326)-30)<0.2,"跨180度与反转Y必须保持实际相对计数一致")
let remapped=TellyGameConfig.parse(optionText+"\nkey_key.left:16\nkey_key.right:18\nkey_key.sneak:54",path:"")!
check(remapped.left==12 && remapped.right==14 && remapped.sneak==60,"归位和方向配合必须读取自定义侧移/潜行键")
print("通过：逻辑/渲染射线区别、方块遮挡、连续相对跟随与反转Y、侧移和潜行键位。")

func landingState(z:Double,previousZ:Double,y:Double,dy:Double,ground:Bool)->BridgeWorldState {
    let pose=F3Pose(x:0.5,y:y,z:z,yaw:0,pitch:45,time:0)
    return BridgeWorldState(pose:pose,renderPose:pose,
        previousPose:F3Pose(x:0.5,y:y,z:previousZ,yaw:0,pitch:45,time:0),
        velocity:(0,dy,0.24),onGround:ground,flying:false,hasBlocks:true,world:1,tick:1,face:nil,
        solid:[F3Block(x:0,y:80,z:2)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
}
let beforeLanding=BridgeLandingForecast.predict(landingState(z:3.18,previousZ:2.94,y:81.015,dy:-0.23,ground:false),height:81,yaw:0)!
check(beforeLanding.seconds==0.05 && abs(beforeLanding.supportZ-3.18)<0.0001 && beforeLanding.z>3.3,"落地按Y碰撞之前的位置判定支撑，不能使用水平推进后的坐标")
let afterLanding=BridgeLandingForecast.predict(landingState(z:3.44,previousZ:3.18,y:81,dy:-0.078,ground:true),height:81,yaw:0)!
check(afterLanding.seconds==0 && abs(afterLanding.supportZ-3.18)<0.0001,"已经落地时仍须保留本刻碰撞前的位置")
print("通过：Y碰撞先于水平推进、边缘落地和落地后读数的预测回归。")

let diagonalRoute=TellyRoute(x:200.5,z:200.5,yaw:-45)
let cornerChoices=diagonalRoute.candidates(after:F3Block(x:202,y:81,z:202))
check(cornerChoices.count==2,"斜向角落应允许两种沿路线前进的面连接顺序")
check(diagonalRoute.candidates(after:F3Block(x:203,y:81,z:202)).count==1,"已经偏向一侧的路径必须回到桥线，不能继续横向偏移")
let cornerView=F3Pose(x:203.664,y:82.249,z:203.665,yaw:135.14,pitch:50,time:0)
let costs=cornerChoices.map { choice -> Double in
    let point=choice.horizontalPoint(from:cornerView)
    check(point.x>=Double(choice.support.x) && point.x<=Double(choice.support.x)+1 && point.z>=Double(choice.support.z) && point.z<=Double(choice.support.z)+1,"保留水平视线的瞄准点仍须在真实方块面内")
    return abs(F3Pose.angle(atan2(cornerView.x-point.x,point.z-cornerView.z)*180 / .pi-cornerView.yaw))
}
check(costs.min()!<1,"斜向面切换不应强制把已接近正确的水平视线扭向面中心")
let moving=landingState(z:3,previousZ:2.76,y:81.249,dy:0.003,ground:false)
let driven=BridgeLandingForecast.predict(moving,height:81,yaw:0)!
let coast=BridgeLandingForecast.predict(moving,height:81,yaw:0,acceleration:0)!
check(coast.supportZ<driven.supportZ && coast.seconds==driven.seconds,"松方向键预测保留惯性并减少超出桥面的距离，不改变重力时间")
print("通过：斜向可见面选择、限制横向偏离、保留水平视线与惯性落点预测。")

// State-driven R release keeps only the already launched cycle alive. Safety
// interruptions still invalidate queued input immediately, including finishing.
func airborneController() -> (TellyController,Double) {
    let engine=TellyController();engine.config=gameConfig;engine.prepareRunup=false
    var yaw=0.0,pitch=0.0
    engine.move={x,y in yaw=F3Pose.angle(yaw+Double(x)*gameConfig.degreesPerCount);pitch+=Double(y)*gameConfig.degreesPerCount}
    engine.press(now:100)
    var now=100.0
    for i in 1...200 {
        now=100+Double(i)*0.01
        let pose=F3Pose(x:0.5,y:64,z:0.5,yaw:yaw,pitch:pitch,time:now)
        let state=BridgeWorldState(pose:pose,renderPose:pose,previousPose:pose,velocity:(0,0,0),onGround:true,flying:false,hasBlocks:true,world:1,tick:i,face:nil,solid:[F3Block(x:0,y:63,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
        engine.observeWorld(state,error:"",now:now)
        engine.tick(now:now,active:true,minimum:18,maximum:18)
        if engine.phase == .takeoff {return (engine,now)}
    }
    fatalError("测试起跳准备未完成：\(engine.message)")
}
let (finishEngine,finishTime)=airborneController()
finishEngine.release(now:finishTime+0.001)
check(!finishEngine.held && finishEngine.finishing && finishEngine.active && finishEngine.phase == .takeoff,"起跳后松开R应保留当前跳，不能立即清空控制器")
finishEngine.release(now:finishTime+0.2)
finishEngine.press(now:finishTime+0.3)
check(finishEngine.held && !finishEngine.finishing && finishEngine.phase == .takeoff,"收尾期间再次按R应继续当前轮，不能重复校准或启动第二任务")
finishEngine.release(now:finishTime+0.4)
finishEngine.tick(now:finishTime+0.41,active:false,minimum:18,maximum:18)
check(finishEngine.phase == .idle && !finishEngine.finishing,"失焦必须立即中断收尾，不得等待落地")
let (timeoutEngine,timeoutTime)=airborneController()
timeoutEngine.release(now:timeoutTime)
timeoutEngine.release(now:timeoutTime+1)
timeoutEngine.tick(now:timeoutTime+1.51,active:true,minimum:18,maximum:18)
check(timeoutEngine.phase == .idle && timeoutEngine.message.contains("及时确认"),"重复松手不能延长收尾的有限超时")
print("通过：起跳后松手收尾、收尾重按续接、重复释放不续期、失焦立即中断收尾。")
// R-up during an unconfirmed flight must not lower the eye by sneaking.
// Recorded SW trial460952: the old branch changed eye height while aiming.
let (releaseFlight,releaseFlightTime)=airborneController()
var releaseFlightKeys=Set<UInt16>()
releaseFlight.key={code,down in if down {releaseFlightKeys.insert(code)} else {releaseFlightKeys.remove(code)}}
func releaseAirState(_ time:Double,_ tick:Int)->BridgeWorldState {
    let p=F3Pose(x:0.5,y:64.42,z:0.8,yaw:0,pitch:0,time:time)
    return BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,0.3332,0.15),onGround:false,flying:false,hasBlocks:true,world:1,tick:tick,face:nil,solid:[F3Block(x:0,y:63,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
}
releaseFlight.observeWorld(releaseAirState(releaseFlightTime+0.05,300),error:"",now:releaseFlightTime+0.05)
releaseFlight.tick(now:releaseFlightTime+0.05,active:true,minimum:18,maximum:18)
releaseFlight.release(now:releaseFlightTime+0.051)
releaseFlight.observeWorld(releaseAirState(releaseFlightTime+0.06,300),error:"",now:releaseFlightTime+0.06)
releaseFlight.tick(now:releaseFlightTime+0.06,active:true,minimum:18,maximum:18)
check(releaseFlight.phase == .flight && releaseFlight.finishing && !releaseFlightKeys.contains(gameConfig.sneak),"松R不能在未确认落点的空中提前潜行改变眼高")
releaseFlight.stop("test cleanup")
print("通过：松R保留当前空中放块姿态，落点确认前不提前潜行。")

// Manual takeover commits the existing landing path, even if R remains
// physically held or is quickly pressed again before that landing completes.
let (manualEngine,manualTime)=airborneController()
manualEngine.requestManualFinish(now:manualTime+0.01)
check(manualEngine.finishing && manualEngine.phase == .takeoff && !manualEngine.held && manualEngine.restartRequiresRelease,"手动操作必须收尾当前跳并锁住仍按着的R")
manualEngine.press(now:manualTime+0.02)
check(manualEngine.finishing && !manualEngine.held,"R重复按下不得取消手动收尾")
manualEngine.release(now:manualTime+0.03)
manualEngine.press(now:manualTime+0.04)
check(manualEngine.finishing && !manualEngine.held && manualEngine.restartRequiresRelease,"收尾期间快速松R再按不能续跳或排队重启")
manualEngine.requestManualFinish(now:manualTime+1.0)
manualEngine.tick(now:manualTime+1.52,active:true,minimum:15,maximum:18)
check(manualEngine.phase == .idle && manualEngine.message.contains("及时确认"),"重复手动输入不能延长收尾超时")
manualEngine.press(now:manualTime+1.6)
check(manualEngine.phase == .idle,"结束后仍按住R不能自动重新开始")
manualEngine.release(now:manualTime+1.7)
manualEngine.press(now:manualTime+1.8)
check(manualEngine.phase == .preparing && manualEngine.held && !manualEngine.manualFinishRequested,"结束后松开再按R可启动一个新任务")
manualEngine.stop("test cleanup")
let (manualFocus,manualFocusTime)=airborneController()
manualFocus.requestManualFinish(now:manualFocusTime+0.01)
manualFocus.tick(now:manualFocusTime+0.02,active:false,minimum:15,maximum:18)
check(manualFocus.phase == .idle && !manualFocus.finishing,"手动收尾仍必须在失焦时立即释放输入")
let manualPreparing=TellyController();manualPreparing.press(now:0)
manualPreparing.requestManualFinish(now:0.01)
check(manualPreparing.phase == .idle && !manualPreparing.finishing && manualPreparing.restartRequiresRelease,"尚未起跳时手动操作取消准备，不多启动一跳")
var manualGate=BridgeManualInputGate()
check(!BridgeManualInputGate.Input.motion(0,0).hasIntent && BridgeManualInputGate.Input.motion(1,0).hasIntent,"鼠标回中产生的零位移不能被当作手动接管")
check(manualGate.consume(.key(13,true),duringFinish:true),"收尾阻止W干扰当前落点")
check(manualGate.consume(.key(13,true),duringFinish:false),"被吞按键在落地后的长按重复仍不泄漏")
check(manualGate.consume(.key(13,false),duringFinish:false),"被吞按下对应的松开不能释放其他持有者的按键")
check(!manualGate.consume(.key(13,true),duringFinish:false),"落稳后的新手动按键正常交回玩家")
check(manualGate.consume(.button(1,true),duringFinish:true) && manualGate.suppressesButton(1),"收尾时手动右键不能额外放块或触发原连点器")
check(manualGate.consume(.drag(1),duringFinish:false),"落地后仍按着被吞右键的拖动不泄漏")
check(manualGate.consume(.button(1,false),duringFinish:false) && !manualGate.suppressesButton(1),"松开右键恢复新点击入口")
check(!manualGate.consume(.button(1,true),duringFinish:false),"落地后的新右键点击正常放行")
check(manualGate.consume(.scroll,duringFinish:true) && manualGate.consume(.modifier,duringFinish:true),"收尾期间滚轮和修饰键不改变手持物或运动")
check(!manualGate.consume(.motion(10,4),duringFinish:false),"收尾结束立即归还鼠标移动")
print("通过：手动接管收尾、R重新按下门槛、输入成对隔离、零位移忽略与失焦立即停止。")

// Recorded NW manual-button restart: body still overlaps the corner by
// 0.00168/0.00206 blocks; old 0.29 F3 probing missed the native support.
func openingSupportPhase(x:Double,z:Double,solid:Set<F3Block>)->TellyController.Phase {
    let engine=TellyController();engine.config=gameConfig
    var yaw=135.0,pitch=45.0
    engine.move={dx,dy in yaw=F3Pose.angle(yaw+Double(dx)*gameConfig.degreesPerCount);pitch+=Double(dy)*gameConfig.degreesPerCount}
    engine.press(now:0)
    for i in 1...60 {
        let now=Double(i)*0.01,p=F3Pose(x:x,y:80,z:z,yaw:yaw,pitch:pitch,time:Double(i)*0.01)
        let s=BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,0,0),onGround:true,flying:false,hasBlocks:true,world:1,tick:i,face:nil,solid:solid,useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
        engine.observeWorld(s,error:"",now:now);engine.tick(now:now,active:true,minimum:15,maximum:18)
        if engine.phase == .aligning || engine.phase == .probing {let result=engine.phase;engine.stop("test cleanup");return result}
    }
    fatalError("Opening calibration did not finish")
}
let restartCorner:Set<F3Block>=[F3Block(x:0,y:79,z:0)]
check(openingSupportPhase(x:-0.29831930983,z:-0.29793542357,solid:restartCorner) == .aligning,"落地收尾后的实际角落接触必须允许重新按R起步")
check(openingSupportPhase(x:0.5,z:0.5,solid:restartCorner) == .aligning,"方块中心的原有起点识别保持")
check(openingSupportPhase(x:-0.301,z:-0.2979,solid:restartCorner) == .probing,"完全离开一条边时不能仅信onGround捏造支撑")
check(openingSupportPhase(x:-0.2983,z:-0.2979,solid:[]) == .probing,"支撑撤回后不得使用上次落地的缓存方块")
print("通过：角落收尾后重新起步、正常中心、完全悬空和当前支撑撤回回归。")

let eyeBoundary=F3Pose(x:0.5,y:81.249,z:2,yaw:180,pitch:70.5,time:0)
check(BridgeRay.intersection(block:rayBlock,pose:eyeBoundary,eyeHeight:1.62)?.axis==1,"站立眼高的边界射线应命中顶面")
check(BridgeRay.intersection(block:rayBlock,pose:eyeBoundary,eyeHeight:1.54)?.axis==2,"潜行收尾眼高下降后应使用新的侧面射线，不能沿用站立眼高")
print("通过：潜行收尾眼高改变后的放置面回归。")

// Live regression: at x=530.0533, y=95.0013 the old 18-CPS-only
// budget kept accelerating. The fourth cell was clicked after its landing
// window, at x=531.5442/y=94.785. Account for both game-tick boundaries.
let lastCellWindow=BridgeLandingForecast(x:531.6589,z:500.5,supportX:531.4039,supportZ:500.5,seconds:0.35)
check(lastCellWindow.needsCoast(remainingCells:4,cps:18,returnTime:0.072),"剩余方块加点击确认及回正来不及，应提前保留惯性而不是继续加速")
let ampleWindow=BridgeLandingForecast(x:3,z:0.5,supportX:2.8,supportZ:0.5,seconds:0.45)
check(!ampleWindow.needsCoast(remainingCells:2,cps:18,returnTime:0.072),"时间充足时仍保留前进，不应每次起跳就减速")
check(!lastCellWindow.needsCoast(remainingCells:0,cps:18,returnTime:0.072),"已铺好的落点不需要额外放块预算")
print("通过：实测最后一格放置过晚的空中时间预算回归。")

var evenTurn=RelativeMouseTurn(x:36000,y:9000,start:0,duration:RelativeMouseTurn.maximumDuration)
var turnSteps=[Int64]()
for i in 0...112 {turnSteps.append(evenTurn.advance(now:Double(i)/1000).x)}
check(Double(turnSteps.max()!)<36000/112*1.3,"转向峰值应低于平均速度的1.3倍，避免中段突然甩动")
let cruise=Array(turnSteps[30...80])
check(cruise.max()!-cruise.min()!<=1,"转向中段保持均匀，差异仅允许整数鼠标计数量化")
check(turnSteps[1]<turnSteps[10] && turnSteps[102]>turnSteps[112],"起止仍平滑加减速，不能恒速硬启停")
check(RelativeMouseTurn.duration(for:180)>=0.10,"180度大转向应至少跨越100毫秒")
print("通过：较慢的大角度转向、均匀巡航段、连续起止及峰值速度约束。")
var cruiseReturn=RelativeMouseTurn(x:36000,y:-9000,start:0,duration:0.112,ramp:0.10)
var cruiseSteps=[Int64](),cruiseX:Int64=0,cruiseY:Int64=0
for i in 0...112 {
    let step=cruiseReturn.advance(now:Double(i)/1000)
    check(step.x>=0 && step.y<=0,"回正曲线不能反转或抖动")
    cruiseSteps.append(step.x);cruiseX+=step.x;cruiseY+=step.y
}
check(cruiseX==36000 && cruiseY == -9000,"均匀回正必须在原112毫秒内完成原角度")
check(Double(cruiseSteps.max()!)<Double(turnSteps.max()!)*0.93,"均匀回正必须降低峰值而非延长动作")
var delayedReturn=RelativeMouseTurn(x:-1200,y:300,start:0,duration:0.112,ramp:0.10)
var delayedX:Int64=0,delayedY:Int64=0
for time in [0.0,0.007,0.026,0.047,0.063,0.089,0.112] {
    let step=delayedReturn.advance(now:time);delayedX+=step.x;delayedY+=step.y
}
check(delayedX == -1200 && delayedY==300,"不规则回调仍须准确回正，不补出额外角度")
print("通过：均匀回正降低峰值，保持时长、角度与不规则回调收敛。")

for yaw in stride(from:-180.0,to:180.0,by:5) {
    let held=TellyController.directionKeys(yaw:yaw,heading:0,config:gameConfig)
    let forward=(held.contains(gameConfig.forward) ? 1.0:0)-(held.contains(gameConfig.back) ? 1.0:0)
    let side=(held.contains(gameConfig.left) ? 1.0:0)-(held.contains(gameConfig.right) ? 1.0:0)
    let r=yaw * .pi/180
    let along=forward*cos(r)+side*sin(r),cross = -forward*sin(r)+side*cos(r)
    check(along>0 && abs(cross)/along<0.42,"转身中配合方向键，合力始终沿桥线且误差不超过离散键位限制")
    check(!held.contains(gameConfig.sprint) || abs(yaw)<12,"回正未完成不能产生侧向疾跑跳跃加速")
}
print("通过：转向全程72个角度的桥线方向配合、疾跑起跳朝向约束。")

for heading in stride(from:-180.0,to:180.0,by:5) {
    for drift in [-0.6,0,0.6] {
        let back=F3Pose.angle(heading+180+drift)
        let outbound=RelativeMouseTurn.yawDelta(from:heading,to:back,preferredSign:-1)
        let returning=RelativeMouseTurn.yawDelta(from:back,to:heading,preferredSign:1)
        check(outbound<0 && returning>0,"接近180度边界有微小误差时仍固定左转放块、右转回正")
        check(abs(outbound+returning)<0.0001 && abs(outbound)<181,"一轮往返净转角为零，不应继续同侧绕整圈")
    }
}
check(RelativeMouseTurn.yawDelta(from:10,to:13,preferredSign:-1)==3,"固定转身方向不能把三度微调变成整圈旋转")
print("通过：216组半周边界偏差下的固定方向往返与小角度修正。")

// Updating a moving face must preserve already emitted counts and the turn's
// original deadline, rather than restarting a full turn at each observation.
var retargeted=RelativeMouseTurn(x:-1200,y:220,start:2,duration:0.112)
var retargetX:Int64=0,retargetY:Int64=0
for i in 0...28 {
    if i==10 {retargeted.retarget(x:-1160,y:250)}
    if i==20 {retargeted.retarget(x:-1145,y:285)}
    let delta=retargeted.advance(now:2+Double(i)*0.004)
    retargetX+=delta.x;retargetY+=delta.y
    check(delta.x<=0,"移动目标的小幅更新不能使回头中途反向")
    if i<28 {check(!delta.finished,"目标更新不能提前结束转向")}
}
check(retargetX == -1145 && retargetY == 285,"目标更新只补发与新终点的差值，不能重复已发送计数")
let retargetEnd=retargeted.advance(now:2.2)
check(retargetEnd.finished && retargetEnd.x==0 && retargetEnd.y==0,"跟踪更新必须保持原始结束时间且不补发残余转向")
print("通过：空中移动目标更新、已发送计数守恒、固定转向期限与无反向跳动。")

// 1.8.3 live trace: at 5.775 s a side-face update emitted 129 Y
// counts (19.35 degrees) in a single event, then stayed flat. Spread this
// correction without an endpoint snap or an urgency-dependent speed burst.
var pitchChange=RelativeMouseFollower(yaw:87.75,pitch:57.45,now:0)
var pitchSteps=[Double](),pitchReached:Double?
for i in 1...20 {
    let delta=pitchChange.advance(yaw:83.7,pitch:76.8,now:Double(i)*0.008,gainX:0.15,gainY:0.15)
    pitchSteps.append(Double(delta.1)*0.15)
    check(delta.1>=0 && pitchChange.pitch<=76.95,"单次放块目标变化不能产生反向抖动或显著过冲")
    if pitchReached==nil && abs(pitchChange.pitch-76.8)<1 {pitchReached=Double(i)*0.008}
}
check(pitchSteps.max()!<6,"19.35度的低头修正不能集中到一个8ms输入中")
check((pitchReached ?? 1)<=0.08,"平滑不能引入超过80ms的单次面修正延迟")
check(pitchSteps.prefix(6).filter{$0>0}.count>=5,"面修正应跨多个输入连续推进，不能跳一步再停")
let duplicate=pitchChange.advance(yaw:95,pitch:65,now:0.16,gainX:0.15,gainY:0.15)
check(duplicate.0==0 && duplicate.1==0,"重复时间不能凭空推进相机")

var movingTurn=RelativeMouseTurn(x:-1200,y:220,start:0,duration:0.112)
_ = movingTurn.advance(now:0.05)
movingTurn.retarget(x:-1160,y:320)
let nextInstant=movingTurn.advance(now:0.0501)
check(abs(nextInstant.x)<=3 && abs(nextInstant.y)<=2,"转身目标改变的瞬间应保持位置和速度，不能缩放整条曲线造成跳角")
_ = movingTurn.advance(now:0.10)
movingTurn.retarget(x:-1000,y:500)
check(movingTurn.x == -1160 && movingTurn.y==320,"最后制动区间不能突然追新的大幅目标；由后续跟随接管")
var brakingTurn=RelativeMouseTurn(x:-1200,y:220,start:0,duration:0.112)
_ = brakingTurn.advance(now:0.084)
brakingTurn.retarget(x:-980,y:220)
check(brakingTurn.x == -1200,"无法在剩余时间内平滑制动的新目标应交给跟随，不能先过冲再反向补偿")
for i in 85...112 {check(brakingTurn.advance(now:Double(i)*0.001).x<=0,"转身制动过程中不能发生反向跳动")}
print("通过：实测19.35度突跳的平滑回归、响应时间上限、重复时钟和动态转向连续性。")

var bridgeMods=BridgeModifiers()
check(bridgeMods.update(code:59,down:true),"Control 是桥接修饰键")
let sprintFlags=bridgeMods.flags
check(!bridgeMods.update(code:13,down:true) && bridgeMods.flags==sprintFlags,"按 W 不得清除已持有的 Control")
check(bridgeMods.update(code:56,down:true) && bridgeMods.flags & sprintFlags == sprintFlags,"潜行与疾跑的事件标志互不覆盖")
_ = bridgeMods.update(code:59,down:false)
check(bridgeMods.flags==(1<<17)|2,"释放 Control 不能释放仍持有的 Shift")
_ = bridgeMods.update(code:56,down:false)
check(bridgeMods.flags==0,"停止后不能残留修饰键")
_ = bridgeMods.update(code:59,down:true);_ = bridgeMods.update(code:62,down:true)
_ = bridgeMods.update(code:59,down:false)
check(bridgeMods.flags==(1<<18)|0x2000,"释放左 Control 保留右 Control")
print("通过：搭路输入修饰键保持、左右修饰键与停止释放回归。")

check(TellyGameConfig.parse(optionText.replacingOccurrences(of:"key_key.forward:17",with:"key_key.forward:20"),path:"")==nil,"T 模式键与移动键冲突时禁止搭路")

// Hypixel practice trace: yaw 1.05, third takeoff. The old yaw-only
// ranking picked the west side from x=5002.1269, east of that face.
let serverRoute=TellyRoute(x:5002.5003,z:2.4869,yaw:1.05)
let serverSupport=F3Block(x:5002,y:79,z:9)
let serverPose=F3Pose(x:5002.1269,y:80.42,z:10.699,yaw:1.05,pitch:45,time:0)
let serverChoices=serverRoute.candidates(after:serverSupport)
check(serverChoices.contains{$0.axis==0},"失败场景必须包含会误选的侧面，不能把偏角悄悄归零")
let exposed=serverRoute.exposedCandidates(after:serverSupport,from:serverPose)
check(exposed.count==1 && exposed[0].axis==2 && exposed[0].sign==1,"服务器偏角起跳必须选择前方已露出的南面")
check(exposed[0].result==F3Block(x:5002,y:79,z:10),"不能把下一落点误规划到人物身侧")
for yaw in [0.0,90,-90,180] {
    let route=TellyRoute(x:0.5,z:0.5,yaw:yaw)
    let support=F3Block(x:0,y:79,z:0)
    let p=F3Pose(x:0.5+route.ux*1.2,y:80.42,z:0.5+route.uz*1.2,yaw:yaw,pitch:45,time:0)
    check(route.exposedCandidates(after:support,from:p).count==1,"四个正向已露出的面不能被过滤")
}
let westPose=F3Pose(x:5001.8,y:80.42,z:9.5,yaw:1.05,pitch:45,time:0)
check(serverRoute.exposedCandidates(after:serverSupport,from:westPose).contains{$0.axis==0 && $0.sign == -1},"人物实际绕到西面之后，仍须允许侧面放置")
print("通过：练习服轻微偏角选错不可见侧面回归、四个正向及侧面实际露出。")
let platformRoute=TellyRoute(x:0.5,z:0.5,yaw:0)
let platform:Set<F3Block>=Set((0...3).map{F3Block(x:0,y:79,z:$0)})
check(platformRoute.frontSupport(from:F3Block(x:0,y:79,z:0),solid:platform)==F3Block(x:0,y:79,z:3),"多格起点须助跑到真实平台前缘，不从第一块起跳")
let broken=platform.subtracting([F3Block(x:0,y:79,z:2)])
check(platformRoute.frontSupport(from:F3Block(x:0,y:79,z:0),solid:broken)==F3Block(x:0,y:79,z:1),"助跑不能跨过未确认的缺口")
print("通过：服务器平台真实前缘与断口助跑边界。")
for overhang in [0.221,0.27,0.29,0.2995] {
    let edge=landingState(z:3+overhang,previousZ:3.10,y:81,dy:-0.078,ground:true)
    check(!BridgeLandingForecast.standingSupport(edge,floor:80).isEmpty,"实际踩住边缘时必须立即保留支撑，不能继续等第四块")
}
check(BridgeLandingForecast.standingSupport(landingState(z:3.31,previousZ:3.1,y:81,dy:-0.078,ground:true),floor:80).isEmpty,"onGround 不能覆盖身体已完全离开方块的事实")
check(BridgeLandingForecast.standingSupport(landingState(z:3.27,previousZ:3.1,y:81.01,dy:-0.1,ground:false),floor:80).isEmpty,"空中接近桥面不能误报实际落地")
var withdrawn=landingState(z:3.27,previousZ:3.1,y:81,dy:-0.078,ground:true)
withdrawn=BridgeWorldState(pose:withdrawn.pose,renderPose:withdrawn.pose,previousPose:withdrawn.previousPose,velocity:withdrawn.velocity,onGround:true,flying:false,hasBlocks:true,world:1,tick:2,face:nil,solid:[],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
check(BridgeLandingForecast.standingSupport(withdrawn,floor:80).isEmpty,"服务器撤回方块后不能以旧支撑确认落地")
print("通过：服务器边缘接触、落地即制动的支撑判定、完全悬空与方块撤回。")
let edgeArrival=landingState(z:3.18,previousZ:2.94,y:81.015,dy:-0.23,ground:false)
check(!beforeLanding.imminentSupport(edgeArrival,floor:80).isEmpty,"Y碰撞在下一刻发生时须预先保护边缘，不能等水平位移结束才潜行")
check(ampleWindow.imminentSupport(edgeArrival,floor:80).isEmpty,"尚在远处的落点不能触发提前收尾")

// Regression: an upcoming vertical contact must not interrupt placement
// before the same physics tick moves the body beyond the support's edge.
let (contactEngine,contactTime)=airborneController()
var contactKeys=Set<UInt16>()
contactEngine.key={code,down in if down {contactKeys.insert(code)} else {contactKeys.remove(code)}}
func contactFrame(y:Double,z:Double,dy:Double,ground:Bool,at:Double) {
    let pose=F3Pose(x:0.5,y:y,z:z,yaw:0,pitch:0,time:at)
    let state=BridgeWorldState(pose:pose,renderPose:pose,previousPose:pose,velocity:(0,dy,0.16),onGround:ground,flying:false,hasBlocks:true,world:1,tick:Int((at-contactTime)*20)+1000,face:nil,solid:[F3Block(x:0,y:63,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
    contactEngine.observeWorld(state,error:"",now:at)
    contactEngine.tick(now:at,active:true,minimum:18,maximum:18)
}
contactFrame(y:64.42,z:0.85,dy:0.333,ground:false,at:contactTime+0.05)
contactFrame(y:64.104,z:1.23,dy:-0.447,ground:false,at:contactTime+0.10)
check(contactEngine.phase == .flight,"下一次Y碰撞后身体会越过桥边，不能提前回正并停止放块")
contactEngine.stop("test finished")
check(contactKeys.isEmpty,"停止时释放本功能持有的按键")
print("通过：垂直接触不能冒充水平移动后的安全落点；停止释放输入。")

// A first flat span with 250 ms left and one missing support cell must
// reserve a complete return turn, just like the later spans. The former
// first-jump 25-ms exception kept accelerating in this exact time window.
let (openingEngine,openingTime)=airborneController()
var openingKeys:Set<UInt16>=[gameConfig.forward,gameConfig.sprint,gameConfig.jump]
openingEngine.key={code,down in if down {openingKeys.insert(code)} else {openingKeys.remove(code)}}
let openingPose=F3Pose(x:0.5,y:65.1708,z:0.95,yaw:0,pitch:0,time:openingTime+0.20)
let openingState=BridgeWorldState(pose:openingPose,renderPose:openingPose,previousPose:openingPose,velocity:(0,-0.155,0.08),onGround:false,flying:false,hasBlocks:true,world:1,tick:500,face:nil,solid:[F3Block(x:0,y:63,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
openingEngine.observeWorld(openingState,error:"",now:openingPose.time)
openingEngine.tick(now:openingPose.time,active:true,minimum:18,maximum:18)
check(openingEngine.phase == .flight,"首跳保留放块过程，不能把收速度当作结束搭路")
check(openingKeys.contains(gameConfig.sprint),"停止方向加速时仍持有疾跑键")
check(!openingKeys.contains(gameConfig.forward) && !openingKeys.contains(gameConfig.back),"首跳缺少支撑且仅余250毫秒时应松开加速，不继续冲出桥边也不反向制动")
openingEngine.stop("test finished")
check(openingKeys.isEmpty,"首跳保护停止后释放所有持有按键")
print("通过：首跳使用完整确认／回正预算；保留惯性、不反向制动。")

func clearanceState(_ boxes:[BridgeCollisionBox],speed:Double=0)->BridgeWorldState {
    let p=F3Pose(x:0.5,y:80,z:0.5,yaw:0,pitch:45,time:0)
    return BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,0,speed),onGround:true,flying:false,hasBlocks:true,world:1,tick:1,face:nil,solid:[F3Block(x:0,y:79,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62,collisionBoxes:boxes)
}
let clearFloor=BridgeCollisionBox(minX:-1,minY:79,minZ:-1,maxX:2,maxY:80,maxZ:8)
let lowCeiling=BridgeCollisionBox(minX:0,minY:82,minZ:0,maxX:1,maxY:83,maxZ:1)
let frontWall=BridgeCollisionBox(minX:0,minY:80,minZ:1,maxX:1,maxY:83,maxZ:2)
let distantCeiling=BridgeCollisionBox(minX:0,minY:82,minZ:2,maxX:1,maxY:83,maxZ:3)
let outsideWall=BridgeCollisionBox(minX:1,minY:80,minZ:0,maxX:2,maxY:83,maxZ:4)
let fence=BridgeCollisionBox(minX:0.375,minY:80,minZ:1,maxX:0.625,maxY:81.5,maxZ:2)
check(!BridgeClearance.jumpBlocked(clearanceState([clearFloor]),yaw:0,rise:0),"连续现有地面不能被当作障碍")
check(BridgeClearance.jumpBlocked(clearanceState([clearFloor,lowCeiling]),yaw:0,rise:0),"起跳前识别脚上两格的低顶")
check(BridgeClearance.jumpBlocked(clearanceState([distantCeiling],speed:0.16),yaw:0,rise:0),"识别跳跃途中上方障碍")
check(BridgeClearance.walkingBlocked(clearanceState([frontWall]),yaw:0),"助跑前识别身体前方实墙")
check(BridgeClearance.walkingBlocked(clearanceState([fence]),yaw:0),"栅栏碰撞体不能因不是完整方块而漏报")
check(!BridgeClearance.jumpBlocked(clearanceState([outsideWall]),yaw:0,rise:1),"路线旁未相交的墙不应阻止起跳")
print("通过：起点低顶、空中顶障、前方墙、非整块碰撞和可通行路线。")

let blockedEngine=TellyController();blockedEngine.config=gameConfig
var blockedKeys=Set<UInt16>(),blockedJumps=0
blockedEngine.key={code,down in
    if down {blockedKeys.insert(code);if code==gameConfig.jump {blockedJumps+=1}}
    else {blockedKeys.remove(code)}
}
blockedEngine.press(now:200)
for i in 1...6 {
    let now=200+Double(i)*0.05
    let p=F3Pose(x:0.5,y:80,z:0.5,yaw:0,pitch:45,time:now)
    let s=BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,0,i<6 ? 0.05:0),onGround:true,flying:false,hasBlocks:true,world:1,tick:i,face:nil,solid:[F3Block(x:0,y:79,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62,collisionBoxes:[clearFloor,lowCeiling])
    blockedEngine.observeWorld(s,error:"",now:now);blockedEngine.tick(now:now,active:true,minimum:18,maximum:18)
    if i==4 {
        check(blockedEngine.phase == .blocked && blockedKeys==[gameConfig.sneak],"有惯性且头顶受阻时保持潜行，不起跳、不裸放全部输入")
        blockedEngine.release(now:now)
        check(blockedEngine.finishing,"障碍停稳期间松R仍须完成制动")
    }
}
check(blockedJumps==0 && blockedKeys.isEmpty && blockedEngine.phase == .idle,"停稳后释放按键，全程不得跳进低顶")
print("通过：带惯性的低顶起点、松R停稳与按键释放。")

for (input,expected) in [(1.0,0.0),(-4.9,0.0),(91,90),(-94,-90),(179,180),(-179,180)] {
    check(abs(F3Pose.angle(TellyController.openingHeading(input)-expected))<0.0001,"近正向起点应轻微对正，避免长桥跨列")
}
check(TellyController.openingHeading(45)==45 && TellyController.openingHeading(5.1)==5.1,"不能把明显斜向也悄悄改成正向")
print("通过：近正向起点对正、180度边界及明显斜向保留。")

// Desktop R/T replay: the forward turn finishes at z=3.063 with 0.13
// blocks/tick remaining. Sending W and waiting for another controller update
// can carry the player past z=3.30 before jump is pressed.
let (edgeHandoff,edgeHandoffTime)=airborneController()
var handoffYaw=0.0,handoffPitch=0.0,handoffKeys=Set<UInt16>()
edgeHandoff.move={x,y in handoffYaw=F3Pose.angle(handoffYaw+Double(x)*gameConfig.degreesPerCount);handoffPitch+=Double(y)*gameConfig.degreesPerCount}
edgeHandoff.key={code,down in if down {handoffKeys.insert(code)} else {handoffKeys.remove(code)}}
func handoffFrame(y:Double,z:Double,ground:Bool,dy:Double,at:Double) {
    let pose=F3Pose(x:0.5,y:y,z:z,yaw:handoffYaw,pitch:handoffPitch,time:at)
    let s=BridgeWorldState(pose:pose,renderPose:pose,previousPose:pose,velocity:(0,dy,0.13),onGround:ground,flying:false,hasBlocks:true,world:1,tick:Int(at*100),face:nil,solid:Set((0...2).map{F3Block(x:0,y:63,z:$0)}),useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
    edgeHandoff.observeWorld(s,error:"",now:at);edgeHandoff.tick(now:at,active:true,minimum:18,maximum:18)
}
handoffFrame(y:64.42,z:0.9,ground:false,dy:0.333,at:edgeHandoffTime+0.05)
handoffFrame(y:64.42,z:1.9,ground:false,dy:0.003,at:edgeHandoffTime+0.10)
handoffFrame(y:64,z:3.063,ground:true,dy:-0.078,at:edgeHandoffTime+0.15)
check(edgeHandoff.phase == .landing,"回归场景须实际进入已确认支撑的落地阶段")
for i in 1...60 {
    handoffFrame(y:64,z:3.063,ground:true,dy:-0.078,at:edgeHandoffTime+0.15+Double(i)*0.01)
    check(edgeHandoff.phase != .runup,"边缘回正结束时不能只发W并空等下一更新")
    if edgeHandoff.phase == .takeoff {break}
}
check(edgeHandoff.phase == .takeoff && handoffKeys.contains(gameConfig.jump),"边缘应在同一次状态转换中按下跳跃")
edgeHandoff.stop("test finished")
check(handoffKeys.isEmpty,"回归场景结束须释放全部按键")
print("通过：桌面入口落地回正与下一跳原子衔接，防止边缘多走一拍。")

let queuedGuard=BridgeInputEpoch(),queuedToken=queuedGuard.snapshot()
check(queuedGuard.authorize(queuedToken,queuedAt:1,now:1.04) == .send,"正常输入队列延迟可发送")
check(queuedGuard.authorize(queuedToken,queuedAt:1,now:1.09) == .expired,"超过80ms的动作不能在恢复后集中补发")
check(queuedGuard.authorize(queuedToken,queuedAt:1.1,now:1.11) == .cancelled,"过期动作取消同批后续动作")
check(queuedGuard.authorize(queuedGuard.snapshot(),queuedAt:2,now:2.01) == .send,"恢复后新任务仍可发送")
print("通过：搭路惯性阶段保留疾跑；输入队列超时取消和新任务恢复。")
