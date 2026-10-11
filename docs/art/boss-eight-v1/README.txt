Dynasty：八个现有小Boss美术升级（2026-10-11）

实际资源已同步到当前 Dynasty 工作区。此目录保存原模型对照、五方向检查、游戏原生截图、Blockbench 可编辑源文件和校验记录。

本轮对象与完成内容
亡故始皇 undead_first_emperor：胸背甲厚度、棺式胸甲、膝关节和弯曲前臂。
宦官首脑 eunuch_mastermind：高翼冠、立领、佝偻胸背、垂袖与腰带层次。
叛将 rebel_general：独立模型、旗背、护颊头盔、肩甲与分段腿；真实主副手物品仍使用握持骨骼。
陷阵断头将 xianzhen_duantoujiang：只补现有胸背甲和裙甲缺口；保留提头、巨刃、颈火及技能时间。
千机百炼偃师 qianji_bailian_yanshi：展开辅助臂、机关箱与胸甲层次；死亡改为侧倒的机关残骸。
披鳞执金吾 pilin_zhijinwu：重甲大色块、头冠、领甲与髋甲；保留已有双手持戟 IK 轨迹。
白面狐仙姑 baimian_huxiangu：面具/发髻比例、宽袖、阶梯裙摆和三尾；修正死亡袍服离地问题。
巨锤金甲力士 juchui_jinjia_lishi：宽胸背甲、脊状头盔、锤柄握点、膝关节及落地弃锤姿态。

每只交付 geo.json、animation.json、实际16×16 PNG，以及 blockbench/ 下的 bbmodel 和动画侧文件。PNG 最多4种纯色（含白色）、白色留边、2×2色块、无渐变。模型为原创 Cuboid，借鉴来源及具体方法见 research-and-selection.json；未复制参考模组资产。暮色森林研究基于实际模型代码，其 Wiki 图片因证书错误未查看。

资源位置
前三只：assets/dynasty/{geo,animations}/boss_cuboid 与 textures/entity/boss_cuboid。
断头将、偃师：当前实际生效的 blueprint/cod2_voxel 路径。
执金吾、狐仙姑、力士：blueprint/elite 路径。
hammer_chain.geo.json 同步调整 UV，因为飞锤与力士共用贴图。
唯一正式 Java 变更是 BossEightArtBindings.java，仅将现有叛将注册到现有 BossCuboidRenderer。未改战斗、AI、注册ID、任务、掉落或数值；未修改镇渊帝君及已精修的非人类资源。

检查与证据
lineup.png 和 *-review.png 是读取真实导出几何与UV的离线预览，包含正面、45度、90度侧面、背面及纯黑剪影。
native-overview.png 和 native-actions.png 是实际 Forge 客户端截图拼图，未把离线预览当作游戏截图。部分场景保留原有掉落、纪念物及特效。
validation.json：8套资源、369骨骼、572 Cuboid、53段动画；检查UV、骨骼引用、旧动画名/时长/循环与死亡地面位置。
native-validation.json：74个连续场景（0–73）、8个真实注册实体；验证实际渲染绑定、贴图与控制器，包含行走、受击、死亡和15个精英技能。原始状态保存在 native-records/，大尺寸截图保存在本地 native/（不提交Git）。
共启动3次安静测试客户端：第一次行走夹具失败，第二次通过42场景后清理夹具失败，修正测试夹具后从42续测，余下32场景通过。通过批次使用完全相同的正式资源和JAR。所有测试客户端均已退出。
这些是受控场景的美术加载和动作验证，不代替自然战斗平衡或真人多人联机验收。
build.log：Forge 1.20.1 / GeckoLib 4.8.4 构建成功；不升级依赖。QA类和静默窗口agent不进入正式JAR。

多人开发与构建边界
独立分支 codex/boss-eight-art 基于 00e9d733。五只精英当前来自共享工作区尚未提交的实现，不能通过提交本轮美术来替其他开发者提交其战斗代码。
本轮构建使用 build/boss-eight-baseline 的冻结代码快照，并只覆盖本轮资源及绑定到 build/boss-eight-integrated；成功构建和原生验证针对这份集成快照。Git美术分支自身不包含其他开发者尚未提交的五只精英实现。后续合入时需要对应实现已经在目标分支存在。
delivery.json 记录同步的26个自有文件及SHA256；protected-files.json 记录本轮未修改的冻结依赖。同步前对共享目标文件做基线比较，旧文件备份在 build/boss-eight-delivery/before-sync。
completed-prompts.json/.patch 只记录删去的已完成建模描述；原有战斗、动态特效、整只精英验收保留。两个共享提示词全文未纳入本轮Git提交。

复现（从仓库根目录，Python需要Pillow和numpy，Java使用17）
python3 tools/art/boss-eight/build.py
python3 tools/art/boss-eight/review.py
python3 tools/art/boss-eight/validate.py
python3 tools/art/boss-eight/snapshot.py /path/to/current/integrated/dynasty
./gradlew --offline --no-daemon -I tools/art/boss-eight/qa.init.gradle -PbossEightSnapshot=true build compileBossEightQaJava bossEightAgentJar --console=plain
python3 tools/art/boss-eight/run_native.py unique-run-name /path/to/existing/forge/launch.json

生成器使用本轮冻结基线，后续有人继续精修这些资源时，不应盲目重跑旧生成器覆盖成果。原生测试需要既有Forge启动配置和缓存依赖；不必为查看交付物再次启动Java。
