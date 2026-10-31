import AppKit
import ApplicationServices

// Local, static AppKit surfaces. No web view, animation loop, or game-thread work.
enum Chrome {
    static let base = NSColor(srgbRed: 0.067, green: 0.075, blue: 0.082, alpha: 1)
    static let surface = NSColor(srgbRed: 0.105, green: 0.117, blue: 0.129, alpha: 1)
    static let ink = NSColor(srgbRed: 0.93, green: 0.95, blue: 0.94, alpha: 1)
    static let muted = NSColor(srgbRed: 0.56, green: 0.60, blue: 0.63, alpha: 1)
    static let accent = NSColor(srgbRed: 0.71, green: 0.86, blue: 0.79, alpha: 1)
    static let line = NSColor.white.withAlphaComponent(0.075)
    static func text(_ value:String, size:CGFloat=12, weight:NSFont.Weight = .regular, color:NSColor = ink) -> NSTextField {
        let field=NSTextField(labelWithString:value)
        field.font = .systemFont(ofSize:size,weight:weight);field.textColor=color
        field.lineBreakMode = .byTruncatingTail
        return field
    }
    static func place(_ view:NSView, in parent:NSView, _ x:CGFloat,_ y:CGFloat,_ w:CGFloat,_ h:CGFloat) {
        view.frame=NSRect(x:x,y:y,width:w,height:h);parent.addSubview(view)
    }
    static func symbol(_ name:String, size:CGFloat=15) -> NSImage? {
        NSImage(systemSymbolName:name,accessibilityDescription:nil)?.withSymbolConfiguration(.init(pointSize:size,weight:.medium))
    }
    static func rule(in parent:NSView,y:CGFloat,width:CGFloat) {
        let rule=NSView(frame:NSRect(x:20,y:y,width:width-40,height:1));rule.wantsLayer=true;rule.layer?.backgroundColor=line.cgColor;parent.addSubview(rule)
    }
}

// Record keys in the settings window itself; it also works with accessibility
// key delivery and does not depend on a global input permission to edit a setting.
final class PanelWindow:NSWindow {
    var captureKey:((UInt16)->Bool)?
    override func sendEvent(_ event:NSEvent) {
        if event.type == .keyDown,!event.modifierFlags.contains(.command),captureKey?(event.keyCode) == true {return}
        super.sendEvent(event)
    }
}

final class PanelSurface:NSView {
    var card=false
    private var tracking:NSTrackingArea?
    private lazy var motion:GlassMotion = {let m=GlassMotion(self);m.changed={ [weak self] in self?.needsDisplay=true };return m}()
    override var isFlipped:Bool {true}
    init(frame:NSRect = .zero,card:Bool=false) {self.card=card;super.init(frame:frame)}
    required init?(coder:NSCoder) {fatalError()}
    override func updateTrackingAreas() {
        if let tracking {removeTrackingArea(tracking)}
        tracking=NSTrackingArea(rect:.zero,options:[.activeInKeyWindow,.mouseMoved,.mouseEnteredAndExited,.inVisibleRect,.enabledDuringMouseDrag],owner:self,userInfo:nil)
        addTrackingArea(tracking!);super.updateTrackingAreas()
    }
    override func mouseMoved(with event:NSEvent) {let p=convert(event.locationInWindow,from:nil);motion.aim(Double(p.x/max(1,bounds.width)*2-1),Double(p.y/max(1,bounds.height)*2-1),1)}
    override func mouseEntered(with event:NSEvent) {mouseMoved(with:event)}
    override func mouseExited(with event:NSEvent) {motion.aim(0,0,0)}
    override func draw(_ dirtyRect:NSRect) {
        let path=NSBezierPath(roundedRect:bounds.insetBy(dx:0.5,dy:0.5),xRadius:card ? 22:0,yRadius:card ? 22:0)
        NSGraphicsContext.saveGraphicsState();path.addClip()
        if card {
            NSGradient(colors:[GlassPaint.color(0.19,0.23,0.29,0.96),GlassPaint.color(0.105,0.13,0.17,0.96)])?.draw(in:path,angle:90)
            GlassPaint.glow(at:NSPoint(x:bounds.width*0.08,y:0),radius:bounds.width*0.7,color:GlassPaint.color(0.59,0.76,0.92,0.08))
        } else {
            NSGradient(starting:GlassPaint.color(0.09,0.13,0.19),ending:GlassPaint.color(0.045,0.055,0.075))?.draw(in:path,angle:90)
            GlassPaint.glow(at:NSPoint(x:0,y:bounds.height*0.35),radius:bounds.width*0.8,color:GlassPaint.color(0.15,0.50,0.67,0.16))
            GlassPaint.glow(at:NSPoint(x:bounds.width,y:bounds.height*0.9),radius:bounds.width*0.7,color:GlassPaint.color(0.27,0.35,0.64,0.15))
        }
        let v=motion.value
        if v.z>0.001 {GlassPaint.glow(at:NSPoint(x:(v.x+1)*0.5*bounds.width,y:(v.y+1)*0.5*bounds.height),radius:card ? 210:300,color:NSColor.white.withAlphaComponent(CGFloat(v.z)*(card ? 0.055:0.045)))}
        NSGraphicsContext.restoreGraphicsState()
        if card {GlassPaint.outline(bounds.insetBy(dx:0.5,dy:0.5),radius:22)}
    }
}

