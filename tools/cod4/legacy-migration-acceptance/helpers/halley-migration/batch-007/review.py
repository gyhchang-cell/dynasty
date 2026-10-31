"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-007'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))


add('waystones-world-directory-legacy-origin-and-physical-uuid-relink',[
 ('core/Waystone.java','read',168),('core/Waystone.java','write',199),('core/Waystone.java','isOwner'),('core/Waystone.java','isValidInLevel'),('core/Waystone.java','resolveDestination'),
 ('core/WaystoneManager.java','read'),('core/WaystoneManager.java','save'),('core/WaystoneManager.java','get'),('core/WaystoneManager.java','addWaystone'),('core/WaystoneManager.java','updateWaystone'),('core/WaystoneManager.java','removeWaystone'),('core/WaystoneManager.java','getWaystoneById'),('core/WaystoneManager.java','findWaystoneByName'),
 ('core/WaystoneProxy.java','WaystoneProxy'),('core/WaystoneProxy.java','isValid'),('core/WaystoneProxy.java','getBackingWaystone'),
 ('entity/WaystoneBlockEntityBase.java','load'),('entity/WaystoneBlockEntityBase.java','saveAdditional'),('entity/WaystoneBlockEntityBase.java','onLoad'),('entity/WaystoneBlockEntityBase.java','loadBackingWaystone'),('entity/WaystoneBlockEntityBase.java','initializeWaystone'),('entity/WaystoneBlockEntityBase.java','initializeFromExisting'),('entity/WaystoneBlockEntityBase.java','initializeFromBase'),
 ('block/WaystoneBlockBase.java','setPlacedBy'),('block/WaystoneBlockBase.java','onRemove'),('block/WaystoneBlockBase.java','playerWillDestroy'),
 ('message/EditWaystoneMessage.java','handle'),('message/EditWaystoneMessage.java','makeNameLegal'),('core/PlayerWaystoneManager.java','mayEditWaystone'),('core/PlayerWaystoneManager.java','mayEditGlobalWaystones'),('core/PlayerWaystoneManager.java','activeWaystoneForEveryone'),('core/PlayerWaystoneManager.java','removeKnownWaystone'),
 ('api/IWaystone.java','wasGenerated'),('api/IWaystone.java','hasName'),('api/IWaystone.java','hasOwner'),('core/WaystoneTypes.java','isSharestone')],
 'Overworld SavedData 按UUID保存整个世界传送点目录；blockentity读UUID/onLoad关联目录；持有原UUID物品放置时可重用原条目，编辑消息修改目录。',
 'Waystones compound列表：WaystoneUid、Name、World资源键、BlockPos、WasGenerated旧布尔、Origin新枚举、可选OwnerUid/Type、IsGlobal。blockentity单存UUID；客户端更新包另带Waystone快照。',
 'WasGenerated=true回退WILDERNESS，否则UNKNOWN；存在Origin时尝试覆盖，非法枚举保留上述回退。缺Type为WAYSTONE，缺OwnerUid为null；目录加载跳过无名字sharestone，同UUID后项覆盖。blockentity找不到有效目录对象时可创建新UUID，并在onLoad把已有对象维度/位置改到实际方块。',
 '旧布尔兼容不是静态别名表，而是进入真实对象生成来源与后续限制的控制流。owner为空时isOwner允许任何玩家，之后激活可指定owner，缺旧owner改变的是实际编辑权限。Type判sharestone含path后缀检查，未校验namespace；未命名sharestone清理是真删除恢复条目。放置有有效原UUID才initializeFromExisting并移动其目录坐标；无效UUID走全新初始化，不保留旧身份。server=null得到独立clientStorageCopy，不能用客户端目录缓存替代服务器持久真值。',
 'Dynasty旧状态转换要明确旧新字段同时存在时优先级、无效新值的保底和未知身份保留策略；有持久目录与物理载体双份状态时明确谁是权威。修复任务物品不能因索引不存在就生成新身份，必须先确认旧ID/进度恢复来源，避免断开原引用。',
 '缺WaystoneUid、坏UUID/World字符串会抛出且列表逐项无隔离，不能声称耐坏档；只兼容所见WasGenerated、缺Type/owner，不支持旧数字维度或任意旧ID。write复用既有compound且owner变null时不删除旧OwnerUid；正常manager.save传新compound，该残留只适用于复用调用。onLoad改目录坐标未在该方法显式manager.setDirty，不声称独立保证下一次存盘。物品掉落loottable未读，不能断言所有丝触物品均实际携UUID；仅证明setPlacedBy遇UUID后的分支。代理缓存backing可能与后续目录变化不同步，isValid检查目录存在不等于物理块/维度目标可传送。未执行Balm同步/原生SavedData存储或游戏。',
 '世界目录旧Origin读器、blockentity重连、物品原UUID放置、编辑和清理同一传送点生命周期合为一条；不按各variant/type或网络/代理多计。与其他世界注册目录有架构风险，差异为真实旧布尔转换及UUID双表示重连；最终由Kepler去重，辅助credit0。')

