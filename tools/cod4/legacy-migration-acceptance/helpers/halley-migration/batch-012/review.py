"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-012'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))





add('astralsorcery-tree-beacon-linked-faked-tree-persistent-state-and-reversion',[
 ('tile/TileTreeBeacon.java','readCustomNBT'),('tile/TileTreeBeacon.java','writeCustomNBT'),('tile/TileTreeBeacon.java','captureTree'),('tile/TileTreeBeacon.java','addComponent'),('tile/TileTreeBeacon.java','tick'),('tile/TileTreeBeacon.java','doHarvestCycle'),('tile/TileTreeBeacon.java','harvestTree'),('tile/TileTreeBeacon.java','validate'),('tile/TileTreeBeacon.java','remove'),('tile/TileTreeBeacon.java','onBreak'),('tile/TileTreeBeacon.java','getDimension'),('tile/TileTreeBeacon.java','onGrow'),('tile/TileTreeBeacon.java','clearServerCache'),
 ('tile/TileTreeBeaconComponent.java','tick'),('tile/TileTreeBeaconComponent.java','getTreeBeaconPos'),('tile/TileTreeBeaconComponent.java','setTreeBeaconPos'),('tile/TileTreeBeaconComponent.java','readCustomNBT'),('tile/TileTreeBeaconComponent.java','writeCustomNBT'),
 ('tile/base/TileFakedState.java','readCustomNBT'),('tile/base/TileFakedState.java','writeCustomNBT'),('tile/base/TileFakedState.java','setFakedState'),('tile/base/TileFakedState.java','getFakedState'),('tile/base/TileFakedState.java','revert'),('tile/base/TileEntitySynchronized.java','read'),('tile/base/TileEntitySynchronized.java','write'),('tile/base/TileEntitySynchronized.java','markForUpdate'),('tile/base/TileEntitySynchronized.java','removeSelf'),
 ('tile/base/TileEntityTick.java','tick'),('tile/base/TileEntityTick.java','getTicksExisted'),('tile/base/TileEntityTick.java','readCustomNBT'),('tile/base/TileEntityTick.java','writeCustomNBT'),('tile/base/TileNetwork.java','markForUpdate'),('tile/base/TileNetwork.java','readSaveNBT'),('tile/base/TileNetwork.java','writeSaveNBT'),
 ('block/base/BlockStarlightNetwork.java','onReplaced'),('block/tile/BlockTreeBeaconComponent.java','createNewTileEntity'),('base/TreeType.java','isTree'),('base/TreeType.java','getTreeGenerator'),('base/TreeType.java','register'),
 ('util/nbt/NBTHelper.java','getBlockStateFromTag'),('util/nbt/NBTHelper.java','getBlockStateNBTTag'),('util/nbt/NBTHelper.java','setBlockState'),('util/nbt/NBTHelper.java','readFromSubTag'),('util/nbt/NBTHelper.java','setAsSubTag'),('util/nbt/NBTHelper.java','readBlockPosFromNBT'),('util/nbt/NBTHelper.java','writeBlockPosToNBT'),('util/MiscUtils.java','getTileAt'),('util/MiscUtils.java','getWeightedRandomEntry'),('util/MiscUtils.java','captureBlockChanges'),('util/MiscUtils.java','canEntityTickAt'),('util/block/BlockUtils.java','getDrops'),('astralsorcery/common/CommonProxy.java','attachEventHandlers')],
 '真实树苗生长事件选同维最近灯塔，捕获生长方块并转换为组件；区块重载读主组件索引与各组件原BlockState，随后服务器tick继续收获，灯塔被替换时尝试恢复原树。',
 '主灯塔components列表每项BlockPos+weight，starlight和playerUUID；组件treeBeaconPos子compound链接，以及基类fakedState.registryName/properties和颜色；父类持久tick状态。',
 '主read先clear索引后put，重复坐标后者覆盖；组件reader将原方块注册名+匹配属性重建，从而真正getDrops以fakedState产生掉落，onBreak组件revert把保存状态放回世界。TreeWatcher运行索引按维度维护，在validate/remove重建，不靠保存静态WATCHERS。主索引和组件是同一棵持久树对象的双向关系，不可只恢复坐标或只恢复外观。',
 '组件每200tick查父灯塔，forceChunkLoad=false使父区块未加载时也返回null，随后removeSelf清为空气，而不是revert原树。缺/错treeBeaconPos子compound被helper返回null覆盖字段原ZERO，tick直接.equals有NPE风险；保存坐标ZERO也被当无主。主reader不验证weights/容量/对应组件父链接。harvestTree在未通过dropChance时return true才有机会随机移除组件，实际产出掉落后return false；不能按函数名猜移除发生在成功产出后。playerUUID只供赞助者颜色，不是所有权许可。',
 'Dynasty迁移有关联持久对象时，先读完整双侧身份和原始载荷，再延迟校验区分未加载/不存在，恢复不可凭坐标匹配就删除原内容。失效组件应隔离并可回滚，不能默认空气或整批清理；有语义的计时/临时starlight也不应纳入玩家永久Clone白名单。',
 'NBTHelper未知方块/AIR回默认AIR，未知属性忽略、坏属性解析catch，坏注册字符串无总catch；只保存BlockState未保存原TileEntity NBT，不能扩展宣称任意含库存方块都无损恢复。生成捕获标志未try/finally，异常可留captureBlockSnapshots开；未执行生成或删方块。父类网络能量完整网络图不在本候选范围，仅保留持久父入口支持；属性渲染不单计。',
 '主索引、组件原状态、树种生成、收获与解除同一链只提一条；每个树种/方块属性/组件/颜色/生命周期函数不计独立数量。与Waystones目录重连有部分模式相似，但持久对象为可还原的实体树状态；Kepler人工裁定，credit0。')

