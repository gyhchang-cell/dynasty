import Foundation
import AppKit
import Vision

let fontImage = NSImage(contentsOfFile: CommandLine.arguments[1])!.cgImage(forProposedRect:nil,context:nil,hints:nil)!
let asciiReader = F3PixelReader(font:fontImage)!
let fontURL = URL(fileURLWithPath: CommandLine.arguments[1]).deletingLastPathComponent()
let unicodeImage = NSImage(contentsOf: fontURL.appendingPathComponent("unicode.png"))?.cgImage(forProposedRect:nil,context:nil,hints:nil)
let unicodeReader = unicodeImage.flatMap { image in (try? Data(contentsOf:fontURL.appendingPathComponent("sizes.bin"))).flatMap { F3PixelReader(unicodeFont:image,sizes:$0) } }
for path in CommandLine.arguments.dropFirst(2) {
    guard let image = NSImage(contentsOfFile: path)?.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fatalError("fixture missing") }
    let pixelBegan = ProcessInfo.processInfo.systemUptime
    let pixelPose = unicodeReader?.read(image,time:pixelBegan) ?? asciiReader.read(image,time:pixelBegan)
    if path.contains("f3-real") {
        guard let pose = pixelPose else { fatalError("实际 Unicode 截图必须识别成功") }
        precondition(pose.x == 2000.515 && pose.y == 80 && pose.z == 4.3 && pose.yaw == 178.6 && pose.pitch == 82.2)
        precondition(pose.looking == F3Block(x:2000,y:79,z:3))
    }
    print("pixel \(URL(fileURLWithPath:path).lastPathComponent) \(Int((ProcessInfo.processInfo.systemUptime-pixelBegan)*1000))ms parsed=\(pixelPose != nil)")
    precondition(pixelPose != nil, "像素识别必须成功")
    if path.contains("target") { precondition(pixelPose?.looking == F3Block(x:-124,y:63,z:986), "准星目标坐标必须准确读取") }
    if path.contains("f3-") && !path.contains("f3-real"), let pose=pixelPose { precondition(pose.x == -123.45 && pose.y == 64 && pose.z == 987.625 && pose.yaw == -179.9 && pose.pitch == 72) }
    for level in [VNRequestTextRecognitionLevel.fast, .accurate] {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = level; request.usesLanguageCorrection = false; request.recognitionLanguages = ["en-US"]
        request.regionOfInterest = CGRect(x:0,y:0.2,width:1,height:0.8)
        let began = ProcessInfo.processInfo.systemUptime
        try VNImageRequestHandler(cgImage:image).perform([request])
        let text = (request.results ?? []).sorted { $0.boundingBox.midY > $1.boundingBox.midY }.compactMap { observation -> String? in
            guard let candidate=observation.topCandidates(1).first,candidate.confidence>=0.65 else{return nil}
            return candidate.string
        }.joined(separator:"\n")
        let pose = F3Pose.parse(text,time:began)
        print("\(URL(fileURLWithPath:path).lastPathComponent) \(level == .fast ? "fast" : "accurate") \(Int((ProcessInfo.processInfo.systemUptime-began)*1000))ms parsed=\(pose != nil)")
        if path.contains("f3-") && !path.contains("f3-real"), let pose { precondition(pose.x == -123.45 && pose.y == 64 && pose.z == 987.625 && pose.yaw == -179.9 && pose.pitch == 72,"识别数值错误") }
        else { print(text) }
    }
}
