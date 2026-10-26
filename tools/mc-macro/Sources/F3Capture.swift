import AppKit
import ScreenCaptureKit
import Vision
import ImageIO
import CoreImage
import CoreMedia

// Only the foreground Minecraft window. No screenshots or OCR text are saved.
final class F3Capture {
    var busy = false
    var generation = 0
    var lastRequest = 0.0
    var window: SCWindow?
    var windowCheckedAt = 0.0
    private let queue = DispatchQueue(label: "local.mc-macro.f3-ocr", qos: .userInteractive)
    private var pixelReaders: [F3PixelReader] = []
    private var configuredDirectory: String?

    func loadFont(directory: String) {
        queue.async { [weak self] in
            guard let self, self.configuredDirectory != directory else { return }
            self.configuredDirectory = directory; self.pixelReaders = []
            let initial = URL(fileURLWithPath: directory)
            let roots = [initial, initial.deletingLastPathComponent(), initial.deletingLastPathComponent().deletingLastPathComponent()]
            var candidates: [URL] = []
            for root in roots {
                candidates.append(root.appendingPathComponent("versions/1.8.9/1.8.9.jar"))
                candidates.append(root.appendingPathComponent(root.lastPathComponent + ".jar"))
            }
            for archive in candidates where FileManager.default.fileExists(atPath: archive.path) {
                func asset(_ name: String) -> Data? {
                    let process = Process(); process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
                    process.arguments = ["-p", archive.path, "assets/minecraft/" + name]
                    let pipe = Pipe(); process.standardOutput = pipe; process.standardError = FileHandle.nullDevice
                    do {
                        try process.run(); let data = pipe.fileHandleForReading.readDataToEndOfFile(); process.waitUntilExit()
                        return process.terminationStatus == 0 ? data : nil
                    } catch { return nil }
                }
                func image(_ name: String) -> CGImage? {
                    guard let data = asset(name), let source = CGImageSourceCreateWithData(data as CFData,nil) else { return nil }
                    return CGImageSourceCreateImageAtIndex(source,0,nil)
                }
                if let font = image("textures/font/unicode_page_00.png"), let sizes = asset("font/glyph_sizes.bin"),
                   let reader = F3PixelReader(unicodeFont:font,sizes:sizes) { self.pixelReaders.append(reader) }
                if let font = image("textures/font/ascii.png"), let reader = F3PixelReader(font:font) { self.pixelReaders.append(reader) }
                if !self.pixelReaders.isEmpty { return }
            }
        }
    }

    private var stream: SCStream?
    private var feed: F3FrameFeed?
    private var streamPID: pid_t?
    private var opening = false
    private var lastFrame = -1.0
    private var accessCheckedAt = -Double.infinity
    private var captureAllowed = false
    private let context = CIContext(options: [.cacheIntermediates:false])

    var running: Bool { stream != nil || opening }

    func reset() {
        generation += 1; window = nil; lastFrame = -1
        let old = stream; stream = nil; feed = nil; streamPID = nil
        old?.stopCapture { _ in }
    }

