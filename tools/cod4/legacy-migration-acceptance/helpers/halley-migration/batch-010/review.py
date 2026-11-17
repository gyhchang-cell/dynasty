"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-010'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))



add('enderstorage-frequency-owner-disk-identity-to-shared-storage-key',[
 ('enderstorage/api/Frequency.java','read_internal'),('enderstorage/api/Frequency.java','write_internal'),('enderstorage/api/Frequency.java','Frequency'),('enderstorage/api/Frequency.java','readFromStack'),('enderstorage/api/Frequency.java','writeToStack'),('enderstorage/api/Frequency.java','writeToNBT'),('enderstorage/api/Frequency.java','hasOwner'),('enderstorage/api/Frequency.java','toString'),('enderstorage/api/Frequency.java','copy'),('enderstorage/api/Frequency.java','set'),('enderstorage/api/Frequency.java','setLeft'),('enderstorage/api/Frequency.java','setMiddle'),('enderstorage/api/Frequency.java','setRight'),('enderstorage/api/Frequency.java','setOwner'),('enderstorage/api/Frequency.java','clearOwner'),
 ('enderstorage/tile/TileFrequencyOwner.java','load'),('enderstorage/tile/TileFrequencyOwner.java','saveAdditional'),('enderstorage/tile/TileFrequencyOwner.java','setFreq'),('enderstorage/tile/TileFrequencyOwner.java','setLevel'),('enderstorage/tile/TileFrequencyOwner.java','readFromPacket'),
 ('enderstorage/item/ItemEnderStorage.java','updateCustomBlockEntityTag'),('enderstorage/item/ItemEnderStorage.java','getFreq'),('enderstorage/item/ItemEnderPouch.java','onItemUseFirst'),('enderstorage/item/ItemEnderPouch.java','use'),('enderstorage/block/BlockEnderStorage.java','use'),('enderstorage/block/BlockEnderStorage.java','getDrops'),('enderstorage/block/BlockEnderStorage.java','createItem'),
 ('enderstorage/tile/TileEnderChest.java','getStorage'),('enderstorage/tile/TileEnderChest.java','onFrequencySet'),('enderstorage/tile/TileEnderChest.java','activate'),('enderstorage/manager/EnderStorageManager.java','getStorage'),('enderstorage/manager/EnderStorageManager.java','instance'),('enderstorage/manager/EnderStorageManager.java','reloadManager'),('enderstorage/plugin/EnderItemStoragePlugin.java','createEnderStorage'),
 ('lib/colour/EnumColour.java','fromWoolMeta'),('lib/colour/EnumColour.java','getWoolMeta'),('lib/colour/EnumColour.java','fromDyeStack'),('lib/colour/EnumColour.java','getSerializedName'),('lib/util/ItemUtils.java','areStacksSameType'),('enderstorage/config/EnderStorageConfig.java','getPersonalItem')],
 '背包物品use、方块实体load、物品放置及实际颜色/私人锁交互恢复Frequency，manager据其规范字符串查找共享物品库存。',
 'Frequency compound：left/middle/right整数颜色，owner UUID可选、owner_name JSON Component可选；物品根Frequency，方块自身Frequency。实际世界存储索引为颜色串+可选owner UUID+,type=item。',
 '缺整个Frequency或三颜色字段时落默认白色频道；owner仅hasUUID才读取，owner_name单独按contains读取。hasOwner要求UUID和名字均非空，toString只有hasOwner时把UUID纳入索引，因此缺名字的UUID不会得到相同私人存储索引。新读取后放置更新tile，onFrequencySet重建并失效原itemHandler。',
 'owner_name不是单纯展示字段：缺失或JSON null将使本来存在UUID的状态按公共频道索引；不同名字文本只要非空则仍用UUID索引。不能只迁移owner UUID便宣称归属完整恢复。频率对象可变，但通常颜色/锁交互copy再setFreq，已创建storage的freq引用不能任意原位改色。pouch绑定时复制箱子频率，anarchy模式仅当前玩家UUID匹配才保留owner。直接用pouch打开存储不另检查当前玩家UUID，持有完整私有频率本身是访问凭据。',
 'Dynasty旧状态迁移应沿实际索引消费者检查所有参与身份的字段，避免把看似展示的字段丢弃；定义缺归属信息时保留待审而不是默默映射公共/默认对象。切换身份要同步失效旧缓存，不能让物理载体、保存索引和能力代理指向不同数据。',
 '未发现旧ID/旧频率整数转换，不声称存在。EnumColour.fromWoolMeta直接values()[id]，负值/超范围无保护；Component JSON解析无catch；复用write_internal不删除已存在而当前变null的owner键，常见writeToStack传新compound避免该特例。anarchy下createItem调用freq.setOwner(null)，所见setOwner(Player)会解引用player，静态存在NPE风险，未运行；不将此分支当成功移除owner示例。CodeChickenLib仅支持，动态4.4.0.+依赖不能证明指定运行二进制对应。',
 '物品/方块/pouch三种载体、三颜色/owner字段及manager lookup合一身份恢复链；不能按4096颜色或名字变体计数。与Waystones UUID目录引用有架构交叠，差异是显示名缺失参与私人索引及可变身份缓存；Kepler最终去重，credit0。')

