import json
from review_batch import accepted,record,O
cs=[c for c in map(json.loads,(O/'candidates.jsonl').read_text().splitlines()) if c['repo']=='ldtteam/minecolonies']
def get(f,m):return next(c['candidate_id'] for c in cs if c['path'].endswith('/'+f+'.java') and c['method']==m)
def support(fs,r):return [c['candidate_id'] for c in cs if any(c['path'].endswith('/'+f+'.java') for f in fs) and c['candidate_id']!=r]
rows=[]
def add(f,m,fam,t,i,o,p,l,fs):
 r=get(f,m);rows.append(accepted(r,fam,t,i,o,p,l+' 固定官方Minecolonies61292848b81ee4a7a33443beb52aabdc446355b8静态源码研究；无游戏/原档操作、不宣称运行验收，框架/网络支持0。',support(fs,r)))
add('WorkManager','read','minecolonies-durable-work-queue-legacy-claim-identity-upgrade-and-side-effect-suppression','完整WorkManager/AbstractWorkOrder/WorkOrderBuilding全文；真实onColonyTick根据已认领/优先级派给有工人的builder，onCompleted移单和后续advance。','newsystem标志、workOrders列表；type、id、claimedBy旧citizenId或claimedByBuilding新BlockPos，已清场/已请求/资源余量/阶段/路径事实。','旧removal类型映射WorkOrderBuilding；旧认领ID存在时经CitizenManager取工作楼坐标，否则读新坐标；manager清map、复原ID、失效认领清空。readingFromNbt使add跳当前界限预检/不重发创建advance/不重放construction tape。','真实已开始工作队列恢复1。mapping、claim布局转换、已请求收据、builder assignment和完成同链，不按4type/每阶段拆；真实世界blueprint与future对象均不保存，恢复后按事实加载。纯注册表/名称显示支持0，区别道路外交pending path266。','缺newsystem主动清全部旧单，不视为可靠兼容；仅contains不检bool值false也进入新分支。旧claimedBy即使无效仍优先阻新格式fallback。未知type在nameToClassBiMap.get(type).getA处NPE不在第一段catch范围，后续read RuntimeException catch不能兜此前；坏ordinal被后段捕捉返回null丢单，无opaque保留。topWorkOrderId read不reset；重复同位置read会remove旧单触发onRemoved副作用；部分dirty仅manager网络flag不证明每步磁盘原子。只读代码，未审蓝图/实际结构放置AI，不是制作建筑。',['WorkManager','AbstractWorkOrder','WorkOrderBuilding'])
record(272,rows)
