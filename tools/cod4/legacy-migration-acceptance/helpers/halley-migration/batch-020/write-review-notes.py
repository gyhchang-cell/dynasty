"""Author two manually inspected entity-state transfer/resurrection families."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
old=(b.parent/'batch-013/review.py').read_text();header=old[:old.index("add('akashictome")].replace('batch-013','batch-020');footer=old[old.index('def generate():'):].replace('batch-013','batch-020')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
add('mca-npc-type-conversion-tracked-state-inventory-and-identity-boundary',
 pick('/entity/VillagerLike.java','toNbtForConversion readNbtForConversion copyVillagerAttributesFrom createTrackedData initialize getAgeState setAgeState')+
 pick('/entity/VillagerEntityMCA.java','convertTo setInventory createTrackedData initialize setInfectionProgress setBreedingAge')+
 pick('/entity/ZombieVillagerEntityMCA.java','convertTo setInventory getTypeDataManager initialize setInfectionProgress')+
 pick('/entity/ai/Residency.java','leaveHome getHomeVillage createTrackedData')+
 pick('/server/world/data/Village.java','removeResident cleanReputation getResidentsUUIDs')+
 pick('/entity/ai/Genetics.java','createTrackedData GeneType getParam')+
 pick('/entity/ai/Traits.java','createTrackedData')+
 pick('/entity/ai/brain/VillagerBrain.java','createTrackedData')+
 pick('/entity/ai/BreedableRelationship.java','createTrackedData')+
 pick('/entity/ai/Relationship.java','createTrackedData')+
 pick('/entity/ai/Pregnancy.java','createTrackedData')+
 pick('/entity/Infectable.java','setInfected')+
 pick('/entity/ai/relationship/AgeState.java','toAge getId byId byCurrentAge getStageDuration getMaxAge')+
 pick('/util/network/datasync/CDataManager.java','CDataManager load save Entry get set register')+
 pick('/util/network/datasync/CTrackedEntity.java','getTrackedValue setTrackedValue')+
 pick('/util/network/datasync/CDataParameter.java','load save get set')+
 pick('/util/network/datasync/CEnumParameter.java','load save fromIndex')+
 pick('/util/network/datasync/CParameter.java','create')+
 pick('/util/network/datasync/NbtCompoundDefaultGetters.java','getCompound')+
 pick('/util/InventoryUtils.java','readFromNBT saveToNBT')+
 pick('/server/SpawnQueue.java','tick copyPastaIntensifies shouldGetConverted addVillager handlesSpawnReason convert')+
 pick('/entity/VillagerFactory.java','VillagerFactory newVillager withName withGender withAge withPosition withType withProfession build spawn')+
 pick('/entity/ZombieVillagerFactory.java','ZombieVillagerFactory newVillager withName withGender withPosition withType withProfession build spawn')+
 pick('/mixin/MixinServerWorld.java','onAddEntity')+
 pick('/mixin/MixinVillagerEntity.java','getSpawnReason onInitialize')+
 pick('/mixin/MixinZombieVillagerEntity.java','getSpawnReason onInitialize setVillagerData')+
 pick('/server/command/AdminCommand.java','convertVanillaVillagers')+
 pick('/server/world/data/VillageManager.java','tick')+
 pick('/forge/ForgeBusEvents.java','onWorldTick')+
 pick('/util/WorldUtils.java','spawnEntity loadData')+
 pick('/server/world/data/Nationality.java','get getRegionId toId Nationality writeNbt'),
 '真实MCA村民感染/僵尸村民治愈经过各自convertTo，先native转换再复制mod注册参数、单独NBT复制库存并保留UUID；同时审查官方原生村民替换队列，比较实际转换保留边界，不将两个方向或三种来源拆数。',
 'CDataManager注册参数集：外观/ageState、gene、traits、brain memories/personality/mood/move/chore/panicking/armor，村民额外infectionProgress/growthAmount、VILLAGE、pregnancy/procreation。库存27槽另经InventoryUtils.saveToNBT/readFromNBT。原生替换队列输入活Entity对象，非持久化任务队列。',
 'toNbtForConversion只getTypeDataManager.save，readNbtForConversion只load；参数convertingTo/convertingFrom未参与过滤。CData注册集包含临时panicking/chore/孕育状态，不等于永久进度白名单。CParameter compound save直接put对象、getter按类型返回原compound，未做通用deep-copy，因此MEMORIES等嵌套NBT可能共享引用；不能把经NBT方法称为全部深拷贝。非注册顶层giftSaturationQueue/longTermMemory不经此copy，库存另拷。',
 '村民转化入口先residency.leaveHome，移除村庄resident并把VILLAGE=-1，即使后续native转换失败也已改归属；成功转Zombie时copy参数后initialize(CONVERSION)，再复制原生villagerData/gossip/offers/xp/UUID并持久化，MCA库存单独复制。Zombie反向只在MCA Villager结果时setUUID/库存并按ageState.toAge设置年龄，细分growthAmount可能重建为阶段边界；显式setInfected(false)，不是原样复制全部状态。两个setInventory都序列化到新compound再读目标，不是直接共享inventory对象。',
 'Dynasty Clone白名单应像显式参数集一样可审查，但只列已批准永久字段；不要照搬此mod的全部tracked字段。身份UUID/维度引用/库存/派生属性要分别验证，目标恢复成功前勿先移源或改变旧所有权；未知旧ItemID/Count/tag原样保留。NBT写入再读取不自动保证嵌套深拷贝，避免新旧玩家共享可变compound。',
 '原生替换队列在poll后先discard旧实体，再Factory重造当前注册实体；只搬name/position/type/profession(level/offers仅正常村民)/age及persistent/invulnerable/noAI/tags，未见复制UUID/原生全部库存/未知附加NBT。WorldUtils.spawnEntity不检查world.spawnEntity返回；队列不持久化，不作可靠迁移事务样板。正常add去重contains，admin.convert直接add无同等guard，重复请求边界未运行验证；Mixin transient SpawnReason缺失回NATURAL，不是保存后恢复原原因。Native MobEntity.convertTo、原生SimpleInventory底层及各AI副作用未重读到底，不宣称全载荷无损或实际测试通过。通用InventoryUtils.save误用setNbt的未调用路径不当当前库存转换bug。',
 '唯一NPC类型转换家族；正反方向/男性女性/原生村民和僵尸变体/Factory、队列、原生codec/参数键/平台tick都支持同一边界，不追加信用。与第019玩家模板CData支持大量共用，独立部分为真实NPC换型UUID/库存/归属取舍；如果主责认为同状态变体则合并或排除，credit0。')

add('mca-tombstone-durable-entity-payload-to-resurrection-and-removal-boundary',
 pick('/block/TombstoneBlock.java','readNbt writeNbt EntityData setEntity writeEntityToNbt startResurrecting tick createEntity createEntityWithoutActiveEffects withoutActiveEffects generateLightning hasEntity getEntityName sync readFromStack writeToStack onPlaced updateTombstoneState onBlockAdded onStateReplaced getDroppedStacks getTicker of')+
 pick('/entity/ai/Relationship.java','onDeath onTragedy placeTombstone')+
 pick('/entity/VillagerEntityMCA.java','onDeath')+
 pick('/entity/ZombieVillagerEntityMCA.java','onDeath convertTo')+
 pick('/util/InventoryUtils.java','dropAllItems')+
 pick('/item/ScytheItem.java','useOnBlock use hasSoul setSoul')+
 pick('/item/StaffOfLifeItem.java','useOnBlock')+
 pick('/entity/ai/relationship/EntityRelationship.java','of onTragedy')+
 pick('/server/world/data/FamilyTreeNode.java','setDeceased willBeRemembered probablyGenerated')+
 pick('/server/world/data/GraveyardManager.java','get GraveyardManager writeNbt setTombstoneState removeTombstoneState findNearest getChunkPos getChunk Chunk toNbt isEmpty removePos addPos opposite')+
 pick('/util/WorldUtils.java','loadData')+
 pick('/util/NbtHelper.java','toMap computeIfAbsent')+
 pick('/entity/ai/relationship/Gender.java','byId'),
 '真实NPC死亡经Relationship选择/放置墓碑并保存实体；世界重载墓碑可继续复活进度，打掉/再放物品可转移载荷；镰刀或生命杖启动服务器tick计时，超过500后从载荷重建实体/可选治愈，消费源墓碑状态。',
 '墓碑根entityData为带注册id的完整原实体NBT，另存entityName JSON/entityGender ordinal、resurrectionProgress int、cure bool；物品subNbt entityData又包一层EntityData字段，只携实体/名字/性别，未携进行中的复活progress/cure。GraveyardManager按维度存EMPTY/FILLED→chunk long→packed BlockPos long索引。',
 'Tile read仅外层entityData是compound才创建EntityData，内部raw实体id和其他NBT暂不解码/预校验；未知类型仍可作为compound保存。EntityData构造name从JSON转Text后转plain string，样式不原样保留；Gender越界fallback。tick恢复progress/cure能续任务，每tick dirty+sync；移动为物品只转EntityData，重放后progress/cure默认不续。实际普通死亡先dropAllItems并clear库存，再relations.onDeath保存实体，因此不能说墓碑复制全部死亡前库存。',
 'createEntity(world,remove,transform)在try里调用EntityType.getEntityFromNbt，但finally无条件在remove=true时setEntity(null)；解码返回empty、转换抛异常均清源，不等成功。复活专用transform复制原compound并只去ActiveEffects，恢复health/max、fallDistance/deathTime/portal/fire/位置；可选zombie.convertTo(VILLAGER,true)并避免二次spawn，否则spawn返回值未检查。FamilyTree deceased=false在目标实例上更新，不证明生成事件接受。原始未知id应保留的阶段在此最终消费边界被破坏。',
 'Dynasty旧ID兼容若当前依赖缺失或NBT暂无法解码，必须保留原栈/原compound，不能finally清源；只在确认恢复/交付成功后提交一次消费标记。持久进度与临时运行任务分开，Clone只迁永久白名单，不照搬完整实体NBT或复活health/状态刷新，不改变本地既有伤势死亡规则或新增死亡惩罚。跨容器/物品载体移动要明确哪些字段故意重置。',
 '这是NPC墓碑保存/复活一条玩法实现，不是玩家Clone或已验证的历史旧ID remap。实际原生EntityType加载/NBT数据修复/事件拒绝/文件崩溃恢复未执行；name JSON坏值可能在EntityData构造抛错，未知id是否为空取决原生加载。墓地索引与tile载荷两个真值，索引解码enum/数值无逐项catch，setEntity更新索引；没有证明所有陈旧索引自动修复。物品写入附lore仅显示支持，读取不显式dirty也未重置computedName，只作静态边界；不按每tickdirty/视觉/两物品拆数。',
 '完整死亡捕获→Tile/Item载荷→重载→复活/治愈→清源与墓地索引合一条，GraveyardManager作为同链索引支持不多计。与第019家谱关系和本批NPCconvertTo共用方法，源消耗/载荷生命周期为独立审查点但主责若判同族应合并；credit0待Kepler，方法与下载数不当信用。')
'''
attach='''\ndef attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=([('/entity/VillagerEntityMCA.java',['CParameter.create(','CDataManager<','new UpdatableInventory']),('/entity/ZombieVillagerEntityMCA.java',['CDataManager<','new UpdatableInventory']),('/entity/VillagerLike.java',['CParameter.create(']),('/entity/ai/brain/VillagerBrain.java',['CParameter.create(']),('/entity/ai/Pregnancy.java',['CParameter.create(']),('/mixin/MixinVillagerEntity.java',['SpawnReason reason;']),('/server/SpawnQueue.java',['ConcurrentLinkedQueue<'])] if 'npc-type-conversion' in row['family'] else [('/block/TombstoneBlock.java',['Optional<EntityData> entityData =','resurrectionProgress;','boolean cure;']),('/server/world/data/GraveyardManager.java',['tombstones ='])])
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
print('Authored two actual transfer-lifecycle families credit0')