    func poll(pid: pid_t, completion: @escaping (F3Pose?, String) -> Void) {
        let now = ProcessInfo.processInfo.systemUptime
        guard !busy, now-lastRequest >= 0.016 else { return }
        if now-accessCheckedAt>0.5 {
            captureAllowed=CGPreflightScreenCaptureAccess(); accessCheckedAt=now
        }
        guard captureAllowed else { completion(nil,"屏幕录制权限不可用。"); return }
        guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else { completion(nil,"已切出游戏。"); return }
        if streamPID != pid || stream == nil {
            guard !opening else { return }
            opening = true
            let token = generation
            SCShareableContent.getExcludingDesktopWindows(true,onScreenWindowsOnly:true) { [weak self] content,_ in
                DispatchQueue.main.async {
                    guard let self else { return }
                    self.opening = false
                    guard token == self.generation else { return }
                    guard let target = content?.windows.filter({ $0.owningApplication?.processID == pid && $0.windowLayer == 0 && $0.frame.width >= 400 && $0.frame.height >= 250 }).max(by: { $0.frame.width*$0.frame.height < $1.frame.width*$1.frame.height }) else { completion(nil,"找不到游戏窗口。"); return }
                    let filter = SCContentFilter(desktopIndependentWindow:target)
                    let config = SCStreamConfiguration()
                    config.width = Int(target.frame.width*2); config.height = Int(target.frame.height*2)
                    config.minimumFrameInterval = CMTime(value:1,timescale:60)
                    config.queueDepth = 3; config.showsCursor = false
                    if #available(macOS 14.0, *) { config.ignoreShadowsSingleWindow = true }
                    let feed = F3FrameFeed()
                    let stream = SCStream(filter:filter,configuration:config,delegate:feed)
                    do { try stream.addStreamOutput(feed,type:.screen,sampleHandlerQueue:feed.queue) }
                    catch { completion(nil,"无法连接游戏画面。"); return }
                    self.stream = stream; self.feed = feed; self.streamPID = pid
                    stream.startCapture { error in
                        if error != nil { DispatchQueue.main.async { self.reset(); completion(nil,"游戏画面采集未启动。") } }
                    }
                }
            }
            return
        }
        guard let (buffer,started) = feed?.latest(), started > lastFrame else { return }
        let sampledNow=ProcessInfo.processInfo.systemUptime
        guard started <= sampledNow else { return }
        guard sampledNow-started < 0.20 else { completion(nil,"游戏画面已超时。"); return }
        lastFrame = started; lastRequest = now; busy = true
        let token = generation
        func finish(_ pose: F3Pose?, _ message: String) {
            DispatchQueue.main.async { [weak self] in
                guard let self else { return }
                self.busy = false
                guard self.generation == token else { return }
                completion(pose,message)
            }
        }
        guard let image = context.createCGImage(CIImage(cvPixelBuffer:buffer),from:CGRect(x:0,y:0,width:CVPixelBufferGetWidth(buffer),height:CVPixelBufferGetHeight(buffer))) else { busy = false; completion(nil,"无法读取游戏画面。"); return }
        self.queue.async {
                    autoreleasepool {
                        for index in self.pixelReaders.indices {
                            if let pose = self.pixelReaders[index].read(image,time:started) {
                                if index != 0 { self.pixelReaders.swapAt(0,index) }
                                finish(pose, ""); return
                            }
                        }
                        let request = VNRecognizeTextRequest()
                        request.recognitionLevel = .fast
                        request.usesLanguageCorrection = false
                        request.recognitionLanguages = ["en-US"]
                        // Full width includes menu/death indicators; F3 is normally in the top portion.
                        request.regionOfInterest = CGRect(x: 0, y: 0.2, width: 1, height: 0.8)
                        do {
                            try VNImageRequestHandler(cgImage: image).perform([request])
                            let lines = (request.results ?? []).sorted { a,b in
                                if abs(a.boundingBox.midY - b.boundingBox.midY) > 0.008 { return a.boundingBox.midY > b.boundingBox.midY }
                                return a.boundingBox.minX < b.boundingBox.minX
                            }.compactMap { observation -> String? in
                                guard let candidate = observation.topCandidates(1).first, candidate.confidence >= 0.65 else { return nil }
                                return candidate.string
                            }
                            let pose = F3Pose.parse(lines.joined(separator: "\n"), time: started)
                            finish(pose, pose == nil ? "未识别到完整 F3 坐标和朝向，请开启 F3。" : "")
                        } catch { finish(nil, "F3 文字识别失败，已暂停输入。") }
                    }
                }
    }
}

private final class F3FrameFeed: NSObject, SCStreamOutput, SCStreamDelegate {
    let queue = DispatchQueue(label:"local.mc-macro.frames",qos:.userInteractive)
    private let lock = NSLock()
    private var frame: (CVPixelBuffer,Double)?
    func latest() -> (CVPixelBuffer,Double)? { lock.lock(); defer { lock.unlock() }; return frame }
    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .screen, sampleBuffer.isValid, let buffer = sampleBuffer.imageBuffer,
              let attachments = CMSampleBufferGetSampleAttachmentsArray(sampleBuffer,createIfNecessary:false) as? [[SCStreamFrameInfo:Any]],
              let status = attachments.first?[.status] as? Int, status == SCFrameStatus.complete.rawValue else { return }
        let presentation = sampleBuffer.presentationTimeStamp.seconds
        guard presentation.isFinite else { return }
        // A complete buffer may arrive before its scheduled presentation time.
        // Keep it usable immediately, without making its age negative or moving
        // old presentations forward. Receipt is the upper bound for freshness.
        let time = min(presentation,ProcessInfo.processInfo.systemUptime)
        lock.lock(); frame = (buffer,time); lock.unlock()
    }
    func stream(_ stream: SCStream, didStopWithError error: Error) { lock.lock(); frame = nil; lock.unlock() }
}
