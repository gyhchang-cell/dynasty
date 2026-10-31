"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-005'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))


# Handwritten chain specifications follow; supporting methods never add credit.
add('coldsweat-temperature-legacy-modifier-and-death-attribute-whitelist',[
 ('temperature/AbstractTempCap.java','deserializeModifiers'),
 ('temperature/AbstractTempCap.java','serializeNBT'),('temperature/AbstractTempCap.java','serializeTraits'),('temperature/AbstractTempCap.java','serializeModifiers'),('temperature/AbstractTempCap.java','deserializeNBT'),('temperature/AbstractTempCap.java','deserializeTraits'),('temperature/AbstractTempCap.java','copy'),
 ('temperature/AbstractTempCap.java','markPersistentAttribute'),('temperature/AbstractTempCap.java','clearPersistentAttribute'),('temperature/AbstractTempCap.java','getPersistentAttributes'),('temperature/AbstractTempCap.java','clearModifiers'),('temperature/AbstractTempCap.java','setModifiers'),('temperature/AbstractTempCap.java','getTrait'),('temperature/AbstractTempCap.java','setTrait'),('temperature/AbstractTempCap.java','tick'),('temperature/AbstractTempCap.java','modifyFromAttribute'),
 ('handler/EntityTempManager.java','attachCapabilityToEntityHandler'),('handler/EntityTempManager.java','handleModUpdates'),('handler/EntityTempManager.java','keepPersistentAttributes'),('handler/EntityTempManager.java','handlePlayerReset'),('handler/EntityTempManager.java','initModifiersOnEntity'),('handler/EntityTempManager.java','gatherTempModifiers'),('handler/EntityTempManager.java','defineDefaultModifiers'),('handler/EntityTempManager.java','tickTemperature'),('handler/EntityTempManager.java','getAllTemperatureAttributes'),('handler/EntityTempManager.java','getAttribute'),('handler/EntityTempManager.java','getAttributeOverride'),('handler/EntityTempManager.java','makeAttributeModifier'),
 ('core/init/DefaultTempModifiersEvent.java','DefaultTempModifiersEvent'),('core/init/DefaultTempModifiersEvent.java','getModifiers'),('core/init/DefaultTempModifiersEvent.java','addModifier'),('core/init/DefaultTempModifiersEvent.java','addModifierById'),
 ('api/util/Temperature.java','getModifiers'),('api/util/Temperature.java','addModifier'),
 ('serialization/NBTHelper.java','tagToModifier'),('serialization/NBTHelper.java','modifierToTag'),('serialization/NBTHelper.java','getTraitTagKey'),
 ('registry/TempModifierRegistry.java','getValue'),('registry/TempModifierRegistry.java','get'),
 ('modifier/TempModifier.java','setNBT'),('modifier/TempModifier.java','setTicksExisted'),('modifier/TempModifier.java','getNBT'),('modifier/TempModifier.java','expires'),('modifier/TempModifier.java','tickRate'),('modifier/TempModifier.java','getExpireTime'),('modifier/TempModifier.java','getTicksExisted'),
 ('config/ModUpdater.java','updateEntity'),('impl/TempCommand.java','executeModifyEntityTemp')],
 '温度 capability 从玩家实体持久化恢复；入世界补默认修饰器；命令设置永久属性白名单；死亡及非死亡 PlayerEvent.Clone 分流。',
 'Traits 双精度值；TempModifiers 每 trait 列表支持旧 Id/ModifierData/ExpireTicks/TickRate/TicksExisted/Hash 与新 type/nbt/expire_time/tick_rate/ticks_existed/hash；PersistentAttributes 为属性注册 ID 列表。',
 '旧修饰器通过注册 supplier 重建，新修饰器用 CODEC；未知正常格式 ID 返回空时跳过。非零 hash 在全部 trait 间复用同一个 modifier 实例；死亡只复制白名单属性的 baseValue，非死亡复制全部 traits/modifier 引用/白名单。',
 '这是同一温度能力生命周期，不能把旧读器、每 trait、每属性、Clone 两监听器再拆计。默认事件构造器先 new HashMap(Temperature.getModifiers(entity))，保留现有列表引用；gather 后 clear 的是原 map，setModifiers 回填，因此不能由 clearModifiers 一行断言读盘临时效果全丢。默认项 SAME_CLASS 去重，气候高级配置变化时则主动清旧 map。命令 permanent 分支 markPersistentAttribute，非 permanent 清白名单；Clone 死亡对未白名单属性恢复默认，复制的仅 baseValue，并非所有 permanent AttributeModifier。updateEntity 把 NaN base 值重置默认并写版本号，不实施旧任务键迁移。',
 '借鉴 Dynasty 的按字段永久白名单与非死亡/死亡区分；在读器、入世界重建、命令 writer、Clone、实际温度 tick 各边界一起核查。旧别名解析应定义旧新字段共存优先级、未知注册 ID 保留策略；不能整份复制临时修饰器为永久进度。',
 '旧 Id 出现即优先旧分支，语法非法 ResourceLocation 可能抛出；hash 只按整数复用，无 payload/类型比较，碰撞会合并不同修饰器。旧 tickRate setter 最小1，新 CODEC 直接赋值可绕过；tick 中取模有零值风险。反序列化 PersistentAttributes 未先 clear，未知注册 ID 可加 null，后续写注册键有失败风险。非死亡 copy 是浅引用；两 Clone 监听器同默认优先级，未证明外部排序或异常时 invalidateCaps 一定执行。温度临时效果有正常 expiry，不保证死亡保留。静态字段 codec 另列 source_declarations；未验证所有 modifier 子类、所有第三方事件或运行效果。',
 '与 batch003 ScalingHealth、此前 capability Clone 家族有架构重复风险；具体建议差异在动态注册属性白名单、死亡重置默认及旧 modifier 身份图兼容读器。作为一条待主责判定，support、CODEC 字段和 API accessor 全部 credit0。')

