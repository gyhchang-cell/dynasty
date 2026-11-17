import AppKit

// Original vector models, projected at draw time. Solid adjoining faces make the
// two routes readable at 1x; pointer parallax changes the camera, not the mode.
enum BridgeArtwork {
    private struct Cell:Hashable {let x:Int;let y:Int;let z:Int}
    struct Block {var x:Double;var y:Double;var z:Double;var platform:Bool=false;var end:Bool=false}
    static func draw(in rect:NSRect,rising:Bool,selected:Bool,pointer:SIMD3<Double>) {
        guard let cg=NSGraphicsContext.current?.cgContext else{return}
        cg.saveGState();defer{cg.restoreGState()}
        cg.clip(to:rect)
        let scale=rect.width/240
        cg.translateBy(x:rect.minX,y:rect.minY);cg.scaleBy(x:scale,y:scale)
        let px=pointer.x,py=pointer.y
        let yaw=px*0.17, c=cos(yaw),s=sin(yaw)
        func project(_ x:Double,_ y:Double,_ z:Double)->NSPoint {
            let u=(x-1.6)*c+z*s, d=z*c-(x-1.6)*s
            return NSPoint(x:109+u*23+d*11+px*3,y:(rising ? 94:78)+d*9-y*19+py*(u*0.9+2))
        }
        func face(_ points:[NSPoint],_ color:NSColor) {
            let path=NSBezierPath();path.move(to:points[0]);for p in points.dropFirst(){path.line(to:p)};path.close()
            color.setFill();path.fill()
            NSColor.black.withAlphaComponent(0.22).setStroke();path.lineWidth=0.55;path.stroke()
        }
        let shadow=NSBezierPath(ovalIn:NSRect(x:21,y:95,width:198,height:13))
        NSGraphicsContext.saveGraphicsState()
        let soft=NSShadow();soft.shadowColor=NSColor.black.withAlphaComponent(0.65);soft.shadowBlurRadius=12;soft.shadowOffset = .zero;soft.set()
        NSColor.black.withAlphaComponent(0.1).setFill();shadow.fill();NSGraphicsContext.restoreGraphicsState()
        var blocks:[Block]=[]
        for x in -2 ... -1 {for z in -1 ... 1 {blocks.append(Block(x:Double(x),y:0,z:Double(z),platform:true))}}
        for x in 0..<6 {
            let height=rising ? x/2:0
            // Keep the small illustration a continuous stepped silhouette.
            for y in 0...height {blocks.append(Block(x:Double(x),y:Double(y),z:0,end:x==5 && y==height))}
        }
        blocks.sort{($0.z*4+$0.x*0.1)<($1.z*4+$1.x*0.1)}
        let occupied=Set(blocks.map{Cell(x:Int($0.x),y:Int($0.y),z:Int($0.z))})
        for b in blocks {
            let x=b.x,y=b.y,z=b.z
            let tint=selected ? GlassPaint.color(0.64,0.91,0.80):GlassPaint.color(0.67,0.79,0.94)
            let top=b.platform ? GlassPaint.color(0.35,0.40,0.48):b.end ? tint:GlassPaint.color(0.86,0.91,0.94)
            let front=b.platform ? GlassPaint.color(0.20,0.24,0.30):b.end ? tint.blended(withFraction:0.30,of:.black)!:GlassPaint.color(0.48,0.62,0.70)
            let right=b.platform ? GlassPaint.color(0.15,0.18,0.23):b.end ? tint.blended(withFraction:0.50,of:.black)!:GlassPaint.color(0.32,0.43,0.53)
            if !occupied.contains(Cell(x:Int(x)+1,y:Int(y),z:Int(z))) {face([project(x+1,y,z),project(x+1,y,z+1),project(x+1,y+1,z+1),project(x+1,y+1,z)],right)}
            if !occupied.contains(Cell(x:Int(x),y:Int(y),z:Int(z)+1)) {face([project(x,y,z+1),project(x+1,y,z+1),project(x+1,y+1,z+1),project(x,y+1,z+1)],front)}
            let topVisible = !occupied.contains(Cell(x:Int(x),y:Int(y)+1,z:Int(z)))
            if topVisible {face([project(x,y+1,z),project(x+1,y+1,z),project(x+1,y+1,z+1),project(x,y+1,z+1)],top)}
            // Tiny face insets suggest blocks without copying game textures.
            let shine=NSBezierPath();shine.move(to:project(x+0.07,y+1,z+0.06));shine.line(to:project(x+0.94,y+1,z+0.06))
            if topVisible {NSColor.white.withAlphaComponent(b.platform ? 0.12:0.45).setStroke();shine.lineWidth=0.6;shine.stroke()}
        }
        // A single direction cue follows the actual top edge, keeping the
        // level route horizontal and the rising route unmistakably stepped.
        let a=project(0.6,rising ? 2.5:2.0,0.1),b=project(4.8,rising ? 4.1:2.0,0.1)
        let arrow=NSBezierPath();arrow.move(to:a);arrow.line(to:b)
        let angle=atan2(b.y-a.y,b.x-a.x)
        for sign in [-1.0,1.0] {arrow.move(to:NSPoint(x:b.x-5*cos(angle+sign*0.6),y:b.y-5*sin(angle+sign*0.6)));arrow.line(to:b)}
        Chrome.ink.withAlphaComponent(0.35).setStroke();arrow.lineWidth=1;arrow.stroke()
    }
}
