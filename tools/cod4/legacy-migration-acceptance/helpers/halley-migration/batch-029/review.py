"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-029'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))















def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('pmmo-overworld-uuid-xp-truth-offline-award-queue-and-death-respawn-consumers',
 [('/storage/PmmoSavedData.java','PmmoSavedData',144)]+whole('/storage/PmmoSavedData.java')+
 pick('/setup/CommonSetup.java','onServerStartup onConfigReload')+pick('/core/Core.java','Core get getData getSide getLevelProvider getLoader getPerkRegistry awardXP doesPlayerMeetReq isActionPermitted getObjectSkillMap getReqMap getEnchantReqs getCommonReqData getEnchantmentReqs getExperienceAwards getCommonXpAwardData getObjectExperienceMap getObjectModifierMap getConsolidatedModifierMap')+
 pick('/core/CoreUtils.java','processSkillGroupReqs processSkillGroupXP processSkillGroupBonus deserializeAwardMap mergeXpMapsWithSummateCondition applyXpModifiers')+
 whole('/registry/LevelRegistry.java')+pick('/registry/PerkRegistry.java','executePerk isPerkCooledDown')+
 whole('/events/impl/LoginHandler.java')+whole('/events/impl/PlayerDeathHandler.java')+
 pick('/events/EventHandler.java','onPlayerJoin onRespawn onDeath onItemActivate')+pick('/events/impl/PlayerClickHandler.java','rightClickItem')+
 whole('/api/events/XpEvent.java')+pick('/api/APIUtils.java','getLevel setLevel addLevel getXp setXp addXp getRawXpMap getAllLevels')+
 whole('/network/clientpackets/CP_UpdateExperience.java')+whole('/network/clientpackets/CP_ResetXP.java')+whole('/network/clientpackets/CP_UpdateLevelCache.java')+
 pick('/network/Networking.java','registerMessages sendToClient')+
 pick('/client/utils/DataMirror.java','DataMirror me getLevelFromXP getXpRaw setXpRaw getXpMap setXpMap getPlayerSkillLevel get setLevelCache'),
 '服务器启动getData/computeLevels、普通玩法awardXP及API/命令改变XP；玩家离线则排队，登录先同步真值再投递队列。死亡显式配置扣除、重生执行SKILL_UP perks；身份真值在世界UUID文件而非PlayerEvent.Clone拷实体数据。',
 'overworld.dataStorage[pmmo]中xp_data与scheduled_xp，XP_CODEC=unboundedMap(UUID字符串,unboundedMap(任意skill字符串,LONG))。每UUID全技能Map与离线差值Map；levelCache为运行派生数据，不写磁盘。',
 'get在ServerLifecycleHooks有server时从overworld.computeIfAbsent取SavedData，无server返回新暂存对象；Core按logical side memoize，但getData每次data.get解析当前存档。构造两map分别parse().result().orElse(empty)，不是每条保留partial；save仅滤xp的空玩家map，保留任意未知skill字符串及原long，scheduled完整encode，encode失败orElse空compound，无错误旁路。UUID_CODEC在PrimitiveCodec.read直接ops.getStringValue.getOrThrow和UUID.fromString，没有将异常封成DataResult.error；错误UUID可能跳出orElse，不能称安全fallback。没有旧ID映射/格式版本升级代码，不因标legacy名字伪称迁移完成。',
 'setXpRaw更新map并setDirty，在线同步并按level升降发perk/advancement；getXpMap返回活动map引用，setXpMap直接接引用。setXpDiff先取old，离线只merge scheduledXP并return true，不setDirty；在线发可取消XpEvent，未取消才setXpRaw(event.skill, oldValue+event.amountAwarded)，技能若由hook改名依旧用旧技能oldValue，普通long加法无溢出检查。awardScheduledXP先copy该UUID queue然后remove原队列，逐项setXpDiff忽略boolean；在线事件取消既不重排也没成功setDirty，途中再离线则setXpDiff重新排队，避免迭代修改只是内存操作，不能称崩溃持久exactly-once。LoginHandler先清客户端mySkills并发XP和levelCache，然后awardScheduledXP。',
 'Dynasty可以比较world UUID真值与PlayerPersisted白名单的生命周期，选择一种权威来源再处理重生/登录同步，不能靠Clone全ForgeData。任务进度/旧任务册的未知注册键和Count/tag应保留，避免失败整map变空或重建默认栈。离线/延后恢复要有dirty、提交成功确认与可重试来源，不把remove-before-consume或Map.copy当一次成功保证；死亡惩罚与永久进度恢复必须明确区分，不把PMMO配置扣XP移植为Dynasty新惩罚。',
 'getPlayerSkillLevel在getLevelFromXP后再跑skill-specific LevelRegistry并maxcap；缓存startup或配置reload重算，动态公式分支未clear旧levelCache就追加，静态列表成功分支替换；未模拟reload，不能声称显示必错。真实consumer Core.doesPlayerMeetReq按恢复XP转level，RightClickItem失败取消并设置FAIL，数据也驱动perk；完整读权限路径、奖励主方法和XP存取，但所有datapack loader、AutoValues、第三方perks、cheese/party内部与ClientUtils弹窗未全域展开，不把它们另计或宣称完整游戏验收。PlayerDeathHandler在loss=0立即返回，否则按保等级/只扣excess配置下界max(safeXP, xp-loss)更新同UUID世界真值；onRespawn不是Clone，只触发perks。未启动客户端/服务端/网络/编译/测试，不证明真实死亡或损坏存档行为。',
 '世界XP+offlinequeue+level cache+同步+死亡处理+perk/等级消费者统一一个进度家族，两个map/每技能/队列方法/死亡分支不拆数。与028Reskillable持久对象和真值位置/未知键保留/缓存/消费控制流不同，广义永久进度相似仍供Kepler裁定。主项目延续官方Caltinor仓且1.20.1分支只固定一份，1.12/新NeoForge/派生镜像不额外计。之前003排除的Harmonised7/Project-MMO 404没有当研究，本次真实官网Source才进入审阅。helper credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    targets=[('/storage/PmmoSavedData.java',None),('/config/codecs/CodecTypes.java',['UUID_CODEC']),('/core/Core.java',['INSTANCES','IDataStorage data','LogicalSide side']),('/api/events/XpEvent.java',None)]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(t in fragment for t in needles):continue
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
    (DOC/'batch-029.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
