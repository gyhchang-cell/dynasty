# cod1 本地接续：2026-10-10

用户要求修改本地工程并删除已完成提示词，GitHub 由用户上传。没有提交或推送。本文件记录实际范围；**全部任务仍未完成：1 DONE / 49 PARTIAL / 44 NOT_STARTED（最新状态见文末；下方保留接续历史）**。

## 实际代码改动

- 古墓三方联动：只有溺鬼成功束足后发出同池、同遭遇、同攻击时钟的有限信号；纸人走正面、童子走背面，已开始的攻击不换目标。信号过期、施法者或目标死亡、离水和遮挡均取消。
- 帝陵新布局版本3加入西侧封闭深水池和入口台阶；旧布局保留原方块，新版纸人位于前方、童子在后方。赑屃与主通道不变。
- 纸轿接入已有阴司石林的午夜结构入口，沿用共享夜间时钟和原遭遇预算。发现并修复阴司噪声顶层密度导致地表结构落在建筑高度之外的问题；下部地形密度保持原值。**修改影响新生成区块，旧区块不会重建，新旧区块边界可能存在高度差。**
- 陷阵断头将：180HP，独立46骨骼/7动画，咆哮、三圈旋斩、锁点投首；背击打断投首、碰墙硬直、实际血池、原生掉落与击杀进度。已有古战场真实结构生成入口，有限UUID名额与死亡冷却；永久移除释放名额，区块卸载保留名额。
- 鬼车九首鸟：160HP，一个实际碰撞飞行实体，八张脸、三段颈骨和断裂中央颈，共74骨骼/7动画；十六次锁点啄击、最多八处血雾、俯冲抓取。侧移、盾挡、撞墙、受击与蹲下脱身有服务器处理；抓取限高限时并保留缓降。已有古战场夜空有限事件入口，真正生产世界入口尚待实机验收。死亡坠落已在最新单机和双客户端落地场景复测通过。
- 使用原有攻击时钟、粒子预算和遭遇存档；没有新维度、没有替换正式最终Boss镇渊帝君。两只精英使用已有功能材料及实际用途；没有改神器奖励来源。

## 已通过的验证及边界

Java17、Minecraft1.20.1、Forge47.4.10、GeckoLib4.8.4。工作区同时有其他本地聊天在改动与编译，原生JVM使用已有冻结脚本复制开发类目录，避免另一轮编译删除正在运行的类。记录对应各次实际输入，不能据此声称所有命名空间或其他聊天改动均验收。

| 验证 | 实际结果 | 不覆盖的范围 |
| --- | --- | --- |
| 初始服务器回归 | 172/172 | 客户端与压力 |
| 古墓联动和阴司入口回归 | 178/178、build通过 | 普通随机世界与活动重连 |
| 断头将三技能及原生保存回归 | 185/185 | 完整世界入口 |
| 断头将实际战场生成、死亡冷却和动作回归 | 186/186 | 假玩家不能领取进度，由真实客户端另外验证 |
| 两精英动作、永久移除与九首鸟死亡回归 | 最新197/197 | 修正原生夹具的实体区块加载时序；保留完整伤害、引信三秒和死亡断言 |
| 青龙关刀相机 | 单机56/56；真实TCP双客户端各14/14 | 不代表12种新神影已实现 |
| 前四只基础怪 | 单机22/22；真实TCP双客户端各22/22 | 普通世界分布、活动战斗重启与压力 |
| 军系五只基础怪 | 单机23/23；真实TCP双客户端各23/23 | 三秒引信完整实机生命周期、压力 |
| 披甲护卫、阴兵、力士、童子、纸人 | 最新单机48/48；真实TCP双客户端各48/48（纸人和童子UV已修正） | 实际结构进场、活动战斗重载与压力 |
| 飞颅、朱蛤、树精、石蝎、玄蛟幼崽 | 单机56/56；真实TCP双客户端各56/56，真实玩家击杀奖励通过 | 结构进场与活动战斗生命周期 |
| 机关组五只 | 最新单机54/54；真实TCP双客户端各54/54 | 结构进场、活动生命周期和压力 |
| 深洞组五只及纸轿 | 最新单机50/50和10/10；真实TCP双客户端各50/50和10/10，真实玩家击杀进度通过 | 结构进场、活动生命周期和压力 |
| 古战场 | 最新单机生产结构生成、正常AI/物理、七名盟友、探索进度及真实玩家受伤/自主攻击通过 | 双人进场、活动战斗重连/重启及压力 |
| 断头将 | 单机15/15；真实TCP双客户端各15/15；真实玩家击杀进度 | 活动战斗重连/重启、最终平衡与压力 |
| 鬼车九首鸟 | 最新单机12/12，真实双客户端各12/12；实际玩家击杀进度及死亡落地通过 | 生产入口、活动战斗生命周期和持续压力尚未实机验收 |

前九只基础怪已实际完成资源重载和空闲状态的真实客户端重连。这不是活动战斗重连。姿态截图已经复核；鸟的悬空问题由截图发现并修复。日志及联系表保存在 [本轮证据](evidence/local-20261010/)，原始客户端观察在 [ingame](ingame/)。各次PASS文件明确限定自己的范围，截图生成不等同完整内容DONE。

## 提示词清理

直接修改了用户原文件 `/Users/a15356015027/Desktop/code x提示词/cod1.txt`，另存 [仓库副本](cod1.txt) 供上传。已删除已经完成的青龙关刀黑屏/相机排查块和客户端启动验证阻塞要求；引信中断/冷却修复、古墓协调代码实现要求改为仅保留尚缺的实机与生命周期验收。纠正“仅9只基础怪已接入”的过时描述为30只，加入两只精英的实际进度。**没有完成整项验收的内容没有整项删除。**

## 每项实际状态

下表引用当前原有目录，未启动条目的拟定资源文件名不视为存在。历史auditStatus仍保留原始审计语义；当前实现依据implementationStatus及本次对应证据。

