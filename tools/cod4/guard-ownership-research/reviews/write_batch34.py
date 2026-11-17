import json,pathlib
R=[]
def a(repo,f,m,o,b,l):R.append(dict(repo=repo,file='/'+f+'.java',method=m,observation=o,application=b,limits=l))
B='VazkiiMods/Botania';W='Electroblob77/Wizardry'
a(B,'MagicMissileEntity','findTarget','已锁活目标直接true不重新shouldTarget；失效才12格找可伤目标，evil找Player，普通用targetPredicate，随机选一。','现有target不能作为永远合法依据，关系/租约改变时要重新核。','两种弹形态仅完整重选实现一处，不把每个随机目标计数。')
a(B,'MagicMissileEntity','shouldTarget','先若Mob正在打isHostile认可对象就允许，再拒驯服动物/马，默认仅Enemy。','优先助攻可越过驯养保护，要看是否符合本项目Enemy硬边界。','不导入外部PVP扩展，只学习条件顺序与最终默认Enemy。')
a(B,'MagicMissileEntity','isHostile','主人与受攻击目标均玩家且主人能伤该玩家时，只护主人自身；其他情况护任何Player。','同一护卫判定依据服务器PVP规则分支，不能把护所有玩家默认为护单一主人。','用户不新增PVP，记录该外部规则而非移植。')
a(B,'MagicMissileEntity','tick','服务器findTarget失败或超过40即删；普通追踪当前位置，evil锁首位置；只有实际碰撞列表含锁定目标才hurt，随后discard。','目标池与碰撞实体池取交集能避免误中旁观者，但旧锁定还需身份重验。','整个真实弹体跟踪命中流程一处，粒子步进不计。')
a(B,'MagicMissileEntity','getDamageSource','Living owner中Player用playerAttack，否则mobAttack，失主使用generic。','失主伤害回退仍会产生作用，租约单位应在更早边界拒绝。','具体弹体归因策略一处，纯owner getter及序列化不计。')
a(B,'PixieEntity','setProps','同时设置target、summoner、damage和pixieType，为后续归因/免疫建立战斗身份。','构造后初始化需要原子配对目标与主人，不能只更新其中一个。','非纯单字段setter；实际绑定一组不同角色状态，类型getter不计。')
a(B,'PixieEntity','customServerAiStep','追target近1格后按summoner玩家/活体/无主三路hurt，非玩家target另加effect，无论hurt返回都discard。','主人失效与附效不受hurt返回控制需分别核；只拦伤害不足保护。','实际召唤精灵完整命中入口，不把每种source拆成多个实现。')
a(B,'PixieEntity','isInvulnerableTo','type0免疫summoner来源，type1免疫所有非Player来源，余下父类。','受控身份可改变受击边界，但不能用自身免疫替代对旁观者的攻击保护。','只计有实际身份分支的伤害门，不计普通不可栓/外观方法。')
a(B,'PixieEntity','baseTick','服务器target空或超过200tick删，客户端按类型发粒子。','无目标是回收条件，死亡target仍非空的情况不能从此方法推断已回收。','具体有限寿命召唤体一处，remove纯爆粒子不计。')
a(W,'AllyDesignationSystem','isValidTarget','owned攻击者递归主人，null目标拒/null攻击者允，队友/自身/FakePlayer/被动类/直系与盟友宠物/心控过滤，外部谓词只在根owner执行。','递归身份应保护直系及间接同主且避免重复调用；失主放开是需避免的反例。','整个实际召唤和AOE公共策略一处，注册List基础设施/文档示例不计。')
a(W,'AllyDesignationSystem','isAllied','空拒，owned攻击者递归主，玩家盟友/自己宠物/盟友宠物/队伍可true，心控直接返回controller等allyOf，否则运行扩展。','早退心控分支可能跳过后续扩展，保护判定必须了解控制流而非只看API名称。','此方法实际用于召唤效果/伤害保护，不把通用registry新增算实现。')
a(W,'AllyDesignationSystem','isOwnerAlly','玩家data空拒；被保护单位owner空则查保存UUID离线盟友，在线Player查实际对象，owner仍ownable则递归。','离线可用UUID保归属，解析不到实体不能抹掉明确存储身份。','不同于普通getter，完整离线/递归盟友判定一处。')
a(W,'AllyDesignationSystem','onLivingAttackEvent','仅Player真源且IElementalDamage生效，玩家受击按blockPlayers，其他按blockOwned+isAllied取消。','伤害门有source类型前提，不能把该事件误称所有普通近战都会被覆盖。','完整友伤兜底一处；用户不要求移植配置系统。')
pathlib.Path(__file__).with_name('batch34.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
