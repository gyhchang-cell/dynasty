"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-006'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))


# Handwritten chain specifications follow; supporting methods never add credit.

add('solcarrot-food-history-registry-resolution-clone-and-derived-health',[
 ('tracking/FoodList.java','deserializeNBT'),('tracking/FoodList.java','serializeNBT'),('tracking/FoodList.java','get'),('tracking/FoodList.java','addFood'),('tracking/FoodList.java','getProgressInfo'),('tracking/FoodList.java','invalidateProgressInfo'),('tracking/FoodList.java','getEatenFoods'),('tracking/FoodList.java','getCapability'),
 ('tracking/FoodInstance.java','decode'),('tracking/FoodInstance.java','encode'),('tracking/FoodInstance.java','equals'),('tracking/FoodInstance.java','hashCode'),
 ('tracking/CapabilityHandler.java','attachPlayerCapability'),('tracking/CapabilityHandler.java','onClone'),('tracking/CapabilityHandler.java','onPlayerLogin'),('tracking/CapabilityHandler.java','onPlayerRespawn'),('tracking/CapabilityHandler.java','onPlayerDimensionChange'),('tracking/CapabilityHandler.java','syncFoodList'),
 ('tracking/FoodTracker.java','onFoodEaten'),('tracking/ProgressInfo.java','ProgressInfo'),('tracking/ProgressInfo.java','milestonesAchieved'),
 ('tracking/MaxHealthHandler.java','onPlayerLogin'),('tracking/MaxHealthHandler.java','onPlayerClone'),('tracking/MaxHealthHandler.java','updateFoodHPModifier'),('tracking/MaxHealthHandler.java','getHealthModifier'),('tracking/MaxHealthHandler.java','updateHealthModifier'),('tracking/MaxHealthHandler.java','maxHealthAttribute'),
 ('solcarrot/SOLCarrotConfig.java','Server'),('solcarrot/SOLCarrotConfig.java','shouldResetOnDeath'),('solcarrot/SOLCarrotConfig.java','shouldCount'),('solcarrot/SOLCarrotConfig.java','isAllowed'),('solcarrot/SOLCarrotConfig.java','isHearty'),('solcarrot/SOLCarrotConfig.java','hasWhitelist'),('solcarrot/SOLCarrotConfig.java','matchesAnyPattern'),('solcarrot/SOLCarrotConfig.java','onConfigReload'),('solcarrot/SOLCarrotConfig.java','getBaseHearts'),('solcarrot/SOLCarrotConfig.java','getHeartsPerMilestone'),('solcarrot/SOLCarrotConfig.java','getMilestones'),
 ('communication/FoodListMessage.java','FoodListMessage'),('communication/FoodListMessage.java','handle')],
 '玩家 food capability 读盘、进食、Clone、登录/重生/换维度同步；配置重载重算里程碑及生命上限。',
 'foodList 为物品注册 ResourceLocation 字符串列表；HashSet<FoodInstance> 持久保存已食物品身份。cachedProgressInfo 为派生缓存，不写入保存。',
 'reader 先 clear，再解析列表并过滤返回null的 FoodInstance，最后清派生缓存。Clone 仅死亡且 resetOnDeath=true 时不复制；其他情况以 serialize/deserialize 重建新集合；默认 resetOnDeath=false。同步后按当前配置重新计算固定 UUID 生命属性修饰器。',
 'FoodInstance.decode 对注册查询返回null的条目警告并丢弃；仍注册但不再可食用的条目只警告，仍保留对象，未来恢复可食用性可再参与统计。无旧ID别名映射，删除mod后的引用没有保留占位。ProgressInfo 使用当前 shouldCount 过滤持久集合，故黑白名单/最低营养改变不会立刻清掉所有旧历史；getEatenFoodCount 直接 size 与用于生命的过滤计数不是一回事。addFood 先执行 foods.add，再 &&shouldCount，因此不计分物品仍可进入集合。固定 UUID 更新先 remove 后 add，生命按新旧上限比例调整；Clone 先复制旧健康modifier不等于最终保留旧收益，Respawn sync 再由新历史重算。',
 '借鉴 Dynasty 的永久事实与派生数值分离：保存已完成标记，按当前配置/任务定义重算展示或收益；死亡复制使用明确 subsystem，迁移后清派生缓存。旧ID缺失应保存原始引用或明确fallback，不照搬丢失未知物品引用策略。固定 UUID 防止重复叠加不等于永久进度本身已迁移成功。',
 'ResourceLocation 语法无catch，坏字符串可能中断 clear 后的恢复，未做事务。源里只证明注册lookup=null时丢弃；未下载/审查此版本 ForgeRegistry 默认项内部，不能断言任意缺失ID一定返回null而非默认项。错误类型foodList getList为空会清历史。附加/克隆无try-finally和完整缺cap容错，FoodList.get可抛异常；未运行事件排序、FirstAid分支或生命值效果。网络方法仅支持同步证明，不执行客户端；无生产变更。',
 '食物历史reader、每物品、NBT复制、健康modifier、配置刷新和客户端接收均同链只一条。与其他玩家能力Clone、ScalingHealth派生健康有架构相似；具体区别在持久食物身份集合、当前过滤重算及已注册非食物保留。由Kepler裁定，不自动计数。')

