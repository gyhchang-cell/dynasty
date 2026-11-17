# D58 Ancient：铜褐厚板、浅骨扣与青色网布

完整四槽原生盔甲研究，非 Dynasty 新稿、穿戴测试或运行兼容证明。来源：[The Betweenlands固定1.12提交](https://github.com/Angry-Pixel/The-Betweenlands/tree/eafac1c217cdf304d477b025708e0dadf82b6953)，ModInfo声明Minecraft1.12.2、模组3.9.6、Forge minimum14.23.5.2773。固定源ZIP、选读文件与SHA见provenance，未执行外部Java。

实际查看native-pixels-01：四张16×16图标与一张128×64 ancient.png；以及raw-nets-01至05五页共43个原始UV尺寸网。只研究无宝石基础设计，aqua/crimson/green图标与穿戴纹理未查看，不计设计。原图没有修改，分析页整数最近邻；不是游戏画面。

## 全族观察

头部图标由浅骨色分枝横冠、铜褐额片与青灰两侧护片组成，下部大开口。胸图是左右宽铜板压在青灰网布上，中心领口深，胸底两片网布留暗隙；不画成细腰人台。腿图上方铜腰、左右浅骨扣，下方两条分离青网腿；双靴是铜筒、青灰横带、浅骨方鞋尖，结构紧凑且能分清材料。

源UV显示铜板正面几块暖亮方簇，侧面较暗；骨件用很少浅黄/灰黄块，网布为两三青灰交错。主cover正面有大脸孔开口，侧/背则保留网布，不能把atlas一块青纹当整件纯铜头盔。胸的两块厚板有少量旋转，腰和肩另设窄板；骨扣和鞋尖不是白底，应保留。

可学材料主次（铜板最大、网布次、骨扣少量焦点）与各槽呼应，不复制分枝鹿角冠、细密青棋格或全身细小骨挂件。古代幻想主题比D57工业礼帽更接近Dynasty，但主题接近不能自动证明独立适用参考；普通布、皮甲不应套角冠。

## 完整静态加载链

TheBetweenlands.preInit→Registries.preInit→ItemRegistry.preInit反射Item字段；registerItem按fieldName小写并以ModInfo.ID设registryName。ANCIENT_HELMET/CHESTPLATE/LEGGINGS/BOOTS各创建ItemAncientArmor对应HEAD/CHEST/LEGS/FEET。ItemRegistry类注册事件总线；registerItems逐项注册ITEMS。模型事件registerModels调用ClientProxy.registerDefaultItemRenderer，getItemModelMap普通分支以registryName#inventory建立meta0映射；四个原生JSON layer0解析到真实items/ancient_*.png。

ItemAncientArmor extends Item3DArmor extends ItemBLArmor，createModel返回ModelAncientArmor；Item3DArmor按类共享缓存，getArmorModel按装备槽调用setVisibilities。所有槽都返回同一128×64 ancient.png；不是普通L1/L2。ItemBLArmor按CircleGemHelper读出的宝石类型选择额外纹理；gem属性来自NBT并驱动物品JSON覆盖。基础ID不当NBT宝石变体，未查看这些覆盖图也不声称验完宝石分支。

ModelBodyAttachment清除继承人体根方体，普通姿态沿ModelBiped，ArmorStand单独转换角度。Ancient子类覆盖resetVisibilities/setVisibilities：HEAD只开helmet_mainrotation；CHEST开躯干及两臂挂点；LEGS开腰和两腿网布；FEET只开boots_main。靴实际挂bipedLeg，不能据base类另外的boot根误判消费者。render内先对源数组postRender(0.0675)，靴0.06625，再super.render；初始pivot不是最终世界位置。

## UV、结构与未验边界

58个ModelRenderer方体声明包括5个0×0×0挂点，只有53个非零体积盒；43个不同UV/尺寸网，不是43个设计。保留每个原点、尺寸、父子、全部pivot覆盖顺序、旋转与mirror设置在addBox前后的关系。右侧分枝mirror在addBox之前；未读取精确1.12 ModelBox消费者，不声称烘焙镜像已验。所有非退化原始UV矩形在128×64内。分析网未实施源旋转、postRender或实际烘焙面方向，不冒充五视/接缝验收。

对照已存完整骨羽挂甲、巨魔皮/骨护额、铁木铆钉文字观察与D54枝板组合；不冒充重读所有旧像素。骨饰、角、铜色或新命名空间不自动增加独立设计。本套厚板/网布/骨扣整体只留一个待审家族；正式信用0，新增学习组0。D56是标准染色L1/L2+overlay，D57是FluffyFur别名根+膨胀外层，D58是旧ModelRenderer父子挂接+槽可见性+宝石替换；机制不同也不直接给视觉独立信用。

待独立语义去重/目标适用性、精确旧版消费者及依赖运行、宝石分支、正/45/侧/背/黑剪影/动画/穿戴接缝。全局已验证适用总数与gap未知；654名称、640盔甲名、215保守学习组不是1000已完成数。289受保护资源保持；不改生产、清单或实例，不开游戏、声音或屏幕。
