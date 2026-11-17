# Halley 第五批：只交待审核建议，不增加主账信用

交付 `batch-005.json` 与 `reviewed-suggestions.jsonl`，四条完整 owner/消费链，全部 `credit:0`、`accepted:false`，由 Kepler 核查完整上下文与语义去重。完整方法、行范围、固定 commit/tree/blob、源文件 SHA256、摘录与 AST 规范化 SHA256 均随每条 evidence 保存。CODEC 静态字段单独放 source_declarations，仅支持证据，不伪装方法。

- Cold Sweat：`Momo-Softworks/Cold-Sweat@849b1484b27cdb047865e9d1939057507163bc84`，1.20.1-FG 分支固定快照。温度 capability 的旧 modifier 格式与死亡属性白名单合为一条；仅复制白名单 baseValue，非死亡才 copy 整个温度能力。入世界事件先浅复制现有 modifier 映射再补默认，随后清原 map 回填，不能断言旧效果全部丢失；气候模式切换是另一个主动重建边界。非零 hash 跨 trait 复用对象，未比较 payload，碰撞/浅拷贝有边界。
- 同仓库旧物品键：容器打开时 fuel→Fuel、temperature→Temperature，两分支同循环合为一条。旧键存在会覆盖已存在的新键，错类型可能变0；真正消费者为灯 tick 和水袋饮用。不是旧 item ID remap，也未证明所有离线或嵌套物品覆盖。
- 同仓库缝入保温材料：护甲能力持有真实材料栈和配置快照，装备温度 tick 消费，容量缩小时退料，一整链一条。decode 失败保留当前列表，encode 失败写空 compound；浅 copy 不标 changed 可与缓存冲突。根同步 tag 与 Forge capability 需要区分，不能将删除旧 Insulation 键当兼容读取已完成。
- Champions：`TheIllusiveC4/Champions@969139a340fabff771bb6f952d2050b6a76d694d`，1.18.x 固定快照。rank/词缀、私有伤害记忆、入世界与实体转换合为一条。writer 写 data compound，reader 以 hasUUID(data) 才恢复，正常 writer 形状与 reader guard 不一致；适应词缀 name/count 会实际改变伤害减免。转换只交付 rank/词缀选择并重跑初始逻辑，不复制旧私有 map。未运行，不能宣称运行复现或1.20.1可移植。

Hearth 关闭粒子偏好完整链虽已阅读，属于协议排除的渲染偏好，**不提交为候选信用**。其他词缀、键名、静态注册、getter、每 trait、平台移植、网络包及支持方法均不拆计。

`document-integrity.json` 记录仅本地文档核对：源字节对应固定 Git blob，完整 AST 范围/哈希核对；主账只读。首方法在主账未发现 ID/摘录/规范化碰撞仍不代表语义独立。与 ScalingHealth Clone/mob、嵌套物品 bonus、简单键迁移有重复家族风险，逐条 limits/risk 已列。方法、声明、下载数均非有效实现参考数。

不修改主账/生产/待办/原存档，不编译、不执行上游代码、不启动游戏/GUI/服务器，不触屏。当前仅研究，无需游戏 QA 交接。本批交付不代表十小时范围完成；继续后续独立来源。
