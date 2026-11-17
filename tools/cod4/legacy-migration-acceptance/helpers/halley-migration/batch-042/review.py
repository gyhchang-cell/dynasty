"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-042'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))



























def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('requiem-bottled-soul-durable-owner-record-to-deferred-release-and-derived-ai-rehydration',
 pick('/core/entity/SoulHolderComponent.java','readFromNbt')+whole('/core/entity/SoulHolderComponent.java')+
 pick('/common/item/EmptySoulVesselItem.java','EmptySoulVesselItem useOnEntity checkCapturePreconditions getCaptureType computeCaptureTime finishUsing setupRecord getMaxUseTime usageTick playSoulCaptureEffects wins computeSoulOffense computeSoulDefense computeStrengthModifier getAttributeBaseValue getUseAction')+
 whole('/common/item/FilledSoulVesselItem.java')+whole('/common/entity/ReleasedSoulEntity.java')+whole('/common/entity/SoulEntity.java')+
 whole('/core/entity/EntityAiToggle.java')+whole('/core/mixin/noai/BrainMixin.java')+whole('/core/mixin/noai/GoalSelectorMixin.java')+whole('/core/mixin/noai/EntityNavigationMixin.java')+
 whole('/mixin/common/vessel/MobEntityMixin.java')+pick('/core/mixin/possession/possessed/PossessableMobEntityMixin.java','possessConvertedZombie')+
 pick('/common/RequiemComponents.java','registerEntityComponentFactories registerScoreboardComponentFactories')+pick('/common/item/RequiemItems.java','init')+
 pick('/common/VanillaRequiemPlugin.java','onRequiemInitialize registerPossessionEventHandlers')+pick('/common/remnant/BasePossessionHandlers.java','register')+
 whole('/core/record/EntityPositionClerk.java')+whole('/api/v1/record/EntityPointer.java')+whole('/core/record/CommonRecordKeeper.java')+whole('/core/record/GlobalRecordImpl.java')+whole('/core/record/ServerRecordKeeper.java'),
 '固定官方Requiem54281728d5f78944955a6e7b952ac4e0835129de。玩家空瓶捕获→物品稳定owner recordUUID→原体removed_soul持久→放飞实体owner_record→缺席主体延迟返还标记→主体record update消费并invalidate。真实捕获/返还玩法一条，不按AI/临时实体/物品/marker拆计。',
 '活动空瓶根requiem:soul_capture{use_time int,target entityUUID}；满瓶requiem:soul_fragment{type entityID,uuid recordUUID}，注意不是原生entityUUID。LivingEntity SoulHolder removed_soul boolean；EntityAiToggle inhibitors string列表只持久true项；ReleasedSoul owner_record UUID与super.max_age int；世界record ENTITY_REF指向原体，RELEASED_SOUL Unit作延迟返还凭据。',
 'finishUsing仅server，先remove活动NBT再用targetUUID查当前ServerWorld，要求LivingEntity/ServerPlayer并重查capturepreconditions。NORMAL成功setupRecord getOrCreateRecord→新filled栈写type+recordUUID→removeSoul；AGGREGATE随机UUID无linked实体并伤害20，与正常主体不能当同一保证。新满瓶是new ItemStack，未copy旧空瓶未知tag，ItemUsage.exchangeStack细节未展开，不能当Count/tag无损迁移范例。临时活动target/use_time不应进永久Clone白名单。',
 'SoulHolder.setSoulRemoved状态变化时按tagSOULLESS及removed flag重算AI inhibitor(soul_capture,persistent=false)，而removed_soul本身持久；原生mob转换事件把flag复制给新体，EntityPositionClerk同事件转移record。AI读inhibitors只载true永久项并refresh，SoulHolder反序列化再生成非持久derived抑制；refresh实际触达Brain/GoalSelector/Navigation禁tick。读AI不clear旧map，同实例缺键可能残留；client sync仅赋disabled不触发refresh，这些不是永久进度读取保证。',
 'Dynasty可借鉴载体保存稳定主体记录身份、永久资格与derived临时能力分离，以及主体暂未加载时留持久待返还标记，等实际主体更新成功后一次消费。审定任务/官阶等白名单必须校验UUID属于目标主体、维度可用和真实提交成功；不能把同链活动target/use_time、max_age、AI/免疫/姿态一并Clone。未知旧ID/原tag必须保留，不能用本例新建空瓶交换覆盖任务原栈。',
 'Filled.use缺uuid/无效record仍releaseSoul(owner=null)并换空瓶，spawnEntity返回未检，非无损事务；type用于tooltip不验证与owner record对应，释放不检查物品持有者是原体owner，不将UUID称玩家所有权授权。ReleasedSoul tick以record.ENTITY_REF有无区分missing与unloaded/far/wrongworld，FOUND无寿命上限；其余setMaxAge(60)但比较实体总age>=maxAge，并非从变状态另计60tick。ISEKAI到期把RELEASED_SOUL写record再discard，主体loaded更新callback giveSoulBack后invalidate整个record；近身碰撞同样marker返还，BODY_MISSING到期invalidate并消失。离线返还依赖record仍valid，未知codec/缺维度拒绝沿040，若失record则资格可能不可恢复。marker重复set幂等，invalidate使后续lookup无效，但无跨保存事务/重入ack证明，不称exactly-once。SoulEntity只写max_age不写targetChanges/cooldown/timeInSolid/NEXT_TARGET；nativeage是否持久未展开，不能声称重载寿命准确延续。玩家SoulHolder registerFor LivingEntity无显式player respawn策略，本批非Player Clone许可。',
 '042为实际灵魂资格从entity→item→deferredmarker→entity重建的不同对象，040仅record关系迁移支持；所有SoulHolder/AI/Item/ReleasedSoul/record/callback/多capture类型合1，不将普通NBT getter/粒子/方法下载数当信用。与其他灵魂容器/实体封装族广义相近请Kepler按真控制流比较，可合并排除。无旧ID专用fallback；实际持久资格读取可建议但credit0 accepted=false。')
def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/common/item/EmptySoulVesselItem.java','/common/item/FilledSoulVesselItem.java','/common/entity/ReleasedSoulEntity.java','/common/entity/SoulEntity.java','/core/entity/SoulHolderComponent.java','/core/entity/EntityAiToggle.java','/api/v1/event/requiem/SoulCaptureEvents.java']:
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
    (DOC/'batch-042.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
