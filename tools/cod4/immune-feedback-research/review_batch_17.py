from ledger import record,verify,B,O
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';root=B/'sources'/r.replace('/','__')
def a(x,s,e):return(p+x,s,e)
def w(x):return a(x,1,len((root/(p+x)).read_text().splitlines()))
def add(key,refs,chain,obs,lesson,category='boss_rejection_semantics'):
 record(key,r,refs,chain,obs,lesson,'固定本地提交全文方法静态观察，未运行/编译/验证像素或声。辅助路径/序列化包装不额外计数；普通体质不新增灰字要求。',category)
add('goety-bulwark-per-victim-charge-consumption-cooldown',[w('common/magic/spells/BulwarkSpell.java'),a('common/events/ModEvents.java',656,949),a('common/events/ModEvents.java',991,1088),a('utils/MiscCapHelper.java',42,100),a('utils/MiscCapHelper.java',355,360),a('common/capabilities/misc/MiscImp.java',30,79),w('common/network/server/SPlayPlayerSoundPacket.java')],
 'Bulwark原生SpellResult给自己或盟友护盾数和持续时间→LivingAttack服务端非bypass门→按受击者cap的shieldCool控制breakShield/可选按伤害多扣/反击→LivingEffects每tick减少shieldCool并管理护盾到期；扣盾后给玩家发原版SHIELD_BREAK个人声音或非玩家原位声音。',
 '有盾且非bypass就取消攻击，即便shieldCool>0也挡；仅cool<=0扣盾、播声和反推攻击者，随后设10tick。这是每受击者的共享冷却，不按攻击者/伤害原因；额外扣盾循环每次都播声，可在同tick重复多声，且breakShield直接--可成负数。shieldCool置10不立即发包，但扣盾已先发旧cool；下一tick减少再同步。效果到期另有WALL_DISAPPEAR提示。非Boss专属，不是灰字实现。',
 '可借鉴每目标限频与“效果持续挡、反馈少发”分离；必须给单次多层消耗聚合回执，否则名义冷却仍能同tick刷声音。','per_target_throttle')
add('goety-no-knockback-single-use-native-event-stamp',[a('common/events/ModEvents.java',989,1088),a('common/events/ModEvents.java',1465,1479),w('utils/NoKnockBackDamageSource.java'),a('utils/ModDamageSource.java',107,109),a('utils/ModDamageSource.java',269,271),w('common/magic/spells/TelekinesisSpell.java')],
 '原生Telekinesis窒息伤害→ModDamageSource.choke→NoKnockBackDamageSource→LivingAttack服务端记录victim.tickCount→LivingKnockBack读取并在相隔<=1tick取消、无论新旧都removeTag。',
 '一次性关联只存tick不是事件ID。相邻tick两个不同攻击可能串用同一标记，第一次knockback会消费，后续同tick可漏；没有>=0下界，保存重开时若旧tick大于当前tick也可能被<=1接受。Attack handler即便此前其他分支取消仍会继续写标记。只覆盖ForgeKnockBack，MobUtil直接setDeltaMovement不经过该事件。无灰字或嗡鸣。',
 '拒控去重应有事件身份与清理策略；仅时间戳可做短窗口，不能当可靠攻击关联，游戏重载须处理时钟重置。','control_immunity_semantics')
add('goety-effect-applicability-state-conflict-and-boss-policy',[a('common/events/PotionEvents.java',1030,1094),a('common/events/PotionEvents.java',1097,1134),w('common/effects/HysteriaEffect.java'),w('common/effects/DoomEffect.java')],
 'Forge注册Applicable完整方法在状态真正生效前按当前effect/装备/实体属性/Boss或维度能力条件设置DENY；Added对冲突状态做反向清理，Hysteria/Doom效果tick分别处理伤害/显示。',
 'BURN_HEX拒FIRE_RESISTANCE、ACID_VENOM拒POISON，SNOW_SKIN或冻结免疫标签拒FREEZING；加SNOW_SKIN又移除已有FREEZING，形成先后顺序都覆盖的状态冲突。Boss标签拒HYSTERIA；DOOM还拒不能换维度目标；BUSTED拒无护甲属性或护甲<=0目标。各分支是同一Applicable策略族，未按每个effect常量拆credit。DENY分支无拒绝文字/声音，Hysteria已被强制挂入时的tick伤害并不因Boss视觉门而跳过，不能把“粒子不显示”当免伤。',
 '实际免疫政策应在应用前确切生产；状态互斥需处理应用次序；Boss身份分支与“当前没有可削弱属性”不是同一反馈原因。','control_immunity_semantics')
