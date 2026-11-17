"""Pinned game feedback lifecycle study; no production or runtime actions."""
from reference_evidence import Evidence,row
import json
E=Evidence(15);R='Electroblob77__Wizardry'
r=lambda f,m=None,**kw:E.ref(R,f,m,**kw)
P='pending_primary_semantic_review';S='support_only_not_effective'
rows=[]
rows.append(row(15,1,'wizardry-disintegration-client-local-death-marker-model-overlay-unbounded-lifetime',P,
 [r('Disintegration','onEntityHit'),r('Disintegration','spawnEmbers'),r('EntityUtils','attackEntityWithoutKnockback'),r('SpellRay','shootSpell'),r('Disintegration','spawnParticleRay'),r('Spells',span=[438,438]),r('Wizardry','postInit'),r('ClientProxy','initialiseLayers'),r('LayerTiledOverlay','initialiseLayers',signature='Class<T> entityType'),r('LayerTiledOverlay','initialiseLayers',signature='Function<RenderLivingBase<EntityLivingBase>'),r('LayerTiledOverlay','doRenderLayer'),r('LayerTiledOverlay','renderEntityModel'),r('LayerDisintegrateAnimation','shouldRender'),r('LayerDisintegrateAnimation','getTexture'),r('LayerDisintegrateAnimation','doRenderLayer'),r('LayerDisintegrateAnimation','onRenderLivingEvent',signature='Pre<EntityLivingBase>'),r('LayerDisintegrateAnimation','onRenderLivingEvent',signature='Post<EntityLivingBase>')],
 'Disintegration命中非FIRE免疫目标先setFire再attackEntityWithoutKnockback（保存速度→hurt→无条件恢复速度，返回bool但调用方忽略）；随后只用Living health<=0判断spawnEmbers。client分支首次写entity NBT disintegrating=ticksExisted，server分支spawn Ember并不发送此专有标记。postInit→ClientProxy.initialiseLayers→所有Living renderer和独立Player skin map加入Disintegrate layer。shouldRender仅hasKey，texture按ticksExisted-start夹0..18，第19tick后一直最后帧，无本链清key/到期门。RenderLiving.Pre有key时deathTime=0且invisible=true，Post无条件invisible=false，未保存原隐身状态；不是server死亡认证包。layer满亮绘原模型贴片，非悬浮文字。',
 '战斗结果展示需要权威对象、明确事件与到期清理；模型/NBT本地状态不能被当作Boss已死亡或免疫回执。临时可见性修改必须还原原值，避免覆盖其它效果。',
 '区别既有Ars Disintegration直接remove绕damage的生产点：本链是Wizardry客户端本地死亡标记→模型覆盖→渲染回调状态恢复，完整producer/注册/consumer已读。所有包装/19帧/不同Living或Player renderer合并一个生命周期提案，credit0待主岗跨项目审。',
 ['已读原生游戏入口/模组注册，但未读Minecraft原生render dispatcher每种取消/异常路径，不宣称Post一定调用。', '没有S2C专有收据证明；源码自身FIXME syncing issues不作为已动态复现证据。', '不更改任何贴图/模型/动画，未打开游戏或操作camera。', '仅保证本链没清key，不声称整个游戏永远不会移除entity/NBT或其它mod不会干预。']))
