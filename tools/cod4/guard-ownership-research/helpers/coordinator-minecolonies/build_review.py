"""Assemble explicitly reviewed candidates; only Herschel may credit the master ledger."""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
DOC = ROOT / 'docs/cod4/audit-20261022/guard-ownership-research/helpers/coordinator-minecolonies'
sys.path.insert(0, str(ROOT / 'tools/cod4/guard-ownership-research/.work/python39'))
from tree_sitter import Language, Parser
import tree_sitter_java
parser = Parser(Language(tree_sitter_java.language()))
manifest = json.loads((DOC / 'source-manifest.json').read_text())
methods = []
sha = lambda data: hashlib.sha256(data).hexdigest()
for source in manifest['files']:
    path = ROOT / source['local']
    raw = path.read_bytes()
    assert sha(raw) == source['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == source['git_blob_sha1']
    def walk(node):
        if node.type == 'method_declaration' and node.child_by_field_name('body'):
            name = node.child_by_field_name('name')
            methods.append({'repo': manifest['repo'], 'commit': manifest['commit'], 'path': source['path'],
                            'source': str(path), 'sourceSha256': sha(raw),
                            'start': node.start_point.row+1, 'end': node.end_point.row+1,
                            'name': raw[name.start_byte:name.end_byte].decode(),
                            'text': raw[node.start_byte:node.end_byte].decode()})
        for child in node.children:
            walk(child)
    walk(parser.parse(raw).root_node)

# Each entry was read in full with the associated source context. Thin forwarding
# methods, getter boilerplate, wake-up variants and guard travel economy are not proposed.
annotations = [
('AttackMoveAI','move','每轮先checkForTarget，再取威胁表；可见刷新lastSeen，失视超过1200tick重置；五次寻路失败降威胁并可放弃。','攻击前持续验证与视线/路径失败回收分开，不能以定期选敌代替即时有效性。','追踪表是该模组设计，不新增到王朝；不能据寻路正常推断目标归属安全。'),
('AttackMoveAI','resetTarget','调用父级失效目标清理后，将targetPath归空、pathAttempts归零，避免复用旧追击状态。','拒绝旧目标后还应排查行动缓存，别让旧导航继续驱动一次攻击。','父级重置和此导航重置是不同状态；若主研究按同一完整失效链计数可并为支持。'),
('AttackMoveAI','tryAttack','依次校验checkForTarget/canAttack、冷却和距离、视线后才doAttack，并把下次时间设为当前tick加间隔。','最终攻击入口先复核目标，再做伤害/动作，不能等AI结束才清目标。','canAttack默认真；安全依赖动态checkForTarget，不能误读为此布尔函数自带友军筛选。'),
('TargetAI','checkForTarget','旧目标死亡先回调并清引用，再取最高威胁；isEntityValidTarget通过才更新target与onTargetChange，否则resetTarget。','重选与续用都走同一有效性谓词，不给陈旧目标一个攻击窗口。','死亡回调与威胁表清理次序未在上游运行，所有结论仅静态控制流。'),
('TargetAI','isEntityValidTarget','先排除自身/null/死亡/超追踪范围/FakePlayer；最后受伤来源直接返回真，其他目标才走isAttackableTarget。','基础生存与距离门必须在特殊分支前；学习反例：报复不能越过王朝owner/非Enemy硬拒绝。','这里允许反击非Enemy，不能原样复制为王朝护卫的选择策略。'),
('TargetAI','resetTarget','目标存在时清匹配的lastHurtMob与lastHurtByMob，威胁表标无效，然后清target。','仅setTarget(null)可能留下其他复仇来源；逐项检查原生AI再抓回旧目标的通道。','王朝不新增威胁表；不能把该来源清理当作已证明原生HurtByTargetGoal所有缓存都消失。'),
('TargetAI','searchNearbyTarget','已有有效目标就返回；否则活体列表逐一检查skipSearch、完整目标谓词及视线后添加威胁。','目标获取应使用和继续攻击一致的谓词；扫描存在不等于允许攻击。','skipSearch返回真会中止整次扫描，不是只跳过单实体；不建议额外引入此中止机制。'),
('TargetAI','isAttackableTarget','默认只接受Enemy并拒绝与user同Java类实例，是具体类型的敌对分类。','保留王朝现有Enemy基线并另加所有者/同盟硬排除，不把玩家类型自动当敌人。','同类排除不是UUID同主关系；子类覆盖和报复捷径另有策略。'),
('DruidCombatAI','doAttack','通过守卫敌对分类选择负面或支援药水，并把相同分类作为溅射目标predicate传给DruidPotionEntity。','范围效果也应逐受体复核友军策略，不能只筛主目标后对周边无差别结算。','药水是支援职业专用，王朝租约守卫不复制药水、职业或治疗玩法。'),
('DruidCombatAI','isAttackableTarget','除敌对对象外，也接受有威胁目标的实体或最近30秒受伤玩家，并排除已受德鲁伊效果者。','不同用途的候选可以更宽，但攻击类型必须在最终结算区分，不把候选等同伤害许可。','这是治疗/支援的候选语义，不能放宽王朝护卫的非Enemy拒绝。'),
('DruidCombatAI','searchNearbyTarget','有效目标优先；新扫目标经存活、视线与有效性后入表，并统计已有效果对象，限制支援目标密度。','候选数量上限与敌友许可是两层边界；达到效果配额可停止新增支援。','与TargetAI扫描骨架相同，仅职业配额分支构成差异；去重若不足独立则并为支持零信用。'),
('RangeCombatAI','canAttack','查询可用装备并实际持握；在下次攻击时间与举弓延迟的条件下开始使用，找不到武器即false。','攻击就绪检查是实物与动作状态，不能只看AI是否有target。','装备就绪不提供所有者安全；本批不再给近战同构持械检查增加信用。'),
('RangeCombatAI','checkForTarget','完整调用父级目标检查；无效且仍在使用武器时stopUsingItem，然后返回有效性结果。','攻击目标失效要取消正在执行的远程使用动作，避免残留蓄力。','这是远程动作取消，不证明飞行中的旧投射物也已取消或重新筛选。'),
('RangeCombatAI','doAttack','近敌随机避让否则停止；依研究可双箭/穿透，真实构造箭矢发射后记录受伤来源并损耗弓。','审查最终投射物发射入口是否依赖上游筛选，别认为创建箭时自动有同盟验证。','本方法没有再次isEntityValidTarget；相关前置在AttackMoveAI.tryAttack，引用此处作为边界对照而非安全范例。'),
('MeleeCombatAI','doAttack','按PVP配置选择伤害来源、火附魔、AOE、穿透拆分伤害，再记录仇恨并损耗武器。','伤害源选择与敌友许可无关；最终近战结算仍需王朝自己的租约有效性门。','上游PVP只是来源类型分支，绝不能给王朝新增PVP规则；本方法本身未再次验证目标。'),
('MeleeCombatAI','doAoeAttack','研究及随机条件下扫描近邻，逐个排除自己、无效目标、盔甲架后才击退和hurt。','AOE需要每个受害者的真实许可，主目标通过不能授权所有周围实体。','伤害分母是整个扫描列表数量而非有效目标数；不复制该数值设计。'),
('AbstractEntityAIGuard','startHelpCitizen','仅canHelp位置通过才向攻击者加20威胁，并注册一次进入ATTACKING的状态目标。','求援事件可以绕开普通扫描，故统一目标谓词和最终伤害边界都需覆盖事件路径。','这里只校验能否求援，不直接做敌友验证，不能把加仇恨本身当攻击许可。'),
('AbstractEntityAIGuard','canHelp','仅无目标或睡眠且可打断时接受；固定驻守任务还检查追击范围，成功前唤醒。','守卫的外部求援也受当前动作与任务半径限制，不无条件覆盖进行中的目标。','此方法主要是行动许可；友军安全依后续目标检查而非醒来这一动作。'),
('AbstractEntityAIGuard','isWithinPersecutionDistance','以任务参考点到实体的距离平方，和任务追击距离加攻击范围的平方比较。','目标范围应有明确参照点与单位，不能混淆owner附近和守卫当前位置。','getTaskReferencePoint/getPersecutionDistance已全文复核但作为同一距离政策支持，不另给两份信用。'),
('AbstractEntityAIGuard','canBeInterrupted','战斗计时未清、ATTACKING、存在lastAttacker、集结或跟随时拒绝打断，否则交给父级。','目标清理与状态机忙闲是不同通道；已有攻击状态不能依赖低频任务更新来变安全。','这是非战斗工作的打断策略，不在王朝新增集结/跟随任务系统。'),
('AbstractEntityAIGuard','isAttackableTarget','配置怪物表与建筑排除表可放行怪物；玩家须敌对rank或有效袭击身份，其他殖民地守卫须袭击资格。','明确白名单和权限分支优于“不是owner就可打”；王朝仅保留原Enemy政策并检查同盟。','该权限制度不同于王朝，不复制殖民地rank/PVP机制；怪物快路径先于colony空判断。'),
('ThreatTable','addThreat','排除FakePlayer后按实体引用查重；新条目给距离/低血量威胁，追加威胁再排序。','仇恨收集和攻击授权是不同层；受击输入不能替代owner/同盟检查。','本方法未做同盟筛选；王朝不新增威胁分数系统。'),
('ThreatTable','getTarget','按远近采用1.3/1.1倍仇恨切换，过期或不能当敌人的条目移除并递归选下一个，负仇恨不返回。','续用目标必须检查时效，非法候选移除后再选择，而非等下一扫描周期。','current是ThreatTableEntry，其instanceof IThreatTableEntity分支未证明可达；不据此声称触发相互仇恨。'),
('ThreatTable','markInvalidTarget','空表退出，死亡则移除；活体目标用-1标无效并移至尾部，重新置当前索引。','暂时失效与实体死亡可分别处理；无效目标不应在同tick继续造成伤害。','与resetTarget是调用链不同节点，若主研究按整链合并则可降为支持。'),
('ThreatTableEntry','addThreat','额外威胁为0直接退出；非零威胁把结果下限钳为0并刷新lastSeen。','威胁更新会重新激活-1无效条目，说明最终攻击仍需硬性友军门，不可依赖标记一次永久安全。','0增量不刷新时间；数学钳制本身不算独立参考，信用仅建议真实失效/再激活策略。'),
]
records=[]
for cls,name,observation,application,limits in annotations:
    hits=[m for m in methods if Path(m['path']).stem==cls and m['name']==name]
    assert len(hits)==1,(cls,name)
    row=dict(hits[0]);row.update(observation=observation,application=application,limits=limits,
                               decision='proposed; master semantic dedup pending',credit=0)
    row['url']=f"https://github.com/{row['repo']}/blob/{row['commit']}/{row['path']}#L{row['start']}-L{row['end']}"
    row['excerptSha256']=sha(row['text'].encode())
    normalized=re.sub(r'/\*.*?\*/|//[^\n]*','',row['text'],flags=re.S)
    row['normalizedSha256']=sha(re.sub(r'\s+','',normalized).encode())
    records.append(row)
assert len({r['normalizedSha256'] for r in records})==len(records)
batch={'repo':manifest['repo'],'commit':manifest['commit'],'proposed_records':len(records),
       'master_credit_added':0,'upstream_executed':False,'production_changed':False,'game_started':False,
       'files_acquired_and_blob_verified':len(manifest['files']),'records':records,
       'uncredited_contexts':['AbstractEntityAIGuard.getTaskReferencePoint','AbstractEntityAIGuard.getPersecutionDistance'],
       'exclusions':['Melee/Range thin classification forwarding','same-equipment melee canAttack mirror','sleep/wake variants','accessor boilerplate','general permission block events not individually reviewed']}
(DOC/'batch-001.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:batch[k] for k in ('proposed_records','master_credit_added','files_acquired_and_blob_verified')}))
