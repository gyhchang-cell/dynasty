# 剩余盔甲 A 组 · 原生像素候选

已完成11套：`cloth`、`bamboo`、`leather`、`brocade`、`silver`、`cinnabar`、`dragon_scale`、`sea_silk`、`phoenix`、`qilin`、`draco_king`。每套4件平面图标与2张人体展开图，共 **44张32×32图标、22张64×32穿戴图**。全部只写在本目录，未安装、未修改任何src文件、公共代码、模型、实例或存档。

用户已确认玄铁胸甲方向并授权剩余套批量；先交龙鳞套，主任务已实际查看龙鳞图标与穿戴页及全部11套总览。没有绘制将军、玉、天界、青铜、玄天等受保护套装。

## 设计与范围

所有图案在目标像素网格内直接绘制，透明度只有0/255；没有高分辨率生成后缩小、抗锯齿、平滑渐变、随机噪声或动画。各文件5—10个实际可见颜色，以大色块和明确接缝表达材料。32×32延续这些装备已有的物品资源规格，用于开放领口、双腿轮廓、独立肩片和局部扣饰；普通方块16×16要求不由此改变。

布衣交领与缠带、竹甲竖片扎绳、皮甲斜背带、织锦交领团花、白银中脊板甲、朱砂符纸护带、龙鳞错层鳞片、鲛绡波褶、凤凰V形羽片、麒麟大菱鳞、龙王倒V厚甲分别采用独立结构。静态检查将颜色标准化后逐像素比较，各相同装备部位均无“同图换色”副本。

穿戴图是单独绘制的人体UV，未把物品图标映射到角色。头盔保留20—30个逻辑像素的正面开口，额外hat岛全透明。layer_1用于头盔、胸甲和靴子，layer_2用于护腿；双臂与双腿共享标准镜像UV。普通人形立方体尺寸、outer=1.0、inner=0.5、leg额外−0.1保持标准。图标上的冠沿、角形纹样及肩片是平面图案，**没有新增穿戴角、羽翼或肩甲模型**。无新增发光材质或着色器。

## 资源关系

每套均为 `dynasty:<set>_<helmet|chestplate|leggings|boots>`；现有 `models/item/<ID>.json` 继续使用 `minecraft:item/generated` 或等价的 `item/generated`，其 `layer0` 为 `dynasty:item/<ID>`，无需修改引用。

候选位于 `candidate/assets/dynasty/textures/item/` 与 `candidate/assets/dynasty/textures/models/armor/`。对应源目标路径、逐文件尺寸、颜色数及SHA-256均列于 `manifest.json` 和 `qa/static-qa.json`。`before/` 保存66张旧PNG及44个物品模型，共110项备份，均与源文件hash保持一致。

## 预览与检查

- `previews/all-icons.png`：全部44图标。
- `previews/all-worn.png`、`previews/all-front-back.png`：11套斜视及正背面总览。
- `previews/<set>-icons.png`：原图与候选、原尺寸、最近邻放大和16px物品栏显示。
- `previews/<set>-worn.png`：原图与候选，标准人体正面、背面、斜视；中性假人，空手。
- `qa/static-qa.json`：66张尺寸/alpha、44条模型引用、头部开口、未使用UV透明、110项源hash、非换色副本检查通过。
- `qa/worn-qa.json`：本机Forge源码来源、镜像与几何说明。

已实际查看原尺寸与最近邻图标、11套正背面及斜视离线预览。离线渲染仅验证纹理与UV观感，**不是游戏截图，未游戏内实测**；不声称完成实际光照、动作或光影模组兼容验证。

复现命令（在本目录内）：

```sh
python3 build_armor.py
python3 qa/render_armor.py --sets cloth bamboo leather brocade silver cinnabar dragon_scale sea_silk phoenix qilin draco_king
python3 qa/audit.py
```

## 额外只读范围核查

`other-texture-scope.json` / `.md`逐项记录另外63张实体、状态、特效、槽位、任务UI与菜单图片。46张有明确既有交付记录需保护；另17张美术完成状态不明，不能据缺记录视为占位并擅自重画。此核查没有新增或修改这63张中的任何一张，也不能用于宣称“项目所有贴图完成”。
