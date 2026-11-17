"""AoA active registrations, native denial and multipart repeat-hit suppression."""
from ledger import B,O,record,verify
import json
r='Tslat/Advent-Of-Ascension';p='source/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
reg=[(p+'common/registration/entity/AoAMonsters.java',29,30),(p+'common/registration/entity/AoAMonsters.java',70,79),(p+'common/registration/entity/AoAMonsters.java',362,369),(p+'common/registration/AoARegistries.java',117,117),(p+'common/registration/AoARegistries.java',174,180),(p+'common/registration/AoARegistries.java',204,222)]
f=p+'content/entity/boss/nethengeic_wither/NethengeicWitherEntity.java';k='aoa-nethengeic-native-aura-energy-hit-conversion-and-melee-recoil-order'
record(k,r,reg+[(f,100,105),(f,115,121),(f,191,240),(f,369,386),(f,399,440),(p+'content/entity/boss/nethengeic_wither/EliteNethengeicWitherEntity.java',385,420),(p+'util/DamageUtil.java',225,231),(p+'util/DamageUtil.java',249,259),(p+'common/registration/AoATags.java',391,391),w('data/aoa3/tags/damage_type/energy.json')],
 '真实注册NethengeicWither/AoABoss→native Brain fight tasks延迟20tick切FLAME_AURA（同步数据默认false）→native hurt hasAura且energy标签来源时heal(amount)+return false；近战分支先反伤/点燃/诅咒再继续super。native aiStep无target关光环。精英同生产分支合并。',
 '能量伤害转本体治疗的最终拒伤点1；不能把所有光环命中都叫免疫：近战仍继续伤害但先反击，后续hurt失败也不回滚这些副作用；energy治疗发生在super的伤害有效性/无敌帧检查之前。光环技能启动声和triggerAnim是状态启动反馈，不是每次拒伤灰字/嗡鸣。客户端aiStep已有光环粒子生产，但自定义tracking粒子消费未全读，本条不声称完成渲染链或观感。energy资源标签实际填充两个可选类型；与普通火免疫无关，不因名为fireaura直接推火伤零。精英只在super成功后检查跨血量阈值，与重复的energy拒伤不另计。',
 'Boss明确拒控单独理由回执；一次伤害失败可有治疗/反击副作用，不能将hurt=false自动映射IMMUNE，更不能重放所有状态启动音作为拒绝音。',
 '固定7919b5fe48599e6105c5740937ce36c36ef21d16；全文关键方法/注册及实际标签已观察，源码snapshot缺少main advent包，未构建/启动，不声称自然获取/可加载整包或像素验收。Flash/Visualent/RockRider整类注释旧代码0。','native_boss_damage_denial');keys.append(k)
f=p+'content/entity/boss/AoABoss.java';k='aoa-native-boss-void-refusal-repositions-to-loaded-arena'
record(k,r,reg+[(f,192,205),(f,100,128),(p+'event/dimension/NowhereEvents.java',53,55),(p+'content/world/nowhere/NowhereBossArena.java',41,68),(p+'content/world/nowhere/NowhereBossArena.java',85,110),(p+'content/world/nowhere/NowhereBossArena.java',223,260),(p+'content/world/nowhere/NowhereBossArena.java',288,290),w('data/aoa3/aoa3/nowhere_boss_arena/square_arena.json')],
 '实际已注册Nethengeic等继承AoABoss.native hurt→服务器Nowhere+FELL_OUT_OF_WORLD+Y<minbuild→getClosestArena（数据重载registry缓存、Boss region过滤、结构bounds）→resetFallDistance/setPos随机bossSpawn→false，否则super。原生customServerAiStep另每60tick检查越界180tick后回场或discard。',
 '一个带恢复位置副作用的最终拒伤点，所有Boss共享base不按名字/arena资源加数。nearest不是必需包含：testDist<2500立即返回第一个，否则全体nearest；结构bounds会额外inflate50。不在Bossregion或无arena时继续super，不保证所有虚空伤害都拒绝。codec要求非空bossSpawns且实际square有坐标，资源不是新制作建筑，不读取/复制NBT。hurt立即回场无显式灰字/光效/声音；setPos非randomTeleport，不能声称走传送可取消事件。AI定时恢复是另入口同保护家族，不另计。',
 '最终伤害拒绝可能是场地恢复，不是控制免疫；灰字只接明确Boss拒控理由，不接通用拒伤返回。恢复坐标/客户端看到移位不等于独立免疫回执。',
 '固定版本源码/数据，完整关键方法已读。AoAResourceCaching内部调度/结构生成没有动态验证，未声称缓存生命周期或场地自然生成已验；仅拒伤逻辑静态研究。无游戏/正式代码/资产/待办改动。','native_damage_denial_recovery');keys.append(k)
k='aoa-native-piercing-arrow-whole-multipart-hit-dedup-before-parent-hurt'
record(k,r,reg+[(p+'content/entity/boss/tyrosaur/EliteTyrosaurEntity.java',84,99),(p+'content/entity/boss/tyrosaur/EliteTyrosaurEntity.java',213,247),(p+'content/entity/base/AoAMonster.java',65,82),(p+'content/entity/base/AoAMonster.java',292,296),(p+'content/entity/base/AoAMonster.java',403,405),w(p+'content/entity/base/AoAMultipartEntity.java'),w(p+'library/builder/MultipartBuilder.java'),(p+'content/entity/base/AoAEntityPart.java',84,89)],
 '实际EliteTyrosaur注册→构造AoAMonster.registerParts→具体definePartEntities/MultipartBuilder建立并缓存各parent新part→原生part.hurt合格时parent.hurt（倍率）→Elite护甲副作用→AoAMonster.onMultipartParentHurt→穿透箭piercingIgnoreEntityIds加入全部parts和parent，随后super.hurt。',
 '原生同箭多部位命中去重策略1，非时间窗口/数值伤害桶。箭pierce>0且parts非空才加IntOpenHashSet，按箭生命期ID集合；加入在实际super受伤接纳前，即最终无敌帧/外部拒伤也已消费该箭对全身各部件的后续命中资格。source只取direct AbstractArrow；本地EntityPart enabled检查拒绝时不达parent。Builder缓存的是构造计划，每次parent重建part，不共享旧实体。并非packet去重，无UUID/维度nonce，不能复用当灰字节流。所有部位共一次策略，不按尾/头/倍率/精英壳拆。',
 'Boss拒控回执去重应绑定一次真实尝试/目标，明确是在最终拒绝后发字；重复部位抑制和按目标短时防刷屏是不同需求。',
 '全文相关native链和Builder关键方法已观察；原版AbstractArrow消费ignore集合内部辅助0，未读原生版本源/未实机，不宣称网络并发或箭命中像素验收。没有新增/复制身体资产。','native_target_hit_dedup');keys.append(k)
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'aoa-batch54','credited_chains':keys,'rationale':'光环能量转治疗、场地虚空恢复、实际箭全身去重三个不同最终位点；精英重复/注释整类/常量0。Elite护甲灰色数值尚缺匹配TES旧版本收包绘制，候选0，不能将现缓存新TES包名强行接活。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
