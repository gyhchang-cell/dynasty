# 破军战斧 v12

现有物品 `pojun_axe`，没有增加注册 ID。大刃面斧头，短尾榫，斜向木柄；16×16透明PNG，像素源见 pixel-source.json。检查放大、16/32/48px小图及黑剪影；上半8行实体像素40→62，斧柄与斧头连通，无半透明像素。

用户认可的其余8件（17PNG，含拉弓阶段）按原稿逐字节安装，未再改设计。品质框依然只是UI方案，没有改Rarity和战斗属性。

## 参考事实

扫描本地登神等整合包，以及缓存的 SimplySwords、SpartanWeaponry、Epic Knights、DivineRPG 官方源码。550个RGBA去重候选实际查看了6张联系表；剔除28个部件、蒙版、食物和空槽后保留522张，覆盖71个非原版模组命名空间。包括材质和版本变体，不能称为522种剑形或独立设计。100个模组/1000把斧的数量目标尚未达到，未声称已完成。路径与像素哈希见 reviewed-references.json。

重点参考：Twilight Forest 牛头人斧的宽刃面、Spartan Weaponry 战斧头柄分量、Simply Swords 的长柄与斧头连接；不直接复制其贴图。

官方网页补充：
- https://github.com/Sweenus/SimplySwords
- https://modrinth.com/mod/spartan-weaponry
- https://www.curseforge.com/minecraft/mc-mods/fancy-battleaxes

## 验证边界

源资源、模型边缘网格、弓三段谓词和本地JAR/导出资源逐项核对。未启动Java、未真实游戏验收、未推送GitHub、未改声音亮度存档。同步中检测到一个导出文件被其他工作更新，拒绝覆盖后重新读取当前版本，仅在目标资源符合原稿/新稿哈希时合并。见 deployment.json。
