# 现有材料炼入装备 · 第一版

本次以整个 Dynasty 项目 main 为基础（7a79adb），cod1 仅是交付分支。
检查了基础材料、稀有材料、回收材料、功能工坊、流派战斗、符箓和已有任务接口。
不改旧 Registry ID、名称、模型、贴图、掉落、配方、修理或其他原用途。
material-audit.json 列出每种真实名称及现有配方/掉落引用。

## 下载后生成游戏内容

下载 cod1 分支完整工程后，运行原来的 `3-打包整合包.command` 或 `打包整合包.command`。
现有 `exportModpack` 会先构建本次代码，再把新 Dynasty JAR、FTB 和配置放入完整 manual.zip。
只下载源码不会自动更新已经安装的游戏；安装新导出的完整包后，创造栏才会出现炼入台。

## 使用

创造栏搜索「炼入台」；生存合成：SJS / BCB / BBB，其中 S=银锭，J=玉，
B=青铜锭，C=工作台。完成原有「获得玉」进度后即可操作；创造模式免门槛与费用。
右键独立 GUI，放入一件武器/防具和材料，选择炼入位，再确认炼入或替换。
普通武器、防具、盾、弓弩、三叉戟及继承这些类型的 Dynasty 装备可用。
每件3个位置，总容量4；同一装备的同类特性冲突。2份材料+3级经验一次。
移除消耗1级经验，不退材料；替换消耗新材料，旧特性被替换。
输入物品归当前玩家容器，关闭、掉线或超出方块距离后由原版容器归还/掉落机制处理。
不向客户端接受结果 NBT，结果预览不是真实输出槽，不能拿取复制。

## 24 种新增用途

| 原材料 ID | 新能力 | 使用场景 |
| --- | --- | --- |
| shanxiao_claw | 魈爪连袭 | 同目标三次蓄满近战后增伤并减速 |
| ghost_face_fur | 鬼面脱身 | 防具受重击后短暂隐身 |
| yin_jade_shard | 寒玉镇魂 | 武器命中亡灵后减速 |
| nether_tatter | 幽缕卸力 | 防具受魔法伤害减伤并缓降 |
| blackened_bone | 腐骨镇煞 | 防具受亡灵攻击后净毒与抗性 |
| vengeful_war_soul | 战魂蓄煞 | 第四次蓄满命中释放伤害与虚弱 |
| heavy_shield_remnant | 残盾定势 | 格挡时保护盾牌耐久 |
| fine_steel_chain | 钢链稳身 | 降低敌人的一次击退 |
| swift_boot_scrap | 疾履借势 | 受击后短暂疾行 |
| dry_peach_branch | 桃木辟邪 | 亡灵显形并虚弱 |
| bronze_ingot | 青铜破势 | 打断正在使用物品的普通敌人 |
| silver_ingot | 银华照隐 | 打破敌人隐身并标记 |
| jade | 玉息回元 | 三连命中后恢复饥饿资源 |
| dragon_scale | 龙鳞护身 | 受重击后短暂伤害吸收 |
| dragon_crystal | 龙晶雷印 | 两连命中后雷印增伤与短暂迟滞 |
| cinnabar | 朱砂火印 | 条件触发点燃 |
| refined_steel | 精钢破甲 | 有护甲目标条件增伤（不永久修改目标护甲） |
| xuanwu_shell | 玄甲完璧 | 举盾前8刻成功格挡获得抗性 |
| qinglong_scale | 青龙追身 | 命中受伤目标后加速与跳跃 |
| baihu_fang | 白虎重袭 | 蓄满下落暴击附加重袭和击退 |
| zhuque_feather | 朱羽阳炁 | 受火伤后熄火与抗火 |
| taiyi_jade | 太乙御风 | 有冷却的坠落伤害减免 |
| ink_stick | 墨引符法 | 佩戴后原符箓法术命中获得护身抗性 |
| talisman_paper | 符纸回气 | 佩戴后原符箓命中恢复饥饿资源 |

真实数值、冷却、适用类型与解锁条件统一定义在 InfusionTraits，GUI同步显示。
战魂需要已有 entered_underworld，龙鳞/龙晶/四象/太乙需要 entered_celestial。
未新增通用灵力池：原符箓使用 indirectMagic，没有通用法力资源，回元使用现有饥饿资源。
没有制造真实雷实体、爆炸或地形损坏；雷印有服务端粒子和伤害反馈。
额外伤害总增幅上限35%，冷却按玩家持有，不因换同类装备重置。
只检测手持/穿戴装备；背包存放不生效，相同防具特性多件只结算一次。
攻击只对非盟友敌对生物生效，不对其他玩家与宠物触发。Boss免打断/额外击退，减速最多20刻。
弓箭在射出时保存装备快照，换手不能把后来的特性补进已射出的箭。

## 任务

保留原有任务节点、依赖和奖励，只在已有总览章增加一个无奖励可选节点，
通过 first_infusion advancement 检测第一次炼入。FTB未安装时也能用工作台。
已有饰品铁砧淬炼和八种工坊的旧交互完全保留。

## 验证

`python3 tools/audit_infusion.py` 在提交前对基线核查旧材料信息及原任务不变。
`python3 tools/art/make_local_repo.py` 准备现有 bundled dependencies。
`./gradlew -I tools/infusion-test.init.gradle -PinfusionTestRun=<新名称> runGameTestServer build --offline`
使用 build/infusion-gametest 下的隔离世界，不触碰用户存档。
测试结果与真实客户端视觉/联机验收状态见 validation.txt；不将服务端测试称为视觉验收。
