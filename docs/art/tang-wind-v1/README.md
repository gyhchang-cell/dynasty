# 唐刀：真实加速触发后的青风尾迹

针对 cod4-3 `tang_dao`，已在实际原生加速施加处接入独立青風尾迹。原 `DynastyCombatEvents` 的伤害计算和 `MOVEMENT_SPEED, 60, 0, true, false` 参数保留；只增加施加前的只读状态判断，以及原 `addEffect` 成功后的视觉回执。没有重写战斗、任务、其他武器机制、公共 `Cod3VfxRenderer` 或其他聊天的模型。

首次获得一级加速、短时一级加速延长到60 tick时触发；等长/更长一级加速、强效加速、无限时长加速不会误触发。Forge 拒绝施加、实际施加后不是原一级60 tick效果也不触发。首次真实服务器测试发现 `addEffect` 可能仅因 ambient/visible 标志更新返回 true，因此增加前后状态核对，保留失败日志，不将这个返回值单独当作加速证据。

实际生产源是 `cod3/TangWind.java` 与 `client/TangWindRenderer.java`，复用现有 `Cod3VisualPacket` 字段，独立 cue `equipment_tang_speed_applied`。32格广播、每玩家每tick一次、客户端每实体一个实例且全局最多12个，12 tick结束；死亡、加速解除、换世界或超过8格瞬移时清除，64格外不画。原七星刀、七种材质命中和通用 cue 分流保留。无额外伤害/加速/音效/相机变化，不新增服务器实体、注册ID或协议字段。

制作前结构方案在 `plan.json`。脚边0.2格和腰部0.85格的两条阶梯风痕，每条五个分离硬边矩形，交叉平面保证侧向有厚度；单实例40三角形、一种青绿色纯色，最大局部范围小于1.8格。12 tick内短伸展及时间衰减，跟随实际实体插值位置，以实际水平速度为方向，静止/纯竖直时使用原触发方向。自己第一人称仅绘脚边一条（20三角形），避免腰部风痕靠近视线。没有模糊贴图、光滑管道或屏幕覆盖层；没有更改唐刀持握、已有物品贴图或生物资源。

验证：

- 整仓冻结5207源的离线 build/reobfJar、Jar检查见 `verification.json` 与 `build-final.log`，没有排除生产客户端类或打入 QA 类。构建 Jar保留在隔离目录，不覆盖共享整合包产物，不推送 GitHub。
- 隔离无界面 Forge 服务器4项 GameTest通过：真实注册唐刀调用原生 `Player.attack` 和效果回调，原60 tick/一级/ambient/visible参数；等长/长时/强效/无限加速拒绝错误风痕；短时刷新、同tick视觉字段和玩家NBT往返；实际Forge Applicable DENY及其他武器不能借用加速。参与者为 FakePlayer/一次性测试牛，**不是真人或游戏客户端**。
- 实际生产Java几何/位置/生命周期104868检查通过，并使用真实 FriendlyByteBuf 编解码。水平、斜向、竖直、零/NaN方向，全部1/8tick取样、实际位置平移跟随、第一人称高度和有限包围均核对，错误/巨大 cue拒绝；见 `geometry-codec.log`。
- `actual-triangles.json` 是上述生产函数的实际输出；`software-views.png` 和 `software-timeline.png` 已实际查看正、45度、侧、背、黑剪影、灰模和起止时序。**仅为不透明软件形状诊断，没有游戏光照、透明叠加、玩家同框或真实客户端证明。**

仍需新版本实机第一/第三人称、普通光照、加速移动/转向/游泳、原残影组合、效果解除和32格真人双客户端旁观/重叠验收。用户愚者游戏与存档保留，本轮没有图形客户端启动，不唤醒屏幕，不调整声音或亮度。原提示词在 `build/maintenance/tang-wind-v1/prompt-before/` 先备份；唐刀及联机条款因上述待验内容保持，未删除部分完成条目。
