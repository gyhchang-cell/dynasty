"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-037'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))






















def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('naturesaura-pet-permanent-revival-eligibility-and-death-copy-transient-reset',
 pick('/items/ItemPetReviver.java','onEntityInteract')+whole('/items/ItemPetReviver.java')+whole('/items/ItemImpl.java'),
 'PET_REVIVER物品构造注册事件；交互已驯服TamableAnimal写资格，LivingTick可见心形消费该资格，LOWEST LivingDeath再使用资格复活。资格写入与实际死亡消费者同链合1。',
 '实体PersistentData中naturesaura:pet_reviver boolean；交互目标需驯服且未标记、手持对应物品。服务端缩减一件，未见creative排除/操作者owner一致性检查，标记写入发生在两端。未标记默认false。',
 '资格不会在复活时remove或设false：永久反复复活意图。默认Overworld共享spawn；在线ServerPlayer owner有床则findRespawnPositionAndUseSpawnBlock用owner当前level，非getRespawnDimension。跨level先移除旧pet后create同EntityType，再restoreFrom；同level也对自身restoreFrom。随后速度0、移到spawn、碰撞逐格上移、满血、停寻路、坐姿、清跳跃和target，最后取消死亡。',
 '这是真实资格字段写入和死亡行为消费，不是空read/write包装。server tick每20tick、owner距离平方<=25时概率心形提示。死亡在LOWEST但未显式receiveCanceled，不可声称已取消死亡仍处理。crosslevel创建结果无null检查、addFreshEntity结果未核；remove发生在create前；noCollision上移无显式高度上限。200000 aura扣在恢复之后，无足额guard，不能假称扣费成功才复活。',
 'Dynasty永久任务/资格白名单需要与复活后重置的生命、移动、战斗目标分离；参考标记实际授权行为与清理临时状态的先后，不整体复制ForgeData。迁移后资格应保留原主体身份；恢复目的维度要由存储的respawn维度校核，创建/添加结果成功后再提交移除，避免因失败丢旧对象。此处仅研究原则不抄实现、不实施。',
 'PersistentData原生落盘/restoreFrom具体NeoForge版本尚未全文展开，故仅主张本模组实际写资格并消费，不能保证所有第三方TamableAnimal和跨维度copy都持久无损。没有Player Clone、旧ID兼容或本地原档验收；不能把native restoreFrom当已审定白名单。粒子包/语言/普通死亡戒指取消事件不另计，原生床spawn/生成生命周期不运行验证。若主责要求证明native落盘触发才入账，保持候选排除即可。',
 '037与036共native restoreFrom边界，但036仅未证实扩展序列化；此处新对象是实际永久pet资格与死亡消费，可独立建议但全部事件/心形/变体合1。与其他宠物救援或死亡资格族须Kepler语义去重；7方法只是支持，不新增方法信用。credit0 accepted=false。')
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
        row['source_declarations']=[]
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-037.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
