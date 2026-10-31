"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-018'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))






def pick(path,names):return [(path,n) for n in names.split()]
add('forestry-backpack-base36-slots-and-persistent-mode-to-resupply',
 pick('/core/inventory/ItemInventory.java','ItemInventory setUID getParent getHand isSameItemInventory isParentItemInventory writeToParentNBT getSlotNBTKey markDirty setInventorySlotContents decrStackSize removeStackFromSlot isItemValidForSlot getItemHandler')+
 pick('/storage/inventory/ItemInventoryBackpack.java','ItemInventoryBackpack canSlotAccept isUsableByPlayer')+
 pick('/storage/inventory/ItemInventoryBackpackPaged.java','ItemInventoryBackpackPaged flipPage')+
 pick('/storage/items/ItemBackpack.java','ItemBackpack onItemRightClick tryStowing switchMode getMode getSlotsForType getBackpackSize evaluateTileHit transferToChest receiveFromChest getContainer')+
 pick('/storage/items/ItemBackpackNaturalist.java','getContainer')+
 pick('/storage/gui/ContainerBackpack.java','ContainerBackpack getSize')+
 pick('/core/gui/ContainerItemInventory.java','ContainerItemInventory addHotbarSlot canAccess canInteractWith slotClick')+
 pick('/core/items/ItemWithGui.java','ItemWithGui onItemRightClick onDroppedByPlayer')+
 pick('/storage/PickupHandlerStorage.java','onItemPickup topOffPlayerInventory')+
 pick('/storage/ResupplyHandler.java','getBackpacks resupply topOffPlayerInventory')+
 pick('/core/inventory/ItemHandlerInventoryManipulator.java','ItemHandlerInventoryManipulator iterator addStack tryAddStack transferStacks tryPut')+
 pick('/core/inventory/InvIterator.java','InvIterator hasNext next')+
 pick('/core/inventory/InvSlot.java','InvSlot getIndex canPutStackInSlot canTakeStackFromSlot getStackInSlot')+
 pick('/storage/ModuleBackpacks.java','getPickupHandler getResupplyHandler')+
 pick('/modules/InternalModuleHandler.java','registerHandlers')+
 pick('/core/EventHandlerCore.java','handleItemPickup')+
 pick('/core/TickHandlerCoreServer.java','onWorldTick'),
 '旧背包物品打开、拾取归仓或世界END补给时重新构造ItemInventoryBackpack，读Slots并补缺失UID；实际RESUPPLY每背包每次成功转一件到玩家已有可合并栈，再把减少后的源槽写回父物品。背包模式来自持久metadata而非会话变量。',
 '父ItemStack Slots compound，键Integer.toString(index,36)，值完整ItemStack NBT；父UID整数缺失时rand.nextInt补写；metadata<1 NORMAL、>=1 LOCKED、>=2 RECEIVE、>=3 RESUPPLY。NORMAL15/WOVEN45/NATURALIST125槽由当前物品type决定，不从旧载荷记录恢复容量。',
 'ItemInventory只枚举0..currentSize-1的已知base36键，缺槽为空；读不调用背包filter，因此旧不合过滤物仍在内存。单槽setInventorySlotContents修改同一Slots compound，保留其他未知槽键；但markDirty/writeToParentNBT新建整个Slots，仅写当前非空槽，超容量/未知槽键会被丢弃。父NBT其他键保留；已知ItemStack载荷经原生reader/writer，未证明未知原生字段完整保留。UID缺失立即补写即构造也有数据变更。',
 'getParent在双手找同item+相同整数UID，未找到回最初parent引用；UID只随机int，无全局唯一或owner绑定校验，同UID复制栈可匹配。玩家包实际补给遍历mainInventory中背包，要求ContainerPlayer，读取恢复mode；RESUPPLY一次从一个可合并槽转1件并即时单槽写回，开启别的容器不补。拾取先补玩家已有栈，再合过滤背包，LOCKED不自动stow；真实收发箱路径用模拟可插入数再提取/写目标。',
 'Dynasty旧任务物品迁移需保留整个原载荷，包括当前容量外的旧条目；区分单槽编辑和全量重编码的保留边界。旧缺身份字段应在确定目标归属/唯一性后初始化，不能把随机int或物品类型当玩家UUID。长期任务字段只迁经审定白名单，原物品Count/tag保留；背包模式是物品配置，不能类推出玩家死亡后所有临时模式应保留。',
 '未执行Forge InvWrapper/原生NBT/物品操作；实际insertItem/extractItem依赖外部接口契约，simulate→extract→insert不是崩溃原子事务。isUsableByPlayer只查主手任意ItemBackpack，不查UID；父类hotbar锁采用UID规则，不能单凭本地代码宣称完整防复制或已验证漏洞。getContainer数据边界使用>而非>=且未检查负数，只记静态边界。RESUPPLY配置关闭时Tick入口不执行，但getMode仍返回持久RESUPPLY；不宣称读取时归一化metadata。naturalist只分页wrapper，不另计。',
 '背包类型/颜色/15或45或125槽、模式、UID初始化、归仓补给、父物品写回同一便携库存恢复家族合一。与第016信件附件共用ItemInventory父codec，相关支持不另计；与主账其他模组背包需比较实际base36/容量/UID/写回消费者语义，credit0待Kepler。')

