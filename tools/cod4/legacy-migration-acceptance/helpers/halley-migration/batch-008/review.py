"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-008'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))



add('corpsecomplex-retained-inventory-preparation-canceled-death-and-clone',[
 ('inventories/VanillaInventory.java','storeInventory'),('inventories/VanillaInventory.java','retrieveInventory'),
 ('InventoryModule.java','playerDeath'),('InventoryModule.java','canceledDeath'),('InventoryModule.java','playerRespawn'),
 ('InventoryHelper.java','process'),('InventoryHelper.java','getDropModeOverride'),('InventoryHelper.java','applyDurabilityLoss'),('InventoryHelper.java','getRandomAmount'),('InventoryHelper.java','saveSoulbound'),
 ('DeathStorageCapability.java','register'),('DeathStorageCapability.java','writeNBT'),('DeathStorageCapability.java','readNBT'),('DeathStorageCapability.java','getCapability'),('DeathStorageCapability.java','DeathStorage'),('DeathStorageCapability.java','getPlayer'),('DeathStorageCapability.java','buildSettings'),('DeathStorageCapability.java','getSettings'),('DeathStorageCapability.java','setDeathDamageSource'),('DeathStorageCapability.java','getDeathInfo'),('DeathStorageCapability.java','addInventory'),('DeathStorageCapability.java','getInventory'),('DeathStorageCapability.java','getDeathInventory'),('DeathStorageCapability.java','clearDeathInventory'),('DeathStorageCapability.java','addEffectInstance'),('DeathStorageCapability.java','getEffects'),('DeathStorageCapability.java','Provider'),('DeathStorageCapability.java','serializeNBT'),('DeathStorageCapability.java','deserializeNBT'),
 ('CommonEventHandler.java','attachCapability'),('CommonEventHandler.java','playerDeath'),('CommonEventHandler.java','playerClone'),
 ('CorpseComplex.java','CorpseComplex'),('CorpseComplex.java','setup'),('CorpseComplex.java','config'),('IntegrationManager.java','init'),
 ('DeathInfo.java','DeathInfo'),('DeathInfo.java','read'),('DeathInfo.java','write'),('DeathSettings.java','DeathSettings'),('DeathSettingManager.java','buildSettings'),('DeathOverrideManager.java','apply'),('DeathConditionManager.java','matches'),('DeathOverride.java','apply'),('InventorySetting.java','importConfig'),('InventorySetting.java','applyOverride'),('ItemOverrideManager.java','getOverride'),('ConfigParser.java','parseDrops')],
 '服务端真实LivingDeath HIGH在keepInventory关闭时准备保留物品，取消事件LOWEST返还同实体，真实死亡Clone LOW向新实体返还；Provider实际序列化死亡库存。',
 '原玩家41槽ItemStack，按主副手/热键/主包/四件装备策略、物品override与Soulbound决定保留；DeathStorage.Inventories.vanilla保存含Slot及完整ItemStack的compound列表，另有死亡来源/维度条件。',
 'process先从原stack.split出保留份，写入Slot与ItemStack NBT；剩余份可继续受耐久与销毁策略影响。Clone按原槽返还，目标空槽直接设置，否则giveItemToPlayer；取消死亡返还后清空死亡库存map。常规Clone不显式清旧map，靠旧实体被移除结束生命周期。',
 '实际保存的是经过死亡策略筛出的物品子集，并非整个ForgeData。取消死亡不是完整回滚：拆出部分和剩余部分此前发生的耐久扣减、销毁数量、Soulbound等级消耗没有还原。KEEP override只把keepChance置1，DESTROY只把destroyChance置1，DROP只把keepChance置0，不能从枚举名称推断其他概率也被清零；Soulbound检查先于消失诅咒，成功保留时该顺序改变最终物品。HIGHEST先固定DeathInfo/buildSettings，HIGH准备库存，LOWEST处理取消；Clone HIGHEST复制DeathInfo引用，LOW才revive原实体并取cap，因此不能用LOW的revive推定更早回调旧cap一定有效。',
 'Dynasty旧任务物品恢复要保留Count/tag与身份，只对批准永久状态做明确子集迁移；准备、提交、取消需要独立定义，若宣称可回滚应先保留未经修改快照。迁移返还时明确原槽冲突处理、坏槽隔离与一次消费标记；不要依赖旧实体销毁间接保证重放安全。',
 '官方1.16.x的历史实现，不能直接套1.20 Forge能力生命周期。未读取原生revive/remove行为或运行事件顺序，不能宣称完整Clone验收。retrieve未显式检查Slot上下界，NBT读取强转且无逐项隔离；存储持有INBT引用，ImmutableMap仅复制容器，非深拷贝。readNBT不先清库存/effects，重复读会保留旧map键及追加effects；EffectInstance.read的null未经检查交给复制方法，死亡维度资源串也未做坏值隔离。可选Curios/CosmeticArmor/ToolBelt只证实按加载状态注册，未审其实现，均不列独立候选。配置override容器PriorityQueue.forEach不保证按优先级出队顺序。无跨版本旧ID转换证明；不移植死亡损失规则，不触碰原存档。',
 '同一vanilla保留库存生命周期的写入/Provider/事件/取消/Clone/耐久与附魔全部合一条；41槽、各种策略名、可选背包平台不多计。与Corpse/ToolBelt等库存持久化存在语义交叠，差异仅在准备时突变、取消非回滚与槽冲突边界，仍由Kepler判定能否独立计数；credit0。')

