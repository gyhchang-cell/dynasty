"""Observed support/exclusions, zero research credit; no candidate auto-promotion."""
from ledger import B,O
import json,hashlib
out=[]
def add(key,repo,paths,observed,reason):
 root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());refs=[]
 for p in paths:
  q=root/p;assert q.is_file();refs.append({'path':str(q.relative_to(B.parents[2])),'source_path':p,'file_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{p}'})
 out.append({'id':key,'repo':repo,'commit':meta['commit'],'research_credit':0,'observation':observed,'exclusion_or_pending_reason':reason,'refs':refs,'read_granularity':'Only described complete methods/classes were observed; no automatic claim all cited files read in full.'})
r='Infamous-Misadventures/Dungeons-Mobs';p='src/main/java/com/infamous/dungeons_mobs/'
add('dungeonsmobs-ensnare-control-support-not-per-wrapper-credit',r,[p+x for x in ['DungeonsMobs.java','mod/ModEffects.java','entities/EntityEvents.java','entities/ClientEntityEvents.java','entities/projectiles/SnarelingGlobEntity.java','entities/ender/SnarelingEntity.java','effects/EnsnaredEffect.java']],
 '上述类全文已读。Snareling原生baseTick射击倒数15 server生成Glob；命中server Living不读hurt或addEffect返回。damage排Enderling但ensnare并未同排。原生effect每tick清XZ/setspeed0并有-5 MULTIPLY_TOTAL modifier；事件取消交互/击退等，client input只将getMoveVector().scale(0)的返回丢弃、另禁跳。onHit原生字节3粒子/落地声与接纳无关。',
 '目前并入既有状态→输入/动作门与addEffect未读结果反例支持0；不能以多个event包装各加1，不能把落地声当Boss免控回执。固定快照编译兼容未验。')
add('dungeonsmobs-enchanter-incomplete-external-defense-chain',r,[p+'entities/illagers/EnchanterEntity.java'],
 '整篇已读：近距攻击tick12，EnchantGoal给外部cap STRONG/PROTECTION2，目标活且<=30保留，remove/失效调用removeAllMobEnchant。List<UUID>同步；默认Level构造错误地取GEOMANCER，EntityType构造另路。',
 '外部EnchantWithMob保护实际消费者未补，未证完整拒伤/回执链；普通buff租期不晋级。未称已运行或确认产品bug。')
add('dungeonsmobs-construct-immunity-and-wildfire-resource-skin',r,[p+'entities/summonables/ConstructEntity.java',p+'entities/blaze/WildfireEntity.java'],
 'Construct整篇、Wildfire.hurt完整方法已读：Construct除OUT_OF_WORLD外拒伤，owner UUID server按维度lookup、life递减；Wildfire盾伤资源耗减/破盾仍returnfalse。',
 'Construct缺具体施放native链，静态来源门不独立晋级；Wildfire并既有Goety盾资源吸收家族0，不按实体名加数。')
r='DivineRPG/DivineRPG';p='src/main/java/divinerpg/entities/boss/'
add('divinerpg-karos-and-scorchers-explosion-source-skins',r,[p+'EntityKaros.java',p+'EntityKingOfScorchers.java'],
 'Karos整篇已读；KingOfScorchers完整hurt/performRangedAttack已读（后段cat输出截断，未称整篇）。两hurt均按EXPLOSION直接false，其余super；Karos其它字幕为场景/嘲讽，不在拒伤点。',
 '同固定damage source筛选换mob名0；不将ambient字幕伪称免疫反馈。')
r='DrZhark/mocreaturesdev';p='src/drzhark/mocreatures/'
add('mocreatures-partial-weapon-mitigation-owner-skins-and-hide-transition',r,[p+x for x in ['entity/monster/MoCEntityWerewolf.java','entity/passive/MoCEntityHorse.java','entity/passive/MoCEntityTurtle.java','entity/MoCEntityAnimal.java']],
 '各完整attackEntityFrom已读；Turtle flipflop完整。Werewolf人形外玩家手持物伤害改1，金工具6..10非免疫；Horse拒当前骑者/狼并清狼target，其余armor+2数值减伤下限0；Animal按名字拒非owner、hurt前发旧health。Turtle隐藏时拒伤，1/10翻身清hiding后本击仍false。',
 '数值部分减伤/已有owner友伤/phase改变支持0；Turtle完整躲藏原生生产链未补，不拿单hurt方法当完成。Animal旧HP消息未补本版本HUD完整链，不额外计。')
r='team-abnormals/upgrade-aquatic';p='src/main/java/com/teamabnormals/upgrade_aquatic/'
add('upgradeaquatic-boxjellyfish-ordinary-retaliation-support',r,[p+'common/entity/animal/jellyfish/BoxJellyfish.java'],
 '整篇已读，hurt只在super成功后设反击target；stingEntity父成功再加毒。hunt cooldown普通AI择敌，不是免疫回执节流。',
 '非独立免控/拒伤/受击文字实现，0。')
r='Octo-Studios/relics';p='src/main/java/it/hurts/sskirillss/relics/items/relics/'
add('relics-partial-resistance-and-noncombat-cancel-support',r,[p+x for x in ['belt/HuntingBeltItem.java','belt/KineticBeltItem.java','RiderFluteItem.java','feet/CutGlassBootItem.java','ring/RingOfTheSevenDeadlySinsItem.java']],
 '完整观察HuntingBelt.onLivingDamageOwner：5宠物/每stack.9，总量再cap.9；KineticBelt.onLivingDamage gliding正向伤害和resistance相减下限0，实际激活producer未补；RiderFlute.getMountedResistance/onLivingDamage全文只见默认partial，slots/store/recall部分完整方法已读未读完整类。CutGlass.onFluidCollision取消流体碰撞、Ring.onSlotClick取消卸装备，并非战斗免疫事件。',
 '不将纯部分减伤、未补真实激活的数学下限或非战斗交互cancel凑入1000；候选0。')
r='P3pp3rF1y/Reliquary';p='src/main/java/reliquary/'
add('reliquary-common-dispatch-already-owned-family-support',r,[p+'handler/CommonEventHandler.java'],
 'CommonEventHandler全文已读：hurt/death按有序handler最先apply成功后break取消，其余普通flight状态/登录。',
 '已有hunger conversion shortcircuit完整家族的分派器，不另按handler包装计数；飞行/非战斗交互辅助0。')
(O/'uncredited-observations-20261027e.json').write_text(json.dumps({'credit':0,'observations':out},ensure_ascii=False,indent=2)+'\n');print({'zero_credit_groups':len(out)})
