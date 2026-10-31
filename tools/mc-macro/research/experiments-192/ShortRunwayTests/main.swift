import Foundation
let block=F3Block(x:126021,y:79,z:22)
let pose=F3Pose(x:126021.83321887857,y:80,z:22.106700563429104,yaw:-45,pitch:87.95,time:0)
let route=TellyRoute(x:126000.5,z:0.5,yaw:-45)
let actual=TellyRoute(x:pose.x,z:pose.z,yaw:-45)
precondition(actual.runway(on:block)==nil,"Historical contact had a chord shorter than initial runup")
let span=route.landingRunway(on:block,from:pose)!
precondition(span.contains(route.along(pose.x,pose.z)))
precondition(span.upperBound-span.lowerBound<0.45)
let missing=F3Pose(x:126023,y:80,z:22.1,yaw:-45,pitch:0,time:0)
precondition(route.landingRunway(on:block,from:missing)==nil,"A path missing the top remains unsupported")
let cardinal=TellyRoute(x:0.5,z:0.5,yaw:0),cube=F3Block(x:0,y:79,z:0)
precondition(cardinal.landingRunway(on:cube,from:pose)==cardinal.runway(on:cube))
// Lateral landing SE20: body has support after movement, but the player's
// centre is already 0.015 past the top face. The usable chord is only 0.334.
let newBlock=F3Block(x:136030,y:79,z:31)
let newPose=F3Pose(x:136031.01489643214,y:80,z:31.25080923848212,yaw:-45,pitch:87.65,time:0)
let newRoute=TellyRoute(x:136000.5,z:0.5,yaw:-45)
precondition(TellyRoute(x:newPose.x,z:newPose.z,yaw:-45).runway(on:newBlock)==nil)
precondition(newPose.x-0.299999<Double(newBlock.x+1))
let newSpan=newRoute.landingRunway(on:newBlock,from:newPose)!
precondition(newSpan.upperBound-newSpan.lowerBound<0.45)
precondition(newRoute.along(newPose.x,newPose.z)>newSpan.upperBound)
print("Recorded short corner landing accepted; nonintersecting ray rejected; cardinal unchanged")
