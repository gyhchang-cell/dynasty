# Jason → Carson：第七批，待审而非入账

`batch-007.json` 提出 **2 条待审链**，`excluded-007.json` 保留 **2 组零增量**。每条 `credit=0`，仅有待主审的 `proposed_credit=1`；没有写 accepted/progress 等主账。20 个来源证据文件、47 段不同完整方法和 3 段明确标注的配置声明是证据量，不能折算成实现数。不是新加 47 条，也未补满 20/80/1000 或证明工作满十小时。

## 可用结论

1. **死亡目标保存弹体经验快照 → 经验掉落事件读取。** 固定匠魂 `f4e77d43f39ba1047bf93ae816b7e1beaab514c2`。完整读实际弓发射、modifier launch、capability、死亡和掉落方法。boxed Float 的 `0` 仍表示存在弹体记录，必须阻止回退读取消费时玩家当前工具；`null` 才表示不存在。此记录在目标实体上，与第六批攻击者 looting 槽动态上下文语义不同。消费没有 remove/TTL/代次；死亡事件不能当未取消的终态死亡或实际掉落证明。横扫可用的是存在性与结果数值分离、快照时点明确、一次消费应显式处理。
2. **自爆30 tick效果 → 松键/卸装取消 → duration==1终端。** 同一固定匠魂提交。完整读真实按键、sender派发、armor start/stop、旧工具unequip、效果终端。新版stop重载会进入旧版removeEffect；NoMilkEffect不阻止这类显式取消。终端先爆炸，再自伤，不检查伤害成功，也没有任务代次。与第六批Sling蓄力共用的基础设施都只作支持；独立待审语义是该效果自己的取消入口与终端副作用边界。不能据此照抄严格duration==1来丢弃合法跨tick伤害事实。

## 保守排除与来源限制

- 二段跳：实际读完客户端上升沿、服务端重新验当前资格、腾空次数配额、起跳/落地清除，以及clone复制、跨维度只sync。已有Enigmatic输入边沿与Artifacts DoubleJumpPacket近似族；未证明新的独立延后伤害事实消费，保守为0。旧腾空请求未带flight epoch只是具体观察，不包装成新增实现。
- 装备监听：ItemStack.matches、newStack.copy及先保存后回调只作为自爆卸装取消支持。客户端/服务端镜像不重复算；代码无注释所说的5tick/半秒门控，观察以正文为准。
- 原Apugli feature固定缓存又读AbstractCooldownPower与ActionOnHarmPower，仍是Apoli冷却/既有harm模板委托，没有新增候选，不拿包装凑数。rpginventory原404继续排除，没有请求或猜新URL。
- experienced的生成配置JSON不在原Java缓存；尝试一次固定提交的raw文本请求，在本机TLS证书校验处失败。错误在 `tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/fetch-007-error.json`，没有重试、换地址或绕过证书校验。保留现有Java配置声明511–513行；该声明不是完整addModifiers方法，已明确标注，不计完整方法。没有声称已核生成资源、加载器或运行时配置，Carson可据此降级相关性。
- 官方来源沿用原固定缓存的source.json和pinned tree，未宣称本轮重新联网核验默认分支/发行版。每个复制文件重算Git blob SHA1并与固定树比较，再记录SHA256。没有执行下载代码。

## 文件与交接

每条JSON均有repo/revision/path/source_local/source_sha256/line/end_line/excerpt/observation/application/limits/url，另有完整支持方法、配置声明类型、具体语义去重、最近既有族。`source-index-007.json`保留完整源索引，`validation-007.json`核对全文摘录/文件哈希/行范围及主账只读快照；这是证据一致性检查，不是编译或玩法测试。通过重复检查不代表独立性自动成立，最终计数只由Carson裁定。

最新人类要求本岗不编译、不测试、不启动游戏/客户端/服务器/GameTest，不动主QA、生产、资产、主待办，不备份待办、不删游戏内容。集中run01与seq50故障处理由主协调负责；本岗不把其进度/修正推断当作验收通过。本轮只写原helper两个目录，保留55项总范围，不擅自缩减或标完成。

下一轮仍先比较本批和第六批。剩余已固定线索为匠魂ThrownTool原槽位/返回物品的一次消费、当前装备派发中旧效果撤销的其他真实消费者；这些只属待阅读线索，信用0，需读完整链后再决定。不要将双跳/装备监听支持重新包装提案。
