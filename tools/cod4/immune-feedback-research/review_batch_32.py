"""Native Reliquary rejection families; source/item-name variants merged."""
from ledger import B,O,record,verify
import json
r='P3pp3rF1y/Reliquary';p='src/main/java/reliquary/';keys=[]
def whole(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
shared=[whole(p+'Reliquary.java'),(p+'init/ModItems.java',101,114),(p+'init/ModItems.java',275,291),(p+'util/InventoryHelper.java',258,271),whole(p+'util/PlayerInventoryProvider.java'),whole(p+'util/PlayerInventoryHandler.java')]
def add(k,refs,chain,obs,lesson):
 record(k,r,refs+shared,chain,obs,lesson,'固定20de88066c41dcb19e50d1744d3edd3627064629；实际完整game方法/原生事件/注册/库存调用全文观察；无运行/客户端/声音验证，静态不证明观感或同步。普通阴阳不加灰字，未改正式源/资产/TODO。','native_refusal_settlement_and_explicit_cue');keys.append(k)
add('reliquary-native-hunger-conversion-shortcircuit-defenses',[(p+'init/ModItems.java',77,77),whole(p+'item/AngelicFeatherItem.java'),whole(p+'item/PhoenixDownItem.java'),whole(p+'item/InfernalClawsItem.java'),whole(p+'item/InfernalChaliceItem.java'),whole(p+'item/KrakenShellItem.java'),(p+'handler/CommonEventHandler.java',37,62),(p+'handler/CommonEventHandler.java',86,103),whole(p+'handler/HandlerPriorityComparator.java'),whole(p+'handler/HandlerPriority.java'),whole(p+'handler/IPlayerHurtHandler.java'),whole(p+'handler/IPrioritizedHandler.java')],
 '真实注册装备construct将具体IPlayerHurtHandler加入TreeSet；真实NeoForge LivingIncomingDamage→beforePlayerHurt按priority遍历，第一个canApply且apply真就break并cancel。Angelic fall/Claws fire/Kraken drown/Chalice firetag实际按食物>0和背包存在检查，原生apply将amount比例加入exhaustion并true。',
 '这是伤害转换为饥饿消耗的最终拒绝家族，所有仅来源/装备/比例替换合计1，不按五种名字加数。只判food>0，不判是否足以承担本次总消耗，未见实际拒绝FX；拥有item就生效非必须穿戴/持用。Chalice火tag与其它source对象identity范围不同，但不额外计；Phoenix fall额外HP>round(amount)区分致命与非致命，父构造也再次注册Angelic handler而不是仅Phoenix。全局TreeSet同priority compare固定1而非0，不满足反对称/自比较契约；可保留多个handler但不能宣称稳定同级顺序，可能重复注册；本次仅第一个成功消耗，不能合并所有装备同时credit。Phoenix死亡恢复/粒子本批仅支持，已有人物保命家族，不重复记原生死亡消费模板。',
 '多层Boss免疫入口要在确定最终原因和成功拒控处去重，不能每个监听都发；服务端布尔true应带清楚语义，消耗资源而拒伤也不是Boss拒控。')
add('reliquary-native-effect-denial-versus-zero-damage-prevent-cue', [whole(p+'item/WitherlessRoseItem.java')],
 '已注册WitherlessRose构造原生Applicable/PreDamage监听；Applicable匹配WITHER且玩家库存有Rose→DO_NOT_APPLY并addPreventParticles；真实LivingDamage.Pre匹配wither source对象→removeEffect、setNewDamage(0)并同cue。InventoryProvider逐实际槽/扩展handler首匹配返回。',
 '明确区分两个原生拒绝阶段：拒绝附加与已有伤害结算置0。一个共用cue家族合计1，不把两个wrapper或十粒子算独立实现。实际粒子仅level.addParticle，服务端回调没有sendParticles/专门S2C，不能宣称远端可见；又无节流，反复尝试可持续调用。hurt前阶段的source对象identity与DamageType tag不等价，不按同名键自动匹配第三方来源。移除效果先于置0，副作用并非空。',
 'Boss灰字/闪光必须从明确拒控原因生产并实际S2C派发；共享本地粒子函数不代表网络已通，也不代表不会刷屏。普通玩家免疫用原反馈即可。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'reliquary-native-batch32','credited_chains':keys,'rationale':'2个真实不同职责：饥饿转换拒伤/优先级首成功归属（多个来源模板合计1）；效果拒绝/已有零伤共用明确cue（合计1）。Phoenix复活模板、Twilight目标AI invis、Emperor fluid交互不额外计数；350源文件导入0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
