"""Handwritten complete gameplay-source notes, static document rendering only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-021/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-021','batch-022');footer=prior[prior.index('def generate():'):].replace('batch-021','batch-022')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('mca-reaper-ritual-persistent-countdown-old-position-fallback-and-final-spawn',
 [('/server/ReaperSpawner.java','SummonPosition',165)]+whole('/server/ReaperSpawner.java')+
 pick('/server/world/data/VillageManager.java','get VillageManager getReaperSpawner tick writeNbt')+
 whole('/mixin/MixinFlintAndSteelItem.java')+whole('/block/InfernalFlameBlock.java')+
 pick('/forge/ForgeBusEvents.java','onWorldTick')+pick('/util/NbtHelper.java','toList toStream fromList')+pick('/util/WorldUtils.java','loadData isAreaLoaded'),
 '打火石成功使用后的服务器任务调用trySpawnReaper，验证仪式后把ActiveSummon放入mca_villages.reapers.summons；世界重载读取剩余ticks与位置，END tick继续取消或最终生成Boss。旧位置直接坐标与新富结构分支为本条迁移重点。',
 'ActiveSummon保存ticks int/position compound。新SummonPosition保存fire、spawnPosition两compound、totems为compound元素列表；旧格式position直接含原生坐标，没有三个富字段时走旧回退。每维度VillageManager持有独立activeSummons map，键spawnPosition.asLong。',
 'SummonPosition(NBT)以fire/totems/spawnPosition任一键存在判新格式，否则从整个tag取spawnPosition、fire=spawnPosition.down(10)、totems空。这是明确旧载荷兼容而非推测版本变化。新writer把totems写NbtList，reader却tag.getCompound("totems")后传net.mca.util.NbtHelper.toList；toStream把传入NbtElement直接强转NbtList。getCompound静态返回NbtCompound，故该新分支存在确定的Java类型不相容；没有逐项catch。',
 'ActiveSummon构造由ReaperSpawner构造forEach直接执行，异常传播至VillageManager构造，不能据此推断底层磁盘加载会如何处理原文件。正常恢复的tick先查central fire是否仍Infernal Flame；取消才把仍存在的totem火转回普通火，置空position/ticks并移除。未取消则--ticks每20tick闪电，到0调用注册GrimReaper.spawn，返回null也返回完成并移除任务；每轮原来非空就manager.markDirty。start同位置computeIfAbsent且ticks>0不重启，但外围仪式FX/方块改变仍执行。',
 'Dynasty迁移格式分支应使用类型与完整结构校验，旧位置回退和新reader/writer必须对齐NBT容器类型；未知/损坏项隔离并保留原payload，不让一个任务阻断整个世界数据对象。一次消费以目标确实生成/接受为提交条件，持久倒计时与临时Clone白名单分开；这只是研究建议，不引入新Boss/计时机制或更改生产。',
 '未运行上游代码、原生Boss生成、文件加载或测试；原生NbtHelper坐标格式和注册实体完整战斗AI本批没有展开，正常旧分支还受central fire存在影响。新分支类型冲突为源码静态结论，不能写成真实世界复现或已验证修复。仪式开始前查周边区块，持续tick未再次调用同检查；不推断强制区块加载行为。多字段/闪电/各tick不多计。',
 'Reaper仪式是一个实际持久任务载荷与显式旧格式兼容家族。VillageManager已为021对象支持，不能把父容器writeNbt与此子任务再算相同reader；本条新增的是SummonPosition旧新结构和ActiveSummon实际续跑/消费。与020墓碑同有倒计时但不同独立载荷/旧格式，最终仍由Kepler语义裁决，credit0。')

add('mca-civil-registry-world-history-json-text-restoration-and-book-page-consumer',
 [('/server/world/data/CivilRegistryManager.java','CivilRegistryManager',26)]+pick('/server/world/data/CivilRegistryManager.java','CivilRegistryManager writeNbt addText getPage get')+
 pick('/server/world/data/Village.java','getCivilRegistry getId')+pick('/server/world/data/VillageManager.java','get VillageManager writeNbt')+
 pick('/entity/VillagerEntityMCA.java','onDeath')+pick('/server/world/data/villageComponents/VillageMarriageManager.java','marry')+
 whole('/network/c2s/CivilRegistryPageRequest.java')+whole('/network/s2c/CivilRegistryResponse.java')+
 whole('/client/book/CivilRegistryBook.java')+whole('/client/book/pages/SimpleListPage.java')+whole('/client/book/pages/ListPage.java')+
 pick('/network/ClientInteractionManagerImpl.java','handleCivilRegistryResponse handleGuiRequest')+pick('/client/gui/ExtendedBookScreen.java','getBook')+
 pick('/item/ExtendedWrittenBookItem.java','use getBook')+pick('/server/world/data/PlayerSaveData.java','getLastSeenVillage')+
 pick('/util/NbtHelper.java','toList toStream fromList')+pick('/util/WorldUtils.java','loadData'),
 '真实村民死亡和村庄婚姻等事件向CivilRegistry.addText写历史；世界重载恢复JSON Text列表，玩家打开民事记录书后按lastSeenVillage请求服务器页，客户端接收转换并实际drawText。书页/网络只是同一历史对象消费链。',
 '主世界PersistentState文件mca_civil_registry_<villageId>，entries NbtList字符串，每项是Text.Serializer.toJson；内存LinkedList<Text>新记录addFirst，page(from,to)为范围子列表。VillageManager却按各传入维度单独加载mca_villages及各自ID计数。',
 'reader把nbt.get("entries")直接交toList，工具直接强转NbtList，没有缺键/错误类型fallback；逐项Text.Serializer.fromJson也没有隔离catch。writer重新建compound只写entries，保留Text JSON不是纯显示名；addText前插并markDirty。get只按村庄int id命名且总用overworld，未含源维度，在各维度村庄管理器可能同id的条件下共用历史键，属于身份命名边界，未运行复现。',
 '实际CivilRegistryPageRequest先PlayerSaveData.lastSeenVillage→当前世界VillageManager.getOrEmpty→Village.getCivilRegistry，服务器getPage只对to取min(size,to)，不限制from负值；返回客户端CivilRegistryBook.receive按14行包装并推进lastIndex，SimpleListPage.render实际画Text。每次book.open清客户端页缓存，说明客户端缓存不是历史真值。历史增补改变前端from索引快照，没有稳定版本/游标，不能当一致历史迁移协议。',
 'Dynasty永久历史标记与任务册记录应保存原始结构和身份命名域，明确世界/维度/玩家UUID，缺依赖或坏一项不覆盖其余历史。显示翻页缓存和永久数据分开；服务端确定输入范围，避免把当前UI读到的条数当完整历史验收。支持对旧任务入口fallback保留原ItemStack/进度键的策略研究，不复制此mod UI或生产代码。',
 '这不是玩家Clone实现，未发现本对象旧ID映射或历史格式升级，不能虚构。缺失entries和坏JSON具体原生错误方式、文件持久恢复及跨维度碰键未运行；完整字体换行/GUI绘制只读未打开。实际增补来源本批保留death/marry完整方法，其余所有事件未穷尽，不按事件种类或书页数加信用。',
 '整个CivilRegistry世界历史对象及真实书页展示合一族；与021Village父对象和019lastSeenVillage支持共用，独立真值在另一个历史文件，但主责若按同村庄历史合并则credit仍0。每页/JSON节点/网络包装/显示文本不是独立实现。')

add('mca-villager-tracker-uuid-global-position-registry-and-compass-carrier',
 [('/server/world/data/VillagerTrackerManager.java','VillagerTrackerManager',29)]+whole('/server/world/data/VillagerTrackerManager.java')+
 whole('/item/VillagerTrackerItem.java')+whole('/network/c2s/SetTargetMessage.java')+whole('/client/gui/VillagerTrackerSearchScreen.java')+pick('/ModelPredicatesMCA.java','setup')+
 whole('/util/MaxSizeHashMap.java')+
 pick('/entity/VillagerEntityMCA.java','tickMovement readCustomDataFromNbt writeCustomDataToNbt interactAt onDeath')+
 pick('/util/NbtHelper.java','toMap fromMap encodeGlobalPosition decodeGlobalPos')+pick('/util/WorldUtils.java','loadData'),
 '玩家曾互动的村民在周期tick、写NBT及死亡入口报告位置到主世界mca_villager_tracker；追踪道具选择UUID后周期读注册表，把GlobalPos写进物品并由真实指南针模型/距离tooltip消费。审查的是真实玩法追踪持久对象，不是泛用缓存库。',
 '主世界PersistentState root UUID字符串→GlobalPos.CODEC NBT(维度+BlockPos)，MaxSizeHashMap上限16384；物品targetUUID UUID/targetName字符串/position GlobalPos。setTarget按当前双手注册Item identifier比对后写姓名和UUID，未同时清旧position。',
 '恢复reader从root各键UUID::fromString、decodeGlobalPos，后者原生CODEC失败error日志→null，由NbtHelper.toMap过滤null；坏UUID未catch。codec统一维度/位置结构，不使用名称身份。bounded map默认LinkedHashMap插入序，removeEldest仅size>上限，非access-order LRU；重载从工具Map.putAll的遍历顺序不等于原始历史访问顺序，因此淘汰语义不能声称持久保持。',
 'set(Entity)只entries.put未markDirty，update仅config+server guard调用set；writeNBT确实写所有entries但不意味着自动触发保存。只有remove显式dirty，检索全部源码未见外部调用remove，因此普通跟踪更新持久提交存在静态缺口。村民onDeath是update最后位置而非remove，所以目标可以保留死亡/过期位置。物品inventoryTick若注册表无该UUID不清旧position；选择新目标也不清旧position，因此旧位置可继续显示至下次成功更新。tooltip只同维度显示距离，角度交原生CompassAnglePredicateProvider，未伪造跨维度导航。',
 'Dynasty永久进度/旧物品恢复要区分持久真值和派生位置缓存；身份UUID+维度可用但不会自动保证新旧对象一致。每个写入明确dirty/提交契约，不依赖另一次偶发删除触发保存；目标换绑或不可解码时保留原载荷同时标记旧缓存来源，避免旧显示冒充新恢复成功。上限/淘汰/过期字段不能混入死亡Clone永久白名单。',
 '无旧ID remap/Clone/显式legacy fallback，只有真实玩法载荷恢复，按协议相关范围提交credit0。未运行原生GlobalPos CODEC/指南针/离线世界保存/边界容量测试；MaxSizeHashMap只是支持，不作通用缓存实现计数。未读完整FamilyTree搜索界面/原生Compass算法，不宣称目标选择权限已验收或实际追踪准确。',
 'UUID位置注册表与追踪物品一个完整玩法家族：map/codec/道具目标字段/角度与tooltip/各报告入口不分计。与019FamilyTree搜索、020/021实体NBT持久支持共用，独立数据对象是外置位置注册表并有指南针实际消费者；若主责按派生缓存排除也不擅加credit，最终Kepler去重。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    suffixes=(['/server/ReaperSpawner.java'] if 'reaper-ritual' in row['family'] else ['/server/world/data/CivilRegistryManager.java','/client/book/CivilRegistryBook.java'] if 'civil-registry' in row['family'] else ['/server/world/data/VillagerTrackerManager.java','/util/MaxSizeHashMap.java'])
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
