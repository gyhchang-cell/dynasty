from pathlib import Path
import json, hashlib, datetime, html
B=Path(__file__).resolve().parent
R=B.parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):
 (B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
FR={
 'Entity':[[317,362],[421,497],[550,562],[1570,1795],[3143,3163],[3270,3294],[3340,3385],[3430,3460],[3540,3566]],
 'EntityType':[[457,463],[507,627]],'EntityStorage':[[1,125]],'EntityPersistentStorage':[[1,16]],
 'EntityLookup':[[1,61]],'EntitySectionStorage':[[1,135]],'EntitySection':[[1,78]],
 'LevelEntityGetterAdapter':[[1,43]],'EntityGetter':[[1,52]],'Level':[[638,714]],
 'ChunkMap':[[1144,1188],[1330,1413]],'ServerChunkCache':[[451,470]],'ServerEntity':[[210,243]]}
VR={
 'Entity':[[412,488],[541,553],[1556,1739],[3072,3092],[3198,3222],[3269,3320],[3367,3390]],
 'FireworkRocketEntity':[[1,284]],'ServerEntity':[[205,302]],'ClientboundAddEntityPacket':[[1,145]],
 'ClientPacketListener':[[435,510],[580,601]],'DamageSources':[[1,125],[195,217]],
 'ServerLevel':[[1065,1087],[1377,1387],[1446,1516]],'LevelEntityGetterAdapter':[[1,43]],
 'EntityLookup':[[1,61]],'ChunkMap':[[1134,1178],[1319,1400]],'ClientLevel':[[319,350],[914,949]],
 'TransientEntitySectionManager':[[1,149]],'ServerChunkCache':[[445,463]]}
m=json.loads((B/'native-source-manifest.json').read_text()); sources=[]
for f in m['files']:
 stem=Path(f['path']).stem; prefix='F' if f['version']=='forge-47.3.0' else 'V'
 ranges=(FR if prefix=='F' else VR).get(stem,[])
 f['id']=prefix+'-'+stem; f['reviewed_ranges']=ranges
 f['read_status']='FULL_FILE_READ' if ranges==[[1,f['lines']]] else 'SELECTED_RANGES_READ' if ranges else 'EXTRACTED_NOT_REVIEWED'
 f['review_recorded_utc']=now
 sources.append(dict(id=f['id'],version=f['version'],local=f['reading_view'],sha256=f['reading_view_sha256'],lines=f['lines'],reviewed_ranges=ranges,read_status=f['read_status'],provenance='native-source-manifest.json'))
m['review_recorded_utc']=now
save('native-source-manifest.json',m)
existing=[]
def ext(id,local,version,ranges,origin):
 p=B/local
 e=dict(id=id,local=local,version=version,sha256=sha(p),lines=len(p.read_text().splitlines()),reviewed_ranges=ranges,read_status='SELECTED_RANGES_READ',provenance=origin)
 if ranges==[[1,e['lines']]]:e['read_status']='FULL_FILE_READ'
 existing.append(e);sources.append(e)
base='../batch-08/native/'
ext('F-PersistentEntitySectionManager',base+'forge-47.3.0/reading-view/net/minecraft/world/level/entity/PersistentEntitySectionManager.java','forge-47.3.0',[[37,320],[360,455]],'../batch-08/native-reconstruction.json')
ext('F-ServerLevel',base+'forge-47.3.0/reading-view/net/minecraft/server/level/ServerLevel.java','forge-47.3.0',[[317,357],[380,398],[680,722],[813,815],[854,866],[1098,1120],[1418,1432],[1480,1566]],'../batch-08/native-reconstruction.json; addFresh ranges also reviewed in batch08 N05')
ext('V-Projectile',base+'vanilla-mcp-1.20.1/reading-view/net/minecraft/world/entity/projectile/Projectile.java','vanilla-mcp-1.20.1',[[1,220]],'../batch-08/native-reconstruction.json')
ext('V-AbstractArrow',base+'vanilla-mcp-1.20.1/reading-view/net/minecraft/world/entity/projectile/AbstractArrow.java','vanilla-mcp-1.20.1',[[45,175],[259,272],[281,393],[468,513],[576,608]],'../batch-08/native-reconstruction.json')
ext('V-PersistentEntitySectionManager',base+'vanilla-mcp-1.20.1/reading-view/net/minecraft/world/level/entity/PersistentEntitySectionManager.java','vanilla-mcp-1.20.1',[[37,101],[112,132],[188,263],[412,438]],'../batch-08/native-reconstruction.json')
bmod='../batch-06/sources/dercodeKoenig__marvins-minecraft-mods/aw_vehicles/src/main/java/Vehicles/'
ballista='dercodeKoenig/marvins-minecraft-mods@20d02ec1300ff6011683d9fd43ef76fd47256234; MC1.20.1 Forge47.3.0 mod1.0.6'
ext('B-Ballista',bmod+'Ballista.java',ballista,[[29,145],[191,245],[276,334]],'../batch-06/ballista-world-emplacement.json')
ext('B-BallistaBolt',bmod+'BallistaBolt.java',ballista,[[27,196]],'../batch-06/ballista-world-emplacement.json')
multicharge='ZaLa0987654321/CrossbowMulticharge@90c26a9023170b9a0d49be1307e61097b8aa4484; MC1.20.1 Fabric loader0.16.10 API0.92.6+1.20.1 Yarn1.20.1+build.10 mod0.11'
ext('M-CrossbowMixin','../batch-07/sources/src/main/java/org/zala/crossbowmulticharge/mixin/CrossbowMixin.java',multicharge,[[230,337]],'../batch-07/crossbow-multicharge-lifo.json')
save('existing-source-review.json',dict(recorded_utc=now,method='历史固定源码的新增选读或明确复用范围；不修改历史批次，不增加家族计数。',files=existing,new_reference_credit=0))
# Range evidence refers to the exact hashed local sources above, not a list of downloaded files.
evidence=[]
def ev(id,family,title,claim,refs,limit='源码静态结论；没有实机复现，也不是实际Fabric合并运行时。'):
 evidence.append(dict(id=id,family=family,title=title,claim=claim,support=[dict(source=s,ranges=rs) for s,rs in refs],qualification=limit,independent_reference_credit=0))
ev('L01','P-BALLISTA','原始owner不等于Projectile归属','BallistaBolt直接继承Entity，自有owner是普通Entity引用；自有NBT仅shotEnd。基础Entity保存位置、Motion、NoGravity及实体自身UUID，不会自动保存这个owner、hitEntities或ticksInGround。', [('B-BallistaBolt',[[27,44],[185,195]]),('F-Entity',[[1570,1795]])])
ev('L02','P-BALLISTA','装填重接是重叠查询','Ballista只有drawProgress==1且bolt==null时查自身AABB，取首个shotEnd=false的箭，覆盖其owner、清空hitEntities、设无重力并归位。箭加入时只通知首个重叠Ballista；没有按保存的双方UUID配对。', [('B-Ballista',[[64,93],[307,324]]),('B-BallistaBolt',[[54,60]])])
ev('L03','P-BALLISTA','列表首项不代表原归属或最近','EntityGetter转入类型过滤查询；Level将结果追加至列表，SectionStorage遍历可访问区段、Section做AABB相交。选读路径没有距离排序或Ballista双方归属过滤，不能将get(0)解释为最近或原配。', [('F-EntityGetter',[[1,52]]),('F-Level',[[638,714]]),('F-LevelEntityGetterAdapter',[[1,43]]),('F-EntitySectionStorage',[[1,135]]),('F-EntitySection',[[1,78]])])
ev('L04','P-BALLISTA','飞行箭读档与普通箭不同','飞行箭若重新构造后没有通过重叠查询关联，owner保持null；其实体伤害分支明确要求owner!=null。该结论不等于Motion丢失，也不等于任何场景都永久失去归属。', [('B-BallistaBolt',[[119,148],[185,195]]),('F-Entity',[[1570,1795]]),('F-EntityType',[[507,627]])])
ev('L05','P-BALLISTA','发射与破坏后的原引用','发射将器械bolt字段置空，箭中仍保留原始owner引用。伤害没有检查owner.isRemoved；破坏/拆除只处理当前装填bolt，不能推定会级联移除已发射箭。普通controllerUUID、reloadTicks和bolt引用也不在该器械自有NBT中。', [('B-Ballista',[[29,47],[96,143],[191,245],[276,288],[307,324]]),('B-BallistaBolt',[[119,127]]),('F-Entity',[[3357,3368]])])
ev('L06','P-BALLISTA','并非所有基础tick清理都继承执行','Ballista调用super.tick，但BallistaBolt自有tick没有调用super.tick。该箭自有落地计数超过6000才discard，没有自有飞行TTL；不可把Entity.baseTick中的低于世界清理自动套到该箭上，也不能据此断言整个环境永无其他清理。', [('B-Ballista',[[96,143]]),('B-BallistaBolt',[[69,183]]),('F-Entity',[[421,497],[550,562]]),('F-ServerLevel',[[680,722]])])
ev('L07','P-BALLISTA','普通新生成与读档回调不同','普通ServerLevel.addEntity只在管理器接受后调用onAddedToWorld；准确Forge47.3.0的processPendingLoads却在addEntity(entity,true)之后不检查返回值就调用onAddedToWorld。取消加入/重复UUID是假设条件，不能将这条路径当成已复现故障。', [('F-ServerLevel',[[813,815],[854,866]]),('F-PersistentEntitySectionManager',[[55,105],[256,264]])])
ev('L08','P-BALLISTA','保存与卸载不是磁盘原子性证明','EntityStorage对每个实体调用save，序列化失败会记录错误并遗漏该项，异步store失败也只在所读层记录。管理器PENDING不保存，FRESH先请求加载；LOADED调用store后执行卸载consumer。此处没有读IOWorker的持久化保证或断电恢复。', [('F-EntityStorage',[[1,125]]),('F-EntityPersistentStorage',[[1,16]]),('F-PersistentEntitySectionManager',[[199,248]])])
ev('L09','P-BALLISTA','卸载、销毁与停止跟踪分开','UNLOADED_TO_CHUNK的destroy=false/save=true；DISCARDED的destroy=true/save=false。setRemoved进入管理器回调，移除区段/UUID并停止tick与跟踪，Forge离开世界钩子也被调用。通用链不自动遍历普通owner字段关联的子弹。', [('F-Entity',[[3348,3385],[3543,3566]]),('F-PersistentEntitySectionManager',[[360,455]]),('F-ServerLevel',[[1480,1566]])])
ev('L10','P-BALLISTA','服务端跟踪终止到客户端移除','ServerLevel跟踪结束交给ServerChunkCache/ChunkMap，TrackedEntity移除配对，再由ServerEntity发送RemoveEntities包。发送此包也可能只是观察者离开跟踪范围，不能反推服务器实体被销毁。', [('F-ServerLevel',[[1480,1566]]),('F-ServerChunkCache',[[451,470]]),('F-ChunkMap',[[1144,1188],[1330,1413]]),('F-ServerEntity',[[210,243]])])
ev('L11','P-MULTICHARGE','原生Projectile持久化与查找','Projectile保存Owner UUID、LeftOwner和HasBeenShot；读档清空缓存，getOwner优先使用未removed缓存，否则仅ServerLevel中按UUID查当前可见索引。没有强制加载区块或跨维度寻主；setOwner(null)本身也不会清空已有字段。', [('V-Projectile',[[38,114]]),('V-ServerLevel',[[1065,1087]]),('V-LevelEntityGetterAdapter',[[1,43]]),('V-EntityLookup',[[1,61]]),('V-PersistentEntitySectionManager',[[37,101],[112,132],[188,263],[412,438]])])
ev('L12','P-MULTICHARGE','普通箭没有owner仍可进入hurt','AbstractArrow命中时owner为空会用arrow(this,this)构造伤害源，而非取消伤害。拾取须服务端、落地/无物理、无shake并通过ALLOWED库存接收或CREATIVE_ONLY创造条件；成功才discard。Multicharge的创造/额外多重箭还会显式设拾取权限。', [('V-AbstractArrow',[[299,393],[468,495]]),('M-CrossbowMixin',[[234,290]])])
ev('L13','P-MULTICHARGE','选中的烟火构造不是鞘翅附着','CrossbowMixin使用带shooter、坐标和shotAtAngle=true的构造；该原生构造设置owner，没有设置attachedToEntity。LivingEntity附着构造是另一条路径。Life、LifeTime、FireworksItem、ShotAtAngle随父级归属一起保存。', [('M-CrossbowMixin',[[234,271]]),('V-FireworkRocketEntity',[[24,88],[249,274]])])
ev('L14','P-MULTICHARGE','烟火伤害需要爆炸数据','烟火只有非空Fireworks.Explosions compound列表才得到5+2*n的基础爆炸伤害。范围候选还检查距离与两条视线；实际hurt用fireworks(this,getOwner)，owner为空不是该方法取消伤害的条件。没有爆炸数据仍可寿命结束后退出。', [('V-FireworkRocketEntity',[[91,220]]),('V-DamageSources',[[79,81],[195,217]])])
ev('L15','P-MULTICHARGE','烟火退出与表现事件','服务端实体命中触发explode；方块命中只在hasExplosion时爆炸；超寿命也爆炸。explode依次发事件17、GameEvent、伤害、discard。客户端效果事件与服务端伤害不是同一件事，也不能按弹种额外计案例。', [('V-FireworkRocketEntity',[[91,181]]),('M-CrossbowMixin',[[234,271],[293,337]])])
ev('L16','P-MULTICHARGE','出生包归属是运行时ID','Projectile出生包data填owner实体运行时ID或0；包自身UUID属于弹体而非owner。客户端recreateFromPacket只在当时getEntity(data)存在时setOwner；客户端基础getOwner没有服务端UUID重查路径。实际跟踪顺序/其他Mixin补偿未验证，不能宣称必定不同步。', [('V-Projectile',[[38,55],[198,208]]),('V-ClientboundAddEntityPacket',[[1,145]]),('V-ClientPacketListener',[[443,456]]),('V-ServerEntity',[[227,302]])])
ev('L17','P-MULTICHARGE','客户端移除不是服务器生命终止证明','原生跟踪结束通过ChunkMap/ServerEntity发送RemoveEntities，客户端handler再调用ClientLevel.removeEntity，TransientManager清理区段与索引。玩家离开跟踪距离也能走配对移除，不能据此声称弹体服务器已销毁。', [('V-ServerLevel',[[1446,1516]]),('V-ServerChunkCache',[[445,463]]),('V-ChunkMap',[[1134,1178],[1319,1400]]),('V-ServerEntity',[[205,227]]),('V-ClientPacketListener',[[580,589]]),('V-ClientLevel',[[319,350],[914,949]]),('V-TransientEntitySectionManager',[[1,149]])])
ev('L18','P-MULTICHARGE','父级低于世界清理可达但不是统一飞行TTL','原生Projectile.tick调用super，烟火也调用super；本批补读AbstractArrow.tick开头的super.tick与落地tickDespawn调用。Entity的低于世界清理可达。这不意味着所有弹体在1200tick飞行后消失，箭的1200是历史已读的入地life逻辑。', [('V-Projectile',[[88,99]]),('V-FireworkRocketEntity',[[91,149]]),('V-Entity',[[412,488],[541,553]]),('V-AbstractArrow',[[121,175],[265,271]])], '源码静态基线；本批新增选读原生箭父级tick和落地阈值，仍无实际Fabric合并或运行验证。')
traces=[]
def trace(id,title,assumptions,steps,result,ids):
 traces.append(dict(id=id,title=title,kind='CONDITIONAL_SOURCE_WALKTHROUGH_NOT_EXECUTED',assumptions=assumptions,steps=steps,result=result,evidence=ids,new_reference_credit=0))
trace('T01','单器械装填读档：器械先加入',['两对象都成功加入、所在区段可查询','drawProgress==1、bolt初始null、箭shotEnd=false且AABB确实相交','没有其他重叠候选或外部监听修改'],['新Ballista恢复draw等字段并onAdded；此时没有箭，未连接','箭成功加入后onAdded查询到Ballista','Ballista重新查询已索引箭，设置owner、无重力并归位'],'满足条件时关联可恢复；不是UUID持久关系，也不保证所有载入状态。',['L01','L02','L03','L07'])
trace('T02','单器械装填读档：箭先加入',['与T01相同且单一候选'],['箭先onAdded，没有器械，未连接','器械加入后checkExistingBolt查询箭','赋owner并归位'],'反向顺序也有可行重接路径；不能说任意加载顺序必然失败。',['L01','L02','L03'])
trace('T03','飞行箭保存后独立加载',['自有shotEnd仍false、保存成功且Motion有效','新对象未遇到可关联器械','没有外部注入owner'],['基础NBT恢复运动，自有NBT仅恢复shotEnd','普通owner引用没有恢复','命中查询后owner!=null不成立'],'这条源码路径跳过实体伤害；不能误报速度必然丢失或箭永远无法再关联。',['L01','L04'])
trace('T04','多个重叠器械/箭',['存在多个可查询相交候选，不假定枚举顺序'],['箭onAdded只通知首个器械，即使首个不满足draw/bolt条件也不尝试第二个','器械checkExistingBolt仅挑首个未shotEnd箭','不校验已有owner，也不验证持久双方UUID'],'不能保证原配或最近，具体错配需要可复现场景；这里未运行。',['L02','L03'])
trace('T05','加入取消与加载回调',['外部取消EntityJoinLevelEvent，或存在重复UUID'],['正常fresh add失败后不会onAdded','processPendingLoads没有检查addEntity返回值就onAdded','失败对象能执行回调，但不等于它已在世界查询索引中'],'只能提条件风险；不得宣称失败箭一定被器械收养或已经复现复制。',['L07'])
trace('T06','器械离开与已射箭',['发射成功，器械bolt字段已经置null','器械随后破坏或卸载'],['器械只对当前装填bolt作专有清理','普通owner引用不是乘客/可自动遍历子实体关系','旧箭自有命中不检查owner.isRemoved'],'不能假定自动清理已发射箭，也不能把owner引用仍存在视为归属持久化。',['L05','L06','L09'])
trace('T07','原生弹体加载时owner尚不可查',['Owner UUID已保存但服务器该UUID暂不在可见索引','普通原生基线，没有额外Mixin修改'],['getOwner返回null，未主动加载owner','后续调用仍可按UUID再次查找；checkLeftOwner在owner为空时可变true','普通箭命中有this作为伤害源后备；烟火伤害还取决于Explosions等条件'],'暂时失主不等于自动移除或统一无伤害；与Ballista不能混为一谈。',['L11','L12','L14'])
trace('T08','无/有爆炸数据烟火',['选用Multicharge实际shotAtAngle构造'],['没有Explosions：dealExplosionDamage中f仍0，仍可超寿命explode/discard','有Explosions：f=5+2*n，再经距离/遮挡检查调用hurt','附着livingEntity构造不属于当前发射分支'],'两者共享同一武器家族；不能将烟火视觉爆炸直接当伤害或额外案例。',['L13','L14','L15'])
trace('T09','客户端出生时owner未到达',['出生包data为owner运行时ID','当时客户端实体表找不到该ID','不假定后续外部补偿'],['先创建弹体并recreateFromPacket','当时getEntity(data)==null，没有setOwner','基础客户端getOwner不走ServerLevel UUID查找'],'指出基线恢复缺口；实际网络顺序与合并Mixin尚未验证，不保证线上会触发。',['L16'])
trace('T10','观察者离开跟踪范围',['服务器弹体仍存活，只有该观察者停止跟踪'],['ServerEntity.removePairing发RemoveEntities','客户端移除本地弹体及索引','服务器实体可继续存在并被其他观察者跟踪'],'客户端消失不能单独证明实体服务端生命周期结束。',['L10','L17'])
limits=[
 '本批是两个既有源码家族的归属/生命周期上下文，0新家族、0自行验收信用；102历史证据、25前批消费者和18本批证据不等于独立案例数量。',
 '原生源码来自已有MCP joined/patch缓存与准确Forge47.3.0官方源码补丁；没有重新运行MCP生成。Fabric只核原生1.20.1基线和准确Yarn别名，没有构建实际Mixin合并环境。',
 'Ballista多对象加载顺序、取消加入、穿墙后实体查询及owner最先相交未实机；外部事件监听器未全面核对。',
 '原生网络owner到达顺序、断线/重生/跨维度的全部具体情景未实测；缓存引用存活与按UUID可见查找分别描述。',
 'IOWorker磁盘写入原子性、崩溃恢复没有读取，不以store调用证明可靠落盘。',
 '只有列出的行范围经过阅读；vanilla EntityType已提取但尚未阅读，明确保留未读。',
 '没有模型+PNG艺术参考增量，也没有关闭逐生物100参考或六机巧各1000参考门槛。',
 '没有生产改动、Java/游戏/声音/亮度/焦点/唤醒/共享Jar/发布/新聊天。独立语义验收与跨包装全局去重仍待完成。']
save('ownership-lifecycle-review.json',dict(updated_utc=now,status='BOUNDED_STATIC_REVIEW_READY_FOR_INDEPENDENT_REVIEW',source_registry=sources,evidence=evidence,state_traces=traces,limitations=limits,new_source_families=0,new_accepted_gate_credit=0,global_accepted_totals=None))
mapfile=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/mcp/1.20.1-20230612.114412/joined/downloadClientMappings/client_mappings.txt')
save('namespace-correspondence.json',dict(updated_utc=now,local_official_mapping=str(mapfile),mapping_sha256=sha(mapfile),mapping_selected_lines=[71458,71651],observations=[dict(mojang='net.minecraft.world.entity.projectile.AbstractArrow',obfuscated='byu',yarn='net.minecraft.entity.projectile.PersistentProjectileEntity',intermediary='net/minecraft/class_1665',url='https://maven.fabricmc.net/docs/yarn-1.20.1%2Bbuild.10/net/minecraft/entity/projectile/PersistentProjectileEntity.html',actually_viewed='class header, mapping table and constructor summaries; web output lines0–181, not full1232-linepage'),dict(mojang='net.minecraft.world.entity.projectile.FireworkRocketEntity',obfuscated='bzb',yarn='net.minecraft.entity.projectile.FireworkRocketEntity',intermediary='net/minecraft/class_1671',url='https://maven.fabricmc.net/docs/yarn-1.20.1%2Bbuild.10/net/minecraft/entity/projectile/FireworkRocketEntity.html',actually_viewed='class header, mapping table and constructors; web output lines0–144, not full575-linepage')],qualification='仅用准确MC1.20.1/Yarnbuild10对应原生类名；JavaDoc不是实现体、Mixin合并产物或运行验证。',new_reference_credit=0))
save('proposal-supplement.json',dict(updated_utc=now,base='../batch-08/semantic-review-proposals.json',status='EXTENSION_ONLY_NO_SELF_ACCEPTANCE',proposals=[dict(id='P-BALLISTA',new_evidence=[e['id'] for e in evidence if e['family']=='P-BALLISTA'],closed_static_gaps=['基础Entity NBT与非Projectile raw owner差别','装填箭重叠重接与双向加入回调条件','准确Forge加载/卸载/移除与跟踪消费者'],remaining=['多对象/实际读档顺序与外部事件的运行复现','碰撞边界真实场景与完整PNG/游戏表现','独立语义验收和全局包装去重']),dict(id='P-MULTICHARGE',new_evidence=[e['id'] for e in evidence if e['family']=='P-MULTICHARGE'],closed_static_gaps=['原生烟火实际选用构造、伤害条件、保存和退出','原生Projectile Owner UUID/缓存/当前世界索引','原生出生包归属ID与客户端移除链'],remaining=['实际Fabric Mixin合并、网络跟踪顺序与客户端行为','混弹/取消续装/HUD等原有运行断点','独立语义验收与全局同源去重'])],new_source_studies=0,new_accepted_gate_credit=0,global_accepted_totals=None,creature_art_reference_credit=0))
# A human-readable small review packet, not a production preview or game screenshot.
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>第九批：归属与生命周期</title><style>body{font:16px/1.7 system-ui;background:#111923;color:#e7edf5;max-width:1100px;margin:40px auto;padding:0 24px}a{color:#9bcef4}h1{font-size:27px}article,details{background:#1b2837;padding:18px;margin:16px 0;border-radius:12px}small{color:#b9c9d8}code{overflow-wrap:anywhere}li{margin:8px 0}</style><h1>弩炮／多重装填弩：归属与生命周期补读</h1><p>源码核查；不是模型成果、不是游戏截图。本批补两个既有家族，新增独立参考与验收信用均为0。</p><p><a href="ownership-lifecycle-review.json">证据与条件推演</a> · <a href="native-source-manifest.json">新增原生源码范围</a> · <a href="existing-source-review.json">历史源码增量选读</a> · <a href="namespace-correspondence.json">Yarn准确版本对应</a> · <a href="proposal-supplement.json">待审提案补充</a> · <a href="../batch-08/index.html">上批原始提案</a></p>']
for family,title in [('P-BALLISTA','弩炮：装填重接不等于持久归属'),('P-MULTICHARGE','原生箭／烟火：持久Owner与实际伤害分开')]:
 parts.append('<h2>'+title+'</h2>')
 for e in evidence:
  if e['family']!=family:continue
  links=[]
  for x in e['support']:
   s=next(v for v in sources if v['id']==x['source'])
   links.append('<a href="'+html.escape(s['local'],quote=True)+'">'+html.escape(s['id'])+'</a> '+html.escape(str(x['ranges'])))
  parts.append('<article><b>'+e['id']+' '+html.escape(e['title'])+'</b><p>'+html.escape(e['claim'])+'</p><small>'+'；'.join(links)+'</small></article>')
parts.append('<h2>条件推演：均未执行</h2>')
for t in traces:
 parts.append('<details><summary>'+t['id']+' '+html.escape(t['title'])+'</summary><p>前提：'+html.escape('；'.join(t['assumptions']))+'</p><ol>'+''.join('<li>'+html.escape(v)+'</li>' for v in t['steps'])+'</ol><p>'+html.escape(t['result'])+'</p></details>')
parts.append('<h2>边界与未完成</h2><ul>'+''.join('<li>'+html.escape(v)+'</li>' for v in limits)+'</ul><p><a href="local-verification.json">本地文件校验</a> · <a href="progress.json">进度</a></p></html>')
(B/'index.html').write_text('\n'.join(parts)+'\n')
p=json.loads((B/'progress.json').read_text());p.update(updated_utc=now,status='BOUNDED_SUBRANGE_READY_FOR_INDEPENDENT_REVIEW',evidence_records=len(evidence),conditional_source_traces=len(traces),extracted_source_variants=len(m['files']),reviewed_new_source_variants=sum(bool(f['reviewed_ranges']) for f in m['files']),unread_new_source_variants=[f['reading_view'] for f in m['files'] if not f['reviewed_ranges']],existing_source_selected_reviews=len(existing),next=['独立审阅本批条件结论，不以证据条数计参考信用。','后续仍需实际Fabric合并、运行复现与全局语义去重；不擅自解锁生产。'],report='index.html');save('progress.json',p)
root=json.loads((R/'progress.json').read_text());old=root.get('this_batch',{})
if old.get('id')!='batch-09' and not any(x.get('id')==old.get('id') for x in root.get('previous_batches',[])):
 root.setdefault('previous_batches',[]).append(dict(old,report=old.get('id','batch-08')+'/index.html'))
root.update(updated_utc=now,status='RESEARCH_SUBRANGE_READY_PENDING_INDEPENDENT_REVIEW',latest_batch='batch-09',this_batch=dict(id='batch-09',source_studies=0,existing_family_context_extensions=2,evidence_records=len(evidence),new_accepted_gate_credit=0,count_note='既有Ballista/Multicharge归属生命周期消费者；不新拆家族、不自验收。'))
root['next']=['第九批归属/生命周期补读可独立审阅；18条证据和10条条件推演不是18或10个参考。','Ballista读档重接与owner缺失、原生烟火伤害/退出已补源码；运行场景和外部消费者仍待验证。','Fabric实际合并/客户端顺序、既有Ars/IE/Grapple上下文断点继续保留。','两项直接提案仍待全局语义去重及独立验收；逐生物100个模型+PNG和六机巧1000门槛未关闭。','已认可资源不动；没有确认新的未制作注册生物，不能用本次源码补读冒充美术参考。']
root['continuation_window'].update(status='BOUNDED_SUBRANGE_SAVED_FOR_REVIEW',last_saved_utc=now,report='batch-09/index.html',full_three_hours_claimed=False)
(R/'progress.json').write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n')
save('checkpoint-20261031.json',dict(saved_utc=now,scope='batch09 native ownership/lifecycle only',window_start=p['window_start'],deadline=p['deadline'],early_bounded_handoff=True,full_three_hours_claimed=False,accepted_credit=0,independent_review='PENDING',unfinished=limits[1:],production_changed=False,java_game_started=False,published=False))
print(json.dumps(dict(evidence=len(evidence),conditional_traces=len(traces),source_variants=len(m['files']),selected_or_fully_read=sum(bool(f['reviewed_ranges']) for f in m['files']),existing_reviewed=len(existing),patch_hunks=sum(len(f.get('patch_hunks',[])) for f in m['files'])),ensure_ascii=False))
