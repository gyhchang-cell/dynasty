# D81：D79材料解析与BASE资格补查

本批补查固定来源中的实际消费者条件，不是新完整设计。新参考信用0、不增加待审完整族、不制作美术。原D79、D80收据及保护稿保持不变。

固定上游仍为SlimeKnights/TinkersConstruct提交 `16bbeb883a933986321867ef3b93bd441f0fa894`；复用D78未截断Git树，补取16个经过Git blob/SHA256校验的文件：12张BASE PNG、4个Java来源文件。`provenance.json`保存来源。实际读MaterialRenderInfo、MaterialTextureField、MaterialRenderInfoLoader全文，MaterialModel只读60–116行，不把下载当全文阅读。未执行任何Java。

## 本批新补齐的有界事实

1. 四张穿戴BASE `plating_armor / maille_armor / plating_leggings / maille_leggings` 均在固定源中，都是64×32。八张对应图标BASE是16×16。实际查看两页原生像素最近邻放大，原图绝对路径与SHA在original-image-paths.json。只是确认固定资源存在与像素，不等于当前运行资源包的TEXTURE_VALIDATOR已通过。
2. MaterialTextureField.get三态：显式texture可指定值或null；未写texture且skipUniqueTexture=false时，返回上下文material.getLocation('_')。铁／皮革渲染JSON没有texture、skipUniqueTexture或parent，所以按该字段规则使用各自材料ID，而非因缺少显式texture就跳过专用图。上下文和Mantle JSON解析运行仍未执行。
3. MaterialRenderInfo.getSprite的图标分支：先尝试材料texture后缀，若sprite不是MissingTextureAtlasSprite则不染色返回；失败后按fallback顺序尝试并带vertexColor；最后返回BASE sprite并带vertexColor。getSuffix对非minecraft命名空间拼namespace_path。MaterialModel.getMaterialSprite先取renderInfo，有则委托getSprite，没有则返回BASE、不染色；validateMaterialTextures是另外的方法。这不能和穿戴层的BASE validator门槛混成同一函数。
4. MaterialRenderInfoLoader扫描 `tinkering/materials`，variant路径映射成材料变体，带变体查询先尝试精确变体，再回退基础ID。onReloadSafe用带MaterialVariantId的context解析，跳过空JSON；最终存Map.copyOf。init声明在RegisterAdditional事件且ModLoader状态有效时重载。这里只读取该初始化方法，不宣称调用入口、资源排序或加载状态实际成功。
5. 对穿戴的MaterialArmorTextureSupplier，继续承接Main已读结论：materialGetter必须先有无后缀BASE通过validator，再尝试专用图。此处补上“BASE在固定源存在”这个前提；没有移除validator或把文件存在改称运行绑定已闭合。
6. 与D79专用图逐像素比较，12张BASE中11张alpha一致。`maille_armor.png`在(7,13)、(16,13)是alpha0，`maille_armor_tconstruct_leather.png`相同坐标为alpha255，其他alpha相同。见base-alpha-difference.json。这个差异不能直接判为缺图、接缝或作者错误；本批没有修改图。颜色和哈希差异也不形成新设计信用。
7. 重读D79定义明确：leather craftable=true、tier0；iron craftable=false、tier2。D79默认两个tier1–2随机材料选择器不保证选出leather。铁／皮革仍只是一套选定研究配置，不能用stats字段存在替代实际生成、制作或获取验收。

## 可直接使用的研究结论

灰度BASE与对应材料专用图仍采用相同甲片／内衬分工；材料色与材质语言属于一套设计的实现，不能拆成多套。用户未改旧金属甲可以借鉴连续亮面与少量连接材料的层次；不把灰度BASE或染色回退直接复制成最终原创，不碰精致已认可图。若后续核查出现“PNG有但不显示”，需同时检查BASE、材质渲染信息、材料索引、resource pack与修改器状态，不能先重画纹理掩盖绑定缺口。

## 保留的限制与交付

核心收据见coordinator-delivery.json；原图路径和哈希见original-image-paths.json。12张BASE只是D79的模板资格证据，不是12个新参考，也不重新审D79整套。既有D54确认对象、全部pending完整族与历史证据完整保留。

仍未闭合：Mantle ResourceValidator／RegistryDataMapLoader内部与实际依赖二进制、材料事件init真实调用入口、当前资源包覆盖和sprite atlas、真实NBT与原生获取、精确穿戴消费者与五视图接缝。未将本批静态source lookup或像素比较当游戏验收。

两份永久贴图要求已读并核哈希；本批无制作，不冒充实际制作snapshot。289保护／70优先资源批前批后核对，不开Java／游戏、不碰Jar、主清单、session、提示词、用户实例／存档、声音亮度。下一步继续尚未读过的完整相关设计，避免反复展开这套换材质模板。
