# 麒麟、鸿蒙八件盔甲图标返修

用户于2026-10-22明确否定v22盔甲插画造型，要求以Minecraft盔甲贴图为基础，参考大量其他模组后重做这八件。此次范围是麒麟鳞甲、鸿蒙帝铠的物品栏图标，不是新增套装或穿戴模型。玉如意、朱雀羽扇和其他精致资产不在范围。

## 参考与设计

从本机整合包JAR读取、按文件SHA256去重整理1000张盔甲相关图标，来源74个namespace，实际查看research/page-01至10，保留索引research/index.json。包含少量盔甲槽占位图等关联图，并非1000件完整套装或1000个整合包，也不声称每张均优质。另直接解包并查看原版铁甲、钻石甲、下界合金甲，见research/vanilla.png。检索核对项目来源为[暮色森林](https://github.com/TeamTwilight/twilightforest)、[Botania](https://github.com/VazkiiMods/Botania)、[Mekanism](https://github.com/mekanism/Mekanism)。他人图仅作结构与像素语言参考，不拷入运行资源。

去掉v22长筒靴、大肩甲、密鳞片和展示插画体积：以短宽胸甲、清晰领口、阶梯盔顶、直腿和外撇短靴为主要轮廓，金边克制、材质靠大像素簇区分。麒麟为青绿、暗绿与旧金；鸿蒙为靛紫、钢灰与旧金。每件独立调用内置imagegen，使用原版对应部件放大图作为比例参考；最终完整提示词和生成路径见selection.json，八张原稿见sources/。未将大图压成16/32px或量化。仅裁透明外框，保留正方形比例并补2px透明边，主体RGBA精确不变。

## 加载与修改边界

保留dynasty:original_item加载器和原显示变换。统一发布脚本增加本批覆盖记录，并使已有ids参数真正限制PNG/模型写入范围；其余成品不重新发布。install.py提供当前批可复现接入。规范中旧install入口在本轮开始时一度缺失，共享仓库随后同步回原稿与工具链；安装前逐像素确认八件恢复内容恰为v22旧稿，再保存before-restored-v22和新baseline。最初32px检查备份和baseline-pre-sync仍保留，不抹去同步历史。

不修改注册、属性、配方、战斗、NPC或装备穿戴UV。并行生物任务的凤凰与基础九尾狐模型/实体UV均不在范围；其手持挂点若后续需要物品，另按实际请求处理。

## 验证与交付

source-check.json验证只改变8张PNG，1100张其他PNG与原模型保持；native.log是真实Minecraft NativeImage/ItemModelGenerator/图集Codec无窗口验证，8张通过、13707个侧面，不能视作实机画面验收。comparison.png每组上旧下新，after.png为新版，inventory-32px.png为缩略检查，均非游戏截图。

publish_local.py对每个现有JAR分别只补丁17项资源（8PNG、8原模型、图集配置），现有导出包仅更改内嵌本模组JAR，不覆盖其他模组、任务或清单。自动保存旧载荷、检查ZIP CRC、并发SHA与所有未选条目不变；DELIVERY.json记录实际完成目标，verify_deployment.py再回读核对。没有启动、关闭、重启游戏或操作声音、亮度、存档；未推送GitHub。真实客户端新画面仍待验。