add('diet-suite-bounded-durable-groups-clone-and-effect-cleanup',[
 ('common/capability/PlayerDietTracker.java','load'),('common/capability/PlayerDietTracker.java','save'),('common/capability/PlayerDietTracker.java','copy'),('common/capability/PlayerDietTracker.java','PlayerDietTracker'),('common/capability/PlayerDietTracker.java','initSuite'),('common/capability/PlayerDietTracker.java','setValue'),('common/capability/PlayerDietTracker.java','setValues'),('common/capability/PlayerDietTracker.java','getValues'),('common/capability/PlayerDietTracker.java','getModifiers'),('common/capability/PlayerDietTracker.java','setModifiers'),('common/capability/PlayerDietTracker.java','setSuite'),('common/capability/PlayerDietTracker.java','setEaten'),('common/capability/PlayerDietTracker.java','setActive'),
 ('common/capability/PlayerDietTracker.java','tick'),('common/capability/PlayerDietTracker.java','consume'),('common/capability/PlayerDietTracker.java','apply'),('common/capability/PlayerDietTracker.java','applyEffects'),('common/capability/PlayerDietTracker.java','decay'),('common/capability/PlayerDietTracker.java','addEaten'),('common/capability/PlayerDietTracker.java','sync'),
 ('common/capability/DietCapabilityEventsListener.java','attachCapabilities'),('common/capability/DietCapabilityEventsListener.java','playerClone'),('common/capability/DietCapabilityEventsListener.java','serializeNBT'),('common/capability/DietCapabilityEventsListener.java','deserializeNBT'),('common/capability/DietCapabilityEventsListener.java','playerTick'),('common/capability/DietCapabilityEventsListener.java','finishItemUse'),('common/capability/DietCapabilityEventsListener.java','playerRespawned'),('common/capability/DietCapabilityEventsListener.java','playerLoggedIn'),('common/capability/DietCapability.java','get'),
 ('services/ForgeCapabilityService.java','get'),('services/ForgeRegistryService.java','getItem'),('services/ForgeRegistryService.java','getAttribute'),('services/ForgeRegistryService.java','getAttributeKey'),('services/ForgeRegistryService.java','getItemKey'),('suite/DietSuites.java','getSuite'),('effect/DietEffect.java','getMatches'),('effect/DietEffect.java','inRange'),('config/DietConfig.java','Server')],
 'Forge 玩家diet_tracker 挂载、读盘、进食与END tick；服务器 Clone 调用按死亡类型复制；每80tick清理旧效果UUID再按实际饮食组重新施加。',
 '当前 suite 定义的组名直接作为根float键，Modifiers 列表记录 AttributeName及UUIDs，Eaten字符串物品列表，Active布尔。suite 字段初始 builtin；prevFood/captured为运行时。',
 '缺组取配置默认并clamp0..1，未知保存组不读；无Active时默认true。属性查不到则跳过，物品查询Optional存在才入集合。Clone 按当前suite逐组复制，死亡按RESET/AMOUNT/PERCENT计算损失；Active复制，Modifiers仅非死亡复制；Eaten和suite在copy中都未复制。',
 '永久饮食组、已吃历史、属性清理索引、开关及运行时字段用途不同，不能看到save全写就认为Clone全保留。save/load均未写/读suite名称，constructor以builtin初始化；setValues仅replace已存在组，若构造时suite无有效定义则load不会补入新key。每80tick按已记录 attribute+UUID移除旧modifier并清索引，再由当前组条件加固定effectUUID的永久modifier并记录，防止直接按旧收益无限累加。死亡默认配置AMOUNT、loss100、min0，是这个模组有意惩罚，不是Dynasty可复制政策。PERCENT与AMOUNT下Math.min(original, max(new,min))避免低于min的原值被死亡反而提高。',
 '借鉴字段用途清单与Clone分项策略，把永久任务事实、派生属性、重建索引和临时计时分开；Dynasty只保留经审定永久字段，绝不引入Diet死亡惩罚。旧格式恢复须先确认初始化定义可用，再恢复获准键；不要只用map.replace而默默丢掉合法旧字段。按固定UUID清旧再派生重算适合避免重复收益。',
 '本条是饮食状态真实持久/Clone链，不是新增旧别名映射。suite/Eaten的复制缺口是已读源码边界，不声称已运行复现；外部API可能另设suite，未证明所有外部调用。ResourceLocation和UUID.fromString无逐条catch，坏条目可中断load；clamp未证明处理NaN。setModifiers浅复制Set引用，未证明与旧实体完全隔离；死亡不复制清理索引时旧modifier是否由Minecraft属性复制残留未运行验证。仅Forge平台审阅；Fabric/Quilt移植不另计，全部事件扩展和网络内部未穷尽。',
 '同一tracker的组数、字段、死亡公式分支、效果条件枚举、网络同步、平台适配、getter均不拆计；与温度白名单和其他选择性Clone有架构风险，但具体在suite定义约束/饮食值惩罚及效果清理索引。与SoL身份集合不是换键克隆；最终语义去重仍由Kepler。')

