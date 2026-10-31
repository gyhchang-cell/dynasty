"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-009'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))



add('travelersbackpack-old-builtins-to-upgrade-item-state-and-legacy-block-reader',[
 ('inventory/BackpackWrapper.java','converter'),('inventory/BackpackWrapper.java','BackpackWrapper'),('inventory/BackpackWrapper.java','fromStack'),('inventory/BackpackWrapper.java','initializeSize'),('inventory/BackpackWrapper.java','initializeSleepingBag'),('inventory/BackpackWrapper.java','isSizeInitialized'),('inventory/BackpackWrapper.java','loadHandler'),('inventory/BackpackWrapper.java','loadHandlers'),('inventory/BackpackWrapper.java','loadStorage'),('inventory/BackpackWrapper.java','loadUpgrades'),('inventory/BackpackWrapper.java','loadTools'),('inventory/BackpackWrapper.java','expandContents'),('inventory/BackpackWrapper.java','setStarterUpgrade'),('inventory/BackpackWrapper.java','createHandler'),('inventory/BackpackWrapper.java','createUpgradeHandler'),('inventory/BackpackWrapper.java','setSlotChanged'),('inventory/BackpackWrapper.java','setBackpackStack'),
 ('blockentity/BackpackBlockEntity.java','load'),('blockentity/BackpackBlockEntity.java','getOldDataBackpack'),('blockentity/BackpackBlockEntity.java','setBackpack'),('blockentity/BackpackBlockEntity.java','setBackpackFromNbt'),('blockentity/BackpackBlockEntity.java','setLevel'),('blockentity/BackpackBlockEntity.java','writeBackpack'),('blockentity/BackpackBlockEntity.java','saveAdditional'),('blockentity/BackpackBlockEntity.java','toItemStack'),
 ('inventory/Tiers.java','of'),('inventory/Tiers.java','getStorageSlots'),('inventory/Tiers.java','getUpgradeSlots'),('inventory/Tiers.java','getToolSlots'),
 ('util/NbtHelper.java','set'),('util/NbtHelper.java','get'),('util/NbtHelper.java','getOrDefault'),('util/NbtHelper.java','isInteger'),('util/NbtHelper.java','isBoolean'),('util/NbtHelper.java','isLong'),('util/NbtHelper.java','has'),('util/NbtHelper.java','serializeHandler'),('util/NbtHelper.java','serializeNBT'),('util/NbtHelper.java','getHandlerNbt'),('util/NbtHelper.java','expandTag'),('util/NbtHelper.java','deserializeHandler'),('util/NbtHelper.java','update'),('util/NbtHelper.java','serializeFluids'),('util/NbtHelper.java','deserializeLeftFluidStack'),('util/NbtHelper.java','deserializeRightFluidStack'),
 ('inventory/UpgradeManager.java','UpgradeManager'),('inventory/UpgradeManager.java','initializeUpgrades'),('inventory/UpgradeManager.java','applyUpgrade'),('inventory/UpgradeManager.java','canAddUpgrade'),('inventory/UpgradeManager.java','detectedChange'),('inventory/UpgradeManager.java','invalidateUpgrade'),
 ('items/upgrades/TanksUpgradeItem.java','isEnabled'),('items/upgrades/TanksUpgradeItem.java','getUpgrade'),('items/upgrades/CraftingUpgradeItem.java','isEnabled'),('items/upgrades/CraftingUpgradeItem.java','getUpgrade'),('upgrades/tanks/TanksUpgrade.java','TanksUpgrade'),('upgrades/tanks/TanksUpgrade.java','setFluids'),('upgrades/tanks/TanksUpgrade.java','createFluidHandler'),('upgrades/crafting/CraftingUpgrade.java','CraftingUpgrade'),('upgrades/crafting/CraftingUpgrade.java','createHandler'),('upgrades/crafting/CraftingUpgrade.java','setSlotChanged'),('inventory/upgrades/UpgradeBase.java','updateDataHolderUnchecked'),
 ('items/TravelersBackpackItem.java','use'),('items/TravelersBackpackItem.java','place'),('inventory/BackpackContainer.java','openBackpack'),('inventory/BackpackContainer.java','createMenu')],
 '真实物品打开/装备构造BackpackWrapper；旧方块实体load遇Tier触发整体旧格式转ItemStack，后续save只写Backpack新容器。',
 '旧物品LeftTank/RightTank/CraftingInventory，旧BE Tier/Inventory/ToolsInventory/LeftTank/RightTank；新物品tier及storage/upgrade/tool槽数、handler.Items/Size和升级物品内部Fluids/BackpackContainer。',
 '先初始化缺少槽数并装载handler，再converter按目标容量重排handler标签；旧双流体被装成一个TanksUpgrade，旧9格合成库存装成CraftingUpgrade，尝试插入空升级槽后无条件删除旧键。BE只要含旧Tier，读取新Backpack之后仍用旧结构重建物品；新保存集中写Backpack完整栈。',
 '这是宿主内置状态转嵌套升级物品的真实格式迁移，不是改显示键。setStarterUpgrade遇level=null、升级配置禁用或无空槽没有成功回执；converter仍删旧键，且已有新同种升级没有合并策略。BE旧Tier优先于已存在新Backpack，getOldDataBackpack无level时选择标准背包，无法保证保留原外观品类。loadHandler仅在Size较小时扩容，后面的converter在不等于目标时expandTag也可能裁掉越界槽；NbtHelper.deserializeHandler判断Size存在于根stack却从子compound取值，不能把稀疏Items数量当总容量。wrapper已存在时setBackpack仅换stack并同步少数升级，不重建全部inventory handlers，混合新旧输入尤其不能声称内存与标签立即一致。',
 'Dynasty迁移应先构造并校验目标状态且取得明确成功回执，再删除旧键；无依赖/无上下文/槽满时保留原数据待重试。对旧新同时存在定义优先级和合并冲突，保留Count/tag与真实身份；稀疏列表按声明容量和槽索引恢复，不按列表长度推断。',
 '仅固定官方1.20.1分支源码，不证明发布二进制或任何世界已成功恢复。边界均静态可见，不推定运行时一定到达。负数/超大槽数没有统一防护，expandTag丢弃范围外slot未返还，旧BE升级槽0/1无本地边界检查；损坏ItemStack/FluidStack仍依赖原生reader。未读全升级tick/GUI配方消费，不声称流体/合成全部功能验收。只证明升级对象构造与内部可持久handler已承接状态。无旧注册ID重映射，也不复制上游实现。',
 '旧BE reader、旧物品converter、两个升级分支、尺寸修复和支持reader/writer合一宿主迁移链；不按两种升级/各级背包/槽/键拆分。与Sophisticated等扩容存在交叠，具体旧内置→嵌套升级为本条差异，credit0待Kepler。')

