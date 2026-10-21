# 基础兵器加粗、猎弓与石戈重做

2026-10-15。用户明确纠正为“加粗”，授权参考后制作并自查返修。打开index.html可查看五件新旧稿和同尺寸缩略对照。

## 参考

references-300.json记录100份弓、100份镰刀（包括短镰）、100份非常规近战贴图：来源压缩包、内部路径、尺寸和SHA256齐全。三类共300个不同文件哈希。包含材质变体，不宣称300种独立轮廓。已逐页实际查看联系表，发现并排除数字编号的拉弦帧、光照层、弓模板、bowcaster、冰弓分层与同一武器展开/图标重复。

来源含本机涟漪之篇、愚者chishi、神话：起源等实例的只读模组资源，以及官方仓库。主要参考：[Spartan Weaponry](https://github.com/ObliviousSpartan/SpartanWeaponry)、[Simply Swords](https://github.com/Sweenus/SimplySwords)、[Epic Knights](https://github.com/Magistu/Epic-Knights)、[DivineRPG](https://github.com/DivineRPG/DivineRPG)、[Mystic Bows](https://github.com/Desoroxxx/Mystic-Bows)、[More Bows](https://github.com/NeRdTheNed/More-bows)、[Maulve's Scythes](https://github.com/Maulve/maulves-scythes)。本机其他来源以清单内原始路径为准。不修改其他整合包，不把它们贴图装入Dynasty。

弓参考观察：原版式斜向轮廓更适合槽位，弓臂和握把应有明确粗细差，弦不能与弓身同粗。镰刀参考观察：连接点决定横刃可信度，杆下方负形区帮助识别；仅借鉴连接关系，不把石戈改成镰刀。非常规兵器观察：战镰、钩枪、双头刃、叉与环刃的辨识依赖轮廓，不能通过换色假装类型不同。

## 已生成及自查返修

- 猎弓V2：重做斜向弓形，加厚木质弓臂与握把，弦保持细于木臂；连接两端，保留弓内空隙。
- 铜刀V2：握柄和刀身加宽，保留红铜与单侧刃口。
- 铁剑V2：柄身加厚，保留双刃、剑脊、小护手。尖端仍较方，需要最终像素稿进一步处理。
- 环首刀V2：加宽柄身和单刃，保留可辨识环孔。
- 石戈V2自查：接头明显弯折、纹理碎；V3减轻碎纹并尖化，但仍有弯折，未当成修复完成；V4改直杆横刃解决结构弯折，明显区别先前石斧式宽头，作为结构候选保存。V4较简，需要用户对该形制的视觉反馈。

所有图片用内置image_gen生成，完整提示词见prompts.json。读取像素数据做握柄横截面对照，见grip-comparison.json；这只是图稿近似测量，不是游戏模型尺寸。

## 验收边界

五件都是审阅图。review.json真实记录尺寸与颜色数：生成图仍非原生16×16四色贴图，并带微小色差，不能称作贴图规范全部通过。未安装游戏、未修改模型/贴图运行资源、未启动Java、未改声音亮度、未接触士兵实体或天子剑等精修物品。未删除任务清单。待审阅风格及制作符合像素约束的正式资源后，才进行UV、弓动作与握持验证。
