// Append to Tests/main.swift when compiling diagonal-finishguard.swift.
// Replays a supported corner with no placeable continuation. This checks the
// camera/input finish contract; it is not a substitute for Minecraft physics.
let guardEngine=TellyController()
guardEngine.config=gameConfig
guardEngine.prepareRunup=false
guardEngine.coordinateMovement=true
guardEngine.forwardPitch=45
var guardYaw = -45.0,guardPitch=0.0,guardKeys=Set<UInt16>()
guardEngine.move={x,y in
    guardYaw=F3Pose.angle(guardYaw+Double(x)*gameConfig.degreesPerCount)
    guardPitch+=Double(y)*gameConfig.degreesPerCount
}
guardEngine.key={code,down in
    if down {guardKeys.insert(code)} else {guardKeys.remove(code)}
}
func guardFrame(at:Double,x:Double,z:Double,y:Double,ground:Bool) {
    let p=F3Pose(x:x,y:y,z:z,yaw:guardYaw,pitch:guardPitch,time:at)
    let state=BridgeWorldState(pose:p,renderPose:p,previousPose:p,
        velocity:(0,ground ? -0.078:0.333,0),onGround:ground,flying:false,
        hasBlocks:true,world:1,tick:Int(at*100),face:nil,
        solid:[F3Block(x:0,y:63,z:0)],useHit:nil,useFace:nil,
        useDown:false,clickDelay:0,eyeHeight:ground ? 1.54:1.62)
    guardEngine.observeWorld(state,error:"",now:at)
    guardEngine.tick(now:at,active:true,minimum:15,maximum:18)
}
guardEngine.press(now:200)
var guardStart=200.0
for i in 1...300 {
    guardStart=200+Double(i)*0.01
    guardFrame(at:guardStart,x:0.5,z:0.5,y:64,ground:true)
    if guardEngine.phase == .takeoff {break}
}
check(guardEngine.phase == .takeoff,"回正回归必须先完成真实控制器的起跳准备")
guardFrame(at:guardStart+0.02,x:1.0,z:0.5,y:64,ground:true)
check(guardKeys.contains(gameConfig.jump) && !guardKeys.contains(gameConfig.left) && !guardKeys.contains(gameConfig.right),"斜向起跳不能把偏移纠正变成侧向跳跃")
guardFrame(at:guardStart+0.05,x:0.85,z:0.85,y:64.42,ground:false)
var protectedFinishSeen=false
for i in 1...260 {
    guardFrame(at:guardStart+0.05+Double(i)*0.01,x:1.29,z:1.29,y:64,ground:true)
    if guardEngine.finishing {
        protectedFinishSeen=true
        check(guardKeys.contains(gameConfig.sneak),"受保护的回正过程必须继续保护桥边")
        check(!guardKeys.contains(gameConfig.jump),"无法续接时不能再开启一跳")
    }
    if guardEngine.phase == .idle {break}
}
check(protectedFinishSeen,"有真实支撑的续接超时必须进入回正收尾")
check(guardEngine.phase == .idle && guardKeys.isEmpty,"收尾后应结束任务并释放按键")
check(abs(F3Pose.angle(guardYaw+45))<1 && abs(guardPitch-45)<1,"退出前必须回到桥线方向和前视俯仰")
check(guardEngine.message.contains("无法安全续接") && guardEngine.message.contains("回正"),"保留异常原因，不能把保护停止报告成连续搭路通过")
print("通过：斜桥支撑不足时保护停稳、最终视角回正、按键释放和真实失败原因保留。")
