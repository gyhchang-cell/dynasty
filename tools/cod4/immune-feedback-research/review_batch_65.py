"""Native effect acceptance explicitly checks the source faction, not target health."""
from ledger import B,O,record,verify
import json
r='TeamLapen/Vampirism';root='projects/vampirism/src/main/java/de/teamlapen/vampirism/';k='vampirism-native-builtin-feature-source-faction-effect-refusal'
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(k,r,[(root+'common/world/entity/ModEntityEventHandler.java',217,222),w(root+'data/ModDataPacks.java'),(root+'common/util/Helper.java',128,130),(root+'common/CommonServices.java',105,140),(root+'common/core/ModRegistryManager.java',87,101),w(root+'VampirismMod.java'),('projects/faction/src/main/java/de/teamlapen/faction/common/factions/FactionPlayerHandler.java',147,150)],
 '实际VampirismMod services注册Mod/Game buses→CommonServices注册ModEntityEventHandler→native MobEffectEvent.Applicable，effectSource是Player、内置undeadvampires已启用、source玩家是Vampire faction且effect为REGENERATION或POISON→DO_NOT_APPLY。ModRegistryManager挂原生AddPackFinders/OnDatapackSync，ModDataPacks装载内置可选包并由server当前selectedPacks同步ENABLED_PACKS集合。',
 '一个native效果最终接纳否决生产点1，两个effect常量/两事件注册helper合并。源码检查的是event.getEffectSource()，不是event.getEntity()受效果目标；不能将它表述为“任何吸血鬼目标都免疫毒与再生”，无source或非玩家source不满足此门。Helper.isVampire(Player)走FactionPlayerHandler当前faction，而非实体名/护甲/HP；包禁用直接不拒。内置包是可选feature false，不能声称默认开启。ENABLED_PACKS static由datapackSync替换，仅本链未见serverstop清空，下一次sync前行为不能静态冒充已验。',
 'Boss控制免疫应核对被控制目标和实际拒绝原因，不能把施加者身份误当目标免疫；普通阴阳体质继续没有灰字门槛。拒绝应用与之前效果已存在/自然到期不同，不能用状态最终为空反推此处触发。',
 '固定83c220f47cd030eed4c779c90f5786b261075869。完整最终方法/启用集合与原生调用入口已观察，固定tree确有内置包目录；资源tag原始全文未在本条读入，不把其条目计数，也不声称上游语义缺陷已动态复现。Faction通用底层/网络/客户端普通effect显示不另计，无游戏或正式源码/资产/TODO修改。','native_final_control_acceptance_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'vampirism-batch65-source-faction-effect-gate','credited_chains':[k],'rationale':'与既有freeze施法Boss准入不同的native Applicable最终点，绑定内置feature+实际施加者faction，非实体常量换壳；poison/regen合1。纯data pack发现/sync集合属于该生产链0额外。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
