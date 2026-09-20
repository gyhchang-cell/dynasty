# 青龙刀天降攻击与龙形升级

## 本轮行为

1. 青龙刀的有效直接近战命中只标记目标，本体扣血为 0。
2. 目标头顶展开两层青色法阵，约第 7 tick 开始有青龙俯冲。
3. 第 20 tick（正常服务器速度约 1 秒）由服务端结算捕获的那次攻击伤害，随后播放落点法阵并淡出。

法阵随目标移动，高度适配目标体型。没有新增范围伤害或百分比秒杀；伤害不足时目标不会死亡，也不破坏方块。第一人称彻底取消手边转圈小龙和自己的背后常驻龙，第三人称仍可见护卫龙。

## 伤害与同步

- 在王朝武器额外伤害、会心等计算完成后，记录该次近战攻击值；标记时不扣血、不消耗护甲和吸收生命。
- 落下时使用独立伤害来源归属原攻击者，跳过重复的王朝加伤/套装/Boss 减伤计算。原版护甲、抗性、保护附魔和吸收在落下时正常参与。
- 只绕过受击冷却，避免连续两次有效攻击的龙互相吞伤害；不绕过无敌、创造模式或事件取消。
- 换武器不会改变已标记的攻击值；攻击者死亡/离线/离开维度或目标已不存在时不追补伤害。
- 服务端通知开始/命中/取消；客户端携带目标 UUID 校验，不把复用实体 ID 当成旧目标。换世界清理特效，停止服务器清理待结算队列。
- 联机协议更新到 4，客户端和服务端需同时更新模组。
- 其他模组若也在伤害事件中重复加成或取消伤害，兼容性还需对应整合包实测。

## 造型

金龙、青龙共同升级为更厚的盘曲躯干、更宽大的三分之二侧面龙首、张口上下颚、獠牙、分叉角、曲线鬃毛、密鳞与双色腹甲。每条龙 7,980 个面，仍为风格化游戏模型，不是参考插画的写实复刻。没有把参考照片当作贴片假装成立体模型。

最多显示 8 个天降过程，优先为攻击预留模型预算，再显示附近护卫龙；全局曲面上限 120,000。实际帧率还未在游戏场景测量。

## 验证

- 编译通过，12 个 GameTest 通过。
- 新增测试覆盖：延迟伤害、护甲/抗性/吸收只计算一次、切换武器、连续命中各结算一次、攻击者移除、已取消事件、同步数据、致死时机及玩家击杀归属。
- 242 个造型动画采样通过有限值检查。
- 预览来自实际几何模型，但天降图是阶段示意，不是游戏实机截图；视角遮挡、联机延迟与光影仍需试玩验证。

```sh
mkdir -p build/imperial-preview
javac -d build/imperial-preview src/main/java/com/dynasty/client/BowSigilGeometry.java src/main/java/com/dynasty/client/ImperialWeaponGeometry.java src/main/java/com/dynasty/client/ImperialDragonMesh.java tools/art/ImperialWeaponPreview.java
java -cp build/imperial-preview ImperialWeaponPreview docs/art/qinglong-descent-v3/preview.svg
magick -font /System/Library/Fonts/Supplemental/Arial.ttf -background none docs/art/qinglong-descent-v3/preview.svg docs/art/qinglong-descent-v3/preview.png
```