rows.append(row(15,2,'wizardry-magic-slime-mounted-slow-refresh-ignores-hurt-result-support',S,
 [r('Slime','onEntityHit'),r('Slime','onMiss'),r('Slime','spawnParticle'),r('EntityMagicSlime','EntityMagicSlime',signature='EntityLivingBase caster'),r('EntityMagicSlime','onUpdate'),r('EntityMagicSlime','setDead'),r('EntityMagicSlime','attackEntityFrom'),r('ISummonedCreature','updateDelegate'),r('Spells',span=[350,350]),r('WizardryEntities',span=[93,93])],
 'Slime射线命中Living且非MagicSlime：普通EntitySlime给caster resist，其他server new MagicSlime在构造器startRiding(target)但忽略bool，再spawn。每16tick==1对当前仍存活Living载体先1MAGIC hurt且忽略bool，再重查ridingEntity是否null后server加20tick SLOWNESS2，同时playAttack声和squish；伤害免疫不阻断慢速尝试。无载体/载体死即setDead，自己IN_WALL false独立；setDead改isDead=true/health0并30粒子及两声，无幂等保护。',
 '附着租期、周期伤害、减速刷新和爆裂反馈应有各自结果，不以hurt=false撤销后续控制假设；startRiding成功需核对实际返回。',
 '与已计wizardry-entrapment-mounted-control-binding-and-teardown同为载具绑定控制生命周期，并与hurt-ignore副作用家族重合，保留支持0，不按16tick/20tick或slime命名新增。', ['原生startRiding及最终Potion接纳内部未展开，不声称Boss一定可骑乘或实际减速。', '父寿终setDead后本tick仍可能往下走，未运行，不把重复爆裂当已证实缺陷。']))
rows.append(row(15,3,'wizardry-purification-cast-relative-first-tick-resist-not-per-target-throttle-support',S,
 [r('RayOfPurification','onEntityHit'),r('RayOfPurification','onMiss'),r('RayOfPurification','spawnParticleRay'),r('SpellRay','cast',signature='EntityPlayer caster'),r('SpellRay','shootSpell'),r('MagicDamage','isEntityImmune'),r('EntityUtils','attackEntityWithoutKnockback'),r('Spells',span=[451,451])],
 'continuous RayOfPurification对Living RADIANT免疫仅ticksInUse==1发resist；非免疫每ticksInUse%10==0尝试hurt并server blindness，未使用hurt bool。此==1是施法相对tick，不是每目标节流：持续施法后才换到免疫目标可不发本次文字。onEntityHit总true，使父层截粒子到命中点，即使这tick既没伤害也没文字；beam按caster tick大小变化，不是成功伤害包。',
 '提示首tick与目标进入时机要分开设计；不能用施法总tick代替每目标拒绝原因的反馈窗口。',
 '与既有wizardry-chain-target-dedup-scope-and-resist-cadence和元素政策重复家族，明确支持0；不按RADIANT常量/continuous变体新增信用。', ['本轮不重跑施法或换目标，未断言用户能看到任何头顶文字。']))
rows.append(row(15,4,'wizardry-disintegration-ember-contact-burn-bypasses-parent-ally-seeking-filter-support',S,
 [r('Disintegration','spawnEmbers'),r('EntityEmber','onUpdate'),r('EntityEmber','onImpact'),r('EntityEmber','applyEntityCollision'),r('EntityEmber','getLifetime'),r('EntityMagicProjectile','onUpdate'),r('WizardryEntities',span=[131,131])],
 'spawnEmbers服务端newEntityEmber带caster；Ember每tick先父寿命/寻敌，再对AABB中除thrower且Living health>0实体直接setFire；未复用父寻敌AllyDesignationSystem条件或MagicDamage.isEntityImmune。applyEntityCollision也在super后对Living活体setFire。原onImpact实体燃烧实现是注释不计，实际BLOCK碰撞只设inGround/运动分量与collidedVertically。未读取原生setFire最终资格，所以这不是能绕过fire immune的证明。',
 '生产点必须覆盖附属实体后续接触；仅最初伤害/寻敌过滤不会自动保护独立setFire入口，但最终免疫仍需原生消费层核对。',
 '同一Disintegration后续附属实体支持，不额外申请免疫位点；纯setFire缺原生消费者也不足有效信用，支持0。', ['没有原生EntityThrowable update/Entity setFire最终实现，不能声称友方最终必被点燃或有实际HP损失。', '不将Ember数量、余命随机值或三坐标碰撞常量当独立参考。']))
print(json.dumps(E.finish(rows),ensure_ascii=False))
