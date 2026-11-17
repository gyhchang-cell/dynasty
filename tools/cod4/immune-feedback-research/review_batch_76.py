"""Native multipart combat-feedback replication and its real receiver boundary."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/AlexsMobs';p='src/main/java/com/github/alexthe666/alexsmobs/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='alexsmobs-native-multipart-hurt-receipt-target-pair-validation'
record(k,r,[f('AlexsMobs.java',55,113),f('AlexsMobs.java',138,182),f('entity/AMEntityRegistry.java',96,96),f('entity/EntityVoidWormPart.java',201,288),f('entity/EntityVoidWormPart.java',338,368),f('entity/EntityVoidWormPart.java',410,428),f('entity/EntityVoidWormPart.java',467,474),w('entity/IHurtableMultipart.java'),w('message/MessageHurtMultipart.java'),f('ClientProxy.java',96,268),f('ClientProxy.java',296,298),w('client/render/RenderVoidWormBody.java')],
 '实际EntityRegistry注册VoidWormPart；原生part.tick在服务端parent为Living且hurtTime/deathTime>0时每tick发三参MessageHurtMultipart(part int,parent int,0)，并本地复制两计时。sendMSGToAll遍历服务器全玩家，sendNonLocal按PLAY_TO_CLIENT；实际setup注册该消息。receiver.queue按接收侧取sender或client Player、当前world用两个整数查实体，再解析damageType注册表，只有type/holder存在才调用IHurtableMultipart.onAttackedFromServer；该真实part consumer仅复制父计时。实际ClientProxy.clientInit注册RenderVoidWormBody，其deathTime参与翻倒旋转。',
 '一个实际分体Boss受击/死亡计时回放及目标对校验边界1，不将codec/发送/renderer包装分别计数。不同于TF共享父盾每tick命中抑制，此处是每受击tick对全服务器玩家重复发送，没有目标反馈去重/距离/维度筛选。服务端getParent以UUID只查本world，包却不含UUID/维度且接收端不验part实际parent关系；当前世界ID复用可错配，未做真实复现。三参constructor把damageType设空串，消费仍先强制注册表查询，该producer未提供实际注册type；不能称原生分体回放已成功。若part缺失且parent.isMultipartEntity，则另直接hurt(parent,damage)，不是纯无副作用visual包；注册本身不限定接收方向，但不能据此未经测试宣称可利用。',
 'Boss灰字S2C必须验证类型、目标UUID/维度和显示期限，不能按任意当前world int和客户端给出的parent配对；回放包应避免产生额外伤害。迟包或不存在目标应安全丢弃，不能用存在发送调用就声称显示链完成。',
 '固定版本，native tick、sender、codec、receiver、实际consumer、关键renderer和注册全文方法已读。isHurt实际health<=5换纹理，不等于瞬间hurtTime闪红；未把两者混为一项。未审/复制模型贴图，未运行客户端，不证明空damageType具体运行异常或画面已复现；其他动物同包生产路径未补，不另计。','native_multipart_combat_feedback_receiver')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'alexsmobs-batch76-multipart-feedback','credited_chains':[k],'rationale':'真实多段Boss原生hurt/death计时广播→消费的目标对/注册damage type边界独立；不同body/tail纹理、发送包装、两个计时字段和codec都合并1，不把素材作为独立实现。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
