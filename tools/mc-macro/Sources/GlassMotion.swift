import AppKit

// A finite UI spring. It sleeps at rest and cancels as soon as the app loses
// the key window, so rendering never becomes a background game workload.
final class GlassMotion {
    weak var owner:NSView?
    var changed:(()->Void)?
    private(set) var value=SIMD3<Double>(repeating:0)
    private var target=SIMD3<Double>(repeating:0)
    private var velocity=SIMD3<Double>(repeating:0)
    private var timer:Timer?
    private var last=0.0
    init(_ owner:NSView) {self.owner=owner}
    func aim(_ x:Double,_ y:Double,_ amount:Double) {
        target=SIMD3(x,y,amount)
        if NSWorkspace.shared.accessibilityDisplayShouldReduceMotion || owner?.window == nil {
            value=SIMD3(0,0,amount);changed?();return
        }
        guard timer == nil else{return}
        last=ProcessInfo.processInfo.systemUptime
        let t=Timer(timeInterval:1/60,repeats:true){[weak self] _ in self?.step()}
        timer=t;RunLoop.main.add(t,forMode:.common)
    }
    func snap(_ x:Double,_ y:Double,_ amount:Double) {
        timer?.invalidate();timer=nil;velocity = .zero;target=SIMD3(x,y,amount);value=target;changed?()
    }
    private func step() {
        guard let view=owner,view.window?.isKeyWindow == true,!view.isHiddenOrHasHiddenAncestor else {
            snap(0,0,target.z);return
        }
        let now=ProcessInfo.processInfo.systemUptime,dt=min(0.025,max(0.001,now-last));last=now
        velocity += ((target-value)*190-velocity*26)*dt
        value += velocity*dt
        changed?()
        let delta=target-value
        if abs(delta.x)+abs(delta.y)+abs(delta.z)<0.001 && abs(velocity.x)+abs(velocity.y)+abs(velocity.z)<0.01 {
            value=target;timer?.invalidate();timer=nil;changed?()
        }
    }
    deinit {timer?.invalidate()}
}

enum GlassPaint {
    static func color(_ r:CGFloat,_ g:CGFloat,_ b:CGFloat,_ a:CGFloat=1)->NSColor {NSColor(srgbRed:r,green:g,blue:b,alpha:a)}
    static func glow(at center:NSPoint,radius:CGFloat,color:NSColor) {
        guard let context=NSGraphicsContext.current?.cgContext,
              let gradient=CGGradient(colorsSpace:CGColorSpaceCreateDeviceRGB(),colors:[color.cgColor,color.withAlphaComponent(0).cgColor] as CFArray,locations:[0,1]) else{return}
        context.drawRadialGradient(gradient,startCenter:center,startRadius:0,endCenter:center,endRadius:radius,options:[])
    }
    static func edge(_ path:NSBezierPath,strong:Bool=false) {
        NSGraphicsContext.saveGraphicsState();path.addClip()
        NSGradient(colors:[NSColor.white.withAlphaComponent(strong ? 0.42:0.2),NSColor.white.withAlphaComponent(0.025),NSColor.white.withAlphaComponent(0.11)])?.draw(in:path,angle:90)
        NSGraphicsContext.restoreGraphicsState()
    }
    static func outline(_ rect:NSRect,radius:CGFloat,selected:Bool=false) {
        let outer=NSBezierPath(roundedRect:rect,xRadius:radius,yRadius:radius)
        (selected ? Chrome.accent.withAlphaComponent(0.7):NSColor.white.withAlphaComponent(0.16)).setStroke();outer.lineWidth=0.75;outer.stroke()
        let inner=NSBezierPath(roundedRect:rect.insetBy(dx:1,dy:1),xRadius:max(1,radius-1),yRadius:max(1,radius-1))
        NSColor.white.withAlphaComponent(0.035).setStroke();inner.lineWidth=0.5;inner.stroke()
    }
}
