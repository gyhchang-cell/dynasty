from ledger import record,verify,B,O
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';root=B/'sources'/r.replace('/','__')
def a(x,s,e):return(p+x,s,e)
def w(x):return a(x,1,len((root/(p+x)).read_text().splitlines()))
def add(key,refs,chain,obs,lesson,limits='固定提交本地源码静态研究；未运行/编译，不证明观感、声音或TCP同步。标签资源未取得，不虚构具体Boss成员。',category='control_immunity_semantics'):
 record(key,r,refs,chain,obs,lesson,limits,category)
add('goety-banish-preteleport-eligibility-and-cancellable-receipt',[w('common/magic/spells/void_spells/BanishSpell.java'),w('api/magic/ITouchSpell.java'),a('api/items/magic/IWand.java',72,95),a('api/magic/ISpell.java',262,268),a('api/magic/ISpell.java',326,332),a('common/items/magic/DarkWand.java',726,757),a('utils/MobUtil.java',379,393)],
 'DarkWand.canCastTouch→IWand.cannotCast→Banish.conditionsMet：原生视线entityResult查询→目标最大血量/banish标签/配置黑名单拒绝，后经ForgeEnderTeleport取消门；通过才允许touchResult随机传送尝试。',
 '拒绝目标资格时播放SPELL_FAIL并false，Forge传送事件取消则false无该提示；两种失败不能等同。conditionsMet射线找的目标与实际touchResult参数并非同一身份绑定；读取完整touchResult，传送失败只是range次尝试结束，stopRiding在每次尝试前，不能把所有最终未传送称免疫且纹丝不动。事件预检坐标给caster位置，实际随机传送另坐标，未消费预检事件修改后的目标坐标。没有灰字或逐目标限频。',
 '免控回执挂到明确资格拒绝，保留第三方取消与无落点的不同原因；用实际被操作目标校验资格，避免射线预检目标与交互目标脱节。')
add('goety-telekinesis-target-filter-and-native-mob-override',[w('common/magic/spells/TelekinesisSpell.java'),a('utils/MobUtil.java',379,393),a('utils/MobUtil.java',715,752),a('utils/MobUtil.java',302,332)],
 'Telekinesis.startSpell清victim→findVictim→getSingleTarget的原生视线/AABB候选predicate→标签/配置/创造旁观及火球类型排除；SpellResult随后通过MobUtil.push操作保存的victim。',
 '玩家查询predicate排除TELEKINESIS_IMMUNE/黑名单和AbstractHurtingProjectile，未产生拒绝字/声；Mob施法者却直接用mob.getTarget覆盖已筛target，存在独立绕过边界。血量上限条件误查this.victim而非新target；startSpell刚清null所以首次获取不会按newtarget最大HP拒绝。体积比较也只是包围一个旧victim判断，不能宣称大Boss必免控。固定全文可见实际push/撞墙hurt/窒息附加不是仅设置一个状态。',
 '目标筛选必须覆盖所有原生施法入口并检查同一目标；灰字应来自最终明确拒绝，不能由“未找到目标”笼统推断。')
add('goety-telekinesis-held-target-termination-lifecycle',[w('common/magic/spells/TelekinesisSpell.java')],
 '持续EverCharge施法使用本技能conditionsMet→受击/持有目标距离门，startSpell/stopSpell管理本技能victim，SpellResult在无目标时再次findVictim。',
 'caster.hurtTime>0立即false；已有victim超range会置null并false；stopSpell清victim并给玩家5秒技能冷却及SE更新。保存的是Entity对象，没有在这些完整方法中验证alive/removed/维度一致；hurt拒绝时本方法未主动清victim，要依stop调用。该5秒是停止施法冷却，不是Boss免疫文字去重。技能碰撞后hurt成功才播放大跌落声。生命周期与目标资格筛选是独立实际行为位点，不把start/stop包装各计。',
 '跟随实体反馈需要明确丢目标/换维度/移除回收；分开技能冷却与目标回执冷却，生命周期不能靠异常捕获代替。')
add('goety-entangle-final-control-gate-before-position-mutation',[w('common/entities/projectiles/TangleEntity.java'),w('common/entities/projectiles/EntangleVines.java'),w('common/magic/spells/wild/EntanglingSpell.java'),w('common/network/server/SRepositionPacket.java')],
 'EntanglingSpell原生生成EntangleVines→服务端tick activeTick→findTarget→TangleEntity.tangleTarget每次检查活体/UNTANGLEABLE/canBeAffected后才setPos/zeroMotion/短TANGLED及前10tick重定位包；子类tangleTarget再继续动画和可选thorns伤害。',
 '群发法杖分支预先排标签但单体分支没有，最终tangleTarget检查覆盖两入口；对已选目标从控制变为免控也能逐tick拒绝。父拒绝void-return不阻止子类setAnimationState(hold)与isDamaging伤害，不能把藤蔓动画或掉血当“控制成功”。目标持UUID服务端重查，实际构造仅以目标位置出生未setTarget，前几tick在自身bbox重新选目标，可能另选。原生byte6每tick累加client activeTick，没有权威age；实体lifeSpan+20销毁。控制拒绝没有灰字/嗡鸣，重定位包按ID查当前世界，缺UUID/维度字段。',
 '控制操作前的最终守卫比最初选取时单次排除可靠；拒控返回值应让后续子类区分控制与伤害，反馈要明确被控制目标而不是出生位置邻近物。')
add('goety-windblast-physical-control-and-attached-effects-refusal',[w('common/magic/spells/wind/WindBlastSpell.java'),a('utils/MobUtil.java',261,277)],
 'WindBlast.SpellResult(ServerLevel)生成风流与沿线装饰→带lineOfSight的范围实体遍历→非盟友且非UNBLOWABLE门→knockBack和杖系附加效果/点火/驱散cyclone→通用技能音。',
 '同一最终guard包住实际速度改变、冰冻/毒/痉挛/虚空/点火和旋风移除；标签拒绝会全部跳过，不是只免击退。前面的风粒子和末尾WIND_BLAST音不依每目标成功。knockBack直接setDeltaMovement加阻抗，不经Forge LivingKnockBackEvent；可取1阻抗归零但不能把该数值缩放当明确拒控事件，原输入速度也被缩放。没有每目标拒绝回执、灰字、嗡鸣或冷却。',
 '最终控制门要覆盖与该操作绑在一起的附加效果；群体装饰/总技能声不证明单体成功，免疫须明确生产原因。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'goety-distinct-native-control-sites','credited_chains':['goety-banish-preteleport-eligibility-and-cancellable-receipt','goety-telekinesis-target-filter-and-native-mob-override','goety-telekinesis-held-target-termination-lifecycle','goety-entangle-final-control-gate-before-position-mutation','goety-windblast-physical-control-and-attached-effects-refusal'],'rationale':'独立操作/策略：传送资格与事件取消、抓取目标筛选、持续抓取终止、藤蔓最终位置守卫、风爆速度及附加效果整块守卫。各含完整方法及原生上下文；不按标签成员/元素/平台/包装加数；念力筛选与终止分别有独立最终行为，不因相同文件自动合并。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
