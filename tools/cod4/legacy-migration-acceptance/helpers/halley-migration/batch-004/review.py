"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-004'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

add('carryon-player-owned-carried-state-and-clone-placement',[
 ('Common/src/main/java/tschipp/carryon/mixin/PlayerMixin.java','onReadAdditionalSaveData'),
 ('Common/src/main/java/tschipp/carryon/mixin/PlayerMixin.java','onAddAdditionalSaveData'),
 ('Common/src/main/java/tschipp/carryon/mixin/PlayerMixin.java','setCarryOnData'),('Common/src/main/java/tschipp/carryon/mixin/PlayerMixin.java','getCarryOnData'),
 ('common/carry/CarryOnData.java','CarryOnData'),('common/carry/CarryOnData.java','getNbt'),('common/carry/CarryOnData.java','setBlock'),('common/carry/CarryOnData.java','getBlock'),('common/carry/CarryOnData.java','getBlockEntity'),('common/carry/CarryOnData.java','setEntity'),('common/carry/CarryOnData.java','getEntity'),('common/carry/CarryOnData.java','clear'),
 ('common/carry/PickupHandler.java','canCarryGeneral'),('common/carry/PickupHandler.java','tryPickUpBlock'),('common/carry/PickupHandler.java','tryPickupEntity'),
 ('Forge/src/main/java/tschipp/carryon/events/CommonEvents.java','onClone'),('Forge/src/main/java/tschipp/carryon/events/CommonEvents.java','onBlockClick'),('Forge/src/main/java/tschipp/carryon/events/CommonEvents.java','onEntityRightClick'),
 ('common/carry/PlacementHandler.java','placeCarriedOnDeath'),('common/carry/PlacementHandler.java','placeCarried'),('common/carry/PlacementHandler.java','getDeathPlacementPos'),
 ('common/carry/PlacementHandler.java','tryPlaceBlock'),('common/carry/PlacementHandler.java','getPlacementState'),('common/carry/PlacementHandler.java','updateProperty'),('common/carry/PlacementHandler.java','tryPlaceEntity'),
 ('CarryOnCommon.java','onCarryTick'),('CarryOnCommon.java','onPlayerAttacked'),('CarryOnCommon.java','potionLevel')],
 '玩家搬起方块或实体，将实际对象转入玩家 CarryOnData；读盘后手动放置或 PlayerEvent.Clone 消费/转交。',
 '玩家根 CarryOnData compound：type 枚举、block/tile 或 entity 快照、activeScript codec，以及 keyPressed、selected、tick。',
 '缺 CarryOnData 保持默认空；缺 type 为 INVALID。非 PLAYER 搬运在 keepInventory 或非死亡 Clone 时转交新玩家；否则旧玩家位置自动放回对象，随后清搬运状态。',
 '数据通过同步实体 compound 存储，getter 先 copy 后构造，setter 每次重写 selected 为目标玩家当前热栏并 tick 为当前 tickCount。拾取先保存 blockstate/带 id 的 blockentity 或 entity NBT，再删除原世界对象；放置按当前位置/邻接关系重建朝向、水浸与 blockentity。普通死亡的寻找空位只测试 canSurvive/replace/unobstructed，找不到返回原位置；放置返回值未核验就 clear。EntityType.create 失败会 clear 局部 CarryOnData 并返回 AreaEffectCloud 占位，不是保留原坏快照。Clone 转交先 setCarryData(newPlayer,carry)，然后才复制 oldPlayer.selected；因为 setter 已写入新玩家之前的 selected，后续 onCarryTick 可能再次选中该先前槽。',
 '借鉴选择性永久域与死亡/End 路径分流，但 Dynasty 永久进度不能照搬整份搬运 compound；keyPressed/tick/选槽和脚本 loop 属运行时或交互状态。旧物品 ID 转换应保留原快照并验证恢复成功，再清旧表示，不能由 addFreshEntity/setBlock 未确认结果就删唯一副本。',
 '固定 branch1.20 的真实 commit 含 HolderLookup、SynchedEntityData.Builder 等较新 API，未证明对应可编译1.20.1版本，不作直接移植模板。CarryType.valueOf 与 activeScript 解码错误会抛出，没有旧 type/旧 ID 映射。getNbt 在 activeScript=null 时不主动删旧 activeScript 键，但 clear 新建 compound；不得声称任意 setter 均清掉脚本。未逐层审查所有 Matchables codec/Minecraft内部创建，不保证坏快照容错、跨维度UUID冲突或崩溃原子性。未运行上游代码/游戏。',
 '方块、实体、玩家乘骑、读盘、死亡转交与各平台事件同一个搬运生命周期，合为一条；Fabric/NeoForge 移植不计。与先前 corpse/灵魂盒/实体快照容器有广义家族风险，本条 owner 是玩家持久搬运域和 Clone 放置策略，由 Kepler 判最终独立性。')

