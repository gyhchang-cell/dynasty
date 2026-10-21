本轮：6件粗糙饰品+4种名称/外形不符材料。精细徽墨、竹简及其他未选中资源保留。
使用内置imagegen生成，prompt和输出来源见selection.json；来源用途核对见material-usage.json。原稿存sources，生产资源只裁透明外边距补2px，主体不重采样、不减色。
丝绸首次原稿对比度偏低，经再次生成加强折痕与轮廓，拒绝稿另存。总览来自实际运行资源，非游戏截图。
未运行游戏、不操作用户存档/声音/亮度、不推送、不修改导出格式。

加载修复：10张新增原稿直接拼图会令Minecraft 16384图集排布失败。增加assets/minecraft/atlases/blocks.json，精确过滤这10个完整sprite并使用原版unstitch切成256以内的小区域，原PNG保留主体全部像素；显式item模型按相同坐标还原正背面与1模型单位的alpha轮廓侧边。不是降低图片分辨率，不修改Java逻辑。仅影响本批10个物品；其他原稿和精细老饰品不修改。
复验：真实Minecraft atlas codec/BlockModel解析；2402 sprites的16384×16384 CPU排布通过；check_tiles.py逐像素重组与几何UV检查、jar图集一致性；originals.py原稿主体/JAR一致性。全整合包GPU及实机仍未测试。
