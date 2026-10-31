"""Render handwritten complete-source research notes; no upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-020/review.py').read_text()
header=prior[:prior.index('def pick(')].replace('batch-020','batch-021')
footer=prior[prior.index('def generate():'):].replace('batch-020','batch-021')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('mca-village-estate-building-origin-fallback-and-real-rank-reputation-consumers',
 [('/server/world/data/Village.java','Village',74)]+
 whole('/server/world/data/Village.java')+whole('/server/world/data/VillageManager.java')+whole('/server/world/data/Building.java')+
 whole('/resources/BuildingTypes.java')+whole('/resources/data/BuildingType.java')+
 whole('/resources/Tasks.java')+whole('/resources/Rank.java')+
 whole('/resources/data/tasks/Task.java')+whole('/resources/data/tasks/BuildingTask.java')+whole('/resources/data/tasks/PopulationTask.java')+whole('/resources/data/tasks/ReputationTask.java')+whole('/resources/data/tasks/BlockingTask.java')+whole('/resources/data/tasks/AdvancementTask.java')+
 whole('/server/world/data/villageComponents/VillageTaxesManager.java')+
 pick('/network/c2s/SaveVillageMessage.java','receive')+pick('/network/c2s/RenameVillageMessage.java','receive')+pick('/network/c2s/GetVillageRequest.java','receive')+
 pick('/forge/ForgeBusEvents.java','onWorldTick')+pick('/util/WorldUtils.java','loadData spawnEntity isChunkLoaded')+pick('/util/NbtHelper.java','toMap fromMap toList toStream fromList')+
 pick('/util/RegistryHelper.java','isTagEmpty getEntries getRegistryOf'),
 '服务器各维度END tick取得mca_villages持久管理器，载村庄/建筑后供实际爵位任务、负声望悬赏、税收和扫描合并消费；这是一个村庄地产对象家族，旧扫描起点兼容并入该家族。',
 'mca_villages：lastBuildingId/lastVillageId、villages列表、reapers子对象；Village保存建筑、UUID居民名/床位posLong、UUID玩家→UUID居民声望、unspentHearts/Mood、税率、阈值、autoScan。Building保存边界/扫描源坐标、type、blocks2注册Identifier→BlockPos列表。',
 'Building读旧NBT若缺posX，使用包围盒中心生成扫描源posX/Y/Z；只以posX存在判整个三坐标组，缺Y/Z回原生0；writer统一写新三坐标。blocks2只读当前键，未见旧blocks转换，不能把名字末尾2当迁移证据。Village缺两个阈值保留字段默认0.75/0.5，缺autoScan强制true而不是当前config；taxesFloat直接读缺值0，不宣称兼容旧整数税率。世界存在时只接受当前BuildingTypes包含的type，未知类型整个建筑过滤，空村在Manager加载时移除并dirty；没有保留未知原载荷区。',
 '恢复后的建筑类型/居民数/声望真实参与Tasks.getRank：从高到低只检查该rank任务，不累计低rank；BuildingTask仅匹配type、不检查Building.isComplete，Population/Reputation各读村庄真值。Manager.tick依负声望决定并实际生成悬赏者；税收用恢复税率/人口/仓库建筑生成物品到storageBuffer再投箱。Village.save不保存storageBuffer与lastMoveIn/lastBedSync，这些不能称持久税收队列。processBuilding扫描后可能merge并删除被合村，但Village.merge只putAll建筑和加unspentMood，未复制声望/unspentHearts/居民名/居所/税率。',
 'Dynasty旧数据迁移应明确兼容回退触发的字段组，旧字段存在但类型错和真正缺省分开；未知注册类型/暂缺依赖应保留原数据而不是过滤后重写。合并永久进度/历史需逐项声明冲突策略、身份UUID/维度和dirty提交；不能以一个容器putAll当全部状态迁移。派生rank与缓存不当永久已验收，实际物品暂存必须明确是否持久。只形成研究建议，不变更原存档或本地政策。',
 'UUID.fromString、Identifier构造及NBT强制转换由NbtHelper流内执行，无逐项catch，坏项可终止对象加载；不同字段和副作用未做崩溃/运行验证。setter和SaveVillage/Rename接收器不显式markDirty；可能有后续dirty不能替代事务保证，也未完整审网络全局权限，不能据此宣布全局权限漏洞。processBuilding的orElse(new Village(lastVillageId++,...))参数即使已有村庄也求值，但仅静态观察不宣称实际损坏。内嵌ReaperSpawner和其他guards/inn/marriage/procreation组件本批未沿到所有消费者，不算独立实现或保证；读取了tick调用边界并审至上述rank/bounty/tax消费者。',
 '一个村庄地产持久对象与其嵌套建筑完整家族：旧坐标回退、声望、税率、任务类型、merge/scan、平台tick、多个键都不分计。与019玩家lastVillage和020居民离家/墓地报告共用支持，应由Kepler决定更广关系家族是否合并；credit0，支持方法/建筑实例/配置条目不当参考数。')

add('mca-baby-child-snapshot-carrier-crib-reload-and-birth-consumption',
 pick('/item/BabyItem.java','birthChild')+whole('/item/BabyItem.java')+whole('/entity/CribEntity.java')+whole('/item/CribItem.java')+
 whole('/entity/ai/Pregnancy.java')+pick('/entity/ai/BreedableRelationship.java','createTrackedData BreedableRelationship getPregnancy isProcreating mayProcreateAgain startProcreating tick handleSpecialCaseGift')+
 pick('/entity/VillagerEntityMCA.java','readCustomDataFromNbt writeCustomDataToNbt tickMovement initialize createTrackedData')+
 pick('/entity/VillagerLike.java','initialize toVillager')+
 pick('/entity/VillagerFactory.java','VillagerFactory newVillager withPosition withGender withAge build')+
 pick('/entity/ai/Genetics.java','combine getGenome getGene Gene get set mutate')+pick('/entity/ai/Traits.java','inherit getInheritedTraits getTraits addTrait')+
 pick('/util/network/datasync/CDataManager.java','load save Entry register')+pick('/util/network/datasync/CDataParameter.java','load save get set')+pick('/util/network/datasync/CTrackedEntity.java','getTrackedValue setTrackedValue')+
 pick('/network/c2s/BabyNamingVillagerMessage.java','receive')+
 pick('/mixin/MixinPlayerEntity.java','onDropItem')+pick('/mixin/MixinPlayerInventory.java','onDropSelectedItem')+pick('/mixin/MixinScreenHandler.java','onSlotClick mca$getDroppedStack')+
 pick('/server/world/data/FamilyTree.java','get getOrCreate getOrEmpty createEntry')+pick('/server/world/data/FamilyTreeNode.java','replaceParents clearParents assignParent setFather setMother removeFather removeMother markDirty')+
 pick('/entity/ai/relationship/EntityRelationship.java','of getFamilyTree')+pick('/entity/ai/Relationship.java','getFamilyEntry')+
 pick('/entity/ai/Memories.java','Memories setHearts getHearts getPlayerUUID toCNBT fromCNBT')+pick('/entity/ai/brain/VillagerBrain.java','getMemoriesForPlayer updateMemories')+
 pick('/util/WorldUtils.java','spawnEntity loadData')+pick('/entity/ai/relationship/AgeState.java','getMaxAge byCurrentAge'),
 '真实生育保存预生成子代自定义NBT到BabyItem，随物品/摇篮重载与年龄积累，命名且成熟后birthChild恢复并出生；NPC孕育进度与物品生育方向都归入同一生命周期，不分男女/双胞胎/平台计数。',
 'Item root baby compound：mother/father UUID及显示名、age int、babyName、child自定义实体NBT。createItem先组合遗传/traits再writeCustomDataToNbt；摇篮mca.Baby是完整ItemStack NBT，Wood/Color是ordinal；pregnancy hasBaby/isBabyMale/babyAge注册参数随村民自定义NBT保存。',
 'getBabyNbt只在root缺baby时写NIL_UUID父母/Unknown名/age0；存在baby但类型错未显式修复，getSubNbt可能null。child缺失时出生用Factory初始子代，存在时直接readCustomDataFromNbt，后写babyName。Crib.read手动读mca.Baby并ItemStack.fromNbt，解码空只告警不保留原compound；Wood/Color直接values[index]无边界fallback。其持久读写没有调用CDataManager.save/load的babyItem键，不能将通用CParameter ItemStack重载误当当前存档路径。',
 '实际birth先WorldUtils.spawnEntity(BREEDING)，该方法initialize再spawn且忽略spawn boolean；随后改FamilyTree父母/亲属hearts并在use扣1，未验证目标已接受。BREEDING初始化跳过遗传/traits randomize，但仍initializeSkin和brain.randomize，故不是child全部状态原样回灌；正常initialize可能生成临时已故双亲，birth后replaceParents先clear再按保存UUID查当前世界实体或主世界图补父母。摇篮取出忽略insertStack返回后清BABY，失败/残余移除边界应审；放入用原stack并removeOne，正常注册maxCount1仍不能等同事务协议。',
 'Dynasty未知旧ItemID/child compound先保留原载荷再验证解码；源物品/容器只在目标出生或接收确认后一次消费。Clone永久白名单应与此预生成子代快照分清，绝不把全entity customNBT/生命/孕育/临时AI作为获准永久数据。UUID引用和世界定位要分层验证，显示名不是身份，缺键回退必须有类型和完整字段组校验；初始化再运行会覆盖哪些已恢复字段应显式记录。',
 '出生/物品复制与原生ItemStack/实体加载未运行，server rejection/满背包/坏UUID/enum崩溃只为静态边界，不宣布已复现。Baby年龄每逢worldTime%1200==0直接加1200，摇篮tick调用相同inventoryTick；非真实经过时间，不新增短期计时持久模式。pregnancy.tick每村民20tick调用一次却加60，到期先resetBabyAge再查father，未找到则仍pregnant并重新积累；成功查到先清pregnant再spawn，类似失败消费风险。birth和pregnancy支持关系图/库存/皮肤/完整遗传权重下游未全域审查，不作已通过原存档迁移或健康政策改变证据。',
 '物品婴儿快照→摇篮载体→出生及NPC孕育作为一个子代生命周期，read/write/命名/防丢弃/男女/双胞胎/计时不拆数。与019家谱和020NPC转换共用大量CData/Factory/关系支持，差别在实际新子代预生成载荷与最终消费；若主责按同实体恢复更广家族合并应遵从。credit0，未审部分/方法数量不当信用。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    suffixes=(['/server/world/data/Village.java','/server/world/data/VillageManager.java','/server/world/data/Building.java'] if 'village-estate' in row['family'] else ['/entity/CribEntity.java','/entity/ai/Pregnancy.java','/entity/ai/BreedableRelationship.java'])
    out=[]
    for suffix in suffixes:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20])
            e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
