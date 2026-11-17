import json,pathlib
R=[]
def a(f,m,s,o,b,l):R.append(dict(repo='Polarice3/Goety-2',file='/'+f+'.java',method=m,start=s,observation=o,application=b,limits=l))
a('ImperialGuardServant','tick',317,'服务器无盾近敌启动逃避并导航，累计5秒或脱离3格完成路径才退逃并进入5秒冷却；另外递减攻击冷却。','战斗模式影响导航/蓄势窗口；非法target即使没受伤也会驱动主动回避。','Rogueguard相同tick端口不计，客户端闲置动画不是计数依据。')
a('ImperialGuardServant','canUse',441,'逃跑或攻击冷却中拒绝；否则活目标非创造旁观且可见才把target缓存在goal。','goal缓存活引用在启动后可能过时，后续tick不能只信canUse判过。','Rogueguard同构canUse不另计；这里只研究已注册技能许可。')
a('ImperialGuardServant','tick',478,'对缓存target超过32格追近，否则停；无盾14格内后退，预攻累计20tick发射，40重置周期。','持续技能按缓存对象动作，改Mob.target未必改变旧goal.target。','Rogueguard同构tick不计，数值/音效变化不算新实现。')
a('PikerServant','tick',347,'攻击第8tick主目标近且伤害成功才扫描前方其他活体；附带对象需可见非盟友，但末尾canAttack误用主目标livingentity。','AOE候选变量与主目标变量必须逐处核对，主目标合法不代表溅射候选合法。','Vanguard近似长矛AOE只换盟友查询模板不另计；此为源码变量事实未实测该模组。')
a('BoneSpiderServant','tick',215,'缓存target近距且可见才减攻击计时，远则清动画追近；20tick蓄吐，0tick再验可见发射并重置。','蓄力后失视与目标失效应区分，持久goal缓存需独立许可。','只计攻击goal，122停速modifier与已读stayingMode同模板不计。')
a('WebSpiderServant','attackGoal',52,'跳扑及近战都要求父许可、非吐网且target有TANGLED才启用。','状态效果可切换攻击模式，过滤须覆盖两种goal而保留合法战斗切换。','两个匿名goal作为一个完整注册方法计，不拆成两条。')
a('WebSpiderServant','tick',134,'服务器未吐网且目标未缠绕时5格内逃离；缠绕则清逃且不攀爬；空target清逃/stopMoving，按stopMoving移除再加固定速度modifier。','目标变化能影响逃跑、攀爬和移动锁，撤销动作需兼顾这些瞬态。','整体真实物种模式切换计一处，modifier模板本身不单独增加。')
a('WebSpiderServant','performRangedAttack',183,'创建以自身为owner的WebShot，用目标速度预判xz及眼高发射，播声并加入世界。','瞄准预判坐标之外，弹体仍携owner供实际命中审查。','类似普通箭发射模板今后不重复，此处研究实际网弹身份传递。')
a('WebSpiderServant','canUse',214,'目标活且非逃跑才先缓存；仅未TANGLED且大于4格返回true。','返回false也可能写goal缓存，后续停用是否清缓存需要与stop配合。','非纯存活门，包含网状态及退避互斥；不按状态常量变体增加。')
a('WebSpiderServant','tick',248,'进射程就停移动，否则追；攻击计时持续递减，预热动画点才验视线，稍后实际performRangedAttack没有再次视线判断。','动画通过时刻与实际发射时刻可分离，合法目标需在最终动作前再核。','与BoneSpider只在可见近距递减并0点再验不同，完整网弹时序一条。')
pathlib.Path(__file__).with_name('batch19.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
