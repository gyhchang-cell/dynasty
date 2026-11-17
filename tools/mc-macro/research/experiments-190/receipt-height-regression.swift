var receipt=BridgeClickReceipt(issuedTick:40)
receipt.observe(tick:40,delay:4)
receipt.observe(tick:41,delay:3)
check(!receipt.mayRetry(tick:41,mouseDown:false),"旧点击倒计时不能确认新点击失败并触发重复输入")
receipt.observe(tick:42,delay:4)
check(!receipt.mayRetry(tick:42,mouseDown:false),"刚收到消费确认时必须等待方块结果")
check(!receipt.mayRetry(tick:43,mouseDown:true),"鼠标仍被游戏观察为按下时不得重复按下")
check(receipt.mayRetry(tick:43,mouseDown:false),"确认消费且下一游戏刻仍未出现方块时允许重试")

let heightEngine=TellyController()
heightEngine.config=gameConfig; heightEngine.prepareRunup=false
heightEngine.coordinateMovement=true; heightEngine.forwardPitch=45
var heightYaw = -45.0,heightPitch=0.0,heightKeys=Set<UInt16>()
heightEngine.move={x,y in heightYaw=F3Pose.angle(heightYaw+Double(x)*gameConfig.degreesPerCount);heightPitch+=Double(y)*gameConfig.degreesPerCount}
heightEngine.key={key,down in if down {heightKeys.insert(key)} else {heightKeys.remove(key)}}
func heightFrame(_ at:Double,_ y:Double,_ ground:Bool,_ floor:Int) {
    let p=F3Pose(x:0.5,y:y,z:0.5,yaw:heightYaw,pitch:heightPitch,time:at)
    let state=BridgeWorldState(pose:p,renderPose:p,previousPose:p,velocity:(0,ground ? -0.078:0.333,0),
        onGround:ground,flying:false,hasBlocks:true,world:1,tick:Int(at*100),face:nil,
        solid:[F3Block(x:0,y:floor,z:0)],useHit:nil,useFace:nil,useDown:false,clickDelay:0,eyeHeight:1.62)
    heightEngine.observeWorld(state,error:"",now:at)
    heightEngine.tick(now:at,active:true,minimum:15,maximum:18)
}
heightEngine.press(now:300)
var heightAt=300.0
for i in 1...300 {
    heightAt=300+Double(i)*0.01;heightFrame(heightAt,64,true,63)
    if heightEngine.phase == .takeoff {break}
}
check(heightEngine.phase == .takeoff,"意外高度回归应先进入起跳")
heightFrame(heightAt+0.05,64.42,false,63)
heightFrame(heightAt+0.10,65,true,64)
check(heightEngine.finishing && !heightKeys.contains(gameConfig.jump),"真实落在高一格方块上时不得按旧高度续跳")
for i in 1...200 {
    heightFrame(heightAt+0.10+Double(i)*0.01,65,true,64)
    if heightEngine.phase == .idle {break}
}
check(heightEngine.phase == .idle && heightKeys.isEmpty,"意外高度保护收尾应释放全部按键")
check(abs(F3Pose.angle(heightYaw+45))<1 && abs(heightPitch-45)<1,"意外高度保护收尾也必须回正")
check(heightEngine.message.contains("实际落地高度"),"意外高度保护停止不能报告为连续搭路通过")
print("通过：点击消费回执与意外落地高度保护回正。")
