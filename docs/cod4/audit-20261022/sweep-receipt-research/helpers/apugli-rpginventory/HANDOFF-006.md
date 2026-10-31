# Jason → Carson：第六批，固定来源中的独立生命周期

本批 `batch-006.json` 提出 **5 条待审候选**，`excluded-006.json` 保留 **3 组零增量**，全部 `credit=0`。共 77 段不同完整方法、35 个证据文件；这是阅读与证据量，不能折成有效实现数量。每条有完整固定来源、全文方法范围、SHA256、观察、应用、限制和语义去重比较；最终由 Carson 审阅入账。

## 来源与范围

本轮首先继续 Apugli 已固定的 feature/1.20（`fbb5d732098ec5832b8b8922843a023ed6f8baa2`，配置 Minecraft 1.20.1 / Apugli 2.9.0-beta.3）与 multiloader/1.19.2（`18680b77417740415df474b1fb6f8ffb25ed4735`，配置 Minecraft 1.19.2 / Apugli 2.6.7）。从已核实的官方迁移仓库 ChrysanthCow/apugli 获取固定提交元数据与文本快照，重建提交树并逐文件核 Git blob。548/510 个保存文本文件不是已研究实现数。4 次研究 HTTP 请求均成功，未重试；未请求已排除的 rpginventory 404 地址。

实际补读的每实体独立空 stack util 连接已有附魔持有者链，仍为 0；AreaOfEffect 只有同步范围遍历，也为 0。本轮已审路径没有新增独立 Apugli 候选，**未声称所有历史分支已研究完毕**。

依据用户本轮明确授权“相关方法不足……在已固定其他来源找同类回执生命周期”，转读项目既有固定缓存 SlimeKnights/TinkersConstruct，提交 `f4e77d43f39ba1047bf93ae816b7e1beaab514c2`。没有去其他 helper 未固定的新仓库下载或改别人源码。该缓存已有 source.json 的官方仓库/下载来源记录；本批重新逐文件核对 pinned tree 的 Git blob 后，仅将所读文本复制到自己的 sources 目录。未宣称新核过 GitHub 默认分支或具体发行版号。完整来源索引为 `tinkers-source-index-006.json`。

## 五个候选的可用结论

| 完整链 | 本批独立状态语义 | 横扫可借鉴与限制 |
|---|---|---|
| Bleeding / Lacerating | 相同 amplifier 的续期保留原模20消费相位；looting 在施加时捕获，伤害来源却每次延后读取目标可变字段 | 归属与参数应说明各自快照时刻；粒子和 DOT 调用不证明实际伤害成功。不是普通无来源 DOT 换名计数。 |
| 护甲 START → STOP → Sling | slot/选中 modifier/start age 挂起；松键先 remove 记录再调用当前装备效果 | 一次取走可挡记录重复消费，但仅存槽位不能挡换装；跨维度 cap revival 还保留原 Holder。头/腿镜像合一。 |
| ModifierLootingHandler | 攻击前按 attacker UUID 临时标源槽，真实掉落事件消费，hurt 后重置；Projectile 走自身能力上下文 | 区分同步动态作用域与能跨 tick 的来源回执。无 finally/前值栈，嵌套或异常不安全；此条相关性仍待主审裁定。 |
| ProjectileImpact 反射/替代处理 | 短防御窗口中改已有弹体 owner、保留箭 pickup、重射并设置 impact 结果 | 未来伤害来源可能被合法改写；碰撞名额、反射与 hurt 成功是不同阶段。完整166行回调只建议一条，退款/穿透分支不拆。 |
| SlimeBounceHandler | 落地保存 Vec3，实体 age+1 恢复一次，再维持动量并用两个宽限截止清理 | 最直接的跨阶段交接例：为避开原版落地清速度而延后应用。仍用 age==预约值，错过后没有补消费；不能照抄为横扫 TTL。 |

公共 performAttack、hurtNoInvulnerableTime、capability 和注册方法全部作支持，不另增信用；已有主账横扫/引信/重力/掉落支持与 coordinator-receipt 十二条均做语义对照。候选记录内 `semantic_dedup` 写明最近已有族与独立性理由，不只比较文件名或行号。外部 Mantle 副手冷却核心未读，因此 OffhandAttack/Parrying 一组明确排除，不补算完整生命周期。

## 核对与后续

`validation-006.json` 记录逐文件 SHA256、Git blob SHA1、完整摘录范围、必需字段和主 accepted/reviewed 只读快照哈希。5 个候选主入口在该快照中未出现；语义独立性仍需 Carson 判定，不能靠精确入口不同自动加分。未编译、测试、启动游戏/服务器/GameTest、操作屏幕或测试真实 TCP，未执行上游代码。无需启动游戏来审核本批。

只写两个 apugli-rpginventory 专属目录，未改主账、生产、资产、主待办，未备份待办或删游戏内容。本批实际5条待审，不足20条，不声称门槛达到或验收完成。后续继续从断点研究；XP 死亡→经验消费仅看到候选路径，完整配置生产链未读完，**目前不作为新增有效案例交付**。旧考试禁测已解除，图形/真实 TCP 仍留主协调集中安排，不碰用户实例。
