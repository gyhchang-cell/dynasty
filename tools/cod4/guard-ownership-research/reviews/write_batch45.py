import json,pathlib
R=[]
def a(r,f,m,o,b,l):R.append(dict(repo=r,file='/'+f+'.java',method=m,observation=o,application=b,limits=l))
B='Moriyashiine/bewitchment';G='Polarice3/Goety-2'
a(B,'Pledgeable','summonMinions','按master UUID只统计自己32格活随从，少于3才生成2至3；初始化后复制目标、设置master与持久化，再入世界。','数量租约和目标继承需要独立验证，复制当前目标并不能代表其仍合法。','完整召唤流程一处，按两三个实体不重复计；不同于玩家法术生成，为Boss master组件。')
a(B,'BWUtil','createGenericPledgeableTargetGoal','排盔甲架；玩家排已向指定pledge效忠者，非玩家排恶魔组；再拒至少三件besmirched装备。','身份授权和装备豁免结合，目标门必须基于当前关系而非最初扫描快照。','三个实际Pledgeable Boss注册调用；只概念借鉴，不能新增王朝效忠或PVP体系。')
a(G,'AbstractEnderling','isAlliedTo','仅无owner才将无队末影人视盟友；同类还要求对方无owner、双方没互锁且hostile状态一致。','无主野生关系与已租借控制关系必须分支处理，不能把野生策略全局重写。','同种且目标相反可撤同盟的完整策略，不是普通相同UUID模板。')
a(G,'ZPiglinServant','hurt','伤害来源非猪人且不盟友时，先向10格野生猪人经canAttack写怒气UUID和目标，最后才检查自身无敌与父hurt。','hurt返回false也可能已激活同伴攻击；统一拒绝要先于任何求援副作用。','真实随从转派野生仇恨路径；未将普通受击特效与数值免疫计入参考。')
a(G,'AbstractIllagerServant','mobInteract','整段仅trueOwner可进入；Waystone还查同维度、箱子可开启，leader向同伴同步存取箱，其余可装备图腾/护符并退旧物。','owner指令的权限与资源入口必须在所有分支前检查，群体转发不能隐式授权陌生人。','完整实际随从交互授权一处；食品粒子、装备包装不拆算，新制作不实现这些额外玩法。')
a(G,'Prisoner','mobInteract','蹲下解缚在master权限分支之前；master可换挖掘工具/箱目标，末尾解除leader或由Ownable owner接回trueOwner并跟随。','控制权迁移和开放释放是独立权限语义，不能仅依据存在旧master认定永久有效。','unshackle本体已研究，本条仅完整交互路由及owner重接，保留开放解缚边界不声称安全。')
pathlib.Path(__file__).with_name('batch45.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