add('coldsweat-inplace-legacy-item-key-alias-real-consumers',[
 ('serialization/NBTHelper.java','updateItemTags'),('serialization/NBTHelper.java','convertTagsInContainer'),('serialization/NBTHelper.java','getTagOrEmpty'),
 ('item/SoulspringLampItem.java','inventoryTick'),('item/SoulspringLampItem.java','setFuel'),('item/SoulspringLampItem.java','getFuel'),('item/SoulspringLampItem.java','addFuel'),('item/SoulspringLampItem.java','getFuelForStack'),('item/SoulspringLampItem.java','isLit'),('item/SoulspringLampItem.java','setLit'),
 ('item/FilledWaterskinItem.java','inventoryTick'),('item/FilledWaterskinItem.java','finishUsingItem'),('item/FilledWaterskinItem.java','consumeWaterskin'),('item/FilledWaterskinItem.java','getCraftingRemainingItem'),
 ('modifier/WaterskinTempModifier.java','WaterskinTempModifier'),('modifier/WaterskinTempModifier.java','calculate'),('modifier/SoulLampTempModifier.java','calculate')],
 'PlayerContainerEvent.Open 遍历该容器实际 ItemStack 列表，将旧键就地升级；灯物品 tick 和饮用水袋实际消费新键。',
 '仅 Soulspring Lamp 的 fuel 与 Filled Waterskin 的 temperature 小写旧键；对应新键 Fuel、Temperature，原栈其他 tag/Count/id。',
 'getDouble 读取旧值，putDouble 写新键，再 remove 旧键；两种物品为一个循环内的 if/else-if，不替换整个 ItemStack。',
 '旧键存在时无论新键是否已存在，都由旧值覆盖新值；未做旧 tag 类型检查，错类型 getDouble 缺省0可能覆盖有效新值。旧键删除后再次执行不再迁移，属于正常成功路径幂等。灯在服务端每5 tick 按 Fuel/气温/维度消耗并给附近实体温度修饰器；水袋饮用读 Temperature，创建100tick CORE 修饰器，并按耐久返还空水袋。空袋结果复制其他 tag 后删除 Temperature/Damage/Purity，不保留已消费温度。',
 '适用于 Dynasty 旧任务物品字段的最小就地转换：先限定真实物品身份与旧字段类型，明确旧新共存策略，保留无关 NBT 和栈数，再验证消费者使用新键。不能把这种键改名当作缺注册旧物品 ID 的 remap 替代。',
 '触发仅容器打开，未证明未开容器、离线玩家或嵌套容器均覆盖；无迁移版本、错误快照备份或事务。getTagOrEmpty 无 tag 时返回未挂载新 compound，但旧键也不可能来自该空 compound，不能据此说正常旧键转换必丢。未逐层审查 FuelData 配置谓词及 Minecraft 物品消耗内部。未运行游戏测试。',
 'fuel 与 temperature 仅物品/键名不同，合并一条；灯 setter、饮用、modifier 计算是同链消费者证据不另计。与主账其他简单旧新键搬运可能同族，Kepler 需做语义去重；本辅助不授予 credit。')