class PanelButton:NSButton {
    var hover=false
    var quiet=false
    var symbolName:String?
    private var tracking:NSTrackingArea?
    lazy var motion:GlassMotion = {let m=GlassMotion(self);m.changed={ [weak self] in self?.needsDisplay=true };return m}()
    convenience init(_ title:String,target:AnyObject?,action:Selector?) {
        self.init(frame:.zero);self.title=title;self.target=target;self.action=action
        isBordered=false;setButtonType(.momentaryPushIn);font = .systemFont(ofSize:12,weight:.medium);focusRingType = .default
    }
    override func updateTrackingAreas() {
        if let tracking {removeTrackingArea(tracking)}
        tracking=NSTrackingArea(rect:.zero,options:[.activeInKeyWindow,.mouseMoved,.mouseEnteredAndExited,.inVisibleRect,.enabledDuringMouseDrag],owner:self,userInfo:nil)
        addTrackingArea(tracking!);super.updateTrackingAreas()
    }
    override func mouseEntered(with event:NSEvent) {hover=true;mouseMoved(with:event)}
    override func mouseExited(with event:NSEvent) {hover=false;motion.aim(0,0,0)}
    override func mouseMoved(with event:NSEvent) {
        let p=convert(event.locationInWindow,from:nil)
        motion.aim(max(-1,min(1,Double(p.x/max(1,bounds.width)*2-1))),max(-1,min(1,Double(p.y/max(1,bounds.height)*2-1))),1)
    }
    override func draw(_ dirtyRect:NSRect) {
        let path=NSBezierPath(roundedRect:bounds.insetBy(dx:0.5,dy:0.5),xRadius:bounds.height/2,yRadius:bounds.height/2)
        NSGradient(starting:NSColor.white.withAlphaComponent(isHighlighted ? 0.16:0.10),ending:NSColor.white.withAlphaComponent(quiet ? 0.025:0.04))?.draw(in:path,angle:90)
        GlassPaint.outline(bounds.insetBy(dx:0.5,dy:0.5),radius:bounds.height/2)
        if motion.value.z>0.001 {
            NSGraphicsContext.saveGraphicsState();path.addClip()
            GlassPaint.glow(at:NSPoint(x:(motion.value.x+1)/2*bounds.width,y:(motion.value.y+1)/2*bounds.height),radius:44,color:NSColor.white.withAlphaComponent(CGFloat(motion.value.z)*0.15));NSGraphicsContext.restoreGraphicsState()
        }
        let color=isEnabled ? Chrome.ink:Chrome.muted
        if let symbolName,let icon=Chrome.symbol(symbolName) {
            icon.isTemplate=true
            let image=NSImage(size:icon.size,flipped:false){r in color.set();r.fill();icon.draw(in:r,from:.zero,operation:.destinationIn,fraction:1);return true}
            image.draw(in:NSRect(x:(bounds.width-16)/2,y:(bounds.height-16)/2,width:16,height:16))
        } else {
            let text=NSAttributedString(string:title,attributes:[.font:font ?? NSFont.systemFont(ofSize:12),.foregroundColor:color]);let size=text.size()
            text.draw(at:NSPoint(x:(bounds.width-size.width)/2,y:(bounds.height-size.height)/2))
        }
        if window?.firstResponder === self {NSColor.keyboardFocusIndicatorColor.setStroke();path.lineWidth=2;path.stroke()}
    }
}