| 内容 | 状态 | 实现类 | geo / animation | texture | 技能 | 世界落点 | 掉落 / 奖励 | 单机 | 双人 | 性能与剩余风险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 卒伍刀手 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `zuwu_daoshou.geo.json` / `zuwu_daoshou.animation.json` | `royal_guard.png` | 阵型冲锋 | minecraft:overworld / two swordsmen guarding an existing ritual priest; safe solid floor | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_22_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_22_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 拒马长枪兵 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `juma_changqiangbing.geo.json` / `juma_changqiangbing.animation.json` | `archer.png` | 枪阵拒马 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_23_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_23_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 连弩阵卒 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `liannu_zhenzu.geo.json` / `liannu_zhenzu.animation.json` | `rebel_soldier.png` | 撤步填机 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_23_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_23_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 橹盾甲士 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `ludun_jiashi.geo.json` / `ludun_jiashi.animation.json` | `royal_guard.png` | 钢铁壁垒 | minecraft:overworld / one shield per military marker; protects ranged/support | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_22_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_22_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 符法祭酒 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `fufa_jijiu.geo.json` / `fufa_jijiu.animation.json` | `imperial_soldier.png` | 兵煞附体 | minecraft:overworld / existing star altar/herbal retreat; one priest with two swordsmen | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_22_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_22_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 铁索斥候 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `tiesuo_chihou.geo.json` / `tiesuo_chihou.animation.json` | `assassin.png` | 锁镰飞掷 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_23_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_23_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 溃军死士 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `kuijun_sishi.geo.json` / `kuijun_sishi.animation.json` | `rebel_soldier.png` | 绝命爆裂 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_23_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_23_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 阵亡掌旗官 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `zhenwang_zhangqiguan.geo.json` / `zhenwang_zhangqiguan.animation.json` | `royal_guard.png` | 军魂不散 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_23_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_23_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 披甲叛将护卫 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `pijia_panjiang_huwei.geo.json` / `pijia_panjiang_huwei.animation.json` | `royal_guard.png` | 霸体反击 | minecraft:overworld / 叛将大帐、地下军械库、关隘顶层 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_48_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_48_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 阴兵鬼卒 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `yinbing_guizu.geo.json` / `yinbing_guizu.animation.json` | `royal_guard.png` | 幽冥遁入 | minecraft:overworld / 浓雾古战场、阴气深涧、乱葬坑 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_48_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_48_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 尸变力士 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `shibian_lishi.geo.json` / `shibian_lishi.animation.json` | `nian_beast.png` | 腐尸剧毒 | minecraft:overworld / 潮湿古墓前室、悬棺崖壁下 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_48_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_48_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 缚魂白布童子 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `fuhun_baibu_tongzi.geo.json` / `fuhun_baibu_tongzi.animation.json` | `imperial_soldier.png` | 定身冤咒 | minecraft:overworld / 荒村枯井、荒芜祠堂、夜间古墓 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_48_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_48_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 纸人剑客 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `zhiren_jianke.geo.json` / `zhiren_jianke.animation.json` | `imperial_soldier.png` | 纸蜕替身 | minecraft:overworld / 荒废义庄、官宦墓道中庭、冥婚废宅 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_48_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_48_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 墓穴飞颅 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `muxue_feilu.geo.json` / `muxue_feilu.animation.json` | `imperial_soldier.png` | 污血淋漓 | minecraft:overworld / 古墓盗洞、深层岩洞、陵墓顶部穹顶 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_56_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_56_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 山精山魈 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `shanjing_shanxiao.geo.json` / `shanjing_shanxiao.animation.json` | `nian_beast.png` | 投石落木 | minecraft:overworld / forest/mountain, solid ground, collision-free, max3 within24 blocks | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_22_NATIVE_ACTION_POSE_STAGES_SCOPE_LIMITED | PASS_22_EACH_REAL_TCP_ACTION_POSE_STAGES_SCOPE_LIMITED | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 赤目朱蛤 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `chimu_zhuha.geo.json` / `chimu_zhuha.animation.json` | `nian_beast.png` | 火毒喷射 | minecraft:overworld / 沼泽水洼、阴暗溶洞潜水区、水畔芦苇荡 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_56_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_56_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 枯木树精 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `kumu_shujing.geo.json` / `kumu_shujing.animation.json` | `nian_beast.png` | 地刺根须 | minecraft:overworld / 阴沉古林、腐烂老树桩群、荒山野径 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_56_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_56_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 鸣沙石蝎 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `mingsha_shixie.geo.json` / `mingsha_shixie.animation.json` | `nian_beast.png` | 金石鸣沙 | minecraft:overworld / 戈壁荒滩、干涸河床、风化沙谷 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_56_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_56_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 碧水玄蛟幼崽 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `bishui_xuanjiao_youzi.geo.json` / `bishui_xuanjiao_youzi.animation.json` | `nian_beast.png` | 寒潭盘绞 | minecraft:overworld / 地下暗河、高山深潭、瀑布水穹 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_56_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_56_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 巨臂石敢当 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `jubi_shigandang.geo.json` / `jubi_shigandang.animation.json` | `royal_guard.png` | 重碑镇煞 | minecraft:overworld / 破损山门、古驿道十字路口、陵寝神道 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_54_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_54_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 巡山木甲犬 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `xunshan_mujiaquan.geo.json` / `xunshan_mujiaquan.animation.json` | `rebel_soldier.png` | 鸣簧示警 | minecraft:overworld / 机关城外围、工匠遗迹、地下库房走廊 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_54_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_54_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 青铜双头蛇傀 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `qingtong_shuangtoushekui.geo.json` / `qingtong_shuangtoushekui.animation.json` | `rebel_soldier.png` | 前后互博 | minecraft:overworld / 机关密室、重臣墓道排水渠、地宫翻板陷阱下 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_54_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_54_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 八足地工蛛 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `bazu_digongzhu.geo.json` / `bazu_digongzhu.animation.json` | `rebel_soldier.png` | 天花破顶 | minecraft:overworld / 矿坑深处、古代采石场遗迹、机关城下层 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_54_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_54_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 幽灯鬼面蝠 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `youdeng_guimianfu.geo.json` / `youdeng_guimianfu.animation.json` | `nian_beast.png` | 幽灯致盲 | minecraft:overworld / 大型地下穹窿、溶洞钟乳石林、裂谷暗处 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_54_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_54_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 穴居盲骨鱼 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `xueju_mangguyu.geo.json` / `xueju_mangguyu.animation.json` | `royal_guard.png` | 地脉共鸣 | minecraft:overworld / 地下大空洞地热区、灵脉深处 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_50_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_50_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 煞水浮溺鬼 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `shashui_funigui.geo.json` / `shashui_funigui.animation.json` | `imperial_soldier.png` | 溺水缚足 | minecraft:overworld / 死水沼泽底、护城河淤泥、沉船水域 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_50_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_50_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 巨力赑屃傀儡 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `juli_bixi_kuilei.geo.json` / `juli_bixi_kuilei.animation.json` | `royal_guard.png` | 千钧重压 | minecraft:overworld / 神道尽头、地下碑林、宗庙遗址 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_50_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_50_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 百目魔蜈 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `baimu_mowu.geo.json` / `baimu_mowu.animation.json` | `nian_beast.png` | 百目凶光 | minecraft:overworld / 万骨坑底、废弃丹炉地窖、极深断裂带 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_50_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_50_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 铜臂飞天夜叉 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `tongbi_feitian_yecha.geo.json` / `tongbi_feitian_yecha.animation.json` | `nian_beast.png` | 鹰击长空 | minecraft:overworld / 深渊裂谷边缘、悬空古栈道、帝陵外侧虚空 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_5_50_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_5_50_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 阴阳纸轿游魂 | PARTIAL | `BlueprintEntities.java`<br>`TemplateMob.java` | `yinyang_zhijiao_youhun.geo.json` / `yinyang_zhijiao_youhun.animation.json` | `imperial_soldier.png` | 幽轿锁魂 | minecraft:overworld / 午夜山隘道、无名野坟岗路口 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_NATIVE_BATCH_OF_1_10_STAGES | PASS_NATIVE_REAL_TCP_BATCH_OF_1_10_STAGES_EACH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 陷阵断头将 | PARTIAL | `EliteContent.java`<br>`HeadlessGeneral.java` | `xianzhen_duantoujiang.geo.json` / `xianzhen_duantoujiang.animation.json` | `royal_guard.png` | 断头咆哮、破阵回旋旋风斩、掷首锁魂 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_15_NATIVE_STAGES_AND_CONNECTED_PLAYER_KILL_HOOK | PASS_15_EACH_REAL_TCP_STAGES_AND_CONNECTED_PLAYER_KILL_HOOK | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 鬼车九首鸟 | PARTIAL | `EliteContent.java`<br>`GhostCarriageBird.java` | `guiche_jiushouniao.geo.json` / `guiche_jiushouniao.animation.json` | `nian_beast.png` | 八首乱啄、九婴啼血、低空掠食抓投 | minecraft:overworld / 待接入 | REGISTERED_RUNTIME_LOOT_AND_USES | PASS_12_NATIVE_STAGES_KILL_HOOK_LANDED_DEATH | PASS_12_EACH_REAL_TCP_STAGES_KILL_HOOK_LANDED_DEATH | 活动生命周期、入口差异、压力与最终平衡未验收 |
| 千机百炼偃师 | PARTIAL | `blueprint/elite/Mechanist.java` | `blueprint/elite/qianji_bailian_yanshi.geo.json` / 同名animation | `blueprint/qianji_bailian_yanshi.png` | 天罗地网丝、飞刃双轮切、构装自爆蛛群 | minecraft:overworld / 天工城工坊与矿场 | 三种原有功能机械材料 | 原生15场景+工坊入口PASS | 双端各15场景+工坊入口PASS | 活动生命周期、矿场次入口、盾牌扩展回归和等级平衡待验收 |
| 披鳞执金吾 | NOT_STARTED | 未接入 | `pilin_zhijinwu.geo.json` / `pilin_zhijinwu.animation.json` | `pilin_zhijinwu.png` | 断水大横扫、破军直刺冲锋、金吾阵令 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 白面狐仙姑 | NOT_STARTED | 未接入 | `baimian_huxiangu.geo.json` / `baimian_huxiangu.animation.json` | `baimian_huxiangu.png` | 心魔幻镜、狐火天降、魅影分身 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 巨锤金甲力士 | NOT_STARTED | 未接入 | `juchui_jinjia_lishi.geo.json` / `juchui_jinjia_lishi.animation.json` | `juchui_jinjia_lishi.png` | 撼地双锤砸、狂怒大车轮、铜锤飞掷 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 蛊毒天蛛女 | NOT_STARTED | 未接入 | `gudu_tianzhunv.geo.json` / `gudu_tianzhunv.animation.json` | `gudu_tianzhunv.png` | 天顶毒瀑布、飞丝坠杀、寄生幼蛛卵 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 阴阳炼丹方士 | NOT_STARTED | 未接入 | `yinyang_liandan_fangshi.geo.json` / `yinyang_liandan_fangshi.animation.json` | `yinyang_liandan_fangshi.png` | 阴阳双煞火、丹煞火海、汞毒金丹 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 伏波巡海夜叉 | PARTIAL | TideYasha / TideVortex / Renderer / 原时钟 | `geo/blueprint/elite/fubo_xunhai_yecha.geo.json` / 对应7段animation | `textures/entity/blueprint/elite/fubo_xunhai_yecha.png` | 分水破浪斩、潜渊突袭、逆水三连挑 | minecraft:overworld / warm、cold ocean ruin / 3×3承重水下地板 | 三种原生掉落与实际用途 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件检查通过；当前构建、实战、生命周期、平衡验收待完成 |
| 搬山甲胄尸狂 | PARTIAL | RageCorpse / RageCorrosion / Renderer / 原时钟 | `geo/blueprint/elite/banshan_jiazhou_shikuang.geo.json` / 对应7段animation | `textures/entity/blueprint/elite/banshan_jiazhou_shikuang.png` | 尸狂龙卷、肉弹飞扑、怨血喷涌 | minecraft:overworld / 新版帝陵开阔陵室东侧25,1,16 | 三种掉落及燃料/回收/剑配方 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件通过；当前构建/实战/生命周期/平衡待验收 |
| 墨家绝影刺客 | PARTIAL | InkAssassin / InkSpike / InkCloud / InkBamboo / Renderer | `geo/blueprint/elite/mojia_jueying_cike.geo.json` / 对应7段animation | `textures/entity/blueprint/elite/mojia_jueying_cike.png` | 水墨遁形、八方墨影斩、墨滴爆裂 | minecraft:overworld / 天工城现有内库廊道87,1,94 | 三种掉落与墨竹原生驱雾 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件通过；原生构建/实战/生命周期/平衡待验收 |
| 撼山铜甲巨猿 | PARTIAL | BronzeGorilla / GorillaStone / Renderer | `geo/blueprint/elite/hanshan_tongjia_juyuan.geo.json` / 对应7段animation及双投射物 | `textures/entity/blueprint/elite/hanshan_tongjia_juyuan.png` | 铜臂狂乱大捶打、拔木穿石、飞跃震荡扑杀 | minecraft:overworld / 高山废弃传送门周边/古战场西侧10,4,13 | 铜片回青铜锭、碎块拼原版石 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件通过；原生构建/实战/生命周期/平衡待验收 |
| 青灯判官鬼差 | PARTIAL | LampJudge / JudgeSpell / Renderer | `geo/blueprint/elite/qingdeng_panguan_guichai.geo.json` / 对应7段animation及三法术 | `textures/entity/blueprint/elite/qingdeng_panguan_guichai.png` | 生死勾名、铁画银钩、勾魂铁索牢 | dynasty:underworld / 新版封印遗迹外厅、合法6格圈 | 铁页回铁粒、封墨换黑染料 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件通过；原生构建/实战/入口/生命周期/平衡待验收 |
| 烈风金雕羽士 | PARTIAL | GoldenEagle / EagleArrow / Renderer | `geo/blueprint/elite/liefeng_jindiao_yushi.geo.json` / 对应7段animation及羽箭 | `textures/entity/blueprint/elite/liefeng_jindiao_yushi.png` / 独立失色死亡图 | 实体24箭雨、36硬羽、碰撞俯冲/5秒反制 | 主世界现有高峰/雪山前哨周边、已加载地面Y>=100、原点4m | 硬翎制箭、骨弓片回骨粉 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件检查通过；构建/真实实战/自然入口/生命周期/性能平衡待验收 |
| 镇墓狻猊铜吼 | PARTIAL | BronzeSuanni / SuanniEffect / Renderer | `geo/blueprint/elite/zhenmu_suanni_tonghou.geo.json` / 对应7段animation及火柱/裂缝 | `textures/entity/blueprint/elite/zhenmu_suanni_tonghou.png` / 独立熄灭死亡图 | 实际3秒90度扫火、5段地火、4m破盾原生抗性吼击 | 现有新版帝陵局部15,1,17、单UUID、确认死亡永久清场 | 铜齿轮熔铜、石火余烬燃料 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件检查通过；构建/真实实战/自然入口/生命周期/性能平衡待验收 |
| 断代凶镬·饕宴之尸 | PARTIAL | TaoyanCauldron / CauldronGroundSpell / CauldronPits / Renderer | 两种真实活镬geo / 各12段animation / 有限油池火缝 | 两阶段16px原生贴图 | 实际12m冲撞、270度骨鞭、油池、丧钟、六裂缝跃砸、柱反制吸力 | 新注册真实40m祭坑、三骨祭祀、单UUID | 三材功能回收、200XP击杀进度、每玩家首次魂晶 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源码/软件通过；耐力/完整登场声画/复战/FTB及原生构建/实战/入口/生命周期/平衡性能待验收 |
| 殉节盲帅·公孙无妄 | PARTIAL | BlindMarshal / MarshalProjectile / MarshalCourtyards | 骨马誓龛及铁橇两形态 / 各12段动作 / 三独立投射物 | 16px原生四色 | 真实绕场内切、低刀风、声音反制、24墙箭、七推进裂隙、限定血雾四闪斩 | 新注册32m瓮城、15m墙、7m门、单UUID | 三材回收、200XP、死亡后中央每玩家一次真龙吟刀 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 源/软件通过；完整声画、复战/FTB、原生构建/实战/入口/生命周期/平衡性能待验 |
| 九霄木鸢·鲁班遗煞 | PARTIAL | WoodKite / WoodKiteBomb / StargazerPlatforms | 真9m翼展/5.5m/73骨骼/双四爪与5级翼轨；26×81 | 四色16px/实UV/原同尺度软件图 | 六技能/200登场/60%转金属48t/220死亡/实际飞行与8触地弹 | 真Y200/35格无护栏平台/首次绳梯/150格坍塌/中央胜利梯 | 修耐久/缓降/图纸制绳梯/一次首杀页/原生击杀 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 八SOURCE未运行；抓取/边缘/入口/生命周期/平衡性能/复战/FTB/声画待验 |
| 沉渊骨龙·烛阴残蜕 | NOT_STARTED | 未接入 | `zhuyin_cantui.geo.json` / `zhuyin_cantui.animation.json` | `zhuyin_cantui.png` | 幽冥冰霜吐息、骨剪摆尾、潜水盘绞、冰魄陨坠、烛阴开眼·天地皆昼、黄泉逆流穿刺 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 金阙尸仙·昭明帝 | NOT_STARTED | 未接入 | `zhaoming_di.geo.json` / `zhaoming_di.animation.json` | `zhaoming_di.png` | 天子九剑·破虏、十二水银飞剑、玉玺镇国运、汞毒血海、万国来朝万剑阵、帝王尸气斩、真龙解体 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 赤练红罗·蛇母娘娘 | NOT_STARTED | 未接入 | `shemu_niangniang.geo.json` / `shemu_niangniang.animation.json` | `shemu_niangniang.png` | 煞音断魂弦、巨蟒贴地横卷、百蛇破土、红罗障目、赤练死锁绞杀、万毒归宗血雾 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 无相孽火·黑风法王 | NOT_STARTED | 未接入 | `heifeng_fawang.geo.json` / `heifeng_fawang.animation.json` | `heifeng_fawang.png` | 无间黑炎球、大悲黑光掌、业障吸星、罗汉降魔杵、明王八方乱打、天魔大寂灭 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 镇国机关偶·刑天遗卫 | NOT_STARTED | 未接入 | `xingtian_yiwei.geo.json` / `xingtian_yiwei.animation.json` | `xingtian_yiwei.png` | 战神断岳斩、重盾排山、飞轮磨魂、泄压蒸汽暴、天倾地裂八方碎、追魂狂暴轮斩 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 九天玄刹·雷泽巨灵 | NOT_STARTED | 未接入 | `leize_juling.geo.json` / `leize_juling.animation.json` | `leize_juling.png` | 雷公槌击破虚、八鼓连珠天雷、电浆乱舞球、雷泽充能、天罚大审判、神速千雷瞬刺 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 幽冥引渡·彼岸冥舟 | NOT_STARTED | 未接入 | `bian_mingzhou.geo.json` / `bian_mingzhou.animation.json` | `bian_mingzhou.png` | 铁篙碎浪劈、骨桨碾压冲锋、彼岸花落生魂引、往生丧音、万魂齐喑冲天炮、忘川沉沦死境 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 封魔剑冢·玄天剑煞 | NOT_STARTED | 未接入 | `xuantian_jiansha.geo.json` / `xuantian_jiansha.animation.json` | `xuantian_jiansha.png` | 重剑开天门、飞剑游龙击、剑气画地为牢、剑刃风暴、瞬影万剑一、天剑劫·落九霄 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 四象逆脉·混元祖兽 | NOT_STARTED | 未接入 | `hunyuan_zushou.geo.json` / `hunyuan_zushou.animation.json` | `hunyuan_zushou.png` | 青龙裂霄霆、虎跃裂穹爪、朱雀劫火焚八荒、玄武厚土逆反盾、玄蛇噬魂毒域、四象混沌大寂灭 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 龙吟斩马断岳刀 | PARTIAL | ArtifactAbility / ArtifactItem / LongyinAbility / ArtifactWave / ArtifactCombat / Memorial | 真2.2m刀身/3m全刀；手持vanilla Cuboid与世界geo共用17块；地裂81帧 | 16px四色刀与独立土石 | 横扫/真实40tick蓄力/十格有限地裂/一次拼刀与包围反制 | 公孙确认击败后中央永久纪念刀 | 空手每玩家一次领取、原生获得进度；无任意合成 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 六SOURCE回归未执行；独立韧性API、其他精英硬直、真击飞高度、持握/生命周期/平衡声画待验 |
| 湛卢仁道八面剑 | PARTIAL | ZhanluAbility / ZhanluField / ZhanluTrialRewards / TaiqingTrials | 真1.4m八面刃/15块手持同源；两段81源姿态 | 16px四色剑/八卦玉太极/2m三状态剑匣 | 四段独立判定/3倍虚空/真实70%减速租约/80tick恢复；三清40t/5点/120t四脉冲 | 太清观21×21实际结构/支撑琉璃屋顶/绿台白道青阵/空手古剑匣 | 实际无伤三关/持久化一次领取/领取留空匣；无合成 | NOT_RUN_USER_EXAM_JAVA_PAUSE | NOT_RUN_USER_EXAM_JAVA_PAUSE | 八神器加二太清SOURCE未运行；完整自然来源/三关/碰撞裁剪/持握战斗/生命周期/拥挤PvP/其他精英时钟/平衡FTB待验 |
| 九曲透骨红缨枪 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `jiuqu_tougu_hongying_qiang.png` | 回马夺命扎、虚实红缨 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 方天乱世破军戟 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `fangtian_luanshi_pojun_ji.png` | 无双乱舞破军阵、狂宴噬血 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 逐日流金落星弓 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `zhuri_liujin_luoxing_gong.png` | 九乌贯日、悬日灼目 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 天机匣式神机弩 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `tianji_xiashi_shenji_nu.png` | 破甲床弩轰、发条储能 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 惊鸿流云金丝扇 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `jinghong_liuyun_jinsi_shan.png` | 拨云见日、清风化煞 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 镇岳九龙受命印 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `zhenyue_jiulong_shouming_yin.png` | 泰山压顶、地脉护佑 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 照胆通幽八卦镜 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `zhaodan_tongyou_bagua_jing.png` | 显形破煞、反躬自省 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 惊世太古晨钟 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `jingshi_taigu_chenzhong.png` | 大音希声、荡涤灵台 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 千机罗刹百刃伞 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `qianji_luosha_bairen_san.png` | 罗刹千刃旋、天罗雨幕 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 广陵遗响九霄琴 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `guangling_yixiang_jiuxiao_qin.png` | 广陵止息·剑气纵横、七弦杀音 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 绝笔春秋判官笔 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `juebi_chunqiu_panguan_bi.png` | 铁画银钩·诛、青史斑斑 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 缚龙索魂玄铁链 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `fulong_suohun_xuantie_lian.png` | 困龙升天、链锁连环 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 夸父逐日追光杖 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `kuafu_zhuri_zhuiguang_zhang.png` | 化杖为林、逐光之志 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 八卦紫金飞龙葫 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `bagua_zijin_feilong_hu.png` | 请君入瓮、纳气还真 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 伏羲连山归藏易 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `fuxi_lianshan_guizang_yi.png` | 大衍之数、勘破死生 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 破阵轰雷生铁铳 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `pozhen_honglei_shengtie_chong.png` | 开山巨铁弹、火浪余威 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 斩业诛邪双柳叶 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `zhanye_zhuxie_shuangliuye.png` | 流星赶月飞柳叶、斩业非斩人 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 辟邪白玉镇魂箫 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `bixie_baiyu_zhenhun_xiao.png` | 凤求凰·安魂曲、清心玉魄 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 翻江倒海混天绫 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `fanjiang_daohai_huntian_ling.png` | 混天锁海大缠绕、随风御浪 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 驱邪伏魔金刚杵 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `quxie_fumo_jingang_chu.png` | 金刚怒目·雷殛伏魔、不动明王 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 青蚨聚宝金错刀 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `qingfu_jubao_jincuo_dao.png` | 青蚨飞散、利市三倍 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 幽都忘川招魂幡 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `youdu_wangchuan_zhaohun_fan.png` | 百鬼夜行·借道、驭灵行尸 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 乾坤阴阳两界环 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `qiankun_yinyang_liangjie_huan.png` | 阴阳互易、乾坤共振 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 巨灵开山神手 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 明镜照世法身 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 三坛海会三头六臂法相 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 玄武磐石覆地真影 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 太白剑仙器灵出窍 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 九天玄女引天刑 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 凶煞白虎裂天影 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 伏羲八卦开天指 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 上古夸父逐日奔影 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 忘川摆渡幽冥客 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 墨家巨子千手天工枢 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |
| 烈火祝融九龙绕体神像 | NOT_STARTED | 未接入 | 未接入 / 未接入 | 未接入 |  |  / 待接入 | NOT_APPLICABLE_VISUAL_ONLY | NOT_RUN | NOT_RUN | 尚未实现 |

