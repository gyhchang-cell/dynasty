# 鸿蒙帝铠：原版轮廓上的高阶创意

用户认可v23，要求仅增强下排鸿蒙的创意。麒麟四件保持v23，穿戴UV和装备数值不改。本批只替换鸿蒙头盔、胸甲、护腿、靴子的物品栏图标。

## 设计与参考

阶梯短冠、金框星核胸甲、分叉金边护腿、外侧短翼靴共用靛紫、钢灰、古金与小块青白嵌片。保留Minecraft物品图标的粗方格、紧凑轮廓及小尺寸可辨性。

研究记录在research：本地模组JAR内去重后选取1000张盔甲相关图标，十页接触表均已查看；筛选来源共1790张候选，包含部分同族变体，并非1000套不同整合包或1000套独立设计。另实际查看Goety: Revelation神灵金Apocalyptium四件图标，学习轮廓与色块组织，没有复制其像素。官方项目版本资料：https://www.curseforge.com/minecraft/mc-mods/goety-revelation/files/6478302 、https://modrinth.com/mod/goety-revelation/version/2.3.4fix2 。

## 原稿与接入

使用内置imagegen编辑获认可的v23自有原稿，参考原版下界合金轮廓。四条完整提示词及原始输出路径见selection.json，生成原稿在sources。实际资源仅裁透明外边距、补2px透明边；不缩成16px、不量化，主体RGBA逐像素保留。comparison.png上旧下新；inventory-32px.png仅供检查小尺寸辨识度，均非游戏截图。

install.py通过统一publish_originals接入最新版本；旧批次保留原档。本地JAR和三种既有导出由publish_local.py逐包仅补丁9个指定资源项，其余文件负载逐项哈希保护，不重建或更换其他模组、配置和类。覆盖旧文件先备份于deployment-before。

## 验证与边界

native.log是Minecraft NativeImage、ItemModelGenerator挤出和图集codec的无窗口检查；source-check.json核对原稿及其他源PNG；DELIVERY.json和installed-readback.json记录各本地JAR/导出实际回读。未启动游戏，未做实机画面验收；不操作存档、声音、亮度和现有客户端。最终结果见final-check.json。
