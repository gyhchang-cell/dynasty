"""Preserve concrete zero-credit observations without promoting lexical candidates."""
from ledger import B,O
import json,hashlib
rows=[]
def zero(key,repo,paths,observation,missing):
 root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());refs=[]
 for rel in paths:
  data=(root/rel).read_bytes();refs.append({'source_path':rel,'path':str((root/rel).relative_to(B.parents[2])),'file_sha256':hashlib.sha256(data).hexdigest(),'commit':meta['commit'],'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{rel}'})
 rows.append({'id':key,'research_credit':0,'repo':repo,'source_refs':refs,'actual_observation':observation,'reason_not_credited':missing})
r='stal111/Forbidden-Arcanus';p='neoforge/src/main/java/com/stal111/forbidden_arcanus/'
zero('fa-skull-wear-not-connected',r,[p+'common/item/ObsidianSkullItem.java',p+'common/block/skull/ObsidianSkullType.java'],
 'ObsidianSkullItem.inventoryTick只有TODO和被注释的旧调用；枚举DEFAULT会递减阶段并换头/播crack，AUREALIC会扣aureal，但本次实际入口不调用它们。',
 '不能把未串活的磨损/扣资源/声音链称原生功能或研究新实现。')
zero('fa-virtual-fire-resistance-consumer-pending',r,[p+'core/mixin/LivingEntityMixin.java',p+'common/item/component/EffectGrantingRule.java',p+'core/init/ModBlocks.java',p+'core/init/ModDataComponents.java','neoforge/src/main/resources/forbidden_arcanus.mixins.json'],
 '已读完整LivingEntityMixin/EffectGrantingRule：实际装备和collectEquipmentChanges使规则缓存失效；hasEffect原false且ServerLevel时按装备component规则返回virtual true；rule匹配effect holder及动态EntityPredicate。ModBlocks真实skull factory配置HEAD火抗，aurealic配置有aureal才满足。不同skull阶段不拆数。',
 '本次尚缺该固定Minecraft版本最终火伤消费者的完整源码核查，EssenceValueEntityPredicate已取但未完整串至当前存储消费；保持0。不能借库存tick注释声称磨损已生效，也不能称客户端vanilla状态图标已同步。')
zero('fa-death-lost-soul-not-immunity',r,[p+'common/event/DeathEvents.java',p+'common/event/EntityEvents.java',p+'ModEventHandler.java'],
 '完整事件文件已读：DeathEvents按死亡源武器及tag/概率生成lost soul；EntityEvents.Post提血/死亡时收Soulbound库存。',
 '没有最终拒控或拒伤，也非受击文字回执；物品/死亡战利品不计本项。')
r='Sweenus/SimplySwords';p='common/src/main/java/net/sweenus/simplyswords/'
zero('simply-wax-target-selection-support-only',r,[p+'world/WaxweaverEncasementManager.java',p+'util/HelperMethods.java',p+'mixin/client/WaxEncasedLivingEntityRendererMixin.java'],
 '完整canStart/start/isEligibleTarget/applyPrison/isEncased/isVisuallySealed及HelperMethods.checkFriendlyFire/checkAbilityTarget已读。资格检查尺寸/同world/距离/友伤/已encased，addStatusEffect后仍停止用物/归零速度/teleport锚点；原生renderer根据真实effect amplifier>0隐藏本体。',
 '目标筛选不是Boss专属拒控reason，也无拒绝灰字。复杂tick/release/生产链未全部完成，本批只作支持材料0，不扩成新Boss规则。')
r='Lothrazar/Cyclic';p='src/main/java/com/lothrazar/cyclic/'
zero('cyclic-beekeeper-source-filter-and-target-clearing-support',r,[p+'enchant/BeekeeperEnchant.java'],
 '全文已读：LOWEST LivingDamage.Pre按护甲附魔level及直接源Bee/Bat/LlamaSpit/Phantom设damage0；NewTarget为Player且Bee时取消并清anger/aggro。',
 '直接源常量filter与既有来源筛选家族合并0；清仇恨不自动等于Boss拒控/灰字，且本次未核实际附魔注册启用，不晋级。')
zero('cyclic-pearl-use-not-refusal',r,[p+'enchant/EnderPearlEnchant.java'],
 '全文已读：有附魔/无CD的服务端rightclick发射原版pearl、设置CD、播放throw声、取消原物品交互。',
 '这里取消的是普通物品交互，不是拒伤/拒控；不能因setCanceled词法命中计研究。')
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
zero('goety-hand-soul-totem-merged-existing-family',r,[p+'common/events/SoulEnergyEvents.java'],
 '完整onLivingDeathEvent与revive已读：持物满魂时1HP/清效果/加保护/消耗魂量，Player专包或非玩家原版byte35；主手if/副手else-if。',
 '普通满资源图腾复活并已有Ars/TF类资源拒死家族0；主副手、Player/Mob、三种buff或两种回放wrapper均不拆分。Arca世界锚点独立资格政策只在有效账另计一次。')
(O/'uncredited-observations-20261027b.json').write_text(json.dumps({'status':'supporting_or_pending_only','effective_added':0,'observations':rows,'note':'Whole listed files are provenance containers; only explicitly named methods/registrations were manually observed. No auto-promotion, no complete-file reading claim for large containers.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'zero_credit_observations':len(rows),'effective_added':0}))