后续仍须完成12只精英、12Boss、25神器、12神影，以及33项已经接入内容的剩余验收。不能以登记、构建或某一类测试代替这些要求。

服务器bird5曾有两项失败（战场夹具未确保实体区块就绪、引线夹具固定第48 tick中断）；未删除失败断言。补上QA专用区块票与失败时清理，从实际点燃时刻验证眩晕及新三秒引线后，bird6最新194项全部通过。正式世界生成不会强加载区块。失败和复测日志均保留在 evidence/local-20261010。

最新接续：修复基础飞行怪/顶棚爬行怪死亡时只关闭无重力却不下落的问题，沿用原版碰撞移动；四种飞行怪实际落地且44 tick寿命不延长的回归通过，整批195项通过。叛将护卫、阴兵、力士、童子、纸人单机48场景及双客户端各48场景通过；单机早于这一共享坠落改动，仍待最新单机补测。两次双人初始握手失败未算通过；第三次使用2G/两CPU原生JVM运行完成。准备阶段曾因重复运行ID而拒绝旧QA清单，保留该失败；实际双端输入见该次 native-runtime-manifest.json，未改动失败记录。

最新纸人/童子UV保持原贴图不变，改取原图中性灰像素；纸人死亡去除持续受伤红色覆盖。`tomb-network4` 登录超时失败已保留；使用同一冻结输入的 `tomb-network5` 两真实客户端各48场景通过，未据此断言已修复连接根因。朱蛤测试夹具改为真实地面接触和实际损血至少6点的重击门槛，正式技能断言未削弱。


## 七人战场与编队边界修复

固定的祭酒、旗官、两斥候、三死士此前沿用了生态阵营分配，导致一个编队内部互相攻击。生产生成后现将该固定遭遇成员统一为叛军，并在原生实体读档时升级旧存档；其他生态种群阵营保持各自规则。已有实际结构生成测试同时核对七个成员及保存后阵营。

共享目标、附体、盾阵和斥候牵引点现在要求同遭遇及合法盟友；缓存每次使用仍检查距离和视线，换据点或阵营后立即解除。服务器 **197/197** 通过，包括跨据点目标隔离及已命中钩索换据点后的解除。日志见 `evidence/local-20261010/assault-server.log.gz`。

`local-20261010-assault-combat` 由生产生成的七人编队保留正常AI/物理，真实生存玩家被伤害，退出时仍有非零攻击、已消耗命中帧和冷却。前两次独立JVM重启因验证时序错误而失败，证据保留；第三次使用全新世界和完整实体tick检查通过。

双客户端深洞/纸轿后续尝试分别遇到显示器休眠的GLFW启动失败及Forge登录超时；只有通过的48/56/54场景批次标为客户端PASS。真实截图已复核，启动失败和空渲染帧没有算作动作验收。


最新 `local-20261010-assault-combat3` 及独立JVM `...-resume` **均通过**。保存时四名成员仍有非零攻击；加载时逐一核对七个UUID、实际冷却、攻击起点和已消耗命中帧，并观察到第一次原生实体tick，正常到期的动作不重放。资源加载队列造成的时序差已由验证器分别检查“刚加入”和“实际tick”，正式攻击逻辑没有为了测试改动。双方结构截图已查看。此证据完成了本场景的活动攻击存档恢复，尚未覆盖第二玩家活动重连、点燃中的三秒引信和持续压力。

最终深洞及纸轿双客户端由原版LAN开放流程启动，分别 **各50/50、各10/10** 通过并复看截图。原来仅手动创建TCP监听的测试器不设置原版已发布状态；更换为原版流程后的两组通过，但不把此前偶发超时全部宣称为已证明同一根因。至此30只基础怪都有本轮单机及双客户端动作证据。

## 乱军活动战斗重连（22:37）

`local-20261010-combat-rejoin2` 两个原生客户端通过实际资源重载及第二名玩家断线重连。原生服务器记录 peer 同一 UUID：JOIN57 → LEAVE845 → JOIN891；断线前斥候正在技能15、死士正在技能17，重连后四名存活者继续自然推进技能。初始七个生产生成的 UUID 由服务端原始队列和实际死亡事件核对；减少为四个存活者不是重建队列。两端资源重载后及 peer 重连后，实际 Gecko 控制器动画与近期服务器技能ID、起始时间一致。

该次 PASS.txt 通用旧模板仍称活动重连另验，以本轮 `resource-reload.json`、`peer/rejoin-before.json`、`peer/rejoin.json` 和 `coord/peer-session-events.jsonl` 的具体断言为准；模板已修正供后续运行，历史文件不覆写。引信进行中重启、压力及完整组合流程仍需继续核对。

## 三秒引信进行中原生存档重启（23:17）

`local-20261010-fuse-checkpoint3` 在实际生产 AI 的技能17前摇、NearTicks40时调用原生停止服务器，保存真实实体和军队状态；`...-resume` 从另一个 JVM 正常加载该存档，确认同一 UUID 的旧引信动作清除、未消耗的技能17冷却清除，其余技能冷却保留。实际实体首 tick 通过。连接的主玩家明确处于生存模式后，正常 AI 重新累计连续近身时限，旧中断动作没有补放；新的连续计数直到60tick才触发自爆。主玩家真实承受伤害，五名存活者与两次实际死亡事件对应，整套入口没有重新制造初始七人队伍。具体断言与计数见 `fuse-restart.json`、`world-combat-reload.json` 和 `world-final-ledger.json`。

首轮 `fuse-checkpoint` 未等待点燃即结束，已标 INVALID_ACCEPTANCE；第二轮源存档成功，但 resume 只验证了原生取消，缺少后续连续爆炸证据，已标 FAIL并保留。第三轮两个过程都通过，不能把前两轮当作成功记录。

## 2026-10-11 偃师和有限压力接续

偃师接入真实服务器三种攻击：14tick蓝丝网、10tick前摇双轮40tick往返、4只所有者绑定的有限自爆蛛。网的90%减速、位移技能拒绝、墙/中间空隙、背部重击打断、自爆蛛反伤与不破坏地形、死亡清理均有实际服务器回归。7项基础偃师测试与原有内容共204项的历史原生运行通过；新增盾牌/卸载墙测试后的206项回归仍在修复，失败日志保留，未把扩展全批标PASS。

`local-20261010-mechanist-solo3` 单机15场景、`local-20261010-mechanist-network3` 两真实TCP客户端各15场景通过。修复轮刃首次tick被误当卸载时间差的问题；修正死亡动画地下穿模并复核截图。第15场景用现有天工城生成器和旋转后的真实工坊地板，普通EliteEncounters tick产生1只正常AI偃师，测试不直接生成该演员。矿场次入口尚未验收。

同一冻结输入的 `local-20261011-stress-solo` 和 `local-20261011-stress-network` 各实际观察3600服务器tick，48个活动槽位包含30种基础怪与3种精英；死亡后有限替换维持负载，保留正常AI/物理。每个客户端覆盖33种实际渲染器，服务器各181次采样，客户端183/185/184次采样。

| 测量 | 单机 | 双人Host | 双人Peer |
| --- | --- | --- | --- |
| FPS中位数/最低 |111 /47 |107 /104 |109 /46 |
| 服务器tick均值中位数/最高(ms) |2.12 /3.94 |2.34 /4.77 |由Host服务器采样 |
| 最大已加载实体 |339 |302 |同Host世界 |
| 最大堆内存(MiB) |989 |1031 |1020 |
| 次级动画状态缓存最大值 |5 |4 |4 |

范围：本机、渲染距离4、无额外光影、三分钟人工恒定负载。实体计数包括普通掉落与投射物，在这段运行内没有超过512的检查预算。该记录不等于无限时长稳定性、全部真实结构分布或等级平衡已经完成。

偃师已实现的技能提示词已删，保留活动生命周期、次入口、扩展回归与平衡缺口；桌面源文件与仓库副本逐字同步。94项当前33PARTIAL/61NOT_STARTED，没有整项DONE声明。古墓第一轮实际自主组合/离池解除通过，但第二轮从合法入口进入后发现童子池沿导航卡住；修复实际池沿阶梯后正在新世界复测，失败不算完成。

轮刃扩展回归发现公共`DynastyCombatEvents`将完整盾挡后的Forge零伤害再次提升为1，导致盾牌耐久已消耗但仍受伤。现对进入管线的非正伤害直接返回，保留正伤害的原有计算与最低值；实际ShieldBlockEvent和最终LivingDamageEvent回归正在复测。

最新 `local-20261011-shield-server6` 原生专用服务器退出0，206/206必需测试通过；含真实盾挡事件、零轮刃最终伤害、盾牌耐久和轮刃卸载时间差回归。古墓池沿增加第二级台阶后的单机自主组合、离池解除与资源重载通过。首次双人因Forge握手断开而失败，未算联机验收。

## 2026-10-11 古墓实际协同和原存档重启

`local-20261011-tomb-combat-solo6` 原生单机通过真实帝陵生成、通常AI/重力、同水池时钟的童子诅咒与纸人正面斩击、离水后控制消退、实际资源重载及返回积水。`local-20261011-tomb-restart-solo6` 独立原生进程加载该次原存档，三UUID和据点保持、冷却没有重置，120个实际服务器tick后旧技能和控制未永久残留。此重启观测不声称覆盖首次实体tick；记录见各run的combat/restart/checkpoint JSON。最终截图已检查，位于实际墓室内部；之前两次行为通过但相机在墓室外的运行已标记不作为视觉验收。实际台阶修复只用于新版本3帝陵，旧区块不会重建。双人流程仍在验收，未据单机标整项DONE。


## 2026-10-11 双人古墓协同收尾与金吾接入

`local-20261011-tomb-route-network12` 两个独立原生客户端均通过：实际帝陵生成、正常AI三成员、同一水池起点的诅咒与纸剑、离水解除、双方资源重载及第二客户端实际断线重连。`local-20261011-tomb-restart-network14` 从新进程加载原存档，两端再次通过，三成员UUID和据点未重建，冷却未重置，120个实际服务器tick后过期攻击和控制没有残留。第一次network12重启尝试登录失败，保留FAIL，不算通过。至此该组合的剩余提示词已从桌面源文件及仓库副本删除；不表示其他基础怪已经整项DONE。

