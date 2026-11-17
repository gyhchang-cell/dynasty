import json,pathlib
R=[]
def a(f,m,o,b,l,s=None):
 d=dict(repo='Polarice3/Goety-2',file='/'+f+'.java',method=m,observation=o,application=b,limits=l)
 if s:d['start']=s
 R.append(d)
a('BearServant','getControllingPassenger','非NoAI时首乘客是Mob按autonomous配置决定是否交控制；其他活体仅坐骑非自主时控制。','实际控制者可为另一随从，不能仅认为坐骑的owner就是即时操作者。','Hoglin同方法为完全相同端口不另计；这不是单字段getter。')
a('BearServant','mobInteract','服务器且操作者真主人时，鱼可治疗耗物；非蹲成年熊可让现乘客下车或让非魔杖持有主人骑上。','下车和骑上都必须在主人许可内部，错误所有者会直接控制别人的乘客。','Hoglin只换治疗物品及少量条件端口不另计，Guardian喂鱼部分也不重复计。')
a('BearServant','checkAndPerformAttack','在攻击半径且冷却到达才doHurtTarget并落站姿；双倍半径内最后10tick起立警告，远处重置冷却及姿态。','预警、蓄势和实伤是三个窗口，撤目标后不得延用旧攻击对象。','本条完整熊近战特殊时序计一处；不把原生通用冷却getter另计。')
a('GhastServant','tick','目标64格内可见累计蓄能，10tick警告20tick生成带ghast owner的Lavaball并进入负40冷却；失视时正蓄能递减。','发射前需用当前许可，飞行中的炸弹还需独立命中/AOE筛选。','这是实际随从自定义Lavaball发射链，后续别模组的原生Ghast复制不重复算。')
a('GuardianServant','hurt','服务端静止守卫在非避荆棘/非荆棘来源时，先对直接Living来源反2伤，再触发游荡和父hurt。','反击会发生在父伤害接受前，故不能只在常规攻击方法过滤旁观者。','不把反伤等同原Enemy规则，守卫本项目无需新增荆棘。')
a('GuardianServant','tick','目标可见才蓄激光，0tick同步目标ID，到攻击时长分别打间接魔法及随从攻击两次，随后清target。','一次技能可走两次不同DamageSource，最终过滤应覆盖完整命中链。','只计445攻击goal tick，502移动数学不计；客户端缓存模板与Cockatrice重复不计。',445)
a('GuardianServant','canContinueToUse','父持续许可成立且长老或当前目标距离平方大于9才继续。','技能近距离退出与普通近战不同，持续许可不能用起始许可替代。','普通存活canUse模板不计；不按长老数值变体重复。')
a('GuardianServant','stop','清同步激光目标ID、清服务器target，再触发随机游荡。','停止技能须撤服务器目标和客户端表现通道，不只清一个缓存。','与普通stop导航模板不同，含激光通道撤销；不声称会撤销已飞行其他弹。')
a('HoglinServant','hurt','先父hurt取得结果；幼体遇非盟友Living伤害源就缓存toAvoid、停路径并设随机逃跑期，不依赖hurt返回true。','攻击失败也可能产生受击仇恨/回避状态，审计必须看副作用条件。','成年不走此逻辑；不会把该外部回避机制引入本项目。')
a('HoglinServant','aiStep','服务端搜索驱避方块设置200退避；幼体从活的toAvoid逃跑，成人清它；两个退避时钟均会清target，再择远离驱避物的可达路径。','除了target还有回避缓存和时钟，模式切换可能清敌但继续移动。','完整物种回避逻辑只计一处，寻路随机数学不拆分。')
a('SlimeServant','remove','服务端死亡且尺寸>1时生2至4幼史莱姆，复制名称NoAI无敌及尺寸，非空owner/剩余limitedLife和hostile也继承，最后父remove。','租约子代必须沿用到期和归属，不能死亡分裂重置生命周期。','不是普通remove包装；不按每个子实体或继承字段算多条。')
a('SlimeServant','mobInteract','增大/回血物品分支在主人校验外；仅空手主手非蹲互动限定主人，Magma变体还可能点燃并伤玩家。','交互并非全部owner专属，必须按实际分支划清授权范围与附带伤害。','本项目不照抄其公开喂养或热伤，只研究不同交互边界。')
a('SlimeServant','tick','每tick为活target扩展其或载具合并AABB，仅列表中同一个target且可伤时dealDamage，随后做落地动画。','接触攻击除了push还有主动tick扫描入口，过滤不能只拦近战goal。','完整方法含粒子但只凭实际目标接触伤害计数，不将粒子循环另计。',174)
a('SlimeServant','push','先父物理推挤，再仅当碰撞实体就是当前target且可伤时dealDamage。','碰撞与普通攻击分离，目标许可变化应在这个最终入口同样生效。','父push物理行为仍发生；只记录实际接触伤害路径。')
a('SlimeServant','dealDamage','存活、尺寸距离内且可见才调用随从伤害，成功才声音/附魔/物种postAttackEffect。','命中副作用严格依赖伤害成功，适合作为最终过滤前后次序参考。','不按尺寸倍率或每种子类附效拆计；不是原生攻击单纯转发。')
a('SlimeServant','canUse','主人非空非旁观、距离达到启动值，自己有正确moveControl且following、非commanded、无target时才缓存owner跟随。','跟随状态不自动等于可启动，战斗和命令通道优先级需完整保留。','常规跟随模板多数重复不计，本条包含史莱姆移动控制与命令互斥。',602)
a('SlimeServant','canUse','无target且非巡逻，只有无主或wandering，并满足落地/水熔岩/漂浮与特定moveControl才随机转向。','无主时的野生式自主分支必须与有租约模式区分，不能一刀切修改。','只计772实际闲逛许可，其他简单水中跳跃模板不计。',772)
pathlib.Path(__file__).with_name('batch17.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
