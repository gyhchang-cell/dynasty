"""Main semantic decisions for helper010-012 candidates; support is not automatically promoted."""
from ledger import B,O,record,verify
import json,hashlib
r='TeamLapen/Werewolves';p='src/main/java/de/teamlapen/werewolves/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
refs=[f('WerewolvesMod.java',72,110),f('WerewolvesMod.java',154,164),f('entities/player/ModPlayerEventHandler.java',205,228),f('entities/player/werewolf/WerewolfPlayer.java',79,81),f('entities/player/werewolf/WerewolfPlayer.java',124,162),f('entities/player/werewolf/WerewolfPlayer.java',536,539)]
k='werewolves-native-transformed-skill-and-source-tag-conjunctive-final-denial'
record(k,r,refs,'真实@Mod构造挂setup，setup在NeoForge EVENT_BUS注册ModPlayerEventHandler；原生LivingIncomingDamage完整方法仅Player且Helper.isWerewolf进入，取玩家附件/skillHandler。伤源WEREWOLF_FUR_IMMUNE标签、当前form.isTransformed和WOLF_PAWN技能三者同时才cancel。后续Survivalist概率分支仍会执行，不是return。',
 '计1独立确定性最终拒伤生产点，按实际状态/技能/伤源合取而非所有狼人/Boss泛免。不是Fall事件改距离/倍率的包装；Fall另有WolfPawn减距减倍率但不据此推成绝对免摔。即使已cancel仍进入后续roll，没有此方法内清除cancel，不能把附带RNG当独立免疫回执。标签成员未取得，不把名字扩成具体火/落伤清单。',
 'Boss拒控需要权威理由合取与控制类型，而非身体状态/伤害来源泛化；拒伤最终生产点和闪避、免控分开，不给普通体质增加灰字。',
 '事件完整方法、注册setup、附件get/form切换及同步调用全文已读；Helper.isWerewolf、form enum、技能可达性及该版本Vampirism技能内部未固定缓存，保留API谓词契约，不借另一版本补实现。无文字/音/闪光/运行通过结论。','native_conjunctive_form_skill_source_final_damage_denial')
k2='werewolves-native-motion-two-stage-dodge-with-failed-arrow-roll-fallback'
record(k2,r,refs,'同一原生Incoming方法后半段，当前form精确SURVIVALIST才参与：速度lengthSqr>0.01、ARROW_AWARENESS技能、伤源精确ARROW且首次随机<0.4则cancel；否则满足sprinting/非null source.entity/MOVEMENT_TACTICS时第二次随机与配置+refinement之和比较cancel。',
 '计1独立随机接纳政策，区别前一确定性标签合取门；两个roll/两个技能/配置与精修常量不拆。else if绑定整个第一条件，包括随机比较，因此箭roll失败也可走sprint第二roll；第二门不限定arrow，只要求非null伤源实体。limit无本地clamp，不推定默认概率或独立随机分布实测。第一确定性门已cancel也未短路，此随机分支可能多消耗RNG但并非额外受击回执。',
 '反馈按最终权威拒绝原因发送一次，不在每个候选roll先发；确定免控和随机闪避必须保持不同语义。',
 '完整含方法与两门上下文已读。配置数值、精修内部、技能获取没有全部展开；不声称具体合成概率、两端动画/网络验收。仅静态最终取消实现，没有Boss专用反馈。','native_motion_conditioned_probabilistic_damage_admission')
r='CoFH/RedstoneArsenal';p='src/main/java/cofh/redstonearsenal/'
k3='rsa-native-paid-shield-repel-precedes-final-use-energy-admission'
record(k3,r,[f('RedstoneArsenal.java',48,80),f('RedstoneArsenal.java',83,114),f('init/registries/ModItems.java',40,72),w('common/item/FluxShieldItem.java'),w('common/item/IFluxItem.java'),w('common/item/IMultiModeFluxItem.java')],
 '真实mod注册FluxShield物品/能力。原生Item.use empowered时先repel，只有useEnergy(true,living)成功才按范围排creative/spectator并对Living调用nativeknockback、其他实体normalize后setDeltaMovement/hasImpulse；repel结束后use再hasEnergy(true)，不足返回FAIL，够交父盾use。onUseTick不足releaseUsingItem；原生capability.onBlock也复用repel，不另计。',
 '计1：实际控制副作用先付费执行，最终持盾准入随后再次验剩余能量的不同门顺序。普通非creative、提取成功且初始恰2000示例可先repel再FAIL，不能用FAIL当控制未发生或Boss拒控。Living原生knockback仍可有外部抗性，非Living走另一直接速度路径；本类没有世界side门，不声称无预测重复。付费不根据目标数量/实际移动成功/伤害回执；无目标也可花费。与MPS hurt true才目标addVelocity、SpellEnginehurt忽略bool后偏移冲量不同，此处根本未调用hurt。',
 'Boss控制门应包住所有实际控制路径，反馈不能根据物品use结果反推；统一语义原因需要位于真正副作用前，尝试成本和提示节流分开。',
 'FluxShield/IFlux/IMultiMode全文和注册已读；外部IEnergyContainerItem实际提取/Utils creative实现、ShieldItemCoFH最终父use未展开，限定接口提取成功假设，不把示例当实测。canBlock特殊flux扩展缺CoFH最终消费者，本轮保留支持0。','native_control_side_effect_precedes_item_use_admission')
