import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-034/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-034','batch-033');footer=prior[prior.index('def generate():'):].replace('batch-034','batch-033')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('naturesaura-chunk-aura-deviation-rehydration-to-active-index-and-persistent-moss-reuse-boundary',
 pick('/chunk/AuraChunk.java','deserializeNBT')+whole('/chunk/AuraChunk.java')+whole('/api/aura/chunk/IAuraChunk.java')+
 pick('/api/aura/type/IAuraType.java','forLevel isSimilar')+
 pick('/InternalHooks.java','createAuraChunk getLevelData getAuraSpotsInArea getSpotAmountInArea getAuraInArea getAuraAndSpotAmountInArea triangulateAuraInArea getLowestAuraDrainSpot getHighestAuraDrainSpot')+
 pick('/Helper.java','getAuraChunksWithSpotsInArea getLoadedChunk')+whole('/api/misc/ILevelData.java')+
 whole('/misc/LevelData.java')+
 pick('/events/CommonEvents.java','onChunkUnload onItemUse onLevelTick onPlayerTick onChunkWatch handleChunkWatchDeferred')+
 pick('/NaturesAura.java','NaturesAura setup preInit init')+pick('/reg/ModRegistry.java','register')+pick('/api/NaturesAuraAPI.java','instance')+
 whole('/packet/PacketAuraChunk.java')+pick('/events/ClientEvents.java','onClientTick')+
 whole('/chunk/effect/SpreadEffect.java')+pick('/chunk/effect/DrainSpotEffects.java','init')+
 whole('/blocks/tiles/BlockEntityNatureAltar.java')+whole('/api/aura/container/BasicAuraContainer.java')+whole('/blocks/tiles/ItemStackHandlerNA.java')+
 whole('/blocks/tiles/BlockEntityMossGenerator.java')+whole('/blocks/tiles/BlockEntityImpl.java')+pick('/items/tools/ItemPickaxe.java','useOn'),
 '真实LevelChunk attachment保存区域灵气偏差drain_spots；恢复后重建LevelData活跃索引，服务端20tick更新/传播与自然祭坛消费。Moss generator依赖另存converted_moss的有限历史抑制刚转换方块再生灵气；作为同一生产-环境资源链合1，不按点/生成器/缓存字段拆数。',
 'naturesaura:aura_chunk AttachmentType.serializable→IAuraChunk；NBT drain_spots list{pos packedLong,amount int,optional original_spread_pos packedLong}，默认环境值1000000在查询时叠加，持久map仅存正负偏差。各ServerLevel本地level_data SavedData内converted_moss list<long>与storages；auraChunksWithSpots/effectPowders/spawnLamps/查询cache/needsSync不写该SavedData。',
 'AuraChunk.deserialize先clear，再逐项DrainSpot ctor按缺省pos/amount读，original_spread_pos有键才设；addDrainSpot验证X/Z应属本LevelChunk，否则throw，没有局部catch或未知原始项旁存，已加载部分仍留内存。重复pos后项覆盖。最后addOrRemoveAsActive将nonempty对象注册到本维度LevelData，卸载移除该运行索引；不是靠把cache当存档恢复。markDirty会setUnsaved/needsSync并清两个cache；deserialize与客户端setSpots只重建索引不清cache，重复读入已查询实例的cache可能过时，新建实例初始为空，未运行复现。',
 '实际Aura查询仅枚举LevelData当前活跃已加载chunk，基线默认Aura+偏差；drain/store负amount直接return0，simulate不创建spot，真实变动删除0并dirty；int上下溢转到pos.above递归，未见原生高度边界在该方法内。SpreadEffect按可加载周围chunk选偏差目标并迁移量，继承originalSpreadPos后dirty。update只对正值且origin非null且超过maxSpreadRange点fizzle；旧payload缺origin读为null，因此不受这一项距离检查，不自动补原点/版本升级。不是任意历史维度数据可重用当前chunk，维度归属由attachment宿主提供。',
 'Dynasty可借鉴持久真值、运行索引和客户端派生数据分开，Clone只复制经审定永久字段而非查询缓存/待发消息/免疫姿态计时器。旧格式缺字段须定义语义默认及一致性校验，不能把异常项导致整批重建为空作为成功；保留源NBT/Count/tag/未知ID，按项验证后才提交。坐标载荷需验证维度与所属对象；固定512条的反刷历史是有意有限窗口，不能类比永久任务历史被截断。同一逻辑读取后重建依赖索引，并明确旧对象cache失效，避免重载前后真实状态与回显不同。',
 'LevelData.isDirty恒true使无tile回调的普通27格enderStorages/converted_moss也在保存检查中参与；此批仅顺读storage，不按另一个read方法给credit。addMossStone超过512删首，load不检查数目/去重/当前方块；实际ItemPickaxe/含chisel路径记录位置，MossGenerator遇已记录moss跳过，若不再匹配则remove，生成后改block。NaturalAltar实际chunk drain→500000 buffer→为item充能或按recipe推进；TILE读recipe需hasLevel，未就绪不保留deferred ID，缺失recipe走null而timer可保留，后续重选recipe边界未运行。BasicAuraContainer读int不clamp/dirty；altar改变buffer/timer不显式setChanged，只item handler变更触发，不能声称所有中途进度立即落盘。SaveType.BLOCK不带altar库存/容器/recipe，不能把放置恢复当整tile复制。',
 '所有aura读写/点传播/活跃索引/packet/watch队列/祭坛/苔石生产链为1建议。server PENDING_AURA_CHUNKS按UUID只存chunkpos、每10tick重试未加载项，未见维度/TTL/logout清理；client包也无dimension，level==null清队列，tryHandle异常日志后returntrue删除；不据此认定跨维度实际错误。其它DrainSpotEffects注册列表只是支持，其余效果实现未全面审查，无其独立信用。无显式旧Forge capability→attachment迁移/PlayerClone，branch名1.20不冒充特定Minecraft小版本。NeoForge native附件/原生SaveData与外部网络/能力实际时序未启动验证，254文件1260方法索引不计。广义资源存储与既有能源参考相近但完整本对象空间偏差/加载索引/来源窗口由Kepler最终语义裁定；credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix,needles in [('/chunk/AuraChunk.java',None),('/misc/LevelData.java',None),('/events/CommonEvents.java',['PENDING_AURA_CHUNKS']),('/api/NaturesAuraAPI.java',['AURA_CHUNK_ATTACHMENT','INSTANCE']),('/blocks/tiles/BlockEntityNatureAltar.java',None)]:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type not in ['field_declaration','static_initializer']:continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(v in fragment for v in needles):continue
            e=dict(sample,node_type=n.type,name=(fragment.split('=')[0].split()[-1] if n.type=='field_declaration' else 'static_initializer'),start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
