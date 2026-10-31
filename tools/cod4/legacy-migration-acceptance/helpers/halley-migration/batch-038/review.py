"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-038'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))
























def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('requiem-permanent-remnant-type-respawn-policy-and-soul-shell-copy-deduplication',
 pick('/common/remnant/RemnantComponentImpl.java','readFromNbt')+whole('/common/remnant/RemnantComponentImpl.java')+
 whole('/core/remnant/MutableRemnantState.java')+whole('/core/remnant/NullRemnantState.java')+whole('/common/remnant/DemonRemnantState.java')+
 whole('/common/remnant/RemnantTypes.java')+whole('/common/remnant/SimpleRemnantType.java')+
 pick('/common/RequiemComponents.java','registerEntityComponentFactories')+pick('/common/RequiemRegistries.java','init')+
 pick('/Requiem.java','onInitialize registerPlugin')+pick('/common/ApiInitializer.java','discoverEntryPoints setPluginCallback')+
 pick('/common/VanillaRequiemPlugin.java','onRequiemInitialize registerEtherealEventHandlers registerRemnantStates resetIdentity refreshInventoryLocks')+
 pick('/mixin/common/event/PlayerManagerMixin.java','firePrepareRespawnEvent fixRespawnWorld firePlayerRespawnEvent')+
 whole('/api/v1/remnant/StickyStatusEffect.java')+whole('/common/entity/effect/AttritionStatusEffect.java')+
 whole('/common/dialogue/RemnantChoiceDialogueAction.java')+whole('/common/advancement/criterion/OnRemnantChoiceCriterion.java')+
 whole('/mixin/common/remnant/ServerPlayerEntityMixin.java')+whole('/core/remnant/RevivingDeathSuspender.java')+whole('/core/util/serde/DamageSourceSerialization.java')+
 whole('/common/remnant/PlayerSplitter.java')+pick('/common/entity/PlayerShellEntity.java','storePlayerData readCustomDataFromNbt writeCustomDataToNbt'),
 '官方Ladysnake/Requiem固定54281728d5f78944955a6e7b952ac4e0835129de；branch1.19但properties实际Minecraft1.19.3/mod2.0.0-beta.16。对话选择→become资格→CCA持久与ALWAYS_COPY→原生respawn事件/prepare→分身split/merge去重，构成1条对象族，不按每组件策略、死亡效果或旧PlayerProfile兼容拆计。',
 'requiem:remnant组件NBT仅id字符串+ethereal boolean；state默认NullRemnantState/MORTAL，splitting仅内存flag。身份registry是DefaultedRegistry以requiem:mortal为默认，init注册MORTAL，plugin注册requiem:remnant。read直接new Identifier(id)→registry lookup→become→setVagrant，无坏Identifier局部catch、无原未知ID存档隔离；默认registry语义须区别缺失key坏格式与合法未知ID。',
 'become同type早退，真实ServerPlayer子类fakeplayer不允许变种；旧state.teardown→新type.create(player)→setup继承old vagrant→sync/callback。Mutable.setVagrant通过updatePlayerState计算SOUL movement config和PAL invulnerability授予/撤销，不把derived能力全量写入remnant NBT。组件注册明确remnant ALWAYS_COPY、possession INVENTORY、movement/deathSuspender/ability等LOSSLESS_ONLY，先remnant后possession；策略名称是外部CCA行为声明，不声称已读CCA实现。',
 'PlayerManager mixin prepare在clone局部变量上触发(original,clone,returnFromEnd)，后存clone.world ThreadLocal，碰撞向上移有Y<256上限；另hook读取该world，RETURN事件用cir.getReturnValue新玩家。plugin原死则resetIdentity(clone)，再新组件prepare；Mutable.prepare只在!lossless&&!isVagrant时setVagrant并复制原维度/位置，original.isDead才加Attrition；随后仅StickyStatusEffect谓词通过的效果复制newInstance，而非全部effects。RemnantComponent.prepare用try/finally清splitting。',
 'Dynasty可参考把审定永久身份/历史任务字段放独立持久对象并明确死亡/返回末地策略；复活后由新对象资格重新计算derived能力，绝不能直接继承全部无敌/姿态/计时器。更适合本任务的明确白名单应保官阶/功名/忠诚/历史标记，同时保持已有死亡规则；不要移植Requiem灵魂无敌、Attrition或硬核额外死亡。双载体去重可借鉴避免把同一永久进度拷到分身/载体制造两份真值，但未知字段先保留校验，不按宽泛黑名单照搬。',
 'PlayerSplitter先native writeNbt，再删除UUID、SpawnX/Y/Z/Forced/Angle/Dimension、EnderItems、abilities、playerGameType/previousPlayerGameType、seenCredits、XpP/Level/Total；CCA ALWAYS_COPY组件从分身NBT去掉，剩余template覆盖to.writeNbt再to.readNbt，因此是宽黑名单，未列临时键仍可带过，非安全白名单。performRespawn临时keepInventory=false/清spawn，finally恢复原对象spawn与gamerule，新clone恢复spawn并重绑定networkHandler；spawnEntity结果未检，非事务承诺。merge真实库存先逐槽移/冲突drop、再dropAll余项以免modded inventory void，后copy数据和加经验，第三方槽/Stack坏ID/unknownNBT无损未核。PlayerShell旧PlayerProfile读为displayprofile，writer仅modelparts+super；nativeFakeServerPlayerEntity displayprofile持久未展开，不独立credit。DeathSuspender只LOSSLESS_ONLY，NBT写lifeTransient/deathCause不写对话倒计时；reader deathCause条件是world.isClient却castServerWorld，server不恢复cause，未清旧cause；倒计时重载后能否再触发未知，非有效永久字段迁移建议。DamageSourceSerialization可丢未知name为GENERIC，source/attacker UUID读取无containsUuid guard，native缺失行为未核。',
 '所有remnant选择/持久/prepare复活/分身数据去重/同链profile兼容合1；PAL/CCA/Impersonate/Automatone以及MovementAlterer/possession/record native展开未全读，仅记录本repo实际调用，不假定端到端运行正确。完整支持方法数字只文档规模，非候选数。与039Identity同玩家档案架构，但实际remnant type/state和soulshell去重对象不同；Kepler最终语义裁决。合法未知registry default可能成为mortal不保原payload，不能称旧ID别名恢复。credit0 accepted=false。')
def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/common/remnant/RemnantComponentImpl.java','/core/remnant/MutableRemnantState.java','/common/remnant/RemnantTypes.java','/common/RequiemRegistries.java','/common/remnant/PlayerSplitter.java','/core/remnant/RevivingDeathSuspender.java','/core/util/serde/DamageSourceSerialization.java']:
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
    (DOC/'batch-038.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