r='stal111/Forbidden-Arcanus';p='neoforge/src/main/java/com/stal111/forbidden_arcanus/'
k4='forbiddenarcanus-native-capture-refusal-versus-interaction-cancel-and-release-failure-settlement'
record(k4,r,[w('ForbiddenArcanus.java'),w('ModEventHandler.java'),f('common/event/PlayerEvents.java',59,68),f('core/init/ModItems.java',79,81),w('common/item/QuantumCatcherItem.java')],
 '真实mod EventHandler注册PlayerEvents，原生EntityInteract对Living+QuantumCatcher无条件cancel事件并把物品返回写cancellationResult。物品先算成本，invalid(类型blacklist或不存活)/已有storage返回PASS，预算不足FAIL；服务端合格时写StoredEntity、discard目标再consume。单stack写原物品，多stack分出普通QuantumCatcher添加/掉落；useOn释放先解析与可替代位置，addFreshEntity结果忽略即清storage并返回true。',
 '整个捕获拒绝—事件消费—存储释放结算整链合并计1，普通/染色/Boss tag名与包装0。与EnderIO不可变Boss硬门+可覆盖名单+动作栏理由、PNC实例来源再验不同：此处PASS仍被外层cancel，不能将事件cancel当实际捕获拒控，也不能用release true/声音证明spawn成功。放出位置/解析失败返回false保留storage，但addFreshEntity false不会保留；capture多stack换成普通item可能丢染色/专用类型。sound的release布尔捕获true/放出false，依实际分支不按资源名解释。',
 'Boss拒控回执只能在具体最终拒绝原因处产生；外层消费输入不等于免疫。目标身份应在移除前确定，跨世界/实体生命周期和失败结算独立于声音。',
 '上述完整物品和注册/事件方法已读。StoredEntity/EssenceCost内部、blacklist实际成员及Valhelsia注册内部未全读，不声称具体Boss清单、跨维序列化保真或付款原子性。此为实际具体游戏策略非通用注册API计数，无运行证明。','native_capture_denial_and_interaction_consumption_semantics')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch122-main-helper010-012-final-semantic-review','credited_chains':[k,k2,k3,k4],'rationale':'Two separate deterministic vs two-stage-random final refusal production sites; paid native repel before final use-admission; capture interaction-consumption and release-failure settlement. Wrapper dispatch, same policy names/variants and source counts0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
b=O/'helpers/herschel-immune'
report={'main_count_before':365,'new_credit':4,'candidate_decisions':{'herschel-010-01':{'credit':1,'id':k},'herschel-010-02':{'credit':1,'id':k2},'herschel-011-01':{'credit':0,'decision':'support; special capability canBlock source extension and onBlock fully read, but external native final shield dispatcher/IShieldItem parent policy missing. Cannot treat available capability as proven incoming-damage refusal.'},'herschel-011-02':{'credit':1,'id':k3},'herschel-011-03':{'credit':0,'decision':'support: full onLeftClick read, eligibility-hit not hurt success; pre-hurt native knockback is related but external native input/C2S dispatch missing and overlaps existing pre/post damage-independent impulse settlement family. Do not credit filters/constants separately.'},'herschel-012-01':{'credit':1,'id':k4}},'helper_support_rows':'all remain0; this pass did not independently re-read all seven support rows; not claimed fully reviewed','helper_file_sha256':{n:hashlib.sha256((b/f'batch-{n}.json').read_bytes()).hexdigest() for n in ['010','011','012']},'method_file_download_count_credit':0,'production_changed':False,'game_started':False,'ordinary_yinyang_gray_text_requirement':False}
(O/'HERSCHEL-010-012-REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');verify()
