# 天河垂落·倒流银瀑

清单奇观#8。原先五条光线加圆环，现替换为三束硬边水幕、向上运动的银白亮带、侧面逆流与少量水雾。正式加载链为ScenicEvents → scenic_08数据包 → Cod3VfxRenderer → ScenicSkyRenderer.drawSilverfall → ScenicSilverfall.mesh；预览分支调用同一几何。

## 本轮100张其他模组场景参考

从14个Minecraft模组的作者Modrinth图库中实际审阅175张候选图，筛选100张不同场景参考，未与既有cod3参考哈希重复。来源包括The Aether、Deep Aether、Tectonic、Terralith、Regions Unexplored、Biomes O’ Plenty、Oh The Biomes We’ve Gone、BetterNether、Promenade、Deeper and Darker、Alex’s Caves、The Bumblezone、Dungeons and Taverns和Floating Islands。这里是100张场景，不是100个模组；拼图按一张计算。广告、Logo、菜单、装备墙和不相关近景不计入。

逐图来源见references.json，九张联系表与取舍依据见reference-review.json。外部原图仅存于ignored build，不作为运行资产，不复制其他模组模型/贴图。主要参考[Aether瀑布与悬崖](https://modrinth.com/mod/aether/gallery)、[Tectonic地下河与峡谷](https://modrinth.com/mod/tectonic/gallery)、[Biomes O’ Plenty发光洞穴](https://modrinth.com/mod/biomes-o-plenty/gallery)的体量/留白/明暗关系。

## 实际改变

主水幕48格，两侧34/39格；共三束，粗阶梯水口和深浅侧面保持Minecraft体块。四种源色、每面硬边，不使用模糊图、渐变贴图或全屏后处理。正背与侧面72条亮带都向上流动，18组双面小雾滴沿固定seed路径上升。单一主体LOD保留远景轮廓，MINIMAL只移除水雾。

合计282面，MINIMAL为246面，均低于清单300预算；不生成流体方块、AI实体、伤害或掉落。沿用主世界边界附近、任意时刻晴天、1200tick寿命；客户端随雨量渐隐。服务器控制固定锚点、seed与start，迟到不重新计时。透明面排序，近裁面保守剔除，离区域/维度清理，不改全局天空、雾或相机。

补上原先缺失的局部水声绑定：仅有效寿命/晴天/48格内有音量，使用原版WATER_AMBIENT，播放频率120tick。静音验收不会试听音效，也不更改系统声音。

## 验证状态

3025组正式几何检查通过，包括确定性、向上流动、范围、寿命、天气、单LOD、MINIMAL与水声参数。已人工查看正面、45度、90度侧面、背面及纯黑剪影的软件预览；这些不是实际游戏截图。全局资源检查160项目录、15套骨架、165动画状态、45地标、6绑定通过。

下方最终构建、服务器和原生检查已完成，任务行按验收记录删除。

## 最终验收（2026-10-18）

完整构建和15项服务器测试通过；与另一项合并使用一个静音临时客户端，共34个场景、68张开关对照截图，全部通过。每项17场景覆盖正面、45度、侧面、背面、近远、MINIMAL、昼夜、雨天、迟到、资源重载、近裁面、时段边界、背向、区域外与不透明屋顶。全部联系表及重点完整画面已经人工检查。古阵另检查实际抬高草地与音频资源静默加载；银瀑相机进入主水幕后允许近面消失，24格近景必须可见。

每项3025帧正式几何检查通过；全局160目录项、15骨架/165动画状态、45地标模型及6绑定校验通过。音效未试听，未改变系统声音或亮度，也未关闭用户存档。单客户端与独立服务端验收不等于多人联机测试；奇观由正式ScenicEvents确定性触发，没有等待自然随机出现。失败轮次及测量修正保留在qa-corrections.md。

验收记录：[verification-20261018-silverfall-array.json](../../cod3/verification-20261018-silverfall-array.json)。两项最新包：`build/cod3-ancient-array-20261018/dynasty-1.4.0-cod3-silverfall-ancient-array.jar`。
