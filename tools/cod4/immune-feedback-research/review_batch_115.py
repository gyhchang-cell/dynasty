"""Actual Sauropod multipart admission loses source/attacker semantics at native relay."""
from ledger import B, O, record, verify
import json
r='AlexModGuy/AlexsCaves';p='src/main/java/com/github/alexmodguy/alexscaves/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='alexscaves-native-multipart-client-admission-versus-generic-server-damage-relay'
record(k,r,[f('AlexsCaves.java',91,135),f('AlexsCaves.java',143,173),f('AlexsCaves.java',180,182),
    f('server/entity/ACEntityRegistry.java',46,46),f('server/entity/living/AtlatitanEntity.java',46,57),
    f('server/entity/living/SauropodBaseEntity.java',104,118),f('server/entity/living/SauropodBaseEntity.java',137,194),
    f('server/entity/living/SauropodBaseEntity.java',247,305),f('server/entity/living/SauropodBaseEntity.java',405,413),
    f('server/entity/living/SauropodBaseEntity.java',617,627),f('server/entity/living/SauropodBaseEntity.java',636,639),
    w('server/entity/living/SauropodPartEntity.java'),w('server/message/MultipartEntityMessage.java'),
    f('server/event/CommonEvents.java',197,214),f('server/event/CommonEvents.java',233,239)],
    '实际ATLATITAN注册→Atlatitan构造→SauropodBase构造七PartEntity，native tickMultipart更新部件、getParts暴露。部件真实hurt先按projectile将amount乘.33，isInvulnerableTo同时看父免疫和同车乘客；只有client非allied来源才向server发MultipartEntityMessage(type1,parentId,playerId,amount)，部件hurt始终false。真实setup注册→enqueueWork receiver以sender当前world解parent/interacter，parent multipart且距离<16后将type1改为generic伤害，直接parent.hurt；父hurt对保留下来的projectile tag才另减伤。',
    '计1：实际战斗部件入口拒绝资格与服务器重新执行之间的来源/攻击者语义丢失。与AlexsMobs VoidWorm原生hurtTime回放不同，此处是原生客户端攻击请求重新造成服务端伤害，非同链port。客户端same-vehicle/allied gate不在receiver重验，包内playerId未与sender绑定，damage无显式有限/正值/上界校验，type1不要求interacter为Player；source被改generic后原projectile属性不再传递，不能假设两次projectile减伤都执行。部件hurt=false并不代表拒伤，可能已经发送真实伤害请求；不允许据此生成Boss免疫字。',
    'Boss反馈从服务端明确的控制拒绝处生成，不能采集任意hurt=false。回执消息不得转为伤害或客户端自报结果；目标/发送者/来源/有限值应在权威执行点验证。原生玩家攻击同车恐龙另由AttackEntityEvent取消，不能当此generic relay已继承相同资格。',
    '实际构造、native tick及multipart更新、部件全文、packet全文、注册和发送完整方法、最终父hurt/isInvulnerableTo、native同车事件已读。无实机/网络攻击测试，不声称漏洞可利用或拒伤画面成功；平台PartEntity/动物继承原版仲裁未完整审计，未按七部件、声音、缩放、实体名字另加数。',
    'native_combat_request_admission_and_authoritative_source_identity_loss')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch115-alexscaves-native-part-hit-request-versus-server-policy','credited_chains':[k],'rationale':'One real native part attack admission and generic server settlement; distinguish existing AlexsMobs hurtTime visual replay, shield-part throttle and generic networking. Seven parts/constant source lists grant no extra credit.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