add('goety-doom-expiry-final-execution-revalidation',[a('common/events/PotionEvents.java',1175,1207),w('common/effects/DoomEffect.java')],
 'MobEffect.Expired消费实际DOOM实例→最终检查可换维度且非Boss→以(amp+1)*5%最大HP为斩杀线→原生hurt(DOOM,maxHP*20)；DoomEffect渲染粒子入口另检查相同身份。',
 '即使状态通过命令/兼容途径挂入Boss，过期时仍独立重验Boss/维度能力，禁止终结伤害；这是最终破坏操作前守卫，区别于Applicable入口和装饰粒子门。不检查hurt返回便结束，不能证明成功斩杀；没有服务端side外层，事件来源/分发顺序未运行确认。没有给被免斩杀目标发字或声；boss粒子过滤不是拒控回执。',
 '不能只在初次挂状态时判免疫；延迟结算时需再验同目标与政策，防目标转变或旁路状态导致Boss被终结。','control_immunity_semantics')
add('goety-void-status-sound-lifecycle-and-position-snapshot',[a('common/events/PotionEvents.java',1097,1207),w('common/network/server/SPlayWorldSoundPacket.java'),a('common/network/ModNetwork.java',112,127)],
 'VOID_TOUCHED Added首次状态门→服务端tracking+self发送ACTIVATE，Remove/Expired分别发DEACTIVATE→SPlayWorldSoundPacket编码BlockPos/soundID/vol/pitch→客户端enqueue、当前ClientLevel中playLocalSound。',
 '声音用出生BlockPos快照，无目标ID/UUID/维度/生命周期票据，移动后不跟随。Add的!hasEffect依事件时序，不可仅静态断言首添加必播；Remove不检查event已取消仍可能发退出声，Expire也有退出声路径，未见两来源去重。tracking+self约束发送范围但消息延迟跨世界后仍可在新世界同坐标播放；无距离/finite值复验/节流。该声是状态生命周期提示，不是Boss免疫嗡鸣。',
 '实际文字/声回执需绑定事件和目标生命周期；状态移除尝试、成功移除及自然到期不可不加区分重复通知。','feedback_lifecycle')
add('goety-bulwark-state-receiver-side-and-capability-validation',[w('common/capabilities/misc/MiscCapUpdatePacket.java'),a('utils/MiscCapHelper.java',281,360),a('common/network/ModNetwork.java',42,42),w('common/magic/spells/BulwarkSpell.java')],
 '护盾状态实际setShields→sendMiscUpdatePacket→tracking+self实体ID+NBT→注册MiscCapUpdatePacket.decode→enqueue后显式PLAY_TO_CLIENT门→ClientLevel/实体存在/capability可用→按键load具体护盾/冻结/声音计时状态。',
 '这是实际战斗状态收包的方向与实体能力校验，不是泛用网络注册。方向在入队后检查；实体缺失丢，不缓存。NBT可能null而load未做null检查；只IntegerID缺维度/UUID或epoch，可能误绑新世界同ID。load只赋存在键，省略的正值字段可能留旧状态，如enchanterTime/noHealTime/sunscreen；包无服务器序号，旧包覆盖新值。只是状态同步，不携单次Boss拒绝原因。',
 '收包方向/能力检查不足以证明目标身份正确；Boss字反馈要补同目标、当前世界、序号及过期校验，显式区分快照省略和清零。','game_feedback_receive_validation')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'goety-native-feedback-policies-batch17','credited_chains':['goety-bulwark-per-victim-charge-consumption-cooldown','goety-no-knockback-single-use-native-event-stamp','goety-effect-applicability-state-conflict-and-boss-policy','goety-doom-expiry-final-execution-revalidation','goety-void-status-sound-lifecycle-and-position-snapshot','goety-bulwark-state-receiver-side-and-capability-validation'],'rationale':'每目标消耗限频、一次性击退关联、应用前冲突政策、过期最终处决守卫、状态音生命周期、实际战斗状态S2C方向/实体能力校验是独立行为。所有effect常量分支合并1，不按getter/codec/声音包装计数；包校验与扣盾限频有不同最终决策和状态副作用。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
