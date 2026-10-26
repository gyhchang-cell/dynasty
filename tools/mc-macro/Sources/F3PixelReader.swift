import CoreGraphics
import Foundation

// Runtime templates come from the user's installed client, not bundled game assets.
final class F3PixelReader {
    struct Glyph {
        let character: Character
        let width: Int
        let mask: [Bool]
    }
    let cellSize: Int
    let glyphs: [Glyph]
    let byCharacter: [Character: Glyph]
    private var layout: (width: Int, height: Int, scale: Int, x: Int, xyzY: Int, facingY: Int)?

    private static func pixels(_ image: CGImage) -> [UInt8]? {
        var bytes = [UInt8](repeating: 0, count: image.width * image.height * 4)
        let okay = bytes.withUnsafeMutableBytes { storage -> Bool in
            guard let context = CGContext(data: storage.baseAddress, width: image.width, height: image.height, bitsPerComponent: 8,
                bytesPerRow: image.width * 4, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue) else { return false }
            context.draw(image, in: CGRect(x:0,y:0,width:image.width,height:image.height))
            return true
        }
        return okay ? bytes : nil
    }

    init?(font: CGImage) {
        cellSize = 8
        guard font.width == 128, font.height == 128, let bytes = Self.pixels(font) else { return nil }
        var glyphs: [Glyph] = []
        for code in 32...126 {
            var mask = [Bool](repeating:false,count:64)
            var right = -1
            for y in 0..<8 { for x in 0..<8 {
                let offset = (((code / 16) * 8 + y) * 128 + (code % 16) * 8 + x) * 4
                let alpha = bytes[offset+3] > 100
                mask[y*8+x] = alpha
                if alpha { right = max(right,x) }
            } }
            glyphs.append(Glyph(character: Character(UnicodeScalar(code)!), width: code == 32 ? 4 : max(2,right+2), mask:mask))
        }
        self.glyphs = glyphs
        byCharacter = Dictionary(uniqueKeysWithValues: glyphs.map{($0.character,$0)})
    }

    init?(unicodeFont: CGImage, sizes: Data) {
        guard unicodeFont.width == 256, unicodeFont.height == 256, sizes.count >= 127,
              let bytes = Self.pixels(unicodeFont) else { return nil }
        cellSize = 16
        var glyphs: [Glyph] = []
        for code in 32...126 {
            let bounds = Int(sizes[code]), left = bounds >> 4, right = bounds & 15
            let rawWidth = right + 1 - left
            let advance = code == 32 ? 4 : rawWidth / 2 + 1
            var mask = [Bool](repeating: false, count: 256)
            if code != 32 {
                for y in 0..<16 { for x in 0..<max(0, rawWidth) {
                    let offset = (((code / 16) * 16 + y) * 256 + (code % 16) * 16 + left + x) * 4
                    mask[y * 16 + x] = bytes[offset + 3] > 100
                } }
            }
            glyphs.append(Glyph(character: Character(UnicodeScalar(code)!), width: advance, mask: mask))
        }
        self.glyphs = glyphs
        byCharacter = Dictionary(uniqueKeysWithValues: glyphs.map { ($0.character, $0) })
    }

