# Dynasty title screen QA

Run from the project root after installing `imperial-dawn.png` and merging the isolated language additions:

```sh
python3 tools/art/gen_title_lang.py
python3 tools/art/gen_title_lang.py --check
./gradlew --offline -I tools/art/title-qa/title-qa.init.gradle runClient
```

This separate source set starts an isolated development client in `build/title-screen-qa/client`. It switches this client's in-memory language to Simplified Chinese with a normal asynchronous resource reload. It never enters a world, joins a server, edits launcher settings or includes its QA class in the production mod jar. Do not combine this init script with the other runtime screenshot init script.

Check `build/title-screen-qa/results/PASS.txt` and ensure there is no `FAIL.txt`; a normal process exit alone does not mean the assertions passed. Old completion markers are reset before each run. The five `title-*.png` files are actual Minecraft framebuffer captures at several logical UI sizes and output pixel scales, including 320×240 and 16:10. Inspect all five for clipping, readable text and composition. These controlled framebuffer captures do not claim to test OS window management or performance.

The checks verify all original Minecraft/Forge action keys, disabled state and tooltip delegation, fitting/non-overlapping controls, Tab access, Enter activation, real screen transitions and Escape returns, and the F6 vanilla fallback. The actual Quit button stops the client only after the other assertions. Realms is retained but not activated to avoid entering its online service. The multiplayer path opens only its original warning or server-list screen; the isolated profile has no saved servers. Singleplayer normally opens Create World in this empty profile, matching vanilla's automatic first-world redirect; QA cancels that screen without creating or entering a world.

The background's true pixel dimensions are decoded after resource loading; no resizing is required. The artwork is packaged locally and never downloaded at runtime. Hold Shift while opening the menu, press F6 on the themed menu, or use `-Ddynasty.vanillaMenu=true` to use the original presentation. Ordinary navigation and permissions still belong to the vanilla buttons.

If Forge's optional early window fails with `glfwGetPrimaryMonitor failed`, use `earlyWindowControl = false` only in this test profile's `build/title-screen-qa/client/config/fml.toml`, as with the existing renderer QA profile. This is a test profile workaround, not a change to the user's game.
