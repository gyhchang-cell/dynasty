"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-003'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

add('passive-skill-tree-version-refund-clone-and-rebuild',[
 ('capability/skill/PlayerSkills.java','deserializeNBT'),('capability/skill/PlayerSkills.java','serializeNBT'),
 ('PlayerSkillsProvider.java','attachCapability'),('PlayerSkillsProvider.java','persistThroughDeath'),
 ('PlayerSkillsProvider.java','serializeNBT'),('PlayerSkillsProvider.java','deserializeNBT'),
 ('PlayerSkillsProvider.java','restoreSkillsAttributeModifiers'),('PlayerSkillsProvider.java','sendTreeResetMessage'),
 ('PlayerSkillsProvider.java','get'),('SkillsReloader.java','getSkillById'),
 ('skill/PassiveSkill.java','isInvalid'),('skill/PassiveSkill.java','learn'),('skill/PassiveSkill.java','remove'),
 ('player/AttributeBonus.java','onSkillLearned'),('player/AttributeBonus.java','applyAttributeModifier'),
 ('player/GrantItemBonus.java','onSkillLearned')],
 '技能数据读盘或服务端 PlayerEvent.Clone，之后玩家加入世界恢复已学习效果。',
 '自有 capability 中 TreeVersion UUID、Points、Skills 字符串列表；writer 另写 TreeReset。',
 '版本不匹配或任一技能缺失/无效时清空技能并按整个旧列表长度退点；版本匹配则解析注册表对象。Clone 只复制自己的序列化域；入世界 learn(false) 重建效果并抑制首次学习物品奖励。',
 'reader 先清 skills，后读取 Points；版本缺失也走不匹配分支。遇无效技能会撤掉本轮已读技能并退整个列表长度，不是保留已成功子集。Clone 明确 server guard、reviveCaps→自己的 serialize/deserialize→invalidateCaps，没有 isWasDeath 分支。属性学习通过 UUID 检查并添加 transient modifier；MAX_HEALTH 修改按原生命比例恢复。GrantItemBonus 在 firstTime=false 时直接返回，避免恢复时再次发一次性学习物品。TreeReset 虽写出，但 reader 没有读取它，也没有在成功路径清 false；新对象可能失去待通知状态、复用对象可能保留旧 true。',
 '可借鉴永久字段白名单、存档版本与内容合法性双校验、数据复制与运行时效果重建分离；quest_ledger 旧 ID 检测不能无条件重置合法新状态。一次性奖励必须与效果重建区分，不能由 Clone 重复发放。',
 '不是旧资源 ID 映射表；ResourceLocation.parse 语法错误未 catch，旧列表重复 ID 没去重、点数无范围校验。revive/invalidate 无 try/finally。没有证明所有技能奖励均 firstTime 安全，仅补读 AttributeBonus 与 GrantItemBonus 两个真实消费者。固定分支源码研究未编译、未运行或验收。',
 '同一玩家技能存储/Clone/退点/属性恢复合为一条；AttributeBonus、GrantItemBonus 只作支持。与已有技能 capability 克隆、版本清空退点家族可能语义重复，主责可降级为支持而非新增。')

