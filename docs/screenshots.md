# 截图与发布素材指南 / Screenshots & release assets

## 建议拍摄的截图（1920×1080，F1 隐藏 UI，可用光影/BSL 提升观感）

| # | 场景 | 拍摄要点 |
| - | --- | --- |
| 1 | **封面图** | 站在宫殿中轴御道上，正对太和殿与四座角楼，黄昏逆光 |
| 2 | 天朝·龙庭全景 | `/tp` 到 `examplemod:celestial_dynasty` 高地俯拍汉白玉大陆与碧海 |
| 3 | 玉林 / 龙脊山脉 | 展示自定义群系植被与天空色调 |
| 4 | 地府 | 黑石峭壁 + 岩浆海 + 幽冥荒原雾气 |
| 5 | 帝陵地宫 | 主墓室棺椁、金柱与宝箱 |
| 6 | 科举 GUI | 打开答题界面（含题干与三选项） |
| 7 | 王朝图鉴 GUI | 翻到“六、军队与阵型”页 |
| 8 | 军队列阵 | 用 `/dynasty army formation wedge 24`，从上方俯拍锋矢阵 |
| 9 | 龙帝 Boss 战 | Boss 血条 + 龙息火球 + 锦衣卫/弓兵混战 |
| 10 | 神兽 | 麒麟 / 凤凰 / 九尾狐合影（可用刷怪蛋） |
| 11 | 春节烟花 | `/dynasty festival spring` 后抓拍烟花与年兽 |
| 12 | 物品展示 | 创造模式物品栏里的王朝分页（药水、丹药、刷怪蛋、图鉴） |

## 拍摄辅助命令

```mcfunction
# 1) 前往天朝并寻找宫殿
/execute in examplemod:celestial_dynasty run locate structure examplemod:palace
/execute in examplemod:celestial_dynasty run tp @s <x> 120 <z>

# 2) 前往地府
/execute in examplemod:underworld run tp @s 0 90 0

# 3) 摆好姿势：列阵 + 召唤神兽
/dynasty army formation wedge 24
/summon examplemod:qilin ~3 ~ ~
/summon examplemod:phoenix ~-3 ~3 ~
/summon examplemod:nine_tailed_fox ~ ~ ~3

# 4) Boss 战演示
/summon examplemod:dragon_emperor ~ ~ ~-6

# 5) 节日烟花
/dynasty festival spring
/dynasty festival newyear
```

## 画质建议
* 光影：BSL / Complementary Reimagined（渲染距离 12+，云=关闭或精致）
* 视角：`F5` 第三人称 + `F1` 隐藏 UI；用旁观模式（`/gamemode spectator`）取景更稳定
* 时间：`/time set 5000`（晨光）或 `18000`（暮色）；天朝可用 `/time set 6000`

## 其他发布素材
* `logo.png`（jar 内已包含 512×512）：作为 CurseForge/Modrinth 项目头像
* `docs/curseforge.md` / `docs/modrinth.md`：页面文案（可直接粘贴）
* `README.md`：仓库首页说明
* `LICENSE`：All Rights Reserved
* 构建产物：`./gradlew build` → `build/libs/dynasty-1.0.0.jar`
