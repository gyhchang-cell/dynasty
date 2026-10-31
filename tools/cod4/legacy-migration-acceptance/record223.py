import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()));root='b341418071c9c065286d'
sel={'EnergyCellBlockEntity.java':{'loadTag','saveAdditional','importSettings','exportSettings','injectAEPower','extractAEPower','onAmountChanged','setChangedNoTicketUpdate','tickingRequest'},'StoredEnergyAmount.java':{'setStored','insert','extract'},'EnergyCellBlockItem.java':{'injectAEPower','extractAEPower'},'AEBaseEntityBlock.java':{'getDrops','setPlacedBy'},'EnergyService.java':{'extractProviderPower','injectProviderPower','extractAEPower','addProvider','addRequester'}}
s=[c['candidate_id'] for c in cs if c['repo']=='AppliedEnergistics/Applied-Energistics-2' and c['path'].split('/')[-1] in sel and c['method'] in sel[c['path'].split('/')[-1]]]
a=accepted(root,'ae2-energy-cell-clamped-durable-balance-portable-component-and-grid-consumption','完整EnergyCellBE/StoredEnergyAmount/EnergyCellBlock/Item；base真实拆块放置方法及EnergyService取注能实际调用','internalCurrentPower double与neighborChangePending boolean，磁盘getDoubleOr0/getBooleanOrfalse；STORED_ENERGY持久Codec.DOUBLE便携物品','setStored小于MIN_AMOUNT归0再clamp0..maximum并发阈值事件；实际inject/extract只有MODULATE更新balance并无ticket标chunk unsaved；拆物export仅DISMANTLE且>0→component，放置import且非null恢复','补全旧pending数值wrapper到真实业务保值和消费链，普通/致密单元同类一个owner；StoredEnergyAmount通用辅助与grid service只支持0，不按能量阈值/数值字段/两容量拆。派生fullness与邻居延迟通知单独处理：load恢复余额再恢复pending，onReady从余额更新显示，不把缓存当永久玩家成就。','容量下降裁剪且无旧溢出旁存；NaN未显式finite检查，不能声称clamp处理全部脏数。setStored事件在load期间发但super grid初始化内部未全展开。Item途径直接amount运算无非负/容量裁剪保护，不同于BE严格存储；出口仅首个同BlockItem加components，无世界/物品联合事务。markUnsaved若chunk取不到直接skip，pending true已有时不再alert，真实tick卸载边界未运行。current modernValueInput/组件API不能直接移植Dynasty1.20.1。读取完整真实消费方法不等于整个AE网络/平台/原生codec已审或测试。',s)
a['reassessment']={'prior_status':'pending','support_batch':223,'reason':'补完整stored amount实现、真实grid消费及实际拆块carrier→放置恢复；不以数值包装层独立计数。'}
for f in (O/'reviews').glob('*.json'):
 rows=json.loads(f.read_text());changed=False
 for n,r in enumerate(rows):
  if r['candidate_id']==root:rows[n]=a;changed=True
  if r['candidate_id']=='8f8495e8215753156401':
   rows[n]={**r,'status':'rejected','reason':'本轮重读完整IMiner并固定源全src搜索：只有interface定义没有implements/调用readMinerData/addMinerData，默认getter0/setter空；Prisoner实现ILooter非IMiner，自身读取MineTimes正确且已040同链排除。接口错键EnchantCool为未接入负例，不能冒称实际游戏恢复实现。'};changed=True
 if changed:f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
extra=[c['private_file'] for c in cs if c['candidate_id'] in set(s)]
r='tools/cod4/legacy-migration-acceptance/.work/sources/AppliedEnergistics__Applied-Energistics-2/src/main/java/appeng/'
extra += [r+'api/ids/AEComponents.java',r+'core/definitions/AEBlockEntities.java',r+'block/networking/EnergyCellBlock.java']
record(223,[],extra)
(O/'semantic-reassessment-20261029-003.json').write_text(json.dumps({'accepted_candidate':root,'prior_status':'pending','credit_change':1,'excluded_interface':'8f8495e8215753156401','scope':'补实际能量消费与carrier桥。IMiner未接入而排除，不重复计Prisoner。若重生成早期记录须再执行record223。','production_modified':False,'gui_started':False},ensure_ascii=False,indent=2)+'\n')