add('scalinghealth-selective-clone-with-death-only-mutators',[
 ('event/DifficultyEvents.java','onPlayerClone'),('event/DifficultyEvents.java','copyCapability'),
 ('event/DifficultyEvents.java','onAttachEntityCapabilities'),('event/DifficultyEvents.java','onAttachWorldCapabilities'),
 ('capability/PlayerDataCapability.java','serializeNBT'),('capability/PlayerDataCapability.java','deserializeNBT'),
 ('capability/PlayerDataCapability.java','setHeartCrystals'),('capability/PlayerDataCapability.java','setPowerCrystalCount'),
 ('capability/PlayerDataCapability.java','updateStats'),('capability/IPlayerData.java','getModifiedHealth'),('capability/IPlayerData.java','getAttackDamageModifier'),
 ('capability/DifficultySourceCapability.java','serializeNBT'),('capability/DifficultySourceCapability.java','deserializeNBT'),
 ('capability/DifficultySourceCapability.java','setDifficulty'),('capability/DifficultySourceCapability.java','canAttachTo'),
 ('utils/config/SHPlayers.java','getCrystalsAfterDeath'),('utils/config/SHPlayers.java','clampExtraHearts'),('utils/config/SHPlayers.java','clampPowerCrystals'),
 ('utils/config/SHDifficulty.java','getDifficultyAfterDeath'),('config/EvalVars.java','apply'),
 ('event/CommonEvents.java','onPlayerLoggedIn'),('event/CommonEvents.java','playerTick'),('event/CommonEvents.java','onLevelChange'),
 ('utils/ModifierHandler.java','setModifier'),('utils/ModifierHandler.java','setMaxHealth'),('utils/ModifierHandler.java','addAttackDamage')],
 '玩家克隆，先复制耐久能力，再按 isWasDeath 区分死亡和返回末地；登录或升级刷新派生属性。',
 'PlayerData 只存 HeartCrystals、PowerCrystals 两整数；DifficultySource 只存 Difficulty 浮点。',
 '克隆先 copy 两个明确 capability，再失效旧对象；非死亡直接返回。死亡先 updateStats，再计算配置表达式后的心数与难度并调用限幅 setter；登录按已存值重建固定 UUID 属性。',
 '这是有选择的域复制而非 ForgeData/所有能力复制。AFK、timeAfk、lastPos 和 difficulty.exempt 没进序列化，Clone 不保留它们。reader 直接 getInt/getFloat 绕过 setter 限幅，合法性边界只在后续 setter。固定健康/攻击 UUID 使用 remove→addPermanentModifier，可避免简单叠加。死亡心数由当前最大生命与配置表达式差值换算，表达式绑定实际 player/world/pos 变量。XP 变化刷新使用一个全局静态 changedLevelThisTick，首个存活服务端玩家 tick 消费，不是玩家 UUID 队列。',
 '借鉴 Clone 前后顺序、仅死亡才扣减的条件，以及永久计数和派生属性分别恢复。Dynasty 应明确 End 返回/死亡/登录各自策略，白名单复制并用稳定属性身份重建；不能整包复制短时 combat、AFK 或免疫窗口。',
 '上游反射 CapabilityProvider.valid 绕过有效性，TODO 指向 reviveCaps，不应照抄；无 try/finally，Clone 方法没有显式 server guard。非死亡早返不在此立即 updateStats，不能宣称该路径已验证完整恢复。外部 EvalEx 计算及 SilentLib.heal 未执行；未证明配置坏值/NaN 安全。OVERWORLD 与玩家复用同一 codec，不另计世界一条。',
 '与其他自有 capability selective Clone 有高家族重合风险；本条按复制后死亡限定表达式变换和派生属性边界建议独立审查，两个能力/各字段/平台不能拆多计。')

