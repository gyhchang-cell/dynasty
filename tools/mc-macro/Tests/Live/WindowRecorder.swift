import AppKit
import ScreenCaptureKit
import AVFoundation

// Test-only recorder. Captures a single Minecraft window, never the desktop
// and never audio. This utility is not included in the distributed app.
final class WindowFeed:NSObject,SCStreamOutput {
    let writer:AVAssetWriter,input:AVAssetWriterInput
    let queue=DispatchQueue(label:"mc-test.recording")
    var began=false
    init(path:String,width:Int,height:Int)throws {
        writer=try AVAssetWriter(outputURL:URL(fileURLWithPath:path),fileType:.mov)
        input=AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:width,AVVideoHeightKey:height])
        input.expectsMediaDataInRealTime=true
        writer.add(input)
    }
    func stream(_ stream:SCStream,didOutputSampleBuffer sample:CMSampleBuffer,of type:SCStreamOutputType) {
        guard type == .screen,sample.isValid,
            let attachments=CMSampleBufferGetSampleAttachmentsArray(sample,createIfNecessary:false) as? [[SCStreamFrameInfo:Any]],
            attachments.first?[.status] as? Int == SCFrameStatus.complete.rawValue else{return}
        if !began {writer.startWriting();writer.startSession(atSourceTime:sample.presentationTimeStamp);began=true}
        if input.isReadyForMoreMediaData {input.append(sample)}
    }
}

@main struct RecordWindow {
    @MainActor static func main()async throws {
        NSApplication.shared.setActivationPolicy(.prohibited)
        let args=CommandLine.arguments
        guard args.count==4,let pid=Int32(args[1]),let seconds=Double(args[2]),seconds>0,seconds<=60 else{exit(2)}
        let content=try await SCShareableContent.excludingDesktopWindows(true,onScreenWindowsOnly:true)
        guard let window=content.windows.filter({$0.owningApplication?.processID==pid && $0.windowLayer==0 && $0.frame.height>250}).max(by:{$0.frame.width*$0.frame.height<$1.frame.width*$1.frame.height}) else{exit(3)}
        let config=SCStreamConfiguration()
        config.width=Int(window.frame.width)*2;config.height=Int(window.frame.height)*2
        config.minimumFrameInterval=CMTime(value:1,timescale:60)
        config.queueDepth=4;config.showsCursor=false;config.capturesAudio=false
        config.ignoreShadowsSingleWindow=true
        let feed=try WindowFeed(path:args[3],width:config.width,height:config.height)
        let stream=SCStream(filter:SCContentFilter(desktopIndependentWindow:window),configuration:config,delegate:nil)
        try stream.addStreamOutput(feed,type:.screen,sampleHandlerQueue:feed.queue)
        try await stream.startCapture()
        print("RECORDING",window.windowID,config.width,config.height)
        try await Task.sleep(nanoseconds:UInt64(seconds*1e9))
        try await stream.stopCapture()
        feed.queue.sync{feed.input.markAsFinished()}
        await feed.writer.finishWriting()
        guard feed.writer.status == .completed else{throw feed.writer.error ?? NSError(domain:"recording",code:1)}
        print("SAVED",args[3])
    }
}
