"""Native bound poppets: successful substitute settlement versus remote protection."""
from ledger import B,O,record,verify
import json
r='Moriyashiine/bewitchment';p='src/main/java/moriyashiine/bewitchment/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def resource(s):
 s='src/main/resources/'+s
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[f('mixin/poppet/LivingEntityMixin.java',70,123),f('api/BewitchmentAPI.java',63,131),f('api/BewitchmentAPI.java',159,169),f('api/BewitchmentAPI.java',191,200),w('api/item/PoppetItem.java'),w('api/misc/PoppetData.java'),w('common/recipe/TaglockCraftingRecipe.java'),w('common/registry/BWRecipeTypes.java'),f('common/item/TaglockItem.java',203,272),f('common/item/TaglockItem.java',282,287),f('common/registry/BWObjects.java',309,315),f('common/registry/BWObjects.java',381,388),f('common/registry/BWObjects.java',417,435),f('common/Bewitchment.java',61,222),w('common/BWMixinPlugin.java'),resource('fabric.mod.json'),resource('bewitchment.mixins.json'),resource('data/bewitchment/recipes/taglock_crafting.json')]
k1='bewitchment-native-bound-living-substitute-success-gates-damage-nullification'
record(k1,r,common+[w('common/registry/BWDamageSources.java'),resource('data/bewitchment/recipes/vampiric_poppet.json')],
 'Fabric metadata真实主入口与mixin配置启用poppet.LivingEntityMixin（plugin只过滤Apoli）；BWObjects/recipe types实际注册→原生TaglockCraftingRecipe将有UUID的taglock复制到空人偶→server applyArmorToDamage HEAD入参修改。amount>0且受伤者Player非vampire，自己主/副手inventory找已绑定VAMPIRIC_POPPET→遍历server所有world用UUID解析活体owner→owner非vampire且非自己，并且owner.damage(VAMPIRE,amount)为true→损耗人偶并把当前amount返回0。',
 '一个真实替伤结算生产点1，绑定/查询/耐久包装合并，不能按被替代玩家或人偶型号重复。人偶可绑定跨维度活体且不检查距离/视线，但只从受伤玩家自己的main+offHand找，虽通用getPoppet能扫所有库存，本分支没有用；armor槽不包含。taglockOwner离线/死亡/未加载则getPoppetFromInventory找不到；首次匹配owner若自己或vampire，会留在此候选而非继续找后面合格者。必须实际owner.damage成功才归零，替代方拒伤不产生“转移成功”。真实调用源为无attacker的VAMPIRE DamageSource；上游该源具体tags原始资源未读不声称所有替代目标可被击穿。损耗按amount取int，wolf familiar随机半额，极小伤害可取整0；不预留剩余耐久，当前击可完整归零后再损耗销毁。没有免疫文字/原生回执S2C，此为结算语义参考。',
 'Boss灰字必须从最终拒控点给出明确reason，不用hurt=false推断；替代伤害链示范正向成功条件与原始伤害归零分离。不能对被转移方受伤或普通阴阳体质错误发Boss免疫。',
 '固定842cd9777b7bde2a0208099d5184baf88f24f63a，核心完整方法/绑定recipe/实际注册已读。getFamiliar只读查询及wolf分支，未审完整熟悉物获取玩法；原版damage流水线、上游mixin执行相对顺序未运行，静态不保证最终客户端数字或音画。未修改正式源码/资产/任务。','native_damage_redirection_settlement')
k2='bewitchment-native-uuid-remote-poppet-source-denial-and-world-key-lifetime'
record(k2,r,common+[w('common/world/BWWorldState.java'),w('common/block/entity/PoppetShelfBlockEntity.java'),w('client/packet/SyncPoppetShelfPacket.java'),f('client/BewitchmentClient.java',93,93),resource('data/bewitchment/recipes/protection_poppet.json')],
 '同一真实applyArmorToDamage方法的PROTECTION_POPPET来源谓词分支→getPoppet(world,item,this)：worksInShelf先扫描server各world持久化poppetShelves按UUID找绑定人偶，再扫全部在线玩家主库存+副手；命中后按伤害int损耗/可能销毁，PoppetData.update写持久化标dirty并条件sync，最后返回0。Shelf原生onUse放入/取出人偶，BWWorldState NBT持久化，SyncPoppetShelfPacket由tracking发送/已注册client receiver解包当前world blockEntity更新clientInventory。',
 '一个UUID跨世界绑定资源替身的最终保护家族1；15个环境伤害常量/来源tag只作同一policy0额外，judgment减到四分之一和fatigue加weakness不冒称完全免疫。与Vampiric分支不同，这里不需目标活体承伤成功；owner已给定，按UUID静态匹配，全server远程携带者可保护目标，无距离或在线同维门。getPoppet命中world即使chunk未加载仍返回，loaded仅决定shelf.sync；不是只限已加载架子。PoppetData仅存longPos/index没有维度：update从各world第一个同坐标shelf更新后return，不再确认原绑定UUID，存在跨维同坐标误关联的静态风险，未动态复现。server sync又按接收玩家world查inventory；client只持pos/NBT且执行时无world空检验/维度代际，不能当安全Boss目标反馈协议。耐久损耗成功与否不作为amount=0的门，毁掉最后人偶该击仍归零。',
 '可借鉴实际UUID绑定查找与明确保护来源，但Boss短寿命浮字应携带足够维度/实体代际并清理，避免仅numericId或坐标误回放；实例消失与自然过期/拒控不同。持久化与网络同步是支持同一政策，不另拆信用。',
 '固定版本、完整核心方法/世界持久化/库存/网络收发已观察；client注册行仅证明注册，完整onInitializeClient其他视觉代码不在本条声明。Shelf block拆除钩子和原版伤害后续未验，不能声称架子销毁后保留或清理已复现，也无实际画面/声音/TCP证据。只读上游与研究记录，无资产/正式Java/TODO修改。','native_final_damage_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'bewitchment-batch67-bound-poppet-settlement','credited_chains':[k1,k2],'rationale':'同一全文修改方法内两种独立最终生产点：必须活体替伤成功才归零 vs source policy匹配绑定资源直接归零。全局绑定/持久化/收包仅各自链支持0，15环境来源常量0，recipe注册/tooltip0；普通免控未附加灰字要求。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
