"""Mekanism independent native refusal/resource/lifecycle implementations."""
from ledger import B,O,record,verify
import json
r='mekanism/Mekanism';p='src/main/java/mekanism/';d='src/datagen/main/java/mekanism/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,refs,chain,obs,lesson):
 if k not in {x['id'] for x in json.loads((O/'reviewed.json').read_text())}: record(k,r,[(p+'common/Mekanism.java',356,361)]+refs,chain,obs,lesson,'固定d4df9b354c209c85713bdc8a017bfe54aa044e40，本地Git blob/tree+SHA256；全文关键native方法/调用观察，datagen是源码启用定义非已运行产物。该源API/版本不同于本项目，不能直接复制。无游戏/正式源/资产/清单变更，通用transaction/codec/同链包装0额外。','native_refusal_resource_accounting_and_effect_lifecycle')
 keys.append(k)
add('mekanism-native-scuba-oxygen-presence-preventable-magic-denial',[(p+'common/CommonPlayerTickHandler.java',201,254),w(p+'common/item/gear/ItemScubaTank.java'),w(p+'common/item/interfaces/IChemicalItem.java'),(p+'common/item/interfaces/IModeItem.java',81,98),(p+'common/util/ChemicalUtils.java',37,52),(d+'common/tag/MekanismTagProvider.java',657,738),(p+'common/registries/MekanismItems.java',253,254)],
 '真实CommonPlayerTickHandler已注册→原生Incoming拒负/零damage和dead→IS_PREVENTABLE_MAGIC tag(MAGIC/INDIRECT_MAGIC)→真HEAD ScubaMask+CHEST ScubaTank、mode和OXYGEN存在→cancel并return。Mode初值false，ChemicalItem原生查capability slot resource type。',
 '以最终装备组合/储氧门1，MAGIC/INDIRECT、模式/chemical查询wrapper不重复。这里只查询氧存在，不在该拒伤分支抽氧，不可称按每次伤害扣氧；呼吸tick消耗是另玩法。source其他类型不拒，本门在MekaSuit reduction注册之前return，所以不能累计二者收益。没有明确拒绝原因S2C/灰字，也不能据所有Incoming canceled推Boss免疫。',
 '拒控语义应由最终拒绝分支生产，精确到Boss与控制类型；资源存在和已付费不能混用。')
add('mekanism-native-modular-armor-transaction-absorption-sideeffect-settlement',[(p+'common/CommonPlayerTickHandler.java',201,254),(p+'common/item/gear/ItemMekaSuitArmor.java',338,455),w(p+'common/content/gear/mekasuit/ModuleInhalationPurificationUnit.java'),(p+'common/registries/MekanismModules.java',128,133),(d+'common/tag/MekanismTagProvider.java',375,390),(d+'common/tag/MekanismTagProvider.java',657,738)],
 '原生Incoming仅装备MODULE_CONTAINERS_ARMOR时添加一次ARMOR reduction callback→伤害扣原armor reduction后剩余toReduce→扫描真装备energy capability和enabled module自定义吸收→不足再按gear/source数据图/配置/slot份额吸收→transaction commit→ratio>=1关闭副作用并返回全部newDamage，否则局部扣减。',
 '最终能量吸收结算一家族1，module/source/slot/数据图/底层抽能包装不增数。amount<=0早退，nativeIncoming还拦dead，避免无伤扣能；module自定义吸收在通用technical/BYPASSES_ARMOR门之前，所以不能称所有technical皆免不了。吸收ratio按剩余cap，ceil能耗及实际extract比例，0cost可全额；只对完全ratio标记no sideEffects，非所有hurt=false。reduction只是native修改回调，尚未验证其他mod后续覆盖或最终HP，也无反馈包。外部transaction实现辅助0，不声称回滚所有实体状态。',
 '完整拒控、部分减免应分明；不要以护甲减伤或取消副作用冒充Boss灰字生产。')
