"""Curated primary decisions after full batch excerpts and local native context reading.
Not automatic promotion, and never imports guard credit. Run once.
"""
from ledger import B,R,O,record,verify,attach_auxiliary
import json,hashlib
D=O/'helpers/herschel-immune'
b=json.loads((D/'batch-002.json').read_text());old=json.loads((D/'batch-001.json').read_text())
manifest={}
for n in ('001','002'):
 for s in json.loads((D/f'source-manifest-{n}.json').read_text())['sources']:manifest[s['repo'].replace('/','__')+'/'+s['path']]=s
# All sources copied in the preceding read-only integrity/import phase.
for s in manifest.values():
 p=B/'sources'/s['repo'].replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 assert json.loads((B/'sources'/s['repo'].replace('/','__')/'source.json').read_text())['commit']==s['commit']
decisions={
1:('pending','保护charge分支和原生Player isInvulnerable hook已全文观察，但固定本地样本未找到Protection.register实际效果注册消费者；保留API能力支持0，不假称已接活某游戏护盾。'),
2:('accept','原生effectsChanged重建动作权限缓存，按交集与最大ordinal原因聚合；聚合语义独立于下一项最终输入/动作取消，不按权限常量拆数。未验证具体外部效果注册样本。'),
3:('accept','原生jump/isImmobile/active item/player attack及客户端输入实际取消统一合计1；clearActiveItem有实际后果，不把查询包装或平台重复计数。'),
4:('accept','原生玩家输入拒绝直接生产本地化HUD错误；castAttempt有一次按住防抖，actionImpaired不受该旗标保护，不能混称所有提示均防刷。'),
5:('accept','独立消息单槽替换/原生client tick倒计时/松开use复位/淡出绘制链补齐；它是屏幕HUD，不是目标锚定世界文字，且无换世界显式清空。'),
6:('accept','每玩家对象预测生命周期，在服务端未确认20tick或确认后结束时清预测，和最终拒控生产/提示各自不同；只计拒绝后的客户端收敛，不认定服务端安全校验通过。'),
7:('support','客户端目标流快照去重只表达瞄准状态，不是命中/拒控/反馈回执节流，间接协议支持0。'),
8:('support','原生isAiDisabled在受限时返回false，与阻止AI的宣称相反；保留反例0。'),
9:('accept','气泡目标资格与dismount UUID重入排除；原生startRiding后实际检查乘客，完整类已读；与Root标签只是不同枚举不重复，实际绑定确认与再入规则是区别。'),
10:('accept','独立server pop幂等同步位+声音、寿命/5tick销毁；保留popping后tick捕获未检查HAS_POPPED的漏洞，不把tryCapturing守卫泛化到所有入口。'),
11:('accept','实际注册AttackEntityEvent取消/重定向及伤害Pre加算、移除时同步pop的生产次序；plain hasPopped未与synced HAS_POPPED统一，不能声称后续伤害只处理一次。'),
12:('pending','直接DISCARD绕过hurt的仪式候选已读，但尚缺本版仪式原生调度/黑名单实际默认覆盖链；0，不把伤害旁路当Boss免控。'),
13:('accept','原生hurt随机拒伤与侧闪安全落点链；碰撞回退原位仍返回false，和既有Evasion/Shroud的成功位置/消耗策略有实际区别；不按召唤武器名计数。'),
14:('merge_existing','召唤武器owner/source友伤资格复用已计召唤归属策略，父类包装不另计。'),
15:('support','bypass-only hurt与既有通用无敌来源排除同族；AntiMagic discard尚缺真实调用生产，不能为两个未独立接活点拼出新credit。'),
16:('accept','原生portal tick以portal UUID+entity UUID双键维护10tick窗口，在停留时延长；先扣目标门户CD再检查目的地可能无效，已补完整Manager/PortalData。只计游戏传送防反复控制策略。'),
17:('accept','与固定冷却不同的每实体20tick循环计数>5后终止门户；owner会受致死惩罚，非滑动窗口且跨维未同样计；只借鉴回执风暴终止边界，绝不采纳杀死目标。'),
18:('accept','Cleanse按真实Holder标签保留受保护效果，治愈资格后即使未移除任何效果仍有粒子；区别Ars可取消Pre及其标签比较问题，不凭粒子声称成功驱散。'),
19:('accept','合并20为Bounce一组：原生Fall取消/下一tick恢复Y及Wall Post置零反冲，事件时序与物理反馈各不同但同状态免伤家族只计1。已读EventQueue，不按damage source常量拆数。'),
20:('merge_batch','合并19 Bounce：墙伤置零与反冲作为完整物理回执支持，不另以另一来源常量计数。'),
21:('pending','原生死亡取消+装备active消耗/睡觉重装候选；尚缺本版perk holder tag写回与消息桥完整语义，暂0。'),
22:('support','地面前置与伤害成功后粒子和ColdSnap同模板；新前置常量不计。'),
23:('accept','实际注册SpellPreResolveEvent取消后重新归属Breeze并定时反射；补全SpellResolver.resume的Pre取消早退/EffectPre取消继续边界，是真实效果拒绝点而非hurt=false猜测。')}
se='ZsoltMolnarrr/SpellEngine';ir='iron431/irons-spells-n-spellbooks';ar='baileyholl/Ars-Nouveau'
sp='common/src/main/java/net/spell_engine/';ip='src/main/java/io/redspace/ironsspellbooks/';ap='src/main/java/com/hollingsworth/arsnouveau/'
def whole(repo,p):return (p,1,len((B/'sources'/repo.replace('/','__')/p).read_text().splitlines()))
extra={
5:[whole(se,sp+'mixin/client/render/MinecraftClientMixin.java'),(sp+'client/gui/HudRenderHelper.java',40,139),(sp+'client/gui/HudRenderHelper.java',455,493)],
6:[whole(se,sp+'client/casting/ClientCastController.java')],
9:[whole(ar,ap+'common/entity/BubbleEntity.java')],
10:[whole(ar,ap+'common/entity/BubbleEntity.java')],
16:[whole(ir,ip+'capabilities/magic/PortalManager.java'),whole(ir,ip+'entity/spells/portal/PortalData.java')],
17:[whole(ir,ip+'damage/PortalDamageSource.java')],
19:[]}
# Avoid hard-coded source tail length on the reviewed complete error-widget methods.
extra[5][-1]=(sp+'client/gui/HudRenderHelper.java',455,len((B/'sources'/se.replace('/','__')/(sp+'client/gui/HudRenderHelper.java')).read_text().splitlines()))
by_old={int(r['id'].split('-')[-1]):r for r in old['rows']}
review=[];promoted=[]
def add(row,reason,refs_extra=(),supp=()):
 refs=[];repo=None
 for ref in list(row['source_refs'])+list(supp):
  s=manifest[ref['source_key']];repo=s['repo'] if repo is None else repo;assert repo==s['repo']
  refs.append((s['path'],*ref['lines']))
 refs.extend(refs_extra)
 existing=next((r for r in json.loads((O/'reviewed.json').read_text()) if r['id']==row['semantic_dedup_key']),None)
 if existing is not None:
  assert existing['repo']==repo and existing['concrete_observation']==row['observation']+' 主岗：'+reason
  assert [(r['source_path'],*r['lines']) for r in existing['source_refs']]==refs
 else:record(row['semantic_dedup_key'],repo,refs,row['native_chain'],row['observation']+' 主岗：'+reason,row['application'],row['limits']+' 仅静态源码；未证明画面、音量、两端或Boss覆盖。普通阴阳体质不要求灰字。守卫旧账0转入。','helper_reviewed_native_immune_feedback')
 promoted.append(row['semantic_dedup_key']);return row['semantic_dedup_key']
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);decision,reason=decisions[n];r={'helper_id':row['id'],'decision':decision,'reason':reason,'research_credit':0}
 if decision=='accept':
  more=[]
  if n==19:more=b['rows'][19]['source_refs']
  r.update(master_id=add(row,reason,extra.get(n,()),more),research_credit=1)
 review.append(r)
