from ledger import record as append_record,verify,O
import json
def record(key,*args,**kwargs):
 if key not in {x["id"] for x in json.loads((O/"reviewed.json").read_text())}:
  return append_record(key,*args,**kwargs)
r='lender544/new1.20.1';p='src/main/java/com/github/L_Ender/cataclysm/'
def cm(key,refs,chain,obs,lesson,limits):
 record(key,r,[(p+f,a,b) for f,a,b in refs],chain,obs,lesson,limits,'immunity_rejection_semantics')
cm('cataclysm-range-damagebucket-authority', [('entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',73,192),('entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java',129,249),('entity/etc/Animation_Monsters.java',97,99)],
 '完整hurt入口及tick衰减链→原版isInvulnerableTo→bypass直接super→damageCap→calculateRange(source owner平方距离)→rangeCap到1.5倍线性减伤/更远拒绝→伤害桶→super结果false回滚桶；两个动画Boss基类同构链合并一条。',
 'range=-1无来源时不做范围拒绝；1.5倍处return false。伤害桶耗尽后并非免疫，而是amount=0.1继续super；受伤失败才回滚桶。tick按DpsCap/20衰减，AI关闭时不衰减。此链没有专用拒绝文本。',
 '伤害限流、部分减伤与拒控免疫必须分开，不能见hurtTime/cap就显示Immune。复用基类的多个Boss不重复计。',
 '只读模组拥有的权威判定到原版super契约；不推断配置实际值或原版受伤内部，不证明任何灰字/运行观感。')
cm('cataclysm-crab-burrow-window-rejection-sound', [('entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java',58,63),('entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java',149,162),('entity/AnimationMonster/LLibrary_Monster.java',57,81),('entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',73,137)],
 '完整hurt覆写读取当前动画和tick字段→CRAB_BURROW限定开区间→排除bypass→ANVIL_LAND原版音→false；未命中时进入已读共享Boss基类。',
 '只在动画tick>9且<52期间挡普通伤害，边界9/52不挡；音量0.4音调2.0，拒绝路径没有粒子/文字。动画整个65tick并非全程无敌。',
 '视觉动画长度不可替代当次服务器拒绝区间；声音可以采用现有原版资源，文字语义需在实际false处接入。',
 '动画更新/广播由lionfishapi外部契约承担，本条不把该库算研究或声称同步已验；不按每个动画帧拆条。')
cm('cataclysm-leviathan-environment-immunity-actionbar', [('entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java',312,350),('entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java',367,389),('entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Part.java',59,66),('config/CMCommonConfig.java',134,140),('entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',73,137)],
 '部件hurt→parent.attackEntityFromPart→parent.hurt；完整环境判断canInFluidType→FluidType.canSwim(self)；非可泳环境且配置开启、非bypass，directEntity为Player时displayClientMessage(translatable,true)，随后拒绝false。其余进共享hurt链，冲刺期成功受伤可触发STUN。',
 '这是原生拒绝处的本地化文本回执，但载体是攻击者动作栏，不是目标头顶。检查的是directEntity，所以玩家射箭的direct为箭时不会命中Player提示分支。配置默认true。模组本方法无独立文本节流/事件去重。',
 '权威拒绝可显式发本地化语义，不需血量改变；攻击者/直接命中体要区分。部件必须映射本体，动作栏回执不能当作灰色目标锚定浮字范例。',
 'canSwim不等于简单isInWater，原版消息网络/GUI为平台契约；尚未取得语言资源翻译值，故只证明key与载体调用。无游戏验收、无像素结论。')
p='common/src/main/java/net/mehvahdjukaar/dummmmmmy/'
record('dummy-authoritative-hit-number-particle','MehVahdJukaar/DuMmmMmmy',[(p+f,a,b) for f,a,b in [('common/TargetDummyEntity.java',403,580),('common/TargetDummyEntity.java',612,700),('common/TargetDummyEntity.java',819,821),('common/TargetDummyEntity.java',861,926),('network/ClientBoundDamageNumberMessage.java',24,129),('network/ModMessages.java',8,15),('DummmmmmyClient.java',48,51),('client/DamageNumberParticle.java',31,222),('configs/ClientConfigs.java',76,124),('configs/ClientConfigs.java',146,191),('configs/CritMode.java',1,21),('common/CritRecord.java',1,35),('compat/CritCompat.java',1,14)]],
 '完整服务端hurt/setHealth/actualDamage→source/crit记录匹配→有战斗追踪玩家才发entityID+amount+damageType+crit；完整包读写/handle→客户端解析目标→particleFactory→35tick独立文字粒子→camera billboard+两次NORMAL font draw。重载/平台包装合并1条；Moonlight网络注册/发包为明确外部API边界。',
 'setHealth在无限血Dummy不实际降血也能发伤害数，说明同步血差不是唯一生产点。服务端玩家追踪300tick；同tickanimationPosition累加不等于伤害数字去重，每次仍可发包；客户端五个横向槽循环，目标当前位置+1出生后不跟随；35tick淡出，alpha最低4避免字体当不透明。NORMAL深度测试并非穿墙；暴击文字保留translatable Component。',
 '应在权威语义点发事件；伤害数与免疫文案需要独立类型。完整目标ID解析可以在目标不存在时不生成；出生点快照与持续锚定是不同选择，去重不能靠横向分槽假定已做。',
 '包handle未显式检查Minecraft.level为空；无维度epoch/UUID/自定义冷却可见于本链；粒子生命周期由原版particle engine持有。不把Dummy模型/贴图当本任务研究，不做资产复制。平台网络和可选CriticalStrike getter为外部契约，未运行验证。')
verify()