    func read(_ image: CGImage, time: TimeInterval) -> F3Pose? {
        guard image.width >= 128, image.height >= 128 else { return nil }
        guard let rgba = Self.pixels(image) else { return nil }
        let width = image.width, height = image.height
        // CGContext's image rows match CGImage's top-origin storage.
        var ink = [UInt8](repeating:0,count:width*height)
        for i in 0..<(width*height) {
            let r=Int(rgba[i*4]), g=Int(rgba[i*4+1]), b=Int(rgba[i*4+2])
            if min(r,min(g,b)) >= 180 && max(r,max(g,b))-min(r,min(g,b)) < 55 { ink[i]=1 }
        }
        func error(_ glyph: Glyph, x: Int, y: Int, scale: Int, cutoff: Int) -> Int {
            guard x >= 0, y >= 0, x + glyph.width*scale < width, y+8*scale < height else { return 999 }
            var mistakes=0
            for row in 0..<cellSize { for col in 0..<(glyph.width*cellSize/8) {
                let actual=ink[(y+Int((Double(row)+0.5)*Double(scale)*8/Double(cellSize)))*width+x+Int((Double(col)+0.5)*Double(scale)*8/Double(cellSize))] != 0
                let expected=col<cellSize && glyph.mask[row*cellSize+col]
                if actual != expected { mistakes += 1; if mistakes>cutoff { return mistakes } }
            } }
            return mistakes
        }
        func prefix(_ text: String, x: Int, y: Int, scale: Int) -> Int? {
            var offset=x
            for character in text {
                guard let glyph=byCharacter[character], error(glyph,x:offset,y:y,scale:scale,cutoff:cellSize/8) <= cellSize/8 else { return nil }
                offset += glyph.width*scale
            }
            return offset
        }
        let numericGlyphs=glyphs.filter { "0123456789 -+./(),".contains($0.character) }
        func line(x: Int, y: Int, scale: Int, numeric: Bool = true) -> String {
            let candidates=numeric ? numericGlyphs:glyphs
            var x=x, result="", blanks=0
            for _ in 0..<140 {
                guard x+9*scale<width else { break }
                var winner: Glyph?, best=1.0
                for glyph in candidates {
                    let count=error(glyph,x:x,y:y,scale:scale,cutoff:cellSize)
                    let rate=Double(count)/Double(glyph.width*cellSize*cellSize/8)
                    if rate < best || (rate==best && glyph.width>(winner?.width ?? 0)) { best=rate;winner=glyph }
                }
                guard let glyph=winner,best<=0.13 else { break }
                result.append(glyph.character);x += glyph.width*scale
                blanks = glyph.character == " " ? blanks+1 : 0
                if blanks>=4 { break }
            }
            return result
        }
        func facingLine(x: Int,y: Int,scale: Int) -> String {
            for direction in [" north (Towards negative Z) ("," south (Towards positive Z) ("," east (Towards positive X) ("," west (Towards negative X) ("] {
                if let end=prefix(direction,x:x,y:y,scale:scale) { return "Facing: ("+line(x:end,y:y,scale:scale) }
            }
            return "Facing:"+line(x:x,y:y,scale:scale,numeric:false)
        }
        if let saved = layout, saved.width == width, saved.height == height,
           let xyzEnd = prefix("XYZ:",x:saved.x,y:saved.xyzY,scale:saved.scale),
           let facingEnd = prefix("Facing:",x:saved.x,y:saved.facingY,scale:saved.scale) {
            let text = "XYZ:"+line(x:xyzEnd,y:saved.xyzY,scale:saved.scale)+"\n"+facingLine(x:facingEnd,y:saved.facingY,scale:saved.scale)
            if let pose = F3Pose.parse(text,time:time) {
                for y in stride(from:saved.facingY, to:min(height-8*saved.scale,saved.facingY+16*9*saved.scale), by:9*saved.scale) {
                    if let end = prefix("Looking at:",x:saved.x,y:y,scale:saved.scale),
                       let full = F3Pose.parse(text+"\nLooking at:"+line(x:end,y:y,scale:saved.scale),time:time) { return full }
                }
                return pose
            }
        }
        layout = nil
        // F3 labels originate at the left margin. Searching the margin rejects right-hand chat and other HUD text.
        for scale in 1...8 {
            var xyz: String?, facing: String?
            var xyzY = 0, facingY = 0
            for y in 0..<min(height-8*scale,Int(Double(height)*0.7)) {
                for x in 0...max(12,4*scale) {
                    if xyz == nil, let end=prefix("XYZ:",x:x,y:y,scale:scale) { xyz="XYZ:"+line(x:end,y:y,scale:scale); xyzY = y }
                    if facing == nil, let end=prefix("Facing:",x:x,y:y,scale:scale) { facing=facingLine(x:end,y:y,scale:scale); facingY = y }
                    if let xyz, let facing, let result=F3Pose.parse(xyz+"\n"+facing,time:time) {
                        layout = (width,height,scale,x,xyzY,facingY)
                        for targetY in y..<min(height-8*scale,y+16*9*scale) {
                            if let end=prefix("Looking at:",x:x,y:targetY,scale:scale),
                               let full=F3Pose.parse(xyz+"\n"+facing+"\nLooking at:"+line(x:end,y:targetY,scale:scale),time:time) { return full }
                        }
                        return result
                    }
                }
            }
        }
        return nil
    }
}
