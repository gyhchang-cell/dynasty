"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-041'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))


























def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('requiem-player-discovered-rift-persistent-whitelist-to-menu-snapshot-and-server-navigation',
 pick('/common/remnant/PlayerRiftTracker.java','readFromNbt')+whole('/common/remnant/PlayerRiftTracker.java')+
 pick('/common/RequiemComponents.java','registerEntityComponentFactories registerScoreboardComponentFactories')+
 pick('/common/block/obelisk/RiftRunestoneBlock.java','onUse createScreenHandlerFactory canBeUsedByVagrant findRespawnPosition')+
 whole('/common/screen/RiftScreenHandlerFactory.java')+whole('/common/screen/RiftScreenHandler.java')+pick('/common/screen/RequiemScreenHandlers.java','init')+
 pick('/common/network/ServerMessageHandling.java','init')+whole('/api/v1/block/ObeliskDescriptor.java')+pick('/api/v1/util/MoreCodecs.java','text')+
 pick('/common/block/obelisk/RunestoneBlockEntity.java','getDescriptorRecord getDescriptor canBeUsedBy readNbt writeNbt')+
 whole('/core/record/CommonRecordKeeper.java')+whole('/core/record/ServerRecordKeeper.java')+whole('/core/record/GlobalRecordImpl.java')+
 whole('/common/entity/effect/AttritionStatusEffect.java')+
 pick('/Requiem.java','onInitialize'),
 '官方Requiem固定54281728d5f78944955a6e7b952ac4e0835129de，已见rift永久UUID集合实际在RiftRunestone.onUse授予、CCA ALWAYS_COPY持久/死亡恢复、菜单factory fetch筛选并传到服务端useRift。1玩家知识对象完整链，底层record代码已040支持复用不再算新信用。',
 'requiem:rift_tracker组件只rift_records UUID int-array列表→HashSet；没有额外临时传送倒计时/生命/姿态字段。addRift require record有RIFT_OBELISK且OBELISK_REF，new UUID才server通知已发现名字。read先clear再逐NbtHelper.toUuid，无局部异常隔离；缺列表为默认空，原unknownNBT不stash，重复UUID合并。',
 'fetchKnownObelisks查世界Scoreboard GlobalRecordKeeper，record需仍valid、RIFT_OBELISK与OBELISK_REF都可取，否则iterator.remove永久从知识集合删除；缺record不区分读档依赖暂未就绪与真实拆除。writer只当前HashSet，失效后写回会失去原UUID，未知记录不是安全隔离。CCA明确ALWAYS_COPY，仅证明注册策略，底层CCA实现未全文展开、不称实测过死亡。',
 'RiftRunestone.onUse先要求ACTIVATED+demon、找到controller，然后addRift发生在incorporeal/Attrition/powered检查之前；肉身形态或无电也可学习入口，不能把学习资格当立即可用。createMenu与writeScreenOpeningData各fetch一次，snapshot descriptor set给handler。canUse检查incorporeal、源controller instance+8格、Attrition<3；USE_RIFT receiver实际只currentScreenHandler instanceof，不显式canUse，再handler只snapshot包含target且!=source。目标之后失效/record变化不会fresh-fetch重校。',
 'Dynasty永久历史入口/任务知识集合适合专用白名单组件，按稳定主体UUID留存；权限资格与临时使用条件必须分开。在旧档恢复中，目标暂不可用不可直接删永久历史，需保原ID等待注册/世界加载验证；菜单snapshot应在实际操作时重新验证服务器真值与源目标维度/所有权。Clone只保审定永久官阶/功名/任务标记，别携带传送损耗/临时冷却/姿态。',
 'useRift收到descriptor包含dimension但findRespawnPosition用player.world和target.pos，teleport也是本world坐标，不使用target.dimension选择世界；fetch不按当前dimension筛选，不能声称跨维度入口恢复正确。碰撞/目标坐标nativeRespawnAnchor实现未展开，snapshot可用性nativecontainer每tick何时close未运行，故不宣称实际漏洞复现。getAttritionLength按距离log罚时，target同pos不同descriptor可能distance0；不据此制造新迁移建议。Attrition是本模组规则，仅解释真实消费者，不适用于Dynasty、绝不新增死亡惩罚。底层记录unknowncodec/缺维度整条拒绝、stale UUID边界沿用040，不另credit。没有旧player rift别名fallback，但实际持久读取与Clone策略可研究，未知坏UUID部分集读取不保证无损。',
 '041为新实际玩家已发现入口知识对象及可见菜单/消费，不是040同record getter包装；与007Waystones广义相近入口网络，需Kepler比较具体控制流（永久HashSet+fetch删除+snapshot导航+维度遗漏）后可合并/排除。所有UUID元素、不同rift、字段、GUI/网络/底层codec与平台版本同族，不多计。credit0 accepted=false。')
def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/common/remnant/PlayerRiftTracker.java','/api/v1/remnant/RiftTracker.java','/common/screen/RiftScreenHandler.java','/common/screen/RiftScreenHandlerFactory.java','/common/screen/RequiemScreenHandlers.java','/api/v1/block/ObeliskDescriptor.java']:
        sample=next((r for r in INDEX if r['path'].endswith(suffix)),None)
        if sample is None:
            manifests=json.loads((BASE/'source-manifest.json').read_text())
            source=next(m for m in manifests if any(f['path'].endswith(suffix) for f in m['files']))
            file=next(f for f in source['files'] if f['path'].endswith(suffix))
            sample=dict(file,repo=source['repo'],commit=source['commit'],git_tree=source['git_tree'])
        raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type not in ('field_declaration','static_initializer'):continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out

def generate():
    rows=[]
    for spec in SPECS:
        evidence=[]
        for selector in spec['selectors']:
            suffix,name=selector[:2]
            matches=[r for r in INDEX if r['path'].endswith(suffix) and r['name']==name and (len(selector)<3 or r['start']==selector[2])]
            if not matches:
                raise ValueError(('No complete source method for evidence',selector))
            for r in matches:
                evidence.append(dict(r,revision=r['commit'],private_file=r['source'],start_line=r['start'],end_line=r['end'],method=r['name'],file_sha256=r['sourceSha256'],method_sha256=r['excerptSha256'],structural_fingerprint=r['normalizedSha256'],context=r['text'],source_url_or_coordinate='https://github.com/'+r['repo']+'/blob/'+r['commit']+'/'+r['path']+'#L'+str(r['start'])+'-L'+str(r['end'])))
        evidence=list({e['candidate_id']:e for e in evidence}.values())
        primary=evidence[0]
        row={k:v for k,v in spec.items() if k!='selectors'}
        row.update(primary)
        row.update(status='helper_reviewed_pending_coordinator',credit=0,accepted=False,evidence=evidence,preservation=spec['observation'],application_limit=spec['limits'],url=primary['source_url_or_coordinate'],excerpt=primary['text'],source_local=primary['source'],source_sha256=primary['sourceSha256'],line=primary['start'],end_line=primary['end'],runtime_validation='not_run_static_research_scope')
        attach_declarations(row)
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-041.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
