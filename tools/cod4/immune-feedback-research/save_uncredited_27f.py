"""Preserve actual zero-credit reads and unresolved provenance; never candidate promotion."""
from ledger import B,R,O
from pathlib import Path
import json,hashlib
rows=[]
def save(key,repo,rels,observation,reason,granularity):
 root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());refs=[]
 for rel in rels:
  path=root/rel;refs.append({'path':str(path.relative_to(R)),'source_path':rel,'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{rel}'})
 rows.append({'id':key,'repo':repo,'commit':meta['commit'],'research_credit':0,'observation':observation,'exclusion_or_pending_reason':reason,'read_granularity':granularity,'refs':refs})
p='src/main/java/com/github/alexthe668/domesticationinnovation/'
save('di-blazing-mismatched-native-loot-key-pending','AlexModGuy/DomesticationInnovation',[p+'server/CommonProxy.java',p+'server/enchantment/DIEnchantmentRegistry.java',p+'server/enchantment/PetEnchantmentLootOnly.java',p+'server/misc/DILootModifier.java','src/main/resources/data/forge/loot_modifiers/global_loot_modifiers.json','src/main/resources/data/domesticationinnovation/loot_modifiers/blazed_enchanted_book.json'],
 'CommonProxy实际hit分支有限blazing bars拒伤/反击/置600冷却；LivingTick缺bars再生200。注册loot-only、不可trade/discover；global列blazing_enchanted_book，但固定tree实际文件blazed_enchanted_book，内容loot_type6/nether_bridge；读完整loot modifier默认.2。',
 '原生资源名称不对应，普通获取链未闭合；不将有限盾计数或新宠物名称当独立新增。未请求不存在的blazing路径、不改游戏资源、不推测已实机失败。','CommonProxy关键完整onLivingHurt/onLivingUpdate；上述enchant/config/modifier及两个JSON全文，固定tree仅路径核对。')
save('di-siphon-merge-existing-owner-distance-redirect','AlexModGuy/DomesticationInnovation',[p+'server/CommonProxy.java',p+'server/misc/DIDamageTypes.java'],
 'tamed非SIPHON、此前flag=false，owner alive距离平方<100时owner.hurt结果未检查就cancel原攻击并pet.hurt(SIPHON,0)；零伤marker绕过同层tamed保护分支。',
 '并入既有Enigmatic按距离转给owner、在owner受伤结果前取消原伤害家族0；不因距离阈值/附魔名/零伤marker单独计数。','CommonProxy完整onLivingHurt已读；DIDamageTypes仅原生SIPHON定义支持，非宣称整类额外研究。')
p='src/main/java/com/Polarice3/Goety/'
save('goety-mirror-and-survey-helper-entities-not-combat-rejection-producers','Polarice3/Goety-2',[p+'common/entities/util/MirrorSpirit.java',p+'common/entities/util/SurveyEye.java'],
 'MirrorSpirit hurt仅返回BYPASSES_INVULNERABILITY bool，不调用parent结算HP；无推挤且状态全拒。SurveyEye hurt=false、owner UUID server/current client查找及camera缺失销毁。',
 '缺具体native生产链；后者为观察相机实体。不能将普通辅助实体hurt=false推作Boss免控回执。','两类全文已读，具体生成玩法/网络/像素未验。')
save('goety-mob-hurt-selected-methods-not-independent-new-family','Polarice3/Goety-2',[p+'common/entities/hostile/ender/Endersent.java',p+'common/entities/hostile/cultists/Crone.java',p+'common/entities/ally/BlackBeast.java',p+'common/entities/hostile/illagers/Trampler.java'],
 'Endersent hurt517–543在parent前更新recentHitTime并半远程伤，缺最终consumer；Crone hurt502–530低血拒cactus/berry/WITCH_RESISTANT、反刺和hitTimes；BlackBeast选定hurt/状态准入为source常量拒伤/部分减伤、父伤前移隐身；Trampler hurt407–416排controllingPassenger身份。',
 '缺完整独立链或并既有source枚举/乘客身份家族0；不是每个新mob+1。Crone已计Transpose与此hurt候选无关，不重复信用。','只读所述完整hurt/canBeAffected方法，非上述实体全文；Crone另有完整原生AI投瓶链见batch112。')
