"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-035'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))





















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
    (DOC/'batch-035.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
