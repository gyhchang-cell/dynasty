"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-027'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))













def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('actuallyadditions-phantom-coordinate-binding-restoration-to-remote-capability-and-world-operation',
 pick('/tile/TileEntityPhantomface.java','readSyncableNBT')+whole('/tile/TileEntityPhantomface.java')+
 whole('/items/ItemPhantomConnector.java')+whole('/blocks/BlockPhantom.java')+
 whole('/tile/TileEntityPhantomItemface.java')+whole('/tile/TileEntityPhantomEnergyface.java')+whole('/tile/TileEntityPhantomLiquiface.java')+
 whole('/tile/TileEntityPhantomRedstoneface.java')+whole('/tile/TileEntityPhantomPlacer.java')+whole('/tile/TileEntityPhantomBreaker.java')+
 whole('/tile/TileEntityInventoryBase.java')+whole('/util/ItemStackHandlerAA.java')+
 pick('/util/WorldUtil.java','doEnergyInteraction doFluidInteraction useItemAtSide getDirectionBySidesInOrder setHandItemWithoutAnnoyingSound')+
 pick('/util/StackUtil.java','canAddAll addAll testDummy findFirstFilled isValid shrink getEmpty')+
 pick('/tile/TileEntityBase.java','init register update updateEntity writeToNBT readFromNBT readSyncableNBT writeSyncableNBT getCapability hasCapability sendUpdate getUpdatePacket saveDataOnChangeOrWorldStart shouldSaveDataOnChangeOrWorldStart setRedstonePowered respondsToPulses activateOnPulse isRedstoneToggle')+
 pick('/blocks/base/BlockContainerBase.java','getDrops onBlockPlacedBy updateTick neighborChanged neighborsChangedCustom updateRedstoneState')+
 whole('/util/VanillaPacketDispatcher.java'),
 '连接器将点击世界坐标/维度存入物品，再传入IPhantomTile；Tile存档恢复坐标后，经真实range/类型guard转发目标capability或远程放置/挖掘。所有phantom类型和重复reader合为一持久目标家族，不另加每个消费者。',
 '工具XCoordOfTileStored/YCoordOfTileStored/ZCoordOfTileStored/WorldOfTileStored；Tile xOfTileStored/yOfTileStored/zOfTileStored与Range，placer另Side。Items由共同TileInventory位置列表持久，仅SAVE_TILE常规存取；coords/Range/Side明确排除SAVE_BLOCK。',
 '连接器getStoredPosition以(0,0,0)为无绑定，不支持真实原点；getStoredWorld由维度ID找已存在world，传入仅在getStoredWorld(stack)==当前world时生效；setBoundPosition只设坐标，sendUpdate后清工具键，不带维度/UUID/目标方块类型到Tile。face和placer reader复用同坐标格式且零坐标不清旧boundPosition，非零则markDirty；SAVE_BLOCK完全不恢复绑定，故拿起拆放不自动接续旧目标。存档内Range并非永久资格，server tick由连续3个booster倍增重算(16或3)。',
 'face.hasBoundPosition拒绝自身坐标及任意IPhantomTile，其他空目标保留；getCapability每次按当前坐标getTileEntity并range/type检查，身份是位置而非原Tile UUID，替换同位方块会接入新Tile。Itemface要求目标至少一个方向item handler；Energy/Fluid排除各自LaserRelay且筛能力；转发使用原查询facing，邻居能量/液体实际投递由base.updateEntity→WorldUtil，先simulate drain再填目标再实际drain，不等于多系统原子交易。父base先share，face随后重算range；启动首tick可在重算前使用持久Range，未实际运行。',
 '对Dynasty旧目标引用和永久进度分开迁移：保留源Count/tag和原身份载荷，明确维度+UUID或坐标语义、空目标可等待与永久失效的不同处理；不能用全零哨兵占掉合法位置，也不能缺键保留旧实例值。Clone批准白名单不应复制Range/side/currentTime或跨重生远程连接缓存。目标载入后重新校验当前世界/类型/权限再允许真实消费，不把仅保存显示数据当恢复完成。重复coords reader和多种capability只借鉴一处。',
 'placer/breaker各9槽，恢复Side无界但getDirectionBySidesInOrder非法值统一WEST；currentTime不写NBT。hasBoundPosition含world.dimension==自身同一值比较，不能视为跨维度验证。常规30tick倒计时/红石pulse调用doWork；breaker从boundPosition查state，却getDrops参数position传本机pos，dummy复制槽模拟能容纳后setBlockToAir，再addAll无返回确认；这里只记录潜在位置/提交边界，未声明掉落丢失复现。placer用首非空槽→WorldUtil.useItemAtSide：红石直接setBlockState后减1不查返回，植物查成功，其他用FakePlayer复制手中栈并返回结果，catch非finally故异常时未保证恢复假玩家旧手。未运行任何FakePlayer或GUI；原生权限事件/handler/LootTable/图形网络底层未全文审，不能宣称实际权限漏洞或事务保证。',
 'Phantom完整坐标持久目标只一条，face/placer重复reader、能源/物品/液体/红石、origin哨兵、booster与方位不拆。face工具/getStoredWorld/clearStorage与024激光创建、026接口范围使用有共同支持，无额外信用；这里不同真值是Tile持久坐标和实际远程消费。与014ModularRouters targets宏观相似但具体持久对象/运行验证及提交顺序不同，仍由Kepler对全主账语义合并/拒绝。credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/tile/TileEntityPhantomface.java','/tile/TileEntityPhantomPlacer.java','/tile/TileEntityPhantomRedstoneface.java']:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode();e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
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
    (DOC/'batch-027.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