p='src/main/java/com/bobmowzie/mowziesmobs/'
save('mowzie-sculptor-elokosa-selected-policies-pending-consumer','BobMowzie/MowziesMobs-Public',[p+'server/entity/sculptor/EntitySculptor.java',p+'server/entity/elokosa/EntityElokosa.java'],
 'Sculptor hurt488–494先延heal再按PASS_TEST/DISAPPEAR拒绝；Elokosa hurt439–444 fall源拒绝且damageThreat写于parent前，knockback602–605特定阶段禁推。',
 '未补实际能力生产与威胁消费者，不从方法存在升有效，不按动画阶段/源常量换壳补数。','只读完整hurt/knockback相关方法，非整类全文。')
save('goety-web-and-launch-support-not-new-immune-receipts','Polarice3/Goety-2',[ 'src/main/java/com/Polarice3/Goety/common/effects/brew/WebbedBrewEffect.java','src/main/java/com/Polarice3/Goety/common/effects/brew/LaunchBrewEffect.java'],
 'Webbed直接setBlockAndUpdate脚下COBWEB后球体随机铺网；Launch先world packet+playSound再MobUtil.push，未在此检查Boss或接纳结果。',
 '已有直接控制/施法声不能证明接纳家族支持0；原生获取/核心push链未按这两条另补，不增加灰字要求。','两brew类全文已读；外部MobUtil.push未在本批完整追链。')
save('relics-mounted-resistance-and-gaze-reduction-pending-no-refusal-inference','Octo-Studios/relics',[ 'src/main/java/it/hurts/sskirillss/relics/items/relics/RiderFluteItem.java','src/main/java/it/hurts/sskirillss/relics/items/relics/back/GhostlyMantleItem.java'],
 'RiderFlute CommonEvents完整resistance/onLivingDamage：双向骑乘身份+stable UUID槽、rank启用，夹[0,1]后减伤并以blocked记经验。GhostlyMantle完整onLivingDamageModifiers：reprisal map按被打目标UUID消费；gaze按attacker UUID charges减伤夹0；onLivingDamage完整额外伤分支。',
 '部分减伤/乘法可能为0不直接等于Boss拒控；缺全量启用/状态积累链，不晋级。既有Ghostly救命免伤不重复计。','上述完整方法已读，物品千行类未全文；死亡逃逸方法只追加读局部，不宣称新完整研究。')
save('werewolves-movement-conditioned-random-denial-pending-activation','TeamLapen/Werewolves',['src/main/java/de/teamlapen/werewolves/entities/player/ModPlayerEventHandler.java'],
 '完整onEntityIncomingDamage：毛皮tag+transformed/WOLF_PAWN取消；SURVIVALIST移速平方>.01且ARROW_AWARENESS、ARROW且.4取消，否则sprint+attacker+MOVEMENT_TACTICS按config/refinement概率取消，无拒绝字。onMountEvent按非humanlike拒挂载并translatable动作栏。',
 '缺真实形态/技能启用链、不同伤害政策对既有闪避家族审查未完，不以几条if或文字constant加数；动作栏不等于目标灰字。','完整所述事件方法及相邻前285行已读，非整类/技能系统全文。')
save('mineandslash-dodge-and-early-spawn-lock-pending-external-native-hook','RobertSkalko/Mine-And-Slash-Rework',['src/main/java/com/robertx22/mine_and_slash/database/data/stats/effects/defense/SpellDodgeEffect.java','src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/reworked/NewDamageMain.java','src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/OnPlayerDamageEntityEvent.java'],
 'SpellDodge全文：magic spell限定，dodge-accuracy夹0后按源等级getUsableValue，随机命中标IS_DODGED。OnPlayerDamageEntityEvent全文static lock/try-finally，client cancel、void放行、mob tick<3取消damage0；原伤非自家源再走转换或tryAttack。NewDamageMain全文注册Exile before/after hooks，多处override先后。',
 '外部Exile原生事件入口/最终结算与实际stat启用未补，已有nullified反馈不重复；早出生取消不能误标Boss免疫。','三类全文已读，外部库和EffectEvent执行器未追齐，0credit。')
