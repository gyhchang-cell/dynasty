"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-019'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))






def pick(path,names):return [(path,n) for n in names.split()]
add('mca-player-uuid-world-save-avatar-inbox-and-last-village-restoration',
 [('/server/world/data/PlayerSaveData.java','PlayerSaveData',73)]+
 pick('/server/world/data/PlayerSaveData.java','get getIfPresent resetEntityData writeNbt setEntityDataSet setEntityData getEntityData getGender sendMail hasMail getMail sendLetter sendLetterOfCondolence showMailNotification updateLastSeenVillage setLastSeenVillage getLastSeenVillage')+
 pick('/util/WorldUtils.java','loadData')+
 pick('/util/NbtHelper.java','fromList')+
 pick('/server/ServerInteractionManager.java','onPlayerJoin')+
 pick('/forge/ForgeBusEvents.java','onPlayerLoggedInEvent onWorldTick')+
 pick('/server/command/Command.java','mail')+
 pick('/server/world/data/VillageManager.java','tick')+
 pick('/network/c2s/PlayerDataRequest.java','receive')+
 pick('/network/c2s/VillagerEditorSyncRequest.java','receive saveEntity syncFamilyTree getFamilyNode getGender')+
 pick('/item/PotionOfMetamorphosisItem.java','use common')+
 pick('/entity/VillagerLike.java','toVillager createTrackedData')+
 pick('/entity/VillagerEntityMCA.java','getTypeDataManager readCustomDataFromNbt writeCustomDataToNbt createTrackedData')+
 pick('/util/network/datasync/CDataManager.java','load save CDataManager Entry register get set')+
 pick('/util/network/datasync/CDataParameter.java','load save')+
 pick('/util/network/datasync/CEnumParameter.java','load save fromIndex')+
 pick('/util/network/datasync/CParameter.java','create')+
 pick('/util/network/datasync/NbtCompoundDefaultGetters.java','getInt getFloat getString getCompound getItemStack')+
 pick('/entity/ai/relationship/Gender.java','byId')+
 pick('/util/InventoryUtils.java','readFromNBT saveToNBT')+
 pick('/entity/ai/Relationship.java','readFromNbt writeToNbt')+
 pick('/entity/ai/LongTermMemory.java','readFromNbt writeToNbt'),
 'PlayerSaveData按玩家UUID独立世界PersistentState恢复，真实登录根据entityDataSet决定是否进入初始定制，PlayerDataRequest提供已设定玩家外观载荷；命令mail从恢复的inbox取成LETTER物品给玩家；世界tick使用lastSeenVillage重新解析村庄并更新。',
 'mca_player_<UUID>世界键：lastSeenVillage仅INT_TYPE才接受，entityDataSet布尔，entityData compound，inbox compound-list原始信页载荷。外层world和uuid来自取对象参数，不从NBT内owner复核。entityData承载村民型数据用于玩家外观/特征模板，不是原玩家整份ForgeData。',
 '普通get将持久管理器统一到server.getOverworld，但loader闭包仍捕获调用时world；getIfPresent却直接使用传入world的manager，因此非主世界离线查询未保证查同份数据。缺entityData会随机创建村民模板（skin/genetics/traits/brain），entityDataSet缺失false；若entityData键存在但为空/错类型，getCompound路径不触发reset，不同于缺键。inbox按compound列表读，writer保留当前复合元素；无显式schema/条数限值。',
 'setEntityData与setEntityDataSet均dirty，编辑保存直接持有传入compound并同步；getEntityData返回同对象，调用方需自行dirty，不是不可变快照。getMail remove(0)并构造LETTER、setNbt原compound，却没有markDirty，实际mail命令循环offerOrDrop也没补dirty；后续100tick的村庄位置更新常会dirty但不能保证每个取信/重启时序都保存已消费。lastSeenVillage writer仅存在时put，不移除传入compound旧键；通常新compound流程与复用载荷需区分。',
 'Dynasty永久进度可以用稳定UUID的独立权威数据并在新玩家实例重新绑定，所有入口必须统一维度寻址；缺失、空值、类型错分别处理并保留原始未知载荷。消费历史迁移凭证/任务物品在实际交付成功后dirty与标记，防重放；只迁经审定的永久白名单，不能把MCA模板CustomData或注册tracked参数整体移入玩家Clone。',
 '这里只证明mod的独立持久对象与实际登录/请求/取信入口，未发现或推断PlayerEvent.Clone实现；不等于实测死亡/末地返回。toVillager经完整readCustomData重构模板，mod codec中还有关系/长期记忆/库存，深层所有skins/brain行为和原生PersistentState刷盘、offerOrDrop事务未全审。编辑请求本方法未见owner/距离权限检查不证明全局网络安全性；网络类本身不给信用。CDataManager是字段注册集，包含mood/panicking等非永久玩家字段，不能当审定白名单。',
 '一个UUID玩家持久对象家族：avatar/初次定制/inbox/lastVillage/登录同步都合并，不因键/信件数量/平台接口/默认getter拆数。与下一家谱对象共享player relation支持，但这里独立对象是玩家定制载荷与信箱，不重复将关系枚举升级记入本条。credit0由Kepler决定是否进一步合并。')

