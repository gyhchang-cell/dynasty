# 真实开发客户端离屏渲染验证

这些 PNG 是 Minecraft 1.20.1 / Forge 47.4.10 **真实客户端、生产 shader 和生产 VBO 渲染器**写入测试 framebuffer 的结果。它们不是 AI 效果图、不是桌面截图，也不是进入世界后的游戏截图。

最终验证：2026-09-19 23:14（UTC+8），Apple M4 Max。14 帧全部非空，OpenGL 错误 0，测试客户端自动退出，始终没有打开存档。完整断言见 `PASS.txt`，实际启动日志见 `client-qa.txt`。

- `guanyu-front/angle/side/back`：四个角度，生产静态 VBO，可见真实衣料金纹贴图。
- `guanyu-forming/nearly-formed`：0.65 / 0.99 形成进度，生产动态裁剪路径。
- `jade-dragon/gold-dragon/jade-dragon-forming`：两个配色缓存与半形成透明度。
- `guanyu-translucent-front/behind`：模拟前后透明物体，前景 RGB 混合、后景深度遮挡断言均通过。
- `*-after-reload`：真正异步重新加载资源后，VBO 失效重建；关羽、青龙、金龙与重载前的逐像素 RGB 最大差均为 0。

透明测试仅证明实际 depth/blend 正确，**不证明 Forge 世界渲染事件的调用顺序**。此测试也不证明电影级美术、整合包兼容性、游戏帧率或全部动画绝无穿插。

测试代码位于 `tools/art/runtime-qa/` 的独立 sourceSet，未加入 main、jar 或 reobfJar。隔离测试配置关闭了 Forge 可选的 early loading window，以绕过其 `glfwGetPrimaryMonitor failed` 启动问题；未更改系统显示设置或用户 Minecraft 配置。

本次生产文件 SHA-256：

```text
ImperialWeaponRenderer.java f82bfa5ea1c4b603ca91488836833400efe3dfa0f4fa71ba752e38e45ec4b4d1
ImperialDragonRenderer.java e3e44bf633d29cb0b5c5d5e1f940913c3bd13c44146c548fa170ae1c87956c51
HouyiAvatarRenderer.java a89885918ff2b4136e93f5324bba552f9e8214552f90d49801c5adbd796ad636
imperial_material.fsh a1796917af87570b235414cc512dd007b268846e0da5b0a3c5f029357f9b662b
```
