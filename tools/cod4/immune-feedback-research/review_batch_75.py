"""One anchor-qualified terminal refusal; ordinary charged totem variants are zero."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='goety-native-arca-qualified-death-refusal-teleport-result-not-checked'
record(k,r,[f('common/events/SoulEnergyEvents.java',60,61),f('common/events/SoulEnergyEvents.java',274,426),f('common/events/SoulEnergyEvents.java',428,454),f('common/blocks/ArcaBlock.java',48,132),w('common/events/ArcaTeleporter.java'),f('utils/SEHelper.java',76,78),f('utils/SEHelper.java',149,155),f('utils/SEHelper.java',314,328),f('utils/SEHelper.java',548,592),f('common/capabilities/soulenergy/SEImp.java',51,117),w('common/capabilities/soulenergy/SEProvider.java'),f('common/events/spell/GoetyEventFactory.java',80,87),f('utils/LichdomHelper.java',16,23),f('utils/LichdomHelper.java',85,87),w('common/network/server/SPlayPlayerSoundPacket.java'),f('common/network/ModNetwork.java',73,74)],
 '实际ArcaBlock.setPlacedBy保存anchor pos/dimension并setSEActive，use可设置8格内revivePos；原生FORGE事件订阅SoulEnergyEvents.onLivingDeathEvent：玩家SEactive+anchor非空+配置允许，按Lich/资源条件选择setHealth1/清效果/加保护/尝试teleportToArca/扣资源/取消死亡，并给本玩家SPlayPlayerSoundPacket。同维standUp与worldborder、跨维serverLevel/standUp/ITeleporter均在实际teleport方法；receiver.enqueueWork取当前proxy Player播放。',
 '一个有世界锚点/资源/巫妖模式条件的终结拒绝政策1，普通持物满魂图腾及非active totem家族并既有资源复活家族0，不按三种Lich配置/保护效果/S2C wrapper拆数。teleportToArca返回false可能来自无standup/世界不存在，调用者不检查而照样1HP、发声、扣资源并cancel；不可用声音声称回锚成功。LichNoSERemove=false分支低资源也拒死并加SoulHunger；true却资源不足则移除Lich、粒子但不cancel。付款经过可取消Loss事件，且decreaseSE仅检查现值>0、不做足额事务，减不足夹0；上层忽略付款返回，不能称不可绕过的已支付才拒绝。',
 'Boss拒控与传送/资源/复活是不同reason。回执应证明其对应拒绝而不夸大附带动作成功；灰字不能从死亡取消或音效泛化，也不能把普通体质与Boss拒控混用。声音可用既有原版资源，但此例WITHER_DEATH不是本需求嗡声方案。',
 '固定来源与native订阅、关键方法全文已读。复活不是Boss控制免疫，作为明确终结拒绝/失败动作回执边界参考；未证明Goety当前源可编译、未运行游戏、未验具体客户端连接/声音。ModNetwork注册行复用已读整注册链证据，不另加数。','native_anchor_qualified_terminal_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'goety-batch75-arca-terminal-policy','credited_chains':[k],'rationale':'世界锚点/巫妖资格与传送失败仍取消死亡的最终政策独立；普通魂图腾reset+buff+35事件与已有Ars/TF资源图腾家族合并0，副手主手不拆分。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
