本轮用户要求：原稿用于实际运行贴图，不缩成16px；追加三批各两件简陋饰品；精细老饰品不动；最后提供灰底带中文名总览。

原稿策略：完整原稿存sources或canonical manifest指定路径。初次将153张原画布逐字节复制后，真实Minecraft Stitcher在16384限制下失败（atlas-check.log）。仅裁掉透明外边距、加2px透明保护边后通过（atlas-trimmed.log）。主体RGBA逐像素保留，无缩放、量化、损失透明度或有损压缩。原画布仍原样保存；运行PNG是保留同等主体像素的紧边版本。

新增选题：玉扳指/玉带钩；书箱坠/墨玉印坠；镇海锚坠/潮信坠。生成工具：内置imagegen；完整prompt保存selection.json。保护基线baseline.json，修改前备份before。

验证：originals.py比对原稿主体像素、模型引用、构建jar内实际文件和未选中素材哈希。总览从运行目录读取，不是游戏截图。图集检查仅覆盖本项目与原版物品/方块，不代表其他模组图集或GPU实际运行通过。未开启、关闭或重启用户游戏；存档、声音、亮度未操作。未推送GitHub，未改整合包导出配置或格式。

结果：159张（56饰品、103材料）原稿主体像素与jar一致；447张未选中物品贴图哈希保持原样。Gradle build成功。2162张本项目+原版贴图通过16384×16384 mip0 CPU排布。尚未进行GPU/完整整合包实机验收，不能据此承诺低显存设备或其他模组叠加情况下可运行。

生成共同要求：single original Minecraft mod inventory accessory sprite; richly crafted crisp pixel art, stepped pixel clusters, discrete shaded material colors, dark outline, large readable silhouette, no smooth cartoon vector/blur/photographic lighting/text/glow; single centered item on genuine transparent background; detailed original, not reduced16x16。各物件描述见selection.json。