add('scalinghealth-mob-saved-state-versus-ephemeral-processing',[
 ('capability/DifficultyAffectedCapability.java','deserializeNBT'),('capability/DifficultyAffectedCapability.java','serializeNBT'),
 ('capability/DifficultyAffectedCapability.java','tick'),('capability/DifficultyAffectedCapability.java','setDifficulty'),('capability/DifficultyAffectedCapability.java','setProcessed'),
 ('capability/DifficultyAffectedCapability.java','canAttachTo'),('capability/IDifficultyAffected.java','affectiveDifficulty'),
 ('event/DifficultyEvents.java','onAttachEntityCapabilities'),('event/DifficultyEvents.java','onLivingUpdate'),
 ('utils/MobDifficultyHandler.java','process'),('utils/MobDifficultyHandler.java','shouldBecomeBlight'),('utils/MobDifficultyHandler.java','getBlightChance'),('utils/MobDifficultyHandler.java','setEntityProperties'),
 ('event/BlightHandler.java','applyBlightPotionEffects'),('event/BlightHandler.java','startTrackingBlight'),
 ('utils/ModifierHandler.java','setModifier'),('utils/ModifierHandler.java','setMaxHealth'),('utils/ModifierHandler.java','addAttackDamage')],
 '真实怪物 capability 从存档读取后，服务端生物 tick 延迟到 tickCount>2 进行首次处理。',
 '持久字段 Blight、Difficulty；processed 仅内存默认 false。',
 '读入旧 blight/difficulty，但首次 tick 重新按当前区域与随机系数计算 difficulty 并 process，随后 processed=true；固定 UUID 健康/攻击 modifier 替换旧值。',
 '不能把这条写成原样恢复怪物难度：reader 存下的 difficulty 随后被 setDifficulty 覆盖，damage boost 也重新随机。makeBlight=true 才 setIsBlight(true)，false 不清已读 true；有效难度仍按旧 blight 标记乘倍率。初次处理和跟踪开始各有实际客户端 blight 通知。processed 不序列化意味着新建能力读取后允许重处理，而非跨卸载一次消费保证。spawnerSpawns 是内存 UUID 列表，处理时移除，仅该次健康倍率使用。',
 '作为迁移反例：恢复永久数据后不可无意重跑一次性随机授予或生成逻辑。为 Dynasty 永久进度设计 durable processed/version，而运行时缓存重建应可重复且无重新奖励；重应用属性用固定身份。',
 '这是怪物持久状态边界，不是玩家 Clone；若主账限定 player/item 可降为支持。不保证每次重载必然处理：命令路径另可 setProcessed(true)，本条不把命令当第二实现。药水数据驱动 effect.apply、数学库概率实现未逐一研究，不据此宣称随机数具体分布或稳定性。没有编译/游戏验证。',
 '与下一条宠物属性重建共享 ModifierHandler 和 tick 入口，支持方法同链不多计；若主责按更宽的属性恢复家族去重，可将本条与宠物条合并，本条独特点是持久标记与非持久 processed 导致重新随机。')

add('scalinghealth-pet-durable-bonus-and-delayed-reapplication',[
 ('capability/PetHealthCapability.java','deserializeNBT'),('capability/PetHealthCapability.java','serializeNBT'),
 ('capability/PetHealthCapability.java','tick'),('capability/PetHealthCapability.java','addHealth'),('capability/PetHealthCapability.java','canAttachTo'),
 ('event/PetEventHandler.java','onPetInteraction'),('objects/item/StatBoosterItem.java','increasePetHp'),('objects/item/StatBoosterItem.java','consumeLevels'),
 ('event/DifficultyEvents.java','onAttachEntityCapabilities'),('event/DifficultyEvents.java','onLivingUpdate'),
 ('utils/ModifierHandler.java','setModifier'),('utils/ModifierHandler.java','setMaxHealth')],
 '服务端玩家拿 HeartCrystal 与已驯服动物互动增加永久生命；重载后服务端已驯服宠物 tick 恢复属性。',
 'SHPetBonusHealth 浮点为永久累计量；refreshed 只为新 capability 对象的运行时 false。',
 '互动费用满足时 addHealth 累加并立即按累计量替换健康 modifier；写盘只写累计量。读盘后 tickCount>2 且未 refreshed 才重新应用，置 refreshed=true。',
 'pet reader 不重放付费互动，仅读累计量；延迟刷新按保存总量设置而非在旧 modifier 上继续加。实际互动过滤功能开关、HeartCrystal、TamableAnimal、isTame 与服务端；未检查 interacting player 是否宠物 owner。increasePetHp 在 capability ifPresent 之后无条件 shrink 与扣等级，能力缺失仍可能付费，不能借鉴成事务。refreshed 在重应用前先置 true，异常后无重试机制。',
 '把永久累计奖励与运行时属性恢复分离，恢复不得扣物品、重复增长或重放玩家互动；为永久字段设独立 owner/权限、范围校验和缺失能力时的失败原子性。仅用于研究建议，不修改现有正式实现。',
 'getFloat 没上下界/有限值校验；不存在旧 ID 别名。refreshed 未在 deserializeNBT 重置，已刷新对象再次读盘不会因此自动重应用。功能关闭/未驯服不会 tick。本条不证明跨模组永久属性冲突无害；宠物和怪物可能共享同一健康 UUID，未实机验收。',
 '高重复风险：与 batch-003 怪物恢复共享入口和属性 setter，仅在永久累计量、付费写入、不重抽随机、refreshed 生命周期语义确属独立时建议保留；主责可合并，不能按 getter/字段数补 credit。')

