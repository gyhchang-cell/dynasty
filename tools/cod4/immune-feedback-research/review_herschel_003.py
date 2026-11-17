"""Primary semantic review of helper batch003; run once, no automatic helper credit."""
from ledger import B,R,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';b=json.loads((D/'batch-003.json').read_text());old=json.loads((D/'batch-002.json').read_text())
manifest={}
for n in ('001','002','003'):
 for s in json.loads((D/f'source-manifest-{n}.json').read_text())['sources']:manifest[s['repo'].replace('/','__')+'/'+s['path']]=s
for s in json.loads((D/'source-manifest-003.json').read_text())['sources']:
 p=B/'sources'/s['repo'].replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 assert json.loads((B/'sources'/s['repo'].replace('/','__')/'source.json').read_text())['commit']==s['commit']
decisions={
1:('accept','原生控制分配/弹种拒绝/目标绑定和停止链完整，合计1；目标UUID和弹整数ID是不同校验对象，客户端死亡stopTracking的server-only条件导致本地分支不清；未缓存默认tag，不能声称某实际弹种必拒。'),
2:('accept','以可破坏控制载体的实际拉回/共享10tick受击窗/断链释放及预FX次序合计1；不是另计已入账multipart每tick盾窗。完整类显示victim server按UUID重取、client仅spawn整数ID当次查找；不按8part计数。'),
3:('accept','原生Wall每目标WeakReference+时间戳的持续尝试窗口，过期删除后仍present导致本次未重打戳；区别portal进出CD与单次链式目标列表去重。所有包装/客户端Emitter支持0额外。'),
4:('accept','原生失败理由→S2C→真实聊天历史按签名替换；独立于SpellEngine屏幕HUD单槽，是聊天签名/频道隔离策略实现。messageChannelId完全未消费，不能声称按频道/目标分流；不是服务端节流。'),
5:('accept','拒伤主动幂等触发复活计时并替换为新Boss实体，区别Frostmaw原实体苏醒；整条阶段转移/反馈只计1，不据hurt=false宣称无后果，不据bypass true宣称扣血。'),
6:('accept','原生维度传送拒绝与调用方先发FX/忽略cancel返回的实际交互链；区别Portal入口冷却和Ars双目标非原子交换，合计1。拒绝不证明成功外观自动终止。'),
7:('merge_existing','真实SummonUtil消费者已接活，但玩家来源/bypass白名单作为已有真实玩家/来源资格拒伤家族支持；仅换召唤物类型不加数，保留无owner条件观察。'),
8:('support','Boss tag标攻击者；先解冻后父hurt不保证实际受伤。静态来源模板支持0。'),
9:('support','FALL常量免疫、projectile减伤0.75、幼龄拆窒息块并非新免控/回执链，支持0。'),
10:('pending','接收/注册真实，固定源码内实际CastErrorPacket发送生产点尚未找到；孤立显示器不计。')}
ir='iron431/irons-spells-n-spellbooks';ar='baileyholl/Ars-Nouveau'
ip='src/main/java/io/redspace/ironsspellbooks/';ap='src/main/java/com/hollingsworth/arsnouveau/'
def whole(repo,p):return p,1,len((B/'sources'/repo.replace('/','__')/p).read_text().splitlines())
extra={1:[whole(ir,ip+'effect/guiding_bolt/GuidingBoltManager.java')],2:[whole(ir,ip+'entity/spells/ender_chain/EnderChain.java')],3:[whole(ar,ap+'common/entity/EntityWallSpell.java')]}
review=[];promoted=[]
def add(row,reason,supp=(),ext=()):
 refs=[];repo=None
 for ref in list(row['source_refs'])+list(supp):
  s=manifest[ref['source_key']];repo=s['repo'] if repo is None else repo;assert repo==s['repo'];refs.append((s['path'],*ref['lines']))
 refs.extend(ext)
 record(row['semantic_dedup_key'],repo,refs,row['native_chain'],row['observation']+' 主岗：'+reason,row['application'],row['limits']+' 主岗全文复核固定版本；静态不证明实际观感/音量/TCP/Boss覆盖；普通体质不要求灰字；守卫旧账0转入。','helper_reviewed_native_immune_feedback')
 promoted.append(row['semantic_dedup_key']);return row['semantic_dedup_key']
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);decision,reason=decisions[n];r={'helper_id':row['id'],'decision':decision,'reason':reason,'research_credit':0}
 if decision=='accept':r.update(master_id=add(row,reason,ext=extra.get(n,())),research_credit=1)
 review.append(r)
by_old={r['id']:r for r in old['rows']}
for s in b['support_for_batch002']:
 id=s['support_for_batch002']
 if id.endswith('-01'):
  review.append({'helper_id':id,'decision':'still_pending','research_credit':0,'reason':'Protection.register实现全文补足，但仍无游戏效果注册消费者；不把公开map/API能力当实际接活。'});continue
 row=by_old[id]
 reason={
 'herschel-002-12':'补齐真实注册→实例化/回绑→BlockEntityTicker→source/backoff/isOff/relay→tryTick始末门→Disintegration.tick；实际DISCARD绕过hurt/死亡，不自动受Boss伤害免疫保护。默认DISINTEGRATION_BLACKLIST数据生成为空；客户端装饰光不证明目标被拒。来源成本仅经验产出时置needsSource，不夸大为每次删除均耗。',
 'herschel-002-21':'补齐装备tag返回引用→修改active→PerkMap新map/ArmorHolder新holder→ItemStack.set写回，persistent CODEC含perkTags；睡眠重装全部世界Player，对tag为空仍发active消息。getHolderForPerk实际遍历后匹配覆盖，不按maxCount选择最高。区别永久消耗生命符，恢复active是再装填机制，不是Boss免控。'}[id]
 ext=[]
 if id.endswith('-12'):ext=[whole(ar,ap+'common/block/ITickable.java'),whole(ar,ap+'common/block/ITickableBlock.java')]
 key=add(row,reason,s['source_refs'],ext);review.append({'helper_id':id,'decision':'accept_after_supplement','research_credit':1,'master_id':key,'reason':reason,'supplement_method_credit':0})
(O/'HERSCHEL-003-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-003.json').read_bytes()).hexdigest(),'rows_reviewed':10,'pending002_completed':2,'promoted':len(promoted),'integrity_is_not_semantics':True,'guard_credit_transferred':0,'decisions':review},ensure_ascii=False,indent=2)+'\n')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'herschel-003-primary-reviewed','credited_chains':promoted,'rationale':'6条独立新链+2条002补证；召唤来源白名单合并既有资格家族；Boss攻击者tag/FALL常量0，Protection缺register消费者/CastError缺producer仍0。没有按方法/实体/包装增加信用。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
