"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-040'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

























def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('requiem-pre-beta14-record-aliases-and-mortician-obelisk-direct-link-to-indirection-migration',
 pick('/common/entity/MorticianEntity.java','baseTick readCustomDataFromNbt writeCustomDataToNbt linkWith setLinkedObelisk initDataTracker initGoals getHome hasInvalidLinkedObelisk tickMovement setFadingTicks getFadingTicks setObeliskProjection isObeliskProjection')+
 whole('/core/record/EntityPositionClerk.java')+whole('/core/record/CommonRecordKeeper.java')+whole('/core/record/GlobalRecordImpl.java')+whole('/core/record/ServerRecordKeeper.java')+
 whole('/api/v1/record/RecordPointer.java')+whole('/api/v1/record/EntityPointer.java')+whole('/api/v1/record/GlobalRecordKeeper.java')+whole('/api/v1/record/RecordType.java')+
 pick('/common/RequiemComponents.java','registerEntityComponentFactories registerScoreboardComponentFactories')+whole('/common/RequiemRecordTypes.java')+
 whole('/core/util/DataResults.java')+whole('/core/util/MoreStreams.java')+whole('/api/v1/block/ObeliskDescriptor.java')+pick('/api/v1/util/MoreCodecs.java','text')+
 whole('/common/entity/MorticianSpawner.java')+whole('/common/entity/ai/MoveBackToObeliskGoal.java')+whole('/core/mixin/tracking/ServerEntityHandlerMixin.java')+
 pick('/common/entity/RequiemEntities.java','init')+pick('/common/block/obelisk/RiftRunestoneBlock.java','findRespawnPosition')+
 pick('/common/block/obelisk/RunestoneBlockEntity.java','RunestoneBlockEntity tick update refreshStructure getDescriptorRecord getDescriptor generateName onDestroyed readNbt writeNbt updatePower updateObeliskPower spawnSoul getRange getObeliskCenter applyPlayerEffects')+
 pick('/common/block/obelisk/InertRunestoneBlock.java','getTicker createBlockEntity shouldHaveBlockEntity onStateReplaced')+
 pick('/common/block/obelisk/BaseRunestoneBlockEntity.java','BaseRunestoneBlockEntity isPowered setPowerRate readNbt writeNbt'),
 '固定官方Requiem54281728d5f78944955a6e7b952ac4e0835129de，pre-2.0.0-beta.14旧record别名/refs→record及Mortician直接obelisk关系→indirect投影关系。实际baseTick迁移后home AI、生成防重复和失联衰退消费新关系。共同关系迁移族1条，不按三个别名、底层容器/各schema字段拆信用。',
 'Scoreboard CCA requiem:global_record_keeper保存records[{uuid,data:{recordTypeID:codecNBT}}]；entity_clerk新UUID record或旧refs list首compound.uuid；Mortician linked_obelisk UUID、fading_ticks int、captured_souls UUID int-array列表、anger原生，checkLegacyData仅内存标记；Runestone linked_record UUID指向worldrecord。',
 'CommonRecordKeeper.tryParseRecordType将requiem:body_ref/soul_owner_ref/mortician_ref全部归一entity_ref；各datum走type codec，所有字段DataResult聚合成map后整record插入。DataResults.ifPresentOrElse仅接受result，不用partial，任何不识别type/codec失败会记录错误并不插入该record，未知payload不保留。UUID读取Throwable转DataResult但其余native/collector异常不全面隔离；同时存在旧别名和新entity_ref会归一成同Map键，Collectors.toMap无merge函数，不能保证多别名安全。ServerRecordKeeper逐字段验证world存在；缺世界record不能插入，非延迟恢复/隔离保留。',
 'EntityPositionClerk读新record containsUuid优先，lookup无结果不退旧refs；旧refs只首项，ref uuid未逐项containsUuid，未见清当前recordId，重新用于同实例缺键会残留旧绑定。Mortician读linked_obelisk即projection=true/checkLegacy=true；baseTick只有当前clerk record存在且含OBELISK_REF才unlink旧entity_ref，再linkWith旧obelisk record：getOrCreateRecord建立独立NPC记录，向obelisk.PROJECTED_MORTICIAN写RecordPointer(NPC recordUUID)，linkedObelisk保持obelisk UUID。迁移开关随后无论成功都清false，目标暂未就绪不在下tick自动重试，通常需重新读档再设。',
 'Dynasty旧入口/主体身份引用若从直接对象改间接记录，可参考显式分离“稳定永久主体UUID”与“当前实体/入口位置”，迁移成功后才更换边并保留原记录，以避免共享进度重复/丢失。旧alias只在registry/codec目标确认有效后提交，未知ID、损坏字段、缺维度和lookup暂不可用应保原payload待恢复；严禁把read失败→空档写回当成功。Clone白名单不要复制整个record图或临时fading/anger/实体目标；只审定永久任务/官阶等主体历史。',
 '实际getHome从linkedObelisk record→OBELISK_REF，MoveBackToObeliskGoal校同维度/距离；tickMovement失效找同世界20格最近可用rift记录，否则fading++到600discard。MorticianSpawner每1200tick查询RIFT_OBELISK且PROJECTED_MORTICIAN.resolve为空才生成：resolve只需record有效，不要求实体loaded，因此持久关系存在可阻止重复生成。EntityPointer本身含entityUUID/world/pos、resolve不加载chunk。clerk.health<=0移entity_ref不立即销毁，destroy hook invalidates whole record，queue到tick才从map删除；writer遍历全部records未过滤invalid，可在queue处理前写出暂未移除record，实际保存时序未验。clerk.updateRecord只比pos未比world/uuid，等坐标跨维度引用刷新未保证。Runestone刷新清旧同posrecord没有比较dimension，跨维度相同pos存在误清风险；recordUuid非null但lookup缺失时不走新建分支，未见clear-and-retry。recordUuid赋值/变化未显式markDirty，CCA/原生实际落盘与外部ObeliskMatcher/nativeAnger未全展开，不能保证迁移无损。captured_souls/death释放/交易灵魂另对象未沿全链审阅，绝不额外计；最初非正式soulId选源描述已撤正。',
 '040新增的是明确旧关系图迁移与实际NPC/obelisk消费者；与038共EntityPositionClerk API调用，但038只支持splittransfer并未研究本旧schema。所有recordcodec/三个aliases/refs/readwrite/pointer/实体getter/生成间接化合1；不当通用缓存算数。Kepler最终按主账语义去重，credit0 accepted=false。')
def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/core/record/EntityPositionClerk.java','/core/record/GlobalRecordImpl.java','/core/record/CommonRecordKeeper.java','/common/entity/MorticianEntity.java','/common/RequiemRecordTypes.java','/api/v1/record/RecordType.java','/api/v1/record/RecordPointer.java','/api/v1/record/EntityPointer.java','/api/v1/block/ObeliskDescriptor.java','/common/block/obelisk/RunestoneBlockEntity.java']:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
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
    (DOC/'batch-040.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