披鳞执金吾已接入实体注册、属性、三种实际服务器技能、单次据点守卫、晚加入技能同步、原生掉落与击杀进度；原创分段骨架45骨骼/67方块、7动画、实际16×16四纯色贴图。build通过。七项新增服务器测试中的六项通过，远端夹具刚生成即按UUID查找导致一项失败，正在修正验证时序；完整214项回归尚有三个失败，未标整批PASS。原生动作、入口、活动生命周期与最终平衡继续验证，金吾任务尚保留。


最新 `local-20261011-mechanist-entries-solo14/network14` 单机与两实际TCP客户端均16场景通过。当前采用并行美术工作的新cod2_voxel渲染器/资源；保留其分段骨架，只补回死亡后护心镜熄灭、箱盖/背箱与四辅助臂的过载动作，并同步原生成源。14个动作/姿势及实际工坊、矿场生成均通过；已删除矿场次入口缺口，活动生命周期与平衡继续验收。

金吾单机与双客户端14个姿势/动作全部获得实际Gecko动画证据；整轮在第15个生产入口时因验证器把活着的入口演员误按死亡膝盖检查而FAIL，未宣称整轮PASS。检查已限制到两个死亡场景，入口相机移到通道避免祭台遮挡，下一冻结构建重新完整运行。


## 2026-10-11 机巧师整项收尾、金吾动作及215项回归

`local-20261011-regression22` 原生服务器退出0，215/215必需测试通过。原生守卫测试改为独立批次，之前同批次的阵令演员触发正式32格防重复生成限制；正式生成上限未放宽。飞颅死亡/古墓导航测试先等待实际实体区块开始tick，再检查真实落地和移除，未改变正式伤害或死亡物理。此前214项失败日志保留。

`local-20261011-jinwu-solo22/network22` 单机与两原生TCP客户端均完整16场景PASS，包含实际古墓与关隘生成入口、全部7种Gecko动画、双手持戟、水平冲锋、单膝死亡与实际玩家击杀进度。GeckoLib4.8.4的world matrix tracker用矩阵相加平移，混入两份单位矩阵；动作验收改为实际model-space旋转与同空间握持点，冲锋轴Y误差小于2e-7。之前失败证据保留。金吾活动战斗、原存档生命周期与压力仍继续，未整项DONE。

偃师`local-20261011-mechanist-combat-solo14`及`...-resume`，`local-20261011-mechanist-combat-network22`及`...-resume`均PASS。实际天工城生成、正常AI三技能自主释放；双方资源重载、第二玩家真正TCP断线重连；独立JVM加载原存档并在首次实体tick检查UUID、原动作时钟、已消耗释放帧和冷却不重置。四原召唤蛛按绝对时限消失，未重复生成。旧network14失败源于QA非原子JSON发布，network18失败源于真实peer玩家未移到实体跟踪范围；修复仅QA，失败记录不删除。

215项中的原生青铜/白银剑校准通过正常ServerPlayer.attack与Forge/护甲管线，偃师实际接受21.0392/81.6816HP，满蓄力命中次数估算7/2；该数字是单次伤害换算，不是整场TTK，也不声称覆盖每种装备组合。另三精英分别10/3、8/2、13/3。结合16场景城市/矿场、击杀钩子、有限3600tick压力和以上活动生命周期，偃师整项标DONE、删除桌面与仓库对应剩余提示词。当前1DONE/33PARTIAL/60NOT_STARTED。古墓组合完整剩余提示词亦已删除，其他条目继续。


## 白面狐仙姑接入（2026-10-11）

沿用现有实体/攻击时钟/同步/生成预算。351镜光：20WINDUP→32ACTIVE移动光束→24RECOVERY→140COOLDOWN，速度.35格/tick、实际碰撞方块遮挡、每束一次命中；80tick原生15%减速和粉色边框，保留WASD。352狐火：20WINDUP→49ACTIVE→30RECOVERY→200COOLDOWN，锁定五个间距1.5的落点，实际释放20/32/44/56/68，各落点提前16tick粉色圆圈；半径1.25与视觉共用。353分身：接受至少12HP单次真实损失→6WINDUP→1ACTIVE→24RECOVERY→300COOLDOWN，最多两只1HP无伤害分身，ownerUUID+120tick绝对过期、死亡立即清理、分身不掉落/不计真实击杀进度；真身仅在已加载、清楚的侧向路线移动。

原创37骨骼/58方块、7动画、实际16×16四纯色资源；分段袍身/半面瓷面具/真实面具裂纹/骨扇/三条三节尾链，同一演员死亡袍落地及白狐逃逸。已有药庐夜间空庭入口，每据点一只，12000tick确认死亡冷却，卸载保留UUID；现有掉落注灵用途保留。build通过，原生regression28五项新行为测试已过、夜间生成测试失败（正在等待原生夜间光照缓存更新），整批未宣称PASS。单机/双人及活动生命周期/压力继续；总计1DONE/34PARTIAL/59NOT_STARTED。

金吾`local-20261011-jinwu-combat-solo24/network24`及各自`-resume`均PASS：实际关隘普通生成/正常AI三种自主释放、实际资源重载及TCP断线重连；新JVM首次实体tick保留UUID/原动作时钟/消耗帧/冷却和单次守卫台账。34种/48槽位压力在进行，整项仍待最后压力。断头将原生战斗24批次入口夹具误用StructureStart带地形缓冲的边界，实际锚点(-10,52,-10)在生产地板下方；已改用实际结构部件边界，未放宽正式生成条件；原无效运行保留FAIL。


2026-10-11 12:00 接续：披鳞执金吾完成并删提示词，当前2 DONE/33 PARTIAL/59 NOT_STARTED。原生单机与双客户端各16场景见jinwu-{solo,network}22；自主技能341/342/343、重载、实际TCP重连及原存档首次实体tick重启见jinwu-combat-{solo,network}24及-resume。34类型48槽位3600tick普通AI/物理压力solo25/network25通过，服务器平均tick采样上限3.23ms，最低观察FPS单机43/联机主105/客55；人工有限补员环境，不代表所有整合包/硬件/完整战斗TTK。青铜/白银真实接触伤害15.770554/74.8176，估算13/3次；215项原生全批回归22已通过。

原生221项回归30：220通过、木甲犬巡逻1失败；狐仙姑全部六项及第五个精英实际武器校准通过（青铜21.569595/白银83.7408，估算7/2次）。保留失败记录。修复测试隔离：巡逻等待实体区段真正tick并使用独立有限平地；盾牌用实际生存玩家与原版举盾/磨损/零伤害断言，独立场地避免前批Assassin攻击，未降低生产伤害断言。


2026-10-11 12:48 接续：隔离编译目录 `/tmp/dynasty-cod1-isolated41` 先准备并冻结 classpath 后再 build，构建通过，原生 222/222 全部通过（含真正普通 FlyingMoveControl 的狐仙姑半格悬停）；日志 `evidence/regression41-native-server.log.gz`。原生38整批221/221也通过。FoxHaze保留原生80tick减速和粉红边框；设计中的WASD反向与后文工程限制冲突，最终按工程限制保留正常控制，曾添加的输入反转类已删除，后续用新运行编号验证正常控制/到期恢复。

原生41：断头将单机/双客户端各15场景通过，正常AI三技能/资源重载/TCP真实重连通过，单机原存档首实体tick重启通过；双人重启卡在Forge握手并保留FAIL，后续完整新存档重跑，不计通过。九首鸟普通AI所有技能、资源重载、真实TCP重连、原存档首tick重启单机/双人均通过；旧双人动作检查在模型尚未烘焙时误启动，已补真实模型/地板等待。狐仙姑单机和双客户端各15动作/药庐入口通过；战斗被同遗迹士兵反击打死（实际失败存档Health=0、NoGravity=1），有限生命周期夹具后续在真实普通生成后隔离其他演员，保留主演员普通AI/物理/真实玩家攻击，不能将此夹具计为整个药庐混战平衡。35类型压力单机通过，双人Peer通过，Host在Peer正常退出后仍按2玩家门槛等待并继续累计3600tick以后的采样，误超上限；已停止完结后采样并提前处理完成握手，后续36类型重跑。

巨锤金甲力士6接入PARTIAL：361近距选择→28 WINDUP→33 ACTIVE（28/44/60三环）→36 RECOVERY→180 COOLDOWN；跳跃使脚底高于.9格免震，原生伤害类型绕过盾牌。362中距→18 WINDUP→49 ACTIVE（18/26/34/42/50/58六次）→40 RECOVERY→180 COOLDOWN；每tick物理推进.12格、WINDUP/ACTIVE抗击退，原生墙碰撞立即取消并STUN60tick。363远距5～12格→36 WINDUP→48 ACTIVE→30 RECOVERY→200 COOLDOWN；前摇累计真实损失10HP可打断，36释放最多一柄OwnerUUID+epoch铜锤，24tick外掷/24tick收回、每目标每段一次，墙阻挡提前回收、绝对48tick及卸载间隔清理、主人死亡立即清理。没有挖地形或瞬移。

当前6的实体/注册/客户端模型渲染/锁链、38骨骼68Cuboid七动画、实际16×16四纯色贴图、原生帝陵东庭坐标(32,1,24)、一次性守卫台账、三种已有功能掉落、真正击杀进度已接入；新六项原生GameTest和第六精英装备校准、36类型压力与客户端验收在进行，不能标DONE。当前2 DONE/34 PARTIAL/58 NOT_STARTED。

并行美术聊天已报告在独立boss-eight-art工作树升级断头将、偃师、金吾、狐仙姑、巨锤五套资源；本聊天停止重跑这些模型生成器，保留当前实际资源/骨骼/技能帧，后续同步按源SHA核对，再做原生截图验收。

### 2026-10-11 13:25 继续验收
第45轮原生服务器全部228项通过（非零测试）；第46轮 prepare/build 均 BUILD SUCCESSFUL，QA自动冻结启动classpath，/tmp与/private/tmp别名均映射独立快照。巨锤HP最终208；铜/银玩家原生接触伤害为10.932129/72.07199，对应20/3次（非整场TTK）。真实古墓守卫坐标从local x32调整为33，避免1.6宽碰撞体卡侧墙，原生第46轮单机15场景和实际结构生成通过；双人初始登录失败保留FAIL，未删整项提示词。

### 2026-10-11 13:27 蛊毒天蛛女与最新美术
原生48 prepare/build成功；冻结的24个八Boss资源SHA与美术74场景验收记录完全匹配。保留这些最新美术，不重跑旧五只精英生成器。天蛛女7已接入：现有矿坑西侧顶棚local(24,4,66)，父实体3×2、八足三节、胸腰分段、42骨骼56 Cuboid/7动画；原始16×16四色白边PNG。实际研究暮色森林Minoshroom模型源码的直立/横卧躯干衔接与承重动画（https://github.com/TeamTwilight/twilightforest/blob/latest/src/main/java/twilightforest/client/model/entity/MinoshroomModel.java）；查看灾变官方Ignis截图（https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png），没有复制资产。技能371：20前摇/100活动/30恢复/180冷却，真实顶棚条件，最多六个100tick酸池、1秒耐久损耗/减速II，可离开范围；372：12前摇/30活动/35恢复/120冷却，原生碰撞下落与半径2着地接触，可闪避；373：18前摇/1释放/40恢复/280冷却，地面条件，最多三个卵/幼蛛，60tick孵化、4HP卵可被原生玩家击碎、总260tick寿命、读档不补孵化、所有者死亡清除。三种掉落分别弓/皮甲材料和原生可食解毒。保持PARTIAL，实际单机/双人/矿场生成/重连重启及最终平衡未过。第48轮两项新测试通过、三项失败：测试NoAI不执行正常落体、蛋反制未使用原生玩家；改为正常AI和玩家真实青铜武器，下轮重验。36种48槽位3600ticks单机/真实双人第46轮全部通过。


## 2026-10-11 13:53 继续：九首鸟完成、天蛛女实机与新形态变更

- regression49实际原生服务器退出0，全部233 required通过；完整gzip日志已归档。记录了七精英实际青铜/白银原生接触伤害，天蛛女20.077194/79.70039（估算9/3次，非实战TTK）。
- 九首鸟当前v2资源：Native41真实战场夜间入口、三技能普通AI、资源重载、实际TCP断开/重连、原存档第一原生实体tick重启，单机/联机与两者resume全部PASS且无FAIL；Native50最新各13场景包括age40死亡羽毛，截图实际已查看，36种48槽3600tick单机/双人压力46通过。整项DONE，已删除外部原文件整段并镜像仓库。
- 真实美术聊天最新直接用户指令否定了8套人形资源，要求更大独立形态。并行任务正在重做；保留资源编辑权，不运行五只旧精英生成器。此前偃师/执金吾功能完成仍有效，整项状态回PARTIAL，仅新形态/碰撞绑定/最新实机验证待续，不重做技能任务掉落。当前1 DONE/36 PARTIAL/57 NOT_STARTED。
- Native48断头将单机/真实双客户端各15姿态及普通AI生命周期、资源重载/真实TCP/原存档重启均PASS；等待新形态资源。Native50狐母修正原生攻击站位后单机真实重击与原存档重启PASS；双客户端初始Forge握手超时，须新ID重试。巨锤普通AI单机/联机通过，联机原存档重启初始登录超时；姿态检查须对应当前双膝跪地而非旧root下沉7像素。
- 天蛛女Native50前11个姿态实机通过（贴顶根旋转、真实坠落、3虫卵），hurt场景因为普通AI受伤反击改变动作身份而失败，控制展示夹具只对hurt禁AI，实际生命周期继续普通AI。实机查看后腹部改为3层大甲壳、腿根扇形、加2×2眼及发束，42骨62cuboids/16×16四色；运行时52待复验。
- regression50加入重击中断测试后遭测试框架GameTestInfo fastutil迭代器异常（回调内追加计时任务）；已把虫卵任务改为开场一次安排。相邻批次盾牌/冲击圈夹具不稳定已加真实持久化/隔离场地和本机块tick就绪等待，不放宽伤害/跳跃规避断言；52准备中。


