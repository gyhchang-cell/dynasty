"""Ars Elemental native mana settlement, debuff refusal, and nonprojectile return attack."""
from ledger import B,O,record,verify
import json
r='Alexthw46/Ars-Elemental';p='src/main/java/alexthw/ars_elemental/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def res(s):return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[w('common/glyphs/EffectBubbleShield.java'),w('common/mob_effects/BubbleShieldEffect.java'),w('registry/ModPotions.java'),w('ArsElemental.java'),f('registry/ModRegistry.java',97,117),f('ArsNouveauRegistry.java',89,95),f('ArsNouveauRegistry.java',128,199)]
ks=[]
k='ars-elemental-native-mana-bubble-post-reduction-settlement-and-iframe-cost-suppression';ks.append(k)
record(k,r,common+[f('event/DamageEvents.java',234,272)],
 '真实@Mod构造→registerRegistries注册EFFECTS，ArsNouveauRegistry.init注册BubbleShield glyph；onResolveEntity仅对有mana capability的living调用applyConfigPotion，MANA_BUBBLE对应mana_shield。@EventBusSubscriber DamageEvents.postReductionDamageTweaking在LivingDamageEvent.Pre做护盾结算：非bypass enchant且有bubble，cost=max(0,配置350-discount*.75)，有限伤害<100000且有mana，maxReduction=mana/cost，amp=min(1+effect amplifier,maxReduction)，new=max(0,damage-amp)。实际reduction>0且mana>=cost才设置新伤害；postAttackInvulnerabilityTicks!=现有invulnerableTime才扣actualReduction*cost；余mana<cost移除状态。',
 '独立实现为原生最终减伤阶段“按法力容量/状态amp限制+实际减额付费+iframe扣费抑制”的事务1，不按公式变量/注册/药水包装拆分。算法可部分减伤或降0，不生产免控语义。阈值不满足不结算；cost可0，浮点除0与后续比较需保留源码事实，不声称NaN安全全覆盖。无mana或过大伤害时WaterMage仅乘.75，也不是完全免疫。先魔火armor加回再bubble，实际顺序已核。',
 '不能把护盾存在或damage降0标成Boss拒控；付款、免伤和灰字回执需各自以最终结果为准。冷却/iframe结算抑制不等于文字/嗡鸣节流。',
 '包含方法及实际mod/effect/glyph注册已读；applyConfigPotion和ManaUtil/getMana/removeMana是已存在外部Ars API调用，本条不新增研究助手保留Ars来源、不声称该依赖版本内部事务或控制应用成功；无正式修改/游戏/像素或网络验收。','native_resource_damage_settlement')
k='ars-elemental-native-mana-bubble-harmful-applicability-refusal-and-asymmetric-payment';ks.append(k)
record(k,r,common+[f('event/DamageEvents.java',274,297),f('datagen/AETagsProvider.java',359,374),res('src/generated/resources/data/ars_elemental/tags/mob_effect/manabubble_blacklist.json')],
 '相同已注册bubble状态，独立原生MobEffectEvent.Applicable→DamageEvents.statusProtect：effect category HARMFUL才读真实registry blacklist，命中holder返回不拒绝；否则random nextInt(10)==0才取得mana，要求current>=2*配置cost，实际removeMana为该值一半，再设置DO_NOT_APPLY。nonharmful分支单独比较MAGIC_FIRE.getDelegate并直接DO_NOT_APPLY。实际生成tag列levitation、hymn_of_order、summoning_sickness。',
 '原生状态接纳的付款拒绝producer1，与伤害减额producer分开是不同最终接纳事件/语义，不把共享glyph/类重复计数。门槛700但实际扣350（默认），不将注释“消耗”理解成完全相同数额；没有每目标时间节流，重复应用可重复随机/扣费。tag成员用holder身份==，本次不据此推测跨registry运行问题。魔火特殊分支只有nonharmful时可达，需实际该effect category才能判断，不称无条件火抗。',
 '明确拒控应由DO_NOT_APPLY这种最终接纳决定点生产；同一状态下减伤、负面效果拒绝和特殊元素保护不能共用hurtfalse推导。服务端显式拒绝理由优于客户端按外观猜测。',
 '完整statusProtect及状态获得/启用/生成tag已读，文件Git blob固定；无额外去查助手保留项目，未核当前实例数据包覆盖或其他listener后续改写结果，不声称生产环境最终免控已通过。','native_effect_admission_refusal')
k='ars-elemental-native-sonic-denial-before-actor-validation-and-independent-return-ray';ks.append(k)
record(k,r,[w('event/ShieldEvents.java'),w('ArsElemental.java'),f('registry/ModRegistry.java',86,86),res('src/generated/resources/data/ars_elemental/enchantment/mirror_shield.json')],
 '真实事件subscriber onSonicImpact要求ServerLevel玩家，offhand EnchantersShield+blocking、mirror holder存在、等级*.25随机成功、有source position且SONIC_BOOM、有mana capability，再用水平source→player与视角dot<0门进入reflectSonicBoom。该方法先cancel原伤害，再验证source.entity是Living；有效才eye→原source ray沿途sendParticles SONIC_BOOM、播放原版WARDEN_SONIC_BOOM、独立hurt10并按抗击退推送，最后扣150mana/盾cooldown/stopUsing。真实生成enchant maxlevel3/offhand/shield tag。',
 '一个无投射物的原生声波拒绝→独立反击射线/声音结算producer1，和普通弹体反速包装合并0（同类onBlock没有另计）。cancel在actor验证前，缺actor仍拒伤但无反击/付款/停止举盾。只检查cap存在，不核余额能付；反击hurt返回值忽略仍推送、扣费、播放声光，反击声光不可证明对方已掉血。source同类可导致再次进入他人的反射政策，本次未运行/未称递归安全。maxlevel3正常数据不达onBlock的homing level>3分支；不把不可自然获得高等级分支算新实现。',
 '拒绝与反击/声音资格分开核查，Boss嗡声应由被拒绝事实而非新反击hurt结果触发。现有原版音源可研究复用，不能据静态认定嗡声听感适配。',
 '完整ShieldEvents和实际subscriber、mod与enchant资源已读；无game/TCP/像素/听验。外部EnchantersShield/Capability内部只作已调用接口边界，本条不计算库或其包装，不制作模型。','native_nonprojectile_refusal_receipt')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'ars-elemental-paid-bubble-and-sonic-return','credited_chains':ks,'rationale':'damage settlement, independent effect-admission final refusal, and native nonprojectile sonic cancellation with separate counterattack =3; shared registry/glyph/API wrappers, random constants, onBlock projectile reflection variants zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
