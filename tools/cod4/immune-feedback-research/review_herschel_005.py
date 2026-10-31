"""Final main review of helper005; independent sites, not one credit per method."""
from ledger import B,R,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';b=json.loads((D/'batch-005.json').read_text());manifest={s['repo'].replace('/','__')+'/'+s['path']:s for s in json.loads((D/'source-manifest-005.json').read_text())['sources']}
ip='src/main/java/io/redspace/ironsspellbooks/';sp='common/src/main/java/net/spell_engine/'
def whole(repo,p):return p,1,len((B/'sources'/repo.replace('/','__')/p).read_text().splitlines())
ir='iron431/irons-spells-n-spellbooks';sr='ZsoltMolnarrr/SpellEngine'
extra={1:[whole(ir,ip+'spells/ender/CounterspellSpell.java'),(ip+'api/spells/AbstractSpell.java',305,333)],2:[whole(ir,ip+'network/casting/OnCastFinishedPacket.java'),whole(ir,ip+'network/casting/CancelCastPacket.java')],3:[whole(sr,sp+'utils/SoundHelper.java')],5:[(sp+'mixin/effect/LivingEntityStatusEffectSync.java',34,96),whole(sr,sp+'mixin/client/render/LivingEntityModelFxRendererMixin.java')],6:[whole(sr,sp+'entity/SpellModelEffect.java'),whole(sr,sp+'client/render/SpellModelEffectRenderer.java')],7:[(sp+'entity/SpellCloud.java',27,101),(sp+'entity/SpellCloud.java',274,386),whole(sr,sp+'utils/SoundHelper.java')]}
reasons={1:'实际busy自有召唤物拒绝反制移除，却仍清魔法状态，与owner友伤来源白名单不同；事件取消扩展点没实际监听故不独立计。光束原生发出不证明取消成功。',2:'原生反制→明确cancelled/UUID结束回执→本地施法状态和远端动画清退，合计1；完整packet构造/codec/处理已读。UUID仅隔离部分状态，声音按资源ID全局stop；不把CastError孤立receiver混入。',3:'一次性原生combat FX坐标快照解决发出源本tick移除竞态，独立于实体附着/持续beam。转换在execute前抓旧world，perform用届时world，缺维度/代际；COORDINATE仍把查出的entity交factory，不能说绝无实体依赖。',4:'跨目标范围结果赋值而非OR，最后目标决定云预算回调，且AOE声/粒子/模型独立发出，是实际聚合/消费边界；共享performImpact的已有Boss门不重记，success本身也不保证原生HP/效果接纳。',5:'附着持有者按worldTime绝对期清理整个同步JSON表，renderer按entity当前位置跟随及第一人称焦点隐藏；服务器过期前客户端取模可循环，append没上限/去重。与独立实体不同持有者/时钟/同步链，计1。',6:'独立反馈实体是原生age/TTL/discard与NBT字段恢复，区别05目标内列表/worldTime；load未回写tracker，字段恢复不能等于客户端显示恢复。shouldRender true不等于无限跟踪。模型几何算法0。',7:'实际Cloud ACTIVE成功循环预算/三阶段幂等winddown控制和反馈合计1，区别已有Wall逐目标窗口和本批AOE聚合；interval=0/数据缺失/owner预算不持久化缺口保留，不按音粒子/变换/阶段拆计。',8:'support0：同已入账链式目标历史作用域家族；Entity查Set<Integer>静态类型错配和子弹copy历史范围作边界，不直接推定实际重击。'}
keys=[];review=[]
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);reason=reasons[n];rr={'helper_id':row['id'],'decision':'accept' if n<8 else 'support','reason':reason,'research_credit':0}
 if n<8:
  refs=[];repo=None
  for ref in row['source_refs']:
   s=manifest[ref['source_key']];repo=repo or s['repo'];assert repo==s['repo'];p=B/'sources'/repo.replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'];refs.append((s['path'],*ref['lines']))
  refs.extend(extra.get(n,[]));record(row['semantic_dedup_key'],repo,list(dict.fromkeys(refs)),row['native_chain'],row['observation']+' 主岗：'+reason,row['application'],row['limits']+' 主岗已逐项读取完整方法/原生调用上下文；005Java来源blob核验，common注册资源只有固定commit完整web观察，原始资源TLS失败后停止请求，未宣称raw资源hash或Mixin运行通过。纯渲染数学/包装0，无游戏/TCP/观感验收；普通阴阳无灰字，守卫旧账0。','native_combat_feedback_target_result_and_lifecycle');keys.append(row['semantic_dedup_key']);rr.update(master_id=row['semantic_dedup_key'],research_credit=1)
 review.append(rr)
(O/'HERSCHEL-005-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-005.json').read_bytes()).hexdigest(),'rows_reviewed':8,'promoted':len(keys),'registration_supplement_credit':0,'guard_credit_transferred':0,'decisions':review},ensure_ascii=False,indent=2)+'\n')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'herschel-005-primary-reviewed','credited_chains':keys,'rationale':'7独立游戏职责：busy自有反制门；cancelled回执清退；detached坐标FX；AOE聚合结果；附着worldTime表；独立age实体；cloud三阶段预算反馈。各方法/平台/几何0额外，弹历史并已有家族0，注册补证0。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
