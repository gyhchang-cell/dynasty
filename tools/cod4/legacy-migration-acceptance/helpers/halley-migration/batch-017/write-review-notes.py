"""Author two manually read durable gameplay families; no upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
old=(b.parent/'batch-013/review.py').read_text()
header=old[:old.index("add('akashictome")].replace('batch-013','batch-017')
footer=old[old.index('def generate():'):].replace('batch-013','batch-017')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
add('forestry-legacy-circuit-uid-restoration-to-farm-control',
 pick('/core/circuits/CircuitBoard.java','CircuitBoard writeToNBT onLoad onInsertion onRemoval onTick getSocketType')+
 pick('/core/circuits/CircuitRegistry.java','registerDeprecatedCircuitReplacement getCircuit getCircuitBoard isChipset getDefaultLayout getLayout registerCircuit')+
 pick('/core/circuits/Circuit.java','Circuit getUID')+
 pick('/core/circuits/ItemCircuitBoard.java','createCircuitboard get')+
 pick('/farming/ModuleFarming.java','doInit registerRecipes')+
 pick('/farming/circuits/CircuitFarmLogic.java','CircuitFarmLogic onLoad onInsertion onRemoval onTick')+
 pick('/farming/logic/FarmProperties.java','FarmProperties getLogic')+
 pick('/farming/logic/FarmLogic.java','FarmLogic setManual isManual')+
 pick('/farming/multiblock/FarmController.java','FarmController writeToNBT readFromNBT refreshFarmLogics setFarmLogic resetFarmLogic getFarmLogic setSocket getSocketType cleanExtents doWork setUpFarmlandTargets cultivateTargets plantGermling')+
 pick('/farming/multiblock/InventoryFarm.java','plantGermling')+
 pick('/farming/FarmHelper.java','cultivateTarget')+
 pick('/farming/logic/FarmLogicCrops.java','FarmLogicCrops maintainCrops trySetCrop')+
 pick('/farming/logic/FarmLogicWatered.java','FarmLogicWatered cultivate maintainSoil maintainWater trySetSoil trySetWater canPlaceWater couldFlow'),
 '旧电路板物品随农场sockets库存NBT重载；refreshFarmLogics先重建默认控制逻辑，再读取旧电路UID，调用board.onLoad恢复各方向种植逻辑，实际doWork/cultivateTargets进入该逻辑种植并扣种苗。不是只有重命名表或tooltip。',
 'CircuitBoard T short、可选LY字符串、CA compound中的I0..I3 UID；物品自身metadata另存电路板类型。ModuleFarming.registerRecipes实际注册managedCereal/manualCereal/managedVegetable/manualVegetable四个旧UID，映射到已注册的managedCrops/manualCrops电路对象；农场持久sockets slot0持有此物品。',
 'getCircuit优先deprecatedCircuits，再当前circuits，故替代表能覆盖同名当前UID；四别名只合一链。CircuitBoard读取四槽逐个解析，未知UID留null；onLoad遍历非null电路，以slot序号映射FarmDirection，CircuitFarmLogic调用setFarmLogic并清extents。FarmController读NBT后立即refresh，工作周期取该方向logic，通过FarmHelper.cultivateTarget进入FarmLogicWatered/FarmLogicCrops，plantGermling成功才decrStackSize1，证实恢复到实际玩法消费者。',
 'LY未知时调用getDefaultLayout却未接收返回值，因此layout仍null；getSocketType返回NONE，但FarmController.refreshFarmLogics这里仍直接getCircuitBoard/onLoad，不验证layout或socket类型。T使用values()[short]无范围保护；固定四槽读取不按板型socket数裁剪。reader丢弃未知电路UID，写新compound只写解析后的nonnull电路，不能声称无损保留。getCircuitBoard仅查hasTagCompound，不验证确为chipset；正常setSocket入口有isChipset，旧NBT库存加载后的refresh没有同等检查。CircuitFarmLogic.isManual默认false看似覆盖manual，但实际FarmLogic.setManual是no-op，最终isManual由构造final值决定；已核实不能据此报告手动模式重置bug。',
 'Dynasty旧ID兼容应验证真实旧别名注册与最终业务消费，区分注册表别名、载荷内部UID和外层物品metadata。应保留未知原UID/载荷并记录明确兼容状态，按当前消费者要求检查范围、类型和上下文，再重建派生逻辑；默认函数必须真正赋值且不能当迁移成功证据。永久任务迁移只复制审定白名单，不把电路工作缓存类临时状态纳入玩家Clone。',
 '未运行游戏；原生ItemStack/Forge数据修复、外部IFarmable.plantSaplingAt的各模组实现及多方块底层磁盘事务未全审，不宣称所有作物结果或刷盘原子性。setSocket有onLoad后再onInsertion的重复调用，当前setFarmLogic覆盖式更新，不能直接泛化为所有电路幂等。read缺LY/坏T/未知UID的行为按源码静态观察；多方向/四别名/板型/颜色不是独立信用。CircuitLibrary的read/write空实现明确排除。',
 '唯一研究对象为旧电路载荷恢复到真实农场控制；注册表、板型、方向、onLoad/onInsertion、四别名及消费者支持方法同链合并一条。与batch015一般registry/BE remap不同在物品内部UID及可执行控制逻辑；同为旧别名主题仍交Kepler最终跨主账去重，credit0。')

add('forestry-trade-station-dual-persistence-to-order-stock-consumption',
 pick('/mail/TradeStation.java','TradeStation readFromNBT writeToNBT handleLetter countFillableOrders canReceivePayment countStorablePayment getSurplusAttachments hasPaper removePaper canPayPostage getPostage getNumStamps removeStamps removeTradegood isValid invalidate setVirtual')+
 pick('/mail/inventory/InventoryTradeStation.java','InventoryTradeStation canSlotAccept canExtractItem')+
 pick('/mail/tiles/TileTrader.java','TileTrader readFromNBT writeToNBT getInternalInventory setAddress handleSetAddressRequest isLinked onRemoval updateServerSide')+
 pick('/core/owner/OwnerHandler.java','readFromNBT writeToNBT readData writeData getOwner')+
 pick('/mail/PostRegistry.java','getTradeStation getOrCreateTradeStation deleteTradeStation')+
 pick('/mail/PostOffice.java','refreshActiveTradeStations lodgeLetter collectPostage')+
 pick('/mail/PostalCarrier.java','handleTradeLetter')+
 pick('/mail/Letter.java','Letter writeToNBT requiredPostage getAttachments addAttachments countAttachments isMailable')+
 pick('/mail/MailAddress.java','MailAddress writeToNBT isValid toString')+
 pick('/mail/gui/ContainerTrader.java','ContainerTrader')+
 pick('/core/tiles/TileForestry.java','readFromNBT writeToNBT getInternalInventory setInternalInventory')+
 pick('/core/inventory/InventoryAdapter.java','InventoryAdapter copy readFromNBT writeToNBT setInventorySlotContents decrStackSize')+
 pick('/core/inventory/InventoryPlain.java','InventoryPlain readFromNBT writeToNBT setInventorySlotContents decrStackSize')+
 pick('/core/utils/InventoryUtil.java','readFromNBT writeToNBT tryAddStacksCopy tryAddStack addStack')+
 pick('/core/utils/ItemStackUtil.java','containsSets condenseStacks isCraftingEquivalent'),
 '交易站世界存档恢复报价、付款模板、纸邮票和货物库存，真实信件订单进入handleLetter，按库存与付款计算订单量，寄回货物并将付款写库存/扣纸邮票货物。与batch016单纯玩家邮箱不同，此对象具有持久订单配置与真实交换经济消费。',
 'WorldSavedData TradePO_<trader address>含owner/address、VRT/IVL及INV40槽；TileTrader另由TileForestry字段inventory保存一份本地fallback INV、address、OwnerHandler owner。世界站库存0报价、1..4交换模板、5..10纸、11..14邮票、15..29收款、30..39货物。',
 'TradeStation reader按存在owner/address恢复，bool缺省false；isValid只检查!isInvalid。PostRegistry按地址取cached/worlddata；getOrCreate命中已有站不会校验当前tile的owner，找不到则创建空库存。TileForestry读写字段inventory；TileTrader服务端有效address时getInternalInventory却转向世界TradeStation，两份持久对象间未见恢复时拷贝合并。故世界文件缺失时新空站可能遮蔽已恢复fallback，不能当历史库存不存在。',
 'handleLetter用ItemStackUtil.containsSets算可付订单；非virtual再按可供货量和模拟收款容量限制。先寄reply，再将exchange模板的副本写入收款槽，扣纸/邮票/货物，最后dirty；并非保留信内付款原栈NBT。containsSets的正常匹配在模板NBT为空时容许同item的NBT变体，而getSurplusAttachments去除付款只isItemEqual不比tag，需明确有损/变体风险。virtual跳过若干供货/资源检查，但后段库存修改仍执行；doLodge=false也未包围实际库存修改，不能把它当纯预演。相关删除/invalidate源码只读，未执行任何文件操作。',
 'Dynasty迁移应识别真正权威数据源，校验外层目录、内嵌owner与对象引用，缺独立世界文件时保留/隔离本地旧库存，不默认空对象覆盖。对旧物品和任务迁移，解析→模拟容量→目标提交→源扣减/标记须有明确成功边界；复制实际原始ItemStack Count/tag而非重造模板。只迁永久白名单；VRT/权限/运行时计时等不能未经审定搬入玩家Clone。',
 '此链与batch016共享Letter/PostOffice/地址/库存codec，重复支持不加信用，保守等待Kepler判断交易站对象是否足够独立。getTradeStation缓存命中不复验invalid，invalidate本身无dirty；文件delete失败仅日志，磁盘/崩溃事务未验证。OwnerHandler不是ACL，ContainerTrader本类未见owner判断不等于已证明全局未授权操作，未深读ContainerTile所有父层。库存NBT reader绕过UI槽位过滤，hasPaper统计纸区域任意非空栈count而removePaper只扣PAPER；正常UI过滤与坏旧NBT须区分。底层原生NBTUtil、容器与ItemStack行为仅按调用接口，不宣称已运行测试或证明可利用。',
 '一条订单配置/双权威持久对象/库存交换恢复家族；不将40槽、货物付款、virtual、owner、邮费、delete风险或simulate标志各算实现。batch016玩家邮件送达与processed边界为高重复风险家族，本条独立部分仅交易站恢复和订单货物/付款状态机；如主责判定同链必须合并而不是增加信用。credit0。')
'''
attach='''\ndef attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=([('/core/circuits/CircuitRegistry.java',['deprecatedCircuits','circuits =']),('/core/circuits/CircuitBoard.java',['circuits;','layout;']),('/farming/logic/FarmLogic.java',['isManual;']),('/farming/circuits/CircuitFarmLogic.java',['isManual ='])] if 'legacy-circuit' in row['family'] else [('/mail/TradeStation.java',['static final','isVirtual =','isInvalid =']),('/mail/PostRegistry.java',['cachedTradeStations']),('/mail/tiles/TileTrader.java',['ownerHandler ='])])
    decl=[]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for node in walk(PARSER.parse(raw).root_node):
            if node.type!='field_declaration':continue
            fragment=raw[node.start_byte:node.end_byte].decode()
            if not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=node.type,name=fragment.split('=')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
            e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);decl.append(e)
    row['source_declarations']=decl
'''
footer=footer.replace('        rows.append(row)','        attach_declarations(row)\n        rows.append(row)')
(b/'review.py').write_text(header+notes+attach+footer)
print('Authored two complete gameplay-family notes; credit0')