final class PanelSwitch:PanelButton {
    private lazy var slide:GlassMotion = {let m=GlassMotion(self);m.changed={ [weak self] in self?.needsDisplay=true };return m}()
    convenience init(_ label:String) {self.init(label,target:nil,action:nil);setButtonType(.toggle);setAccessibilityLabel(label);setAccessibilityRole(.checkBox)}
    override var state:NSControl.StateValue {didSet {
        guard state != oldValue else{return}
        let target=state == .on ? 1.0:0.0
        if window == nil {slide.snap(0,0,target)} else {slide.aim(0,0,target)}
        needsDisplay=true
    }}
    override func draw(_ dirtyRect:NSRect) {
        let t=CGFloat(max(0,min(1,slide.value.z)))
        let rect=bounds.insetBy(dx:0.5,dy:1)
        let track=NSBezierPath(roundedRect:rect,xRadius:rect.height/2,yRadius:rect.height/2)
        let off=GlassPaint.color(0.20,0.24,0.30),on=GlassPaint.color(0.34,0.76,0.59)
        let color=off.blended(withFraction:t,of:on)!
        NSGradient(starting:color.blended(withFraction:0.15,of:.white)!,ending:color)?.draw(in:track,angle:90)
        GlassPaint.outline(rect,radius:rect.height/2)
        let diameter=bounds.height-7,travel=bounds.width-diameter-8
        let knob=NSBezierPath(ovalIn:NSRect(x:4+t*travel,y:3.5,width:diameter,height:diameter))
        NSGraphicsContext.saveGraphicsState()
        let shadow=NSShadow();shadow.shadowColor=NSColor.black.withAlphaComponent(0.4);shadow.shadowBlurRadius=3;shadow.shadowOffset=NSSize(width:0,height:1);shadow.set()
        NSColor.white.setFill();knob.fill();NSGraphicsContext.restoreGraphicsState()
        NSGradient(starting:.white,ending:GlassPaint.color(0.80,0.85,0.90))?.draw(in:knob,angle:90)
        if window?.firstResponder === self {NSColor.keyboardFocusIndicatorColor.setStroke();track.lineWidth=2;track.stroke()}
    }
}

final class RangeRail:NSView {
    var low=15.0 {didSet{needsDisplay=true}}
    var high=20.0 {didSet{needsDisplay=true}}
    override func draw(_ dirtyRect:NSRect) {
        for i in 1...40 {
            let x=CGFloat(i-1)/39*(bounds.width-2)+1
            let active=Double(i)>=low && Double(i)<=high
            (active ? Chrome.accent:Chrome.muted.withAlphaComponent(0.24)).setStroke()
            let path=NSBezierPath();path.lineWidth=active ? 2:1
            path.move(to:NSPoint(x:x,y:2));path.line(to:NSPoint(x:x,y:(i%5==0) ? 13:8));path.stroke()
        }
    }
}

