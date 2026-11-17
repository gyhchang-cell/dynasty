"""Publish manually reread combat receipt observations; no master research credit."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/cod4/audit-20261022'
HELPERS = BASE / 'guard-ownership-research/helpers'
specs = [
 ('coordinator-minecolonies/batch-001.json', 2,
  'tryAttack用nextAttackTime>=gameTime拒绝，真正允许时间严格大于截止；doAttack是void，调用后无条件推进下一攻击时间，无法由冷却推进反推造成伤害。',
  '横扫应明确伤害生产tick和END消费tick的允许年龄；不要把攻击尝试时钟或动画当成功回执。',
  '这是攻击尝试节拍，不是上游成功伤害回执机制；不能直接把其严格大于截止用到Dynasty而保留现有一刻错位。'),
 ('coordinator-minecolonies/batch-001.json', 8,
  'Druid完整doAttack先挥手，按敌友决定药水与效果，再投掷、按gotMaterial消耗素材、记录instantEffect、换手物、清当前威胁并给经验，没有等待命中确认。',
  '分清释放/消耗反馈和命中反馈；横扫命中回执不应在尝试挥击或付款时预先合成。',
  '具体投掷函数和药水命中在另一链，本方法只能证明尝试阶段状态修改；与普通弓释放的相似语义由Carson决定合并。'),
 ('coordinator-minecolonies/batch-001.json', 13,
  'Range doAttack一次调用可能发射一或两支箭，逐箭设属性/发射/播声，之后统一setLastHurtByMob和武器损耗；这些发生在实际弹体命中之前。',
  '一个动作可产生多个延迟伤害事件，视觉回执去重应按原动作归属，而不能把每个伤害事件都当新一轮横扫。',
  '本函数为void，未读到发射成功返回值；不能声称该setLastHurtByMob已经证明真实生命伤害；多箭概率/强度不能照搬。'),
 ('coordinator-minecolonies/batch-001.json', 14,
  'Melee doAttack在hurt前挥手、播声、点火及可能AOE；Huscarl分支同一目标分别调用PIERCE和普通hurt且均不接返回值，最后仍仇恨和损耗。',
  '成功伤害事件可来自同一原生动作的多段/次级目标；消费一次回执应保留全部原有伤害，避免用反馈门闩误吞第二段。',
  '与doAoeAttack是同一上级攻击链，虽各有独立控制流观察，最终不得仅因方法不同强行双计。未执行上游。'),
 ('coordinator-minecolonies/batch-001.json', 15,
  'AOE先按概率进入，再对候选逐个过滤、先击退后hurt；伤害分母是过滤前entities.size。即使没有有效受害者，仍播音/粒子并更新lastAoeUseTime。',
  '发动AOE和实际命中不能混淆；横扫回执应依据真实成功伤害而不是AOE冷却或粒子。一个窗口内多受害者只产生原定义的一次专用反馈。',
  '这是释放反馈不保证伤害的反例；与上级Melee同链可合并，不能为本任务改变伤害分母、概率或平衡。'),
 ('coordinator-minecolonies/batch-002.json', 3,
  'handleDamagePerformed先把部分伤害分给坐骑、执行离开/仇恨，再可能因Knight格挡返回false；只有本体super.hurt成功才加威胁与部分护甲/幸福副作用。',
  '原始hurt返回false不代表整次动作没有其他实体伤害。回执应绑定实际事件受害者/攻击源，防止用主目标结果抹掉次级成功伤害。',
  '调用者hurt入口已另读作支持不计；坐骑伤害与本体格挡是源码顺序观察，未声称已实机复现。'),
 ('coordinator-guardvillagers/batch-001.json', 2,
  'Guard tryAttack在super.tryAttack前已对踢击目标施加击退、设kickTicks、发实体状态并转头，随后无条件损耗武器，才返回父类攻击结果。',
  '不能通过动画、击退或耐久变化推断横扫真实命中；回执生产应放在确切成功伤害事实处，拒绝时也不额外制造命中特效。',
  '这是Fabric/Yarn实现观察，不是Forge可直接复制的API；与recruits的恒true返回并非同一返回值语义，仍需跨仓库去重。'),
 ('coordinator-guardvillagers/batch-001.json', 4,
  '远程attack先改盾牌时钟；弩分支shoot、弓分支造箭和spawnEntity后损耗主动手物品，方法为void，未验证spawnEntity返回值也未等待伤害。',
  '发射回执与命中回执分开，延迟到达不可复用一个无年龄约束的布尔标记；不能凭释放声音补假横扫反馈。',
  '与Minecolonies远程释放可因相同语义被合并；此处不声称确认弹体成功加入或命中，不以附魔/弹道计算额外计数。'),
 ('coordinator-guardvillagers/batch-001.json', 12,
  '弩tick将CHARGING、CHARGED延迟、READY_TO_ATTACK分开；完成蓄力后10至14刻才READY，可见目标才调用attack并清charged。友军避让分支停用物品并改回UNCHARGED。',
  '横扫消费应把记录事实、等待时间与消费分开，明确取消/失效条件；延迟不能同时要求事实tick恰好等于消费tick。',
  'stop已全文复读作同链支持；其未重置crossbowState/attackDelay，不单凭此断言可利用。弩蓄力状态机可与已有模板合并。'),
 ('halley-recruits/batch-001.json', 6,
  'onLivingHurt在服务端火枪兼容分支可能cancel事件，但cancel后仍继续alertTeam；允许分支先给经验再进入之后的伤害流程。',
  '监听器处观测结果不自动等于最终伤害成立；横扫不能凭进入hurt事件或前置经验副作用就生产成功标记。',
  '需要结合事件优先级及后续监听器才能确认最终取消结果；本条不把alertTeam同链辅助另计，也不声称已验证全部事件顺序。'),
 ('halley-recruits/batch-001.json', 19,
  'doHurtTarget先可能点火，调用entity.hurt取flag，仅附魔效果与lastHurtMob受flag控制；经验、饥饿、士气与武器损耗不受flag限制，最终恒return true。',
  '原生攻击入口返回true也不必然是成功扣血。回执须追踪实际伤害生产事实，成功动作与成功受害者事件不能混为一谈。',
  '与GuardVillagers返回父类结果不同；不因各项消费各算一个实现，整个完整方法仅一个建议位点。'),
 ('halley-recruits/batch-001.json', 26,
  'Recruit弩tick的AIMING到SHOOT跨状态延后；SHOOT重查存活/canAttack/非被动态，可能临时切为坐骑再恢复原目标。战略坐标火力则独立处理，无实体target也能开火。',
  '延迟回执需记录原始归属和维度/目标身份，执行时重查；有坐骑重选的行动不应只认旧主目标，两个路径也不能共享无语义过期标记。',
  '完整方法含两个射击分支，仍只提一个方法位点；不移植战略火力/PvP或扩大Dynasty功能。与GuardVillagers弩模板需最终语义审查。'),
]
records = []
for rel, index, observation, application, limits in specs:
    data = json.loads((HELPERS / rel).read_text())
    previous = (data['records'] if isinstance(data, dict) else data)[index]
    record = dict(previous)
    source = Path(record['source'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sourceSha256']
    snippet = '\n'.join(source.read_text().splitlines()[record['start']-1:record['end']])
    assert snippet.strip() == '\n'.join(record['text'].splitlines()).strip()
    record.update({
        'id': 'coordinator-receipt-' + hashlib.sha256((record['url'] + '/receipt-review').encode()).hexdigest()[:16],
        'observation': observation, 'application': application, 'limits': limits,
        'prior_guard_review_provenance': str((HELPERS / rel).relative_to(ROOT)),
        'reread_for': 'Fangtian successful damage receipt age, delayed consumption and duplicate secondary hits',
        'accepted': False, 'research_credit': 0, 'credit': 0,
    })
    records.append(record)
out = BASE / 'sweep-receipt-research/helpers/coordinator-receipt'
out.mkdir(parents=True, exist_ok=True)
assert not (out / 'batch-001.json').exists()
(out / 'batch-001.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
support = []
for rel, index in [('coordinator-minecolonies/batch-002.json', 1), ('coordinator-guardvillagers/batch-001.json', 11)]:
    support.append(json.loads((HELPERS / rel).read_text())['records'][index])
(out / 'supporting-methods-001.json').write_text(json.dumps(support, ensure_ascii=False, indent=2) + '\n')
(out / 'verification.json').write_text(json.dumps({
    'date': datetime.datetime.now().astimezone().isoformat(),
    'full_methods_reread_for_this_issue': 14, 'proposals': len(records), 'support_only': 2,
    'master_credit_added': 0, 'semantic_review_owner': 'Carson',
    'scope': 'Existing pinned sources reused with explicit prior provenance and newly written receipt-specific observations; never automatic cross-task credit.',
    'production_changes': False, 'game_clients_started': 0, 'servers_started': 0,
}, ensure_ascii=False, indent=2) + '\n')
print(f'Published {len(records)} proposals, 2 uncredited supports; master credit 0')
