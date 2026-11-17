import json,pathlib
R=[]
def a(r,f,m,o,b,l,s=None):
 d=dict(repo=r,file='/'+f+'.java',method=m,observation=o,application=b,limits=l)
 if s:d['start']=s
 R.append(d)
G='Polarice3/Goety-2';M='AlexModGuy/AlexsMobs';C='lender544/new1.20.1'
a(G,'AbstractBorderWraith','attackAI','非breathing按fireTick20发魔火54终止；breathing锁初始点并逐步追踪，20帧后真实getSingleTarget再doBreathing，超3.5秒或hurtStop终止。','锁定目标与实际呼吸命中实体不同，许可门应作用最终命中而非初始getTarget。','BorderWraithServant实际继承，区别普通Wraith为独立呼吸射线攻击出口，移动/粒子不单计。')
a(G,'AbstractBroodMother','attackGoal','近战Goal在非circling才启用，目标到范围后改扫前方AABB，排创造旁观与盟友逐个doHurtTarget，成功或blocking都算一次挥击反馈。','单目标近战实际可转为多目标伤害，最终每个victim都必须核归属。','完整真实Goal注册含circling互斥及格挡反馈；攻击宽度常量不拆算。')
a(G,'AbstractBroodMother','attackAI','WEB第7帧八次射击，LAY_EGG第10帧生成以自身为trueOwner的有限寿命SpiderEgg并finalize入场；冲锋/后跳第10帧起areaAttack。','攻击状态本身还会生成有二级owner的下一代，主人失效必须阻止整个攻击状态出口。','四攻击状态合并一处，八发与三个寿命值不凑数；普通毒后效端口未另计。')
a(G,'AbstractBroodMother','areaAttack','范围先排盟友/死者，实际3格内用getServantAttack伤害，成功才标hurtMarked；目标已TANGLED则不击退。','直接hurt绕过doHurtTarget，租约安全检查不能仅限某个近战辅助入口。','持续冲锋范围实效出口，不按TANGLED分支或向量数学另计。')
a(G,'AbstractObsidianMonolith','silentDie','父die后爆炸专伤同owner或自身owned随从并清野猪人；杀手Mob正锁自己时转其目标与Brain记忆到trueOwner，Warden另加怒。','被移除单位仍可在死亡回调传播伤害与目标，普通discard与die语义不可混用。','完整死亡归属与仇恨迁移行为，Apostle冷却写入一起观察不另计。')
a(G,'AbstractObsidianMonolith','ownerlessBehavior','无主路径按难度/附近数量生成生物；强化时可生成Maverick，清空时概率生成Heresiarch并绑定leader/monolith，通过SummonCircleBoss入场成功才存UUID和5分钟CD。','无主野生生成与租约失效删除是不同政策，不应让失效守卫自然落到野生攻击/生成分支。','真实无主分支完整93行已读；通用自然生成检查只作同链支持，不按召唤类别额外计数。')
a(G,'AbstractReaper','attackMobs','先给master玩家按主目标SoulGiven收益，范围内排自身/盟友/标记架/坐骑，先击退后hurt，成功才点火并按二级owner规则再给魂。','收益和位移发生在实际伤害前，拒绝无效目标须截断整个攻击而非事后取消hurt。','真实受控Reaper横扫完整路径，不把附魔伤害计算当独立实现。')
a(G,'AbstractSnareling','checkAndPerformAttack','敌人超近战范围优先随机传送其周围，成功发位置包并6秒CD，失败走导航；范围内停导航、设ATTACK再doHurtTarget。','目标无效时单拦hurt仍允许传送逼近和播放攻击，canAttack入口应提前约束。','实际注册随从专用近战Goal，纯传送几何函数不另计。',433)
a(M,'EntityBaldEagle','positionRider','确认确实乘客后定位到鹰爪并强制旋转，passengerTimer每40tick直接hurt乘客1点，与当前target无关。','控制/捕获关系也有独立持续伤害，清getTarget不能证明所有攻击已解除。','完整抓取乘客实效出口；普通坐骑偏移矩阵不独立计数。')
a(M,'EntityCaiman','registerGoals','同挂定制Caiman近战和原版近战；owner两种受击目标Goal start设tameAttackFlag，stop却调用super.start再清flag；野生猎食Goal只非幼体且非tame。','驯服与野生选敌分支应明确隔离，停止回调错误重启目标需要最终门兜底。','实际两条owner目标回调同构仅合并一次，普通注册列表不逐条计。')
a(M,'EntityRaccoon','isAlliedTo','对BlueJay先按其raccoonUUID等于自己判断并直接返回，其余再走tame owner/其他宠物/主人队伍模板。','跨物种绑定是独立同盟来源，统一目标策略要尊重实体既有isAlliedTo而非只比类型。','本条仅新增BlueJay关系前置的完整策略，后半经典宠物同盟模板不重新计。')
a(M,'RaccoonAIWash','tick','水边停导航进入washing，累计100tick或糖20tick后stop，非糖吃食，再postWashItem按之前eggThrowerUUID驯服，退容器并扣物。','延迟行为完成才建立owner，开始时投掷者记录与最终控制权提交有窗口。','完整实际宠物驯服洗食链合计一处，postWashItem随机赋主与Gorilla食品模板仅支持不另计。')
a(C,'Netherite_Ministrosity_Entity','mobInteract','owner先允许收空桶否则非蹲开库存并强制坐姿；未驯服用LavaPowerCell经可取消tame事件觉醒；任何人可给煤治疗，主人蹲才三态命令。','所有权许可按具体动作区分，公开治疗不应推导为可打开他人宠物库存或改命令。','完整交互含有库存与回收权限，普通三态setter及纯屏幕同步基础设施未计。')
a(C,'The_Baby_Leviathan_Entity','mobInteract','未驯服累计鱼数随机/保底驯服，已驯服先公开鱼疗，再无owner检查调用桶回收，只有末尾命令才isOwnedBy。','前置回收路径可早于owner命令检查，不能仅看末尾归属门断言所有交互安全。','与Ministrosity空桶仅owner不同为公共桶捕获真实反例；数值/物种替换不单计。')
pathlib.Path(__file__).with_name('batch48.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