save('forbidden-quantum-catcher-cost-hint-support-not-native-boss-feedback','stal111/Forbidden-Arcanus',['neoforge/src/main/java/com/stal111/forbidden_arcanus/common/event/PlayerEvents.java','neoforge/src/main/java/com/stal111/forbidden_arcanus/common/item/QuantumCatcherItem.java','neoforge/src/main/java/com/stal111/forbidden_arcanus/client/gui/label/QuantumCatcherFlyingLabel.java'],
 'EntityInteract将item.onEntityInteract返回设为取消结果并无条件cancel；target黑名单/死亡或已存entity返回PASS，资源不足FAIL；成功服务端序列化存stack/discard后consume。释放addFreshEntity结果不查就清存储。cost按maxHealth/friendly类别算；client label仅空容器+valid target时显示cost格式。',
 '捕获黑名单与已计SoulVial/Bubble对比支持0；cost/hint具体EssenceCost/StoredEntity/实际渲染方法未补，不把目标提示接口或新物品名当Boss免疫文字。','三个类全文已读，实际注册两字段已观察；只固定版本补抓2Java，获取本身0。')
# Spectrum cache observed read-only: retain prior fixed manifest but no independent tree admission.
manifest=R/'docs/cod4/audit-20261022/sweep-receipt-research/helpers/combat-spectrum/source-manifest.json';meta=next(x for x in json.loads(manifest.read_text()) if x['repo']=='DaFuqs/Spectrum');root=R/meta['source_root'];refs=[]
for x in meta['files']:
 rel=x['path']
 if any(s in rel for s in ['DefaultAzureDikeComponent.java','AzureDikeProvider.java','AzureDikeItem.java','AetherGracedNectarGloves','PuffCircletItem.java','SleepStatusEffect.java','LivingEntityMixin.java','SpectrumComponentInitializers.java']):
  q=root/rel;assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'];refs.append({'path':str(q.relative_to(R)),'source_path':rel,'file_sha256':x['sha256'],'url':f'https://github.com/DaFuqs/Spectrum/blob/{meta["revision"]}/{rel}'})
rows.append({'id':'spectrum-local-cache-native-admission-observed-provenance-pending','repo':'DaFuqs/Spectrum','commit':meta['revision'],'research_credit':0,'refs':refs,'observation':'AzureDike absorb即使空盾也延充，少量护盾被吸尽后可仍失败挡状态；Gloves只够完整amp成本才拒绝harmful/frenzy且排bypass tag；Puff fall要求charges>cost严格大于，等于成本不反弹；Sleep immuneish不是全部拒睡：部分改duration，Fatal仍可伤，Eternal非player强制sleep分支不以immuneish全面豁免。Dike NBT存float读int、copyData将lossless作为resetCharge，不能假设balance完整保留。','exclusion_or_pending_reason':'已有他岗固定归档manifest/hash支持；主岗独立fixedtree请求25秒超时，4366639bytes部分结果保存，未导入有效来源、不重试。实际资源/最终外部入口未全部闭合，不能提前算有效或转旧账。','read_granularity':'DefaultAzureDikeComponent/AzureDikeProvider/AzureDikeItem/Gloves/PuffCirclet/SleepStatusEffect/SpectrumComponentInitializers全文已读；LivingEntityMixin只读完整选定390–590段方法，非整类；组件interface未读。'})
(O/'uncredited-observations-20261027f.json').write_text(json.dumps({'credit':0,'observations':rows},ensure_ascii=False,indent=2)+'\n');print(len(rows),'groups, credit0')
