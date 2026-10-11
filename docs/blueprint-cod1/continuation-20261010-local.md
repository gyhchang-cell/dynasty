# cod1 本地接续：2026-10-10

用户要求修改本地工程并删除已完成提示词，GitHub 由用户上传。没有提交或推送。本文件记录实际范围；**全部任务仍未完成：0 DONE / 33 PARTIAL / 61 NOT_STARTED**。

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
| 伏波巡海夜叉 | NOT_STARTED | 未接入 | `fubo_xunhai_yecha.geo.json` / `fubo_xunhai_yecha.animation.json` | `fubo_xunhai_yecha.png` | 分水破浪斩、潜渊突袭、逆水三连挑 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 搬山甲胄尸狂 | NOT_STARTED | 未接入 | `banshan_jiazhou_shikuang.geo.json` / `banshan_jiazhou_shikuang.animation.json` | `banshan_jiazhou_shikuang.png` | 尸狂龙卷、肉弹飞扑、怨血喷涌 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 墨家绝影刺客 | NOT_STARTED | 未接入 | `mojia_jueying_cike.geo.json` / `mojia_jueying_cike.animation.json` | `mojia_jueying_cike.png` | 水墨遁形、八方墨影斩、墨滴爆裂 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 撼山铜甲巨猿 | NOT_STARTED | 未接入 | `hanshan_tongjia_juyuan.geo.json` / `hanshan_tongjia_juyuan.animation.json` | `hanshan_tongjia_juyuan.png` | 铜臂狂乱大捶打、拔木穿石、飞跃震荡扑杀 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 青灯判官鬼差 | NOT_STARTED | 未接入 | `qingdeng_panguan_guichai.geo.json` / `qingdeng_panguan_guichai.animation.json` | `qingdeng_panguan_guichai.png` | 生死勾名、铁画银钩、勾魂铁索牢 | dynasty:underworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 烈风金雕羽士 | NOT_STARTED | 未接入 | `liefeng_jindiao_yushi.geo.json` / `liefeng_jindiao_yushi.animation.json` | `liefeng_jindiao_yushi.png` | 破晓千羽落、翎羽风刃切、旋风俯冲突刺 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 镇墓狻猊铜吼 | NOT_STARTED | 未接入 | `zhenmu_suanni_tonghou.geo.json` / `zhenmu_suanni_tonghou.animation.json` | `zhenmu_suanni_tonghou.png` | 地心石火喷、青铜踏碎、铜兽怒吼 | minecraft:overworld / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 断代凶镬·饕宴之尸 | NOT_STARTED | 未接入 | `taoyan_zhishi.geo.json` / `taoyan_zhishi.animation.json` | `taoyan_zhishi.png` | 铁撞角碎岳、骨鞭扫千军、沸油泼地、丧钟夺魂、炎角炼狱砸、饕餮暴饮 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 殉节盲帅·公孙无妄 | NOT_STARTED | 未接入 | `gongsun_wuwang.geo.json` / `gongsun_wuwang.animation.json` | `gongsun_wuwang.png` | 踏阵马踏飞燕、裂地回旋劈、听风辨位、残矢齐射、十方俱灭狂斩、孤忠泣血 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 九霄木鸢·鲁班遗煞 | NOT_STARTED | 未接入 | `luban_yisha.geo.json` / `luban_yisha.animation.json` | `luban_yisha.png` | 掠空翎羽斩、天女散雷火、鹰爪碎颅抓、暴风气流柱、天枢引雷落、绝灭神机冲 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 沉渊骨龙·烛阴残蜕 | NOT_STARTED | 未接入 | `zhuyin_cantui.geo.json` / `zhuyin_cantui.animation.json` | `zhuyin_cantui.png` | 幽冥冰霜吐息、骨剪摆尾、潜水盘绞、冰魄陨坠、烛阴开眼·天地皆昼、黄泉逆流穿刺 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 金阙尸仙·昭明帝 | NOT_STARTED | 未接入 | `zhaoming_di.geo.json` / `zhaoming_di.animation.json` | `zhaoming_di.png` | 天子九剑·破虏、十二水银飞剑、玉玺镇国运、汞毒血海、万国来朝万剑阵、帝王尸气斩、真龙解体 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 赤练红罗·蛇母娘娘 | NOT_STARTED | 未接入 | `shemu_niangniang.geo.json` / `shemu_niangniang.animation.json` | `shemu_niangniang.png` | 煞音断魂弦、巨蟒贴地横卷、百蛇破土、红罗障目、赤练死锁绞杀、万毒归宗血雾 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 无相孽火·黑风法王 | NOT_STARTED | 未接入 | `heifeng_fawang.geo.json` / `heifeng_fawang.animation.json` | `heifeng_fawang.png` | 无间黑炎球、大悲黑光掌、业障吸星、罗汉降魔杵、明王八方乱打、天魔大寂灭 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 镇国机关偶·刑天遗卫 | NOT_STARTED | 未接入 | `xingtian_yiwei.geo.json` / `xingtian_yiwei.animation.json` | `xingtian_yiwei.png` | 战神断岳斩、重盾排山、飞轮磨魂、泄压蒸汽暴、天倾地裂八方碎、追魂狂暴轮斩 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 九天玄刹·雷泽巨灵 | NOT_STARTED | 未接入 | `leize_juling.geo.json` / `leize_juling.animation.json` | `leize_juling.png` | 雷公槌击破虚、八鼓连珠天雷、电浆乱舞球、雷泽充能、天罚大审判、神速千雷瞬刺 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 幽冥引渡·彼岸冥舟 | NOT_STARTED | 未接入 | `bian_mingzhou.geo.json` / `bian_mingzhou.animation.json` | `bian_mingzhou.png` | 铁篙碎浪劈、骨桨碾压冲锋、彼岸花落生魂引、往生丧音、万魂齐喑冲天炮、忘川沉沦死境 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 封魔剑冢·玄天剑煞 | NOT_STARTED | 未接入 | `xuantian_jiansha.geo.json` / `xuantian_jiansha.animation.json` | `xuantian_jiansha.png` | 重剑开天门、飞剑游龙击、剑气画地为牢、剑刃风暴、瞬影万剑一、天剑劫·落九霄 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 四象逆脉·混元祖兽 | NOT_STARTED | 未接入 | `hunyuan_zushou.geo.json` / `hunyuan_zushou.animation.json` | `hunyuan_zushou.png` | 青龙裂霄霆、虎跃裂穹爪、朱雀劫火焚八荒、玄武厚土逆反盾、玄蛇噬魂毒域、四象混沌大寂灭 |  / 待接入 | PENDING_REGISTERED_ITEM_AND_USE_MAPPING | NOT_RUN | NOT_RUN | 尚未实现 |
| 龙吟斩马断岳刀 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `longyin_zhanma_duanyue_dao.png` | 断岳千重浪、威慑阵列 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
| 湛卢仁道八面剑 | NOT_STARTED | 未接入 | 未接入 / 未接入 | `zhanlu_rendao_bamian_jian.png` | 仁道止戈、不杀而屈 |  / 待接入 | PENDING_REWARD_HOOK | NOT_RUN | NOT_RUN | 尚未实现 |
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
