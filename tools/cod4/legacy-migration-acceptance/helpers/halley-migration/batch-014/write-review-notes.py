"""Author static research notes only; no upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
old=(b.parent/'batch-013/review.py').read_text()
header=old[:old.index("add('akashictome")].replace('batch-013','batch-014')
footer=old[old.index('def generate():'):].replace('batch-013','batch-014')
notes=r'''
add('modularrouters-security-upgrade-durable-owner-to-recompiled-access',[
 ('item/upgrade/SecurityUpgrade.java','onCompiled'),('item/upgrade/SecurityUpgrade.java','getPlayerIDs'),('item/upgrade/SecurityUpgrade.java','addPlayer'),('item/upgrade/SecurityUpgrade.java','removePlayer'),('item/upgrade/SecurityUpgrade.java','use'),('item/upgrade/SecurityUpgrade.java','interactLivingEntity'),('item/IPlayerOwned.java','getOwnerID'),('item/IPlayerOwned.java','getOwnerName'),('item/IPlayerOwned.java','setOwner'),('item/upgrade/UpgradeItem.java','onCompiled'),
 ('tile/ModularRouterBlockEntity.java','load'),('tile/ModularRouterBlockEntity.java','saveAdditional'),('tile/ModularRouterBlockEntity.java','hasItems'),('tile/ModularRouterBlockEntity.java','ModularRouterBlockEntity'),('tile/ModularRouterBlockEntity.java','compile'),('tile/ModularRouterBlockEntity.java','compileUpgrades'),('tile/ModularRouterBlockEntity.java','serverTick'),('tile/ModularRouterBlockEntity.java','recompileNeeded'),('tile/ModularRouterBlockEntity.java','RouterItemHandler'),('tile/ModularRouterBlockEntity.java','onContentsChanged'),('tile/ModularRouterBlockEntity.java','UpgradeHandler'),('tile/ModularRouterBlockEntity.java','isItemValid'),('tile/ModularRouterBlockEntity.java','addPermittedIds'),('tile/ModularRouterBlockEntity.java','isPermitted'),('tile/ModularRouterBlockEntity.java','getOwner'),('tile/ModularRouterBlockEntity.java','getFakePlayer'),('tile/ModularRouterBlockEntity.java','getUpgrades'),('tile/ModularRouterBlockEntity.java','createMenu'),('block/ModularRouterBlock.java','use'),('block/ModularRouterBlock.java','getTicker'),('container/RouterMenu.java','RouterMenu'),('container/RouterMenu.java','stillValid'),('util/fake_player/RouterFakePlayer.java','RouterFakePlayer')],
 '安全升级物品通过潜行使用设置owner、对玩家使用增删名单；router世界NBT重载其升级库存，新实例初始重编译及随后升级变化触发编译，真实方块交互据编译后的UUID集合决定是否开菜单。',
 '升级ItemStack根Owner为两个字符串ListTag：[显示名,UUID字符串]；Players compound以UUID字符串为键、名字为值。router Upgrades为ItemStackHandler序列化compound，内存permitted不直接序列化；新实例recompileNeeded初始同时含模块和升级位。',
 'load读取Buffer/Modules/Upgrades等，saveAdditional写含物品升级库存。服务端tick先compile，compileUpgrades先清permitted再调用各升级onCompiled并合并getPlayerIDs；owner不存在即返回空集合，即便Players存在也忽略。isPermitted在集合为空或玩家UUID在集合中时允许，否则任意一手持Override Card也允许。getOwner从安全升级取同一owner构建fake-player GameProfile，升级重新编译会丢弃旧fakePlayer使下次重建。',
 '名单是从持久物品重新推导的派生状态，恢复Owner只留名字/漏UUID或只迁Players会改变真实访问控制。getOwnerID直接解析Owner[1]，短列表、错类型或非法UUID无局部catch；Players任一非法UUID键也可中断编译。添加名单UI最多6人，但reader直接读取所有键，没有上限裁剪。设置新owner不清Players且持有者潜行即可重写owner，不能宣称仅原owner可转让。RouterMenu.stillValid只检查未移除及距离平方<=64，菜单开启后权限变更不在此方法复验。',
 'Dynasty永久归属/任务权限迁移应同时保留UUID与存在结构，并明确缺失/坏结构不能静默变成公开；把派生权限重建纳入恢复完成边界，在最终操作重查。Clone仅复制经审定永久键后重算派生对象，不复制整个ForgeData、旧fakePlayer或临时冷却。',
 '这里只证明本mod的库存序列化调用及访问消费，未重读Forge ItemStackHandler/原生ItemStack全部底层实现，不能保证未知物品ID/ForgeCaps无损。未证明放置物品BlockEntityTag的原生恢复链；block类中另一deserialize只是tooltip，不当放置证据。初始字段保证新实例请求编译，不声称任意已存在实例load都自动重新编译或断言首tick前可利用窗口。fakePlayer仅追到profile构造，未审查Activator最终攻击/所有权边界。缺owner开放是该mod策略而非建议照搬。',
 'owner codec、名单、库存load/write、编译、菜单、fakePlayer身份都是同一归属恢复家族，一条建议。Owner字符串槽/6个成员/升级种类/GUI和网络外壳不另计；与batch012 gateway ACL在模式上接近但权威数据为升级物品与派生集合，Kepler可语义合并，credit0。')

add('modularrouters-module-global-target-restoration-to-real-item-transfer',[
 ('logic/ModuleTarget.java','fromNBT'),('logic/ModuleTarget.java','toNBT'),('logic/ModuleTarget.java','ModuleTarget'),('logic/ModuleTarget.java','isSameWorld'),('logic/ModuleTarget.java','getItemHandler'),('logic/ModuleTarget.java','getItemHandlerFor'),('logic/ModuleTarget.java','equals'),('logic/ModuleTarget.java','hashCode'),
 ('item/module/TargetedModule.java','useOn'),('item/module/TargetedModule.java','isValidTarget'),('item/module/TargetedModule.java','handleSingleTarget'),('item/module/TargetedModule.java','handleMultiTarget'),('item/module/TargetedModule.java','onSneakRightClick'),('item/module/TargetedModule.java','setTarget'),('item/module/TargetedModule.java','getTarget'),('item/module/TargetedModule.java','getTargets'),('item/module/TargetedModule.java','setTargets'),('item/module/TargetedModule.java','updateTargetBlockName'),('item/module/TargetedModule.java','doModuleValidation'),('item/module/TargetedModule.java','validateTarget'),('item/module/TargetedModule.java','maxDistanceSq'),('item/module/TargetedModule.java','isRangeLimited'),('item/module/TargetedModule.java','getMaxTargets'),
 ('item/module/SenderModule2.java','SenderModule2'),('item/module/SenderModule3.java','SenderModule3'),('item/module/SenderModule3.java','badDimension'),('item/module/SenderModule3.java','isRangeLimited'),('item/module/IRangedModule.java','getCurrentRange'),('item/module/ModuleItem.java','ModuleItem'),('item/module/ModuleItem.java','compile'),
 ('logic/compiled/CompiledModule.java','CompiledModule'),('logic/compiled/CompiledModule.java','getTarget'),('logic/compiled/CompiledModule.java','hasTarget'),('logic/compiled/CompiledModule.java','getRange'),('logic/compiled/CompiledModule.java','getRangeSquared'),('logic/compiled/CompiledModule.java','getRangeModifier'),('logic/compiled/CompiledModule.java','getItemsPerTick'),('logic/compiled/CompiledModule.java','onCompiled'),
 ('logic/compiled/CompiledSenderModule1.java','CompiledSenderModule1'),('logic/compiled/CompiledSenderModule1.java','execute'),('logic/compiled/CompiledSenderModule1.java','isValid'),('logic/compiled/CompiledSenderModule2.java','CompiledSenderModule2'),('logic/compiled/CompiledSenderModule2.java','setupTargets'),('logic/compiled/CompiledSenderModule2.java','findTargetInventory'),('logic/compiled/CompiledSenderModule2.java','validate'),('logic/compiled/CompiledSenderModule2.java','getEffectiveTarget'),('logic/compiled/CompiledSenderModule3.java','CompiledSenderModule3'),('logic/compiled/CompiledSenderModule3.java','validate'),
 ('tile/ModularRouterBlockEntity.java','load'),('tile/ModularRouterBlockEntity.java','saveAdditional'),('tile/ModularRouterBlockEntity.java','compile'),('tile/ModularRouterBlockEntity.java','compileModules'),('tile/ModularRouterBlockEntity.java','executeModules'),('tile/ModularRouterBlockEntity.java','serverTick'),('util/ModuleHelper.java','validateNBTForWriting'),('util/MiscUtil.java','serializeGlobalPos'),('util/MiscUtil.java','deserializeGlobalPos'),('util/MiscUtil.java','getWorldForGlobalPos'),('util/MiscUtil.java','makeGlobalPos'),('util/InventoryUtils.java','getInventory'),('util/InventoryUtils.java','transferItems'),('util/InventoryUtils.java','countItems'),('ModularRouters.java','getDimensionBlacklist')],
 '潜行对真实库存设置Sender目标，模块ItemStack持久Target在router Modules库存保存/重载后由compile读取；服务端真实execute查目标capability并把buffer物品插入远端库存。Sender2/3共用一个持久目标家族。',
 '模组tag中Target compound：Pos包含BlockPos NBT及维度资源名，Face为方向byte，InvName为显示翻译键；另有MultiTarget compound-list，通过HashSet按GlobalPos+face去重。未见旧ID或旧维度别名转换。',
 'getTarget只接受compound类型，否则null；fromNBT构建GlobalPos及方向。Sender2编译时读取并按已加载目标更新显示名，执行必须同维且距离平方<=range²。Sender3复用读取/真实execute，只放宽validate为同维或源目标均不在跨维黑名单。getItemHandlerFor首次取capability遇到world=null/未加载/无BE返回empty，成功缓存并注册失效监听，execute空目标/无cap均不转移，不强载区块。',
 '诊断TargetedModule.validateTarget在validateBlocks时对源目标维度都查黑名单，而实际Sender3.validate先sameworld短路，同维可绕过该黑名单检查；不能以tooltip通过/失败代表真正执行。InvName仅显示，不验证原目标方块身份，换同位置库存仍可能收物。updateTargetBlockName在加载区块时通过setTarget写回，getTargets多目标循环也调用它，从而可能写单Target而不更新MultiTarget原名。单目标缺失仍可能形成含null的单元素targets，hasTarget只查list非空，findTargetInventory另有null guard。',
 'Dynasty任何持久位置/物品恢复先保存原维度键与原载荷，缺维度/未加载和真正无效区分；从最终消费者检查权限、维度和资源存在，避免只修诊断路径或显示名。若需旧ID映射，在原生解码前白名单转换并保留未识别载荷，不把InvName用途键当物品ID。',
 'deserializeGlobalPos对资源名无catch/默认别名；Face缺失会以byte0解析，构造允许null face但toNBT直接解引用。维度key比较用==，不推断资源keyinterning必坏。成功cap缓存期间不重复loaded检查，依赖失效事件；未执行其可靠性验证。InventoryUtils.transferItems先模拟提取、真实插入再真实提取，依赖capability契约，无事务回滚；countItems仅item/可选damage不比较NBT。完整Filter/Augment策略未深审，仅记录调用，不声称全部过滤、权限或调度正确。多目标真实Sender4执行未深审，作为同codec旁证不另候选。',
 'Pos/Face/InvName、单/多目标、Sender2/3等级、范围getter、capability与真实transfer支持为同链一条；不按每维/坐标/面/键/模块等级拆数。与其他GlobalPos持久玩法需Kepler最终语义去重，credit0，通用capability本身无独立信用。')
'''
fieldfn='''\ndef attach_fields(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    sample=next(r for r in INDEX if r['path'].endswith('/tile/ModularRouterBlockEntity.java'))
    raw=(ROOT/sample['source']).read_bytes()
    fields=[]
    for node in walk(PARSER.parse(raw).root_node):
        if node.type!='field_declaration':continue
        fragment=raw[node.start_byte:node.end_byte].decode()
        if not any(t in fragment for t in [' recompileNeeded =',' permitted =','DEFAULT_FAKEPLAYER_PROFILE =']):continue
        e=dict(sample,node_type='field_declaration',name=fragment.split('=')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
        e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end'])
        fields.append(e)
    assert len(fields)==3
    row['source_declarations']=fields
'''
footer=footer.replace('        rows.append(row)','        attach_fields(row)\n        rows.append(row)')
(b/'review.py').write_text(header+notes+fieldfn+footer)
print('Authored two semantic families; credit0')
