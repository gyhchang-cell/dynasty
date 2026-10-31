"""Two manual source reviews; no upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-025/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-025','batch-026');footer=prior[prior.index('def generate():'):].replace('batch-025','batch-026')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('actuallyadditions-player-interface-persistent-uuid-binding-probe-revocation-and-live-inventory-charge',
 pick('/tile/TileEntityPlayerInterface.java','readSyncableNBT')+whole('/tile/TileEntityPlayerInterface.java')+whole('/blocks/BlockPlayerInterface.java')+whole('/items/ItemPlayerProbe.java')+
 pick('/items/ItemPhantomConnector.java','clearStorage')+pick('/tile/TileEntityPhantomface.java','upgradeRange')+whole('/tile/CustomEnergyStorage.java')+
 pick('/tile/TileEntityBase.java','init register TileEntityBase readFromNBT writeToNBT readSyncableNBT writeSyncableNBT getUpdatePacket onDataPacket getUpdateTag handleUpdateTag sendUpdate update updateEntity saveDataOnChangeOrWorldStart sendUpdateWithInterval getCapability hasCapability')+
 whole('/util/VanillaPacketDispatcher.java')+pick('/blocks/base/BlockContainerBase.java','onBlockPlacedBy getDrops breakBlock shouldDropInventory')+pick('/util/StackUtil.java','isValid'),
 '玩家接口首次放置绑定placer UUID/name；探针捕获其他玩家身份，可将探针NBT转入接口；接口存档/同步恢复绑定后由实际capability提供对应玩家库存，服务器tick用恢复的能量给目标库存物品充能。',
 'Tile PlayerMost/PlayerLeast与PlayerName，只在非SAVE_BLOCK写入，Energy由CustomEnergyStorage统一读写；Probe root UUIDMost/UUIDLeast/Name。运行缓存oldPlayer/playerHandler/oldEnergy/range不是持久真值。',
 'read检查PlayerLeast且type!=SAVE_BLOCK才getUniqueId(Player)，不校验Most存在/UUID类型或当前用户权限；缺键不主动清旧connectedPlayer/name。writer未绑定不写该组，普通SAVE_TILE及SYNC保留，方块携带Data故意排除，因此拆放由placer重新绑定；调用BlockPlayerInterface绑定在super.read SAVE_BLOCK前，后者该类型不覆盖身份。name仅HUD展示，getPlayer以UUID查当前world玩家并distance<=range；未在线/同世界或超距返回null，不主动删除持久绑定。',
 '探针itemInteractionForEntity只检查主手确是本工具、目标Player且目标不sneak，存UUID/name；onUpdate在工具所在world找目标，离线/其他world或目标sneak清工具三键，并发消息，但已复制到Tile的绑定不随探针清除。onItemUse只要当前hand载荷UUIDMost和目标Tile类型即server覆盖绑定/dirty/update/clear工具，未重验目标在线、距离、同意或接口当前owner。工具撤销与持久绑定撤销不是同一个生命周期。getItemHandler按getPlayer结果引用变化重建PlayerInvWrapper；外部缓存先前返回的wrapper未见失效包装，不能声称后续每次操作复核距离。',
 'Dynasty应区分永久UUID身份/历史资格、临时可访问性及可携带物品策略，不能只因持久化就列入Clone永久白名单。迁移应成组校验UUID键，缺键处理明确，别让重复读取残留上次值；显示名不当主键。若旧任务册含身份载荷，应保留完整原Count/tag再按当前权威玩家接续；死亡恢复只复制审定永久字段，不带能量/远程访问缓存/免疫计时器。恢复后每个实际消费者复核活体世界、距离和权限，而非仅获取wrapper时验证。',
 '范围每server tick重新由头顶连续最多3个booster将32倍增，oldPlayer/range不从存档恢复；接口能量每格cap.receiveEnergy(false)后extractEnergyInternal，单格count必须1。changed局部始终false，故该if块不dirty/send；能量差触发interval发送但sendUpdate本身不markDirty。CustomEnergyStorage读Energy直接set、不限capacity/非负，未见该storage变更回调dirty；不能据此断言必丢档或原生保存事件行为。Forge PlayerInvWrapper/EnergyStorage/vanillaNBT底层未全文研究，未实际模拟缓存wrapper/换手/跨维度或死亡；本链不是PlayerEvent.Clone或旧ID别名实现。',
 '一个玩家远程接口身份对象家族，probe采集/工具撤销/复制/Tile持久恢复/显示/能量/库存消费者均支持同链；不是给UUID两个long/每个NBTType或能量codec加数。与023 UUID世界PlayerSave书籍进度对象不同：这里绑定他人身份并驱动真实库存capability；共享Tile基类与024/025codec/同步支持不计。credit0由Kepler最终裁定。')
add('actuallyadditions-spawner-changer-entity-type-payload-to-native-spawner-state-replacement',
 pick('/items/ItemSpawnerChanger.java','onItemUse')+whole('/items/ItemSpawnerChanger.java')+pick('/items/ItemPhantomConnector.java','clearStorage')+
 pick('/config/ConfigValues.java','defineConfigValues')+whole('/config/values/ConfigStringListValues.java')+pick('/util/StackUtil.java','shrink isValid'),
 '真实工具右击非玩家非Boss活体，将注册实体类型写入物品Entity字符串后杀死来源；带载荷工具用于原生MobSpawner，先移除旧SpawnPotentials/SpawnData再设置类型，dirty/update并清工具Entity，生存消耗。',
 '输入来源entity.class→EntityList.getKey ResourceLocation，ConfigStringListValues.SPAWNER_CHANGER_BLACKLIST当前配置；持久载体是ItemStack根tag.Entity非空string，目标是原生MobSpawnerBaseLogic.writeToNBT导出的compound。',
 'storeClickedEntity确保root compound、排除EntityPlayer且isNonBoss，取得注册名非空后精确字符串比黑名单，默认minecraft:villager_golem，由defineConfigValues加载currentValue；写Entity成功才itemInteractionForEntity调用entity.setDead。只带实体类型，不带源UUID/生命/装备/自定义tag/驯服主人。getStoredEntity只认非空字符串，无版本标记/旧名alias或注册存在校验。',
 '实际onItemUse server读取主手stack，不按回调hand取源；用该stack做canPlayerEdit(pos.offset(facing),facing,stack)，只接受TileEntityMobSpawner。逻辑writeToNBT保留其余目标属性，删除两组旧生成候选及SpawnData，再readFromNBT，然后new ResourceLocation(entity)并setEntityId；随后tile.markDirty与notifyBlockUpdate，再clearStorage(Entity)。非创造setHeldItem(hand,shrink主手stack1)；若offhand调用则读主手但写传入hand，源码存在角色不一致，未跑游戏不声称复现。恶意/旧非法Entity在删除旧状态之后才构造ResourceLocation，无catch/原载荷备份，不能称原子替换。',
 'Dynasty旧物品注册替代需在目标注册/格式校验成功后再改变来源；有选择清除旧结构以免覆盖新ID的思路可借鉴，但要先保护Count/tag和失败回退。仅目标类型迁移不等于恢复原实体/玩家永久进度；批准Clone白名单不能照搬实体全量序列化。对于失效旧ID应保留来源载荷并给出显式审计状态，不默认无提示地删源或重建默认栈。',
 '写入时实体类注册名通常合法，但历史/外部编辑载荷是否有效不再验证，使用时也不重跑黑名单；EntityList、ResourceLocation、原生Spawner.readFromNBT/setEntityId实际行为及生成事件未全文追原生实现、未执行。只能确定本mod调用顺序和显式剔除字段，不能声称旧SpawnData所有未知扩展都保留、合法类型一定实际spawn成功。工具配方清空等未审完整消费者不另算。',
 '捕获类型→物品载荷→清旧生成候选→nativeSpawner实际写回是一个转换家族；getter/黑名单每条/键删除/物品消耗不是独立实现。与MCA020墓碑完整实体快照和克隆不同，只携实体类型并覆写既有刷怪笼；两者广义搬运类比仍需主责语义比对。不是UUID接口链的换键克隆。credit0待Kepler。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=['/tile/TileEntityPlayerInterface.java'] if 'player-interface' in row['family'] else ['/config/values/ConfigStringListValues.java']
    out=[]
    for suffix in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode();e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
