# NPC 自然像素与交易服务

本轮修改 15 名剧情 NPC 的脸部、发际线、服装接缝及皮革、木材、金属像素。保持现有角色、碰撞、骨骼、握点、剧情与 165 个动画；移除两片悬浮黑色眼睛几何，眼睛绘入头部真实 UV。128×128 原创硬边图集，16–23 色，逐面 UV 与两像素保护边。普通人类保留人类身份。

实际查看用户提供的 [Human Companions 人物图](https://media.forgecdn.net/attachments/423/810/models.png)、[MCA Reborn 村落人物画面](https://media.forgecdn.net/attachments/590/210/2023-01-02_11.png)、[Wizardry 冰巫师](https://media.forgecdn.net/attachments/202/398/2017-01-16_20.png)、[Iron's Spells 火焰法师](https://media.forgecdn.net/attachments/653/528/2023-04-27_19.png)。借鉴眼白与瞳孔、发际线、衣领、腰带和靴子的像素层级，未使用参考作品像素或模型。原版自然人物比例与本轮最新版《建模要求.txt》11、19、20 节适用。

右键直接进入原版村民交易布局；上方切换交易、修补、附魔、交谈。Shift 右键也可进入原有剧情。修补一次 16 铜币，恢复全部耐久；随机附魔一次 32 铜币，增加或提升 1–3 项适用于该物品且兼容现有附魔的非诅咒、非宝藏附魔。姓名、物品 NBT 和旧附魔保留。确认成功时服务端扣费，产生真实成品槽；关闭或切回交易返还所有剩余物品。原有商品、库存和特殊场景权限保留。

15 种 NPC 与 30 种普通生物刷怪蛋按服饰、皮毛、甲壳、元素配色，原有 ID 不变。实际客户端两层 ItemColors 已验证。

可编辑源：`tools/art/cod3/rebuild_npcs.py`、`natural_pixels.py`、本目录 `blockbench/*.bbmodel` 与相邻动画。运行资源仍为 `assets/dynasty/{geo,animations}/npc` 和 `textures/entity/npc`，绑定仍为 `Cod3NpcRenderer`。

`verification.json` 和 `native/` 保存本轮证据。一个静音隐藏的真实 Forge 客户端完成集成服务器交易、实际网络切页与成品同步、实际世界渲染和 75 张 GeckoLib 正面/45°/侧面/背面/纯黑剪影视图。图形资源检查为自动客户端，不是人工游玩。离线隔离构建通过。其他开发者构建期间更新了非 NPC 资源，测试用冻结 JAR 不覆盖他们当前的整合包本体；下一次正常导出会从当前本地源码构建全部改动。
