import Foundation

struct Target:Decodable {let time:Double,yaw:Double,pitch:Double}
struct Fixture:Decodable {
    let source:String,scope:String
    let initialYaw:Double,initialPitch:Double,degreesPerCount:Double,baselineLargestPitchEvent:Double
    let targets:[Target]
}
let fixture=try JSONDecoder().decode(Fixture.self,from:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
var follower=RelativeMouseFollower(yaw:fixture.initialYaw,pitch:fixture.initialPitch,now:0)
var rows=[[String:Double]](),peakPitch=0.0,reached:Double?
for i in 1...25 {
    let time=Double(i)*0.008
    let target=fixture.targets.last(where:{$0.time<=time}) ?? Target(time:0,yaw:fixture.initialYaw,pitch:fixture.initialPitch)
    let counts=follower.advance(yaw:target.yaw,pitch:target.pitch,now:time,gainX:fixture.degreesPerCount,gainY:fixture.degreesPerCount)
    let deltaPitch=Double(counts.1)*fixture.degreesPerCount
    peakPitch=max(peakPitch,abs(deltaPitch))
    if reached==nil && abs(follower.pitch-fixture.targets.last!.pitch)<1 {reached=time-fixture.targets[0].time}
    rows.append(["time":time,"targetYaw":target.yaw,"targetPitch":target.pitch,"yaw":follower.yaw,"pitch":follower.pitch,"pitchStep":deltaPitch])
}
let output:[String:Any]=["source":fixture.source,"scope":fixture.scope,"baselineLargestPitchEvent":fixture.baselineLargestPitchEvent,"candidateLargestPitchEvent":peakPitch,"candidateWithinOneDegreeMilliseconds":(reached ?? -1)*1000,"samples":rows]
let data=try JSONSerialization.data(withJSONObject:output,options:[.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(data);print("")
