"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-032'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))


















def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('roots-old-inline-pouch-inventory-to-uuid-world-inventory-migration-and-herb-spending',
 pick('/handler/PouchHandler.java','PouchHandler')+whole('/handler/PouchHandler.java')+whole('/handler/OldPouchHandler.java')+
 whole('/world/data/PouchHandlerRegistry.java')+whole('/world/data/PouchHandlerData.java')+whole('/item/PouchType.java')+whole('/handler/IPouchHandler.java')+pick('/item/ItemApothecaryPouch.java','ItemApothecaryPouch')+pick('/item/ItemHerbPouch.java','ItemHerbPouch')+pick('/item/ItemFeyPouch.java','ItemFeyPouch')+
 pick('/item/ItemPouch.java','ItemPouch getType getPouchType getHerbQuantity onItemRightClick createData getNbtQuantity useQuantity addHerbToNbt')+
 whole('/util/ServerHerbUtil.java')+whole('/util/CommonHerbUtil.java')+pick('/integration/baubles/pouch/BaublePowderInventoryUtil.java','getPouch')+
 pick('/container/ContainerPouch.java','ContainerPouch createPouchSlots isApothecary isHerb isFey createHerbPouchSlots createFeyPouchSlots createComponentPouchSlots createApothecaryPouchSlots createPlayerInventory canInteractWith transferStackInSlot slotClick detectAndSendChanges onContainerClosed PouchSlot isItemValid onSlotChange onSlotChanged')+
 pick('/GuiHandler.java','getServerGuiElement')+pick('/event/ItemEventHandler.java','onEntityItemPickup')+
 pick('/spell/SpellBase.java','costsMet enactCosts enactTickCosts')+pick('/item/ItemStaff.java','onItemRightClick onUsingTick')+
 pick('/api/Herb.java','getName equals')+pick('/init/HerbRegistry.java','getHerbByItem isHerb'),
 '真实右键/服务器容器/草药数量查询首次构造PouchHandler；检测旧ItemStack根handler compound，将旧背包普通/草药格转换进UUID索引的世界WorldSavedData，随后真实GUI取放、拾取refill与法杖施法耗草药使用恢复后的对象。整个迁移+持久消费一个家族，不按包类型/槽位/方法计数。',
 '旧handler.inventory_slots/herb_slots经OldPouchHandler及Forge ItemStackHandler解码；APOTHECARY强制旧Size为18/9，其余旧handler默认12/6。新ItemStack根bag_id UUID；维度0 MapStorage下Inventory-UUID，保存pouch ordinal/inventory/herbs。物品根的草药名(path)double保存不足一个物品的已提取余量，不在世界herbs格内。',
 '构造先选既有bag_id或随机创建数据并写bag_id，再读取旧handler所有非空ItemStack，调用insertItemStacked(false)分别合并普通/草药区；没有用new Item重造这些栈，保留Count/tag意图可见，但底层Forge未知ID/损坏栈解码未全文研究。任一插入余量只error日志，仍removeTag(handler)与markDirty，不保留失败余量原项/事务确认；迁移是由旧键存在触发的一次路径，不能保证崩溃两处持久化一致。其他物品根键未清空，旧槽位编号压为非空列表并重新堆叠，不承诺原索引。',
 'Registry.getData只用UUID+当前物品PouchType查维度0；若缺数据或data.type!=type，直接new空对象覆盖同名MapStorage，不升级保留旧对象；同UUID克隆物品可指向同份数据，没有owner/player/dimension权限字段。PouchHandlerData字符串构造UUID.fromString无兜底，延迟read按ordinal建handler，缺pouch为0(HERB)，越界fromOrdinal返回null→createHandler抛异常；读取不保留未知根字段，handler.deserializeNBT容量由原生Size语义决定。upgrade虽然按ordinal升type并setSize保前min(old,size)，本仓库未找到实际调用，不能宣称现有升级配方已用它迁移。',
 'Dynasty可借鉴明确旧载荷触发、先枚举完整输入再转换、永久存储身份与物品关联分离；但任务册/Count/tag/未知ID需要保留原始NBT与每个余量，在目标写入与持久确认成功后才删旧键，失败保持可重试且防重复提交。UUID相同而对象类型变更应显式迁移/隔离旧对象，不自动创建空档覆盖真值；查不到外部任务入口同样不等于旧进度为零。Clone仅保审定永久字段，不因一个bag_id关联就copy所有资源/临时余量/计时器；healing_talisman历史替代语义不变。',
 '实际ContainerPouch服务器选手持/副手/首包，取新handler；canInteractWith比较持有的pouch，槽位禁止嵌套包，detectAndSendChanges持续markDirty，关闭saveAllData却用player当前世界MapStorage，而数据固定维度0，跨维度即时落盘结果未运行验证。草药useQuantity从world格extract一件后在物品根创建1.0余量，再递归扣小数；SpellBase.costsMet及ItemStaff成功cast才调用enactCosts/连续tickCosts。自动拾取refill直接grow栈/stacks.set未显式markDirty，只有其他容器/迁移写入路径可能补dirty；不能保证脱离GUI的refill单独落盘。外部MysticalLib ItemUtil、Forge ItemStackHandler/ItemHandlerHelper、Baubles本体/native MapStorage未全域审查，无游戏/测试/上游运行；ContainerPouch源头含单独版权限制，仅供研究不复制实现。',
 '组件/药剂师/草药/fey包、旧Size修补、UUIDRegistry、世界数据读写、GUI、refill、法杖耗用均同一个包迁移对象链，全部合为1建议。旧包accessor/新世界读写/upgrade未调用体/packet/每草药key不拆信用。与014路由安全、024 AA袋子普通库存广义NBT相近，但本对象实际inline→UUID外置迁移且有剩余失败边界；Kepler最终去重，可合并/排除，不以750下载或4223 AST数量计数。credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/handler/PouchHandler.java','/handler/OldPouchHandler.java','/world/data/PouchHandlerData.java']:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
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
    (DOC/'batch-032.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
