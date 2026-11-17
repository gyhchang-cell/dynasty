# D49：GeoTetraArmor 九模块重甲完整配置研究

这是外部原生参考研究，未制作或覆盖 Dynasty 贴图。目标是尚未进入既有 reviewed_case_keys 的完整重甲配置；九个模块、十二张 PNG、三份模型都不能拆成多个盔甲设计。

固定来源、SHA、原始条目与只读 javap 在 provenance.json 和 dependency-provenance.json。whole-native-source.png 已实际查看，采用原始像素整数放大，仅供看原图，非游戏截图、非最终四槽合成图标。三张 64×64 穿戴图逐字节相同；九张 16×16 图是模块零件。没有把它们合成为冒充原生最终图标。

## 完整配置及四槽调用

原生注册物品只有 geotetraarmor:head、chest、legs、feet；注册 bootstrap 2/4/5/3 分别直接构造 ModularHeadItem/ChestItem/LegsItem/FeetItem。子类构造器分别传 HEAD/CHEST/LEGS/FEET。必需 major 模块为头一、胸三、腿三、靴二，详见 whole-configuration.json。研究配置名不是注册 ID，也不是已实际获取的 NBT 变体。

九个 heavy.json 均允许 tetra:metal/。Tetra MaterialVariantData.combine 的拼接把 heavy_* / 前缀与材料 key iron 相接；MaterialData.kneadModel 对 iron 的 metal/default 纹理名无法匹配 base/left/right，走 availableTextures[0] 回退。MaterialData 构造器的 textureOverrides 为空数组，iron.json 未覆盖它。ItemColors 的 iron 为 0xffffff，MaterialColors.Deserializer 解析该颜色，模型 tint 经 renderer 变为不透明白色。材质选图不等于游戏中已成功组装。

ModularArmorItem 从 getAllModules → ItemModule.getModels，过滤 nonNull 与 type.startsWith("gecko")，通过 bootstrap 16 的 ModularGeoArmorRenderer 构造器建渲染器。ModularArmorModel 将 location 转为 geo/*.geo.json、animations/*.animation.json、textures/*.png。Mixin 在 renderArmorPiece HEAD 获取当前槽物品并检验该装备槽，prepForRender 后调用模型纹理；没有据此声称取消原版渲染。

Renderer 自定义 armorBelt 并在 LEGS 槽启用；其余头身臂腿靴依赖继承的 GeoArmorRenderer。当前没有完成对应依赖版本的全部继承可见性/变换与最终烘焙验证，不能据原始骨名宣称已完成全套穿戴验收。原生 iron replacement JSON 实际指向 vanilla 模块，不是本研究的 heavy 配置。

## 看图后的可用原则与反例

- 头部模块是紧凑倒 U 开口、平顶与少量分级亮暗；短胸片用大灰色块表现体积，左右肩和腿的边线克制，适合学习普通金属盔甲的大色块组织。
- 左右模块高光方向分别排布，不能直接把单侧 PNG 当最终双侧物品，也不能机械复制镜像到所有穿戴 UV。
- 穿戴图集以共享金属灰阶为主，但局部存在细碎亮点；只借鉴材料分区，不把所有亮点照搬成 Dynasty 噪点。
- 三份几何共 19 骨、45 长方体：基础31，左7，右7；20 个 box UV 与25个逐面 UV，原始正负 UV 保存在 declared-geometry-uv.json。这里是声明坐标，不是已变换世界边界或五视角效果。
- 基础头盔有 bloody_star 14 块和 bone 10 块附加结构，局部 Y 延伸明显高于 armorHead，带多级旋转。不能当普通盔甲紧凑比例的正面范例；强力装备也应先服从用户认可的原版轮廓。
- 三份动画均只声明空骨骼的 idle/fly 循环，不能靠动画文件存在就宣称头饰隐藏、运动正常或握点正确。

## 结果与保留项

review.py 已核验两份固定归档、53 条原始条目与17份只读反汇编哈希、9模块/4槽布局、12 PNG、完整声明几何及289条 Dynasty 保护路径，均通过。未修改受保护资产。

新增一个待独立语义审查的完整配置候选，不增加已验设计信用。旧654名称族/640盔甲名称族/215学习组不是已验独立1000总数，门槛仍未达到。最终四槽图标合成、精确依赖版本下继承可见性/逐面烘焙、实际组装获取与穿戴五视角仍待验。本轮不启动游戏、不删除任务提示词。
