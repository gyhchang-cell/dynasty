# 其他贴图范围只读核查

共核查 63 张现有 PNG：实体21、状态图标7、特效材质1、槽位1、任务UI32、主菜单1。**本核查没有绘图或修改源文件。**

结论：已有明确美术交付 14 张；另有任务UI交付 32 张；其余 17 张保留为完成状态不明。缺少专属交付记录不等于占位/未完成，不能据此覆盖。

任务UI32张的交付文档实际位于 `docs/quests-remaster/`，不是 `docs/art/`。关羽织锦与主菜单背景分别与保留原稿SHA-256完全一致；其余以明确目标路径、当前资源规格及交付记录建立保护，未声称复核了原交付最终文件hash。

本页所有路径相对 `/Users/a15356015027/Desktop/dynasty`。逐文件完整hash、初始范围hash、生成输出匹配与证据见 `other-texture-scope.json`。

| 当前资源 | 分辨率 | 处理 | 具体交付/来源文件 |
| --- | --- | --- | --- |
| `src/main/resources/assets/dynasty/textures/entity/archer.png` | 64×64 | 保留：美术完成状态不明 | `tools/art/gen_entities_humanoid.py` |
| `src/main/resources/assets/dynasty/textures/entity/assassin.png` | 64×64 | 保留：美术完成状态不明 | `tools/art/gen_entities_humanoid.py` |
| `src/main/resources/assets/dynasty/textures/entity/dragon_emperor.png` | 256×256 | 保护：已有美术交付 | `docs/art/boss-trinket-remaster-v1/README.md:8`<br>`docs/art/boss-trinket-remaster-v1/image-prompts.md` |
| `src/main/resources/assets/dynasty/textures/entity/dragon_king.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/entity/eunuch_mastermind.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/entity/imperial_soldier.png` | 64×64 | 保留：美术完成状态不明 | `tools/art/gen_entities_humanoid.py` |
| `src/main/resources/assets/dynasty/textures/entity/jade_guard.png` | 256×256 | 保护：已有美术交付 | `docs/art/boss-trinket-remaster-v1/README.md:8`<br>`docs/art/boss-trinket-remaster-v1/image-prompts.md` |
| `src/main/resources/assets/dynasty/textures/entity/merfolk.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/entity/minister.png` | 64×64 | 保留：美术完成状态不明 | `tools/art/gen_entities_humanoid.py` |
| `src/main/resources/assets/dynasty/textures/entity/nian_beast.png` | 128×128 | 保留：美术完成状态不明 | `tools/art/gen_beast_nian.py` |
| `src/main/resources/assets/dynasty/textures/entity/nine_heaven_general.png` | 256×256 | 保护：已有美术交付 | `docs/art/boss-trinket-remaster-v1/README.md:8`<br>`docs/art/boss-trinket-remaster-v1/image-prompts.md` |
| `src/main/resources/assets/dynasty/textures/entity/nine_tailed_fox.png` | 128×128 | 保留：美术完成状态不明 | `tools/art/gen_beast_fox.py` |
| `src/main/resources/assets/dynasty/textures/entity/phoenix.png` | 128×128 | 保留：美术完成状态不明 | `tools/art/gen_beast_phoenix.py` |
| `src/main/resources/assets/dynasty/textures/entity/qilin.png` | 128×128 | 保留：美术完成状态不明 | `tools/art/gen_beast_qilin.py` |
| `src/main/resources/assets/dynasty/textures/entity/rebel_general.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/entity/rebel_soldier.png` | 64×64 | 保留：美术完成状态不明 | `tools/art/gen_entities_humanoid.py` |
| `src/main/resources/assets/dynasty/textures/entity/royal_guard.png` | 128×128 | 保护：已有美术交付 | `docs/art/entity-batch-01/README.md:5`<br>`docs/art/entity-batch-01/prompts.json` |
| `src/main/resources/assets/dynasty/textures/entity/soul_soldier.png` | 256×256 | 保护：已有美术交付 | `docs/art/boss-trinket-remaster-v1/README.md:8`<br>`docs/art/boss-trinket-remaster-v1/image-prompts.md` |
| `src/main/resources/assets/dynasty/textures/entity/terracotta_warrior.png` | 128×128 | 保护：已有美术交付 | `docs/art/entity-batch-01/README.md:5`<br>`docs/art/entity-batch-01/prompts.json` |
| `src/main/resources/assets/dynasty/textures/entity/thunder_envoy.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/entity/undead_first_emperor.png` | 256×256 | 保护：已有美术交付 | `docs/art/realm-remaster-v4/DELIVERY.md:24`<br>`docs/art/realm-remaster-v4/skins.json` |
| `src/main/resources/assets/dynasty/textures/mob_effect/dragon_might.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/internal_injury.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/intimidation.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/iron_wall.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/loyalty.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/mandate_of_heaven.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/mob_effect/swift_wind.png` | 18×18 | 保留：美术完成状态不明 | `tools/art/gen_effects.py` |
| `src/main/resources/assets/dynasty/textures/effect/guanyu_brocade.png` | 1254×1254 | 保护：已有美术交付 | `docs/art/imperial-remaster/README.md:19`<br>`docs/art/imperial-remaster/image-prompts.md:5` |
| `src/main/resources/assets/dynasty/textures/slot/empty_trinket_slot.png` | 16×16 | 保留：美术完成状态不明 | `docs/更新日志-1.4.0.md:675`<br>`docs/更新日志-1.4.0.md:871`<br>`tools/art/gen_dynasty3.py:512` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_archer.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_catalog.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_guard.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_home.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_sword.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/backdrop_talisman.png` | 1024×1024 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_archer.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_guard.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_stage_0.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_stage_1.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_stage_2.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_stage_3.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_sword.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/card_talisman.png` | 1024×268 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_archer.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_back.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_belt.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_body.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_bracelet.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_charm.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_guard.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_hands.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_head.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_home.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_necklace.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_ring.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_sword.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/title_talisman.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/volume_0.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/volume_1.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/volume_2.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/quests/volume_3.png` | 1024×144 | 保护：已有UI交付 | `docs/quests-remaster/流派任务与图鉴布局.md:39`<br>`docs/quests-remaster/流派任务与图鉴布局.md:41`<br>`tools/art/QuestAtlasArt.java:72` |
| `src/main/resources/assets/dynasty/textures/gui/title/imperial-dawn.png` | 1672×941 | 保护：已有美术交付 | `docs/art/schools-remaster-v1/final-assets.json:3`<br>`docs/content/王朝主菜单-使用与验证.md:12`<br>`docs/content/王朝主菜单-使用与验证.md:24` |

## 不得扩大完成声明

本轮盔甲完成范围仍是本任务的11套候选。不能写“项目所有贴图已完成”：9张实体、7张状态图标和1张槽位图标的专属美术验收尚不明确；同时已交付的实体、关羽材质、任务UI和菜单背景需保护。实体或特效若后续要重制，必须先以各自实际模型/UV和既有任务边界独立评估。
