"""Three active Aether boss denial policies and actual feedback semantics."""
from ledger import B,O,record,verify
import json
r='The-Aether-Team/The-Aether';p='src/main/java/com/aetherteam/aether/';keys=[]
def w(f):return p+f,1,len((B/'sources'/r.replace('/','__')/(p+f)).read_text().splitlines())
f=p+'entity/monster/dungeon/boss/Slider.java';k='aether-slider-native-tool-room-refusal-explicit-reason-shared-cooldown'
record(k,r,[(p+'entity/AetherEntityTypes.java',93,94),(f,146,169),(f,206,320),(f,635,646),('src/generated/resources/assets/aether/lang/en_us.json',631,631),('src/main/resources/assets/aether/lang/zh_cn.json',598,598)],
 '实际Slider entity registration→native hurt先canDamageSlider→直接Living工具能力/tag/正确挖掘CarvedStone或投射物tag+owner+BossRoomTracker空间资格→不合法反向投射物并向玩家发本地化invalid/tooFar文字→Boss本体15tick chatCooldown→native tick递减；合格才super.hurt/start/受击倾斜。',
 '明确拒伤理由+按Boss实例共享限频家族1，不按工具/房间/投射物/消息helper拆。cooldown属于Boss而非每攻击者，A玩家失败会压住B玩家反馈；invalid与tooFar共用15tick。wrongtool文字是动作栏或聊天由config决定，不是目标头顶灰字；实际zh/en key均有对应文本。绕过无敌来源仍先走资格检查（可能发invalid/反弹），随后调用super.hurt却未return结果，末尾false；所以可真的扣血但返回false。合格分支只有super成功且health>0才true，致命击同样可能false；hurt=false尤其不能自动作为免疫回执。无明确逐次免控声/闪光。',
 'Boss回执最好携带可区分原因，以最终控制拒绝为准；按Boss或按攻击者节流必须明确，别把共享CD错误描述成每位玩家单独限频；普通体质不加灰字。',
 '固定e07d30e16fbd0f09cc067b39594035e395dcf996；关键完整方法已读。BossRoomTracker来自外部Nitrogen，其空间判断内部未观察0；本条观察明确wrongtool生产/原生拒伤而非宣称场地几何已验证。无游戏/正式代码/资产/待办改动。','native_boss_rejection_reason_and_throttle');keys.append(k)
f=p+'entity/monster/dungeon/boss/SunSpirit.java';k='aether-sun-spirit-native-cold-reflection-opens-different-damage-policy-window'
record(k,r,[(p+'entity/AetherEntityTypes.java',105,106),(f,76,83),(f,154,161),(f,240,260),(f,354,369),(f,522,549),(f,695,706),w('entity/projectile/crystal/IceCrystal.java'),(p+'data/resources/registries/AetherDamageTypes.java',24,24),(p+'data/resources/registries/AetherDamageTypes.java',34,34),(p+'data/resources/registries/AetherDamageTypes.java',52,54),('src/generated/resources/data/aether/tags/damage_type/is_cold.json',1,5),('src/generated/resources/assets/aether/lang/en_us.json',649,649)],
 '实际SunSpirit注册+默认非frozen→native isInvulnerableTo非frozen只放bypass/cold→native IceCrystal.hurt反击转owner为攻击者、水平look*2.5→命中doDamage或Boss customServerAiStep近距补判→原生ICE_CRYSTAL damage→Boss super.hurt成功才置frozen/175tick/一次弱点提示+FireMinion→serverAI倒数到0后解除→拒伤政策恢复。',
 '冷弹反击打开特定受击窗口的实际最终拒伤家族1，所有冷tag/反弹helper合并。冻结时政策改成只允许living来源且不是SunSpirit，反而不检查BYPASSES_INVULNERABILITY；不能按注释笼统说永远只吃冰晶。非frozen有cold标签即可能伤害，不强制direct IceCrystal；但置frozen必须actual direct IceCrystal+living source+成功且health>0。doDamage成功才弱点附加效果，但此WeaknessDamage内部未研究0。被拒绝的攻击没有专门灰字/嗡声；英文弱点提示发生在接纳后，且displayWeakMessage一次门不是拒控节流。冻结状态是Boss特有状态，不等于可受普通所有药水/停全部AI；近距check与碰撞都可能尝试同颗晶体，未见本方法逐目标nonce。',
 '免疫与阶段弱点接纳需使用不同语义；不能从“受击后frozen”反推普通Boss控制皆可施加，也不能将成功弱点提示当拒控灰字。',
 '固定版本/真实cold标签已读。原版粒子/同步引擎及WeaknessDamage辅助0；不声称晶体源生成AI、自然获取、完整渲染/两TCP/观感验收。无游戏或正式修改。','native_boss_damage_policy_transition');keys.append(k)
f=p+'entity/monster/dungeon/boss/ValkyrieQueen.java';k='aether-valkyrie-queen-native-negotiated-fight-readiness-damage-refusal'
record(k,r,[(p+'entity/AetherEntityTypes.java',99,100),(f,164,168),(f,319,367),(f,373,389),(f,398,426),(f,564,575),(p+'entity/monster/dungeon/AbstractValkyrie.java',118,124),w('network/packet/serverbound/NpcPlayerInteractPacket.java'),(p+'Aether.java',252,252),('src/generated/resources/assets/aether/lang/en_us.json',617,623),('src/main/resources/assets/aether/lang/zh_cn.json',584,590)],
 '实际Queen注册默认DATA_IS_READY=false→已注册playToServer NpcPlayerInteractPacket取sender+当前世界NpcDialogue→handleNpcInteraction选项1服务器检查非和平/库存10勋章→readyUp附近聊天/setReady true并扣勋章→native hurt bypass先放，否则ready+livingowner+非和平+房间资格才super→首次接纳并存活后回满血/开战/关房。',
 '协商开战资格的最终拒伤点1，回执/门槛/消耗同链不拆。ready先于扣物写入，扣物遍历inventoryMenu而countItem来自Inventory，未经运行不能声称所有自定义槽完全对应。native packet只看sender server非空+当前world entityID是NpcDialogue，未查距离/当前conversingPlayer/对话窗口token；一次合法语义接口不等于严格会话授权。hurt前置拒绝没有免疫灰字，准备/未够勋章聊天属于交互理由，不能冒充攻击拒绝回执。首次有效攻击super会生效但接着回满血，是战斗启动特例，非控制免疫。chat(sound)不读sound参数总播interactSound，邻近每个player调用可能重复声，不能当节流。',
 'Boss拒控逻辑与开战/交互资格分开，拒控反馈不应启动/重置战斗；S2C只显示服务器决定的目标和类型，不让客户端请求自由触发Boss灰字。',
 '固定版本，全文关键hurt/交互/packet/聊天方法已读；客户端对话UI发包生产和Nitrogen room内部辅助0，未声称网络安全或整包真实通过。身体模型/动画原岗，未改资产。','native_boss_interaction_damage_gate');keys.append(k)
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'aether-boss-batch56','credited_chains':keys,'rationale':'Slider资格+具体拒绝文字/共享CD、Sun冷弹切换不同最终政策、Queen勋章交互开战资格各1；room边界包装/名称/状态常量不拆；Sun blanket effect false另归既有boss-effect allowlist辅助0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
