# 六项美术测试失败核收

结论是六个旧断言都和当前资源合同不一致。修正输入合同后，六项隔离探针均通过。48 个带显式轮廓的物品模型通过原有侧面逐 texel 比对。本批保留源测试和运行美术，原始全量日志仍记录 176 项里有 6 项失败。隔离探针不代表全量已绿。

| 测试 | 现行依据与结论 |
|---|---|
| FeedbackTests.test_side_meshes_cover_only_real_silhouette_pixels | 首个失败为朱雀弓。朱雀弓和三帧的 PNG、JSON 均与 weapons-twenty-v5 交付哈希一致。父链为 solid_bow → solid_handheld，末端无 generated 父模型。只放开这条已发布的父链后，原测试继续按实际透明度重算 48 个模型的边缘，未发现缺边或在透明源像素上生成厚度。 |
| RealmArtTests.test_manifest_assets | 旧清单统一规定三组为 128×128 或 256×256。实际八张地表方块为 16×16 RGB，cube_all 各引用对应本地纹理，拼接预览可见各自材质。25 个武器里龙晶剑、巨阙、承影为发布过的 16×16 像素原稿，三套 PNG 与模型均匹配各自发布收据。现用三组文件相互独立、原清单的源文件仍可读取。八张地表图没有找到由旧 128 版切换为当前 16 版的单独选稿收据，因此它们的更换履历仍待补。 |
| RealmArtTests.test_new_bows_aim_forward_both_hands | 六把弓的三帧都走 solid_bow，保留显式正反面、三段覆盖和双方第一人称姿态。当前六套拉弓图均看见箭头朝左，按测试的 −X 合成旧版视角旋转，18 帧双手均过原方向阈值。实际握点、遮挡和左右手仍待实机。 |
| AccessoryExpansionTests.test_twenty_eight_unique_authored_sprites_with_backups | 香囊是本组唯一非 128×128 资源。原稿 1254×1254，运行图 1125×1226，主体裁框逐 RGBA 一致，四边各留 2px 真透明。现用 original_item 加载器，发布回执与现图哈希匹配。36 条素材按各自尺寸继续满足主体可见、透明边、原阈值的相对占比和不同图片要求。 |
| SchoolContractTests.test_bow_models_have_three_real_draw_stages_not_registered_items | 逐星弓保持三个动态覆盖，阈值 0、0.65、0.9。旧检查既要求原版拉弓父模型，也把箭头输入写成 +X。现用三帧实图都朝左，仅修改父模型预期会把朝向算反。改用 −X 后通过原先的双手角度阈值，实机仍待验。 |
| SchoolContractTests.test_fifteen_original_assets_are_128px_visible_and_distinct | 流云剑是已单独发布的 16×16 原稿，现用纹理和模型逐字节匹配 swords-distinct-v9。预览中剑钩和剑尾轮廓可辨。其余受测图片维持 128×128，全部可见且相互不同。 |

## 复核入口

在仓库根目录运行 PYTHONDONTWRITEBYTECODE=1 python3 docs/art/visual-test-audit-20261126/probe.py。它在内存中替换六项旧输入预期，保留原测试资源路径、箭向计算、轮廓匹配、透明边及相对面积的断言。地表与皮肤尺寸取现场冻结清单，只用于归因，不能由此推出新永久契约。release-and-alpha.json 保留每项当前 PNG 的 RGBA 哈希、尺寸、图像模式、边缘与原稿来源，以及可证明的发布匹配。

已目视三份分析页。历史日志、原稿、玩家实例和共享包均未修改，未启动游戏。先前五套盔甲的制作准入和实机验证继续独立保留。待主协调将可证明的父链、箭向和原稿尺寸写入常规测试；地表图的切换批准与真机画面另行验收。
