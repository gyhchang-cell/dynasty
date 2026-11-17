// Geometry tests use the same corner that previously started a forward,
// backward, then second forward turn before the next jump.
let corridorRoute=TellyRoute(x:0.5,z:0.5,yaw:-45)
let corner=F3Block(x:1,y:63,z:0)
func corridor(_ cells:Set<F3Block>,x:Double=1.10,z:Double=1.10,
              collisionX:Double=1.02,collisionZ:Double=1.02)->BridgeContinuationWindow? {
    BridgeContinuationWindow.evaluate(solid:cells,floor:63,route:corridorRoute,
        x:x,z:z,collisionX:collisionX,collisionZ:collisionZ,requiredForward:0.35)
}
check(corridor([corner]) == nil,"只有角落碰撞不能授权回正后继续前进")
let nextCell=F3Block(x:1,y:63,z:1)
check(corridor([corner,nextCell]) != nil,"真实相邻块补齐后可在同一次回望结束时提交下一起跳走廊")
check(corridor([corner,F3Block(x:1,y:64,z:1)]) == nil,"上方方块不能充当当前层的连续跑道")
check(corridor([corner,F3Block(x:2,y:63,z:2)]) == nil,"远处方块不能跨越支撑缺口拼成走廊")
check(corridor([corner,nextCell],collisionX:3,collisionZ:3) == nil,"水平移动后的落点有块也不能忽略垂直碰撞前的缺口")

// Sign and origin invariance; do not only validate the previously passing NW.
for sx in [-1,1] {for sz in [-1,1] {
    let yaw=atan2(-Double(sx),Double(sz))*180 / Double.pi
    let route=TellyRoute(x:500.5,z:700.5,yaw:yaw)
    func reflect(_ v:Int,_ sign:Int,_ origin:Int)->Int {origin+(sign>0 ? v:-v-1)}
    let cells=Set([corner,nextCell].map {F3Block(x:reflect($0.x,sx,500),y:$0.y,z:reflect($0.z,sz,700))})
    let result=BridgeContinuationWindow.evaluate(solid:cells,floor:63,route:route,
        x:500+Double(sx)*1.1,z:700+Double(sz)*1.1,
        collisionX:500+Double(sx)*1.02,collisionZ:700+Double(sz)*1.02,requiredForward:0.35)
    check(result != nil,"连续支撑检查应在四个斜向和不同世界坐标下对称")
}}
check(BridgeContinuationWindow.evaluate(solid:[corner,nextCell],floor:63,route:corridorRoute,
    x:Double.nan,z:1,collisionX:1,collisionZ:1,requiredForward:0.2)==nil,"异常读数不能授权下一跳")
print("通过：下一跳连续支撑、薄角、断层、真实高度和四斜向对称性回归。")