2026-10-11 14:08 用户直接要求：正在考试，先不要运行Java测试。本任务已停止自己的原生Java客户端和测试协调器；后续只改本地代码/资源、静态验证，须用户明确恢复Java测试才可启动。原生53天蛛女普通战斗夹具错误地把矿坑gallery底层当localY1；真实Blueprint.hollowBox仅墙面，地板在localY0，已修正readiness为feet.below(4)、玩家地面高度feetY-3。54 prepare已成功且冻结，尚未运行其服务器或客户端，不宣称235通过。


## 2026-10-11 考试期间续作：Java测试暂停，炼丹方士8已写入待验收

用户直接要求“我在考试先不要运行java测试”。已停止本任务原生53协调器与其两只Java客户端（停止前逐个验证所属PID/QA运行ID），没有操作别的聊天的Java进程。此后没有启动Gradle、build、Java服务器或游戏窗口；考试期间只进行了源码/资源修改、Python静态资源检查。暂停不因经过一段时间而自动恢复，须用户明确允许。53双人战斗目录保留DO_NOT_RUN，临时原生runner也已拒绝复用PASS/FAIL/DO_NOT_RUN目录。

暂停之前regression52已经实际退出0并全部234 required通过，gzip完整日志在evidence/regression52-native-server.log.gz。53天蛛女单机/双人各14受控动作通过，但第15真实矿坑入口失败；普通战斗单机没有进入ready，双人由用户暂停而中断，不能记PASS。生产bindEncounter已按真实支撑面即时初始化贴顶与重力；战斗QA原矿坑地面已改为markerY-3、地板marker.below(4)。这些修正尚未运行。54准备成功但冻结发生在QA地面修正和本次炼丹方士之前；后续恢复必须使用新编号、最新源码重新prepare并冻结，不能拿54证明当前代码通过。新增顶棚生成测试也尚未运行。

炼丹方士8新增Alchemist、AlchemistOrb、AlchemistZone、独立Geo渲染器，注册实体/刷怪蛋/属性。三技能：381有16tick前摇与两条反相螺旋实体弹道，原生墙碰撞/最近敌人碰撞、半径2伤害/火或缓慢/饱和度消耗，40tick绝对飞行寿命；382有24tick前摇、半径5的160tick原生火海区域，每20tick有限敌人伤害且不改方块；383有22tick前摇，吞服的一枚给200tick反伤外壳，另两枚实际抛物线实体金丹落地后生成半径2.5/120tick汞雾。每个所有者至多两个飞行弹与三个区域，宿主死亡/失效/超过范围清理；missed tick不补飞行接触。重击前摇可打断、保留冷却；反伤只基于已接受敌人伤害，过滤THORNS、每攻击者20tick且最多16记录，UUID/原绝对护壳截止时间/反伤冷却随NBT保存。普通导航保留实体碰撞与32格药棚归巢，不传送追玩家。

入口复用现有herbal_retreat的露天丹棚，TravelSitePiece只加local(25,1,10)落点方法，没有更改建筑；EliteEncounters增加真实tag及SavedData单槽，死亡后12000tick再生，卸载保留UUID，共享每次扫描生成预算仍为2。白天炼丹方士分支先于夜间狐母分支，避免被狐母day检查吞掉。三种原生战利品裂纹丹炉铜片/阴阳火灰/凝汞丹珠接入已有淬炼词条xuanwu_shell/cinnabar/poison_ward；新增既有minecraft:player_killed_entity击杀进度。三词条按现有冲突/冷却/成本执行，没有另造淬炼系统。

实际阅读暮色森林LichModel完整源码：https://raw.githubusercontent.com/TeamTwilight/twilightforest/latest/src/main/java/twilightforest/client/model/entity/LichModel.java 。只借鉴宽领幕扩大施法者轮廓；全部体块/UV/骨架/动作原创。炼丹方士为35骨骼、63长方体、7动画：分片中空袍体与连续后袍摆、非直棍弯肘宽袖、破莲花冠、偏置独立三足中空丹炉、错落拂尘；idle/walk/helix/sea/pells/hurt/death与服务端时间轴绑定。实际16×16PNG、白色加三纯色、一像素白边、6×6色岛/4×4重复面UV；3物品图标同样遵守四色/白边/至少2×2色区。独立法球4骨/5Cuboid/1clip共享四色纹理，不可见分支按synched pill/side隐藏。死亡炉脚飞散/袍体消失、两色火与碎铜有固定80tick有限表现，late-track同步原绝对时间。

已完成Python静态检查：JSON无重复key、父骨存在/无循环、动画骨引用存在、关键帧不越clip时长、逐面UV整像素且不越16、四张实际16×16PNG均≤4色/白边/每个色点隶属至少2×2色区；generator语法通过，git diff --check通过。五视图为近似骨变换静态预览，见evidence/alchemist-static-fiveviews-20261011.png，实际看过后补后袍摆和拂尘朝向/错落流苏，不能代替游戏截图。直接读取本机当前Forge映射source.jar核对接口，发现EntityRenderer.getPackedLightCoords为final，已改为getBlockLightLevel发光覆写；没有运行Java工具。6项AlchemistGameTests及8精英真实武器校准代码已准备，全部尚未编译/执行，不能记通过。

当前1 DONE /37 PARTIAL /56 NOT_STARTED。炼丹方士PARTIAL且明确新源代码未构建。外部cod1原文先备份到build/blueprint-client/prompt-backups/cod1-before-alchemist-partial-20261011.txt，再补进展与考试暂停记录，保留整个第8设计；仓库cod1镜像和README已同步。原有world-placement两行过时的天蛛女/炼丹方士PROPOSED字段已按实际绑定修正。九首鸟已完成提示词删除不回写；其他待验收任务提示词不删除。并行美术的8套大形态编辑权继续保留，没有重跑它们的旧生成器。


## 2026-10-11 夜间续作：炼丹方士器物主体重构

按新版建模要求和用户“人形自然或明确非人结构”的直接指令，炼丹方士原穿袍人体已改成丹炉承载残魂：真实炉壁/开口/内核、三足支撑、嵌入式面具、后轴炉盖、侧轴→连杆→卡箍→拂尘，布幕从后炉沿绑带垂落。源为tools/blueprint/generate_alchemist.py；37骨/68Cuboid/七原有动画名，数目只记录成本。实际参考暮色森林DeathTomeModel源码的器物自身与铰接作用部关系，不复制资产。16×16四纯色PNG色岛重新安排成2像素白边，逐点2×2色区和面UV检查通过。

同尺度前/后/左右/45度/灰模和黑剪影、七段动作PNG均来自当前导出资源真实逐面PNG，见evidence/alchemist-ding-v2。自查修正拂尘流苏穿地、死亡足角穿地、金丹被炉盖遮住；七段各81帧取样地面最小Y均0，走动至少两足接地，循环接缝（含法球360度等价闭合）通过。主体1.75宽×1.75高×1.0625长，完整静止2.1861宽×2.0625高×1.375长，最大动作高度2.3157m/水平半径1.8196m。测量为源码/软件值。当前父碰撞1.6×2m和导航保留；必要挂点适配将发射源移至脚底+1.5m/朝前.55m炉口，Renderer补有限4.4×4.4×3m裁剪箱；读取当前1.20.1映射源码与Gecko4.8.4实际class方法表核对可覆写接口，没有运行Java工具。

用户晚间睡觉要求：不启声音、不调亮度，愚者存档用后不要关闭。只读确认其愚者chishi实例正在运行，本地模组含Cataclysm3.16、TwilightForest4.3.2508、Goety2.5.36.1；窗口工具无法绑定这个独立Java窗口，未声称看到实机怪物，未操作或关闭游戏。既有考试期间Java测试暂停仍保留，没有启动Gradle、服务器或新客户端。炼丹方士构建/实机仍PENDING，原提示词只更新真实进度并保留全文，当前1 DONE/37 PARTIAL/56 NOT_STARTED。


## 2026-10-11 巡海夜叉9接续（源码与软件，未实机验收）

> 本地进度（2026-10-11）：已写入独立低伏甲壳主体、六足承重、三节尾针和真实连接叉钳，原2.4米穿甲双手人形描述只保留靛青、铜眼、獠牙和钢叉身份元素，形态以新版建模要求为准。三技能沿用原服务端攻击时钟：18 tick双水柱前摇、30 tick潜渊（前20 tick跟踪、末10 tick锁圈、仅一次合法落点）、三段各2格实际碰撞冲刺；已接入原版冷/暖海底遗迹、共享2只生成预算/64引用上限、同结构UUID名额与12000 tick死亡冷却。三种功能掉落、击杀进度、7段动画、3米限时水柱和源码回归用例已写入。正背/双侧/45度/灰模/剪影、主体握持细节和全部动作软件自查通过，并修正了重叠面、遮挡及读档问题。Java构建、普通实战、单机/双人、真实结构入口、重载/重连/重启、压力与装备数值验收仍待完成；当前PARTIAL，整项提示词保留，不能将软件图当游戏截图。遵守考试期间暂停Java、睡觉期间不改音量亮度且不关闭愚者存档的要求。

- 最新汇总：**1 DONE / 38 PARTIAL / 55 NOT_STARTED**。未删第9项整段，后续第10～15精英、12 Boss、25神器、12神影继续待实施。
- 源形态：`tools/blueprint/generate_tide_yasha.py`；42骨骼/73cuboids/7clips，水柱另18骨骼/25cuboids/1spin。无人体颈、胸腰或人类双臂；宽甲壳本身为主体，六足与叉钳真实连接。参照作者Cataclysm Amethyst Crab实际构造代码，未复制资源。
- 四层尺寸见 `content-definitions.json` 与 `evidence/tide-yasha-v1/software-sampling.json`：主体含支撑3.0×1.4375×2.3392m，包含叉/尾完整可见3.125×1.4375×5.125m；新物理2.8×1.8m；三米水柱/2m圈/2.8m叉路分别记录；有限客户端裁剪6.2×3.4m。
- 潜渊第9～29tick模型隐去、伤害碰撞保留，水圈前20tick跟踪、末10tick锁点；30tick只允许一次距离/高度/区块/实际碰撞/视线通过的侧向落点。动作不能用瞬移循环追人；出水无合法落点则30tick硬直且不退冷却。是否所有视觉与服务器时钟一致须实机。
- 水柱原生实体只维持40tick，偏向两侧各10°、每目标每柱一次、最多16命中UUID；检查完整柱体扫掠与实际遮挡，不把主人当障碍，死亡/重载时间跳变清理。三连挑每段10tick×0.2m，普通move碰墙硬直；第三段真实跳跃与原生重力，不只抬动画。
- 原版warm/cold ocean ruin通过已有loaded结构引用读取，25个水平候选×最多15层，无强制区块加载；共享2只预算/64结构引用，UUID卸载保留，确认死亡后原12000tick冷却。没有创建新海底建筑或替换旧最终Boss。
- 掉落甲片+2铁+皮革合盾，净潮精粹沿用200tick水肺/缓降食用，3叉齿+2木棍合原版钢叉，配方数值尚待原生平衡。已有native kill advancement；不重新生成其他线程正在制作的任务书。
- `TideYashaGameTests`六项源用例覆盖真实列体、中心避让、遮挡落点、三段真实冲刺/跳跃、重击/冷却读档和水下名额；`EliteBalanceGameTests`增加第九只。**源文件写好不等于用例通过，全部未运行。**
- 复查修正：叉钳/脚盖共面重叠、钢叉连接，水柱改为连续双螺旋而非漂浮方环、原先方块挡住尾针、预览参照人物没有地面；最终重做实际同尺度地面视图并复看。death先叉插地、海水外渗、白色矿壳替换、碎块散去，80tick只结算一次掉落。
- 软件重现（需Python numpy/PIL，不启动Java）：`tools/blueprint/review_tide_yasha.py` 后 `tools/blueprint/validate_tide_yasha.py`。软件图明确标记非游戏截图。
- 下一原生验证须用户明确恢复Java后重新构建当前源；不能拿regression52、prepare54或旧modpack JAR当第8/9项成功证据。
- 愚者现有Java存档仅只读检查本地资源；窗口工具不能绑定其独立Java窗口，未冒称看到实战。未操作音量/亮度，也未结束其进程。


## 2026-10-11 搬山尸狂10接续（源码和软件，原生未运行）

> 本地进度（2026-10-11）：已写入独立四足棺壳尸怪，真实中空腹腔、双铰接血门、前拳铁枷与三节连接链、三把有插座的背部残兵；不使用人的头颈胸腰结构。原2.7米保留为物理高度，主体含四足4.0×2.75×3.1875米，残兵最高3.4248米，有限裁剪6.8×5.5米，具体四层尺寸见仓库。401保留22 tick前摇/80 tick旋转平移/40 tick反打窗口；402保留14 tick前摇、20 tick真实碰撞弧线飞跃8格、落地半径3格，浅坑只破坏一层允许方块并遵守生物破坏/Forge否决，容器矿石不破坏；403保留16 tick前摇/固定朝向腹腔血流、5秒原生护甲腐蚀与有限耐久损耗。已接入现有帝陵新版开阔陵室东侧、持久化UUID名额及12000 tick死亡冷却，三种有用途的掉落和击杀进度。七段动作×81帧软件采样与正背/双侧/45度/灰模/剪影/细节自查通过，修正前拳穿地、关节共面和预警范围；八项原生回归源码及第十只装备对比用例已写好但未执行。Java构建、实战、单机/双人、真实入口、重载/重连/重启、压力和平衡均待验收，当前PARTIAL，整项提示词保留。仍遵守暂停Java、不改音量亮度、不关闭愚者存档。

