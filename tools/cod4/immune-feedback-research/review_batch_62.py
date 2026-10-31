"""Wizardry native collision-shield refusal versus player resistance."""
from ledger import B,O,record,verify
import json
r='Electroblob77/Wizardry';p='src/main/java/electroblob/wizardry/';k='wizardry-native-separate-collision-shield-refusal-and-weak-owner-lifetime'
def w(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(k,r,[w('spell/Shield.java'),w('entity/EntityShield.java'),(p+'item/ItemWand.java',377,409),(p+'item/ItemWand.java',414,545),(p+'data/WizardData.java',225,242),(p+'registry/Spells.java',28,30),(p+'registry/Spells.java',316,316),(p+'registry/WizardryEntities.java',163,164),(p+'client/ClientProxy.java',909,909),w('client/renderer/entity/RenderBlank.java')],
 '实际Registry new Shield/EntityShield→ItemWand原生右键启动持续使用→native onUsingTick逐tick计charge/SpellCast.Tick/魔力预算→cast Shield服务端给10tickRESISTANCE，WizardData SHIELD_KEY空才造单独可碰撞EntityShield并存引用/spawn→Shield原生attackEntityFrom若direct IProjectile在弹位置广播DEFLECT声，仍调用super后恒false；native onUpdate弱引用owner跟随look，非activeHand或activeItem非ISpellCastingItem清key并setDead；已注册实体RenderBlank是空doRender。',
 '一个独立可碰撞代理实体的最终拒伤/声回执整链1，不与玩家本体RESISTANCE减伤混为全免疫。source是投射物即可先发声，super结果被忽略后总false，不证明弹真的反向/销毁或玩家没伤；声位置是弹当前位置。constructor bbox在玩家look偏移1，onUpdate跟随偏移.3，原生碰撞时序须实机；没自写反射速度逻辑。SHIELD_KEY只在null时spawn，无isDead重建检查。owner弱引用丢失server会setDead但不清玩家key；activeHand只检casting item，不检当前spell仍Shield。默认网络构造不设player，原生spawn tracking未自传owner，client代理不靠同一弱引用跟随，不能称双端锁定成功。RenderBlank对代理无几何，其他Shield视觉不在本条证据内。',
 '显式最终拒控点与额外减伤效果必须分开；声音先于判定结果时不能冒充Boss免疫已确定。目标销毁/key清理/重新追踪是实际生命周期条件，不拿单个构造器或hurt=false代替整链。',
 '固定fe5d05a7a134836dd972e3680a900619c7e9c134。关键native包含方法/注册/consumer全文已读；此处只确认独立代理拒绝，不声称所有箭碰撞一定反弹、全身免伤、完整spell视觉或原生音质。通用Forge追踪/RESISTANCE引擎0，不启动游戏或改正式代码/资产/待办。','native_final_damage_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'wizardry-collision-proxy-shield-batch62','credited_chains':[k],'rationale':'独立实体native最终拒伤与弱owner/hand生命周期整链1，不按DEFLECT声wrapper、blankrenderer、resistance与每tick重复cast加数；与既有装备方向盾或Forcefield群体力场不是常量换壳。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
