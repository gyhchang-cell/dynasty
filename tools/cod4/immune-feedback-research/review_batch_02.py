from ledger import record, verify, O, B, R
import json,hashlib
repo='TeamTwilight/twilightforest';p='src/main/java/twilightforest/'
def tf(key,refs,chain,obs,lesson,limits):
 return record(key,repo,[(p+f,a,b) for f,a,b in refs],chain,obs,lesson,limits,'immunity_rejection_semantics')
tf('tf-lich-shield-and-clone-rejection', [('entity/boss/Lich.java',356,407),('entity/boss/Lich.java',824,857),('components/entity/FortificationShieldAttachment.java',93,126),('network/ParticlePacket.java',17,77)],
 '原生hurtServer入口→瞬移不可见/影分身/同源巫妖/盾层判定→拒绝return false；破盾分支更新同步盾值并调用完整粒子构造→tracking玩家包→enqueueWork→当前玩家level.addParticle。完整hurtServer及其盾值getter、粒子辅助和包编解码/处理均已读；成功受伤后的传送行为不作为本条研究对象。',
 '影分身有独立受击声；普通盾拒绝有格挡声和ENTITY_DAMAGE gameEvent；可破盾魔法damage>2削一层仍返回false，产生16颗面向攻击源的破盾粒子。没有任何文字组件；gameEvent出现并不表示血量损失。',
 '免疫语义应来自明确拒绝分支，不能以ENTITY_DAMAGE、格挡声或零血差推断。攻击成功破盾与完全无效应可区分；粒子与文字属于语义之后的表现。',
 '未验证像素、网络运行或传送AI。粒子快照包无目标ID/维度epoch，当前level处理不等于长期目标绑定。Boss专用规则不能扩到普通阴阳体质。')
tf('tf-naga-home-source-rejection', [('entity/boss/Naga.java',347,364),('entity/boss/Naga.java',428,446),('entity/EnforcedHomePoint.java',46,60)],
 '原生isInvulnerableTo→分别检查source实体和direct实体→isOtherEntityWithinHomeArea→三轴home bounds→home GlobalPos维度有效性；hurtServer仅在super成功后记伤害/眩晕累计。',
 '爆炸直接拒绝；攻击者或投射物源任一越过home矩形边界也拒绝。无有效同维度home时边界辅助返回true。本链无专用S2C文字或声音。',
 'Boss免疫原因可与攻击来源及区域有关；目标ID相同不能证明两次事件原因相同，维度/来源必须纳入语义分析。',
 '只读模组覆写和home辅助，原版super以平台契约为界；不把无专用文本称作灰字实现。')
tf('tf-alpha-yeti-ranged-phase-projectile-rejection', [('entity/boss/AlphaYeti.java',167,179),('entity/boss/AlphaYeti.java',277,296)],
 'hurtServer完整覆写→canRampage本地布尔+isTired同步标志+IS_PROJECTILE标签→拒绝；否则super成功才置canRampage；setTired重置canRampage。',
 '只在不能狂暴且未疲劳时免疫投射物；承受一次有效伤害会改变后续拒绝条件。拒绝路径没有自定义文本、粒子或声音。',
 '同一目标的免疫可随阶段变化，不能在客户端永久缓存“此Boss免疫”；拒绝回执应对应当次服务器决策。',
 '未研究狂暴AI全时序或原版伤害内部；本条只计完整阶段拒绝链，不按三个状态分支拆数。')
tf('tf-knight-phantom-directional-shield-rejection', [('entity/boss/KnightPhantom.java',310,341)],
 '原生hurtServer→完整isDamageSourceBlocked→pierce箭排除、BYPASSES_SHIELD、实际blocking item、sourceposition和水平点积→原版SHIELD_BLOCK声音→false；否则super。',
 '正面且实际举盾才阻挡；穿刺箭、绕盾伤害、无源位置不走拒绝。使用已有原版格挡音，不需要新录音。',
 '格挡与Boss拒控是不同语义；不应把所有hurtServer false都标成Boss Immune。可借鉴原版声音资源与明确判定点。',
 '代码注明该辅助为VanillaCopy；这里只计模组实际接入的整条Boss拒绝与声音链，不计原版复制方法为另一条，不证明画面。')
tf('tf-mounted-goblin-shared-shield-rejection', [('entity/monster/UpperGoblinKnight.java',89,121),('entity/monster/UpperGoblinKnight.java',138,190),('entity/monster/UpperGoblinKnight.java',237,248),('entity/monster/UpperGoblinKnight.java',267,360),('entity/monster/LowerGoblinKnight.java',155,188)],
 '上层/下层hurtServer均以攻击角度进入同一个takeHitOnShield→disabled/斧头/伤害阈值→声音、盾值/禁用同步→拒绝；server AI恢复禁用，破盾广播STOP_ATTACKING→客户端breakItem。两个实体入口合为一条。',
 '斧头首次命中禁用盾并被挡，后续禁用期直接不挡；disabled计数后置++达到100时恢复。累计3次高伤破盾，非正面可随机损盾。骑乘下层委托上层盾，不能把上下实体各计一次。',
 '共享盾/部件应归到同一语义目标，显示去重不能盲按命中部件刷屏；同步禁用状态与事件反馈不同。已有SHIELD_BREAK/BLOCK足以提供可选原版声音依据。',
 '此为普通怪盾行为参考，不能据此新增普通体质灰字门槛；未做实际破盾画面或乘骑同步验收。')
# 补齐已阅读的Toro实际tick生产入口，非新增研究信用。
f=O/'reviewed.json';rows=json.loads(f.read_text());rel='src/main/java/net/torocraft/torohealth/mixin/PlayerEntityMixin.java';s=B/'sources/ToroCraft__ToroHealth'/rel
for row in rows:
 if row['id']=='torohealth-tracked-health-particle':
  row['source_refs'].append({'path':str(s.relative_to(R)),'source_path':rel,'lines':[22,31],'file_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'url':f'https://github.com/ToroCraft/ToroHealth/blob/{row["commit"]}/{rel}#L22-L31'})
f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
verify()
