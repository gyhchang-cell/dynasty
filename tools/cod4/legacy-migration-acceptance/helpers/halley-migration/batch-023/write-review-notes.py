"""Render one manually reviewed UUID world-record family; no method-count credit."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-022/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-022','batch-023');footer=prior[prior.index('def generate():'):].replace('batch-022','batch-023')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('actuallyadditions-uuid-world-player-record-disk-sync-field-policy-and-real-booklet-trials',
 pick('/data/PlayerData.java','readFromNBT')+whole('/data/PlayerData.java')+whole('/data/WorldData.java')+
 pick('/ActuallyAdditions.java','serverStarted serverStopped init')+
 pick('/event/CommonEvents.java','onLogInEvent onCraftedEvent')+pick('/event/ClientEvents.java','ClientEvents onClientTick')+
 pick('/network/PacketHandlerHelper.java','syncPlayerData sendPlayerDataToServer')+pick('/network/PacketHandler.java','init')+[('/network/PacketHandler.java','handleData',125)]+
 whole('/network/PacketClientToServer.java')+whole('/network/PacketServerToClient.java')+
 pick('/booklet/misc/BookletUtils.java','getBookletPageById')+pick('/booklet/gui/GuiBooklet.java','initGui onGuiClosed')+
 pick('/booklet/gui/GuiMainPage.java','actionPerformed')+
 whole('/booklet/chapter/BookletChapterTrials.java')+whole('/booklet/page/PageTrials.java')+
 pick('/booklet/page/BookletPage.java','getIdentifier')+pick('/booklet/chapter/BookletChapter.java','getPageIndex')+
 pick('/items/ItemWingsOfTheBats.java','livingUpdateEvent getWingItem showDurabilityBar getDurabilityForDisplay getRGBDurabilityForDisplay')+
 pick('/misc/apiimpl/LaserRelayConnectionHandler.java','readNetworkFromNBT')+pick('/misc/apiimpl/ConnectionPair.java','readFromNBT')+
 pick('/util/StackUtil.java','isValid'),
 '服务器启动forceLoad actuallyadditionsdata世界记录，UUID查找PlayerSave，登录同步客户端；真实手册书签/教程/试炼标记更新后发回服务器dirty保存，翅膀每tick消费恢复状态。整个玩家持久对象合一族，不按字段或网络分支拆数。',
 'WorldData.PlayerData列表：UUID + Data compound。PlayerSave磁盘savingToFile=true保存BookGotten/DidTutorial/HasBatWings/BatWingsFlyTime、12格书签页面ID、Trials字符串列表；同步savingToFile=false额外ShouldDisableWings。lastOpenBooklet仅client内存，不写NBT。',
 'getDataFromPlayer先检map命中和save.id==玩家UUID，失败new PlayerSave替换并dirty；不是读取玩家NBT/Clone。WorldData静态唯一data在serverStarted以server.getEntityWorld强制载入，serverStopped及无client world时clear；后续get(world)未按维度或side重新分key，因此不将其当跨世界身份隔离范本。read先clear/恢复laser网络，再clear/恢复PlayerData；连接Type非空非法值会在LaserType.valueOf抛异常并阻止后续玩家载荷读取，未逐子对象隔离。',
 'savingToFile真正限制ShouldDisableWings只走同步，并非全部临时字段隔离：HasBatWings/BatWingsFlyTime仍上磁盘，不能当Dynasty永久Clone白名单。loadBookmarks只按输入列表长度写固定12数组，>12越界，短列表重复载入未清尾部；页面ID由chapterID+page index生成，当前查找不到→null，下次writer写空串导致未知页ID不可逆丢失。loadTrials先clear，忽略空串但保留未知非空ID和重复；真实PageTrials按钮仅手工toggle完成标记并同步，不能称服务器自动验证任务达成。',
 'Dynasty永久进度可借鉴独立UUID持久对象与明确disk/sync字段协议，但需保留已审永久字段、未知历史标记和原ItemStack Count/tag；不复制完整WorldData或飞行/临时disable状态。旧页面/任务入口暂不可解析时保留原ID，别将null回写空串；限长/短载荷重置策略与字段组类型需要明确，单个坏对象不得阻断其他玩家恢复。此处无已确认Clone钩子，不把该研究变成本地存档迁移或新生产实现。',
 '本固定源码检索未见MissingMappings/remap或Clone处理，不虚构旧别名兼容。磁盘player数据取值不会单靠UUID证明原生死亡/跨端流程已验收；没有跑游戏/上游/网络/存档。PLAYER_DATA_TO_SERVER使用载荷World+UUID找玩家，ctx没有在该handler绑定真实发送者，且直接接受书签/教程/试炼；包调度源码已读，但未全域安全审计，不宣布漏洞复现。飞行更新sync本身不dirty，首次建玩家/首次送书/客户端数据回传与serverStarted会dirty；不能把偶发dirty等同每次飞行状态提交保证。底层Forge世界保存/native UUID连续性未执行。',
 '唯一PlayerSave世界对象家族：BookGotten/教程/书签/Trials/翅膀与登录同步/双向包/两端调度都支持一条，不因字段数/试炼个数/包ID多计。Laser网络解码仅证明同WorldData容器先序失败边界，本条不拿网络读写独立credit；后续若完整研究真实激光网络玩法需另做语义边界复核。主责Kepler最终去重，credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=[('/data/PlayerData.java',None),('/data/WorldData.java',None),('/network/PacketHandler.java',['IDataHandler SYNC_PLAYER_DATA','IDataHandler PLAYER_DATA_TO_SERVER']),('/booklet/gui/GuiBooklet.java',['BookmarkButton[] bookmarkButtons'])]
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
q=(b.parent/'batch-022/record-document-integrity.py').read_text().replace('batch-022','batch-023').replace("'reused_batch019_files_not_credit':477,'new_downloaded_files_not_credit':0", "'reused_batch019_files_not_credit':0,'new_downloaded_files_not_credit':474")
(b/'record-document-integrity.py').write_text(q)