# Previously pending chains now complete with batch002 supplementation, not 35 new credits.
for support in b['support_for_batch001']:
 n=int(support['support_for_batch001'].split('-')[-1]);row=by_old[n]
 reason={6:'延迟伤害债务非免疫：Pre置0后同步float债务，客户端心跳按债务/HP变频；移除结算伤害或spawn期kill，归零再sync。Player整数ID表、magic mob类型校验不同，无UUID/世界epoch；含NBT不等于死亡保留。',21:'补PortalTile同维位置包/区块跟踪+乘客原生包以及跨维DimensionTransition；事件取消在FX前，但Ender事件修改目标坐标未采用，onResolve无卷轴的施法者直传支路不走同一Ender资格，不泛称所有Blink均可拒。',26:'补完整spawnIce两个重载/物理碎片tick与碰撞/落地：主伤害失败仍有碎片，落地AOE减速不依赖hurt成功；保持Flare/Windshear同模板0，不能把主攻击拒伤当全部后效免疫。'}[n]
 refs=[]
 if n==21:refs=[whole(ar,ap+'common/spell/effect/EffectBlink.java')]
 key=add(row,reason,refs,support['source_refs']);review.append({'helper_id':support['support_for_batch001'],'decision':'accept_after_supplement','research_credit':1,'master_id':key,'reason':reason,'supplement_methods_credit':0})
(O/'HERSCHEL-002-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-002.json').read_bytes()).hexdigest(),'rows_reviewed':23,'pending001_completed':3,'promoted':len(promoted),'integrity_is_not_semantics':True,'guard_credit_transferred':0,'decisions':review},ensure_ascii=False,indent=2)+'\n')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'herschel-002-primary-reviewed','credited_chains':promoted,'rationale':'23建议逐条复核，14条独立生产/回执/生命周期晋级，另3条补齐001待定；Bounce两来源合并，aimstream、owner包装、Mob AI反例、未接活Protection注册/仪式调度/AntiMagic/装备tag支持仍0。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
verify()
