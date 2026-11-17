"""Two manually read gameplay persistent objects; no credit from supports."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-023/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-023','batch-024');footer=prior[prior.index('def generate():'):].replace('batch-023','batch-024')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('actuallyadditions-laser-connection-world-graph-restoration-to-real-energy-delivery',
 pick('/misc/apiimpl/LaserRelayConnectionHandler.java','readNetworkFromNBT')+whole('/misc/apiimpl/LaserRelayConnectionHandler.java')+whole('/misc/apiimpl/ConnectionPair.java')+
 whole('/data/WorldData.java')+whole('/api/laser/Network.java')+
 whole('/tile/TileEntityLaserRelay.java')+whole('/tile/TileEntityLaserRelayEnergy.java')+
 pick('/tile/TileEntityInventoryBase.java','TileEntityInventoryBase readSyncableNBT writeSyncableNBT loadSlots saveSlots')+
 pick('/tile/TileEntityBase.java','TileEntityBase update updateEntity readFromNBT writeToNBT readSyncableNBT writeSyncableNBT hasCapability getCapability sendUpdate')+
 pick('/items/ItemLaserWrench.java','onItemUse')+pick('/items/ItemPhantomConnector.java','getStoredPosition getStoredWorld storeConnection clearStorage')+
 pick('/ActuallyAdditions.java','preInit serverStarted serverStopped')+pick('/util/StackUtil.java','isValid getEmpty'),
 '真实激光扳手建边、WorldData Networks保存/恢复连接图；Tile重载从世界图取network，Energy capability实际receiveEnergy沿恢复端点找到邻接受能器并执行receiveEnergy。不同等级/能量流体物品方向不拆数，本批追到能量实际消费者。',
 'WorldData.Networks列表→每Network.Network列表→ConnectionPair的x0/y0/z0、x1/y1/z1、SuppressRender、可选Type枚举名。Tile Energy.Mode字符串另存SAVE_TILE/SYNC但不存SAVE_BLOCK；range upgrade库存走Items codec；cachedNetwork/changeAmount为内存派生缓存。',
 'world graph reader逐pair建立新Network并原样加入ConcurrentSet，没有逐项类型catch或端点存在/维度/距离复验；Type空缺保留null，非空非法LaserType.valueOf抛异常。Type缺省不等于已迁移到ENERGY：真实Energy消费者按端点TileEntityLaserRelayEnergy实例工作，未按pair.type过滤。Tile Connections列表仅NBTType.SYNC发送/接收，SAVE_TILE实际连接真值在WorldData；SYNC先remove当前relay网络再按列表add，重建使用this.type而非pair存储type，不把同步路径当第二个存档迁移。',
 '扳手创建时验证同一world对象/相同relay.type/最小range；world载图和getNetworkFor只按坐标，WorldData又是静态唯一data，连接未存维度，不能声称恢复后仍具有同等维度检查。Energy能力入口→transmitEnergy→getNetwork→transfer遍历端点，仅loaded并为energy tile、输出模式允许才找receiversAround；接收器先simulate，再真实receive，按位置去重，损耗计入transmitted。邻居表由world-start更新重建，network.changeAmount让缓存失效，writer不保存该运行缓存。',
 'Dynasty旧ID/状态恢复要区分持久图真值和重建缓存；保存身份/维度/注册类型的原始值，在解码失败时保留载荷且隔离坏项，不能直接清全集再读后丢失原始别名。创建时的guard不自动覆盖存档恢复路径；能力/缓存刷新属于目标就绪条件，不能把成功解析看成玩法恢复已验收。玩家Clone只迁永久白名单，不带这些缓存/传输计时。',
 '这是真实Minecraft能量网络玩法，非通用网络库；包/ConcurrentSet/合并工具仅支持不计。未运行外部capability、跨维度世界、丢包、能量损耗或存档测试；未展开高级relay/流体/物品实际搬运，不给其额外参考。ConnectionPair.equals同序任一端匹配便true而未override hashCode，集合去重契约有静态风险，但未据此宣布复现网络损坏。Mode未知非空也valueOf异常；base updateEntity存在其他共享能量/流体分支，未把它们当本次已读消费者信用。',
 '整个世界连接图含扳手/WorldData/Tile同步/实际Energy transfer一族。023为PlayerSave对象时已将同WorldData读取顺序与readNetworkFromNBT作限制支持，无网络信用；本条只有完整不同持久对象及实际消费者，若主责仍判父容器同链则合并。能量等级、Mode、边/端点、共同codec和辅助方法不拆数，credit0待Kepler。')

add('actuallyadditions-bag-items-list-restoration-filter-policy-and-remainder-writeback',
 pick('/inventory/ContainerBag.java','ContainerBag')+whole('/inventory/ContainerBag.java')+whole('/items/ItemBag.java')+
 pick('/items/ItemDrill.java','loadSlotsFromNBT writeSlotsToNBT')+
 whole('/tile/TileEntityInventoryBase.java')+whole('/util/ItemStackHandlerAA.java')+
 whole('/tile/FilterSettings.java')+
 whole('/inventory/slot/SlotItemHandlerUnconditioned.java')+whole('/inventory/slot/SlotDeletion.java')+whole('/inventory/slot/SlotImmovable.java')+
 pick('/inventory/slot/SlotFilter.java','checkFilter isFilter')+
 pick('/inventory/GuiHandler.java','getServerGuiElement')+pick('/event/CommonEvents.java','onItemPickup')+
 pick('/util/ItemUtil.java','canBeStacked')+pick('/util/StackUtil.java','isValid getEmpty grow'),
 '真实普通/虚空背包打开Container，从当前主手物品Items/Filter/AutoInsert恢复，操作关闭写回；普通袋对外容器右键实际逐槽insert并将剩余写回，自动捡拾读取相同库存与filter，虚空方向仍合一族。',
 '普通袋28槽、虚空1槽，ItemStack root.Items为按索引位置排列的compound列表，无Slot字段；每项完整ItemStack id/Count/Damage/tag由原生构造/写出。Filter嵌套Items四槽+Whitelist/Meta/NBT/Mod/Oredict；AutoInsert布尔。Container以sack对象引用确认仍是主手，不持久UUID。',
 'loadSlots以当前容量循环并setStack：列表项有id才new ItemStack，否则EMPTY；没有保留原始未知项/超出容量的旁路；saveSlots重建正好当前容量的列表并写空compound占位，超过容量的旧条目下次写回被截。底层未知注册ID是否变EMPTY依原生ItemStack解析，未展开原生不当确定复现。Filter.read无hasKey分支，缺Filter或缺字段时getBoolean/getInteger覆盖构造默认，普通袋原本respectMeta=true会在含NBT却无Filter时被清false；不是兼容旧策略的明确升级。',
 'ItemBag.onItemUse从袋载入独立库存，外部handler.insertItem(false)返回remain不等于原输入才更新袋槽，最后仅changed写回；没有先清整袋再尝试插入。CommonEvents自动插入保留NBT相等堆叠约束，普通袋改变后写回，虚空袋直接清拾取物。Container.canInteractWith用主手stack==sack；固定热栏SlotImmovable和SWAP guard阻止移走，close仍重新取currentItem并仅检instanceof ItemBag，无UUID/同对象复核，所以不称所有关闭边界均原子保障。',
 'Dynasty原栈迁移须保留Count/tag和未知原ID，有限槽位读取应有溢出/未知项保留策略，避免重写当前容量时静默截旧载荷。借鉴目标接收结果返回余量后写回源，但目标与源写回仍非持久事务；Clone和旧物品恢复只使用审定永久数据，不把Filter/AutoInsert等临时容器配置当任务进度。缺字段恢复旧默认需要明确而不是全部getBoolean=false。',
 '普通袋/虚空/过滤子物品、捡拾与GUI均同链支持，不加独立信用。没运行满包、外部handler返回异常、关闭切物品或服务器保存测试；ItemBag.getNBTShareTag返回null不代表服务器丢库存，标准容器同步未运行。SlotFilter.checkFilter调用slotClick具体交互/ContainerFilter未沿到全部逻辑，不声称嵌套filter所有路径已审；真实普通ItemStack匹配分支和源/余量已完整阅读。共用TileInventory codec还供巨箱/钻头，不能以换消费者名重复计普通读写。',
 '一个背包持久载荷与真实恢复/消费/回写家族；28槽/1槽、4过滤格、多个布尔、普通/虚空、GUI/pickup/手持方向不拆数。将来巨箱若提交必须有独立升级载荷转移语义，不能再把相同loadSlots当新reader。主责Kepler最终去重，credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    suffixes=(['/misc/apiimpl/ConnectionPair.java','/api/laser/Network.java','/tile/TileEntityLaserRelay.java','/tile/TileEntityLaserRelayEnergy.java'] if 'laser-connection' in row['family'] else ['/inventory/ContainerBag.java','/items/ItemBag.java','/tile/FilterSettings.java','/util/ItemStackHandlerAA.java'])
    out=[]
    for suffix in suffixes:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
