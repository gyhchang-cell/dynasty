"""Chunk placed-owner persistence and attribution lifecycle, one object family."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-029/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-029','batch-030');footer=prior[prior.index('def generate():'):].replace('batch-029','batch-030')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('pmmo-chunk-placed-owner-map-persistence-piston-relocation-and-production-xp-attribution',
 pick('/storage/ChunkDataProvider.java','deserializeNBT')+whole('/storage/ChunkDataProvider.java')+whole('/storage/ChunkDataHandler.java')+
 pick('/setup/CommonSetup.java','onCapabilityRegister onCapabilityAttach')+
 whole('/events/impl/PlaceHandler.java')+whole('/events/impl/BreakHandler.java')+whole('/events/impl/PistonHandler.java')+
 whole('/events/impl/CropGrowHandler.java')+whole('/events/impl/FurnaceHandler.java')+
 whole('/mixin/ServerLevelMixin.java')+whole('/mixin/AbstractFurnaceTileEntityShrinkMixin.java')+whole('/mixin/CampfireMixin.java')+whole('/api/events/FurnaceBurnEvent.java')+
 pick('/events/EventHandler.java','onBlockPlace onBlockBreak onPistonMove onCropGrow onSmelt')+
 pick('/features/party/PartyUtils.java','getPartyMembers getPartyMembersInRange')+
 pick('/core/Core.java','awardXP get getData getExperienceAwards getCommonXpAwardData getConsolidatedModifierMap getObjectExperienceMap getObjectModifierMap isActionPermitted doesPlayerMeetReq')+
 pick('/storage/PmmoSavedData.java','setXpDiff setXpRaw awardScheduledXP')+pick('/core/CoreUtils.java','processSkillGroupXP')+
 pick('/registry/PerkRegistry.java','executePerk isPerkCooledDown'),
 '真实EntityPlace写入每区块放置者映射；区块capability序列化并加载后，生长/熔炼按位置归属玩家奖XP，破坏移除、活塞移动所有权，持久身份与瞬时连锁破坏者分别管理。一个区块归属对象，不把多个事件和getter加数。',
 '每LevelChunk上pmmo:placed_data capability；CODEC为BlockPos packed long的十进制string键→UUIDUtil.CODEC值。backend.placedMap持久，breakMap非持久；没有独立dimension字段，由所属区块世界提供。',
 'onCapabilityAttach为LevelChunk附provider，serialize从backend.getMap编码并resultOrPartial记录错误/空compound兜底；deserialize parse.result().orElse(empty)→new HashMap→setMap，未保存坏条目原NBT。BLOCKPOS primitive直接getStringValue/map(Long.valueOf).getOrThrow→BlockPos.of，无显式位置属于本区块验证/失效位置过滤。checkPos缺失返回Reference.NIL而非null；placedMap值是UUID，不含当前方块种类/放置时间/version，不能据同位记录证明还是原对象。getMap/setMap为可变引用，调用者更新须自己dirty。',
 'PlaceHandler通过权限/hook后server cap.addPos并chunk.setUnsaved(true)。BreakHandler先算自放reuse penalty(成熟CropBlock例外)再delPos/必要时setBreaker并dirty；不是死亡惩罚。PistonPre先删除将毁块，再从旧位置取owner逐一del，放入临时updateToMap后统一加新坐标/两端dirty，避免重叠移动时边遍历边覆盖；但structure.resolve返回未检查，Pre阶段先改记录，没有原生运动成功确认/事务回滚。ServerLevelMixin在destroyBlock的setBlock调用前取本chunk cap.getBreaker(邻位)并remove，一旦在线玩家找到则post BreakEvent并把breaker传到当前pos；breakMap不写入持久codec，没有TTL/重载恢复承诺，跨chunk邻位仍查本chunk因此不能声称所有连锁都获归属。',
 'Dynasty可借鉴持久资格/来源归属和一次运行传播状态分开保存，Clone只保审定永久字段，绝不因map能序列化就复制临时breakMap或免疫/姿态状态。旧位置/ID迁移应先读取完整来源到独立暂存，再确认目标写入成功，保留Count/tag/未知字段/失败来源以便重试；Pre事件先删源的方案只作为失败边界参考。维度由所属存储暗含时必须验证载荷归属，不将合法位置/未知UUID默认重建为新的本人进度。',
 'CropGrow只查在线player，离线直接return，非离线农作补发；源位置由上下相邻cascading tag推导，在源chunk cap中addPos新位置，未改用目标chunk且未显式setUnsaved，实际跨界/原生生长dirty结果未运行。Furnace/campfire声明Mixin post FurnaceBurnEvent，handler缺归属NIL最终无profile通常return；离线且profile缓存命中时new ServerPlayer不读原玩家存档，非登录实体，PartyUtils无team时含本人→core.awardXP→setXpDiff因PlayerList仍无该UUID而入029scheduledXP。不能据临时同UUID对象称原装备/位置/技能上下文完整恢复，也不保证有party时本人列入。Mixin实际注入签名、原生UUIDUtil/Chunk保存/取消优先级及外部钩子未启动验证；本批不研究新平台迁移，不声称损坏NBT可全部恢复。',
 '区块放置归属完整生命周期为一条，placed map读写、piston坐标迁移、reuse反刷、grow/furnace/campfire、一次breaker传播均同对象支持；没有按对象位置/存储条目或同codec方法拆分。029为玩家world XP真值，此处新增另一真实持久对象/空间重定位/生产归属语义，最终XP队列和Core方法重用不加数；若主责认为某事件仅支持则全部已合并。031vein玩家charge另待完整研究，不据本批cap getter偷加。credit0待Kepler。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix,needles in [('/storage/ChunkDataProvider.java',None),('/storage/ChunkDataHandler.java',None),('/config/codecs/CodecTypes.java',['BLOCKPOS_CODEC'])]:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
