"""Two independent Relics native defense sites; no credits for component/wrapper count."""
from ledger import B,O,record,verify
import json
r='Octo-Studios/relics';p='src/main/java/it/hurts/sskirillss/relics/';q=p+'items/relics/ShieldOfRetaliationItem.java';keys=[]
def whole(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
shared=[whole(p+'Relics.java'),(p+'init/RelicsItems.java',78,82),(p+'init/RelicsDataComponents.java',76,82),(p+'init/RelicsDataComponents.java',106,114),whole(p+'network/NetworkHandler.java'),(p+'api/relics/data/AbilityData.java',272,274)]
def add(k,refs,chain,obs,lesson):
 if k in {row['id'] for row in json.loads((O/'reviewed.json').read_text())}:
  keys.append(k);return
 record(k,r,refs+shared,chain,obs,lesson,'固定da846fcb3223e88d7c926b4478506b3089caff51。完整Shield类全部方法及实际native item/event/client tick/packet全文观察。未运行，不证明画面/粒子可辨、两端一致或声音合适；Shake内部渲染/codec未全文研究，只证明addForPlayer定向发包，不把相机方案应用到本项目。普通阴阳无灰字要求。','native_defense_feedback_and_target_lifecycle');keys.append(k)
add('relics-native-shield-final-cancel-recoil-and-release-rearm',[(q,72,324),(q,491,557),(q,645,751),(q,755,895),whole(p+'network/packets/S2CSetEntityMotion.java'),whole(p+'network/packets/item/shield_of_retaliation/C2SShieldOfRetaliationRelease.java'),whole(p+'dev/shake/ShakeManager.java'),whole(p+'dev/shake/misc/ShakePacket.java'),whole(p+'utils/TargetingUtils.java')],
 '已注册Shield原生use开每stack窗口；server LivingIncomingDamage→实际using同一stack/能力/方向资格→applyBlockRecoil先发本机motion→cancel事件并记成功，随后sound/可选反弹或捕获/定向Shake/可选stun；非guard当击关窗stopUse。原生inventoryTick/释放finishParry；client实际按用下降沿5tick发release，server收包仅解本人inventory所有此盾lock。',
 '方向位置按direct entity中心→owner中心→sourcePosition择一；无来源位置直接允许格挡，未检查bypass tag，不能把它当vanilla shield来源策略。成功格挡仍强制反冲，因此取消伤害不等于不受控制。motion包按当前world整数id只查实体非null，无UUID/维度/代际/数值finite校验；server applyBlockRecoil只发client没有同法写server运动。finish没成功才设miss弱点，下一击finite乘伤后消费。client重发release是重武装，不是重复免疫反馈节流；packet无item token/age/use真实性验证，解锁全部同类stack。每包装/方向条件/声音变体0额外。',
 'Boss明确拒控应保持本次位移不执行，不能因cancel伤害就发Immune；按权威目标与原因生产反馈。本项目不能照搬改变他人Camera的Shake。输入重发与服务端目标反馈去重是不同职责。')
add('relics-native-prehit-projectile-capture-uuid-anchoring-release',[(q,181,270),(q,299,490),(q,537,751),(q,755,895),(q,895,914)],
 '同一实际原生inventoryTick在active held盾时holdCapturedProjectiles；先已有UUID重新定位，再以swept shieldBox/朝向/弹运动筛真实弹，按UUID加入stack持久component并noGravity/速度零，发布成功/声/延长窗口；client RenderFrame用同stack UUID局部8格查询按eye/offset定位。finish/release在server UUID取弹→改owner/恢复重力/瞄准发回并清列表。',
 '这是实际接触扣血之前的弹实体控制点，与LivingIncomingDamage拒伤不同。服务端UUID查本维全entity，客户端8格局部且不cleanup；持有stack仅UUID+局部偏移无世界键/原owner/原gravity快照，换维或掉落时不存在所示独立清退，不能说完整恢复。captureProjectile和扫描hold重复逻辑合并1；hold先取captured快照，再positionCaptured内可能清理并写新表，末尾changed时会把旧snapshot写回，静态可能恢复缺失UUID条目。反冲/捕获的FX只证明已取弹，不等于未来伤害有效；release忽略被移除弹并在released>0才声/Shake，给每颗写一次bonus，下一伤害事件读后删。无捕获数量上限，UUID防同弹不等于同目标提示节流。组件只persistent，未见explicit networkSynchronized，不声称frame端必收所需表。',
 '控制载体的目标绑定应使用可校验身份和世界，提前消失/换维/持有物丢失要安全退场；临时反馈的快照和追随目标职责应区分，不能据几何调用假定像素可见。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'relics-shield-native-batch30','credited_chains':keys,'rationale':'2个原生不同最终职责：实际受击事件取消/反冲回执；扣血前捕获弹实体UUID锚定与释放生命周期。输入release包、component/codec/客户端frame/瞄准/常量0额外；不按每包装拆信用。525Java导入0，Immortality缺producer0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