final class BridgeChoice:PanelButton {
    var rising=false
    override var state:NSControl.StateValue {didSet{if state != oldValue {needsDisplay=true};setAccessibilityValue(state == .on ? 1:0)}}
    private var pressOrigin:NSPoint?
    private var dragged=false
    override func mouseDown(with event:NSEvent) {
        pressOrigin=convert(event.locationInWindow,from:nil);dragged=false;mouseMoved(with:event)
    }
    override func mouseDragged(with event:NSEvent) {
        guard let origin=pressOrigin else{return}
        let p=convert(event.locationInWindow,from:nil)
        if hypot(p.x-origin.x,p.y-origin.y)>4 {dragged=true}
        motion.aim(max(-1.5,min(1.5,Double(p.x/bounds.width*2-1)*1.5)),max(-1.5,min(1.5,Double(p.y/bounds.height*2-1)*1.5)),1)
    }
    override func mouseUp(with event:NSEvent) {
        guard pressOrigin != nil else{return}
        pressOrigin=nil
        let p=convert(event.locationInWindow,from:nil)
        if !dragged,bounds.contains(p) {performClick(nil)}
        if !bounds.contains(p) {motion.aim(0,0,0)} else {mouseMoved(with:event)}
    }
    override func draw(_ dirtyRect:NSRect) {
        let chosen=state == .on,v=motion.value
        NSGraphicsContext.saveGraphicsState();defer{NSGraphicsContext.restoreGraphicsState()}
        if let cg=NSGraphicsContext.current?.cgContext {
            cg.translateBy(x:bounds.midX,y:bounds.midY)
            cg.concatenate(CGAffineTransform(a:1,b:v.x*0.014,c:-v.y*0.018,d:1,tx:v.x,ty:-v.z))
            cg.translateBy(x:-bounds.midX,y:-bounds.midY)
        }
        let rect=bounds.insetBy(dx:4,dy:4),path=NSBezierPath(roundedRect:rect,xRadius:19,yRadius:19)
        NSGraphicsContext.saveGraphicsState();path.addClip()
        let upper=chosen ? GlassPaint.color(0.20,0.31,0.34):GlassPaint.color(0.18,0.23,0.30)
        NSGradient(starting:upper,ending:GlassPaint.color(0.075,0.105,0.15))?.draw(in:path,angle:90)
        GlassPaint.glow(at:NSPoint(x:bounds.width*0.55,y:bounds.height*0.60),radius:135,color:(chosen ? Chrome.accent:GlassPaint.color(0.50,0.67,0.89)).withAlphaComponent(0.095))
        BridgeArtwork.draw(in:NSRect(x:0,y:25,width:bounds.width,height:bounds.height-29),rising:rising,selected:chosen,pointer:v)
        if v.z>0.001 {
            let p=NSPoint(x:(v.x+1)*0.5*bounds.width,y:(v.y+1)*0.5*bounds.height)
            GlassPaint.glow(at:p,radius:112,color:NSColor.white.withAlphaComponent(CGFloat(v.z)*0.18))
            let glint=NSBezierPath();glint.move(to:NSPoint(x:p.x-70,y:0));glint.line(to:NSPoint(x:p.x+36,y:bounds.height));glint.lineWidth=30
            NSColor.white.withAlphaComponent(CGFloat(v.z)*0.025).setStroke();glint.stroke()
        }
        NSGraphicsContext.restoreGraphicsState()
        GlassPaint.outline(rect,radius:19,selected:chosen)
        let text=NSAttributedString(string:title,attributes:[.font:NSFont.systemFont(ofSize:13,weight:.medium),.foregroundColor:Chrome.ink])
        text.draw(at:NSPoint(x:17,y:14))
        let ring=NSBezierPath(ovalIn:NSRect(x:bounds.width-30,y:16,width:13,height:13))
        if chosen {
            Chrome.accent.setFill();ring.fill()
            let check=NSBezierPath();check.move(to:NSPoint(x:bounds.width-27,y:22.5));check.line(to:NSPoint(x:bounds.width-24.2,y:25));check.line(to:NSPoint(x:bounds.width-20,y:20));check.lineWidth=1.4
            Chrome.base.setStroke();check.stroke()
        } else {NSColor.white.withAlphaComponent(0.22).setStroke();ring.lineWidth=0.8;ring.stroke()}
        if window?.firstResponder === self {NSColor.keyboardFocusIndicatorColor.setStroke();path.lineWidth=2;path.stroke()}
    }
}

