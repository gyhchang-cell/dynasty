"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-039'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))























def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('identity-prevariant-player-unlocks-to-typed-identities-and-respawn-state-copy-boundaries',
 pick('/mixin/player/PlayerEntityDataMixin.java','readNbt')+whole('/mixin/player/PlayerEntityDataMixin.java')+
 whole('/mixin/player/RespawnDataCopyMixin.java')+whole('/mixin/player/PlayerManagerMixin.java')+whole('/mixin/PlayerManagerMixin.java')+
 whole('/api/variant/IdentityType.java')+whole('/api/variant/TypeProvider.java')+whole('/impl/variant/SheepTypeProvider.java')+
 whole('/api/PlayerUnlocks.java')+whole('/api/PlayerFavorites.java')+whole('/api/PlayerIdentity.java')+whole('/api/IdentityGranting.java')+
 pick('/mixin/LivingEntityMixin.java','onDeath')+pick('/mixin/PlayerEntityAttackMixin.java','identityAttack')+
 whole('/network/impl/UnlockPackets.java')+whole('/network/impl/FavoritePackets.java')+whole('/network/impl/SwapPackets.java')+
 pick('/network/ClientNetworking.java','registerPacketHandlers runOrQueue handleIdentitySyncPacket handleAbilitySyncPacket')+
 pick('/Identity.java','initialize registerJoinSyncPacket hasFlyingPermissions')+whole('/api/FlightHelper.java')+
 whole('/api/PlayerAbilities.java')+whole('/api/PlayerHostility.java')+whole('/mixin/player/PlayerEntityTickMixin.java')+
 whole('/mixin/ActiveTargetGoalMixin.java')+whole('/mixin/player/ClientPlayerDataCacheMixin.java')+
 pick('/screen/IdentityScreen.java','populateRenderEntities collectUnlockedEntities')+
 pick('/network/ServerNetworking.java','initialize registerUseAbilityPacketHandler')+
 pick('/registry/IdentityEventHandlers.java','initialize registerHostilityUpdateHandler'),
 '官方Draylar/identity arch-1.20.1固定2fdf47a7c8c727f05460378247ff118f868f0713，PlayerEntity原生read/writeCustomData RETURN mixin接线；ServerPlayer.copyFrom TAIL恢复；死亡击杀学习及GUI实际用解锁集合。common持久链合1，不按Fabric/Forge平台或每variant拆计。',
 '旧UnlockedMorphs字符串列表、旧FavoriteIdentities字符串列表；新UnlockedIdentities与FavoriteIdentitiesV2写compound{EntityID,Variant}；CurrentIdentity{id,EntityData}含原生entityNBT及IdentityType；AbilityCooldown/RemainingHostilityTime int。HashSet type+variant equals去重，读取前清各集合。',
 '旧ID经new Identifier及registry containsId，有效则IdentityType(type)取provider默认（羊WHITE）；未知注册ID跳过无日志payload保留，坏Identifier未局部catch。新compound经IdentityType.from registry校验，但直接构造Variant，缺失-1，不走from(type,int)的范围校验。旧新列表都读入HashSet union；writer只写新列表而不主动remove旧keys，原生外层tag是否保留旧key不承诺。',
 'FavoriteIdentitiesV2 writer追加writeCompound，reader却getList(...STRING_TYPE)并对元素强转NbtCompound，明显元素类型契约不一致；未展开native NbtCompound.getList，静态证据不称实测丢失。CurrentIdentity writer把IdentityType放EntityData子compound，reader调用IdentityType.fromEntityNbt(tag)却给外层，路径不一致；id=empty只清identity、不清identityType；无效实体type不主动清旧identity，create返回未检查/castLivingEntity无类型guard。完整原生NBT写后read可携带超出资格的数据，不推断全部安全或无损。',
 'Dynasty可以借鉴旧ID列表→有类型永久资格集合的读旧写新，并将坏ID保留到隔离区再提交升级，不能跳过后重写造成永久丢项。Clone白名单应仅保审定永久字段与历史任务，显式排除技能冷却/敌意/姿态/免疫等；本实现把冷却和敌意也复制，是需要辨析的反例。校核嵌套tag位置、列表元素类型、旧新并存优先规则以及新玩家对象作为同步目标，保留原物品Count/tag和主体UUID。',
 'copyIdentityData忽略alive布尔，复制冷却/敌意、原LivingEntity对象引用、unlocked/favorites（setterclear/addAll），不复制identityType且不调用updateIdentity重建derived飞行/health；不是深克隆/永久字段白名单。两个PlayerManager respawn RETURN mixin都用形参player而非cir.getReturnValue，同步/维度/最大血处理未证明作用于新玩家。实际server tick逐tick将两timer减到>=0，canUseAbility<=0，hostility>0影响Monster目标，所以timer确为临时战斗态。Client cache跨respawn存旧provider并复制后清，仅客户端补同步，不等于server持久化。Swap C2S只检查enableSwaps/permission和variant范围，未见PlayerUnlocks.has复核；因此不称恢复集合是服务端授权安全边界。native NBT/mixin实际装载/Architectury transport/其他六种variant provider与对应配置平台未全文审查，无运行或原档验收；羊provider仅fallback实例，不外推全部variant无损。',
 '一条完整玩家形态档案生命周期：旧alias/variantcodec/unlockgrant/persistence/Clone/clientcache/favorites与currentidentity读写全合1，不能按字段、两个旧键、七variant、平台移植拆出信用。与通用玩家能力档案有共同NBT架构但该旧格式→variant迁移/真实击杀资格对象具体不同，Kepler最终按语义核对；支持方法/下载/AST数均不计，credit0/accepted=false。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/mixin/player/PlayerEntityDataMixin.java','/api/variant/IdentityType.java','/mixin/player/ClientPlayerDataCacheMixin.java']:
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
    (DOC/'batch-039.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
