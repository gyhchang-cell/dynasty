import Foundation
func check(_ value:Bool,_ why:String) {if !value {fatalError(why)}}
let base=F3Block(x:0,y:79,z:0)
for yaw in [-135.0,-45,45,135] {
    let route=TellyRoute(x:0.5,z:0.5,yaw:yaw)
    let xFace=route.ux>0 ? "east":"west",zFace=route.uz>0 ? "south":"north"
    for face in [xFace,zFace] {
        let target=route.placementAtHit(base,face:face,floor:79,front:base,solid:[base])
        check(target != nil,"either exposed forward side can continue a diagonal")
        check(target!.result.y==79,"level span must stay level")
        check(route.placementAtHit(base,face:face,floor:79,front:base,solid:[base,target!.result])==nil,"do not click a filled cell")
        check(route.placementAtHit(base,face:face,floor:80,front:base,solid:[base])==nil,"raised span must establish its top before extending sides")
    }
    check(route.placementAtHit(base,face:"up",floor:79,front:base,solid:[base])==nil,"cached roof hit must not add accidental height")
    check(route.placementAtHit(base,face:"up",floor:80,front:base,solid:[base]) != nil,"one intended rising top is allowed")
    check(route.placementAtHit(base,face:route.ux>0 ? "west":"east",floor:79,front:base,solid:[base])==nil,"reject reverse growth")
    check(route.placementAtHit(base,face:"down",floor:79,front:base,solid:[base])==nil,"reject underside")
    check(route.placementAtHit(base,face:xFace,floor:79,front:base,solid:[])==nil,"require observed support")
    let behind=F3Block(x:Int(-route.ux*5),y:79,z:Int(-route.uz*5))
    check(route.placementAtHit(behind,face:xFace,floor:79,front:base,solid:[base,behind])==nil,"reject a face behind the current route front")
}
print("PASS native face eligibility: four diagonal orientations, level/rise floor, occupied/absent/reverse/roof/behind rejection")
