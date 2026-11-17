# D61 潜伏者皮甲：四槽来源、NBT与材质对应

官方 Angry-Pixel/The-Betweenlands 1.12 固定 eafac1c217cdf304d477b025708e0dadf82b6953。同一固定ZIP的Ancient已研究，本批是**另一套实际四槽皮甲**，不因多下载/同库/新图文件而给独立信用。ModInfo完整实读：MC1.12.2/mod3.9.6、最低Forge14.23.5.2773；build.gradle83–89声明构建1.12.2-14.23.5.2773。不是Forge1.20.1的直接兼容实现。

ItemRegistry310–313四实际new ItemLurkerSkinArmor(HEAD/CHEST/LEGS/FEET)。TheBetweenlands132–164 preInit→Registries9–23→ItemRegistry604–627反射Item字段，Locale.ENGLISH小写注册，原生thebetweenlands:lurker_skin_helmet/chestplate/leggings/boots；registerItems823–833注册列表；registerModels837–841调用proxy.registerDefaultItemRenderer；ClientProxy610–635对应非多模型/非状态接口走registryName#inventory meta0。ModInfo.ASSETS_PREFIX明确thebetweenlands:。

四完整基础JSON：item/generated，layer0=thebetweenlands:items/lurker_skin_<slot>（plural items）；还有gem=1/2/3三个overrides。ItemLurkerSkinArmor和ItemBLArmor完整实读；前者构造用ARMOR_LURKER_SKIN、renderIndex3、armorName lurker_skin，后者基础穿戴路径textures/armor/lurker_skin_1或_2.png；只有LEGS选2，其他槽1。该继承链没有自定义模型callback，不能把Ancient的ModelBodyAttachment/53盒误套到本套。

CircleGemHelper38/59–79/127–133实读：顶层整数NBT Gem；无整数字段返回NONE；item property gem读枚举id。CircleGemType顶部0..3声明实读（NONE=0/AQUA=1/CRIMSON=2/GREEN=3）。ItemBLArmor根据gem.ordinal索引构造中设置的aqua/crimson/green图，不是凭文件名称猜出新注册物品。三种颜色/宝石及其JSON/图解压保存，但本批仅视读无宝石基础套；不给其他变体像素/四槽新设计信用。未实测NBT变体获取或绘制。

实际看4个16x16基础图标+2张64x32穿戴图及2张标准区域原始矩形分析页。图标暗墨绿/橄榄皮，面孔大黑开口，头中央浅骨纵块与下颌两牙；胸短宽肩、深主面和浅绿腹腰，直腿裤腰与前胫偏浅，短L脚尖明确。低对比暗色帽身局部不易辨，不能直接作为项目全身深黑模板。图集L1前腹浅绿、背部3段浅骨横块、袖和靴口重复浅绿；L2腰胯/腿用更大片浅绿，前后反差不同。原生长条/大面建立皮与腹部身份，小鳞点偏碎只作反例。不复制骨块位置、配色或原作者形状。

另固定官方MinecraftForge/MinecraftForge 1.12.x commit3effde4f1fc9d14d6ed1dbf6bebc39c2b18780e1。实际完整读LayerArmorBase/LayerBipedArmor补丁，ForgeHooksClient170–175/244–248，ItemArmor补丁hasOverlay条款。消费链补丁提供：原生槽匹配后取模型→getArmorModelHook→设置姿态和可见性→getArmorResource→ForgeHooksClient.getArmorTexture调用当前ItemBLArmor覆盖，非null优先；LayerBipedArmor hook回ForgeHooksClient.getArmorModel，未提供模型则保留默认ModelBiped。hasOverlay由LEATHER或非白color判定，本套是自定义material且未覆盖color；本批没有读完Vanilla ItemArmor颜色默认源码，故不假称覆盖层条件实测。

补丁不是完整Vanilla源码：**精确1.12 ModelBiped盒/UV、各槽可见部件switch、ModelBox面向仍未完整读到**；标准raw区域从既有保存64x32上下文保守引用并记录哈希，用于比较材料位置，不证明1.12最终面接缝/左右烘焙/穿戴5视。补丁commit也不是已加载旧Forge构建身份。未运行上游或游戏。

与已有完整保存 forest_troll_hide、creature_hide_shell_vests、naga_scale_green、mixed_caveman_asymmetric_hide文字观察实际对照：深绿皮+浅骨与既有绿皮骨护额高度重合，腹部大浅绿面/背横骨可以提供组织方法，但不保证独立语义。先作为1整套候选，正式信用0；不将四件、2图、宝石变体、同库另一材质自动算不同相关设计。

可用于Dynasty leather材料区与bamboo“主体/绑条”主次学习，不将水生怪物牙口移植普通头盔，不因低阶皮甲候选而覆盖精致老稿。28优先ID共70输入文件本轮哈希对上既有快照，但不是70次美术目视验收；确定从未重画套数仍0。D54验1族沿账本继承追加0，全局total/gap未知，gate false。无生产变更/Java游戏/主清单删除，保护289按另存哈希记录。
