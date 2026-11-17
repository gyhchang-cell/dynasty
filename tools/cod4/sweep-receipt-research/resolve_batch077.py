"""Manually reviewed spear release, delayed collision/return and replication chain."""
import json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';cs=[json.loads(l) for l in (O/'candidates.jsonl').read_text().splitlines()]
P='build/item-use-references/Moriyashiine__bewitchment/src/main/java/moriyashiine/bewitchment/'
E='tools/cod4/legacy-migration-acceptance/.work/sources/Moriyashiine__bewitchment/src/main/java/moriyashiine/bewitchment/common/entity/projectile/HornedSpearEntity.java'
A='tools/cod4/legacy-migration-acceptance/.work/sources/Tslat__Advent-Of-Ascension/source/'
def m(p,*ns):return [[p,n] for n in ns]
n='全文HornedSpearItem→HornedSpearEntity全类及SyncHornedSpearPacket：蓄力>=10 server先伤耐久再copy整stack给弹体，spawn返回未检查即发仅当时tracking玩家自定义ID+stack包/音，非创意再扣1，不能用cue证明spawn或伤害。命中先dealtDamage=true再damage，失败也不重试，伤害真才附魔回调/命中特效，Enderman真伤直接return不反弹；检测owner当前minion可跳过碰撞，属于当前所有权而非发射快照。玩家owner且已命中/入地>4/越底后每tick归航，owner失效允许拾取才落item然后discard；允许拾取不走普通age过期，dealtDamage/Spear持久。onPlayerCollision UUID使用==引用比较而非equals，不夸大为可靠owner值匹配。自定义包receive先解码stack再client.execute，在当前world按entityID直接cast无null/type/UUID/原维度/epochguard；初次tracking若已晚失配会异常，没有重试/同tick要求，晚追踪支持本轮未找完整通路不能声称已同步。整条实际释放→首命中锁→延后owner返还/客户端物品载荷链1，不拆多命中分支/NBT/发包；与已审ThrownTool原槽回收和scheduler重力玩法不同。'
p=O/'review-resolutions.json';d=json.loads(p.read_text());assert not any(e['candidate_index']==3883 for e in d['entries']);d['entries'].append(dict(candidate_index=3883,candidate_id=cs[3883]['candidate_id'],decision='accepted',observation=n,supporting_candidate_indices=[],reviewed_at=datetime.datetime.now().astimezone().isoformat()));p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
S=m(P+'common/item/HornedSpearItem.java','use','onStoppedUsing','getMaxUseTime')+m(E,'onEntityHit','getEntityCollision','onPlayerCollision','tick','age','readCustomDataFromNbt','writeCustomDataToNbt','isOwnerAlive')+m(P+'client/packet/SyncHornedSpearPacket.java','send','receive')
r=json.loads((O/'reviews/batch-177.json').read_text())[0]
S2=m(A+'client/player/ClientPlayerDataManager.java','handleKeyInput')+m(A+'player/AoAPlayerEventListener.java','onKeyPress')+m(A+'player/ability/innervation/StunStrike.java','handleKeyInput','handleAfterAttacking')+m(A+'player/ability/innervation/InnervationDodge.java','handleKeyInput','handleIncomingDamage')
(O/'manual-chain-spec-077.json').write_text(json.dumps([dict(candidate_indices=[3883],observation=n,supporting_methods=S),dict(candidate_indices=[289],observation=r['observation'],supporting_methods=S2)],ensure_ascii=False,indent=2)+'\n')
