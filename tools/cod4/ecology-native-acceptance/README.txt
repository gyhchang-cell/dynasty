私有生态原生诊断接入（生产内容未修改）

prepare_helper.py 将原被动observer只改命名空间/取消自动注册，将canonical gate observer按字节复制；bootstrap明确注册一次。
qa.init.gradle 只离线编译和reobf私有helper。正常API按安装版本重映射，3个Mixin方法名用固定SRG绑定。离线通过不等于实际注入通过。
prepare_inputs.py inputs-01 已从停止的自有QA checkpoint创建APFS独立副本：720文件前/源后/副本SHA256完全一致。85生产Jar和配置/资源包独立复制；加1个私有helper；不改原存档。
inputs-01当前仍冻结compile03 helper且runtime_ready=false。之后compile05及更新版本必须先按现有helper哈希做受控更新并更新收据，不能误以为副本自动包含最新源码。

明确的接入开关：
- ecology.nativeqa.enabled=true：严格私有process cwd/instance/world/output路径检查，显式注册两个observer，正常停止控制器。
- ecology.nativegate.observe=true / ecology.bounded.observe=true：两个新鲜且不同的输出叶目录，默认关闭。
- ecology.nativeqa.openCopiedWorld=true：单独显式打开已有私有复制世界；worldFolder只允许ecology-checkpoint，不新建世界。尚未启用运行。

watchdog.py 只管理自身Popen创建的新进程组，不接受旧PID、不扫描用户实例。正常退出请求后60秒宽限，再TERM/15秒/KILL。有上限的startup/runtime/absolute预算，不依赖游戏Tick推进。verify_watchdog.py仅Python子进程4类检查通过，没有启动游戏。
私有bootstrap在4600原生tick/300秒或observer请求时调用正常halt，客户端正常stop。退出码0、请求文件与实际存盘三者分别记录，不能互相替代。

运行前仍需：独立复核最新版；四个已有自然场景的真实客户端动作控制（背包回读、真实攻击计数竞争者、有界观察和同UUID拾取）；验证过的private launcher接上watchdog；检查副本helper/source/config映射。不要启动旧live-run1，不拿只读准备或compile删除生态待办。
自然出生仍24/30，材料同UUID拾取仍9/10，未新增游戏或出生信用。

2026-10-28后续复核已收到：已按报告落实预加载saves/world精确真实路径、ready与实际请求世界绑定、observer归一化路径去重，compile05通过。audit_native_gates.py新增scope/祖先/整tick异常保守拒绝，12个合成校验器case通过（零游戏信用）。preflight_inputs.py对inputs01完成114个最终私有输入文件的白名单覆盖核对及720个原副本存档哈希检查，收据inputs-01/final-input-preflight.json；runtime_ready仍false。

2026-10-29接续：NativeSceneDriver已实现默认关闭的原生动作驱动，compile/reobf11通过。200tick初始库存/门槛核对，最多1200tick/64个确认KILLED的原版计数CREATURE准备；原生C2S THROW/attack输入与服务端回读/实际死亡分别记证。四场景各最多800tick，原UUID灯油最多200tick且不延场景；CREATURE门槛关闭时仍独立执行一次MONSTER灯油窗口，不重复场景碰运气。
launch_once.py plan inputs-01只生成安装版离线身份/前台JVM计划；run代码已连接watchdog，但必须有最终reviewed-launch-ready.json与精确当前工具/最终输入/构建源码/版本metadata/世界/审查哈希。当前没有ready、未替换inputs01的03helper、未启动任何游戏。
运行前仍需Herschel驱动/launcher独立复核、补全出生精确坐标环境与事件后真实世界存在确认，再受控整合最终helper并生成readiness。即使30/30出生与10/10材料补满，也必须保留原任务要求的荒村/义庄/墓地/鬼市等场景剩余范围，不能仅凭这四个诊断点删除整项。

2026-10-29 checkpoint: runtime01 hidden client failed before any world due to core classes inside reserved Mixin package. Owned process stopped with coordinator TERM, exit143, no normal save; 720 source/copied world files unchanged. Compile17 split .mixin package passes offline inventory and independent narrow review; runtime still unverified. Frozen inputs01 helper remains16 and consumed runtime01 receipt/marker retained. Future --attempt runtime-02 requires a separate explicit readiness receipt, controlled helper17 integration and full source/archive/world checks. No automatic retry. Review P2 now requires all three Mixin Java/config/provenance and archive entries.