add('waystones-player-activated-uuid-order-and-cross-loader-persistent-domain',[
 ('core/PersistentPlayerWaystoneData.java','getWaystones'),('core/PersistentPlayerWaystoneData.java','getWaystonesData'),('core/PersistentPlayerWaystoneData.java','getActivatedWaystonesData'),('core/PersistentPlayerWaystoneData.java','activateWaystone'),('core/PersistentPlayerWaystoneData.java','isWaystoneActivated'),('core/PersistentPlayerWaystoneData.java','deactivateWaystone'),('core/PersistentPlayerWaystoneData.java','swapWaystoneSorting'),('core/PersistentPlayerWaystoneData.java','getWarpStoneCooldownUntil'),('core/PersistentPlayerWaystoneData.java','setWarpStoneCooldownUntil'),('core/PersistentPlayerWaystoneData.java','getInventoryButtonCooldownUntil'),('core/PersistentPlayerWaystoneData.java','setInventoryButtonCooldownUntil'),
 ('core/PlayerWaystoneManager.java','activateWaystone'),('core/PlayerWaystoneManager.java','isWaystoneActivated'),('core/PlayerWaystoneManager.java','getWaystones'),('core/PlayerWaystoneManager.java','getPlayerWaystoneData'),('core/PlayerWaystoneManager.java','getNearestWaystone'),
 ('core/WaystoneProxy.java','isValid'),('core/WaystoneProxy.java','getBackingWaystone'),('core/WaystoneManager.java','getWaystoneById'),('core/WaystoneManager.java','get'),
 ('handler/LoginHandler.java','onPlayerLogin'),('core/WaystoneSyncManager.java','sendActivatedWaystones'),('block/WaystoneBlock.java','handleActivation'),('block/WaystoneBlockBase.java','use'),('menu/WaystoneSelectionMenu.java','createWaystoneSelection'),
 ('common/src/main/java/net/blay09/mods/balm/api/BalmHooks.java','getPersistentData'),('common/src/main/java/net/blay09/mods/balm/api/Balm.java','getHooks'),('forge/ForgeBalmRuntime.java','getHooks'),('forge/ForgeBalmHooks.java','getPersistentData'),
 ('forge/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','load'),('forge/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','saveWithoutId'),('forge/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','getFabricBalmData'),
 ('fabric/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','load'),('fabric/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','saveWithoutId'),('fabric/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','getFabricBalmData'),('fabric/src/main/java/net/blay09/mods/balm/mixin/EntityMixin.java','setFabricBalmData'),('fabric/FabricBalmHooks.java','getPersistentData'),('fabric/FabricBalm.java','onInitialize')],
 '真实玩家激活、登录全局点补齐、GUI候选列表/最近传送点消费；通过Balm持久域访问已激活UUID列表和排序。补读声明版本的Forge/Fabric存储路径与COPY_FROM支持链。',
 'BalmData.WaystonesData.Waystones字符串UUID有序列表；同域还有WarpStoneCooldownUntilUnix和InventoryButtonCooldownUntilUnix长整型时间。Forge玩家置于Player.PERSISTED_NBT_TAG/BalmData，Fabric置于实体根BalmData。',
 '嵌套compound/list读取后重新put挂载；列表项转UUID代理，目录无该UUID时读取方法立即iterator.remove。管理层先查已激活再追加，底层直接activate本身不去重；排序可以首移/尾移/交换。Balm在Forge目标BalmData空时导入Fabric根数据；Fabric载根BalmData为空时尝试ForgeData.PlayerPersisted.BalmData。',
 '已解锁列表属于玩家事实，而前条目录属于世界对象，两者不能互相替代；目录不存在并不保留悬挂解锁记录，普通读取/同步也会改存档域。目录错误加载或身份被重建会影响引用恢复，不能把read当纯查询。Forge钩子明确进入PlayerPersisted，Balm没有在所读路径另做逐字段死亡白名单；Fabric COPY_FROM不看alive，直接将旧compound引用交新玩家而非copy。Fabric importer外层要求根包含BalmData，只有ForgeData但完全没有根BalmData时不进入回退；Forge非空目标域则不合并Fabric源，可能保留部分目标而忽略源中独有键。',
 'Dynasty永久字段应明确保存位置、Clone拷贝范围与跨格式优先级，不能由persistent命名推断行为；只迁移经审定永久键，不能把同域冷却时间一并永久化。恢复阶段先建立世界目录/身份再解析玩家引用，避免读时清理造成不可逆进度遗失；遇未知UUID宜保留原始引用待判定。',
 'Balm仅支持依赖，不计独立参考。Waystones声明7.3.38+1.20.1，官方v7.3.38解到6120c9fb26446d4c2ddb669e4fe016f653fcb3f3，双方gradle.properties声明1.20.1/Forge47.3.27并留哈希，未证明发布二进制逐字节一致。Forge原生PlayerPersisted死亡复制未本批重新审查，不声称新增完整原生Clone验收；只证明本插件实际持久入口。UUID.fromString无catch，错误list类型会被新空list替换。未证明全局目录加载先后、跨模组异常、原子保存或重生/换平台运行表现；Fabric共享compound有别名风险。',
 '玩家列表reader/writer/排序/激活/登录同步与Balm根域迁移/Clone支持只合一条；不按UUID项、冷却getter、Forge/Fabric移植增数。与前条世界目录共享proxy只支持不多计，与其他玩家引用列表/Clone仍需Kepler语义去重。')

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
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-007.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