add('coldsweat-sewn-insulation-materials-owned-state-codec-and-consumption',[
 ('insulation/ItemInsulationCap.java','deserializeNBT'),('insulation/ItemInsulationCap.java','serializeNBT'),('insulation/ItemInsulationCap.java','copy'),('insulation/ItemInsulationCap.java','addInsulationItem'),('insulation/ItemInsulationCap.java','removeInsulationItem'),('insulation/ItemInsulationCap.java','canAddInsulationItem'),('insulation/ItemInsulationCap.java','calcAdaptiveInsulation'),
 ('handler/ItemInsulationManager.java','attachCapabilityToItemHandler'),('handler/ItemInsulationManager.java','slotChanged'),('handler/ItemInsulationManager.java','getAppliedArmorInsulators'),('handler/ItemInsulationManager.java','isInsulatable'),('handler/ItemInsulationManager.java','getInsulationSlots'),('handler/ItemInsulationManager.java','getSlotsFilled'),('handler/ItemInsulationManager.java','getInsulatorInsulation'),
 ('container/SewingContainer.java','onTake'),('container/SewingContainer.java','createResult'),('container/SewingContainer.java','insulateArmorItem'),
 ('event/ProcessEquipmentInsulation.java','applyArmorInsulation'),('event/ProcessEquipmentInsulation.java','applySewnArmorInsulation'),('event/ProcessEquipmentInsulation.java','applyBuiltinArmorInsulation'),('event/ProcessEquipmentInsulation.java','popExtraInsulation'),('event/ProcessEquipmentInsulation.java','onArmorBroken'),
 ('configuration/InsulatorData.java','copy'),('configuration/InsulatorData.java','test'),
 ('api/insulation/Insulation.java','getCodec'),('api/insulation/AdaptiveInsulation.java','calculateChange'),('api/insulation/AdaptiveInsulation.java','getFactorFromArmor'),('api/insulation/AdaptiveInsulation.java','setFactorToArmor'),('api/insulation/AdaptiveInsulation.java','readFactorFromArmor'),('api/insulation/AdaptiveInsulation.java','getCold'),('api/insulation/AdaptiveInsulation.java','getHeat'),('api/insulation/AdaptiveInsulation.java','copy')],
 '可保温护甲挂 item_insulation capability；缝纫将真实材料栈与保温配置快照写入能力，服务端装备 tick 消费，容量缩小时退还多余材料。',
 'insulation 列表包含 item ItemStack codec 与 insulation InsulatorData 列表；嵌套 static cold/heat 或 adaptive value/adapt_speed/factor。',
 'decode 成功才替换当前 list；失败不改现有 list。序列化按 changed 缓存 compound。缝纫复制护甲后修改副本能力，存 count1 的材料副本；实际热计算读取存入能力的材料配置并更新 adaptive factor。',
 '这里持久 owner 是护甲材料及适应进度，不是展示 tooltip。applySewnArmorInsulation 根据当前实体条件筛选保存数据，求冷热贡献，调用 calcAdaptiveInsulation；超容量从末尾移除材料并掉落，护甲损坏也返还。缓存 writer 返回同一个 compound 引用；copy 仅 clear/addAll 共享 Pair/列表且不设 changed，重用已有缓存对象时有旧缓存风险。slotChanged 删除旧 Insulation 键后 merge 新 codec tag 作同步；不能把删除该键声称已读取旧格式迁移。createResult 修改 processed 副本后，又将原 wearableItem 的能力序列化到结果根 tag；实际 Forge capability 与展示同步根可能不一致。',
 '借鉴旧物品升级时保留原材料、嵌套状态和消费端一致性核查；永久字段迁移应区分真实 owner 能力与客户端同步副本。codec 失败应明确保留原快照还是重置，不用空编码结果覆盖唯一数据。容量配置变更要有可核验返还策略。',
 'encode 失败 fallback 空 compound，不能声称失败安全 roundtrip；decode fail 在新实例仍为空。InsulatorData 深复制 insulation 但共享若干 requirements/attrs，对所有子 codec 的未知字段行为未完成穷尽审查。Adaptive armor factor setter 用 getTagOrEmpty，若原护甲无 tag 则写入临时 compound 未挂载；readFactor 仅非零覆盖，零/缺失不能区分。未跟踪 WorldHelper/Minecraft 掉落内部，不保证原子返还或崩溃一次性。',
 'cap reader/writer、静态/自适应 codec、缝纫、每 tick、超容量退料合并一条；与 PassiveSkillTree 物品嵌套 bonus 有结构风险，但保存真实材料和可返还所有权不同。具体主账去重归 Kepler；所有支持方法 credit0。')

