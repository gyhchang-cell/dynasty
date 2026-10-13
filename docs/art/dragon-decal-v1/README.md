# 屠龙刀：龙类实际受击部位龙纹

本轮接入 cod4 `dragon_slayer` 的龙类命中 decal。分类使用新增实体类型标签 `dynasty:dragon_decal_targets`，默认仅原版末影龙、现有龙王和龙帝；不通过实体名字或所有人形共同基类猜龙。注册ID、Boss资源、AI、原伤害和350武器加成保留。

普通标签龙沿用已有不可变原始武器回执，观察直接玩家近战的最终正伤害。末影龙原生攻击指向 `EnderDragonPart`，最终 LivingDamageEvent 却在父龙上，已有 `primaryStack` 因UUID不同不能直接复用。因此本轮独立捕获实际 AttackEntityEvent 的屠龙刀与部位接触回执，绑定攻击者、父龙、维度、同tick和实际部位槽号；最终正伤害才发送。间接攻击、法术、合成伤害、取消、零或NaN最终伤害拒绝。回执最多32条、每tick末/停服清理，每玩家同tick至多一次。没有修改公共战斗类来让末影龙更易受伤。

生产源 `cod3/DragonDecal.java`、`client/DragonDecalRenderer.java`，`Cod3VisualPacket` 仅增加专用路由，字段和编码不变。该cue的origin为父体局部接触快照、tick为实际部位槽号；客户端查父龙的当前同一部位并插值其真实位置，转向/摆头也跟随，不只是跟父体平移。普通龙沿用身前接触快照。锚点、尺度依据真实包围尺寸，平面0.45–1.4格、12tick淡出，两个三角形，最多12实例、32格广播、64格绘制距离，死亡/移除/换世界清理。独立纹理缓冲与GL恢复，不动公共 `Cod3VfxRenderer`，不增加声音、相机、伤害、硬直、实体或掉落。

`plan.json` 为制作前方案。实际资源 `textures/effect/dragon_slayer_decal.png` 与 `.png.mcmeta` 已接入：原创有分叉双角、宽吻、弯曲长身、短爪及尾的阶梯龙纹，16逻辑格按2像素硬块形成32×32图，三种纯色、透明两像素边距，nearest且不模糊。它是受击表面纹样，不是新生物模型；不生成无用途geo/animation。可编辑源是 `tools/art/dragon-decal/make_texture.py`，精确再生成、色板/边距/材质元数据检查通过。

实际生产Java `DragonCheck` 130687项通过，覆盖24方向、三尺度、三接触偏移、每半tick、UV完整图集、有限两三角形、实体平移、原FriendlyByteBuf往返及非法槽号/字段拒绝。`actual-triangles.json` 由真实生产函数导出。`software-views.png` 使用当前PNG真实UV nearest采样，实际查看正、45度、左右侧、背、黑剪影、灰色；表面decal侧边不可见是预期。`software-timeline.png` 核对12tick淡出结束。**软件图仅验证资源/几何/读图，不是游戏截图，没有证明GL光照、模型遮挡或实际透明重叠。**

隔离真实Forge无图形服务器6项通过：两只真实注册Boss原生 `Player.attack` 与实际身前锚点；真实末影龙头原生攻击、父体伤害回调、真实部位接触而非父体中心、头部独立位移后的锚点跟随；普通目标/其他武器/箭伤害拒绝；后续取消/零/NaN拒绝；过期部位回执、名字伪装拒绝；同tick字段/NBT及视觉不重新造成伤害。FakePlayer和一次性测试世界不是真人联机或用户存档。首次测试修正了测试生物属性上限与入世界后Boss重设血量，再定位并修复上述父子UUID问题；首次失败日志保留，最终部位跟随版再次6项全过。

首次当前整仓冻结编译因另一开发者尚在编写的 `blueprint/elite/BronzeSuanni.java:96` 使用不存在的 `AABB(Vec3)` 构造而失败，本轮新增类没有编译错误，未修改或排除该开发者代码。采用上一轮完整5255源成功构建基线，加本轮6个源/资源，私有 `qa-frozen` 中6项服务器测试及离线 build/reobfJar通过，Jar不含本轮QA。**本轮最终Jar是明确的旧成功基线加本轮改动，不能称为最新整仓构建，也不覆盖共享/导出Jar。** 哈希、版本及首次当前整仓失败在 `verification.json`；待该文件由原开发者修好后补验完整最新源。

待验：最新整仓构建；新版本静音实机普通光照/阴影、龙王/龙帝表面贴合与动画遮挡、末影龙自然飞行各部位、资源重载、第一/第三人称、真实32格双客户端视距/重叠。原提示词先备份于 `build/maintenance/dragon-decal-v1/prompt-before/`，因完整验收未满足，本轮不删对应龙纹或真人条款。用户愚者客户端仍运行，不启动图形客户端、不关/重启/修改存档、不动声音/亮度、不唤醒屏幕、不推送GitHub。
