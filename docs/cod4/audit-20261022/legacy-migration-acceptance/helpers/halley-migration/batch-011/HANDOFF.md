# Halley batch 011 — Astral Sorcery（待 Kepler 审核）

3 条完整语义建议，credit=0、accepted=false；154 个完整方法仅为同链支持，1321 个已固定源文件不代表参考数量。来源为官方 HellFirePvP/AstralSorcery 的 1.16-indev 分支 commit `3599b4819dba3553896f87c0505ccd84bafb0550`，Git tree/blob 与源文件 SHA256、完整 AST 方法范围/原文/摘录 SHA256/归一化 SHA256 均已核对。无运行、编译、游戏、用户存档或主账写入。

1. **个人研究/旧 perk 格式 → UUID 文件 → Clone 效果重建**：`sealedPerks` 存在触发旧格式。旧令牌丢弃原 namespace 并替换标点；树版本不同时保留经验但重建 root、丢分配/令牌。缺书籍标记默认已收过，Clone 读取 UUID 进度而非复制整个实体 NBT。文件队列与备份同属一条，不拆键或方法。
2. **知识共享物品白名单 → 单调合并**：导出研究/星座/等级，排除 perk/XP/当前调谐/发书等。writer 写 wasAttuned，reader 没有消费它；实际 give 的额外 tier 通知比较源对象而非收取者，但 mergeApply 已执行完整同步。可复用共享物品不是恢复所有个人状态。
3. **水晶永久属性 → 实际工具耐久/挖掘**：未知合法注册项跳过；无 tier/重复属性校验。Attribute 构造器恒设 discovered=true，原 false 无法保留；不能仅看 getBoolean 就宣称无损。两个工具公式和每个属性不分计。

特别限制：备份 getter 先创建目标空文件，但 Files.copy 未指定 REPLACE_EXISTING；主文件缺失会先生成空文件而不读取已有备份；有效备份读取后的 copy-back 也可能落入失败清空分支。失败处理即使 .lerror 复制失败仍删两份数据，属于只读发现的风险，绝不执行/照搬。队列无同步、无成功确认，写 IOException 被忽略。这里的备份均为上游源码语义，未备份/删除用户文件。

JSONL 每条包含完整 evidence 支持链；主账 candidate/excerpt/normalized 精确匹配为零只代表机械筛查，仍须按语义与主责家族人工去重。与技能树/UUID/白名单家族可能重叠。未查清独立消费者的 attuned/trait getter 不列候选。版本为官方历史分支，不推定具体发布 jar 对应。

下一批保留同 commit 的 TreeBeacon 持久树状态、CelestialGateway 世界目录及真实消费者；未审查不计数，避免与本批个人研究/物品属性混算。十小时目标仍未完成，继续后续范围。
