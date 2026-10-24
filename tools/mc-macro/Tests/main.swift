import Foundation

func check(_ condition: @autoclosure () -> Bool, _ message: String) {
    guard condition() else { fatalError(message) }
}
var p = MacroPolicy()
p.physicalLeftHeld = true
p.targetActive = true
check(!p.mayClick, "关闭时不能点击")
p.enabled = true
check(p.mayClick, "启用且游戏前台且按住时应点击")
p.targetActive = false
check(!p.mayClick, "游戏失焦不能点击")
p.targetActive = true
p.physicalLeftHeld = false
check(!p.mayClick, "松手不能点击")
p.physicalLeftHeld = true
p.stop()
check(!p.enabled && !p.physicalLeftHeld && !p.mayClick, "停止必须清除按住状态")
check(MacroPolicy.validRange(15, 20), "默认范围")
check(MacroPolicy.validRange(18, 18), "固定 CPS")
check(!MacroPolicy.validRange(20, 15), "拒绝倒置范围")
check(!MacroPolicy.validRange(.nan, 20), "拒绝 NaN")
check(!MacroPolicy.validRange(0, 20), "拒绝零值")
check(!MacroPolicy.validRange(15, .infinity), "拒绝无穷")
check(abs(MacroPolicy.interval(cps: 20) - 0.05) < 0.000001, "20 CPS 间隔")
check(!MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java -jar editor.jar"), "其他 Java 程序不能误认")
check(!MacroPolicy.looksLikeMinecraft(name: "Minecraft Launcher", bundle: "com.mojang.minecraftlauncher", command: ""), "启动器不能误认")
check(MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java net.minecraft.client.main.Main"), "原版检测")
check(MacroPolicy.looksLikeMinecraft(name: "java", bundle: "", command: "java net.fabricmc.loader.impl.launch.knot.KnotClient"), "Fabric 检测")
print("通过：输入状态、失焦／松手／停止、CPS 校验、游戏与启动器识别。")
