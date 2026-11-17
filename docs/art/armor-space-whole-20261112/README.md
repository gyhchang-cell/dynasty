# D52：Ad Astra 基础太空服整套来源核对

仅本地参考研究，未制作或覆盖 Dynasty 贴图。研究对象是原生四件基础太空服，不把四个部位、十三个长方体、七十八个 UV 面或升级配色拆成多个设计。当前新增候选整套为 1；新增已验收独立设计信用为 0。适用1000参考仍未核定完成，全球已验证适用总数与确切缺口均为 null，保留历史参考，不将654名称/640盔甲名称/215学习组当作有效总数。

## 固定来源与范围

官方仓库 https://github.com/terrarium-earth/Ad-Astra ，1.20.1 分支固定提交 `5a986665e1d91e31c50321ff225a3fb23558ff35`。保留固定源码ZIP、34个选取条目的逐项SHA、原生四图标和64×64穿戴图。`gradle.properties` 为1.15.21、Minecraft1.20.1，Forge/Fabric双平台。没有运行外部项目代码或构建脚本。源码许可证保留在 source/LICENSE；只学习方法，不向 Dynasty 复制外部像素或几何。

## 实际看图与可借鉴点

已查看 `native-source-images.png` 中五张原生PNG的整数最近邻展示，以及 `raw-uv-crops.png` 的13方块、78个原始UV面裁片。这些是源码图分析，不是游戏截图，也不是穿戴姿态验收。运行原图未缩放或减色；分析页不作为新贴图交付。

- 胸甲图标采用短宽躯干、两段式浅色胸腹块、紫灰关节和袖口。材质靠连续大块分离，不靠密线条雕花；可学习浅色主体与深色接缝的对比。
- 腿甲腰带为完整深色横条，中间保留裆部负形；浅色胫部与暗色侧边分开，避免整条腿糊成同色板。
- 靴子是两只明确分离的L形短厚脚，筒与脚尖通过阶梯连接；深紫材料仍保留亮、底、侧面三档明暗。图标不等于实际穿戴轮廓。
- 头盔为封闭面罩盘形，不符合 Dynasty 普通头盔的倒U开口要求。只借鉴紧凑体量和离散色簇，不把其轮廓作为古风普通盔甲模板。
- 图集的头面罩主要是低对比半透明灰块，头壳上下和背部为环状接口；胸正面浅色板与背面深关节明确区分。背包正面/背面、顶/底不是同一块重复平涂：背包后面有小块控制面板，侧面有纵向浅色分带。
- 腰带方块大部分透明，只在腹腰相应高度留下浅色和紫灰带；腿部顶面有实体深色盖，脚部则在0.6与1.0厚度两层上分配稀疏纹理。不能把空白UV当漏画，也不能把盖面像素直接移到普通模板。
- 左臂、左腿和左靴采用镜像；左靴第二块继承builder的镜像状态。裁片页仅按最小矩形显示像素，没有模拟镜像后的顶点绕序和世界面朝向。

太空题材并非 Dynasty 古风材料身份参考；本来源仅可适用于MC方块比例、专用图集/材质块与槽位可见性的技术学习。主题适用性和独立设计语义验收待确认，不占有效1000信用。

## 原生加载对应关系

`ModItems` 99–102 四行分别注册 `ad_astra:space_helmet`、`space_suit`、`space_pants`、`space_boots`，对应HELMET/CHESTPLATE/LEGGINGS/BOOTS。胸件 SpaceSuitItem 继承 CustomDyeableArmorItem，其余三件直接使用后者。四个物品模型为generated并分别引用自己的item纹理。

Forge客户端MOD事件 `onClientSetup` 排队 `AdAstraClient.init`，后者调用 `registerArmor`，四个物品均注册 `SpaceSuitModel::new`、同一layer与同一texture。Architectury `@ExpectPlatform` 声明与Forge `ClientPlatformUtilsImpl` 中的逐物品ARMOR_RENDERERS映射对应。层定义事件注册专用 `createSpaceSuitLayer`。Forge Mixin配置明确列出 CustomDyeableArmorItemMixin，其IClientItemExtensions按物品查映射，bakeLayer后以真实slot/stack/parentModel构造模型。

SPACE_SUITS 指向 `space_suit_items`，原生tag列出四件。纹理分支优先jet、再netherite、最后基础space；基本套装共用 `ad_astra:textures/entity/armor/space_suit.png`，不是普通layer_1/layer_2。材质getName返回iron，不能据此猜成iron盔甲纹理。

专用基本层为14个部件、13个长方体；body的子件backpack与两侧臂根的cube_r1/cube_r2保留层级。头槽开启head/visor，胸槽body/arms，腿槽belt/legs，足槽boots。背包随body参与。完整原始声明、偏移、膨胀、镜像和有符号UV矩形保存于 `geometry-and-raw-uv.json`。UP面的V方向原样保留；裁片页仅归一化边界用于看像素，不当最终面方向。

源码存在命名交叉：rightBoot字段取left_boot，leftBoot字段取right_boot，然后分别复制父模型右/左腿姿态。该事实被保留，不在没有实机的情况下判定最终视觉左右错误，也不修改外部源码。

## 当前 Dynasty 真正待核范围

`current-dynasty-targets.json` 保存七个历史静态问题家族的28个实际原生ID及每套四图标、四模型声明、两穿戴图的当前SHA；注册来源为当前 DynastyGear。五套cap风险为bamboo/brocade/cloth/leather/sea_silk，三套材料优先项为hongmeng/cinnabar/brocade，去重七套。它们不是七套已确认可以重画的任务；旧静态发现与实际穿戴仍须区分。没有已确认“从没重画过”的套装。bronze/general/jade/sky/xuantian五套精致老稿继续保护。

289个受保护源文件与既有基线逐项一致。未动游戏、实例、存档、共享Jar、声音、亮度或主清单，未提交推送。

## 仍未完成

真实Forge运行中的平台注入、Mixin应用、最终染色/透明叠层，正面/45度/侧面/背面/黑剪影穿戴观感及UV接缝均未验收。本批只闭合固定源码静态对应，不宣称全部运行正确。D49/D50由Main提供的独立静态审查收据哈希已核实，作为历史支持，不重新计设计信用。继续新的有效相关整套来源；达到适用参考门槛后才进行获授权的原创资源修复和相应验收。