extension MacroApp:NSTextFieldDelegate {
    func buildDashboard() {
        window=PanelWindow(contentRect:NSRect(x:0,y:0,width:580,height:716),styleMask:[.titled,.closable,.miniaturizable,.fullSizeContentView],backing:.buffered,defer:false)
        (window as? PanelWindow)?.captureKey = { [weak self] code in
            guard let self,self.recordingHotkey else{return false};self.captureHotkey(code);return true
        }
        window.title="mcPvPmax";window.titleVisibility = .hidden;window.titlebarAppearsTransparent=true
        window.backgroundColor=Chrome.base;window.appearance=NSAppearance(named:.darkAqua)
        window.isReleasedWhenClosed=false;window.acceptsMouseMovedEvents=true;window.center()
        let root=PanelSurface();window.contentView=root
        let dot=NSImageView();dot.image=Chrome.symbol("cube.transparent",size:18);dot.contentTintColor=Chrome.accent
        Chrome.place(dot,in:root,26,40,20,22)
        targetLabel.font = .systemFont(ofSize:12,weight:.medium);targetLabel.textColor=Chrome.muted;targetLabel.maximumNumberOfLines=1
        Chrome.place(targetLabel,in:root,55,40,420,22)
        settingsButton=PanelButton("设置",target:self,action:#selector(showPreferences));settingsButton.symbolName="slider.horizontal.3"
        settingsButton.toolTip="设置";settingsButton.setAccessibilityLabel("设置");Chrome.place(settingsButton,in:root,522,35,32,32)

        let clicks=PanelSurface(card:true);Chrome.place(clicks,in:root,24,82,532,222)
        Chrome.place(Chrome.text("连点",size:16,weight:.semibold),in:clicks,20,19,100,24)
        clickStateLabel=Chrome.text("关",size:11,color:Chrome.muted);Chrome.place(clickStateLabel,in:clicks,408,23,36,20)
        clickSwitch.target=self;clickSwitch.action=#selector(toggleFromDashboard);Chrome.place(clickSwitch,in:clicks,466,18,44,26)
        hotkeyButton=PanelButton(hotkeyTitle(),target:self,action:#selector(recordKey));hotkeyButton.toolTip="连点开关键";hotkeyButton.setAccessibilityLabel("修改连点快捷键")
        Chrome.place(hotkeyButton,in:clicks,350,18,36,26)
        for (field,x,label) in [(minimum,CGFloat(20),"最低 CPS"),(maximum,CGFloat(208),"最高 CPS")] {
            field.font = .monospacedDigitSystemFont(ofSize:38,weight:.light);field.textColor=Chrome.ink
            field.isBordered=false;field.drawsBackground=false;field.focusRingType = .none
            field.alignment = .left;field.delegate=self;field.target=self;field.action=#selector(commitCPS)
            field.setAccessibilityLabel(label)
            Chrome.place(field,in:clicks,x,66,100,52)
            Chrome.place(Chrome.text(label,size:10,weight:.medium,color:Chrome.muted),in:clicks,x+2,119,100,18)
        }
        Chrome.place(Chrome.text("—",size:24,weight:.ultraLight,color:Chrome.muted),in:clicks,149,77,40,32)
        Chrome.place(Chrome.text("左键 + 右键",size:11,color:Chrome.muted),in:clicks,385,87,120,18)
        Chrome.place(rangeRail,in:clicks,23,145,486,14)
        Chrome.rule(in:clicks,y:175,width:532)
        Chrome.place(Chrome.text("疾跑",size:12),in:clicks,20,189,60,20)
        sprint.target=self;sprint.action=#selector(sprintChanged);sprint.state=UserDefaults.standard.object(forKey:"sprint") as? Bool == false ? .off:.on
        Chrome.place(sprint,in:clicks,466,185,44,26)
        sprintKey.addItems(withTitles:["Control","R"]);sprintKey.selectItem(at:UserDefaults.standard.integer(forKey:"sprintKey") == 1 ? 1:0)
        sprintKey.target=self;sprintKey.action=#selector(sprintChanged)
        sprintKey.isBordered=false;sprintKey.font = .monospacedSystemFont(ofSize:11,weight:.regular)
        sprintKey.setAccessibilityLabel("疾跑按键");Chrome.place(sprintKey,in:clicks,360,187,86,24)

        let bridge=PanelSurface(card:true);Chrome.place(bridge,in:root,24,316,532,258)
        Chrome.place(Chrome.text("Telly",size:16,weight:.semibold),in:bridge,20,19,90,24)
        let r=PanelButton("R",target:nil,action:nil);r.isEnabled=false;r.toolTip="按住 R 搭路";r.setAccessibilityLabel("搭路按键 R")
        Chrome.place(r,in:bridge,350,18,36,26)
        bridgeStateLabel=Chrome.text("开",size:11,color:Chrome.muted);Chrome.place(bridgeStateLabel,in:bridge,408,23,36,20)
        Chrome.place(bridgeEnabled,in:bridge,466,18,44,26)
        for (choice,index,x) in [(levelChoice,0,CGFloat(20)),(risingChoice,1,CGFloat(272))] {
            choice.tag=index;choice.target=self;choice.action=#selector(selectBridgeTile);choice.setAccessibilityRole(.radioButton)
            Chrome.place(choice,in:bridge,x,62,240,148)
        }
        risingChoice.rising=true
        bridgeStatus.font = .systemFont(ofSize:11);bridgeStatus.textColor=Chrome.muted;bridgeStatus.maximumNumberOfLines=1;bridgeStatus.lineBreakMode = .byTruncatingTail
        Chrome.place(bridgeStatus,in:bridge,20,226,414,20)
        Chrome.place(Chrome.text("T 切换",size:10,color:Chrome.muted),in:bridge,459,226,60,20)

        let inventory=PanelSurface(card:true);Chrome.place(inventory,in:root,24,586,532,58)
        Chrome.place(Chrome.text("自动工具",size:12,weight:.medium),in:inventory,20,20,130,20)
        Chrome.place(autoToolEnabled,in:inventory,206,16,44,26)
        Chrome.place(Chrome.text("同种补料",size:12,weight:.medium),in:inventory,286,20,130,20)
        Chrome.place(supplyEnabled,in:inventory,466,16,44,26)
        autoToolEnabled.toolTip="连点关闭时，真实按下左键且准星命中方块才切换快捷栏工具；床用剑。"
        supplyEnabled.toolTip="Telly 起跳前切换同种、同颜色的快捷栏备用方块；不打开背包。"
        statusLabel.font = .systemFont(ofSize:11);statusLabel.textColor=Chrome.muted;statusLabel.maximumNumberOfLines=1;statusLabel.lineBreakMode = .byTruncatingTail
        Chrome.place(statusLabel,in:root,28,668,410,23)
        let stop=PanelButton("停止",target:self,action:#selector(emergencyStop));stop.toolTip="立即释放全部输入"
        Chrome.place(stop,in:root,474,663,80,32)
        window.initialFirstResponder=stop
    }

    func captureHotkey(_ code:UInt16) {
        if code == 53 {recordingHotkey=false;notice="快捷键未更改"}
        else if [12,14,17,44,15].contains(code) {notice="请选其他键，T、E、/、Q、R 已保留。"}
        else {
            boundHotkey=code;UserDefaults.standard.set(Int(code),forKey:"hotkey")
            recordingHotkey=false;notice="快捷键已保存"
        }
        hotkeyButton.title=recordingHotkey ? "…":hotkeyTitle();updateUI()
    }

    @objc func toggleFromDashboard() {
        cancelInventoryActions()
        if policy.enabled {stop("已关闭。");return}
        guard AXIsProcessTrusted(),CGPreflightListenEventAccess(),installTap() else {
            notice="输入权限未就绪";updateUI();return
        }
        // Arming from the dashboard must not emit input outside the target game.
        hardwareMouse.start();policy.stop();policy.enabled=true;policy.targetActive=false
        notice="已开启，等待游戏前台";updateUI()
    }
    @objc func selectBridgeTile(_ sender:NSButton) {setBridgeMode(sender.tag == 0 ? .level:.rising)}
    @objc func commitCPS() {
        guard minimum.stringValue != String(format:"%g",cpsMin) || maximum.stringValue != String(format:"%g",cpsMax) else {
            if notice.contains("设置未保存") {notice="设置已保存";updateUI()};return
        }
        saveSettings();updateUI()
    }
    func controlTextDidEndEditing(_ obj:Notification) {commitCPS()}

    @objc func showPreferences() {
        if preferences.isShown {preferences.close();return}
        let vc=NSViewController();let root=PanelSurface(frame:NSRect(x:0,y:0,width:360,height:340));vc.view=root
        Chrome.place(Chrome.text("设置",size:16,weight:.semibold),in:root,20,20,300,25)
        Chrome.place(Chrome.text("游戏实例",size:11,color:Chrome.muted),in:root,20,63,100,18)
        targetPicker.target=self;targetPicker.action=#selector(selectTarget);targetPicker.font = .systemFont(ofSize:12)
        Chrome.place(targetPicker,in:root,16,87,328,28)
        Chrome.rule(in:root,y:133,width:360)
        Chrome.place(permissionsLabel,in:root,20,149,320,20)
        permissionsLabel.font = .systemFont(ofSize:11);permissionsLabel.textColor=Chrome.muted
        let permissions=NSStackView();permissions.spacing=8
        for (title,selector) in [("辅助功能",#selector(openAccessibility)),("输入监控",#selector(openInputMonitoring)),("重新检查",#selector(requestPermissions))] {
            let b=PanelButton(title,target:self,action:selector);b.widthAnchor.constraint(equalToConstant:96).isActive=true;b.heightAnchor.constraint(equalToConstant:28).isActive=true;permissions.addArrangedSubview(b)
        }
        permissionControls=permissions;Chrome.place(permissions,in:root,20,180,320,30)
        let read=PanelButton("检测连接",target:self,action:#selector(testBridgeReading));Chrome.place(read,in:root,20,224,100,30)
        let detail=PanelButton("诊断详情",target:self,action:#selector(showDiagnostics));Chrome.place(detail,in:root,132,224,100,30)
        Chrome.rule(in:root,y:278,width:360)
        Chrome.place(Chrome.text("mcPvPmax  /  1.9.3",size:10,color:Chrome.muted),in:root,20,298,220,18)
        let exit=PanelButton("退出",target:self,action:#selector(quit));exit.quiet=true;Chrome.place(exit,in:root,274,290,64,30)
        preferences.contentViewController=vc;preferences.behavior = .transient;preferences.appearance=NSAppearance(named:.darkAqua)
        updateUI();preferences.show(relativeTo:settingsButton.bounds,of:settingsButton,preferredEdge:.maxY)
    }
    @objc func showDiagnostics() {
        preferences.close()
        if let bridgeWindow {bridgeWindow.makeKeyAndOrderFront(nil);return}
        let panel=NSWindow(contentRect:NSRect(x:0,y:0,width:500,height:310),styleMask:[.titled,.closable],backing:.buffered,defer:false)
        panel.title="诊断";panel.isReleasedWhenClosed=false;panel.appearance=NSAppearance(named:.darkAqua);panel.center()
        let root=PanelSurface();panel.contentView=root
        diagnosticLabel.font = .monospacedSystemFont(ofSize:11,weight:.regular);diagnosticLabel.textColor=Chrome.muted
        diagnosticLabel.isSelectable=true;Chrome.place(diagnosticLabel,in:root,20,20,460,270)
        bridgeWindow=panel;updateBridgeUI();panel.makeKeyAndOrderFront(nil)
    }

    func updateDashboard() {
        clickSwitch.state=policy.enabled ? .on:.off
        clickStateLabel.stringValue=policy.enabled ? "开":"关";clickStateLabel.textColor=policy.enabled ? Chrome.accent:Chrome.muted
        rangeRail.low=cpsMin;rangeRail.high=cpsMax
        let ready=AXIsProcessTrusted() && CGPreflightListenEventAccess()
        let invalid=notice.contains("设置未保存")
        if invalid {statusLabel.stringValue="CPS 需在 1–40 之间，且最低 ≤ 最高"}
        else if recordingHotkey {statusLabel.stringValue=notice.contains("已保留") ? "按键已占用，请换一个":"按下新快捷键 · Esc 取消"}
        else if !ready {statusLabel.stringValue="输入权限未就绪 · 在设置中检查"}
        else if policy.enabled {statusLabel.stringValue=isTargetFront() ? "连点已开启":"连点已开启 · 等待游戏前台"}
        else {statusLabel.stringValue="连点已关闭"}
        statusLabel.textColor = invalid || !ready ? .systemOrange:Chrome.muted
        statusLabel.toolTip=notice
        targetLabel.stringValue=manualPID.map{"Minecraft · 实例 \($0)"} ?? (targetPIDs.isEmpty ? "Minecraft · 未连接":"Minecraft · 已识别")
        permissionsLabel.stringValue=ready ? "输入权限已就绪":"输入权限未就绪"
        permissionControls?.isHidden=ready
        statusItem?.button?.title=policy.enabled ? "MC ●":"MC ○"
        updateBridgeUI()
    }
    func updateBridgeDashboard() {
        levelChoice.state=bridgeMode == .level ? .on:.off;risingChoice.state=bridgeMode == .rising ? .on:.off
        bridgeStateLabel.stringValue=bridgeEnabled.state == .on ? "开":"关";bridgeStateLabel.textColor=bridgeEnabled.state == .on ? Chrome.accent:Chrome.muted
        if bridgeEnabled.state != .on {bridgeStatus.stringValue="已关闭"}
        else if telly.finishing {bridgeStatus.stringValue="正在收尾"}
        else if telly.active {bridgeStatus.stringValue="搭路中"}
        else if bridgeDiagnosticUntil>0 {bridgeStatus.stringValue="等待游戏连接…"}
        else if let problem=bridgeProblem() {bridgeStatus.stringValue=problem}
        else if telly.restartRequiresRelease {bridgeStatus.stringValue="已停稳 · 松开 R 后可重新开始"}
        else {bridgeStatus.stringValue="待命"}
        bridgeStatus.toolTip=telly.message
        bridgeStatus.textColor=telly.active ? Chrome.accent:bridgeProblem() == nil ? Chrome.muted:.systemOrange
        diagnosticLabel.stringValue=bridgeDiagnostics()
    }
    func bridgeProblem()->String? {
        guard !telly.active else{return nil}
        let message=telly.message
        if message.contains("R 已用作疾跑键") {return "按键冲突 · 疾跑键需设为 Control"}
        let failures=["失败","失效","超时","超出","超过","未能","未及时","未读到","未确认","未正确","无法","没有","缺少","落空","未落","已变化","异常","不是完整","请关闭飞行","未找到"]
        guard failures.contains(where:message.contains) else{return nil}
        return String(message.split(separator:"；").first ?? Substring(message)).replacingOccurrences(of:"。",with:"")
    }
    func bridgeDiagnostics()->String {
        let fresh=bridgeWorldPreview.map{ProcessInfo.processInfo.systemUptime-$0.pose.time<0.25} ?? false
        var lines=["游戏状态：\(fresh ? "已连接":"已停止")",telly.message]
        if let config=telly.config {lines.append(String(format:"灵敏度 %.1f%%",config.sensitivity*200))}
        if let pose=[telly.track.latest,bridgePreview].compactMap({$0}).max(by:{$0.time<$1.time}) {
            lines.append(String(format:"XYZ %.3f / %.3f / %.3f\n朝向 %.1f / %.1f",pose.x,pose.y,pose.z,pose.yaw,pose.pitch))
        }
        return lines.joined(separator:"\n\n")
    }
}
