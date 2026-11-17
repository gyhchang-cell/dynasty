# 十二件旧武器与工具重做 v21

用户要求增加本轮数量，同时继续处理既有简陋资源。实际审看119张尚未纳入统一原稿链的非盔甲物品（audit-0.png / audit-1.png），保护精致早期饰品和已获认可的武器；选择当前仍是早期32px简图/复用外形的12件，未因不在清单就一律重画。

| 资源 | 获取/定位 | 新稿识别 |
| --- | --- | --- |
| tong_dao 铜刀 | 前期COPPER；当前配方石戈+3铜锭 | 大色块铜单刃、木柄，保持原版式简朴轮廓 |
| huan_shou_dao 环首刀 | BRONZE前中期 | 钢单刃、开孔环首、朴素柄 |
| zhanma_dao 斩马刀 | 环首刀+3精钢 | 长双手柄、重刃、银色切削边 |
| gilded_mace 御赐金锏 | JADE官阶御赐装备 | 方棱钝锏、加固箍、红缠柄，不做剑尖 |
| dragon_spear 龙胆亮银枪 | DRAGON_CRYSTAL名将装备 | 亮银长杆、细长枪刃与蓝缨 |
| dragon_slayer 屠龙刀 | 龙晶剑+龙宫玉印+龙帝玉玺 | 宽厚黑钢单刃与双手柄 |
| bawang_spear 霸王枪 | DRAGON_CRYSTAL高阶长柄 | 宽菱形枪刃、短倒钩、黑杆红缠柄 |
| halberd_fangtian 方天画戟 | 破军斧+龙晶剑+龙鳞+帝骨+图纸 | 中央枪尖与双侧月牙刃 |
| qilin_war_axe 麒麟战斧 | 麒麟角+精钢+图纸 | 玉绿大斧面、宽银刃与短后突 |
| baihu_glaive 白虎戟 | 白虎牙+精钢+图纸 | 单侧虎牙刃、后钩、银白虎纹 |
| yu_di 玉笛 | FluteItem；玉材料阶段、范围削弱 | 玉笛音孔、吹孔、端箍与短红穗 |
| pickaxe_dragon_crystal 龙晶镐 | 玉镐+2龙晶+精钢+帝骨 | 双端晶镐头、钢套筒和木柄 |

具体配方快照在 recipe-evidence.json。分期依据真实注册tier、构造参数和当前配方；代码历史伤害注释有与参数不一致处，本轮不修改数值，不把这些注释当作实测伤害。

内置 imagegen 每件单独生成，完整原稿在 sources/，提示词与来源在 selection.json。采用此前用户认可 v19/v20 的像素材质方向，前期保持大色块简朴结构，高阶靠独特刃形与材料识别。没有声称本轮重新审看1000张新参考图。实际审图检查12件轮廓、环孔/戟间隙/音孔、32px缩略和原稿边缘，所有原稿画布边界均无 alpha>=128 的实体截断。

发布：统一 install.py 原稿链；运行PNG只裁透明外边和补2px，原稿主体RGBA精确保留，无降采样、减色。使用现有 original_item 加载器按新轮廓生成侧边，左右手变换统一到 solid_handheld。环首刀和玉笛旧模型使用 item/generated，本轮修正为合适的手持变换。保持注册ID、任务、配方、AI、伤害与存档。

comparison.png 每4件一组，上旧下新，均来自实际运行资源，缩略仅作展示。after.png 为新稿总览；inventory-32px.png 为32px物品格审查图，均非游戏截图。native.log、review.json、DELIVERY.json、installed-readback.json 记录原生PNG/侧面/UV/图集检查及本地实例和现有导出文件逐项校验。备份在 before/ 和 deployment-before/。

未启动、重启或关闭客户端，未动声音亮度与存档。真实世界持握与光影画面尚待实机验收；本轮无图形测试不替代实机。未推送GitHub。
