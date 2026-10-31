# 方天横扫回执交付（2026-10-29）

研究门槛与本岗源码修复、离线验证已经完成；真实 C2S 与完整视觉组合验收尚未完成，总待办未改。

- 主账 `accepted.jsonl`：1000 条、80 仓库、949 固定源码，SHA256 `c13a16d62edf4724f41284e30a78672d862c4b0d3ad7d0cef521a62e9d8feeff`。逐条观察、原裁定/补充裁定与语义合并保留；7532 候选、133 辅助、旧状态1000语料、通用基础设施均不能转成此次有效参考信用。
- `gate-1000-integrity.json` 独立复核1000条源字节/完整方法范围/片段哈希/固定revision与结构去重，0错误。协调 `coordinator-integrity-1000-20261029.json` 另查同一账本，信用0，未覆盖该文件。
- 本轮尾部批次188/189/190及完整使用链094/095/096保存了195段完整方法；支持方法数量不加信用。4174补齐首次pending记录后沿用原同一补充裁定，没有双算；Forsaken/姜饼人同链补读排除。语义判断由人工观察承担，完整性脚本不能替代它。

## 正式源码变更

仅 `src/main/java/com/dynasty/cod3/FangtianSweep.java`，6行增加、3行删除：

1. Receipt捕获生产时ServerLevel对象。
2. END结算接受`now - receipt.tick`等于0或1；负数、2及以上丢弃。
3. 玩家与主目标必须仍是该原ServerLevel，防双方一起换维后旧位置回执误发。

原来源对象/直接拥有者/真实伤害证据、玩家存活/移除检查、END先出队、每玩家每结算tick STAMP去重均保留。`begin/attack/finish/real/damage/stopped/packet/accepts/geometry/at/quad` 方法正文逐字节相同，哈希见 `fix-delivery-receipt.json`。`DynastyCombatEvents.sweep`及任何伤害、原mesh_weapon残影、其他VFX、资产均未改；packet开始时间仍采用消费tick。

源码修复后SHA256：`02557c5e4a411561d5754b35e119b3af2c6d9eff2d132820cc4773621240a912`。

## 已实际执行的验证

- `offline-compile-receipt.json`：Java17、真实官方映射Minecraft1.20.1/Forge47.4.10依赖，冻结目标源码/1492基线class/901依赖Jar到本岗私有目录，离线javac退出0。没有调用Gradle、没有写共享缓存/构建输出、没有启动任何游戏或服务器。
- `offline-boundary-receipt.json`：完整未改写生产FangtianSweep源码在小型API替身下执行55例，全部通过。覆盖4991→4992、同tick、2tick过期/长过期/未来、主/副目标成功证据、零/负/NaN/无限金额、取消、错误来源/拥有者/法术、换维/同维另一世界对象、玩家死亡/移除、START/END阶段、每END一次、重复结算、不同拥有者、原点方向快照、停服清队列。
- 同一替身/同一4991→4992首例运行修复前生产源码：编译成功，断言失败（退出1）。这是原缺陷检出证明；修复后退出0。
- 初次替身编译因AttackEntityEvent.getTarget返回类型过窄失败，保存在`.work/receipt-fix/boundaries/`；仅将替身改为Object后在`boundaries-02/`完成。生产源哈希不变。未隐去初次失败。

这55例是生产类的离线控制流验证，不是原生Forge事件、真实伤害/TCP、双客户端或像素验收；未以FakePlayer代替真人，也未重跑套装63项或护卫已过项。

## 精确交付与集中验收

交付目录：`tools/cod4/sweep-receipt-research/delivery/`。

- `source/com/dynasty/cod3/FangtianSweep.java`
- `official-mapped/classes/com/dynasty/cod3/FangtianSweep.class`
- `official-mapped/classes/com/dynasty/cod3/FangtianSweep$Receipt.class`
- `official-mapped/classes/com/dynasty/cod3/FangtianSweep$Start.class`
- `official-mapped/classes/com/dynasty/cod3/FangtianSweep$Contact.class`

四类均有SHA256范围清单，见 `fix-delivery-receipt.json`。它们是official-mapped开发输出，不能直接替换生产SRG Jar；请主协调复制源码进入当前冻结树统一编译/reobf，再按四类范围集成。未生成全Jar。共享`modpack/mods/dynasty-1.4.0.jar`前后SHA均为`0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba`。

主协调仍需集中有界原生C2S复验：真实击中能在相邻END发专用月牙，与原mesh_weapon残影和其他既有组合共存；取消/无有效伤害不造cue；期限、换维与去重仍有效。完整画面不以nonzero像素代替。未验事项不标完成，由主协调整项核实后处理总待办，本岗不操作原档或游戏实例。

用户此前10小时持续主动工作要求未声称完成；本文件是本岗受影响源码与离线证据交接，不代表53项总任务完成。
