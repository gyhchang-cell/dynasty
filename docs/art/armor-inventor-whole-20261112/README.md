# D57 Inventor Wizard：宽檐帽、短袖外层与专用腿靴别名根

实际四槽完整原图/穿戴UV/消费链研究，非新稿或实机。[Wizards Reborn 固定提交](https://github.com/MaxBogomol/WizardsReborn/tree/7ba78764cf6b4b0ca60e39722ca1452f7bd7f66b)，mod0.3.2、Minecraft1.20.1、Forge47.3.0、FluffyFur0.3。固定ZIP与提取文件对应见provenance。

实际看 native-pixels-01.png 的四张16×16图标、一张128×64原生穿戴图，及两页 raw-faces 原生裁片。附带inventor_wizard_belt素材未当四槽的一部分，不增加图数/设计数；没有研究其他皮肤PNG，不把纹理名或源文件数量当完成参考。

## 整体观察与用途

帽是平顶、宽平檐和一条暖铜色带，不是尖帽。胸图两肩短宽，中央暖铜竖襟与暗棕衣料分开，底部收得紧凑。裤子腰部连接直腿，两腿铜色横带高度不一致，不能把左右当同图自动镜像。双靴分开、有短方鞋头，鞋口两条暖带呼应帽带和衣襟。整套使用棕底/暗边/小块铜饰，身份来自衣物部位和带的布局，不靠漫布细雕花。

源穿戴体块14个，其中帽檐16×0×16是零厚度平面，帽体10×4×10；帽檐实际范围比普通盔甲大，作为本项目原版头盔的谨慎反例，不直接照搬。躯干8×12×4膨胀0.85，短袖基础0.52/外层0.72、腿基础0.75/外层1.02、靴1.02，pelvis独立带护档。短袖外层与腿外层大部分透明，只保留材质条；不能误认为第二套完整衣物，也不能清理成“不必要透明”。

前胸原生裁片有暖色V领与竖襟，背面用暗棕方块集中，不增加多处同亮度焦点；左右裤腿亮带的朝向/高度不同由原生UV区表达。靴子贴图只在下部成形，虽模型方体12高，不能据尺寸把全12高涂满。颜色较暗，单一衣料身份可学；不能把棕色全部替成金色来充神圣装备。

## 加载链与专用UV

WizardsRebornItems用ITEMS注册 inventor_wizard_hat/costume/trousers/boots，分别HELMET/CHESTPLATE/LEGGINGS/BOOTS，四个原生JSON的layer0解析真实图标。InventorWizardArmorItem继承ArcaneArmorItem；initializeClient选择共享INVENTOR_WIZARD_ARMOR（ItemSkin存在时可替换），设置slot、copyFromDefault、setupAnim。getArmorTexture默认返回 inventor_wizard.png；ItemSkin路径另行覆盖，未把基础设计等同所有皮肤。

WizardsRebornModels.ClientRegistryEvents明确MOD/CLIENT总线：RegisterLayerDefinitions注册createBodyLayer，AddLayers烘焙并赋共享模型。FluffyFur addLayer(namespace,name)构造#main标识。依赖源固定提交 `76f32e28e1abbf13e22621be731df98c8ce89756`，其配置也声明0.3/1.20.1/47.3.0；仍未校验实际加载二进制，不冒充运行一致。

FluffyFur ArmorModel.createHumanoidAlias替换空body/pelvis/head/arms/leggings/feet根；headParts仅HEAD，bodyParts按CHEST(body+arms)、LEGS(pelvis+legging)、FEET(feet)分流。copyFromDefault把躯干/双腿姿态分别复制到别名根。它不是Mortem标准L1/L2双纹理，也不是D55每槽独立mesh；同一128×64图集给分层别名模型。

14方体产生84原始盒面，帽檐4面零面积，80个非退化矩形均在128×64内。帽檐texOffs(-16,14)不是可见UV负数错误：两有效平面矩形在0..32内，负数只落零面积侧面。原始裁片未实施烘焙方向/姿态，不能当实际穿戴、接缝或黑剪影验收。

## 去重与适用限制

对比 wizard_hat_robe_variants 的宽檐尖帽+长襟、explorer_straps_iron_variant 的轻装绑带，以及D55护目镜长披风：本套平顶帽、短袖、裤腿错位带与分槽别名根只留一个待审整套。帽/外袖/裤外层/靴不拆计；换色与可选皮肤不计。技术机制不同不自动等于视觉独立，新增已验证信用0，新增学习组0。

可为锦/布/皮革目标学习少量铜带、正背材质块和靴筒透明分区；工业礼帽/现代外套不原样搬进古风甲。全局独立适用总数与精确缺口仍null，654/640/215历史计数不变。待独立整套去重适用性、准确依赖加载与皮肤分支、动作后根姿态/UV接缝、正/45/侧/背/剪影验收。保护289资源不变，不开游戏、不改生产或任务清单。
