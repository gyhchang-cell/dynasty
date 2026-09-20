# Real Minecraft framebuffer smoke test

This opt-in harness launches an isolated Forge development client, waits for the main menu and resource loading, draws the production renderers into its own `TextureTarget`, checks OpenGL errors and non-background pixels, writes PNGs, and exits the test client. It never opens a world, touches player saves, captures the desktop, or controls an existing Minecraft process.

```sh
./gradlew --offline -I tools/art/runtime-qa/runtime-qa.init.gradle runClient
```

The client profile is `build/runtime-render-qa/client`; reports and sixteen framebuffers are in `build/runtime-render-qa/results`. A successful Gradle exit alone is **not** the assertion: read `PASS.txt` and ensure no `FAIL.txt`. Both completion markers are reset before each test run so old success cannot hide a startup failure. PNGs left by a failed run are not evidence of that run passing.

The extra `runtimeQa` source set is opt-in and separate from `main`. Its source is joined only to the development client's Dynasty mod source list. It is never added to `jar` or `reobfJar`. Compile-only integrations stay out of the runtime classpath; adding `main.compileClasspath` to the test runtime would incorrectly enable Curios's unmapped mixins in this workspace.

Covered paths:

- `ImperialMaterialShader` and glow registration through real Forge resource loading.
- Brocade resource loading, plus visual inspection of gold patterned cloth in the framebuffer.
- `HouyiAvatarRenderer.drawGuanYu` at four yaw angles, fully formed cached VBO, and 0.65/0.99 dynamic clipped formation.
- `ImperialDragonRenderer.draw` using both palette caches and 0.55 opacity.
- Actual `ShaderInstance.apply`, `BufferUploader.drawWithShader` and `VertexBuffer.drawWithShader` under Minecraft's OpenGL context.
- Qinglong seal at tick 13 (rising connections) and tick 26 (larger dragon descending): the test invokes the production geometry callback, camera-relative ribbon expansion, body draw and glow shader. Its deterministic target is a synthetic coordinate, not an entity. The two images exercise actual Minecraft GPU rendering without claiming world-event, target-binding or network synchronization coverage.
- A translucent quad drawn in front of the opaque guardian blends correctly; one drawn behind it is depth-occluded. The three center-pixel RGB channels are checked against the expected blend/background values. This simulates draw order and does **not** validate Forge's world event sequence.
- Asynchronous `Minecraft.reloadResourcePacks()` without blocking the render thread, followed by redraws of Guan Yu and both dragon palettes. The three reloaded images are compared pixel-by-pixel to the corresponding originals; maximum RGB deviation must be at most 1.

The source set uses the same package as the dragon renderer to exercise its package-private production entry point without changing production visibility. All assertions and offscreen cameras are in this test source set.

These PNGs are **actual Minecraft renderer framebuffer tests, not gameplay screenshots**. They test registration, materials and draw paths, not world-camera integration, modpack compatibility, frame rate, artistic fidelity, or complete animation collision safety. The isolated profile skips its first-launch accessibility introduction only to reach the menu; no user profile settings are changed.

Verified 2026-09-19 23:14 +0800 on Apple M4 Max with the final dragon clearance revision: fourteen frames nonempty; zero OpenGL errors; front/rear translucency assertions pass; all three resource-reload comparisons have maximum RGB delta 0; no world opened; automatic clean exit. Evidence is preserved in `docs/art/imperial-remaster/runtime/`.

Re-verified 2026-09-20 07:08 +0800 with the larger Qinglong seal/dragon sequence: sixteen frames pass, including `qinglong-cage-forming.png` (tick 13, 289,040 non-background pixels) and `qinglong-cage-dragon-descending.png` (tick 26, 119,876 pixels). The latter queues exactly one cached production dragon. Both use the registered glow shader; GL errors remain zero, and all three resource-reload comparisons remain pixel-identical. This run still opens no world and does not test server bindings or network cancellation.

The retry used `earlyWindowControl = false` in **only** `build/runtime-render-qa/client/config/fml.toml`, because Forge's optional early-loading window reported `glfwGetPrimaryMonitor failed` before Minecraft initialized. This test-profile-only workaround allowed the normal Minecraft OpenGL context to initialize. No operating-system display setting or user Minecraft profile was changed. On a fresh test profile, apply this isolated setting only if the same early-window failure occurs.