add('corpsecomplex-experience-three-field-remainder-and-death-clone',[
 ('experience/ExperienceModule.java','playerRespawn'),('experience/ExperienceModule.java','playerXpDrop'),('experience/ExperienceModule.java','getExperiencePoints'),('experience/ExperienceModule.java','getExperiencePointsFromLevel'),('experience/ExperienceModule.java','getDroppedExperiencePoints'),
 ('ExperienceSetting.java','importConfig'),('ExperienceSetting.java','applyOverride'),('ExperienceSetting.java','getLostXp'),('ExperienceSetting.java','getXpDropMode'),('ExperienceSetting.java','getDroppedXpPerLevel'),('ExperienceSetting.java','getDroppedXpPercent'),('ExperienceSetting.java','getMaxDroppedXp'),
 ('CommonEventHandler.java','attachCapability'),('CommonEventHandler.java','playerDeath'),('CommonEventHandler.java','playerClone'),('DeathStorageCapability.java','getCapability'),('DeathStorageCapability.java','getSettings'),('DeathStorageCapability.java','buildSettings'),('DeathStorageCapability.java','setDeathDamageSource'),('DeathStorageCapability.java','getDeathInfo'),
 ('DeathSettingManager.java','buildSettings'),('DeathSettings.java','DeathSettings'),('DeathOverrideManager.java','apply'),('DeathConditionManager.java','matches'),('DeathOverride.java','apply'),('DeathInfo.java','DeathInfo'),('CorpseComplex.java','CorpseComplex'),('CorpseComplex.java','setup')],
 'LivingExperienceDropEvent先改原实体经验，死亡Clone按新实体死亡设置复制旧玩家剩余经验；实际模块在Mod构造时注册Forge事件总线。',
 '原玩家experience进度条、experienceLevel等级、experienceTotal累计值，以及死亡条件决定的lostXp/dropMode/dropPercent/dropPerLevel/maxDroppedXp。',
 'loss<=0直接取消经验掉落实体事件，不改旧经验；loss>0按等级分段公式加当前条四舍五入算总点，lostPoints截断，先将三字段归零再giveExperiencePoints(keptXp)，由重算后的等级差或损失点比例决定掉落且上限截断。死亡Clone仅在新settings.lostXp<1时复制旧玩家全部三项经验字段；非死亡不复制。',
 '保留状态先写回旧玩家，再让Clone消费该剩余状态，不能只看Clone三行就推断它保留原始经验；等级、进度和累计值是耦合表示，独拷一个字段可能不一致。lostXp为零时取消掉落和Clone保留是两个配合分支；lostXp为一时完全不走复制。DeathInfo是Clone传递的共享上下文，而settings由新玩家能力按需重建，理论上不是旧settings对象整体拷贝。所见官方入口无Corail Tombstone专用禁用判断，不沿用未经证实的集成假设。',
 '对Dynasty已审定永久进度，先辨识同一状态的多种表示以及Clone前是否已被其他事件修改，再复制完整且最小的耦合字段；事件取消与后续Clone各自职责要明确。这里经验/死亡损失仅作为边界研究，不能据此新增死亡惩罚或复制整个能力。',
 '历史1.16.x经验公式及映射不是当前版本验收；LivingExperienceDrop事件外部取消、keepInventory及原版Clone与其他mod先后未运行验证。分段公式大等级整数溢出/浮点截断及非法override范围没有额外防御；不声称数值任意范围精确。Clone源经验是否由另一个处理器后续重写仍未知。该链不等于磁盘旧ID迁移；只提供真实死亡Clone耦合状态边界，源文件完整哈希固定，无游戏或测试执行。',
 '所有经验公式、掉落模式、设置getter和Clone仅一条状态链，不按三字段或模式多计；与此前Diet/SoL玩家Clone保留有共享架构，区别是原生经验耦合表示及先改源再复制，最终由Kepler去重，credit0。')
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
    (DOC/'batch-008.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