add('travelersbackpack-wearable-item-custody-disk-death-placement-and-clone',[
 ('handlers/NeoForgeEventHandler.java','playerClone'),('handlers/NeoForgeEventHandler.java','attachCapabilities'),('handlers/NeoForgeEventHandler.java','onPlayerDrops'),('handlers/NeoForgeEventHandler.java','playerJoin'),
 ('capability/TravelersBackpackWearable.java','TravelersBackpackWearable'),('capability/TravelersBackpackWearable.java','hasBackpack'),('capability/TravelersBackpackWearable.java','getBackpack'),('capability/TravelersBackpackWearable.java','equipBackpack'),('capability/TravelersBackpackWearable.java','updateBackpack'),('capability/TravelersBackpackWearable.java','removeWearable'),('capability/TravelersBackpackWearable.java','removeWrapper'),('capability/TravelersBackpackWearable.java','remove'),('capability/TravelersBackpackWearable.java','synchronise'),('capability/TravelersBackpackWearable.java','serializeNBT'),('capability/TravelersBackpackWearable.java','deserializeNBT'),
 ('capability/TravelersBackpackCapability.java','createProvider'),('capability/TravelersBackpackCapability.java','Provider'),('capability/TravelersBackpackCapability.java','getCapability'),('capability/TravelersBackpackCapability.java','serializeNBT'),('capability/TravelersBackpackCapability.java','deserializeNBT'),('capability/CapabilityUtils.java','getCapability'),('capability/CapabilityUtils.java','isWearingBackpack'),('capability/CapabilityUtils.java','getWearingBackpack'),('capability/CapabilityUtils.java','synchronise'),
 ('util/BackpackDeathHelper.java','onPlayerDrops'),('util/BackpackDeathHelper.java','placeBackpack'),('util/BackpackDeathHelper.java','tryPlace'),('util/BackpackDeathHelper.java','placeBackpackInTheWorld'),('util/BackpackDeathHelper.java','getNearestEmptyChunkCoordinatesSpiral'),('util/BackpackDeathHelper.java','checkCoordsForBackpack'),('util/BackpackDeathHelper.java','isTopSolid'),('util/BackpackDeathHelper.java','areCoordinatesTheSame'),
 ('blockentity/BackpackBlockEntity.java','setBackpack'),('items/TravelersBackpackItem.java','updateCustomBlockEntityTag'),('common/BackpackManager.java','addBackpack'),('common/BackpackManager.java','getBackpackFile'),('common/BackpackManager.java','getPlayerBackpackFolder'),('common/BackpackManager.java','getBackpackFolder'),('common/BackpackManager.java','getWorldFolder'),
 ('TravelersBackpack.java','enableIntegration'),('TravelersBackpack.java','enableCurios'),('TravelersBackpack.java','isAnyGraveModInstalled'),('TravelersBackpack.java','TravelersBackpack'),
 ('network/ClientboundSyncCapabilityPacket.java','ClientboundSyncCapabilityPacket'),('network/ClientboundSyncCapabilityPacket.java','handle'),('util/PacketDistributorHelper.java','sendToPlayersTrackingEntityAndSelf')],
 '独立玩家可穿戴能力写盘/读盘、LivingDrops死亡处理、死亡或非死亡Clone以及登录/重生同步。',
 '能力持有真实Backpack ItemStack及运行时wrapper/owner；磁盘仅完整合法背包栈，wrapper由equip重建。Curios开启时可见穿戴状态改从Curios查找，未整份拷贝ForgeData。',
 'Clone对旧玩家revive后直接把旧getBackpack返回引用交新能力equip，无isWasDeath筛选也未copy/清旧能力；死亡drop开启keepInventory则保留，普通死亡尝试将同一背包放成方块并清穿戴，失败/坟墓mod则加入掉落实体并清穿戴。集成开启时本处理器只写恢复文件并return，由外部集成处理归属。',
 'Clone保留内容取决于先前死亡处理是否已清空能力，而不是每次死亡无条件额外生成背包。equip先remove再判断新栈类型，坏输入能清原持有状态；Owner与wrapper重建不作为永久字段复制。原玩家getBackpack返回可变栈，Clone未copy而共享引用；未finally移除或重新失效原实体，不能称严谨能力生命周期。同步包构造先复制backpackCopy，但精简memory列表时NbtHelper.set写的是原参数backpack，不是backpackCopy，可改服务端持久记忆匹配样本；因此同步不能被当纯展示无副作用。',
 'Dynasty需区分磁盘持久真值与Clone后新对象运行时代理，Clone只迁移批准永久字段并copy可变NBT；复核死亡之前是否已合法消耗/转移，防止双重恢复。迁移失败先验证目标类型再改原持有状态，客户端数据精简必须只操作副本。',
 'NeoForgeEventHandler只是文件名，此固定源实际导入net.minecraftforge并订阅FORGE总线，不额外当NeoForge移植。未读Curios集成最终死亡处理，不能证明开启集成后原生cap复制一定不重复。原生Player.revive行为及事件先后未运行核实。setBlockAndUpdate成功后若取BE/转NBT异常没有回滚，drop加入列表也未证明外部取消后的完整事务。上游恢复文件写入只做静态研究，无实际写档/备份执行；其秒级命名未防同玩家同种背包同秒覆盖。',
 '穿戴能力存取/Clone/死亡落地与失败掉落/同步均一条物品归属链；备份写器仅支持，恢复命令未本条研究不增数。与CorpseComplex库存子集不同，这里整体穿戴物身份及实体→方块归属转移，但共享Clone架构需主责最终判定，credit0。')

