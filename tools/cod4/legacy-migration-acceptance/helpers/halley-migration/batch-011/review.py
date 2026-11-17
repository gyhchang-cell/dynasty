"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-011'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))




add('astralsorcery-player-research-legacy-perk-format-to-uuid-store-and-clone-effects',[
 ('data/research/PlayerPerkData.java','load'),('data/research/PlayerPerkData.java','isLegacyData'),('data/research/PlayerPerkData.java','loadLegacyData'),('data/research/PlayerPerkData.java','legacySplitKey'),('data/research/PlayerPerkData.java','save'),('data/research/PlayerPerkData.java','AppliedPerk'),('data/research/PlayerPerkData.java','deserialize'),('data/research/PlayerPerkData.java','serialize'),('data/research/PlayerPerkData.java','setSealed'),('data/research/PlayerPerkData.java','isSealed'),('data/research/PlayerPerkData.java','addAllocation'),('data/research/PlayerPerkData.java','getEffectGrantingPerks'),('data/research/PlayerPerkData.java','getPerkData'),('data/research/PlayerPerkData.java','applyPerkAllocation'),('data/research/PlayerPerkData.java','updatePerkData'),('data/research/PlayerPerkData.java','getData'),('data/research/PlayerPerkData.java','findAppliedPerk'),
 ('data/research/PlayerProgress.java','load'),('data/research/PlayerProgress.java','store'),('data/research/PlayerProgress.java','copy'),('data/research/PlayerProgress.java','getPerkData'),('data/research/PlayerProgress.java','getAttunedConstellation'),('data/research/PlayerProgress.java','didReceiveTome'),('data/research/PlayerProgress.java','setTomeReceived'),
 ('data/research/ResearchHelper.java','getProgress'),('data/research/ResearchHelper.java','getProgressServer'),('data/research/ResearchHelper.java','loadPlayerKnowledge'),('data/research/ResearchHelper.java','load_unsafe'),('data/research/ResearchHelper.java','load_unsafeFromNBT'),('data/research/ResearchHelper.java','savePlayerKnowledge'),('data/research/ResearchHelper.java','saveAndClearServerCache'),('data/research/ResearchHelper.java','getPlayerFile'),('data/research/ResearchHelper.java','getPlayerBackupFile'),('data/research/ResearchHelper.java','getPlayerDirectory'),
 ('data/research/ResearchIOThread.java','onServerStart'),('data/research/ResearchIOThread.java','onServerStop'),('data/research/ResearchIOThread.java','reset'),('data/research/ResearchIOThread.java','doSave'),('data/research/ResearchIOThread.java','scheduleSave'),('data/research/ResearchIOThread.java','flushAndSaveAll'),('data/research/ResearchIOThread.java','saveProgress'),('data/research/ResearchIOThread.java','saveNow'),
 ('data/research/ResearchManager.java','grantResearch'),('data/research/ResearchManager.java','grantProgress'),('data/research/ResearchManager.java','applyPerk'),('data/research/ResearchManager.java','doApplyPerk'),('data/research/ResearchManager.java','setTomeReceived'),
 ('event/handler/EventHandlerCache.java','attachListeners'),('event/handler/EventHandlerCache.java','onPlayerConnect'),('event/handler/EventHandlerCache.java','onPlayerClone'),('event/handler/EventHandlerCache.java','onServerStop'),
 ('perk/PerkEffectHelper.java','onPlayerCloneEvent'),('perk/PerkEffectHelper.java','onPlayerConnectEvent'),('perk/PerkEffectHelper.java','modifyAllPerks'),('perk/PerkEffectHelper.java','modifySource'),('perk/PerkEffectHelper.java','applySource'),('perk/PerkEffectHelper.java','removeSource'),
 ('perk/PerkTree.java','getPerk'),('perk/PerkTree.java','getRootPerk'),('perk/PerkTree.java','getVersion'),('perk/PerkTree.java','getData'),('perk/data/PreparedPerkTreeData.java','getVersion'),('perk/data/PreparedPerkTreeData.java','getRootPerk'),('perk/data/PreparedPerkTreeData.java','getPerk'),('constellation/ConstellationRegistry.java','getConstellation'),
 ('data/research/PlayerPerkAllocation.java','unlock'),('data/research/PlayerPerkAllocation.java','PlayerPerkAllocation'),('data/research/PlayerPerkAllocation.java','getType'),('data/research/PlayerPerkAllocation.java','getLockUUID'),('data/research/PerkAllocationType.java','getSaveKey'),('util/MiscUtils.java','getEnumEntry'),('util/nbt/NBTHelper.java','readList'),
 ('common/CommonProxy.java','initialize'),('common/CommonProxy.java','attachLifecycle'),('common/CommonProxy.java','attachEventHandlers'),('common/CommonProxy.java','onServerStarted'),('common/CommonProxy.java','onServerStopping'),('common/CommonProxy.java','getASServerDataDirectory'),('util/ServerLifecycleListener.java','wrap'),('util/ServerLifecycleListener.java','start'),('util/ServerLifecycleListener.java','stop'),('astralsorcery/AstralSorcery.java','AstralSorcery')],
 '真实服务端按UUID首次查询进度时读世界astralsorcery/playerdata文件；研究获得/技能分配生成保存快照；玩家登录和Clone从UUID进度重建效果，停止事件刷出待保存数据后清缓存。',
 '旧sealedPerks存在即识别legacy；旧perks的perkName/perkData、sealedPerks、pointTokens、perkExp、perkTreeVersion；现代perks带applicationData/applicationTypes；外围星座、研究ordinal、tier、bookReceived、usePerkAbilities。',
 '匹配perk树版本时把旧perks恢复成UNLOCKED分配，再给已存在分配设置sealed；旧pointTokens小写化、取首冒号后路径、改写横线/冒号，固定到astralsorcery命名空间。现代tokens仅将整个ResourceLocation字符串横线改下划线。树版本不匹配时仅重建当前调谐星座root，两个格式均保留经验，却不保留旧分配和令牌。新写格式不再写sealedPerks，PlayerProgress.copy通过store/load重新解析。',
 '旧缺bookReceived视为true避免登录反复发书；缺usePerkAbilities则默认true。研究/tier越界ordinal经MiscUtils钳制，与AppliedPerk.applicationTypes直接values()[type]无界检查不同。Clone只撤旧对象效果、在新对象添加基于UUID进度的未封印效果，不拷贝整份实体ForgeData；文件快照按UUID合并最近提交。CommonProxy按注册顺序调用停止监听，ResearchIOThread排在EventHandlerCache清进度之前。磁盘恢复不是可靠事务：backup getter会先创建空文件，而Files.copy没有REPLACE_EXISTING；有效备份读完后的copy-back也可能因主文件已存在而落入第二层失败清空分支。',
 'Dynasty永久历史可按稳定UUID独立保存并在Clone仅重建派生效果，或仅白名单迁移真正永久的旧root键；先保留原始载荷，显式映射旧别名并检查冲突，再确认写出成功，不能把非法数据默认值、版本变更或复制过程当成功迁移。书籍发放标记的缺省策略须按实际历史设计，不能机械套true。',
 '非1.20发布二进制复现；固定官方1.16-indev commit，不声称特定jar对应。legacy识别仅contains，无类型/版本联合验证；命名空间被忽略可碰撞，现代全字符串替换也可能改合法命名空间。坏ResourceLocation/非法applicationTypes可中断整份load，未知perk会跳过。load失败分支即使.lerror复制失败仍删除两份进度，这是静态风险绝不执行或建议照搬。缺主文件会新建空文件而不尝试已有备份。saveNow备份复制失败仍写主文件，主写IOException忽略；队列在写后无成功确认即清除，HashMap/普通标志跨Timer线程无同步，无可靠故障重试。copy重新load可能再次执行重置。仅审到效果分派/去重调用边界，未验证各ModifierManager数值实现，不主张所有属性运行正确；禁止迁入健康/冷却等运行态或引入死亡处罚。',
 '旧令牌/封印/XP/book缺省、UUID文件读写、队列合并、Clone效果重建合成个人永久研究进度一条；每键、每perk、每个getter、网络同步、线程与备份都不是额外候选。与主账UUID/Clone/白名单及本助手PST等家族有交叠；需Kepler按实际语义而非方法数决定信用，credit0。')