add('mca-family-tree-sentinel-gated-relationship-enum-compatibility',
 [('/server/world/data/FamilyTree.java','FamilyTree',33)]+
 pick('/server/world/data/FamilyTree.java','get writeNbt getOrEmpty getOrCreate createEntry getAllWithName remove')+
 pick('/server/world/data/FamilyTreeNode.java','FamilyTreeNode save getRelationshipState setRelationshipState updatePartner isPlayer markDirty setProfession getProfessionId setFather setMother removeFather removeMother replaceParents assignParent clearParents getRelatives getAllRelatives gather gatherParents gatherChildren streamParents streamChildren isRelative')+
 pick('/entity/ai/relationship/RelationshipState.java','byId isMarried')+
 pick('/entity/ai/relationship/Gender.java','byId')+
 pick('/util/NbtHelper.java','toMap fromMap toList toStream fromList')+
 pick('/util/WorldUtils.java','loadData')+
 pick('/entity/ai/relationship/EntityRelationship.java','of getFamilyTree getRelationshipState isMarried isEngaged getPartnerUUID getPartner getRelationshipStream marry endRelationShip onTragedy')+
 pick('/server/world/data/PlayerSaveData.java','getFamilyEntry getIfPresent marry endRelationShip')+
 pick('/server/ServerInteractionManager.java','sendProposal acceptProposal endMarriage procreate')+
 pick('/network/c2s/VillagerEditorSyncRequest.java','getFamilyNode syncFamilyTree')+
 pick('/entity/ai/Relationship.java','getFamilyEntry'),
 'MCA-FamilyTree PersistentState加载全图后执行一次旧关系语义修正；读取后的状态实际被玩家求婚/成婚/生育准入和离线亲属悲伤传播消费，不是仅修复图形界面或枚举getter。',
 'NBT顶层每个key为UUID字符串，value含name/isPlayer/gender/father/mother/children[{uuid}]/可选spouse/marriageState整数/isDeceased/profession。特定UUID 12341234-1234-1234-1234-123412341234作为已升级哨兵，实为普通debug节点，不是独立版本字段。',
 'FamilyTree ctor先NbtHelper.toMap(UUID.fromString)构造全部节点，marker不存在则插入debug节点并dirty，再遍历关系：ENGAGED且双方isPlayer相同→MARRIED_TO_VILLAGER；接着若partnerIsPlayer→MARRIED_TO_PLAYER；MARRIED_TO_PLAYER且partner不是玩家→WIDOW。三个if顺序执行并可在同次遍历继续改，修复依赖整个图已有partner信息，而非纯ordinal加偏移。marker存在完全跳过；未知partner被判partnerIsPlayer=false，并不验证双向关系完整。',
 'RelationshipState.byId越界回SINGLE，旧ordinal在枚举有效范围内但语义已错不能由范围检查纠正，这正是额外迁移存在的原因。无旧version判断：任何缺marker的图都会运行，包括新存档首次再次加载；预先有同UUID条目可跳过。family nodes无raw未知字段保留，save新compound未写reader会读取的profession，重新保存后该字段丢失。father/mother直接getUuid无containsUuid保护；UUID坏key/坏父母/child转换无逐项catch，单坏项可令整个构造失败。',
 'Dynasty旧任务/官阶枚举迁移应使用明确版本和稳定语义ID，先加载必要身份上下文再转换，不能仅依赖数值范围或猜测偏移。一次迁移标记应与完整目标写入同一成功边界，保留未知原值；不把哨兵混入真实任务/玩家集合，也不能按旧任务ID每项增加参考数。Clone仅保留审定永久历史，不迁临时请求、情绪或悲伤计时。',
 '当前代码修正历史的真实触发与后续婚姻gate已完整阅读，未运行历史样本或证明所有旧关系都能正确复原；缺partner如何恢复原关系不在此算法能力。EntityRelationship.getRelationshipStream对离线玩家先getIfPresent，继承前条维度寻址风险。marry/endRelationship、in-memory proposals/procreateMap不是额外持久/Clone实现；其发送行为只读代码，不执行或发给玩家。setRelationshipState本身不dirty但迁移块先统一dirty；不能错报每个节点必定不保存。',
 '整个家谱解码/一次升级/父母配偶图/真实婚姻消费合一条，不把三if、每个枚举、哨兵、节点writer、亲属查询或平台分别算实现。与前条共享PlayerSaveData接口，独立迁移真值在MCA-FamilyTree世界图；若主责按同关系链合并必须遵从，credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    if 'player-uuid' in row['family']:
        targets=[('/entity/VillagerLike.java',['CParameter.create(']),('/entity/VillagerEntityMCA.java',['CDataManager<','new UpdatableInventory']),('/entity/ai/brain/VillagerBrain.java',['CParameter.create(']),('/server/world/data/PlayerSaveData.java',['lastSeenVillage =','entityDataSet;','entityData;','inbox ='])]
    else:targets=[('/server/world/data/FamilyTree.java',['DATA_ID =']),('/server/world/data/FamilyTreeNode.java',['profession =','partner =','relationshipState ='])]
    decl=[]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for node in walk(PARSER.parse(raw).root_node):
            if node.type!='field_declaration':continue
            fragment=raw[node.start_byte:node.end_byte].decode()
            if not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=node.type,name=fragment.split('=')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
            e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);decl.append(e)
    row['source_declarations']=decl
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
    (DOC/'batch-019.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