- 当前94项：**1 DONE / 39 PARTIAL / 54 NOT_STARTED**。没有删除第10项整段。后续11～15精英、12Boss、25神器、12神影待实施。
- 原创棺壳是主体、前拳+后足四处支撑、腹腔血门是攻击源。36骨骼/101cuboids/7clips；来源生成器及实际资源路径已写入原目录。参照Goety GraveGolem实际作者构造，不声称参考本身为四足，不复制资源。
- 软件全部视图和七段动作已经复看；改正前拳旋转边角穿地、前后肢关节共面抖动、背部刀片共面和血流预警比判定少1.2m的问题。七段×81采样有限边界、接地、循环、16px四色/2px边距/最小2x2色区与整数UV通过；这不是游戏截图或原生PASS。
- Native回归源为`RageCorpseGameTests`八项：完整旋转时间轴、真实8m20步飞扑、动态墙体+重力恢复、重击/卸载不重播、固定锥路/遮挡/腐蚀到期、真实护甲磨损、受规则保护的一层浅坑、陵室单UUID名额/死亡冷却。`EliteBalanceGameTests`新增第十只并扩大夹具地板，让宽体不重叠且所有行在地板内。全部未运行。
- source接口已按当前Forge47.4.10核对；只有重恢复后重新构建当前工作区才能验收Java。旧regression52/prepare54/JAR不证明8～10新内容。
- 帝陵点避开封闭陪葬室，使用原开阔室东侧，空间匹配8m飞扑；不移旧Boss、不造新建筑。浅坑依用户技能设定可能改变原允许地板，但只一层/29格以内，容器矿石与自定义方块保护。真实入口和死亡后的可重生地形仍须验收。
- 静态重现：Python `tools/blueprint/review_rage_corpse.py` 后 `tools/blueprint/validate_rage_corpse.py`；飞扑图是同源点的肢体姿态，真实2m高8m远弧线属于服务器物理，未用软件图冒称已观察原生飞行。


## 2026-10-12 墨家绝影11接续（源码和软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创低伏折帛墨鳐机关：横向墨匣核心、两片真实铰接折翼、沿短轨收拢的双反握匕首、腹下两根接地竹橇及两段帛尾，不使用人形头胸腰、双臂双腿。原1.75米穿甲人体仅保留黑白玄水甲、墨滴与双刃身份意象，主体含折翼2.5×0.875×1.625米，完整可见2.5×0.875×2.5米；物理1.4×0.8米与有限4.8×2.0米裁剪分开记录。411隐形最多4秒，保留碰撞与受击，墨迹末10tick锁点，只允许一次已加载、地面/碰撞/视线合法的背后1格显形，转身取消三倍背刺；412四根真实可横扫标枪、10tick前摇及四次实际对角穿斩，破任意标枪服务器中断、保留冷却并清理余枪；413真实后撤、至多3枚可见墨丸、20tick延迟、有限墨雾与5秒原版失明，不增加纯黑全屏遮罩。驱雾墨竹可用一秒吹散6格/60度内至多三云。已接入现有天工城中殿内库廊道、同结构UUID名额/12000tick死亡冷却、三种有实际用途的掉落与击杀进度。七动画×81帧及标枪/墨丸软件自查通过，修正短刃支架共面与死亡墨纹裁剪范围；七项原生回归源码和第十一只装备对比已写好。当前构建、单机/双人、实战、真实入口、重载/重连/重启、压力和平衡尚未验收，PARTIAL，整段保留。继续暂停Java，不改声音亮度，不关闭愚者存档。

- 当前94项：**1 DONE / 40 PARTIAL / 53 NOT_STARTED**。没有删第11整段。尚未实施12～15精英、12Boss、25神器、12神影；其他PARTIAL的旧实机证据不自动覆盖新模型与最新代码。
- 可编辑源`tools/blueprint/generate_ink_assassin.py`导出19骨骼/41cuboids/7clips原创非人形机关墨鳐；1骨骼/4cuboids墨竹标枪、1骨骼/3cuboids真实墨丸共享四色16px纯色岛。标枪是零XP/无掉落活体，不是无法横扫的普通Entity假靶点；最多四根，真实伤害即取消同owner同epoch领域。
- 时间轴：411隐形1..79且普通受击保留，前70tick实体寻路和可见地面墨迹，末10锁点，80tick一次合法背后1m显形，玩家转向使3倍变为普通伤害；412前摇10，实际四次对角穿行，15/27/39/51tick四次有限圆判定，56tick标枪到期，恢复36tick；413连续六次0.16m真实后撤，8tick放至多3枚实物墨丸，20tick后化云，绝对100tick云寿命，原版失明100tick。
- 驱雾墨竹UseAnim.TOOT_HORN与20tick使用、6m/60度视线锥、最多三云、消耗1/40tick冷却均接入；源遵守无声执行，本轮没有播放音频。保留原版有限失明，不增加全黑遮罩或改WASD。
- 世界入口仅复用天工新版中殿现有内库廊道点，沿用mechanist_sites、全局2预算/64引用、单结构UUID、卸载名额和12000tick确认死亡冷却。旧机关城/矿业/主线/Boss位置不重建。来源现有城市几何代码确认；真实自然进场未验收。
- 两竹橇始终接地，所有七clip各81软件采样通过；已实际复看六向/灰模/剪影、握持细节、全部clips、独立标枪与墨丸。修正刀轨共面抖动、刀刃与主体重叠、上下翼转向、死亡墨纹实际Z包围超过初始裁剪等问题。新版有限4.8x2.0m裁剪覆盖源采样；这不是游戏截图。
- 七项`InkAssassinGameTests`原生源覆盖实际三倍背击/转身反制、新墙取消/可见性恢复、四次真实移动接触、原生玩家剑击附近牛的横扫命中标枪、三丸整20tick引信+真物品驱雾、原版有限失明到期、UUID卸载/时间跳变/死亡冷却。`EliteBalanceGameTests`增加第十一只。全部NOT_RUN，未用手写模拟值冒称Native PASS。
- 最终Java/客户端加载、普通导航/背刺/盾挡、真实入口/多人点名隔离、活动重连/重载/重启、压力与装备平衡待用户明确恢复Java后重建再验。不能沿用52/54冻结目录或他人打包JAR证明8～11已验收。
- Python重现：`tools/blueprint/review_ink_assassin.py`然后`tools/blueprint/validate_ink_assassin.py`；仇恨消失与渲染隐藏为源码适配待原生，不把源姿态图当隐形客户端截图。


2026-10-12动作复查补充：搬山尸狂喷血前双拳现抬至腹门，前视实际导出已复看，重新采样七段81帧/段通过源码软件检查。绝影刺客改为低伏双刃从下盘背击，不沿用旧人形颈部挂点，保留背向三倍和转身反制；该外形挂点适配待原生实战检查。两项保留PARTIAL和整段提示词。


## 2026-10-12 铜甲巨猿12接续（源码和软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创浇铜巨猿：前重胸背、向前伸出的猿类口鼻、长而厚的分段前臂巨拳、短后腿四足承重、真实握持的断裂铜桩；不套人体或其他四足模型。实际四足3.625×2.2×3.625米，直立擂胸最高3.3841米；固定物理3.8×3.4米留足直立头部空间，有限裁剪8×6米单独记录。421为24tick直立擂胸前摇、64个真实碰撞步共8格、八次宽2格正面捶打与42tick反打窗口，单击最多破坏一格一层允许地面，遵守生物破坏和Forge否决，容器矿石不毁；422为18tick扣地/真实双手举石、发一枚锁定前摇起点瞄准的1.5米重力岩石，碰撞至多裂成三块不能继续分裂的碎石；423为12tick前摇、24步真实弧线飞扑最远12米/峰高3米、半径4米落地，末6tick红圈指向同一真实落点。巨猿会整身直立后前栽，胸甲开裂，90tick死亡并只结算一次掉落。接入古代废墟次选场景的现有古战场西侧空地10,4,13，保留结构UUID名额与12000tick死亡冷却，不新造建筑；高山/巨人庭院主选入口仍待后续补齐。铜片可回收青铜锭，岩碎可拼石，击杀进度已接入。七动画各81帧、巨石/碎石各81帧和全部多视角软件自查通过，修正肩/前臂/口鼻共面与举石握持，十项原生回归源码和第十二只装备对比已写好。Java构建、单机/双人实战、自然入口、生命周期、压力和平衡待验收，PARTIAL，整项保留。继续暂停Java，不改声音亮度，不关闭愚者存档。

- 当前94项：**1 DONE / 41 PARTIAL / 52 NOT_STARTED**。本轮没有新增整项提示词删除。13～15精英、12Boss、25神器、12神影尚未接入；30基础与8～12等当前PARTIAL不会借用52/54旧证据冒称已验收。
- 可编辑源`tools/blueprint/generate_bronze_gorilla.py`，`review_bronze_gorilla.py`，`validate_bronze_gorilla.py`。用本机已配置含NumPy/Pillow的bundledPython执行；系统Python不保证NumPy。主模型24骨骼/65cuboids，投石与碎石各1骨骼2cuboids，均原创16px四色/2px白边/整数UV。实际同尺度六向/灰模/剪影/主体细节、七clips和双投射物均已复看。
- 三技能时间轴：421(24/64/42/240CD)24..87每tick实际0.125m推进，24/32/40/48/56/64/72/80八次窄正面捶击，保持朝向不可追转；422(18/20/30/200CD)18释放至多一石，锁定前摇起点瞄准且后续不追踪，落地/墙/首个有效接触最多三碎片；423(12/24/42/260CD)12..35真实碰撞弧线，距离<=12m、峰高3m、35tick落地半径4m，30..35同一落点红圈，障碍取消40stun，所有动作的已花冷却保留。
- 只破坏最多一格一层自然/古战场指定方块，容器/矿石/自定义建筑方块不可毁；生物破坏开关与Forge否决生效。保留真重力，未设置NoPhysics/NoGravity，最后落地由真实碰撞/Floor判定，不是动画假跳。
- 世界复用现有古战场开阔西翼，不新增建筑或迁移Boss/NPC；当前属于规划中的古代重型遗迹次选场景，高山/巨人庭院主选入口尚未接入，明确留作未完成项。全局2预算/64引用、单结构UUID保留、确认死亡12000tick冷却和原存档身份保留。
- 十项原生回归源覆盖完整24tick前摇/8m移动/2m范围/42tick反打、锁向墙障、24步真实扑杀/真重力与新墙取消、真实投石和恰好三枚不可递归碎片、有限寿命/主人死亡清理、重击打断、活动存档时间跳变、入口UUID/死亡冷却、一层坑/容器矿石保护。破坏开关需要true的用例使用独立batch，避免并行修改同一world规则。第十二只装备对比已接入。所有Java/原生用例均未运行，没有编译通过结论。
- 用户未恢复Java：不能删除第12整段，当前jar与游戏画面未验收。后续需全新当前构建、单机与双人、真实普通导航和投石/盾挡/红圈、入口/重载/重连/重启、压力与青铜/白银平衡，并补主选入口。愚者实例、音量与亮度保持用户状态。

2026-10-12巨猿入口补充：高山主选已用现有原版高山废弃传送门周边接入（实际原版1.20.1数据资源已查看）。只扫描已加载9列×最多24层，IS_MOUNTAIN、海拔>=96、5×5同高实心地面、无液体、完整3.8×3.4m站立盒/世界边界/6..48m玩家距离检查；不改地形或强加载。古战场次选入口保留。上面“主选待补”是接续历史，当前缺口转为新构建的两个真实入口验收。仍PARTIAL、暂停Java、提示词保留。


## 2026-10-12 青灯判官13接续（源码与软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创活化铁册与滑行墨盂：书脊、双册页铰链、嵌入独眼、紫色封皮/封条、青灯、真实轴接笔架和分段判官笔为主体，无人体骨架。主体约2.19×2.2×1.39米，完整待机约2.6244×2.2×2.75米，物理2.4×2.2米、主模型有限裁剪6.6×4.4米和三法术范围分别记录。431点名40tick/三次12、24、36闪烁，36锁点，40释放一枚真实下落巨笔，仅笔尖造成原生魔法伤害，第三闪后能侧移躲避、屋顶能挡，刺空会短暂无伤插地后到期清理；432为10tick前摇和10/18/26/34/42五道真实墨痕，每道最多16次不同UUID接触/80tick寿命，墙前同步截断模型与伤害；433为16tick前摇、四柱一服务器实体组成直径6格牢笼，最多八名现有生存玩家、160tick限时，原生同维度位置限制保持当前视角，判官有效背击立即破笼并保留冷却，无安全纠正位置时解笼。重击打断、有限目标距离/区块/时间跳变取消、死亡清理/84tick仅一次掉落均写入；死亡含六组折页蝴蝶、真实断笔、墨盂消散。复用冥界现有新版封印遗迹外厅朝向和入口，确认死亡12000tick冷却，卸载保留UUID名额，不新造建筑/强加载/替换最终Boss。铁页回收六铁粒、封墨换两黑染料、原生击杀进度已接。七动作各81帧和全部多视角/三法术软件检查通过，九项原生回归和第十三只装备对比源码未运行，Java构建/单机双人/真正自然入口/生命周期/压力/平衡待验收，PARTIAL，整项保留。保持暂停Java、不操作声音亮度、不关闭愚者存档。

