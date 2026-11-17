"""Botania native refusal and qualification; neither textures nor generic particles counted."""
from ledger import B,O,record,verify
import json
r='VazkiiMods/Botania';x='Xplat/src/main/java/vazkii/botania/';f='Forge/src/main/java/vazkii/botania/forge/';keys=[]
def s(q,a,z):return q,a,z
def whole(q):return q,1,len((B/'sources'/r.replace('/','__')/q).read_text().splitlines())
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定0ddec883d6ec4c7be78525267e29cbf1bd98c672；实际完整方法及原生事件/实体调用上下文。未运行，没有画面/TCP/声音验收；不复制资产，普通阴阳体质无灰字新增要求。','native_damage_refusal_and_target_validity');keys.append(k)
init=f+'ForgeCommonInitializer.java';items=x+'common/item/BotaniaItems.java'
add('botania-holy-cloak-native-zero-damage-stack-cooldown-reentrancy',
 [whole(x+'common/item/equipment/bauble/CloakOfVirtueItem.java'),whole(x+'common/item/equipment/bauble/CloakOfSinItem.java'),whole(x+'common/item/equipment/bauble/BaubleItem.java'),whole(x+'common/handler/EquipmentHandler.java'),whole(f+'integration/curios/CurioIntegration.java'),s(f+'xplat/ForgeXplatImpl.java',540,546),s(init,147,187),s(init,287,292),s(init,424,440),s(init,518,566),s(items,284,286),s(items,394,401),s(items,431,435),s(x+'common/helper/ItemNBTHelper.java',38,40),s(x+'common/helper/ItemNBTHelper.java',50,52),s(x+'common/helper/ItemNBTHelper.java',108,110),s(x+'common/helper/ItemNBTHelper.java',120,122)],
 '原生LivingHurt完整listener遍历实际EquipmentHandler.getAllWorn→Cloak.onPlayerDamage，非bypass/找到本件且!inEffect才设置重入标记→cooldown==0才effectOnDamage；Holy把MutableFloat置0、声音及粒子调用，成功才设每stack200tickCD，回传event.setAmount；实际Curios wrapper.curioTick调用onWornTick递减。',
 '零伤与取消原生事件不同，原生受击其它步骤/监听仍可能发生；CD只在穿戴tick推进，换stack不共享。inEffect用于反伤递归，没try/finally，异常可留真。Sin继承同包装但不减原始amount，只AOE反伤后声/粒子，故不把共享cooldown外观叫免疫，也不另计Sin信用。Forge原生LivingHurt为服务器路径，effect内仅level.addParticle无sendParticles专门S2C；不能据循环30次宣称远端可见。Inventory fallback.getAllWornItems返回空，fallback虽能find单件但原生listener不会遍历它，不能夸大为无Curios也生效。',
 'Boss拒控反馈节流须针对Boss/原因而非装备stack；明确最终拒绝与零伤/反击副作用，粒子API调用不等于已到客户端。')
add('botania-native-missile-immunity-acquisition-versus-existing-lock',
 [whole(x+'common/entity/MagicMissileEntity.java'),whole(x+'common/item/rod/UnstableReservoirRodItem.java'),s(items,193,193),s(items,394,401),s(items,431,435),s(x+'common/entity/BotaniaEntities.java',72,76),s(x+'common/entity/BotaniaEntities.java',130,150),s(init,147,187),s(init,193,215)],
 '真实法杖onUseTick资源初查→服务端spawnMissile先findTarget成功才spawn/声/请求扣资源；已注册MagicMissile原生tick再次findTarget，首次查询按实际玩家/mob/generic DamageSource过滤isInvulnerableTo并按阵营谓词选目标；没有目标或time>40服务端discard。',
 '一旦已有目标仍alive立即true，不再检查免疫、距离或资格；锁后获得无敌不会阻止追踪。近身hurt返回未查就discard，故尾迹或消失并非命中有效/immune回执。目标整数ID无UUID/epoch；友方弹每tick追当前中心，evil分支固定首次lock位置（本记录evil仅同类支持，不另计Boss发射生产）。碰撞原生onHitEntity仅相同target会discard，未在该回调扣伤；实际扣伤在tick AABB，不能把箭矢命中事件套用。法杖玩家循环的装饰粒子不保证产弹。',
 '目标选取时过滤免疫不替代执行前最终判定；回执只能在实际拒绝点生产，不能按锁定/尾迹/载体移除猜结果。')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'botania-native-batch28','credited_chains':keys,'rationale':'2个实际不同职责：原生Holy零伤+每stack冷却/防重入；原生法杖弹免疫资格选取与存活旧锁的不同再验策略。Sin反伤共享包装0，Odin来源tag模板0，Gaia既有阶段门不重记。1098文件导入0，Curios包装和粒子绘制循环0额外。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
