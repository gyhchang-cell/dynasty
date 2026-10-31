import Foundation

// Experimental geometry only; this is not part of the released app.
// Eye positions may disagree across a logical tick and an interpolated frame.
// A nonexistent overlap must not be silently treated as a visible side face.
extension TellyPlacement {
    func sidePitchWindow(eyes:[F3Pose], yaw:Double, eyeHeight:Double,
                         inset:Double=0.08) -> ClosedRange<Double>? {
        guard axis==0 || axis==2, !eyes.isEmpty, yaw.isFinite,
              eyeHeight.isFinite, inset>0, inset<0.5 else {return nil}
        let angle=yaw * .pi/180, dx = -sin(angle), dz=cos(angle)
        let direction=axis==0 ? dx:dz
        guard abs(direction)>1e-8 else {return nil}
        var lower = -88.0, upper=88.0
        for eye in eyes {
            guard eye.x.isFinite,eye.y.isFinite,eye.z.isFinite,
                  isExposed(from:eye) else {return nil}
            let distance=(axis==0 ? x-eye.x:z-eye.z)/direction
            guard distance>0 else {return nil}
            let lateral=axis==0 ? eye.z+dz*distance:eye.x+dx*distance
            let edge=Double(axis==0 ? support.z:support.x)
            guard lateral>edge+inset,lateral<edge+1-inset else {return nil}
            let a=atan2(eye.y+eyeHeight-Double(support.y)-1+inset,distance)*180 / .pi
            let b=atan2(eye.y+eyeHeight-Double(support.y)-inset,distance)*180 / .pi
            lower=max(lower,min(a,b));upper=min(upper,max(a,b))
        }
        return lower<=upper ? lower...upper:nil
    }
}
