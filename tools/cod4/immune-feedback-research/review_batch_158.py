"""Actual attack-attempt target receipt and cursor-qualified gameplay cache: one chain."""
from ledger import B,O,record,verify
import json
repo='Mickelus/tetra';root=B/'sources/Mickelus__tetra';p='src/main/java/se/mickelus/tetra/'
refs=[(p+'TetraMod.java',82,228),(p+'TetraMod.java',247,267),(p+'ClientSetup.java',57,67),(p+'ClientSetup.java',135,153),(p+'effect/ItemEffectHandler.java',160,204),(p+'effect/SlamEffect.java',45,84)]
for rel in ['effect/revenge/RevengeTracker.java','effect/revenge/AddRevengePacket.java','effect/revenge/RemoveRevengePacket.java','effect/gui/RevengeGui.java','effect/gui/AbilityOverlays.java']:
 f=p+rel;refs.append((f,1,len((root/f).read_text().splitlines())))
k='tetra-native-attack-attempt-target-receipt-owner-bucket-lifetime-and-cursor-qualified-feedback'
record(k,repo,refs,
 'Mod构造器实际注册ItemEffectHandler+ClientSetup，setup注册Add/RemoveRevengePacket。原生LivingAttack监听末尾调用RevengeTracker.onAttackEntity：server且精确PLAYER type、source entity非null时登记其IntegerID，再只向受击ServerPlayer发送Add包。客户端handle登记本地玩家bucket；真实AbilityOverlays注册BelowAll并eventbus，START clienttick以mc.hitResult更新RevengeGui，render实际drawChildren。指向已登记攻击者且手持有abilityRevenge才动画显示准星左右indicator。',
 '一个游戏攻击来源回执→目标集生命周期→实际目标准星显示链1，非通用Guava网络/图形计数。owner key服务端正ID/客户端负ID，enemy key整数ID无UUID/维度/代际；最多100受击者bucket，expireAfterWrite30秒，HashSet.add并非cache写入，不续期老bucket。后来的另一个攻击者可继承更短剩余期；重复攻击仍每次发Add包，集合去重不等网络节流。server与client各自从首次插入计墙钟过期，有延迟差，不是严格tick同步；未见该完整Tracker中的登出/换维清理，不能宣称无ID复用污染。资格展示由当前手持模块决定，但server登记所有符合PLAYER受击尝试不要求持有模块。LivingAttack不是最终伤害，已取消事件接收行为由Forge默认语义决定，后续listener仍可能拒绝，绝不可当Boss免疫/成功掉血。Remove包只移除该ID、不删bucket；完整groundSlamEntity在hit result非fail后尝试stun、不读addEffect结果便消费标记及同步，不能当控制成功。',
 'Boss明确拒控回执应绑定目标UUID/维度/生命周期与真实裁决；按目标节流不能做受击者共享短命bucket、也不能把集合不重复误作无刷包。客户端实际目标可见资格与服务器原因分开，不从攻击尝试回执导出灰字。墙钟cache过期和跨端到包时间不构成严格同帧同步。普通阴阳体质不增加灰字。',
 'Tracker、两个packet、RevengeGui和AbilityOverlays全文；完整Mod构造器/setup、client注册方法、攻击listener及groundSlamEntity已读。Mutil AbstractPacket/PacketHandler线程及direction校验、GuiRoot/GuiTexture底层/素材像素、其他技能消费入口未全部展开；不声称网络方向安全、目标世界锚定文字或实际观感通过。此处为准星HUD目标标记而非世界浮字。Slam上游所有技能调度/原版damage最终结算不在本闭合反馈子链，地震stun成功未验。仅真实来源研究，无生产修改/编译/游戏。','native_target_receipt_lifecycle_and_cursor_feedback')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch158-native-revenge-target-set-gameplay-feedback','credited_chains':[k],'rationale':'Attack attempt provenance synced to victim and current item/cursor-qualified HUD with shared owner-bucket lifetime; not raw network/cache library credit. Add/remove wrappers, abilities and left/right indicators all merged.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
