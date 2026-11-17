# 第八批：延迟归还、返程快照与防御成功门控

交 Carson 主审；3 条待审候选，全部 credit=0，未增加主计数。未凑足20条，不把36段完整方法与3段配置声明当39个实现。本批不宣称1000或剩余缺口闭合。

- `batch-008.json`：三条完整候选；每条含固定repo/revision/path/source_local/source_sha256/line/end_line/excerpt/observation/application/limits/url、支持链与语义去重。
- `source-index-008.json`：17个匠魂源文件逐个比对缓存固定提交树的Git blob SHA1并复制至专属目录；记录SHA256。另有原版本机Forge mapped源Jar的父类支持，明确只用版本与Jar SHA256，不伪造其Git提交/网页URL，不单独计数。
- `validation-008.json`：文本、完整范围与哈希校验 errors=[]；仅证据完整性检查，不是编译、测试或运行验收。

来源：既有官方来源缓存 SlimeKnights/TinkersConstruct，固定 `f4e77d43f39ba1047bf93ae816b7e1beaab514c2`。本轮没有外部请求或重试；不改变 rpginventory 既有排除。Apugli不足后转读已固定其他来源，依据人类已有明确授权；写权限仍限本岗两个helper目录。

1. `thrown-tool-owner-gated-original-slot-reconciliation`：ballista实际消费弹药前按对象身份记录原槽；实体持有独立单件，归还重验原槽空/同物同NBT可叠，否则回退库存。父类先检查owner或owner缺失，库存接收成功后才discard。与已入账磁盾先清PrevSlot再交换、ThrownTool重力/引信调度及shuriken伤害退款分别比较；同一投掷实体的任务入口、拾取分支和NBT不另算。特别限制：owner缺失允许拾取，不能说严格仅限原主人；loyalty可无界，1200/6000不是短TTL。
2. `returning-first-anchor-refresh-and-dimension-terminal-gate`：真实末影蛋糕ADD续期保持首个Added位置/维度，duration=1读快照，同维度才发可取消返程事件。区别第七批自爆终端与第六批流血续期；新单元是“首次位置快照跨续期保留+维度拒绝消费”，公共helper为0分支持。取消、提前移除、跨维度均未清anchor；结果忽略，没有once/代次标记，不照搬精确duration到横扫TTL。
3. `enderdodge-teleport-success-before-cooldown-and-hurt-cancel`：真实护甲MODIFY_HURT，最多16次可取消/碰撞检查；传送返回true后才设干扰冷却、损耗工具并返回0，真实LivingHurt入口取消伤害。两类来源概率配置只算同一链。此项是同步防御与效果冷却，相关性弱于前两条，保留供Carson保守裁决；不能说跨tick成功伤害回执，也不能把传送成功当作受害者实际损血。

原版支持已全文读：ThrownTrident.playerTouch/getPickupItem、AbstractArrow.playerTouch、Projectile.setOwner/getOwner/ownedBy。注意getOwner可从当前ServerLevel按UUID解析失败而返回null，不能省略这个放宽边界。相邻onHitEntity/onHitBlock已读，仅作排除：命中锁、防重复、临时持物交换与既有伤害/looting链关联，不增加本批有效数。

接续：原ThrownTool待补父类/生产链已闭合为本批候选1；下一步只读 RecurrentProtectionModule / RestoreLostHealthModule 的实际状态与消费入口，先对已有护甲1000/sweep链去重。仍未逐方法审完的线索信用为0。未动正式Java、QA、资产、总待办或Carson账本；无编译、测试、游戏、服务器、GUI、屏幕操作，集中run10由主协调处理。