add('forestry-cocoon-persistent-individual-and-age-to-hatch-lifecycle',
 pick('/lepidopterology/tiles/TileCocoon.java','readFromNBT writeToNBT TileCocoon onBlockTick attemptButterflySpawn getCaterpillar setCaterpillar setAge getCocoonDrops isSolid')+
 pick('/lepidopterology/blocks/BlockCocoon.java','BlockCocoon updateTick createNewTileEntity getPickBlock')+
 pick('/lepidopterology/blocks/BlockSolidCocoon.java','BlockSolidCocoon createNewTileEntity removedByPlayer')+
 pick('/lepidopterology/items/ItemButterflyGE.java','onItemUse getAge setAge')+
 pick('/lepidopterology/genetics/ButterflyRoot.java','plantCocoon getValidCocoonPos isPositionValid getMember getMemberStack getDefaultTemplate templateAsGenome templateAsIndividual spawnButterflyInWorld getKaryotype')+
 pick('/lepidopterology/genetics/Butterfly.java','Butterfly copy canTakeFlight canFly isActiveThisTime isAcceptedEnvironment getCocoonDrop getGenome')+
 pick('/lepidopterology/genetics/ButterflyGenome.java','ButterflyGenome getLifespan getFertility getMetabolism getCocoon getFireResist getSize getPrimary getSpeciesRoot')+
 pick('/core/genetics/Genome.java','Genome getChromosomes writeToNBT getActiveAllele checkChromosomes')+
 pick('/core/genetics/Chromosome.java','create validateAllele Chromosome writeToNBT')+
 pick('/core/genetics/IndividualLiving.java','IndividualLiving writeToNBT')+
 pick('/core/genetics/Individual.java','Individual writeToNBT')+
 pick('/core/owner/OwnerHandler.java','readFromNBT writeToNBT setOwner')+
 pick('/core/utils/EntityUtil.java','spawnEntity')+
 pick('/lepidopterology/entities/EntityButterfly.java','EntityButterfly setIndividual onInitialSpawn writeEntityToNBT readEntityFromNBT'),
 '世界茧Tile重载Caterpillar/Age/CATMAT/isSolid后，普通BlockCocoon随机tick继续成熟；到最后阶段且环境容许飞行时先出掉落并移除茧，再生成携同一个体副本的真实蝴蝶。固体茧另经玩家采集取实际掉落；不把固体构造当普通孵化入口。',
 'Caterpillar compound含Individual长期基因/配偶/分析状态/Health/MaxH；Age阶段、CATMAT阶段内计数、isSolid旗标及owner GameProfile。物品茧NBT_AGE与tile Age经getPickBlock→itemUse→plantCocoon保持阶段，CATMAT与owner不在此物品中一并复制。',
 'TileCocoon缺Caterpillar时保留字段默认CabbageWhite个体；存在空Caterpillar时new Butterfly，其缺Genome回root默认Brimstone，而非CabbageWhite，故缺键与空载荷不同。Age/CATMAT/isSolid直接读，缺失各归0/0/false，可覆盖solid构造age2/true；无上下界裁剪或与世界block类型交叉校验。onBlockTick用基因lifespan/(fertility*2)计算阈值，阶段<2时age++并清计数，否则在canTakeFlight下发掉落/移块/生成实体。',
 '实际spawn先copy经NBT roundtrip重构个体，EntityButterfly.setIndividual从基因重建尺寸、species和火抗，home重新设置为出生位置；不复制整个旧实体或owner字段。EntityUtil.spawnEntity调用world.spawnEntity但未检查boolean，Tile先setBlockToAir，不能以函数返回对象证明世界已接受新实体。solid块未覆盖updateTick，不能因setTickRandomly(true)就声称执行普通茧孵化。固体掉落额外保留蝴蝶物品由isSolid控制，未知/缺flag会改变输出。',
 'Dynasty旧状态恢复需区分缺键与存在空compound的不同默认，并验证载荷状态与当前对象类型；阶段、累计时间与永久进度要分别审定，不能整份Clone。把派生属性从已迁白名单重建，替换原载体必须确认目标成功后再移除源；未知基因/任务ID应保留原始载荷以免fallback后永久丢失。',
 '本链遗传codec是第016已读支持而非新的蜂/蝶染色体信用；未验证原生世界刷盘、生成事件否决/崩溃原子性、所有气候/allele配置。onBlockTick未显式markDirty，只有阶段变化notify，不能保证阶段内CATMAT每tick可靠刷盘。getCocoonDrop第二血清chance分支改变局部stack后实际又创建另一个加入，静态可见但不据此开新研究数。EntityButterfly持久PLN缺Root兼容treeRoot、未知Root可能null、STATE无界等只作下游支持范围，不额外计一链。没有运行孵化/采集样例。',
 '茧→阶段恢复→普通孵化或固体采集→蝴蝶载体合一生命周期，不按年龄/solid/owner/genome/实体读写/血清数量拆计。与第016蜂基因恢复共享完整codec须合并支持，独立部分为茧持久阶段和替换载体消费者；如主责认定同对象变体则排除，不自动credit。')