- 当前94项：**1 DONE / 42 PARTIAL / 51 NOT_STARTED**，没有新增整项提示词删除。精英14～15、12Boss、25神器、12神影仍未接入；所有PARTIAL均保留原生验收缺口。
- 可编辑权威源`tools/blueprint/generate_lamp_judge.py`、`review_lamp_judge.py`、`validate_lamp_judge.py`；33骨骼/66cuboids，七clip；三法术分别1骨骼/4、2、52cuboids，四柱与32固定链接无需37个空更新骨骼，已合并为一个静态root。实际16px四色/2px白边/整数逐面UV；待机及判官笔、合册、侧背、死亡、独立落笔/墨痕/牢笼均已软件复看。曾发现笔架/书脊/独眼共面与墨瓶一像素色边，已针对接触面/色区修正。
- 431(40/12/40/260CD)：前三闪12/24/36由同步标记渲染，35tick结束追踪，36锁定，40真实巨笔出生，30tick最大寿命/.7m每tick下落，只笔尖.3m半径造成1.8×7原生indirectMagic；实体全身墙障/屋顶能挡。原文无界距离适配为初选28m、同维度已加载追踪<=64m，避免强加载远区块，并在元数据声明。
- 432(10/40/34/220CD)：五次10/18/26/34/42对应五笔旋转和实测笔尖挂点；实际墨痕长<=5.5m宽.5m/80tick，每道最多16个不同UUID/局部查询16，固体墙使模型根骨缩放及同一命中线截断；每victim一次，不每tick刷伤害。所有法术总数<=7。
- 433(16/160/36/300CD)：完整7×7局部碰撞空间/地面检查，四柱直径6m原生擂台，最多8个形成时存在的生存玩家，160tick寿命。真实服务端同维度位置纠正保留视角，中心留玩家身体裕量2.6m，不能穿墙/水/未加载区块；目的地及上个安全点都失效时解笼而非持续纠错。有效背面伤害触发35tick硬直和解笼，已花冷却不退。普通AI可走向圈心而不冻结导航；创模式/旁观者不困，离开维度/死亡不跨维度拉回。
- 已接入当前>=3版封印遗迹外厅offset0,10，使用相同朝向哈希。只在冥界已加载的合法开放地面出现；至多6个垂直候选、全局2预算/64引用、结构UUID保留、死亡12000tick；不改解谜构造/容器/Boss/NPC。死亡和destroy移除使用实体所在维度的SavedData，确保冥界名额真正释放，原主世界行为保持。
- 九个原生GameTest源码覆盖40tick完整前摇/真实落笔、第三闪侧移避开、后建屋顶、恰好五墨痕/死亡清理、墙截断与UUID一次伤害/80寿命、两个真实ServerPlayer困圈与160到期、有效背击/保留冷却、卸载时间跳变与非有限NBT、障碍拒圈/重击打断；第十三只青铜/白银对比已加入并扩展隔离场地。全部均未运行，分隔符检查不构成编译证明。
- 后续待当前独立构建/单人及双人真实普通AI、法术与盾牌、囚笼边界台阶/斜坡/屋顶/背击、真实自然冥界入口与原存档、重载/重连/重启/卸载、性能和装备平衡。用户未恢复Java，不能删除第13整段；不借旧52/54构建和服务器数据冒充。

- 最终方向复查：实际阅读Gecko1.20.1 `GeoEntityRenderer`源码，发现非Living的法术默认不读实体偏航。已在判官SpellRenderer明确传同步偏航，确保墨痕模型与服务端方向/墙截断/裁剪段一致；主笔架右侧挂点也按实际Geo轴翻转修正为side系数-1.25。软件尺寸采样仍不是原生渲染通过。


## 2026-10-12 烈风金雕14接续（源码与软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创完整猛禽主体：钩喙、厚胸背、分节主翼/外翼与阶梯大飞羽、双关节跗腿、两爪真实握弓/拉弦，不使用人的头胸腰和双臂双腿；主体含羽翼/爪5.7572×1.8931×4.3125米，完整待机含骨弓约5.7572×2.5875×4.3125米，物理核心2.2×2.8米和有限8×7米裁剪分开。地面上方4米真实飞行有碰撞/有限已加载探地，落地硬直/死亡恢复重力；441保持30tick拉弓，真实向上45度光矢到达同一锁定圈天顶后分裂24支下落箭、半径4米，实体墙/屋顶可挡，原生持盾抬头可招架并消耗1耐久；442保持12tick真正前合翼、36支实体硬羽/180度/16米上限，正常护甲管线及命中后有限护甲耐久损耗；443保持16tick自转前摇、16步真实碰撞俯冲/半径2米落地，29～31tick受有效重击触发100tick落地反打窗口。箭总数至多80，光矢30tick/其他60tick寿命，死亡/中断/卸载时间跳变清理。死亡包含原生重力倒栽、失色羽翼、真实断弦、有限灰翎/金砂与84tick完全消散、90tick一次移除结算。已接原版雪山高峰前哨周边现有地面入口、结构UUID名额/12000tick死亡冷却、硬翎制八箭/骨弓片制骨粉与击杀进度；只查已加载8列×24层、不新造神殿、不改最终Boss。七动作各81帧、正背双侧/45度/灰模/剪影、弦爪挂点与独立羽箭软件复查通过，修正腿旋转符号、拉弦中间帧脱节、共面重叠和死亡朝向。八项原生回归源码及第十四只装备对比均未运行；构建、单机/双人实战、自然入口、生命周期、压力和平衡仍待验收，PARTIAL，整项保留。继续暂停Java、不动声音亮度、不关闭愚者存档。

- 当前94项：**1 DONE / 43 PARTIAL / 50 NOT_STARTED**。没有新增整项删除。第15精英、12Boss、25神器、12神影待接；全部PARTIAL保持原生验收缺口。
- 权威可编辑源为`generate_golden_eagle.py`，软件查看为`review_golden_eagle.py`，实际PNG/逐面UV/环缝/边界/腿跗与弦尾连接检查为`validate_golden_eagle.py`。主模型23骨骼/70cuboids、7clips，原生羽箭1骨骼/3cuboids。弓拉弦0/25/50/75/100%与释放恢复已查看，实际跗端/爪和弦中段误差<=约1.3毫米（密集关键帧线性采样），不是动画资源数代替握持检查。
- 身体包含双翼/双爪实际5.7572×1.8931×4.3125m，完整待机含骨弓5.7572×2.5875×4.3125m；物理核心2.2×2.8m保证地面俯冲恢复的主体空间，羽翼不是伤害方盒。有限裁剪8×7m/Y[-1.8,5.2]；所有姿态源采样与灰模/正背左右/45度/剪影/详情均已查看。死亡朝向已修成喙先向下，死亡/俯冲局部落地姿态按实际所有顶点修正，84tick零面积/90tick服务端消失；真正4m下坠仍由原生重力负责，软件图不证明实机下坠。
- 441(30/50/36/240CD)真实双爪向上45度拉弓、满拉10u。弓尖实际(13,10,-27+10)，弓握点(13,10,-12)，方向和发射点使用同一45度；生成一支光矢向固定天顶、抵达一次分裂24支箭，天顶XY投影与同步地面半径4m圈相同。目标距离3..16m，天顶高度由真实45度抛射线决定，没有穿屋顶瞬移箭。原生箭墙碰撞、60tick期限，玩家实际持盾/看上方可阻挡下落接触并消耗1耐久。
- 442(12/20/40/240CD)翼根+外翼前合护胸再真实展开，在测得腕点左右各发18支、前180度共36支实体硬羽。硬羽<=16m/60tick，使用正常原生箭伤与护甲，成功伤害后各已有护甲槽2耐久，创模式免扣；没有把破甲解释为绕过原生伤害。
- 443(16/16/100/300CD)前摇自转720度、16步实际有碰撞俯冲至同一合法地面点；31tick半径2m/1.5×7/原生击退。29..31tick接受实际>=8重击则中断并恢复重力/100tick落地硬直；之前前摇重击30tick，撞墙40tick，冷却不返。自然AI使用原生飞行导航与move control，读取有限9层地面、地面上4m悬浮、活动范围32m、全途实体碰撞；没有noPhysics和强加载。
- 入口只复用原版前哨山侧现有空地：冻结/尖峭/裸岩山峰或雪坡、Y>=100；8列×最多24层、3×3实心/无水地面、完整6×6×7m空场、玩家6..48m；共享2生成预算/64引用、单结构UUID、死亡12000tick且卸载仍保留名额。原文候选悬崖神殿没有可复用当前结构，因此没有编造次入口或新造建筑。
- 八个原生回归源码覆盖完整30tick/真实光矢/恰好24箭、屋顶挡光矢和箭雨、完整12tick/36实体/到期、后建墙挡俯冲、29tick重击100硬直与保留冷却、实际ServerPlayer抬盾/1耐久、保存时间跳变/非有限落点取消、真实生成UUID名额与死亡90/12000。全部未运行；第十四只青铜/白银装备样本源已加入。随后须当前独立构建与单/双人普通AI/实战，真实山地自然入口/地形低顶与盾牌、重载重连重启卸载、性能压力和装备校准。


## 2026-10-12 镇墓狻猊15接续（源码与软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创镂空青铜狮形机关：真实腹腔火核/风箱、双齿轮鬃圈、铰接长兽口、四组连续髋膝足关节及粗体块铜球；无人体模板。七段动作每段81个真实源姿态采样、贴图/UV/落地/步行三足支撑/髋膝到足端连接检查通过。已接入24tick前摇/3秒90度扫火、10tick踏足/五段限时地火缝、14tick吼击/真实盾牌禁用与原生击退抗性、90tick四足断裂炉腔熄灭；只复用现有新版帝陵墓室局部15,1,17空场、同存档单UUID和确认死亡永久清场；齿轮熔铜、石火余烬燃料和原生击杀进度已接入。原文“无条件震退6格”与“霸体硬抗”相互冲突，保留原生击退抗性和地形，1.4强度的实机位移尚待标定。已写八项原生回归源码但按用户考试期间要求未运行Java/Gradle；构建、单/双人战斗、自然入口、持久化和装备平衡待实机验收，仍为PARTIAL，保留本条提示词。

- 当前94项：**1 DONE / 44 PARTIAL / 49 NOT_STARTED**。未新增整项删除；30基础/15精英的源码链已写入，12Boss/25神器/12神影仍待接；全部PARTIAL保留实机验收缺口。
- 权威可编辑源`generate_bronze_suanni.py`与实际runtimeJSON/PNG已同时更新；`review_bronze_suanni.py`、`validate_bronze_suanni.py`采样七段动作每段81帧，并检查实际串联髋膝到独立足端连接，最大误差0.000682m。正/背/两侧/45度/灰模/剪影及攻击、步行、死亡姿态均已实际软件查看；不是原生截图。
- 28骨骼94粗体块，四足铜球、真实腹腔/风箱/双八边齿轮颈圈/铰接狮口；主体含支撑2.125×2.3125×3.6875m（肩顶2m，齿轮高2.3125m），含尾饰2.125×2.3125×4.8319m。物理4×2.4m、有限cull6×5m/Y[-.5,4.5]，长度适配声明待实机标定。
- Java文法检查11个新建/共享文件通过，只使用Python tree-sitter，没有编译/JVM/Java测试。八个原生回归SOURCE覆盖完整24tick/单8m火柱/扫火/恢复、新建墙截火/挡伤、10tick/五段推进/60tick期、墙截地缝、one-layer whitelist/容器矿石/真实griefing、实际ServerPlayer盾牌/原生抗性/墙挡、重击/冷却/保存时间跳变、真实一次性UUID与卸载/90tick死亡。全部未执行；仍需新构建和单/双人普通AI、自然墓门入口、持久化重启卸载、性能与第十五只青铜/白银装备校准。


## 2026-10-12 Boss1饕宴活镬接续（源码与软件、原生未运行）

> 本地进度（2026-10-12）：已写入原创三足活镬/八足活镬双形态，主体为真正镂空铜镬，铰接兽口、双空腔钟、真实攻城轴座/活塞、12节连续骨鞭、六技能、8秒登场保护、60%变形/移速50%、10秒死亡、真实40米中心跨度祭坑/12柱/3骨祭祀/单UUID、有限陷阱与掉落/用途/原生击杀进度。两形态各12段动作×81真实源姿态和模型/PNG/UV/步行支撑/骨鞭伤害挂点/死亡落地软件检查通过；死亡壳体已修正为支撑崩解同时落地。完整无人体模板，主体含支撑高3.1875m、带残兵冠完整4.5m，物理4.8×4.5m适配明确记录。八项原生回归源码已写但未运行；本项目无既有耐力API，丧钟现接原生饱食消耗，精确耐力机制、完整登场声画、明确复战入口、FTB章节以及原生构建/单双人实战/世界入口/持久化/平衡性能仍待验收。因此PARTIAL，整项提示词保留；不运行Java、不播放声音、不操作亮度、不关闭愚者存档。

