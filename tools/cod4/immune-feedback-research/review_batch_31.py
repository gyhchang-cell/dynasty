"""Concrete Relics native control denial, temporary invulnerability, effect feedback and dodge."""
from ledger import B,O,record,verify
import json
r='Octo-Studios/relics';p='src/main/java/it/hurts/sskirillss/relics/';g=p+'items/relics/back/GhostlyMantleItem.java';shield=p+'items/relics/ShieldOfRetaliationItem.java';keys=[]
def whole(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
shared=[whole(p+'Relics.java'),whole(p+'init/RelicsMobEffects.java'),(p+'init/RelicsItems.java',76,82),whole(p+'items/relics/base/WearableRelicItem.java'),(p+'utils/EntityUtils.java',216,239),(p+'api/relics/data/AbilityData.java',268,274)]
def add(k,refs,chain,obs,lesson):
 record(k,r,refs+shared,chain,obs,lesson,'固定da846fcb3223e88d7c926b4478506b3089caff51。相关完整方法及实际native原生调用/注册上下文全文已读；源Git blob核验；资源注册完整固定commit网页已观察见relics-registration-web-primary.json，资源原始字节未下载/hash。未运行/编译上游，不证明TCP、实际画面/声音/Boss覆盖。普通阴阳无灰字要求，守卫0转入。','concrete_native_control_and_combat_feedback');keys.append(k)
add('relics-native-tremor-attacker-disable-versus-victim-immunity',[(g,217,366),whole(p+'entities/GhostlyFogEntity.java'),(p+'init/RelicsEntities.java',119,127),whole(p+'utils/TargetingUtils.java'),whole(p+'effects/TremorEffect.java'),(p+'mixin/LivingEntityMixin.java',76,85)],
 '原生已注册GhostlyMantle Curio tick→tickFogTrail按移动/地面生成真实Fog；server原生Fog.tick对真实living target尝试TREMOR，TargetingUtils返回实际addEffect。Tremor静态事件subscriber在原生EntityInvulnerabilityCheck读source.directEntity的TREMOR，设受害者invulnerable；物品起用/挖掘及client真实interaction/hand render分别执行门与手抖。',
 '此免疫来自攻击者被禁用而非目标Boss体质，不能把最终invulnerable一律标Boss Immune。只认direct LivingEntity，投射物owner不会被该式认定；original invulnerability为真直接return。TREMOR实际注册factory=StunEffect而非TremorEffect，静态subscriber仍按TREMOR键检查；STUN/PARALYSIS才在aiStep混入置immobile，因此不从类名推断TREMOR已冻结AI/身体。Fog状态接纳返回未读，空气扣减和IN_WALL伤害可独立发生；曝光UUID pair去重只挡统计/经验，不挡状态/空气/伤害/反馈，支持0额外。',
 '服务端Immune原因必须区分施法者/攻击者被禁、队伍资格、目标真正拒控；装饰手抖不是目标已受控或伤害已拒的证明。')
add('relics-native-lethal-escape-grants-followup-incoming-immunity',[(g,217,276),(g,570,617),whole(p+'effects/ImmortalityEffect.java'),whole(p+'effects/FlightEffect.java'),whole(p+'utils/TargetingUtils.java')],
 '真实server LivingDeath遍历装备GHOSTLY_MANTLE且能力可用/stack逃生CD0→cancel死亡，至少1HP/清deathTime，grant有期限FLIGHT和IMMORTALITY并设置stackCD；随后原生LivingIncomingDamage只要持IMMORTALITY即取消。原生穿戴tick推进CD；Flight实体post tick按原状态tag切换飞行能力并在效果结束关飞行。',
 '不是把原伤害false当无后果：死亡已触发逃生模式，后续拒伤由实际effect consumer。两个grant的addEffect返回均未查，不能声称不可被其它mod否决；Immortality没bypass来源例外。CD在每stack且只穿戴推进；脱下不撤现有effect，换stack不共享。Flight只保留hadEffect布尔不保存原mayfly来源，退出非创/观察时直接关，可能影响其它飞行赋予者。reprisal按攻击者UUID mark，完整damageModifiers消费在本批支持，不追加来源变体信用。',
 '临时免疫要有明确授予/期限/后续拒绝链；只做灰字不应额外授予保命、飞行或改玩家相机。普通体质政策独立。')
add('relics-native-status-receipt-target-membership-to-stun-render-policy',[(shield,491,517),(shield,755,870),whole(p+'utils/TargetingUtils.java'),whole(p+'mixin/LivingEntityMixin.java'),whole(p+'network/packets/PacketSyncEntityEffects.java'),whole(p+'network/NetworkHandler.java'),whole(p+'effects/StunEffect.java'),whole(p+'client/gui/layers/StunEffectLayer.java'),(p+'client/handlers/ClientHandler.java',43,44),(p+'client/handlers/ClientHandler.java',230,239)],
 '真实Shield拒伤后stunNearbyTargets实际addEffect为真才记stunned；LivingEntity原生onEffectAdded/Updated/Removed server TAIL生产NBT+action+整数entityId→已注册S2C排队→当前world查LivingEntity→add/remove效果；真实RenderLiving.Pre读STUN与alive，按实际height/width/原生tick提交头顶星，GUI注册stun layer读本机effect duration渐淡。',
 '本条研究具体战斗效果归属/增删同步→目标render成员资格，非通用网络库。只tracking而非self，没有join开始追踪补全证据；无UUID/维度/seq/延迟去重，missing entity丢包。Action未知ordinal映射ZERO即ADD；client UPDATE仍addEffect，remove后旧ADD可能复活视觉，未复现实验。目标dead/dying不画星；nativeFirstPerson无专门星分支，焦点body是否进入事件取决实际渲染；层只nativehasEffect，alpha按duration，不能据FULL_BRIGHT/cutout推断遮挡一定正确。星/FOV/手操作/GUI是同状态反馈家族合计1，几何/图案支持0，不制作任何资产。',
 'Boss世界文字应绑定权威目标及短生命周期，迟包/丢目标/换维需安全处理；无灰字的状态视觉不能冒充Boss文字需求，也不以静态渲染调用证明观感。')
add('relics-native-distortion-damage-denial-retaliatory-disorientation',[(p+'items/relics/back/GlitchyMantleItem.java',334,338),(p+'items/relics/back/GlitchyMantleItem.java',474,551),whole(p+'effects/GlitchEffect.java'),whole(p+'utils/TargetingUtils.java')],
 '已注册GlitchyMantle真实LivingIncomingDamage确定实际living攻击者或projectile owner→能力/反制canHarm资格/概率→cancel并给受害者10tickGLITCH；rank disorientation实际对ServerPlayer攻击者同位teleport转朝向、所有living改body/head/yaw，Mob清target停导航再走开；后续单独IN_WALL+启用phase分支取消。',
 '拒伤同时可生产攻击者控制，不能称“Boss不受控制且双方无位移/朝向副作用”。canHarm不允反制则连防御本身都不触发，不等于来源无伤；无明确attacker环境来源不进入随机防御，IN_WALL另判。GlitchEffect类只有标记，未完整研究shader消费者，不声称画面已出现；fall同mode分支已读，仅乘伤/0伤模板支持0。IN_WALL常量门并本条，不另计。',
 '最小Immune反馈不得顺便对攻击者teleport/改镜头/清AI；只有实际拒绝的语义点能发该原因，不能把随机闪避标成Boss控制免疫。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'relics-native-control-batch31','credited_chains':keys,'rationale':'4个独立真实位点：来源TREMOR禁攻；原生死亡逃生后grant免疫；STUN增删目标回执及实际渲染成员资格；随机拒伤伴攻击者转向反制。不同效果键/包装/序列化/粒子常量不重复计，Fog曝光仅统计去重0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