add('passive-skill-tree-tagged-item-bonus-reconstruction',[
 ('item/ItemBonusHandler.java','deserializeBonus'),('item/ItemBonusHandler.java','serializeBonus'),
 ('item/ItemBonusHandler.java','getBonusesFromTag'),('item/ItemBonusHandler.java','getItemBonuses'),
 ('item/ItemBonusHandler.java','getCraftingBonuses'),('item/ItemBonusHandler.java','getUpgradeBonuses'),
 ('item/ItemBonusHandler.java','setTagBonuses'),('item/ItemBonusHandler.java','setUpgradeBonuses'),('item/ItemBonusHandler.java','setCraftingBonuses'),
 ('item/ItemBonusHandler.java','addCraftingBonuses'),('item/ItemBonusHandler.java','addEquipmentAttributeBonuses'),('item/ItemBonusHandler.java','mergeItemBonuses'),('item/ItemBonusHandler.java','mergeGroupedItemBonuses'),
 ('item/GroupedItemBonus.java','deserialize',208),('item/GroupedItemBonus.java','serialize',223),
 ('item/EquipmentBonus.java','deserialize',130),('item/EquipmentBonus.java','serialize',141),
 ('player/AttributeBonus.java','deserialize',330),('player/AttributeBonus.java','serialize',340),
 ('recipe/workbench/WorkbenchUpgradeBonusRecipe.java','getResult'),('inventory/menu/WorkbenchMenu.java','updateCraftingResult'),('inventory/menu/WorkbenchMenu.java','addCraftingBonuses'),('player/CraftedItemBonusBonus.java','itemCrafted')],
 '工作台制作/升级物品后写入有注册类型的复合列表；以后装备更换时从存档物品重建玩家 transient 属性。',
 'ItemStack 原 tag 的 UpgradeBonuses 与 CraftingBonuses；每项 type 指定 ItemBonus serializer，GroupedItemBonus 递归 inner_bonuses，EquipmentBonus 包含 skill_bonus。',
 'serializer 写类型标识和具体负载，reader 按当前注册表重建嵌套对象；typed getItemBonuses 扁平化后筛选，装备事件移除旧属性并添加非动态新属性。升级以原物品 copy 为结果，写自己子标签。',
 '这是真实制作物品的状态读取与效果消费，不是通用网络模板。缺 type 或未知 serializer 返回 null，但 getBonusesFromTag 保留 null；typed 路径 type.isInstance 会过滤它。ResourceLocation.parse 和顶层注册表查询在 catch 之外，语法异常不被捕获。嵌套组任一 child 未知会 requireNonNull 抛出，由外层 deserializeBonus 捕获并把整个组降为 null，不是逐子项保留。升级 getResult 读取的是合并后的两类 bonuses，却全部写回 UpgradeBonuses；原 CraftingBonuses 仍保留，可能重复表示原制作奖励。mergeGroupedItemBonuses 忽略 mergeItemBonuses 返回值，实际返回未合并的新列表。',
 '旧 ID 转换应使用实际物品 copy 保留 Count、损伤和无关 tag，并仅转换批准字段；先验证注册类型及嵌套负载，决定未知值保留/隔离规则，避免一项坏数据吞整组。迁移不能把不同子标签重复汇总再写回其中一份。',
 '两种标签、递归组、equipment/attribute serializer 和 workbench writer 整链只算一条。未审查所有 bonus/predicate 类型，因此不宣称所有负载可完整往返；这里的 getOrCreateTag 也可能为读取缺标签物品创建空根。未运行测试或游戏，不把静态疑点称为复现 bug。',
 '与其他存储物品类型化奖励/词缀家族相似；与本批玩家技能条共享 AttributeBonus，但后者 owner 是 player capability、此条 owner 为 ItemStack 且消费触发为换装。仍须 Kepler 按整个持久化家族去重。')

