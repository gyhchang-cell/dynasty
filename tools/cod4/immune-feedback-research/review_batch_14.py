from ledger import record,verify,B,O
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';root=B/'sources'/r.replace('/','__')
def a(x,s,e):return (p+x,s,e)
def w(x):return a(x,1,len((root/(p+x)).read_text().splitlines()))
record('goety-empowered-monolith-native-rejection-shield-receipt',r,[a('common/entities/hostile/cultists/Heresiarch.java',258,265),a('common/entities/hostile/cultists/Heresiarch.java',472,549),a('common/entities/neutral/AbstractObsidianMonolith.java',173,184),a('common/entities/neutral/AbstractObsidianMonolith.java',210,252),a('common/entities/neutral/AbstractObsidianMonolith.java',358,468),a('common/entities/neutral/AbstractMonolith.java',99,137),w('common/entities/hostile/servants/ObsidianMonolith.java'),w('client/render/ObsidianMonolithRenderer.java'),w('client/render/AbstractMonolithRenderer.java'),a('init/ClientInitEvents.java',568,568),a('common/entities/ModEntityType.java',461,466),a('common/entities/ModEntityType.java',646,649),a('Goety.java',144,164)],
 '注册的Heresiarch原生服务端aiStep寻找leader或范围内ObsidianMonolith，保存对象引用，后续每tick续empowered=10；注册的ObsidianMonolith继承aiStep/hurt，非emerging且empowered的非bypass受击→broadcastEntityEvent6+原版熄火声→false；客户端handleEntityEvent6设置shieldTime10→aiStep递减→实际注册ObsidianMonolithRenderer调用OMShieldLayer→energySwirl提交。生产、拒绝、事件、衰减、声与层包装合并一条。',
 'IS_EXPLOSION/IS_FIRE在empowered分支之前返回false，没有同一护层回执；BYPASSES_INVULNERABILITY豁免保护。attackable/canBeSeenAsEnemy在empowered时也false，可能先阻止特定正常瞄准/攻击入口，不能称所有尝试都到hurt。IN_WALL的destroyBlocksTick20是挖墙计时而非回执节流；每次命中保护分支都会播LAVA_EXTINGUISH音量1音调0.5及重置shieldTime，没有单目标/事件序号节流。shieldTime按tick衰减非按frame；层贴合实体当前变换放大1.05/1.025，局部变量alpha其实传给RGB，最终alpha为1，不是透明渐隐；未见文本。Heresiarch引用非UUID重查，保护续期至多10tick，但此链未为关联对象失活定义全面清理；同类Heretic/Servant续保护入口不另计。',
 '可借鉴服务端明确拒绝点→原生实体事件→实体局部限时反馈，并保留拒绝原因差别；实际Boss灰字仍需目标身份、明确原因和节流，不能把范围/火免伤或普通体质混进。沿用合适原版声是可行素材策略，静态不能决定此音是否符合COD4嗡鸣。',
 '仅静态完整目标方法与自有调用链；没有运行声音/像素/包顺序验收。模型setupAnim/几何和贴图美术未作为新资产研究或观感通过；本条记实际已接活的拒绝反馈，不等于已有灰字。','boss_rejection_semantics')
record('goety-native-stun-applicability-denial-versus-explosion-push',r,[w('common/events/StunnedEvents.java'),w('common/magic/spells/geomancy/TemblorClapSpell.java'),w('utils/SpellExplosion.java'),a('utils/ExplosionUtil.java',14,16),a('utils/ExplosionUtil.java',52,64),a('utils/MobUtil.java',302,332),a('init/ModTags.java',189,190),a('init/ModTags.java',233,239),a('common/effects/GoetyEffects.java',14,22),a('common/effects/GoetyEffects.java',145,157),a('Goety.java',200,205),a('Goety.java',237,240),w('common/network/server/SRemoveEffectPacket.java'),a('common/network/ModNetwork.java',86,95),a('common/network/ModNetwork.java',123,129)],
 'TemblorClapSpell.SpellResult(ServerLevel)实际产生范围SpellExplosion，构造器经深度限制/范围/遮挡/友伤筛选调用匿名explodeHurt；先super伤害与push，再addEffect(STUNNED3秒)。已注册Forge StunnedEvents在Applicable对STUNNED+unstunnable实体标签返回DENY；其余原生attack/use/target事件通过共同isStunned取消已中晕实体行为。死亡时服务端移除两effect并sendToALL SRemoveEffectPacket，客户端enqueue按实体ID/效果ID删除；注册/编码/清理包装不加数。',
 '拒晕是明确Applicable DENY，而不是血量是否变化；Temblor不检查addEffect成功且super.explodeHurt的push在hurt成功判断之外，拒晕不能推出无伤或纹丝不动。MobUtil.push按击退抗性缩放整个(原速度+增量)，并设置hasImpulse，非LivingKnockBackEvent，所以仅TANGLED的onKnockback取消不能证明此push被挡。拒晕分支无专门文字、微光、嗡声或限频；范围smash粒子/爆炸声不论单体是否拒晕都可发生。普通已中晕行为取消与拒晕是两个语义，不能把取消use包装各计一条。死亡清理包发ALL且仅实体ID，在另维度同ID可能误命中，客户端实体缺失直接丢，不含维度/UUID/代际。第三方stun兼容靠descriptionId.contains字符串，未证明实际格式命中。',
 'Boss控制免疫须在明确拒绝处生成原因回执；状态未加上不保证击退/动作没发生。声音/文字节流应随拒绝事件独立而不能用AOE总声或已有状态清理包代替。type9普通体质不用追加Boss灰字。',
 '读取了实际施法结果、范围伤害、push和拒绝监听的完整方法；未展开整个施法物品选择系统或运行原生施法。unstunnable标签资源不在本地Java缓存，未确认具体Boss成员，不能宣称某Boss已覆盖；静态记录机制及明确缺口。泛用网络和深度保护仅链路辅助0额外计数。','control_immunity_semantics')
f=O/'candidates.json';rows=json.loads(f.read_text())
for x in rows:
 if x['id']=='goety-monolith-native-feedback-pending':
  x.update(status='historical_candidate_resolved_into_reviewed_chain',resolved_into='goety-empowered-monolith-native-rejection-shield-receipt',remaining_for_promotion='已补生产及注册，计数只在reviewed.json中一次；此候选历史保留0。')
f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
verify()
