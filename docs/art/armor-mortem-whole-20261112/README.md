# D56 Mortem：染色底层、固定骨饰与标准穿戴图集

完整四件原生设计参考，非 Dynasty 新贴图或实机。来源：[Forbidden & Arcanus 固定1.20.x提交](https://github.com/stal111/Forbidden-Arcanus/tree/189c3ca451af186415e3e2f3f0fbb4d8226819b6)。源ZIP、原PNG与Java声明保存在本地，逐文件SHA见 provenance.json；配置 mc_version=1.20.1、Valhelsia Core 1.1.2。

实际查看两页 native-pixels，共四图标的底层/overlay八张及两层穿戴的底层/overlay四张。四页 raw-uv 为原始标准盒网裁片，保留透明区；非带有正确镜像/朝向的烘焙模型，也不是穿戴验收。

## 整套观察

头部底图是灰白倒U边框，overlay补紫褐兜帽边与浅骨面具；不能把底图单独当最终完整头盔。胸部底图两肩和两条竖向灰带有较大透明间隙，overlay的中央浅黄骨饰由横片和竖片组成，肩缘少量紫色。腿部底图是直腿连接腰，紫色overlay只在腰部；不是把全条腿染紫。双靴是分开的直筒L形，紫色鞋口/鞋面由overlay补入。四件共享“浅底布/骨色固定装饰/深紫约束带”语言，不是四个设计。

原生穿戴L1的 head 基础区基本透明，脸主要来自overlay；hat区域有实际灰布/紫边。胸正面留空配浅骨饰，背面有另一组骨片。L2只有腰和两腿，overlay仅腰带。浅布区域有少量斑块，可研究材质分区，但密集零碎斑点不是本项目应照抄的MC粗像素标准。骨面具用途不能因此强加给原本普通布甲；可借鉴“底料可染、装饰不变色”的分层原则。

## 注册及消费者

ModItems.HELPER 分别请求注册 mortem_helmet/chestplate/leggings/boots，各传相应 ArmorItem.Type；HELPER来自 ForbiddenArcanus.REGISTRY_MANAGER 的 Valhelsia ItemRegistryHelper。MortemArmorItem继承DyeableArmorItem，只覆盖颜色：display.color存在则使用，否则RGB(199,198,191)。未声明自定义模型/纹理接口，ModArmorMaterials.getName返回 forbidden_arcanus:mortem。

四原生物品JSON的 layer0/layer1 解析到真实底图/overlay。ColorEvents声明 tintIndex>0 返回白色，否则使用物品颜色；**该订阅注解没有显式MOD事件总线，运行事件是否调用未验证**，不能据静态回调声称图标染色已正常生效，也不改外部模组代码。

复用已保存Forge1.20.1 HumanoidArmorLayer上下文：LEGS取L2，其余L1；DyeableLeatherItem底层按颜色乘RGB，再以白色绘overlay；材质命名空间拼成四张64×32原生纹理路径。未运行精确依赖、其他Mixin及最终合成。Valhelsia注册helper实现尚未闭合，不将注册请求冒充运行注册收据。

## 去重、适用性与边界

与已有开襟袍族、原版皮革染色及骨/羽装饰甲比较：染色机制、灰白/紫换色、四槽、12张PNG都不构成新增设计。骨面具、分离胸带、固定骨饰与紫腰带的整套组合保留一个待独立审查家族；新增已验证信用和学习组均0。对布、锦、海丝目标可学“少量硬边装饰留在overlay、底料单独处理”，不能照搬骨面具主题。

全局适用独立设计总数、精确缺口仍null；历史654名称/640盔甲名/215学习组不变。正/45度/侧/背/黑剪影、染色实际表现、接缝、模型镜像、事件调用及依赖注册仍待验。289保护资源未改，不开游戏、不覆盖生产图、不删任务。