add('astralsorcery-celestial-gateway-world-directory-access-list-load-to-teleport',[
 ('data/world/GatewayCache.java','readFromNBT'),('data/world/GatewayCache.java','writeToNBT'),('data/world/GatewayCache.java','read',240),('data/world/GatewayCache.java','write',212),('data/world/GatewayCache.java','hasAccess'),('data/world/GatewayCache.java','onLoad'),('data/world/GatewayCache.java','offerPosition'),('data/world/GatewayCache.java','removePosition'),('data/world/GatewayCache.java','getGatewayNode'),('data/world/GatewayCache.java','getGatewayPositions'),('data/world/GatewayCache.java','updateGatewayNode'),('data/world/GatewayCache.java','update'),('data/world/GatewayCache.java','equals'),('data/world/GatewayCache.java','hashCode'),('data/world/GatewayCache.java','GatewayNode'),('data/world/GatewayCache.java','writeAccess'),('data/world/GatewayCache.java','getPos'),('data/world/GatewayCache.java','getOwner'),('data/world/GatewayCache.java','isLocked'),('data/world/GatewayCache.java','getAllowedUsers'),('data/world/GatewayCache.java','setOwner'),('data/world/GatewayCache.java','setLocked'),('data/world/GatewayCache.java','setAllowedUsers'),
 ('tile/TileCelestialGateway.java','readCustomNBT'),('tile/TileCelestialGateway.java','writeCustomNBT'),('tile/TileCelestialGateway.java','tick'),('tile/TileCelestialGateway.java','updateAccessInformation'),('tile/TileCelestialGateway.java','getOwner'),('tile/TileCelestialGateway.java','isLocked'),('tile/TileCelestialGateway.java','getAllowedUsers'),('tile/TileCelestialGateway.java','setOwner'),('tile/TileCelestialGateway.java','lock'),('tile/TileCelestialGateway.java','unlock'),('tile/TileCelestialGateway.java','canAddAllowedUser'),('tile/TileCelestialGateway.java','addAllowedUser'),
 ('auxiliary/gateway/CelestialGatewayHandler.java','onWorldInit'),('auxiliary/gateway/CelestialGatewayHandler.java','loadIntoCache'),('auxiliary/gateway/CelestialGatewayHandler.java','getGatewayNode'),('auxiliary/gateway/CelestialGatewayHandler.java','addPosition'),('auxiliary/gateway/CelestialGatewayHandler.java','removePosition'),('auxiliary/gateway/CelestialGatewayHandler.java','getFilter'),('auxiliary/gateway/CelestialGatewayHandler.java','forceLoad'),('auxiliary/gateway/CelestialGatewayHandler.java','onServerStart'),('auxiliary/gateway/CelestialGatewayHandler.java','onServerStop'),
 ('util/PlayerReference.java','deserialize'),('util/PlayerReference.java','serialize'),('util/PlayerReference.java','writeToNBT'),('util/PlayerReference.java','isPlayer'),('util/PlayerReference.java','getPlayerUUID'),('network/play/client/PktRequestTeleport.java','handler'),('block/tile/BlockCelestialGateway.java','onBlockActivated'),('block/tile/BlockCelestialGateway.java','onReplaced'),('util/MiscUtils.java','getTileAt'),('util/MiscUtils.java','transferEntityTo'),('astralsorcery/common/CommonProxy.java','scheduleDelayed'),('astralsorcery/common/CommonProxy.java','attachTickListeners'),('common/CommonScheduler.java','tick'),('common/CommonScheduler.java','addRunnable'),('common/CommonScheduler.java','canFire'),
 ('registry/RegistryData.java','init'),('astralsorcery/common/CommonProxy.java','attachEventHandlers'),('util/nbt/NBTHelper.java','readOptional'),('util/nbt/NBTHelper.java','writeOptional'),('util/nbt/NBTHelper.java','readList'),('util/nbt/NBTHelper.java','writeList'),('util/nbt/NBTHelper.java','readEnum'),('util/nbt/NBTHelper.java','writeEnum'),('util/nbt/NBTHelper.java','readBlockPosFromNBT'),('util/nbt/NBTHelper.java','writeBlockPosToNBT'),
 ('observerlib/common/data/WorldCacheDomain.java','getData'),('observerlib/common/data/WorldCacheDomain.java','getFromCache'),('observerlib/common/data/WorldCacheDomain.java','getCachedData'),('observerlib/common/data/WorldCacheDomain.java','getSaveDirectory'),('observerlib/common/data/WorldCacheDomain.java','getNewInstance'),('observerlib/common/data/WorldCacheDomain.java','createSaveKey'),('observerlib/common/data/WorldCacheManager.java','createDomain'),('observerlib/common/data/WorldCacheManager.java','doSave'),('observerlib/common/data/WorldCacheManager.java','scheduleSaveAll'),('observerlib/common/data/WorldCacheManager.java','cleanUp'),
 ('observerlib/common/data/WorldCacheIOThread.java','loadNow'),('observerlib/common/data/WorldCacheIOThread.java','loadDataFromFile'),('observerlib/common/data/WorldCacheIOThread.java','attemptLoad'),('observerlib/common/data/WorldCacheIOThread.java','scheduleSave'),('observerlib/common/data/WorldCacheIOThread.java','run'),('observerlib/common/data/WorldCacheIOThread.java','saveAllNow'),('observerlib/common/data/WorldCacheIOThread.java','saveNow'),('observerlib/common/data/WorldCacheIOThread.java','saveDataToFile'),('observerlib/common/data/WorldCacheIOThread.java','getDirectorySet'),('observerlib/common/data/WorldCacheIOThread.java','sanitizeFileName'),('observerlib/common/data/WorldCacheIOThread.java','DirectorySet'),('observerlib/common/data/WorldCacheIOThread.java','getErrorDirectories'),('observerlib/common/data/WorldCacheIOThread.java','onServerStart'),('observerlib/common/data/WorldCacheIOThread.java','onServerStop'),('observerlib/common/data/WorldCacheIOThread.java','flushAndSaveAll'),
 ('observerlib/common/data/base/GlobalWorldData.java','GlobalWorldData'),('observerlib/common/data/base/GlobalWorldData.java','writeData'),('observerlib/common/data/base/GlobalWorldData.java','readData'),('observerlib/common/data/base/GlobalWorldData.java','markDirty'),('observerlib/common/data/base/GlobalWorldData.java','markSaved'),('observerlib/common/data/base/GlobalWorldData.java','needsSaving'),('observerlib/common/data/base/GlobalWorldData.java','getSaveFile'),('observerlib/common/data/CachedWorldData.java','readIO'),('observerlib/common/data/CachedWorldData.java','writeIO'),('observerlib/common/data/CachedWorldData.java','getSaveKey'),('observerlib/common/CommonProxy.java','onServerStopping'),('observerlib/common/CommonProxy.java','onServerStarted'),('observerlib/common/CommonProxy.java','attachEventHandlers'),('observerlib/common/event/handler/EventHandlerIO.java','init'),('observerlib/common/event/handler/EventHandlerIO.java','onSave'),('observerlib/ObserverLib.java','ObserverLib')],
 'World.Load按维度恢复GatewayCache，区块中的gateway保留自身访问数据/登记标记；真实C2S传送在服务端查目标世界目录权限，通过后调度到ServerTick.END执行实体转移。世界保存和停服沿ObserverLib刷盘支持。',
 '世界gateway-cache.dat posList中坐标、显示JSON、颜色ordinal、locked、owningPlayer_present+UUID/名字、allowedUsers的index→玩家引用；方块重复保存locked/owner/allowedUsers及networkRegistered。文件按namespace目录和DIM_规范化维度键隔离。',
 'GatewayNode.hasAccess在owner缺失或未锁时放行，否则只认owner UUID或允许名单UUID。可选owner读取必须同时拥有_present=true，仅迁移子compound而漏旗标会变成公共访问。Cache reader加入HashSet且不clear，坐标相同按equals/hashCode去重，重复不同ACL不会覆盖已有node。onLoad强制查实际tile，查到null剔除，抛异常则保留；未见剔除后markDirty。',
 '实际传送读的是世界node而非目标tile的ACL；源tile仅查存在、多方块、天空。tick只在networkRegistered=false时尝试offer；若已有同坐标目录node，offer返回false而不复制tile的ACL，若保存true却目录丢失也不主动重建。允许名单和owner必须联同目录更新，迁移单侧可留旧权限。调度lambda捕获已授权的player/world/pos，执行前不重查目标node、ACL或目标结构，存在延迟边界；不能把网络handler外壳算独立实现。',
 'Dynasty带归属的持久目录恢复应从最终操作检查权威源，完整迁入存在旗标/UUID/维度和访问名单，明确两份副本的冲突合并规则；未加载与无效不同，修剪必须dirty并可追溯。真正实施迁移时要先核查原目录、保留未知载荷，不能以登记布尔推断数据完整或默认公开。',
 '没有旧ID映射声明。PlayerReference.deserialize无UUID/JSON防护、颜色ordinal直接数组索引，坏单项可能中断整个世界对象加载。ObserverLib先尝试主目录再备份，每次new实例，全部失败才返回新对象；失败文件复制/删除逻辑是静态风险，绝不执行。GlobalWorldData使用Guava Files.copy，不混同batch011 java.nio.Files.copy覆盖语义；但WorldCacheIOThread捕获IOException后仍markSaved，普通HashMap/标志跨线程无同步，GatewayCache修改也未全走其读写锁，故不主张可靠事务。维度名规范化可能碰撞。固定Observer1.5.2 commit且63个Java与主声明v77官方sources.jar字节一致，只证明源码对应、不证明实际运行二进制。filter文件与网络包旁读仅支持、未新增信用；创作/放置owner赋值全局事件不作已审查主张。',
 '世界目录、tile访问副本、玩家引用、真实传送及落盘/失败处理合一链；每个ACL槽、颜色、维度、备份、库方法不拆计。ObserverLib纯支持，不能作为通用库候选。与Waystones/EnderStorage身份家族交叠，差别是存在旗标可失去锁及双副本权威；Kepler可合并拒绝，credit0。')
