# 云砖交付：2026-10-11

已完成并删除追加清单独立行“fading_cloud_tile：云砖，踩踏后逐渐失碰撞再恢复。”，累计12处删除；完整冲霄隐仙观及其余清单仍保留。

实际注册dynasty:fading_cloud_tile，交付三层粗阶梯Cuboid模型、16×16四纯色白边PNG、四向blockstate和嵌入同一贴图的可编辑bbmodel。制作前体块与动作说明见PLAN.md，五视图和黑剪影见cloud-review.png。原生Java方块模型由现有BE渲染，不新增无用途的Gecko实体动画。

踩踏触发现有房间时钟：20tick预警逐渐收缩，40tick消散且真实无碰撞，36tick恢复生长后重新承重。复用原FLOOR存档/同步/防夹逻辑：占位生物未离开时保持无碰撞、不突然显示。没有改共享DungeonMechanismBlock和DungeonMechanismBlockEntity，也没有改其他开发者战斗/任务/AI。

构建及79项原生Cod2服务端测试通过。新增测试验证预警承重、消散与恢复期间无碰撞、存档不补跳时间、占位等待和清空后恢复。最终静音隔离Forge实机native/run2有9张截图和10条记录；同一云砖实例下玩家实际踩上Y=-57，随后物理下落至Y=-60，客户端与服务端位置一致，碰撞依次为有/无/无/有。多视角、恢复动画及实际资源重载均已查看。3个运行资源与生产JAR一致，QA类不进入JAR。

本轮客户端启动2次。run1因独立拍摄相机抑制玩家位置上报而断言失败，保留失败证据；run2在测试代码中通过原版移动包同步真实客户端物理位置，不直接移动服务器玩家、不修改生产逻辑，验收通过。两次客户端均已关闭。截图总览：native/run2/review-contact-sheet.jpg；机器报告：DELIVERY_20261011.json。

删除前文件精确匹配上一账本SHA，source/cod2-before-cloud-deletion.txt保留检查点，已验证仅移除独立云砖行、其他字节不变。人物新要求保持在assets/dynasty/AGENTS.md，本批没有改人物或小Boss，未把机关验收算作人物完成。未推送GitHub。
