"""Incoming damage, retaliation propagation and projectile ownership source review."""
from pathlib import Path
import hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[5]
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/guard-ownership-research/helpers/coordinator-minecolonies'
sys.path.insert(0,str(ROOT/'tools/cod4/guard-ownership-research/.work/python39'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
manifest=json.loads((DOC/'source-manifest-002.json').read_text())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
annotations=[
('IGuardBuilding','checkIfGuardShouldTakeDamage','无守卫建筑时放行；当前跟随/集结玩家与来源玩家相等时拒绝，否则放行。','检查伤害另一端也可按真实跟随者身份拒绝，不能只相信调用者提供owner名。','这是守卫被玩家伤害的保护，不是王朝守卫对外伤害许可；不能倒置使用。'),
('EntityCitizen','hurt','依次处理墙内伤害、来源校验和职业ignoresDamage；无殖民地才走super，否则进入受伤处理。','核对原生入口控制流，友军筛选需在真实受伤与仇恨派发前，而非AI末尾补清。','内部来源检查仍可能读取colony，不能声称末尾空colony兜底保证上游永不空指针；未执行上游。'),
('EntityCitizen','checkIfValidDamageSource','同殖民地公民伤害直接拒绝；跨殖民地PVP可登记敌对；服务端玩家受袭击阶段、伤害量/权限和跟随守卫身份限制。','真实伤害边界需解析归属与来源身份，多种入口一致硬拒绝同阵营。','1点及以下伤害存在权限例外，客户端和服务端分支也不同；王朝不能复制该伤害豁免或殖民地权限系统。'),
('EntityCitizen','handleDamagePerformed','将伤害限为生命20%并处理骑兵分摊/格挡/撤退减伤；super.hurt失败即退出，成功后才把生物来源加入威胁表。','只有真实成功受伤才触发后续仇恨，不能把失败、免疫或取消伤害当作有效报复凭证。','performMoveAway及setLastHurtMob发生在super.hurt之前，故不是所有前置状态都以成功受伤为条件；数值机制不照抄。'),
('EntityCitizen','performMoveAway','环境来源且允许打断则避让；空来源退出；守卫求援后返回，其他公民切逃跑并向守卫求援。','一处受伤可能启动其他守卫，必须审查间接求援路径而不只本怪最近玩家目标。','该方法没有敌友许可，不能将它当作选敌安全；仅研究现有入口，不新增王朝公民求援。'),
('EntityCitizen','callForHelp','非活体或求援冷却中退出，睡眠守卫不求援；按同殖民地及距离收集守卫，先加0威胁再canHelp并排序，最后逐个startHelpCitizen。','即使canHelp拒绝，先入表的目标也可能后续重新被选中；最终伤害门不能依赖一次状态拒绝。','循环边界i<=CALL_TO_HELP_AMOUNT可能包含第N+1个，不称严格N；与batch001接收侧startHelpCitizen有关，最终可按整链合并信用。'),
('CombatUtils','createArrowForShooter','先给原箭设shooter，再允许Bow自定义箭或改为矛/三叉戟，最终再次设owner与出手位置。','替换投射物后必须重新绑定真实来源，避免武器工厂更换实体丢失所有者。','setOwner不是碰撞友军过滤；投射物身份正确不证明绝不误伤，射击几何函数不计信用。'),
('CombatUtils','notifyGuardsOfTarget','同建筑已分配公民在没有lastHurtByMob时接收0威胁；目标为袭击者时又给范围内守卫建筑临时巡逻点。','目标共享有第二入口，审查广播接收者和最终攻击不能只筛原始选敌者。','无直接友军判断且target来自调用者；王朝不新增威胁广播或跨建筑调度。'),
]
records=[]
for cls,name,observation,application,limits in annotations:
    file=next(s for s in manifest['files'] if Path(s['path']).stem==cls)
    source=ROOT/file['local'];raw=source.read_bytes();assert sha(raw)==file['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==file['git_blob_sha1']
    hits=[]
    def walk(n):
        if n.type=='method_declaration' and n.child_by_field_name('body'):
            key=n.child_by_field_name('name')
            if raw[key.start_byte:key.end_byte].decode()==name:hits.append(n)
        for c in n.children:walk(c)
    walk(parser.parse(raw).root_node);assert len(hits)==1,(cls,name)
    n=hits[0];text=raw[n.start_byte:n.end_byte].decode();start=n.start_point.row+1;end=n.end_point.row+1
    assert '\n'.join(raw.decode().splitlines()[start-1:end]).strip()=='\n'.join(text.splitlines()).strip()
    norm=re.sub(r'\s+','',re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S))
    records.append(dict(repo=manifest['repo'],commit=manifest['commit'],path=file['path'],source=str(source),
                        sourceSha256=sha(raw),name=name,start=start,end=end,text=text,excerptSha256=sha(text.encode()),normalizedSha256=sha(norm.encode()),
                        url=f"https://github.com/{manifest['repo']}/blob/{manifest['commit']}/{file['path']}#L{start}-L{end}",
                        observation=observation,application=application,limits=limits,credit=0,decision='proposed; master semantic dedup pending'))
prior=json.loads((DOC/'batch-001.json').read_text())['records']
assert len({r['normalizedSha256'] for r in prior+records})==len(prior+records)
batch=dict(repo=manifest['repo'],commit=manifest['commit'],proposed_records=len(records),master_credit_added=0,
           upstream_executed=False,production_changed=False,game_started=False,records=records,
           unrelated_downloaded_methods_not_credited=True)
(DOC/'batch-002.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'proposed_records':len(records),'credit_added':0,'range_blob_and_prior_exact_dedup':'PASS'}))
