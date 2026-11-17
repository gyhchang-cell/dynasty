"""Primary semantic decisions after full excerpt reading and native-context supplementation.
Not an automatic helper promotion. Helper receipt remains credit zero.
"""
from ledger import B,R,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';batch=json.loads((D/'batch-001.json').read_text());rows={int(x['id'].split('-')[-1]):x for x in batch['rows']}
manifest=json.loads((D/'source-manifest-001.json').read_text())['sources'];by={x['repo'].replace('/','__')+'/'+x['path']:x for x in manifest}
# Copy only hash-verified immutable source, never overwrite another version.
for src in manifest:
 p=R/src['local'];data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==src['sha256']
 dst=B/'sources'/src['repo'].replace('/','__')/src['path'];dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==data
 else:dst.write_bytes(data)
 metaPath=dst.parents[len(dst.relative_to(B/'sources'/src['repo'].replace('/','__')).parts)-1]/'source.json'
 meta=json.loads(metaPath.read_text());assert meta['commit']==src['commit']
 if not any(x['path']==src['path'] for x in meta['files']):meta['files'].append({'path':src['path'],'sha256':src['sha256'],'git_blob_sha1':src['computed_git_blob_sha1'],'proof':src['proof']});metaPath.write_text(json.dumps(meta,indent=2)+'\n')