- 当前94项：**1 DONE / 45 PARTIAL / 48 NOT_STARTED**。未新增整项删除。新Java文法13文件通过（Python tree-sitter，仅文法）；完整24段动作各81帧、两法术和全部实际软件画面复核，通过后又发现死亡40tick无足悬空并修复，重新导出/采样/复看；不是构建/游戏PASS。八项nativeSOURCE覆盖真实祭坑/8秒保护、20tick完整前摇/12m物理冲撞/命中一次、新障碍阻断、低扫流血、真实6m油池期限、60%转阶段/4m跃砸/六缝、重击保冷却/保存时间跳变、卸载不是胜利/单UUID/死亡环境游标与NBT恢复。
- 实际完整尺寸第一阶段5.0779×4.5×5.0938m、第二阶段5.0779×4.5×5.4415m（含鞭/锤/冠；主体与支撑分别3.25×3.1875×3.9062m、4.1955×3.1875×4.3518m）。八足相位步行至少七足接地，前后转换至少三足支撑，骨鞭十二节连续连接最大误差0；源到原生命中方向六帧吻合。18m×10m有限cull与两阶段固定4.8×4.5m物理适配明确记录。
- 狻猊火柱也已修复0.1m锚点导致原版仅6.4m默认可见的问题；保持64m源渲染门限和实际有限火柱视锥。其资源SHA/软件结果已刷新，状态不提升。


## 2026-10-12 公孙无妄与中央龙吟刀接续（源码/软件，原生未运行）

> 本地进度（2026-10-12）：已写入原创骨马承载空腔铁誓龛、解体后双铁橇支撑的两种非人形结构，不保留人体头胸腰与双臂双腿。主体高3.8m/2.8m，真实四米切刀由双夹钳和轴承握持；24段动作各81帧、四色16px/UV、四足串联关节、接地、变形承重、原生下劈挂点与死亡消散软件检查通过，已修正过高刀风、箭尖碰撞错位和变形穿插。踏阵实际绕场内切、五米实体刀风、服务器疾跑/跳跃/攻击听声、24枚真实城墙箭、七次实际推进与限时裂隙、耗2.5%生命/限定场内3m血雾与四次安全闪斩已写入。真实32m中心跨度/15m城墙/7m开口瓮城、单UUID/卸载保留、12秒死亡、有限野花和每玩家一次中央空手拔龙吟刀已接入。九项Boss及六项神器原生回归源码未执行；完整登场声画、旧面容死亡意象的非人形适配、明确复战/FTB、原生构建/单双人实战/入口/生命周期/数值性能待验收，PARTIAL，整项提示词保留。继续暂停Java，不播放声音、不改亮度、不关闭愚者存档。

> 本地进度（2026-10-12）：已写入独立龙吟刀和统一ArtifactAbility/不同AttackProfile：实际2.2m刀身、3m全刀、闭合吞口环/朱砂柄/阶梯龙脊，手持原版Cuboid模型与世界Gecko纪念刀共用17个真实体块，16px四色PNG/UV及同尺度正背双侧/45度/灰模/剪影已复核。左击3.2m/180度横扫、0.8攻速/4tick技能后摇、原生40tick蓄力、十个实际已加载地面格/20tick限时地裂/16UUID命中去重/墙体阻断、服务器3tick拼刀另留1tick接收容差/40tick反击机会、三敌包围正面物理伤害减免25%均已接入。请求不携带身份/目标/坐标/伤害，服务器验证实际手持引用、冷却与自身时钟；地裂伤害在施放时固定，换武器不能借用伤害。击败公孙无妄后，12秒死亡结束才放置中央纪念刀，参战玩家空手领取一次；UUID/领取记录持久化，纪念物保留，不新增任意合成。六项原生回归源码未运行；本项目没有独立削韧/韧性API，暂用原生减半击退、既有受挫免疫和两Boss攻击时钟中断，其他精英统一硬直、实际3m击飞标定、左右手持/普通战斗/单双人/重载持久化/平衡和完整声画仍待验收，PARTIAL，整项保留，不以软件图充当实机。

- 当前94项：**1 DONE / 47 PARTIAL / 46 NOT_STARTED**，未新增整项删除。34个相关Java源文件通过Python tree-sitter文法解析，不能当作类型/API/构建通过；两个Boss重新软件复核，三份实际资源SHA无过期记录。
- 骨马完整静态2.7553×5.8125×5.125m（含4m武器），主体高3.8m；双橇完整2.75×4.8125×2.5m（含武器），主体2.8m。变形30..50t沿地面整体收缩，串联足端与新支撑连续，第二形态不使用人腿。下劈原生挂点分别1.125m和约1.14485m高，不从玩家头顶掠过。软件图是实际导出预览，不是游戏截图。
- 龙吟刀稳定追加请求ID18并纳入完整协议指纹，保留0..17原序号；载荷为空，拒绝额外字段。原版use/release也只作为请求，服务器记当前真实ItemStack引用与开始gameTime；换手/死亡/离维度/登出清会话。波伤害在释放时固定，不能靠切换武器提高伤害；16UUID/10格/20tick/已加载/墙体截断，不毁地形。
- 六项原生SOURCE覆盖空请求伪字段/手持检查、39vs40tick与换手/重复释放、10格波与换武器伤害快照、释放后新墙阻断、确认死亡/240tick后纪念刀/一次领取与SavedData、真实前向拼刀/25%包围减伤/背面例外。全部未运行；睡觉期间没有播放音频、改亮度或关闭已有愚者存档。


## 2026-10-12 湛卢剑接续（源码与软件；原生未执行）

> 本地进度（2026-10-12）：已写入独立湛卢剑和四个不同AttackProfile：实际全长1.4m、10骨骼/15Cuboids，四个45度真实切角组成八面墨玉剑刃，阶梯圆盘铜格/鹿皮柄，手持vanilla mesh与世界geo共用实际体块。左击刺/抹/撩/劈四段链、原生1.1攻速、无武器/受挫目标三倍原生绕护甲/抗性/附魔/盾牌的虚空伤害、高于80%生命命中免耐久、缺血延长3..12tick一次招架已接入。服务器20tick右键起势后展开5m/80tick止戈领域，16敌上限、双手物品原样暂存/70%独立减速、单UUID租约/多人不复制、取消/死亡/短租约过期恢复、主动击杀取消30%最大生命恢复；换成同ID另一把剑也取消原场。原创白八卦/旋转太极地面物体、半透明有限渲染、四色16px/UV、两模型81帧与实际八面截面软件检查通过；修正挥剑离手、每tick持物NBT刷新和最后耐久释放会话清理。无伤三清试炼/单次剑匣领取的可信服务端钩子与SavedData已写，但实际太清观、三关目标和剑匣互动尚未接入，不能从世界正常取得，不新增任意合成。八项湛卢原生回归源码和追加后的七项龙吟回归均未运行；构建、单双人握持/战斗/读档、多于16敌与PvP缴械、其他精英攻击时钟中断、数值/耐久/冷却/性能和声画待验，仍PARTIAL并保留整项提示词。

- 当前94项：**1 DONE / 48 PARTIAL / 45 NOT_STARTED**。八项湛卢SOURCE覆盖招架/非盾牌/内置武器识别、四段空间差异/3倍伤害/80%耐久阈值、20tick与80tick租约恢复/一次30%治疗、场外主动击杀取消治疗、换同ID另一栈/设备被替换后一次归还、双施法者争用、实际Mob NBT读档短租约恢复、三清钩子顺序/真实受伤拒绝/一次领取和SavedData。龙吟追加最后耐久释放清会话SOURCE，现七项。均未执行，不能代替原生场景验收。
- 已查看同尺度正背双侧/45度/灰模/剪影与领域四时刻实际资源软件图；15块手持/geo同源、3321点八面截面覆盖、两个81采样循环/地面/裁剪与四色PNG有效UV已检查。手持旋转不移动握柄，开始/结束只写一次姿态NBT，属性事件不把剑当成永久盾牌。
- 领域最多16敌，内置武器实体保守视作持械；原文全部敌人、PvP缴械和其他精英技能时钟中断仍待实际适配。无伤试炼目标与真实剑匣尚未实现，保持acquisitionActive=false。完整清单尚未完成，不删除PARTIAL任务。


## 2026-10-12 木鸢Boss3接续（源码/软件，原生未执行）

> 本地进度（2026-10-12）：已写入原创非人形机关鸟双形态：真实9m翼展/5.5m机身、五级连续折翼滑轨、开式齿轮箱/腹部弹仓、钢剪喙/双变焦镜头/独立脉冲雷核、四喷筒/双尾连杆及双四爪起落架；头顶铜盖补连续框架，折腿与弹仓错开，刃口伤害点/舱口投弹位置按实际模型修正。木壳过热48tick脱离后保留全金属支撑，无人体模板。六个独立服务端技能、200tick破云登场、60%阶段、原生碰撞限速飞行、8枚真实缓落雷火弹/触地引信/一次有限爆炸、抓取近边击飞/掩体挡风、4次落雷和平台1005格中最多150格烧塌、60tick升空后落地波/抬脚0.5m避波、220tick死亡解体已接入。真实Y200/35格无护栏八角平台与边缘首次登台绳梯、单UUID/卸载保留、确认死亡后中央绳梯/局部有限日晕、修复180耐久机括/120tick缓降木羽/残页加八线合成16节绳梯、原生击杀进度已写。两形态和炸弹共26动画各81真实源姿态、串联翼轨/双爪关节、落地/折腿/实际刃口挂点、循环/cull/四色16px和同尺度软件画面复核通过；47个相关Java只用Python文法解析。八项原生回归SOURCE未运行，构建、单双人完整飞行/抓取/边缘碰撞/原地形入口/死亡掉落绳梯与重载/多人密集目标/装备平衡性能及完整声画、复战和FTB待验收，仍PARTIAL，保留整项提示词。不运行Java、不播放声音、不调亮度、不关闭已有愚者存档。

- 当前94项：**1 DONE / 49 PARTIAL / 44 NOT_STARTED**，本次没有删除任何新增整项提示词。两形态73骨骼/172与136Cuboids；实际完整9×3×5.5m。四处结构脱节/穿插已修正：金属头顶连续支架、收腿移到舱壁外侧、折腿脚轴抵消、伤害线放回可见羽刃，投弹上缘与龙骨避让。
- 26动画各81帧、实际UV材质岛/四色16px、零串联翼轨/爪关节误差、脚底/折腿/循环/有限裁剪与三帧刃口端点检查通过；新参考实际读取官方RavenModel与HarbingerModel的父子与喷筒附着结构，未复制几何和素材。
- 八SOURCE覆盖原Y200平台/连续绳梯/完整10秒保护、8真实缓落弹/触地引信/到期、招架断钟与弹体/保冷却、60%48t过热/四落雷与150/1005格烧塌、真实50m升空/落地波与抬脚避波、炸弹与施法者重载不补伤、卸载保留UUID/确认死亡与220t中央梯/持久化、真实另一手修耐久/一次羽片缓降。Native未运行，47Java只通过Python文法，不能替代类型/API或构建。


## 2026-10-12 本批收尾：太清观与三清试炼（源码/软件；原生未运行）

> 本地进度（2026-10-12，本批收尾）：独立湛卢剑与四段服务端AttackProfile已写入；真1.4m/10骨骼/15Cuboids八面墨玉剑、铜格鹿皮柄、原生手持mesh和geo同源。刺/抹/撩/劈、无武器或受挫目标3倍虚空伤害、80%生命耐久阈值、3..12tick一次招架，以及20tick起势、5m/80tick止戈领域、16敌装备租约/70%减速/未主动击杀则恢复30%最大生命已有源码。已补真正21×21太清观原生结构/三座连续支撑琉璃屋顶/绿凝神台与相连白石道/青止戈阵，以及2m古剑匣三个原生状态；内部复用实际15块剑体，领取后留空匣。服务端实际40tick静立、五个顺序路径点、空双手120tick四次有预警可躲的真实伤害脉冲，全程无伤/不得主动攻击/90秒超时；离开、跳过道、移动或时钟断续、换维/退出取消，不强载区块。空主手靠近4m、库存空位、SavedData按世界玩家UUID一次领取，已获得资格不能另开试炼，无任意合成。实际八面截面/两模型81帧、16px四色/UV、剑匣封存/解封/空匣和1.4m内部尺寸软件复核通过；53个相关Java只由Python作文法解析。原有八项神器与新增两项太清观原生回归SOURCE均未运行；构建/API、自然地形生成与完整三关/剑匣碰撞裁剪、单双人握持战斗/读档、多于16敌/PvP政策、其他精英时钟、数值/耐久/冷却/性能/声画与FTB尚待验收，仍PARTIAL，保留整项提示词。

- 本批最后检查：53个Boss/神器/共享Java源码经Python tree-sitter文法检查通过；这不是类型/API或构建结果。木鸢26动画各81真实姿态；湛卢实际八面截面3321点、原生15块手持与geo同源、剑/领域两动画各81帧；剑匣封存/解封各21块、领取后空匣6块，内部真实1.4m剑完整容纳，16RGB四色/2px白边/最小2×2色块/整数UV检查通过。实际软件图及五份当前源码指纹已同步。
- 三座屋顶用既有原生砖木/琉璃方块；真实连贯白石折线路径与两个参悟区域在21×21范围内，沒有新造怪比例人像。四次止戈伤害有20tick扇区预警，可移动避区、抬脚跳过或由真实柱挡住；无主动音效、无全局天气改动、无强载区块。
- 两项新增太清观GameTest仅为SOURCE：实际原生地板/支撑/屋顶/2m碰撞与40t静立；实际受伤取消、重试和位置突变后不能取得资格。完整三关、自然地形生成、剑匣裁剪/碰撞、多人竞争与存档重启尚无当前原生通过结果。不能把旧湛卢钩子测试当作整个三关验收。
- 当前94项：**1 DONE / 49 PARTIAL / 44 NOT_STARTED**。九首鸟旧整项提示词已删除，其余93项未完成任务的要求和记录保留；本批没有新增整项删除。外部cod1与仓库副本同步；保留建模要求文件和用户未提交改动，不提交不推送，不运行Java、不播放声音、不调亮度、不关闭现有愚者存档。用户最后要求“做完这些结束”，完成本批收尾后停止，不启动Boss4/神器3或其他新条目。