add('passive-skill-tree-poisoned-weapon-finite-use-persistence',[
 ('event/PoisonedWeaponEvents.java','hasPoison'),('event/PoisonedWeaponEvents.java','setPoisonedWeaponEffects'),
 ('event/PoisonedWeaponEvents.java','getPoisonedWeaponEffects'),('event/PoisonedWeaponEvents.java','hasInfinitePoisonUses'),('event/PoisonedWeaponEvents.java','getPoisonUses'),
 ('event/PoisonedWeaponEvents.java','applyPoisonedWeaponEffect'),('event/PoisonedWeaponEvents.java','consumePoisonStack'),('event/PoisonedWeaponEvents.java','clearWeaponEffects'),
 ('recipe/workbench/WorkbenchWeaponPoisoningRecipe.java','getResult'),('recipe/workbench/WorkbenchWeaponPoisoningRecipe.java','assemble'),
 ('recipe/workbench/WorkbenchWeaponPoisoningRecipe.java','isValidPoison'),('inventory/menu/WorkbenchMenu.java','updateCraftingResult')],
 '工作台将药水效果写到近战武器；后续 LivingAttackEvent 从玩家主手武器读取效果并扣可用次数。',
 'poisoned_weapon_effects Compound 列表以及 poisoned_weapon_uses_left 整数，-1 为无限次数。',
 'hasPoison 要求非空效果列表且次数为 -1 或正数；每次使用有限次数减一，到零同时移除次数和效果两个子标签；其余物品根标签保留。',
 '真正消费点是 LivingAttackEvent：来源实体为玩家、主手近战、有有效毒性后先给目标加效果，再对非无限次数 decrement。这里没有显式 server guard、最终伤害成功或取消检查，不能视为成功伤害回执。MobEffectInstance.load 的结果没过滤 null。制作 getResult 用 new ItemStack(weaponStack.getItem()) 而不是 copy，因而直接丢失原 Count、损伤、命名和其他 tag；与上一条升级 copy 路径有实质保留边界差异。',
 '永久物品迁移必须保存剩余次数与无限哨兵语义，不得每次读盘重新满充；耗尽时清整组配套字段。只替换旧 ID 时应保留完整原 stack 状态，不能照用新建物品结果作为迁移模板。',
 '这不是旧 ID 迁移实现，而是真实武器持久状态的 reader/消耗语义参考。未证明该事件代表有效最终伤害，不能借鉴成防重复战斗回执；药效 load 在 Minecraft 中的内部实现未下载研究，不宣称损坏效果数据安全。未进行编译/测试/游戏验收。',
 '与泛用耐久/剩余次数物品存在重复风险；按效果列表+有限/无限次数+耗尽双键删除+真实主手消费者作为一条家族，writer/getter/两个键名均不另计。')


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
        row.update(status='helper_reviewed_pending_coordinator',credit=0,accepted=False,evidence=evidence,preservation=spec['observation'],application_limit=spec['limits'],url=primary['source_url_or_coordinate'],excerpt=primary['text'],source_local=primary['source'],source_sha256=primary['sourceSha256'],line=primary['start'],end_line=primary['end'],runtime_validation='not_run_exam_prohibition')
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-003.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_restriction':'No builds, tests, games, servers, GameTest, GUI, screen or lock interaction until explicit user restoration','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