add('enderstorage-item-inventory-capacity-reconciliation-and-two-file-commit-lifecycle',[
 ('enderstorage/storage/EnderItemStorage.java','loadFromTag'),('enderstorage/storage/EnderItemStorage.java','alignSize'),('enderstorage/storage/EnderItemStorage.java','saveToTag'),('enderstorage/storage/EnderItemStorage.java','EnderItemStorage'),('enderstorage/storage/EnderItemStorage.java','empty'),('enderstorage/storage/EnderItemStorage.java','getContainerSize'),('enderstorage/storage/EnderItemStorage.java','getItem'),('enderstorage/storage/EnderItemStorage.java','setItem'),('enderstorage/storage/EnderItemStorage.java','removeItem'),('enderstorage/storage/EnderItemStorage.java','removeItemNoUpdate'),('enderstorage/storage/EnderItemStorage.java','setChanged'),('enderstorage/storage/EnderItemStorage.java','openContainer'),('enderstorage/storage/EnderItemStorage.java','openInventory'),('enderstorage/storage/EnderItemStorage.java','closeInventory'),
 ('enderstorage/manager/EnderStorageManager.java','EnderStorageManager'),('enderstorage/manager/EnderStorageManager.java','load'),('enderstorage/manager/EnderStorageManager.java','save'),('enderstorage/manager/EnderStorageManager.java','getStorage'),('enderstorage/manager/EnderStorageManager.java','onWorldSave'),('enderstorage/manager/EnderStorageManager.java','init'),('enderstorage/manager/EnderStorageManager.java','onServerStarted'),('enderstorage/manager/EnderStorageManager.java','reloadManager'),('enderstorage/manager/EnderStorageManager.java','instance'),('enderstorage/manager/EnderStorageManager.java','requestSave'),('enderstorage/manager/EnderStorageManager.java','registerPlugin'),
 ('enderstorage/api/AbstractEnderStorage.java','setDirty'),('enderstorage/api/AbstractEnderStorage.java','setClean'),('enderstorage/api/AbstractEnderStorage.java','AbstractEnderStorage'),('enderstorage/plugin/EnderItemStoragePlugin.java','createEnderStorage'),('enderstorage/EnderStorage.java','EnderStorage'),
 ('lib/inventory/InventoryUtils.java','readItemStacksFromTag'),('lib/inventory/InventoryUtils.java','writeItemStacksToTag'),('lib/inventory/InventoryUtils.java','decrStackSize'),('lib/inventory/InventoryUtils.java','removeStackFromSlot'),('lib/util/ServerUtils.java','getSaveDirectory'),('lib/util/ServerUtils.java','getServer'),
 ('enderstorage/container/ContainerEnderItemStorage.java','ContainerEnderItemStorage'),('enderstorage/container/ContainerEnderItemStorage.java','quickMoveStack'),('enderstorage/container/ContainerEnderItemStorage.java','removed'),('enderstorage/container/ContainerEnderItemStorage.java','addPlayerSlots'),('enderstorage/tile/TileEnderChest.java','activate'),('enderstorage/tile/TileEnderChest.java','getCapability'),('enderstorage/config/EnderStorageConfig.java','load')],
 'ServerStarted重建服务端manager，实际访问指定Frequency时懒读对应库存；配置改变后load/save容量协调；Level.Save提交脏库存并更新双文件选择锁。',
 '存储条目size字节索引0/1/2对应9/27/54槽；Items列表每项short Slot及完整ItemStack，支持额外Numeric Quantity覆盖Count。世界EnderStorage目录data1.dat/data2.dat压缩NBT，lock.dat选择上次提交文件。',
 '按保存size先分配旧容量再读物品；扩容保留原索引，缩容仅非空栈数可装入目标时压紧，否则继续保留旧容量。save在open==0才额外尝试容量协调。manager为修改过的条目保留完整saveTag，写备用数据文件关闭后才写lock选择字节，切换下次目标。',
 '拒绝会溢出的缩容避免简单裁槽丢物品，代价是配置目标未立即生效；成功缩容改变槽位置但不是重新付费或生成物品。CCL支持的Quantity是数值标签覆盖，EnderStorage默认writer maxQuantity64不主动生成Quantity，不能宣传本mod所有大栈扩展兼容。load只读lock指向的一份，不会在该份损坏时尝试另份；save在磁盘写前便setClean并清dirty队列，若I/O失败后再继续进程，同一未再次修改对象不会自动重新排队，不能称完整故障事务。',
 'Dynasty恢复先按原容量/索引读全数据，再验证目标容量，无法无损压缩时保留原载荷并显式报告；永久进度迁移同样不能为满足新结构删除未映射字段。提交成功后再清脏/标记完成；读取备份不能凭文件存在推断其校验有效。',
 'size索引和配置整数均无本地范围校验；CCL readItemStacksFromTag不查Slot上下界，Quantity允许任意数值，坏一项可中断整条加载。lock值未限0/1，缺lock即忽略现存数据文件，不等于数据已空；异常只抛出，不作为删除任何用户文件的指令。无fsync/原子rename证明，也没实际测试断电或重生。CodeChickenLib固定1.20.1支持源版本4.4.0，双方属性均mc1.20.1/47.1.65，但主声明4.4.0.+，不证明已发布二进制精确对应。纯EnderLiquidStorage委托read/write仅旁读，不另作信用。',
 '库存payload reader/容量变换、真实菜单消费、脏队列和双文件提交是同一完整持久生命周期一条；CCL Quantity helper及通用库不另计，data1/data2不算两个实现。前条身份读器作为定位支持，与本条不同对象语义仍由Kepler裁定是否保留两条，credit0。')
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
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-010.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
