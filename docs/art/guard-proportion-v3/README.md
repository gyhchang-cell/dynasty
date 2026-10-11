# 禁卫比例收尾与新建模要求 / 2026-10-11

在已验收的[裙甲与兵种剪影v2](../guard-style-v2/README.md)上，头部及全部脸型/盔冠子骨统一缩小6%，肩距10→10.5单位（+5%），腰主块5.05→4.95单位（−1.98%）。仍有166个Cuboid、72个原骨骼名，新增/删除体块和骨骼均为0。脚向前厚度、分段前臂/护腕、胸腰骨盆、刀鞘、箭匣、长枪、双持弩均保留。其他三角色在96组实际Java姿势中完全相同。未修改任何PNG、战斗/任务/AI/军籍代码、ID、存档、实体碰撞或渲染全局缩放。

制作前说明见[PLAN.md](PLAN.md)。新收到的《建模要求.txt》已读取，原文快照、哈希和实际参考记录见[reference-study.json](reference-study.json)。已实际查看灾变发布者的[Ignis展示](https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png)、[Ignis模型层级](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/client/model/entity/Ignis_Model.java)，以及暮色森林的[PhantomArmor模型](https://github.com/TeamTwilight/twilightforest/blob/ff2560a8d071a0b8e9e2dfbe4609537a50553bb0/src/main/java/twilightforest/client/model/armor/PhantomArmorModel.java)、[KnightPhantom模型](https://github.com/TeamTwilight/twilightforest/blob/ff2560a8d071a0b8e9e2dfbe4609537a50553bb0/src/main/java/twilightforest/client/model/entity/KnightPhantomModel.java)与[盔甲UV](https://github.com/TeamTwilight/twilightforest/blob/ff2560a8d071a0b8e9e2dfbe4609537a50553bb0/src/main/resources/assets/twilightforest/textures/entity/equipment/humanoid/phantom.png)。借鉴的是醒目的大盾/武器、分层躯体、头盔子骨与硬像素分区；维持Dynasty自己的翼冠、军队色、分节肘膝和兵种附件。参考源码/图片只在忽略的build目录中查看，没有复制到生产资源、移植代码或执行外部脚本。本轮是普通禁卫收尾，不宣称替其它任务完成小Boss。

首次数值测试发现脸型变体会覆盖横向缩放，修正到变体之后再缩放。首次29阶段客户端虽通过驱动断言，但五面/黑剪影人工审查发现下颌与颈部空隙，**未接受最终视觉，也未删比例提示词**。保留缩放，将头的局部位置向颈部移动0.249单位，新增32组看向/受击/倒地姿势下的下颌/颈OBB接触检查；最小接触深度0.003125格。最终原生渲染每次裙腿采样同时断言颈部接触。失败和拒收记录见[diagnostics.json](diagnostics.json)、[visual-rejected-01.json](visual-rejected-01.json)。

最终构建与`guard-proportion-final-02`全29阶段通过：16个刀/枪/盾/弩视角，空场、18站立、18真实AI跟随，4个真实行走近景、6个未改变的叛将视角。每帧渲染全部18人，18人均移动超过1格并出现膝动画，服务器主人位置由真实客户端输入改变。移动帧中位8.666ms、P95 9.933ms。13,545组真实Java姿势/4,740,750对OBB检测为0裙腿重叠，裙/腿/脚顶点与v2逐字节相同，root位置不变；128组弩双握点和原生各武器挂点通过。数值证据、原生截图、五面软件/纯黑图分别标记，详情见[visual-review.json](visual-review.json)和[validation.json](validation.json)。软件身体顶点不含原版持物层的刀/盾/弩，持物效果用游戏原帧检查。

最终JAR SHA256 **8296372b2eae931140ef9111063b562d4e8e1d4f149ebd90832611024909d3b4**，保存到本地`build/maintenance-artifacts/art-guard-proportion-v3/dynasty-1.4.0.jar`。对上一轮v2的5,444个JAR条目，只有Manifest和`DynastyCharacterModel.class`改变；资源、其他生产类均相同，QA/隐藏agent没有进入JAR。该隔离验证包使用前轮冻结的源，不包含其它开发者后来在main上的WIP。源文件以SHA保护只同步本轮明确文件，其它改动保留。

`verify_guard_proportion.py`只核对文件，不启动Java。`run_native.py --guard-proportion`用于必要的单次集中原生复验。历史v2保留其独立冻结证据，复现旧报告应使用对应旧提交/构建。

备份后删除cod6最后一段比例要求，7.3四个正文段落均完成后移除空标题；准确原文、备份和前后哈希见[prompt-edits.json](prompt-edits.json)。本次手动续作合计删除4段禁卫要求，cod4没有新删除。T35付费阵位、自然射击/装填/技能命中时序、真实生态和真人联机仍未实测并继续保留，8个小Boss由另一任务处理。用户建模规范文件本身保留，不当作可删除待办。仅本地保存与提交，不推送GitHub，不恢复旧夜间定时任务。
