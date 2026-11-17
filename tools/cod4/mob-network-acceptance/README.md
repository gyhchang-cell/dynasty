# COD4-1 私有真实双客户端生物网络验收

范围：固定 `ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b` 的已验 Dynasty Jar，配 GeckoLib、Curios 和本辅助 Jar。两个自动化真实 Minecraft 客户端，host 使用原生集成服务器发布随机 LAN 端口，peer 独立离线 UUID 经 127.0.0.1 TCP 加入。验证 ServerPlayer 类、非 FakePlayer 和 TCP 地址。不是两名真人，也不是完整整合包或生存获取验收。

写入仅限本 tools 目录、对应 docs 目录和私有 build/cod4-mob-network-20261023。只读取原 network-acceptance 的启动、驱动和 Gradle 辅助模式；不修改其他客户端、生产 Java、资产、TODO 和共享 Jar。辅助 Jar 只含私有 QA 类。reobf 的私有 compile-dynasty.jar 从现有只读开发类建立，仅作编译继承映射，不装进游戏。

## 运行

1. `python3 tools/cod4/mob-network-acceptance/prepare.py`：重新核对 request 与 SecondaryMobs 的30个ID，生成 applicability.json/md（不改运行器）。
2. `python3 tools/cod4/mob-network-acceptance/build.py build-XX.log`：私有编译映射与辅助Jar构建，固定生产Jar哈希校验。
3. 新编号运行：`python3 tools/cod4/mob-network-acceptance/run.py run-XX`。30类主体+特殊交互套件。
4. 补充低血逃跑/双方分别受击输入与客户端血量同步：`python3 tools/cod4/mob-network-acceptance/run.py run-YY reactions`。
5. 六类中立全新实体分别由双方独立挑衅：`python3 tools/cod4/mob-network-acceptance/run.py run-ZZ neutral`。
6. 每次使用新编号，失败运行/世界保留。运行器只终止自己创建的两个进程组。当前界面主线程无需手动操作。

## 输入与证据

攻击使用 `MultiPlayerGameMode.attack`，交互用 `MultiPlayerGameMode.interact`，药草点使用 `MultiPlayerGameMode.useItemOn`，掉落诱饵用 `LocalPlayer.drop(false)` 的原生 C2S。未手动调用 mobInteract、攻击/交互事件、doHurtTarget、服务端 hurt 来代替输入。服务端 Forge 事件仅监听。潜行识破先按住原生 keyShift 跨6个客户端tick，再经原生 interact 发送实际潜行标志；同时发送原生 PRESS_SHIFT_KEY/RELEASE_SHIFT_KEY。

每阶段 command.json 是服务端夹具准备完成后的指令；双方 input 文件记录真实客户端发起的调用，ack 用于等待两端处理；result 文件保存服务端行为前后快照、原生攻击/交互计数、死亡事件、掉落实体 UUID、库存和物品守恒。两端不保证同一服务端 tick 到包；`simultaneous-C2S-kill` 指同一指令阶段的并发争抢攻击，不声称精确同 tick。两个原生攻击都可被事件监听记录，但死者只触发一个掉落事件。

展示图由 AFTER_LEVEL 后的 RenderTick.END 从实际 framebuffer 保存。展示阶段明确 NoAI/摆位；行为阶段恢复正常 AI。隐藏 HUD 以避免高血量夹具的心形柱遮住生物。图中应有本地第三人称玩家、另一名玩家及当前生物。补充套件最终血量同步展示前，将同一NBT重新装载以清理瞬时动作/目标，NoAI后摆位；行为判据在此之前完成。展示图证明真实世界实体同框，不能证明每个战斗动作或全部美术质量。

## 明确夹具

初始实体、平台、玩家传送、生存模式高血量、测试物品、攻击属性由服务端提供。争抢击杀前把实体设为1血、停AI，并在其**原始**战利品表选择1..192内的正掉落种子；不替换掉落表、不人工发奖励。验证的是实际原生死亡/单次掉落与争抢拾取守恒，不重新统计随机掉率。

盗窃原料带 MobQaToken 标签，便于区分返还物与随机同类战利品。死亡前清理两名玩家的剩余夹具库存，按死亡事件产出的全量物品建立守恒账本。骗子非客户识破的负例会给 peer 一份真实假药的夹具复制品，明确不是产品复制产物。药草点实际等待1200世界tick，不写完成状态或手动调事件。

## 判定边界

按实际定义区分6中立与24敌对。饥民/采药客/螺女每tick清目标；骗子受击后能保存报复目标，但其近战Goal始终排除骗子，不能误要求它清空目标。night_watchman/jingwei_bird 则允许受激选敌。所有类低于25%生命受击的通用逃跑需另用补充套件核对。

采药客是铜钱换2茶叶并有实体级200tick冷却。螺女源码只有缩壳、清目标，没有已定义交易入口；真实铜钱交互无结果仅为不适用探测，不能据此新增产品需求或缺陷。赤狐自然攻击会偷一份可食物并保存，源码没有“吃完消失”的消费阶段；死亡应返还保存的一份。机关鼠是发条鼠 clockwork_rat。

## 后续全包套件（独立于原30类结论）

`run.py run-XX fullpack` 在同一私有build根下创建两实例。完整复制modpack的85个生产Jar与配置/资源包，私有副本替换为已验语言修复0e1 Jar，另加QA共86Jar。生产源码/原包/旧档不修改。新世界使用NORMAL普通地形而非FLAT，不铺测试平台；生物、武器/护甲、高生命与初始位置是夹具。

测试四种代表生物的双方原生attack、生产AI实际伤害及单次死亡，再在自然生成地表0/256/512偏移处各按原生keyUp+keyJump步行126客户端tick；仅测兼容性，绝不冒充自然取得或完整生态分布验收。场景起点/同框镜头摆位与传送如实记录，步行阶段无服务端位移代替输入。dynamic_fps模组保留，私有配置关闭后台限帧。所有原30类报告固定引用原run-03/04/06，不被全包新结果覆盖。
