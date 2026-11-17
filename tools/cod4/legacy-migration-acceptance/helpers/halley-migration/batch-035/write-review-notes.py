import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-033/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-033','batch-035');footer=prior[prior.index('def generate():'):].replace('batch-033','batch-035')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('naturesaura-named-overworld-ender-inventory-binding-carrier-and-actual-menu-restoration',
 pick('/blocks/tiles/BlockEntityEnderCrate.java','readNBT')+whole('/blocks/tiles/BlockEntityEnderCrate.java')+
 pick('/blocks/BlockEnderCrate.java','BlockEnderCrate getEnderName onAnvilUpdate use')+
 pick('/items/ItemEnderAccess.java','ItemEnderAccess use createMenu getDisplayName')+whole('/gui/ContainerEnderCrate.java')+
 whole('/misc/LevelData.java')+whole('/api/misc/ILevelData.java')+pick('/InternalHooks.java','getLevelData extractAuraFromPlayer auraPlayerInteraction')+
 pick('/reg/ModRegistry.java','register registerCapabilities')+pick('/Helper.java','getEquippedItem isEmpty')+
 whole('/api/aura/container/ItemAuraContainer.java')+whole('/blocks/tiles/ItemStackHandlerNA.java')+
 pick('/blocks/tiles/BlockEntityImpl.java','saveAdditional load writeNBT readNBT modifyDrop loadDataOnPlace canUseRightNow allowsLowerLimiter')+
 pick('/blocks/BlockContainerImpl.java','getDrops playerWillDestroy setPlacedBy'),
 '真实铁砧用名字和EnderEye给EnderCrate/EnderAccess创建绑定，放置crate恢复名称、实际菜单与自动化wrapper访问同名世界库存，拆掉block只携带绑定名不散落共享库存；Item远程打开同一份世界对象。整个共享存储生命周期1条，不按block/item/menu镜像拆信用。',
 '物品根naturesaura:ender_name string；tile TILE/SYNC name string；真实内容位于Overworld level_data SavedData.storages list{name,ItemStackHandlerNA payload}，每新name默认27格。各维度crate都ILevelData.getOverworldData；name是共享字符串键，没有playerUUID/owner，客户端本地LevelData只镜像菜单而非服务器真值。',
 'LevelData构造逐storage name→computeIfAbsent handler→deserializeNBT整个compound，save只编码非空handler后写name，空仓库名不保留；重复name复用同handler再读，原生后写覆盖/Size行为须另核native。SavedData.isDirty恒true，所以tile=null的27格handler虽不显式dirty，保存检查仍会认为有更新；不等于立即写盘/崩溃事务保证。物品绑定名不含库存，复制同name载荷会引用同份物品世界真值；block dropInventory覆写为空，modifyDrop写名，loadDataOnPlace服务器只接受非空名。readNBT name缺失不清旧name，空字符串键若存在则canOpen(name!=null)为true，不能把缺少绑定一概等同空档。',
 'onAnvilUpdate验证left是crate/access、right为EnderEye且Count>=leftCount、名字非空、目标storage无TOKEN_TERROR，stack.copy保留原Count/tag后只put绑定名；materialCost=stackCount。isEnderStorageLocked遍历物品是否有TOKEN_TERROR，仅被命名时调用，现有crate/远程item用名打开不再查token，源码不是玩家所有权安全锁。Block.use canOpen且canUseRightNow(2500)后drain/open；lower limiter存在才约束环境余额，否则允许负aura。wrapper insert/extract按实际结果数量扣aura，simulate不扣；getStack/setStack直接委托不收费，故不能宣称所有GUI逐物品更新都有同一扣费边界。',
 'Dynasty可借鉴任务册载体只保存稳定入口身份，而进度真值保在明确玩家/队伍/世界存储；恢复旧ID时校验目标对应同一主体，不能在缺入口/空name/未知ID时默认为新空进度。保留原栈Count/tag与未知键，只有目标注册/权限/可用性核对成功才提交；共享名字可用不是已有owner验证。Clone白名单只保经审定永久任务/官阶等，不整体复制仓库别名/临时充能与容器字段。显式区分“禁新建绑定”与“禁访问”政策，禁止把一个token判断移植为泛化恢复授权。',
 'ItemEnderAccess仅主手且名字非空；非client extractAuraFromPlayer(10000,false)返回true才openMenu，helper实际只要求所选ItemAuraContainer.drainAura>0，部分不足10000也可true，未运行复现；原生cap匹配优先Curios再inventory。createMenu使用原始world库存handler，不走crate每项aura wrapper；stillValid恒true，无当前物品/距离/身份重新校验，不据此声称存在网络越权。Container quickMove保留完整ItemStack copy/原栈移动，但nativeStack解码/容器网络/外部Curios与SaveData落盘未全文审查，未知坏ID/超27 Size无损不能保证。isDirty alwaystrue不弥补未知payload丢弃；writer不保存原storages外自定义NBT。没有旧别名fallback/Player Clone/原存档验收。',
 '035新增命名共享inventory真实对象，其全部binding/itemcarrier/worldcodec/menu/wrapper合1；033 LevelData存储方法已顺读，只是支持，这里有真正完整新对象消费者，不能把同read方法重复算额外。与010 EnderStorage/032 UUID pouch都涉及外置库存但名称身份/token命名限制/拆放carrier语义不同，Kepler最终按对象与实现去重，可合并或排除。empty/getter/每storage name/27slots/两Aura容器容量/平台移植不计；credit0/accepted=false。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix,needles in [('/blocks/tiles/BlockEntityEnderCrate.java',None),('/misc/LevelData.java',['enderStorages','FACTORY']),('/api/aura/container/ItemAuraContainer.java',None)]:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(v in fragment for v in needles):continue
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