add('travelersbackpack-nested-memory-slot-format-repair-and-actual-insertion-policy',[
 ('util/NbtHelper.java','deserializeMemorySlots'),('util/NbtHelper.java','deserializeMemoryStack'),('util/NbtHelper.java','serializeMemorySlots'),('util/NbtHelper.java','serializeMemoryStack'),('util/NbtHelper.java','deserializeIntList'),('util/NbtHelper.java','serializeIntList'),('util/NbtHelper.java','getOrDefault'),('util/NbtHelper.java','get'),('util/NbtHelper.java','set'),
 ('inventory/BackpackWrapper.java','getMemorySlots'),('inventory/BackpackWrapper.java','getUnsortableSlots'),('inventory/BackpackWrapper.java','setMemorySlots'),('inventory/BackpackWrapper.java','setUnsortableSlots'),('inventory/BackpackWrapper.java','setData'),('inventory/BackpackWrapper.java','getStorageForInputOutput'),
 ('inventory/StorageAccessWrapper.java','insertItem'),('inventory/StorageAccessWrapper.java','extractItem'),('inventory/StorageAccessWrapper.java','matchesStack'),('util/ItemStackUtils.java','isSameItemSameTags'),('util/ItemStackUtils.java','isSameItemSameComponents'),('util/ItemStackUtils.java','checkComponentsIgnoreDamage'),
 ('network/ServerboundSlotPacket.java','handle'),('network/ServerboundSlotPacket.java','decode'),('network/ServerboundSlotPacket.java','encode'),('util/NbtHelper.java','serializeMemorySlotsPacket'),('util/NbtHelper.java','deserializeMemorySlotsPacket'),('blockentity/BackpackBlockEntity.java','getCapability'),('network/ClientboundSyncCapabilityPacket.java','ClientboundSyncCapabilityPacket')],
 '真实背包记忆槽/不可排序槽持久读取，服务端已打开SettingsMenu确认样本并保存；漏斗/管道暴露的StorageAccessWrapper实际依记忆槽和锁槽规则插入/抽出。',
 '新MemorySlots compound列表，每项Slot、Pair(ItemStack完整NBT及matchNbt)；旧MemorySlots.MemorySlots嵌套列表。不可排序等整数列表存在相同旧key.key容器修复。',
 '新getList为空时从同名compound里取旧同名列表，直接tag.put把旧嵌套替换成平列表，然后解析Slot、ItemStack、matchNbt；整数列表同规则，只作为同族支持。写器保存平列表。服务端packet用真实menu槽样本而非客户端任意ItemStack；空槽可沿用原记忆样本，仍空则跳过。',
 '兼容读取会原地改持久tag，且以列表为空作为回退条件，没有区分合法新空列表、缺键和类型错误。读取出的记忆样本实际优先接收匹配物品，之后普通目标槽若不可排序就拒绝；extract对不可排序槽也拒绝。matchNbt=true的真实比较忽略Damage，Hose同物品还绕过NBT比较，不能描述成严格全NBT一致。服务端保存旧嵌套布局会在此读时展平，但网络构造的精简分支反而写原背包并丢matchNbt样本标签，迁移验证要覆盖非reader的写入路径。',
 'Dynasty兼容读取应区别缺失、类型损坏和用户有意清空，明确转换是否原位并只在成功恢复后提交；用实际功能消费者验证持久旧字段仍控制玩法，不能凭读取字符串即宣称进度恢复。迁移后同步/界面路径也不能修改权威原始数据。',
 'Slot负数/越界/重复没有迁移过滤，StorageAccessWrapper在记忆slot插入会依赖底层handler边界；ServerboundSlotPacket.getSlot同样没本地范围保护。列表空回退会用空旧列表替换错误类型数据，没有旁路留存。这里未声称sorter/全部升级过滤器同样通过验收，也未运行漏斗/界面或任何游戏。同步副作用是静态源可见，持久落盘时机未知。',
 '记忆compound列表和整数列表同一种旧key.key展平模式合一条，不按键/设置项加数。与前两链共享宿主NBT及同步仅作为支持；本条独立对象是有真实自动插入/锁槽消费的持久过滤规则。credit0由Kepler语义去重。')
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
    (DOC/'batch-009.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