add('toolbelt-stack-owned-stable-slot-format-and-upgrade-preservation',[
 ('belt/ToolBeltInventory.java','getStackInSlot'),('belt/ToolBeltInventory.java','getSlots'),('belt/ToolBeltInventory.java','getTag'),('belt/ToolBeltInventory.java','setStackInSlot'),('belt/ToolBeltInventory.java','insertItem'),('belt/ToolBeltInventory.java','extractItem'),('belt/ToolBeltInventory.java','validateSlotIndex'),
 ('belt/ToolBeltItem.java','initCapabilities'),('belt/ToolBeltItem.java','getSlotsCount'),('belt/ToolBeltItem.java','setSlotsCount'),('belt/ToolBeltItem.java','upgrade'),('belt/ToolBeltItem.java','tickAllSlots'),('belt/ToolBeltItem.java','BeltExtensionContainer'),
 ('network/SwapItems.java','handle'),('network/SwapItems.java','swapItem'),('ToolBelt.java','anvilChange'),('integration/SewingUpgradeRecipe.java','assemble'),
 ('common/BeltContainer.java','BeltContainer'),('common/BeltContainer.java','stillValid'),('common/BeltContainer.java','quickMoveStack'),
 ('common/BeltSlot.java','BeltSlot'),('customslots/ExtensionSlotItemHandler.java','onWornTick'),
 ('BeltFinder.java','findBelt'),('BeltFinderBeltSlot.java','findStack')],
 '真实腰带物品的 capability 对原 ItemStack tag 直接读写；换手/GUI/每槽 tick 消费保存工具；铁砧或缝纫升级转换腰带。',
 'Size 整数限显示2..9，Items compound 列表，以整数 Slot 索引，ItemStack.of 读子栈。',
 'reader 每次扫描列表返回第一个对应槽的子栈；writer 更新或删除第一个同槽条目，否则追加。铁砧升级 copy 原 stack 后只增 Size；缝纫用旧 tag.copy().merge(新结果tag)，新结果冲突键优先。',
 '实现显式说明与上游序列化变动隔离，实际没有借 ItemStackHandler 的序列化格式自动升级。无 Size 时 getInt0 再 clamp 到2；Items 内超出当前可见容量的数据未被 reader 删除，升级后可能重新可见。重复 Slot 返回首项且 writer 仅改首项，不能断言已去重；子栈完整交给 ItemStack.of/save，保留其 Count/tag。simulate 插入/抽出不调用写入，但读取可能 getOrCreateTag 创建空根。真实 SwapItems 服务端工作队列从 belt finder 找持久腰带，将主手和目标槽互换并同步，非仅 tooltip reader。',
 '用于 quest_ledger 栈替换时保留原 ItemStack/Count/tag 的原则；固定格式必须明确重复槽、容量缩小与坏索引处理。新结构对旧结构只覆盖获批字段；迁移时不能把容量以外的条目悄悄删掉。用消费端确认数据确为真实库存而非展示缓存。',
 '无实际旧 ID 映射，不是通用 Slot 名字就独立算法。setSlotsCount writer 不 clamp，reader clamp；of(7/8) 可写9以上但读取最多9，属于静态边界。setStackInSlot 首项更新靠已有 ListTag 引用而直接 return，不显式重新 put；不能将 wrong-type ListTag 也当安全。SewingRecipe.super.assemble 依赖 SewingKit1.8.0，未补读其完整实现，仅审查本模组结果tag合并，Count由外部结果定义不声称保留。未运行测试。',
 '腰带库存、升级、缝纫合并、换手和GUI整链只给一条；与 EvilCraft crafter 的 Slot 库存家族可能重合，差异在长期 ItemStack owner、首匹配直接tag和升级保留语义，需主责复核。与下一条玩家额外槽的 owner/死亡策略不同，不能仅因两者都叫belt算新增。')

