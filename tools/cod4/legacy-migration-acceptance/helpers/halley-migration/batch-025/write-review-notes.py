"""One crate payload-upgrade family, complete manually read gameplay paths."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-024/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-024','batch-025');footer=prior[prior.index('def generate():'):].replace('batch-024','batch-025')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('actuallyadditions-crate-live-and-carrier-upgrade-inventory-preservation-boundaries',
 pick('/items/ItemChestToCrateUpgrade.java','onItemUseFirst')+whole('/items/ItemChestToCrateUpgrade.java')+
 whole('/blocks/BlockGiantChest.java')+whole('/tile/TileEntityGiantChest.java')+whole('/tile/TileEntityGiantChestMedium.java')+whole('/tile/TileEntityGiantChestLarge.java')+
 whole('/inventory/ContainerGiantChest.java')+pick('/inventory/GuiHandler.java','getServerGuiElement')+
 whole('/crafting/RecipeKeepDataShaped.java')+whole('/crafting/RecipeKeepDataShapeless.java')+
 pick('/crafting/BlockCrafting.java','init')+pick('/crafting/InitCrafting.java','init')+pick('/RegistryHandler.java','onCraftingRegistry')+pick('/items/InitItems.java','init')+
 pick('/util/crafting/RecipeHelper.java','addRecipe')+
 pick('/blocks/base/BlockContainerBase.java','onBlockPlacedBy getDrops shouldDropInventory dropInventory dropSlotFromInventory breakBlock removedByPlayer harvestBlock')+
 whole('/tile/TileEntityInventoryBase.java')+whole('/util/ItemStackHandlerAA.java')+
 pick('/tile/TileEntityBase.java','readFromNBT writeToNBT readSyncableNBT writeSyncableNBT canPlayerUse')+
 whole('/inventory/slot/SlotItemHandlerUnconditioned.java')+
 pick('/util/ItemUtil.java','getPlaceAt contains areItemsEqual')+pick('/util/StackUtil.java','isValid getEmpty')+
 pick('/util/AwfulUtil.java','fillInventory shuffleItems getEmptySlotsRandomized'),
 '真实普通箱→巨箱及巨箱升级道具在服务器替换方块并复制库存；另一条保箱器掉落物携Items→注册保NBT配方升级→放置回灌→实际Container取出。统一审查巨箱载荷转换，两个入口和等级都合为一候选，不凭共享codec/配方另加数。',
 '直接升级：start类+end方块状态、当前IInventory/TileInventory槽位快照ItemStack[]。携带升级：掉落物root.Items位置列表与Data子compound(如LootTable)，recipe结果目标注册巨箱item的原生NBT；小/中/大容量117/234/351。',
 'onItemUseFirst只在sneak且start.isInstance(tileHit)后server执行，先逐槽ItemStack.copy快照，再removeTileEntity/setBlockState(end,2)，非创造消耗升级道具，然后目标是TileInventory才逐i复制且newSlots>i才写。目标创建或setBlockState返回未确认；超容量槽没有保留/掉落。InitItems中small→medium的start=TileEntityGiantChest.class，能匹配large子类，而end为medium；因此类guard不是容量单调升级保障。快照只拷物品，不拷旧tile完整自定义名/LootTable/所有权等元数据，不能称全NBT迁移。',
 '保箱器路线：getDrops先取base掉落，找到keeper槽后将其他槽逐项写ItemStack NBT，跳过keeper整个位置所以后续索引前移；shouldDropInventory=false阻止另落库存，keeper正常maxStack1。配方getCraftingResult在原生输出中找首个同item/meta或wildcard源，setTagCompound(input.getTagCompound())不copy，不保证可变NBT引用隔离；shaped/shapeless为同控制流，大小升级不另计。placed逐列表tagCount写目标slot，无容量上界；然后super读Data的SAVE_BLOCK，TileInventory此type不再load Items，因此不清刚回灌列表。',
 'Dynasty旧物品映射应完整保留源Count/tag/未知ID，在目标注册与恢复成功前保留原载荷，并校验来源真实类型/目标容量而非只isInstance。永久Clone字段用审定白名单，不能效仿snapshot全数组或全compound迁移；相同NBT引用与显式ItemStack.copy应区分。item升级配方改变目标item/输出数量是其玩法，不能直接用于quest_ledger旧栈迁移时重建默认数量。为保留失败恢复入口，应将被截/未知槽的原NBT另存可审计区域，而非先删源再丢超限。',
 'lootTable持久于Data/普通Tile，fillWithLoot先置null后生成并写实际槽；原生LootTable查找/世界取消/方块创建失败/异常和磁盘事务未执行，本批不宣称运行通过或修复完成。stopFromDropping使base不加掉落时，巨箱getDrops仍可能访问drops.get(0)，只为源码边界，不宣布已复现。未读Forge原生ShapedOreRecipe/SlotItemHandler底层全域，但本mod注册、保NBT方法、drop/place、实际shift取出均完整。配方完整BlockCrafting.init含无关配方，只作为完整上下文，不对其条目/颜色计数；未审电池和钻头换色消费者不计。',
 '巨箱迁移一个家族：live替换、carrier掉落/配方/放置、LootTable、大小规格/GUI页/keeper都支持同对象载荷，主责可进一步裁决实际独立边界但助手不拆数。与024背包共享TileInventory/ItemStackHandler codec及Slot，绝不重复计算普通loadSlots或键名；本条新增真实旧容器→新容量与物品载体升级控制流。credit0待Kepler。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=[('/items/ItemChestToCrateUpgrade.java',None),('/blocks/BlockGiantChest.java',None),('/tile/TileEntityGiantChest.java',None),('/crafting/RecipeKeepDataShaped.java',None),('/crafting/RecipeKeepDataShapeless.java',None),('/util/crafting/RecipeHelper.java',['RECIPE_LIST']),('/RegistryHandler.java',['RECIPES_TO_REGISTER'])]
    out=[]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