def declaration_evidence():
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    wanted={'common/capability/PlayerDietTracker.java':{65,66,67,69,70,72,73}}
    output=[]
    for source in json.loads((BASE/'source-manifest.json').read_text()):
        for f in source['files']:
            if not any(f['path'].endswith(suffix) for suffix in wanted):continue
            starts=next(lines for suffix,lines in wanted.items() if f['path'].endswith(suffix))
            raw=(ROOT/f['source']).read_bytes()
            for n in walk(PARSER.parse(raw).root_node):
                if n.type!='field_declaration' or n.start_point.row+1 not in starts:continue
                body=raw[n.start_byte:n.end_byte].decode()
                output.append(dict(repo=source['repo'],commit=source['commit'],git_tree=source['git_tree'],**f,
                    start=n.start_point.row+1,end=n.end_point.row+1,name='tracker ownership/default field declaration',node_type=n.type,
                    text=body,context=body,excerptSha256=sha(body.encode()),normalizedSha256=norm(n,raw),
                    candidate_id=sha((source['repo']+source['commit']+f['path']+str(n.start_byte)).encode())[:20],
                    url='https://github.com/'+source['repo']+'/blob/'+source['commit']+'/'+f['path']+'#L'+str(n.start_point.row+1)+'-L'+str(n.end_point.row+1),
                    role='support_only_not_method_not_additional_credit',credit=0))
    assert len(output)==7
    return output

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
        row['source_declarations']=declaration_evidence() if spec['family']=='diet-suite-bounded-durable-groups-clone-and-effect-cleanup' else []
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-006.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