add('forestry-fruit-pod-allele-fallback-and-maturity-to-harvest',
 pick('/arboriculture/tiles/TileFruitPod.java','readFromNBT writeToNBT TileFruitPod setProperties onBlockTick canMature addRipeness getDrops pickFruit writeData readData')+
 pick('/arboriculture/blocks/BlockFruitPod.java','updateTick removedByPlayer getDrops createNewTileEntity canGrow grow')+
 pick('/arboriculture/genetics/TreeRoot.java','setFruitBlock')+
 pick('/arboriculture/FruitProviderPod.java','FruitProviderPod getFruits trySpawnFruitBlock getProducts')+
 pick('/arboriculture/genetics/alleles/AlleleFruit.java','AlleleFruit getProvider')+
 pick('/arboriculture/genetics/alleles/AlleleFruits.java','registerAlleles')+
 pick('/core/genetics/alleles/AlleleRegistry.java','getAllele'),
 '果荚Tile恢复UID/MT/SP，真正随机生长tick使用产率SP决定成熟，玩家移除方块经tile.getDrops→allele.provider.getFruits得到产品；成熟果pickFruit取果后重置阶段。不是只有客户端模型恢复。',
 'UID字符串指定IAlleleFruit，MT short成熟度、SP float产率；setProperties初次种植另外赋genome，字段默认genome取treeRoot默认模板、defaultAllele为forestry.fruitCocoa。持久writer仅UID/MT/SP，不保存genome。',
 'read用alleleRegistry查UID且instanceof IAlleleFruit才接受，否则回defaultAllele；下一次write将fallback UID写回，不保留未知原UID/原因。MT与SP原值读，无下界/NaN等显式检查；canMature只MT<2，addRipeness只裁上界2，缺SP为0通常不长但rand.nextFloat<=0仍有零值边界。genome持久遗漏，重载后回默认；当前FruitProviderPod.getFruits只看ripeningTime>=2和固定drops，忽略genome参数，因此不能把genome丢失直接报告为已证明产物改变。',
 'TreeRoot.setFruitBlock完成放置且拿到tile后才setProperties并返回true；read不会按当前BlockFruitPod.fruit重建allele或交叉校验，因此未知UID可回可可provider而外层仍另一果荚块。BlockFruitPod.removedByPlayer真实服务端获取tile掉落，默认getDrops空；只看继承普通掉落路径会误判没有持久消费者。客户端readData也做fruit类型fallback但只传UID，MT来自块状态/其他入口，不等同完整服务端NBT恢复。',
 'Dynasty旧任务册/物品恢复应保留无法解析的旧标识，校验外层物品注册名与内部类型一致，明确哪些原始字段被fallback替换。若某派生字段不持久，应证明当前消费者无需它或可从白名单重建；不能根据字段名猜测数据丢失影响。Clone永久字段默认值要分别定义缺键/空值/类型错，而非将错误一律静默变默认成功。',
 '无显式旧别名注册，不将registry getter当独立兼容实现。getFruits的当前固定pod provider支持到真实产品复制，第三方IFruitProvider/其他果树provider不在本候选范围。读MT异常后块AGE值域、原生随机tick与setBlockState刷盘未运行验证；本静态记录不承诺坏NBT安全。addRipeness与pickFruit未显式markDirty但会写块状态，不能静态推断精确保存时机。',
 '一条果荚持久对象恢复和最终产品消费，UID/MT/SP、三果品、UI网络、种植/收获不拆数。与第016基因slot fallback不同为独立果荚简化载荷，但与主账其他植物成熟数据需人工去重，credit0待Kepler。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    if 'backpack' in row['family']:targets=[('/core/inventory/ItemInventory.java',['KEY_SLOTS =','KEY_UID =','rand =']),('/core/config/Constants.java',['SLOTS_BACKPACK_'])]
    elif 'cocoon' in row['family']:targets=[('/lepidopterology/tiles/TileCocoon.java',['caterpillar =']),('/lepidopterology/items/ItemButterflyGE.java',['NBT_AGE ='])]
    else:targets=[('/arboriculture/tiles/TileFruitPod.java',['MAX_MATURITY =','defaultGenome =','defaultAllele =','genome =','allele =']),('/arboriculture/genetics/alleles/AlleleFruits.java',['fruitCocoa ='])]
    decl=[]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for node in walk(PARSER.parse(raw).root_node):
            if node.type not in ('field_declaration','static_initializer'):continue
            fragment=raw[node.start_byte:node.end_byte].decode()
            if not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=node.type,name='static-initializer' if node.type=='static_initializer' else fragment.split('=')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
            e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);decl.append(e)
    row['source_declarations']=decl
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
        attach_declarations(row)
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-018.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