add('mekanism-native-fall-energy-extraction-and-full-block-step-sound',[(p+'common/CommonPlayerTickHandler.java',257,307),(p+'common/CommonPlayerTickHandler.java',339,359),(p+'common/item/interfaces/IFreeRunnerItem.java',38,77),(p+'common/item/interfaces/IFreeRunnerItem.java',108,141),(d+'common/tag/MekanismTagProvider.java',375,390)],
 '原生LivingFall按SAFE_FALL_DISTANCE/FALL_DAMAGE_MULTIPLIER算ceil伤害→MekaSuit靴tag或active FreeRunner cap且primary mode允许→实际事务抽能→full remaining<=epsilon取消并目标step sound；partial把剩余伤害换回距离交原生结算。',
 '独立LivingFall前置资源结算1，FreeRunner/MekaSuit boot同算法不拆2。getActiveFreeRunners取首个有能量pair，但getPrimaryFreeRunners另取首个pair模式；两者未必同一item，不能声称每次按被抽能pair的模式验证。0cost无抽能直接吸收；partial无full step cue。音是落地步声不是受击免疫嗡声，未验听感。事件无server-only显式门，不擅自认所有side均一致。事务commit不证明原生fall从此不受其他监听修改。',
 '按目标的明确拒绝声光要和普通落地/部分防护声区分，冷却状态不依赖画面是否生成。')
add('mekanism-native-radiation-specific-target-tag-invulnerability',[(p+'common/CommonPlayerTickHandler.java',191,199),(d+'common/tag/MekanismTagProvider.java',232,270),w(p+'common/lib/radiation/capability/RadiationEntity.java'),(p+'common/lib/radiation/PlayerExposure.java',26,70),(p+'common/capabilities/Capabilities.java',84,87)],
 '实际native EntityTick.Post(非玩家)→PlayerExposure updateEntityRadiation→真实RadiationEntity update按severity+随机产生RADIATION hurtServer→原生EntityInvulnerabilityCheck仅先前未immune、Living和该source时target MEK_RADIATION_IMMUNE；tag实际定义Robit及铁/雪傀儡。玩家另tick入口存在，主单位以非玩家native链为据。',
 '独立最终实体来源专属免疫1，所有tag成员同一门不拆。原isInvulnerable true保持，setInvulnerable false仅原未免时，不会解除别家免疫。RadiationEntity只有ServerPlayer分支hurt true才criterion，非玩家忽略bool；玩家即使本次hurt失败仍可能addExhaustion，伤害免疫不等于所有辐射后果都停。update不等于每tick必伤，severity/随机门保留。无拒伤灰字/控制回执，不给普通玩家增加要求。',
 '免疫范围精确到实际控制/来源，不能根据无伤就把资源、饥饿、音效副作用全判已取消。')
add('mekanism-native-purification-paid-effect-duration-advance-and-hidden-rollover',[(p+'common/item/gear/ItemMekaSuitArmor.java',207,224),(p+'common/content/gear/Module.java',114,124),w(p+'common/content/gear/mekasuit/ModuleInhalationPurificationUnit.java'),(p+'common/registries/MekanismModules.java',128,133),(p+'common/util/MekanismUtils.java',423,457)],
 '实际INHALATION_PURIFICATION_UNIT默认harmful true、其他false→装备server inventoryTick开root transaction→enabled Module.tick→purification检查能量可用并逐效果实际消费→受category和SPEED_UP_BLACKLIST门的active effect执行9次安全tickDownDuration→隐藏效果翻出时更新attributes/dirty、乘客与ServerPlayer原生effect包。',
 '以独立已接纳状态的缩短/隐藏层生命周期1，不当最终免疫；魔法damage吸收callback归上一家族0额外。只tickDownDuration避免重复触发毒伤，没有替代Living原生effect到期移除门；效果duration<=0安全helper无动作。每effect收费且预先模拟一份，没效果不正式抽能。tickClient以未commit子事务调用同逻辑仅回滚能量，不等于自动回滚对象duration；客户端实际装备tick入口未在此补齐，不宣称已运行双端。隐藏层S2C只在rollover路径，不称每9次缩短全量旁观同步。普通效果/类别换名不拆数。',
 'Boss控制拒绝与事后缩短状态严格区分；反馈生命周期、隐藏/续期代际及目标归属必须明确，静态不证明画面。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'mekanism-native-batch39','credited_chains':keys,'rationale':'潜水氧门拒魔法、护甲事务吸收最终结算、摔落前置结算、原生特定来源实体免疫、已接纳效果缩短/隐藏层生命期各1；module/装备/tag常量、底层transaction/codec0。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
