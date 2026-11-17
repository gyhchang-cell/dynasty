"""IE native shield refusal and aggregate equipment electric settlement."""
from ledger import B,O,record,verify
import json
r='BluSunrize/ImmersiveEngineering';p='src/main/java/blusunrize/immersiveengineering/';a='src/api/java/blusunrize/immersiveengineering/api/'
def f(s,x,y):return p+s,x,y
def w(s,api=False):
 rel=(a if api else p)+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
common=[f('ImmersiveEngineering.java',93,115),f('ImmersiveEngineering.java',117,204),f('common/IEContent.java',104,165),f('common/register/IEItems.java',298,301),f('common/register/IEItems.java',322,345),f('common/register/IEItems.java',376,388),f('common/register/IEItems.java',418,421),f('common/EventHandler.java',242,289),w('common/items/IEShieldItem.java'),w('common/util/IEDamageSources.java')]
k1='ie-native-shock-shield-source-discard-refusal-and-energy-paid-rearm'
record(k1,r,common+[f('common/util/Utils.java',368,382),w('common/items/UpgradeableToolItem.java'),w('common/items/upgrades/ToolUpgrade.java'),w('common/items/upgrades/ToolUpgradeItem.java'),w('tool/upgrade/Cooldown.java',True)],
 '实际modConstruction→IEItems.Misc.SHIELD/SHIELD_SHOCK注册；Workbench重算IUpgrade进UPGRADE_DATA。实际setup注册EventHandler→原生LivingDamageEvent.Pre目标Player正在使用IEShield、originalDamage>=3、非BYPASSES_ARMOR且isBlocking且有sourcePos方向dot<0→hitShield。SHOCK存在且CD0：projectile+direct非null则discarddirect、newDamage0；Living source.entity近距平方<4另调用Tesla.apply；任一成立置CD40并播spark。',
 '一个前向盾源资格+销毁投射物整次拒伤点1，反击/声音/资源rearm都同链0。SHOCK初始IDLE即使0energy也可第一次触发，触发不即时扣电；inventoryTick仅服务端且!inHand或!blocking，花10energy才减少1CD，两个升级分开扣。持续举盾不会自然恢复，缺电CD也不会自动到期。若仅近距反击，不设置newDamage0；不能将任一spark视为确已拒伤。Utils是BYPASSES_ARMOR而非BYPASSES_SHIELD，不检测piercing，方向判据包含俯仰的viewvector。Tesla.apply返回dmg>0而不取hurt布尔，因此反击实际伤害/控制成功不能由它反推。没有Boss免控/灰字。',
 'Boss需要自己的每目标回执节流，不复用声音或CD代表拒控成功。区分尝试消耗、支付后恢复和真正拒绝；声音优先现有适当原版资源，无须造新音频。',
 '固定75a27f03e4243544243567e8d5c38d336f4f10f4，完整原生event、shield、升级重算/IDLE/tick/方向方法已读。未审具体NeoForge此版damage callback次序、未跑游戏/听音或声称实际动画通过。','native_directional_projectile_refusal')
k2='ie-native-electric-equipment-aggregate-mask-refusal-before-hurt'
record(k2,r,common+[w('tool/IElectricEquipment.java',True),w('common/items/FaradaySuitItem.java'),f('common/items/SkyhookItem.java',215,222)],
 '同一原生Hurt盾/电包反击调用causeTeslaDamage→ElectricDamageSource.apply：Living先IElectricEquipment.applyToEntity遍历全部EquipmentSlot及持物，单次新HashMap传各onStrike；FaradaySuit在source.level<1.75时按物品ArmorType.ordinal OR位，等于15把共享dmg置0；>=1.75每件令dmg*=1.2且非creative损耐久2；最终apply仅dmg>0才e.hurt并返回dmg>0。Skyhook的WIRE_SHOCK+INSULATED+骑hook或正在用物品归零变体同族0。',
 '一个原生电击结算前聚合四种装备类型的拒伤实现1，不按四件/电线等级/skyhook常量重复。检查按物品Type而非实际eqSlot，因此不能静态宣称必须正确穿齐，手里持一件也参与同次mask。cache仅本次打击有效，不跨目标，不是免控/伤源全局免疫。高强电源不拒绝反而逐件放大且损耐久。apply未检查e.hurt返回值：正dmg即true；电包据此加STUNNED可能在hurt被其他系统拒绝后仍尝试控制，addEffect返回也未验。低强全套dmg0使applyfalse，原生上层不加该stun，但spark照常。故“无实际伤害”与“拒控”不能由hurt=false统一归因。',
 '将Boss明确控制拒绝与伤害结算、免疫装备提示区别；灰字只绑定目标真实拒控reason，并确保不可被普通体质type9或声响误触发。',
 '固定版本，完整ElectricDamageSource/IElectricEquipment/Faraday及原生event全文，Skyhook完整onStrike；不是把通用迭代基础设施当计数。WireDamageHandler另已全文读，其wrapper和能量结算本批0。未启客户端/并发或真实声音测试。','native_aggregate_equipment_damage_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'ie-batch72-shield-electric','credited_chains':[k1,k2],'rationale':'原生方向盾投射源销毁拒伤与电击前装备位mask聚合拒绝为独立最终点；反伤声音/布尔/资源恢复均上下文0，skyhook同电装备归零变体0，未计普通闪光、机器人互动、注释死代码。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
