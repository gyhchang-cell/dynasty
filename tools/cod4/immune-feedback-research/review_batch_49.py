"""Two distinct native Goety denial producers with actual state and replay context."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,refs,c,o,l):
 for f,a,z in refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines()),(f,a,z)
 record(k,r,refs,c,o,l,'固定02adbe7491767210f63857fa763a6f1de1262cbd；完整关键方法和原生native事件/实际注册/状态生产已读，上游原生实体事件、渲染底层不冒充额外研究。静态无实机/TCP/像素/声音通过声明；不改正式Java/资产/待办。','native_denial_with_target_state_receipt');keys.append(k)
f=p+'common/entities/hostile/Wight.java'
add('goety-wight-native-hiding-immunity-with-successful-teleport-state-window',[(p+'common/entities/ModEntityType.java',1533,1537),(f,167,173),(f,413,457),(f,534,540),(f,557,567),(f,569,599),(f,683,831),(f,834,841),(f,947,1065),(f,1149,1175),w(p+'client/render/WightRenderer.java'),(p+'init/ClientInitEvents.java',765,765)],
 '真实Wight registry→native hurt非致命/非NoKnockBack来源在非攻击及CD可用时尝试teleport→实际地面/水/EnderTeleport cancel/原生randomTeleport成功后分支setHide(true)+entityevent4→isInvulnerable/isInvulnerableTo+不可攻击/不可见/缩小尺寸统一读取DATA_HIDE；native server aiStep hidingTime>=100解除+event5并尝试再次teleport；client实体事件同字段写入/renderer消费原生可见性。',
 '隐藏生命周期保护门1，免伤/不可攻击/模型隐藏/尺寸/事件4/5/传送包装同家族不拆。teleport成功才可能入隐藏，不同随机分支也会召小怪/幻象而不hide。当前触发teleport的hurt随后仍super.hurt，原生新隐藏状态可能影响其最终结果，不能把teleportCool设值当本次伤害已拒。隐藏gate覆盖全部source且不单独排bypass，代码没因此停正常全部AI：hide/scream时清输入，仍super.aiStep。每次server hide到期先setHide(false)再试teleport/teleportHit，不以位置迁移成功为解除必要条件；重进hide时hidingTime只在非hide分支归零，连续重入具体时长不凭源码泛称恒100。幻象伤害>0先smoke+discard再super，消失不等于hurt成功或Boss免疫反馈。普通烟雾/黑暗/传送声是状态/传送cue，未专门逐次拒伤灰字/闪光/嗡声/节流；isInvisibleTo幻象例外不要误归普通hide。',
 '免疫资格由明确当前server状态裁决，不能把视觉不可见/传送成功或消失误当控制拒绝；同步文字与状态生命周期并避免过期ID附着。')
m=p+'common/entities/hostile/illagers/Minister.java'
add('goety-minister-native-staff-budget-refusal-break-on-next-hit-and-replay',[(p+'common/entities/ModEntityType.java',1499,1504),(m,132,136),(m,181,187),(m,253,299),(m,380,438),(m,477,506),(p+'utils/ServerParticleUtil.java',201,208),(p+'utils/MobUtil.java',261,277),(p+'utils/MobUtil.java',1177,1194),w(p+'client/render/MinisterRenderer.java'),(p+'client/render/model/MinisterModel.java',108,130),(p+'init/ClientInitEvents.java',759,759)],
 '真实Minister registry/HAS_STAFF默认true→native hurt server且aggressive/!casting/coolDown<=10：staffDamage>=64先break清staff+entityevent13+布碎粒+击退自身+ITEM_BREAK且false；未过预算时排各bypass/explosion/creative/ally/无sourceentity，按actual toolAttack Axe加倍累计并event8/SHIELD_BLOCK/碎屑→false。native entityevents启动block/smashedAnimationState，实际MinisterModel.setupAnim消费且staff.visible同步hasStaff。',
 '累计实际damage预算且下一击才断杖的原生拒伤+回执生产点1；不同于TF一次禁盾/固定hitcount、RSA可再充charge，此链阈值超出仍挡当前，下一次>=64断杖门在source排除之前且断杖那击也false。无sourcePosition仍false但不累计/不播block反馈；AXE加倍是预算消耗不是导致对目标双伤；fraction amount用float累计。for20/5次helper自身再循环5，实际100/25组sendParticles调用，不能据外层20/5说粒子总数；5%笑声不是节流。server tick每tick14/15aggression事件不是每目标反馈冷却。断杖MobUtil.knockBack改变Minister自身速度而非攻击者，不能把其动作复用为Boss“纹丝不动”实现。所有灰字/回执节流仍缺，原版ShieldBlock/ItemBreak只是已存在合适声音参考。未读取整个骨骼动画曲线，不声称动作像素优质；不取用资产。',
 '正式Boss拒控门不能借用盾破坏/受击伤害预算；需唯一拒控事实+按目标窗口统一声音/微光/灰字，明确反馈可见与实际拒绝分别验证。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'goety-batch49','credited_chains':keys,'rationale':'实际隐藏资格/生命周期拒绝1，实际杖damage预算拒绝/断杖事件1；所有wrapper/动画/粒子包不拆。Crone低血source门与flat source-list支持不单独凑；RedstoneMonstrosity距离门需和既有EnderKeeper合并审查，0；Damned恒bypass门/VizierClone成功bool不能直接作Boss免控，0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
