"""Native finite block budget, destructive shield break and loss of control; one family."""
from ledger import B,O,record,verify
import json
r='Fuzss/illager-invasion';root=B/'sources'/r.replace('/','__');p='Common/src/main/java/fuzs/illagerinvasion/'
ns=['world/entity/monster/Basher.java','client/render/entity/BasherRender.java']
refs=[(p+x,1,len((root/p/x).read_text().splitlines())) for x in ns]+[(p+'world/entity/monster/Inquisitor.java',246,279),(p+'IllagerInvasion.java',53,56),(p+'init/ModRegistry.java',66,66),(p+'init/ModRegistry.java',79,79),(p+'init/ModRegistry.java',186,188),(p+'client/IllagerInvasionClient.java',43,60)]
k='illagerinvasion-native-finite-block-budget-destructive-disarm-and-stun-release'
record(k,r,refs,
 '真实Basher注册与spawn egg→finalizeSpawn/raidbuff给主手盾，原生MeleeAttackGoal使其攻击→hurt仅aggressive时检查attacker：Living攻击且斧helper/IronGolem/blockedCount>=4在先，破盾声/60tick stun/服务端装备石斧后super.hurt；否则箭或直接Living且有盾→block声、计数++、returnfalse。tick递减stun，isImmobile与hasLineOfSight依据同步DATA_STUNNED禁运动/视线；renderer原版Illager模型与持物层仅aggressive时显示盾或替换后的斧。',
 '独立有限挡击预算耗尽导致破坏性换武器/短stun/当前攻击重新走parent的最终政策1。与已账Mowzie累计概率反击并临时无敌不同，这里确定阈值、单向盾→斧，计数不随tick减也无本类自动重置/补盾；60tick恢复的是stun而非盾。blockedCount未NBT保存，stun单独保存，不能把重载状态等同原挡击预算。只有source.getEntity Living进入破盾分支；直接箭若owner非Living仍可在count>=4后继续挡，不称所有第五击必破。无方向/正伤害或BYPASSES_SHIELD门；普通break声发生在superhurt之前，不能当本次HP成功。近似Inquisitor hurt仅副手、额外声光/反冲差异合并支持0，不按两个实体或盾手拆数。',
 'Boss灰字要表示最终拒控而非破盾/击晕/伤害false；失败与接受后续链应明确。每目标节流不能借用普通挡击预算；声音优先原版适合资源，但SHIELD_BLOCK不自动等同需求嗡鸣。普通阴阳无灰字追加。',
 'Basher全类、真实注册/装备/goal/native hurt/tick及renderer已读；Inquisitor只读hurt对照，不声称其整个恢复或模型已主审。PuzzlesLib斧判断、原版MeleeAttackGoal/音粒子派发和绘图底层仅调用点支持0；未运行AI/TCP/图像/声音，不宣称专门躯体stun动画已存在或通过。','native_final_refusal_budget_and_destructive_release')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch138-finite-block-budget-permanent-disarm','credited_chains':[k],'rationale':'Actual deterministic finite block budget consumed into destructive equipment transition and current-hit admission differs from Mowzie probabilistic counter/rearm and Cat shield durability. Inquisitor sibling same shield budget merges0; item helper/renderer wrappers0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