# One decision per helper row. Explicit merged/rejected rows never gain implicit credit.
decisions={
1:('accept','友伤最终取消与SpellDamageEvent取消明确区分；并入04原生incoming归属保护，同一归属家族合计1。'),
2:('merge_existing','与goety-no-knockback-single-use-native-event-stamp同一单次时间窗消费策略；UUID地图/清旧项作为支持，不另计。'),
3:('accept','Post伤害附加冻结的最终canFreeze门与伤害结果独立；非hurt=false推断。'),
4:('merge_batch','合并01原生召唤归属保护；直接源优先与UUID比较保留为对照。'),
5:('accept','只计冰墓重定向与Fireward来源保护家族，排除整方法内既计Evasion/Shroud；取消后仍可能墓体受伤。'),
6:('pending','债务入账/移除/心跳方法已读，暂缺SyncedSpellData实际积累与客户端同步完整上下文；0。'),
7:('merge_existing','Goety Telekinesis自述移植Irons，握持目标物理控制已计；施法者阻力误用作为版本差异支持。'),
8:('accept','Boss系数0.5仅软抗性；持续吸引资格与到期爆散未重验的生命周期差异真实独立。'),
9:('accept','最终Root创建前CANT_ROOT及实际#c:bosses资源，资格/绑定/远距释放链完整；不是状态药水换色。'),
10:('accept','服务端原生hurt的随机方向parry有明确false、100tick冷却及S2C动画/声，已补完整接口、包、接收及RawAnimation入口。'),
11:('accept','原生knockback与实体push的阶段资格不同；只计合并策略，不据此声称直接motion也免疫。'),
12:('merge_existing','出场phase状态无敌与既有cat-scripted-animation-phase-invulnerability-family同族，不按pose名/实体名换壳计数。'),
13:('support','定时/受击引爆假人主要是攻击生产；hurt=false为客户端/原生无敌帧，未额外形成独立拒控或免疫反馈，0。'),
14:('support','熔岩环境来源拒伤与距离减伤支持，不将单个伤害来源常量变化另算一处。'),
15:('support','自身药水/固定列表资格为既有来源保护和状态资格策略对照；常量表扩张不独立计。'),
16:('accept','只计共享父盾hurtThisTick对所有子盾同tick命中的合并消费策略；盾资源损失和hurt=false仍区分，非重复计通用盾吸收。'),
17:('accept','防御期近距非穿甲反伤在本体最终拒伤之前发生；阶段生命阈值还在父hurt后修正，非纯phase常量换壳。'),
18:('support','Holder instanceof和局部重赋值不足以证明真实拒控，保留0且不写成可靠实现。'),
19:('accept','倒带Boss黑名单影响申请及历史采集，原生数据生成将Boss纳入；重复倒带不是免疫。'),
20:('accept','两方传送各自可取消且可能只移动一方，独立于单目标banish；不假称原子交换。'),
21:('pending','实体warp/资格已读；PortalTile、PacketWarpPosition接收尚未全文补齐，0，不按重载拆数。'),
22:('accept','Snare真实addEffect被拒仍直接motion归零的独立控制后果；补全IPotionEffect所有包装，包装0。'),
23:('accept','最终knockback按目标阻力乘算且strength>0才写运动；与下限0.2/0.3仍强制移动的策略有实质区别。'),
24:('accept','可变source/amount的Pre拒绝、原生hurt布尔以及Post发布次序是独立的游戏伤害结果生产点；不把Post数额当HP差。'),
25:('accept','Dispel真正可取消Pre及效果清除后存活判定/目标回调/Post生命周期；deny标签Holder比较疑点保留，不声称标签生效。'),
26:('pending','ColdSnap缺同名spawnIce另一重载的完整原生流程及碎片链边界，暂0。'),
27:('merge_batch','Flare与ColdSnap同骨架/元素换壳，0；26未晋级也不因此给27计数。'),
28:('accept','延时药水/即刻直接下拉两条控制入口，玩家近地面与非创造flight限制不同；补完整GravityEffect，合并1。'),
29:('accept','独立倒带控制终止/换维度/登出/停服恢复；已补EventQueue、ITimedEvent、RewindEntityData全文，明确stop/监听未统一收尾风险。'),
30:('accept','原生目标预选反馈、multipart父目标映射、目标警告，与最终Root/telekinesis控制结果不同；只计反馈生产，不把底层ray包装再算。')}
extra={}
ir='iron431/irons-spells-n-spellbooks';ar='baileyholl/Ars-Nouveau';ip='src/main/java/io/redspace/ironsspellbooks/';ap='src/main/java/com/hollingsworth/arsnouveau/'
def whole(repo,p):return(p,1,len((B/'sources'/repo.replace('/','__')/p).read_text().splitlines()))
fire=ip+'entity/mobs/wizards/fire_boss/FireBossEntity.java'
extra[1]=[(ir,ip+'damage/DamageSources.java',114,163)]
extra[8]=[(ir,ip+'api/util/Utils.java',807,813)]
extra[10]=[(ir,fire,424,440),(ir,fire,486,563),(ir,fire,942,949)]+[(ir,*whole(ir,ip+p)) for p in ['entity/mobs/IAnimatedAttacker.java','network/SyncAnimationPacket.java','setup/PayloadHandler.java']]
extra[11]=[(ir,fire,424,435),(ir,fire,506,563)]
extra[17]=[(ar,ap+'common/entity/WildenChimera.java',658,680)]
extra[19]=[(ar,*whole(ar,ap+'common/event/timed/RewindEvent.java'))]
extra[22]=[(ar,*whole(ar,ap+'api/spell/IPotionEffect.java'))]
extra[28]=[(ar,*whole(ar,ap+'common/potions/GravityEffect.java')),(ar,*whole(ar,ap+'api/spell/IPotionEffect.java'))]
extra[29]=[(ar,*whole(ar,ap+p)) for p in ['api/event/EventQueue.java','api/event/ITimedEvent.java','common/spell/rewind/RewindEntityData.java']]
promoted=[];review=[]
for n,row in rows.items():
 status,reason=decisions[n];entry={'helper_id':row['id'],'decision':status,'reason':reason,'research_credit':0}
 if status=='accept':
  refs=[];repo=None
  for ref in row['source_refs']:
   s=by[ref['source_key']];repo=s['repo'] if repo is None else repo;assert repo==s['repo']
   p=B/'sources'/s['repo'].replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['file_sha256'];refs.append((s['path'],*ref['lines']))
  for r,p,a,b in extra.get(n,[]):assert r==repo;refs.append((p,a,b))
  key=row['semantic_dedup_key']
  record(key,repo,refs,row['native_chain'],row['observation']+' 主岗复核：'+reason,row['application'],row['limits']+' 静态源码研究，不证明画面/声音或TCP。普通阴阳体质不要求灰字；守卫旧账0自动转入。','helper_reviewed_native_immune_feedback')
  entry.update({'research_credit':1,'master_id':key});promoted.append(key)
 review.append(entry)
(O/'HERSCHEL-001-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-001.json').read_bytes()).hexdigest(),'rows_reviewed':30,'promoted':len(promoted),'credit_not_inherited_from_guard':True,'decisions':review,'integrity_is_not_semantics':True,'ordinary_constitution_gray_text_required':False},ensure_ascii=False,indent=2)+'\n')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'herschel-001-primary-reviewed','credited_chains':promoted,'rationale':'30个建议逐项全文复核，18晋级；友伤生产/原生incoming归属合并，击退时间戳消费及移植telekinesis/纯phase/元素换壳不重复；3项链不完整待补，不使用守卫旧账。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
