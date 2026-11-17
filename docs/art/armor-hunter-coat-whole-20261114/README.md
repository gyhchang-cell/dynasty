# D90：普通猎人外套四槽新来源研究

本批只做参考研究，未改运行图标/穿戴UV、身体/程序、共享Jar或任何清单/存档。保留289精致项与70优先项，未开Java、声音、亮度或屏幕。新增独立验收信用0；1000适用独立总数/精确缺口仍未知，不能提前制作。

固定官方 TeamLapen/Vampirism 提交 `ee4f4a2635604925c7bdc3b46f91127ff950f37c`，根树 `69229b727d21489935c4f0c46c3a9c84b62fb969`。24个文件逐个核对根树Git blob SHA-1与SHA-256。源码声明MC1.20.1、Forge47.1.0，版本组成1.10.18；gradle.properties的mod_version字面Test由其他脚本覆盖，因此不编造已发布Jar版本身份。

## 真正查看与观察

实际查看普通版四个16²图标及两张64×32穿戴图，共6个原生PNG。`normal-source-study.png`仅为他人原图整数最近邻放大，不是Dynasty新美术或游戏截图；未改原稿RGBA、分辨率或透明边。强化/终极版没有下载/看图或额外计数。

头图为短檐黑帽和单条灰带；胸为两袖加开前襟黑长外套，几颗竖扣点出衣缘；裤有完整腰连接双直腿、棕色脚口，靴有两只分开的黑直筒。四个部位组织完整，而非护膝/腰带图标。胸仍是外套，不能拿长衣襟作为普通短宽金属胸甲模板；帽也不是倒U防护盔。

黑布靠少量灰簇、袖口、襟边和靴带表达层次，无满身金线。但暗部区分度低，小尺寸在暗背景下材质难辨，是对比不足反例，不能照搬“整套近黑”。L1图集有帽带/帽面区和黑胸臂区；L2既有黑腿区也有棕色衣片大区，不能把下层衣片或透明开口当丢图补满。最终人体衬托/上下槽遮挡尚未实测，不把图集视觉观察冒充穿戴通过。

与旧cultist_belted_cloth、immersive_robe_open_front、ninja_cloth_cowl的原观察对照，黑外套/窄衣缘/扣带存在重叠；旧族全部原图本批未重开。新命名空间、帽檐或配色都不直接证明语义独立，只保留1个完整新来源候选，新增已验收信用0。

## 四槽绑定与实际消费者证据

完整读HunterCoatItem、VampirismHunterArmorItem、util.ArmorMaterial及HumanoidArmorLayerMixin。ModItems四个NORMAL注册段、4份generated item JSON及4份weapontable配方实际查看；客户端其他已下载大类未宣称通读。下载的VampirismArmorModel不是本外套已选模型，未拿其类名猜3D衣服绑定。

NORMAL material名为`vampirism:hunter_coat`，util.ArmorMaterial.getName原样返回。HunterCoatItem和父类没有getArmorTexture/initializeClient替换；父类有protected getTextureLocation辅助函数，但不能把一个辅助函数当实际渲染override。

另下载与源码声明相同的官方Forge47.1.0 sources Jar，用官方SHA-1文件校验，抽取HumanoidArmorLayer补丁、ForgeHooksClient、IClientItemExtensions、IForgeItem。补丁全文读过，其余只读相关getter/default/model段。Forge实际fallback先分材质namespace，LEGS选2、其他选1；item hook返回null保留fallback。IForgeItem默认null，IClientItemExtensions默认返回original模型。因此本源码静态选择两张64×32图集；没有把Java类叫“coat”推断成独立geo或分层长袍模型。Mixin所读注入仅记录partialTicks。

这是固定版本的源文件路径证据，**不是加载中的Forge二进制、完整模组集合、最终原版网格/slot可见性或实机验收**。未做完整signed UV、镜像、接缝、五视角、灰模/黑剪影或游玩验收。

四份配方为level1、lava2的4×4武器台配方，原料为铁/皮革/大蒜，胸另用吸血鬼牙。普通版修补标签为铁。实际标签来源、原生获取、付款、制作均未执行，不能说只用原版铁甲合成或已完成材料链。

## 接收D88独立复核

`coordinator-D88-hold-reference.json`只引用主协调独立复核的绝对路径、58306字节、SHA-256 `1b46560c9436b458b313e600ca93ce51f21744e537a20b9018f297a9c268f91a`，不修改主协调文件、不重跑D88。依其最新委派继续HOLD0：护膝/腰带不作完整腿形、旧族完整原图和库版本匹配/最终UV仍待验；没有预记信用或改旧ledger。

本批保存要求全文/哈希，ledger仅追加1条待验及新prior链接；70优先资源中仍无同时“未重做且简陋”的确证，不因穿戴待验重画认可图标。冻结时复核289/70及主协调收据哈希，所有未验任务继续保留。