add('champions-affix-owned-persistence-conversion-and-damage-memory',[
 ('capability/ChampionCapability.java','deserializeNBT'),('capability/ChampionCapability.java','serializeNBT'),('capability/ChampionCapability.java','setData'),('capability/ChampionCapability.java','getData'),('capability/ChampionCapability.java','getCapability'),('capability/ChampionCapability.java','createProvider'),('capability/ChampionCapability.java','Provider'),
 ('capability/CapabilityEventHandler.java','attachCapabilities'),('capability/CapabilityEventHandler.java','onLivingConvert'),('capability/CapabilityEventHandler.java','onSpecialSpawn'),
 ('common/ChampionEventsHandler.java','onLivingJoinWorld'),('common/ChampionEventsHandler.java','onLivingUpdate'),('common/ChampionEventsHandler.java','onLivingHurt'),
 ('util/ChampionBuilder.java','spawn'),('util/ChampionBuilder.java','copy'),('util/ChampionBuilder.java','createAffixes'),('util/ChampionBuilder.java','createRank'),('util/ChampionBuilder.java','applyGrowth'),('util/ChampionBuilder.java','grow'),
 ('util/ChampionData.java','read'),('util/ChampionData.java','createAffixes'),('util/ChampionData.java','createRank'),
 ('affix/core/AffixData.java','readData'),('affix/core/AffixData.java','saveData'),('affix/core/AffixData.java','getData'),
 ('affix/AdaptableAffix.java','onHurt'),('affix/AdaptableAffix.java','readFromNBT'),('affix/AdaptableAffix.java','writeToNBT'),
 ('util/ChampionHelper.java','isValidChampion'),('rank/RankManager.java','getRank'),('rank/RankManager.java','getLowestRank'),('api/IAffix.java','onSpawn'),('api/IAffix.java','onInitialSpawn'),('impl/ChampionsApiImpl.java','getAffix')],
 '敌对活体的 Champion capability 读写 rank/词缀及其私有数据；入世界有 rank 则不重新 spawn；LivingConversion.Post 转交等级/词缀但重跑初始逻辑；伤害事件消费适应性伤害记忆。',
 'tier 整数，affixes compound 列表含 identifier 字符串和 data compound。另支持根 persistentData.ChampionsData 的 tier 整数或 min/max compound、affixes 字符串列表或 count/values compound 预设。',
 '未知 tier 退最低配置（空配置退 EMPTY_RANK）；未知词缀跳过。常规加载 rank 存在时保留选择的词缀。转换 copy rank 和 affix 列表、重设成长、onInitialSpawn；未复制旧 server.data。',
 'writer 对每词缀 put(DATA_TAG, compound)，reader 却用 tag.hasUUID(DATA_TAG) 才调用 getCompound，因此按已见正常 writer 格式，词缀私有 compound 数据不满足该 UUID guard，未恢复。AdaptableAffix 的 name/count 真正改变连续同类伤害减免：onHurt 读私有数据、增计数后 saveData，结果下限按 max reduction；所以不是普通展示字段。数据从能力读回失败时默认空 name/count0，rank/词缀仍可存在，入世界只调用 onSpawn，不因私有数据空而重做整个实体 spawn。转换同样不交付私有伤害记忆。',
 'Dynasty 迁移必须核对 reader 的 NBT 类型条件与 writer 一致，不能只看到相同键名就断言进度保留；实体转换/玩家 Clone 要分别列明永久选择和临时战斗记忆，避免整份复制。根预设只在能力缺 rank 的 spawn 分支消费，不能当每次读盘迁移器。',
 '固定1.18.x源码仅静态证据，不代表1.20.1可直接移植；hasUUID 为调用点类型检查观察，未执行Minecraft runtime验证。旧能力重复 deserialize 时无 tier/affixes 的分支不清旧对象、data map亦未清；不保证重复读取一致。getData反射可能返回null后调用者未防护。ChampionData 根键未删除，不是一次性旧键迁移；未知词缀遗失且未来保存不保留原快照。未审查所有 affix 初始化，仅 Adaptable damage memory 做消费证明；其余词缀状态不宣称全兼容。',
 '与 ScalingHealth mob difficult/blight 生命周期有高层相似，但此条具体在词缀私有 compound 类型 guard、固定词缀读盘与转换初始化边界；一条完整 owner 链建议。rank/getter、预设格式分支、damageData、网络同步和其他数十 affix 皆不另计。')

def declaration_evidence():
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    wanted={
      'api/temperature/modifier/TempModifier.java':{44},
      'common/capability/insulation/ItemInsulationCap.java':{26,31},
      'data/codec/configuration/InsulatorData.java':{70,75},
      'api/insulation/AdaptiveInsulation.java':{15},
      'api/insulation/StaticInsulation.java':{15},
    }
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
                    start=n.start_point.row+1,end=n.end_point.row+1,name='CODEC declaration',node_type=n.type,
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
        row['source_declarations']=[d for d in declaration_evidence() if
            (spec['family']=='coldsweat-temperature-legacy-modifier-and-death-attribute-whitelist' and d['path'].endswith('/TempModifier.java')) or
            (spec['family']=='coldsweat-sewn-insulation-materials-owned-state-codec-and-consumption' and not d['path'].endswith('/TempModifier.java'))]
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-005.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
