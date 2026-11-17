# Halley → Kepler：第四批，3 条手工建议，credit 0

只完成研究交付，不直接增加主账。78 个完整去重 AST 方法节点、19 个证据文件；144 个下载文件、740 个索引节点不计 credit。未执行上游代码，未编译或运行测试/游戏/服务器/真实 TCP，未操作屏幕或用户实例，未写主账/生产/原存档/待办。

来源已在下载前向 Kepler 保留：

- Tschipp/CarryOn，branch1.20，commit `41af4218d3d1ad86f9e9e1d3491529e205cbfcb3`。
- gigaherz/ToolBelt，branch1.20.1，commit `e5f7efe5d4005a06dd45ba314045e51f3d5fac9c`。
- SUPPORT ONLY：MinecraftForge/MinecraftForge，branch1.20.1，commit `d13dd327bdc75c010f3358992e80e7e92f51e030`；ItemStackHandler 不作额外实现 credit。

精确 tree/blob、文件 SHA256 与官方 commit/tree 原始响应见 tools 同名 batch-004/source-manifest.json 及 provenance。每条 JSON 含 repo/commit/path/start/end/name/source/sourceSha256/text/excerptSha256/normalizedSha256/url/observation/application/limits，以及完整 evidence 调用链与语义重复风险。入口 batch-004.json 或 reviewed-suggestions.jsonl。

1. Carry On：玩家根搬运快照 reader→实际拾取/放置→keepInventory/死亡/返回末地 Clone。方块、实体、玩家乘骑、保存/读取/Clone 合为一条，不拆平台计数。读盘缺 type 为 INVALID；非法枚举/脚本会抛出；实体创建失败清局部快照并返回云占位；放置结果未确认便清唯一搬运表示，不能当事务模板。临时按键、tick、槽选择与脚本也写入，不能整份借给永久进度白名单。该 branch1.20 的固定源码含较新 API，**未证明可编译1.20.1**。
2. Tool Belt 内部工具库：物品栈自己拥有 Size/Items/Slot，reader clamp2..9、首匹配，writer 只处理首重复槽，超容量旧条目未自动删除。铁砧 copy 后增 Size，缝纫旧tag.copy().merge(新结果tag)；升级与两个消费者同链合并。缝纫依赖 super.assemble 未补读，不推断 Count 完整保留。
3. Tool Belt 玩家额外腰带槽：LivingDrops 先消失诅咒/keepInventory/spectator 过滤，Clone 只接剩余腰带；新能力缺失则 drop，功能关闭则返还并清槽。oldPlayer.revive() 不是 reviveCaps。Clone 共用 stack 引用，未清旧槽，不宣称跨崩溃 exactly-once。与先前 selective Clone 有高家族重复风险，由主责裁决。

补读依赖范围：ToolBelt build.gradle 明确 Forge `1.20.1-47.1.3`，已只下载官方 sources.jar，SHA256 `f6b596560576b3c3e2e9292ab5016605e0c2959083701714ab6628eb388637eb`。ItemStackHandler.java entry SHA256 `056424ca0f84ec388530cd93af0d2e1a384eaeb731486ffdf6491b215f5d0cd0`；它与固定 Git 分支文件 **字节不相同**，完整 diff 已读，所用 serialize/deserialize/setSize/setStackInSlot 四个完整方法 AST 去标识规范化一致（SRG 名字差异）。原始 entry、精确方法正文/范围/哈希及比较在 provenance/MinecraftForge__MinecraftForge/declared-codec-methods.json；不把当前 Git commit 伪称47.1.3发布 commit，不声称二进制运行兼容验收。

document-integrity.json 仅静态文档溯源核对：Git blob/文件字节/完整 AST 范围与哈希无差异；当时主账921行，primary三类指纹无命中。语义去重仍待 Kepler，尤其 Carry On 与此前实体快照容器、额外槽与 capability Clone 家族。

用户已解除考试禁编译/测试；当前研究分工无需启动游戏。如后续确需图形/游戏/真实 TCP，由主协调集中安排，本岗先在记录注明，不自行启动。不修改原存档或删除游戏内容，不备份或删除未验收待办。10 小时研究目标仍在推进，交此批不等于结束。
