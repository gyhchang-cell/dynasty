"""Native accepted-hit interruption to action replay, one game policy, not model/library credits."""
from ledger import B,O,record,verify
import json
r='BobMowzie/MowziesMobs-Public';p='src/main/java/';m=p+'com/bobmowzie/mowziesmobs/';n=m+'server/entity/naga/EntityNaga.java'
def f(s,a,b):return m+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(m+s)).read_text().splitlines()))
def lib(s):
 s=p+'com/ilexiconn/llibrary/'+s
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
k='mowzie-naga-native-accepted-hit-phase-interruption-to-ground-recovery-replay'
record(k,r,[(n,73,87),(n,158,300),(n,371,564),(n,605,672),(n,675,835),w('server/entity/MowzieLLibraryEntity.java'),w('server/ai/animation/AnimationAI.java'),w('server/ai/animation/SimpleAnimationAI.java'),w('server/ai/animation/AnimationProjectileAttackAI.java'),lib('server/animation/AnimationHandler.java'),lib('server/network/AnimationMessage.java'),f('server/message/NetworkHandler.java',29,52),f('server/entity/EntityHandler.java',64,64),f('client/ClientEventBusSubscriber.java',20,41),w('client/render/entity/RenderNaga.java'),w('client/model/entity/MowzieEntityModel.java'),f('client/model/entity/ModelNaga.java',773,1240)],
 '固定7aa173，实际NAGA注册/渲染注册。native hurt先父方法，再读当前animation；parent结果true且damage>0、非FALLING、吐弹tick<30或俯冲tick<25才send HURT_TO_FALL并interrupted=true。原生Goal及performRangedAttack检查interrupted拒后续攻击；tick在受击动画17切FALLING，落地或入水/岩浆切FALLEN/LAND并置60tick地面窗口，窗口结束且无动画再GET_UP，动画26恢复HOVERING。',
 '计1：真实成功受击且攻击阶段限定的打断→物理坠落→落地锁定→起身恢复政策及同实体动作回放整链，区别通用hurt动画包装、Thrasher pre-hurt概率预算和Illage零伤吟唱预算。原生travel FALLING/FALLEN走重力摩擦分支；causeFallDamage仅FALLING交父，不能称一直免摔。AnimationHandler服务端setAnimation+tracking/self广播，AnimationMessage当前world查ID/IAnimatedEntity后按index设动画/tick0；未校index范围/UUID/维度代际。movement/interrupted非同步字段，客户端靠收到animation及local tick推导，不声称两端同帧已验。真正ModelNaga.animate完整按HURT_TO_FALL/LAND/GET_UP动骨，但FROZEN_DATA为true时整段动画跳过。',
 'Boss拒控灰字仅在明确拒控分支生产；成功受击可打断的相反例说明不能依据动画或hurt bool给Boss贴immune。动作阶段、物理状态与收包身份/时间基准必须分别验证，模型动作归原建模对话，普通体质type9不扩门槛。',
 'registerGoals/tick/hurt/performRangedAttack/travel/动画访问器和实际模型animate、消费setupAnim全文已读；不是整篇Naga或整篇ModelNaga全文。NetworkHandler只读完整register方法，通用LLibrary helper随实际链支持0，不单计网络/模型方法。模型default-angle细节、DynamicChain/动画器底层及像素/声音/双TCP未验，不声称任何观感通过，不复制资产。','native_accepted_hit_phase_specific_action_interruption')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch108-native-naga-accepted-hit-phase-interruption','credited_chains':[k],'rationale':'One phase-qualified accepted-hit interruption policy with delayed falling/ground lock/recovery and real animation consumer. Not generic hurt animation wrapper, not pre-parent capture escape budget, not zero-hit chanting counter. Shared network/model helpers remain zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
