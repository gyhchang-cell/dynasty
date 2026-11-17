# D12穿戴声明续核 D17

静态核对4个既有名称族的16件物品：warding、guardian_ocean、sakura、virtual_gold。不复读旧图标，不增加名称或设计信用，不生成或覆盖贴图。

本批核实9个外层类、6个同一Celestial Core JAR内嵌l2damagetracker类，并复用D12已固定4份声明。`javap`仅解析类文件，不加载模组或启动游戏。Forge 1.19.2使用已安装43.3.2客户端字节码；1.20.1使用已固定47.4.10映射源码，不混用版本猜路径。逐字节来源见class-provenance.json、nested-class-provenance.json、source-provenance.json。

- Ward物品注册名为warding_helmet/warding_chest/warding_leggings/warding_boots；供应器12–15均选DIAMOND_WARDING而非WARDING_MAIL。材料名返回spellblademod:diamond_warding，默认腿选layer_2，其余layer_1，与既有候选图一致。
- Celestial Core由CCMaterials.values→MATS.genItem生成四部位；材料armorPrefix返回celestial_core:<id>，ArmorMat原样返回name。Ocean/Sakura选GenericArmorItem，VirtualGold选VirtualGoldArmorItem并提供inner/outer两种自定义64×64模型。
- sakura/virtual_gold共8件默认图集资源存在，连同warding共12件有精确源JAR纹理对应。
- **guardian_ocean四件的默认路径为guardian_ocean_layer_1/2.png，源JAR只有ocean_layer_1/2.png。** 已确认两条默认路径在固定源JAR不存在，不能把旧ocean候选静默当成实际选中。需查最终Forge hook、资源覆盖和实穿效果；缺路径不等于已证明游戏Bug。

`static-binding-study.json`逐件记录注册、槽位、材料、模型、图标、默认资源和限制；`method-excerpts.json`保留可复查的方法片段。16条仅为Forge hook之前默认资源链，不宣称排除其他覆盖、不关闭实际穿戴或Dynasty目标UV验收。D12静态默认材料名部分已补齐，最终绑定缺口仍保留。

验证PASS_STATIC_DEFAULT_RESOURCE_EVIDENCE，289条保护路径未变。累计仍为532已读名称、518盔甲名称、203保守学习组、14排除项；已验完整独立设计总数未知，最低缺口797。无新制作、运行资源修改、游戏启动、共享Jar覆盖或任务删除。