add('astralsorcery-knowledge-share-item-export-whitelist-and-monotone-merge',[
 ('data/research/PlayerProgress.java','storeKnowledge'),('data/research/PlayerProgress.java','loadKnowledge'),('data/research/PlayerProgress.java','acceptMergeFrom'),('data/research/PlayerProgress.java','memorizeConstellation'),('data/research/PlayerProgress.java','discoverConstellation'),('data/research/PlayerProgress.java','setTierReached'),('data/research/PlayerProgress.java','forceGainResearch'),('data/research/PlayerProgress.java','isValid'),('data/research/PlayerProgress.java','getTierReached'),
 ('item/ItemKnowledgeShare.java','onItemRightClick'),('item/ItemKnowledgeShare.java','onItemUse'),('item/ItemKnowledgeShare.java','getKnowledge'),('item/ItemKnowledgeShare.java','setKnowledge'),('item/ItemKnowledgeShare.java','getKnowledgeOwner'),('item/ItemKnowledgeShare.java','getKnowledgeOwnerName'),('item/ItemKnowledgeShare.java','isCreative'),('item/ItemKnowledgeShare.java','canInscribeKnowledge'),('item/ItemKnowledgeShare.java','tryGiveKnowledge'),('item/ItemKnowledgeShare.java','tryInscribeKnowledge'),
 ('data/research/ResearchHelper.java','mergeApplyPlayerprogress'),('data/research/ResearchHelper.java','savePlayerKnowledge'),('util/nbt/NBTHelper.java','getPersistentData'),('util/nbt/NBTHelper.java','hasPersistentData'),('util/nbt/NBTHelper.java','getData')],
 '非创造知识共享物品由所有者铭刻后，其他真实服务器玩家在实际use入口使用，读取knowledgeTag并合入收取者永久研究进度。',
 '物品mod compound的知识白名单knowledgeTag、所有者UUID及显示名；known/seen星座列表、tier、research和wasAttuned。',
 'storeKnowledge仅导出星座认识、研究与等级，不导出perk/XP/令牌、当前调谐星座、论文、发书标记或能力开关。loadKnowledge并集合并星座、取较高tier、union研究；wasAttuned虽写却没有被该reader读取。真实give经ResearchHelper.acceptMergeFrom再次只合白名单，sync并保存，不覆盖收取者原有更高进度。',
 'canInscribe只允许空owner或同UUID铭刻；give对自己/无主且可铭刻的情况return，其他玩家才拿到知识。读取错误catch后返回null，不能把坏载荷视作完整恢复。give的tier更新条件在合并前后比较源progress而不是收取者，因此额外tier通知分支静态上不会反映收取者升级；mergeApply本身已sync。物品不消耗，可重复分享，集合幂等而不生成额外技能经验。',
 'Dynasty兼容导入应定义最小永久历史白名单，用并集/单调等级合并并保留已有进度，明确所有者授权、是否可转交及拒绝坏载荷；白名单writer和reader逐字段对应，避免存了未消费的字段却声称恢复。',
 '创造分支forceMaximizeAll不是迁移，本条不以其为证据计数。isValid始终true，不能当结构验证；ResourceLocation异常会使整个知识载荷拒收，reader不是逐项隔离。载体owner只约束铭刻，不是禁止持有者读取分享的访问控制。无运行或存档验证，不把同步包额外分支或每个星座当新实现。',
 '有明确不同的可转让物品永久知识对象、导出白名单与非破坏合并语义，提出独立建议；与上一条共用PlayerProgress/存盘支持不重复计，若Kepler将其归同家族应合并；所有知识字段合一链，credit0。')