def add_static_initializer(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    sample=next(r for r in INDEX if r['path'].endswith('/base/TreeType.java'))
    raw=(ROOT/sample['source']).read_bytes()
    node=next(n for n in walk(PARSER.parse(raw).root_node) if n.type=='static_initializer')
    fragment=raw[node.start_byte:node.end_byte].decode()
    e=dict(sample,node_type='static_initializer',name='<clinit>',start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
    e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end'])
    row['source_declarations']=[e]

def generate():
    rows=[]
    for spec in SPECS:
        evidence=[]
        for selector in spec['selectors']:
            suffix,name=selector[:2]
            matches=[r for r in INDEX if r['path'].endswith(suffix) and r['name']==name and (len(selector)<3 or r['start']==selector[2])]
            if not matches:
                raise ValueError(('No complete source method for evidence',selector))
            for r in matches:
                evidence.append(dict(r,revision=r['commit'],private_file=r['source'],start_line=r['start'],end_line=r['end'],method=r['name'],file_sha256=r['sourceSha256'],method_sha256=r['excerptSha256'],structural_fingerprint=r['normalizedSha256'],context=r['text'],source_url_or_coordinate='https://github.com/'+r['repo']+'/blob/'+r['commit']+'/'+r['path']+'#L'+str(r['start'])+'-L'+str(r['end'])))
        evidence=list({e['candidate_id']:e for e in evidence}.values())
        primary=evidence[0]
        row={k:v for k,v in spec.items() if k!='selectors'}
        row.update(primary)
        row.update(status='helper_reviewed_pending_coordinator',credit=0,accepted=False,evidence=evidence,preservation=spec['observation'],application_limit=spec['limits'],url=primary['source_url_or_coordinate'],excerpt=primary['text'],source_local=primary['source'],source_sha256=primary['sourceSha256'],line=primary['start'],end_line=primary['end'],runtime_validation='not_run_static_research_scope')
        if spec['family'].startswith('astralsorcery-tree-beacon'): add_static_initializer(row)
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-012.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