add('toolbelt-player-extra-slot-death-filtered-transfer',[
 ('slot/BeltExtensionSlot.java','playerClone'),('slot/BeltExtensionSlot.java','playerDeath'),('slot/BeltExtensionSlot.java','attachCapabilities'),
 ('slot/BeltExtensionSlot.java','serializeNBT'),('slot/BeltExtensionSlot.java','deserializeNBT'),('slot/BeltExtensionSlot.java','entityTick'),('slot/BeltExtensionSlot.java','dropContents'),('slot/BeltExtensionSlot.java','joinWorld'),('slot/BeltExtensionSlot.java','tickAllSlots'),
 ('customslots/ExtensionSlotItemHandler.java','setContents'),('customslots/ExtensionSlotItemHandler.java','notifyEquip'),('customslots/ExtensionSlotItemHandler.java','notifyUnequip'),
 ('ToolBelt.java','commonSetup'),('BeltFinderBeltSlot.java','initBaubles'),('BeltFinderBeltSlot.java','findStack'),
 ('net/minecraftforge/items/ItemStackHandler.java','serializeNBT'),('net/minecraftforge/items/ItemStackHandler.java','deserializeNBT'),('net/minecraftforge/items/ItemStackHandler.java','setSize'),('net/minecraftforge/items/ItemStackHandler.java','setStackInSlot')],
 '玩家或盔甲架的额外腰带槽持久化，LivingDropsEvent 先决定是否保留，再 Clone 只转交剩余腰带；配置关闭时返还槽内物品。',
 '自有 belt_slot capability 包一槽 ItemStackHandler；Forge codec 有 Size 与 Items/Slot，保存的是腰带这个物品，不复制玩家所有能力。',
 '消失诅咒先清槽；玩家非 keepInventory 且非 spectator 时加入死亡掉落并清槽。Clone 转交剩余 stack；新玩家缺 capability 则在旧玩家处 drop。配置禁用时返还物品并清槽。',
 'Clone 没有再根据 isWasDeath 独立复制判定，而依赖前面 LivingDropsEvent 已把应掉物移出，体现事件链所有权边界。调用 oldPlayer.revive() 是实体恢复 workaround，不是 reviveCaps，不能混写。转交用同一个 stack 引用且不在 Clone 清旧槽，完整去重依赖旧实体生命周期；不宣称严格跨崩溃一次交付。额外槽在配置关闭时仍可挂载/读盘，END tick 通过 giveItemToPlayer/spawnAtLocation返还再清。Forge reader Size 合类型才用，否则原槽数，随后 setSize 清空库存，Slot 范围过滤后写入；多项同槽后项覆盖。',
 'Dynasty Clone 永久字段应只复制明确域，死亡损失规则和复制策略必须按实际事件先后核对，避免把已掉落物又克隆一份。缺新容器/关闭功能要明确保留或返还方案；不能整份复制 ForgeData。',
 '未证明 drops 事件取消/其他模组优先级与Clone先后在运行中满足假设。Forge reader 接受存档 Size 而不强制1，坏值/大值防护不在该 codec；单槽wrapper不等于永远一槽。item capability holder未见此处invalidate listener，不推断生命周期安全。支持源码固定 Forge1.20.1分支 commit，另已下载声明47.1.3 sources.jar（SHA256与entry哈希留档）；两者不是字节相同，完整diff为SRG映射名字差异，所用四完整方法AST规范化一致，不能声称Git commit就是47.1.3发布commit或运行兼容已验收。',
 '与 batch003 selective capability Clone 家族有高重复风险；本条具体以事件先掉落/清槽再Clone剩余物以及功能关闭返还为建议独立语义。RpgEquipment/example镜像、Forge codec、每个同步方法均不另计；与前条腰带内部库存不能重复拿同一工具列表credit。')


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
    (DOC/'batch-004.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
