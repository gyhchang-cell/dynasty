"""Explicit full-method review, no automatic master credit or upstream execution."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[5]
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/guard-ownership-research/helpers/coordinator-guardvillagers'
rows=json.loads((BASE/'candidate-methods.json').read_text())
manifest=json.loads((DOC/'source-manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
annotations=[
(0,'setTarget尾部注入发现村民/守卫遭锁定时，向附近空目标守卫转派攻击者；铁傀儡以守卫为目标时清空。','外部Mixin也能直接setTarget，必须在最终伤害边界维持归属安全。','循环内IRON_GOLEM判断用的是this攻击者类型而非候选mobEntity，不能概括为仅守卫与傀儡接收；只静态研究不照搬。'),
(19,'以持久UUID查当前世界玩家，并按followHero配置及村庄英雄状态解析有效owner；IllegalArgumentException时返回空。','持久身份和当前可用owner不是同一概念，应在攻击时重新解析有效关系。','这是英雄跟随机制，不是王朝装备租约；不导入英雄状态门槛。'),
(23,'踢击时先向传入活体施加击退、发状态并转头，损耗武器后才调用super.tryAttack。','最终伤害拒绝还须放在击退/动作/耐久副作用之前，不能仅让末尾hurt返回false。','方法内没有owner过滤，是相关反例；强转LivingEntity依赖上游，不保证任意Entity参数安全。'),
(46,'同时注册近战/弓弩、村庄保护、报复、主人受击/攻击、怪物分类及愤怒玩家目标选择器。','逐入口枚举选敌通道，改一个最近玩家选择器不能保证所有赋目标路径都安全。','配置会启用不同分支；只研究分层入口，不为王朝新增村庄愤怒或PVP。'),
(48,'武器类型决定弩shoot或构造弓箭；设置附魔、弹道并spawnEntity后损耗主动手武器。','射击最终入口若只相信参数target，状态变化后仍可能放箭，应核查目标许可的位置。','这里没有再次canTarget；没有执行上游，不能据静态入口声称真实误伤。'),
(55,'统一canTarget同时拒绝黑名单、英雄、owner、村民、铁傀儡和其他守卫，再走super。','在统一候选谓词中硬拒绝归属和同盟，比只在AI尾部清目标更完整。','目标为null时此实现先解引用，王朝实现需自己处理空/死亡/过期，不照抄。'),
(59,'setTarget遇守卫、村民、铁傀儡直接返回；其他对象和null才调用super。','直接目标赋值也可加防线，尤其防外部事件绕过选择器。','拒绝赋值不等于清旧目标；这里没拒绝owner/英雄，不能视作完整归属策略。'),
(84,'遍历近邻村民对玩家的声望，低于配置阈值记为目标；最终排除英雄、旁观和创造玩家。','获取玩家目标需明示原因与过滤，不应把附近玩家无条件当敌人。','这是村庄声望政策，王朝不新增该政策；villageAggressorTarget未在本方法开头清空，不能假设每轮完全重新选择。'),
(94,'近战目标距离及攻击冷却通过后，重置冷却、停止举盾/使用、设置盾冷却、挥手并tryAttack。','最终近战入口不仅伤害，还有动作和冷却；所有者拒绝应在这些副作用前。','这是GuardEntityMeleeGoal嵌套方法；本方法没有额外敌友判断，依赖统一过滤和tryAttack边界。'),
(107,'owner为空就拒绝；否则读取主人攻击对象及攻击时间，只在新时间戳且canTrack通过时启动。','同一主人攻击事件用时间戳去重，不能每个AI周期重复转移仇恨。','canTrack额外拒绝商人/守卫、start保存时间戳均已全文读，作为同链支持；与其他模组原版主人攻击目标模板需最终去重。'),
(116,'弓AI持续跟踪目标、视线计数和距离；失视超过60tick取消使用，20tick拉弓后调用attack，巡逻时抑制横移。','长动作期间每次发射仍需考虑目标关系变化，视线与非空不代表归属有效。','整体有原版弓AI模板；若无足够独立语义应降支持，不把路径/拉弓分支拆开凑数。'),
(121,'弩AI停止时清attacking、target、seeTime；若使用物品则停止并取消charging，恢复站立姿态。','目标/蓄力/姿态等残余状态要一起清理，不能只删target引用。','没有在本方法重置crossbowState枚举或清已装填NBT，不能声称完整清空每种装填状态。'),
(124,'弩AI管理UNCHARGED/CHARGING/CHARGED/READY状态；检测友军阻挡且配置启用时先取消使用/充能、重定位并退回未蓄状态。','在发射前处理友军安全和动作取消，避免先射击再下周期清目标。','此配置分支按原文friendlyFire真启用，不能凭名称反推配置含义；未运行上游或复制其机制。'),
(125,'扫描5格附近非主目标，把owner、村民、守卫、傀儡列为友方；方向点积、可见性与4格距离成立时报告阻挡。','友方遮挡检查与主目标合法性是不同层，远程保护要审查两者。','dotProduct<1不是精确射线相交，不宣称挡在弹道上；与弩tick同一安全链最终可合并信用。'),
(132,'服务端按玩家当前世界的实体ID取守卫，切换follow并用实际连接玩家UUID重写owner。','身份应来自真实发送者，不能信任包内伪造UUID；也要检查实体操作权限和范围。','本方法未验证既有owner/距离，不能称安全网络授权范例；read/write/getType包装不计。'),
]
records=[]
for index,observation,application,limits in annotations:
    r=rows[index];source=ROOT/r['source_local'];raw=source.read_bytes()
    assert sha(raw)==r['source_sha256']
    f=next(f for f in manifest['files'] if f['local']==r['source_local'])
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==f['git_blob_sha1']
    text=r['excerpt'];assert '\n'.join(raw.decode().splitlines()[r['line']-1:r['end_line']]).strip()=='\n'.join(text.splitlines()).strip()
    normalized=re.sub(r'\s+','',re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S))
    records.append(dict(repo=manifest['repo'],commit=manifest['commit'],path=f['path'],source=str(source),sourceSha256=sha(raw),
                        start=r['line'],end=r['end_line'],name=r['name'],text=text,excerptSha256=sha(text.encode()),normalizedSha256=sha(normalized.encode()),
                        url=f"https://github.com/{manifest['repo']}/blob/{manifest['commit']}/{f['path']}#L{r['line']}-L{r['end_line']}",
                        observation=observation,application=application,limits=limits,credit=0,decision='proposed; master semantic dedup pending'))
assert len({r['normalizedSha256'] for r in records})==len(records)
batch=dict(repo=manifest['repo'],commit=manifest['commit'],proposed_records=len(records),master_credit_added=0,records=records,
           source_branch='1.20.1',mapping='Fabric/Yarn; conceptual source reference, not a Forge patch',upstream_executed=False,game_started=False,production_changed=False,
           support_methods_read_full=[108,109,129,130,131,126],
           excluded_without_credit=['isOwner getter-style forwarding','HeroHurtBy timestamp mirror as additional credit','Patrol packet sibling','getter boilerplate','general movement/regeneration and equipment data'],
           source_files_acquired_and_blob_verified=len(manifest['files']))
(DOC/'batch-001.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:batch[k] for k in ('proposed_records','master_credit_added','source_files_acquired_and_blob_verified')}))
