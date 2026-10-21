# 铜刀样稿与500件武器参考

2026-10-15。当前为用户确认风格的单件样稿；没有替换运行资源，没有启动Java，没有修改天子剑、士兵内嵌武器、玩法或任务。

## 参考范围

实际打开十张每张50项的联系表：Spartan Weaponry 250、Epic Knights 180、Simply Swords 70。500个贴图哈希不同，逐项路径与哈希见 references-500.json。包括不同材质武器和三维武器UV图集，不等于500种轮廓，更不等于500个整合包。

官方来源：[Spartan Weaponry](https://github.com/ObliviousSpartan/SpartanWeaponry)、[Epic Knights](https://github.com/Magistu/Epic-Knights)、[Simply Swords](https://github.com/Sweenus/SimplySwords)。使用各仓库此次下载的默认分支，见sources.json；不是声称检查了各整合包特定发行版本。RLCraft武器来源关系参照[其Spartan Weaponry页面](https://rlcraft.wiki.gg/wiki/Spartan_Weaponry)。参考原图仅在本机临时研究目录，不加入运行包、不复制为原创资源。

## 实际观察

- 表1–5：Spartan的短刀、军刀、武士刀由刃宽、护手与柄比例区分；铜偏红，青铜偏黄。各材质沿用轮廓，不能把数量当成形状多样性。长枪与细剑在小槽位偏细，不用于这把基础铜刀。
- 表6–8：Epic Knights的短剑宽厚、刺剑窄长；波刃剑依靠阶梯边缘区分。骑枪、重钉锤、晨星贴图是展开图，仅观察色阶和分区，不当作完整轮廓预览。
- 表9–10：Simply Swords的弯刀尖端上挑，单侧亮刃和深色握柄清楚；双头刃、战刃和巨斧有不同重量分布。巨锤是UV图集。符文级高亮不适合低阶铜刀。

## 铜刀方案与限制

短木柄、小护手、单侧刃面、略上挑刀尖；克制红铜配色，不加宝石、金饰、发光。使用内置image_gen两次生成，首轮完整提示见generation-prompt.txt，第二轮强调16格和纯色扁平化。

tong_dao-review-v2.png为当前样稿。生成器仍保留微小色差，输出也不是原生16×16；因此明确不作为已经合格的四色游戏贴图、不覆盖正式铜刀。review.json记录真实尺寸与颜色数。现有铜刀模型含按旧轮廓生成的侧边面，未来换正式轮廓需同步核对侧边与透明遮罩，不能简单换PNG便声称手持正确。

正式资源的像素约束、UV及手持验收尚未完成；先由用户查看铜刀方向，再批量推进其他基础兵器。任务清单未删条目。