add('astralsorcery-crystal-properties-durable-item-reader-to-real-tool-stats',[
 ('crystal/CrystalAttributes.java','deserialize',302),('crystal/CrystalAttributes.java','deserialize',442),('crystal/CrystalAttributes.java','serialize'),('crystal/CrystalAttributes.java','Attribute'),('crystal/CrystalAttributes.java','getCrystalAttributes'),('crystal/CrystalAttributes.java','store'),('crystal/CrystalAttributes.java','storeNull'),('crystal/CrystalAttributes.java','copy'),('crystal/CrystalAttributes.java','getProperty'),('crystal/CrystalAttributes.java','getTier'),
 ('item/tool/ItemCrystalTierItem.java','getAttributes'),('item/tool/ItemCrystalTierItem.java','setAttributes'),('item/tool/ItemCrystalTierItem.java','getMaxDamage'),('item/tool/ItemCrystalTierItem.java','getDestroySpeed'),('item/tool/ItemCrystalTierItem.java','hitEntity'),('item/tool/ItemCrystalTierItem.java','onBlockDestroyed'),
 ('crystal/CrystalCalculations.java','calculate'),('crystal/CrystalCalculations.java','getToolDurability'),('crystal/CrystalCalculations.java','getToolEfficiency'),('crystal/CrystalProperty.java','modify'),('crystal/CrystalProperty.java','addModifier'),('crystal/property/PropertyToolDurability.java','PropertyToolDurability'),('crystal/property/PropertyToolEfficiency.java','PropertyToolEfficiency'),('crystal/CalculationContext.java','uses'),('crystal/CalculationContext.java','withUse'),('crystal/CalculationContext.java','withUsage'),('crystal/CalculationContext.java','newBuilder'),('crystal/CalculationContext.java','addUsage'),('crystal/CalculationContext.java','build'),('util/nbt/NBTHelper.java','getPersistentData'),('util/nbt/NBTHelper.java','getData'),('util/nbt/NBTHelper.java','hasPersistentData')],
 '已有水晶工具ItemStack实际计算耐久上限和有效挖掘速度时，读取物品持久化crystalProperties，属性注册表恢复后进入真实工具计算，使用工具消耗耐久。',
 'mod持久compound下crystalProperties.attributes列表，每项property ResourceLocation、pLevel整数、discovered布尔；不是tooltip或临时网络包。',
 '外层缺crystalProperties/空compound返回null，合法但未知property跳过；已知property保留tier并构造Attribute。serialize写回完整列表；copy也是序列化再解析。真正getMaxDamage按USE_TOOL_DURABILITY乘系数并round，getDestroySpeed按USE_TOOL_EFFECTIVENESS乘系数；具体工具耐久系数1+0.25*tier、效率1+0.15*min(tier,4)。',
 'Attribute构造函数忽略discovered形参而恒赋true，因此保存false也不能无损恢复；这不是reader里显示的getBoolean就能证明。reader不钳制tier，不去重property，重复项在calculate逐项生效，坏ResourceLocation中断而不是跳过。非空compound但缺/错attributes会读成空属性对象；与真正null的默认工具路径要区分。setAttributes(null)仅移除该对象键，不清整件物品NBT。',
 'Dynasty旧ID/永久物品状态迁移需跟到真实耐久/功能消费者，确认构造器没有篡改保存字段；注册表缺项应保留原始未知载荷待兼容，读出后验证范围和唯一性，避免重复属性放大效果。用明确存在/空/错误类型区分恢复策略。',
 '没发现本水晶读器旧ID别名，不虚构迁移。此条属于真实完整持久物品语义，不是Clone实现；工具耐久与效率仅同属性对象的两个用途，不拆两条。Builder中的tier上限不等于deserialize有同样校验；非法负tier可进入算式，本地无finite/非负保护，未实际运行。attuned/trait简单ID getter未追到独立消费者，未纳入候选。',
 '物品水晶属性reader/writer/拷贝及耐久/挖掘消费者合一语义链；每个property、tier、工具变体、两个公式不独立计数。与普通物品NBT/属性家族架构重合但具体持久对象不同，Kepler审定，credit0。')
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
    (DOC/'batch-011.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
