"""Preserve actual reviewed exclusions/pending chains, always zero credit."""
from ledger import O,B,R
import json,hashlib
rows=[]
def add(key,repo,names,state,reason,remaining):
 root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());refs=[]
 for name in names:
  matches=list(root.rglob(name));assert matches,(repo,name)
  for p in matches:
   rel=str(p.relative_to(root));refs.append({'path':str(p.relative_to(R)),'source_path':rel,'lines':[1,len(p.read_text().splitlines())],'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{rel}'})
 rows.append({'id':key,'repo':repo,'commit':meta['commit'],'status':state,'research_credit':0,'reason':reason,'remaining_for_promotion':remaining,'source_refs':refs})
add('mineandslash-old-render-dead','RobertSkalko/Mine-And-Slash-Rework',['DamageParticleRenderer.java','DmgNumPacket.java','DamageParticleAdder.java'],'excluded_inactive',
 '完整renderParticle含if(true)return；旧DamageEvent.sendDamageParticle的实际调用处均注释。注册旧包不等于生产回执仍接活；不能把不可达font调用当显示实现。',
 '永久保留本固定提交反例；新nullified原生粒子链已合并计入有效台账，不重复。')
add('meteor-client-delta-text-overlap','njlent/Damagenumbers-Meteor-client-addon',['DamageNumbersMeteorAddon.java','LivingEntityMixin.java','DamageNumbersModule.java','TextParticle.java'],'reviewed_zero_pending_semantic_independence',
 '四Java全文已读：客户端tick TAIL血差→module过滤48格/本世界→deque256/64/16淘汰→快照头顶+重力→COLLECT_SUBMITS SEE_THROUGH。与已计血差粒子家族机制高度重合，Meteor生命周期包装/颜色阈值不足以自动新增计数；没有拒控语义。',
 '若后续能证实独立且切题的生命周期/语义特性，再复核；当前0。未声称其是已证明源码复制。')
add('retro-port-family','astryxion/Damage-Indicators',['PopoffRenderer.java'],'excluded_family_port',
 'Retro家族版本/平台分支不能按文件或绘制包装重复计数；当前已读有效Retro主链另有1条，不把跨版本存量直接累计。',
 '需独立的新语义调用链而非类名/平台改名。')
add('netherite-unused-hurtparts','lender544/new1.20.1',['Netherite_Monstrosity_Entity.java','Netherite_Monstrosity_Part.java'],'excluded_unproven_entry',
 '完整部件hurt实际调用attackEntityFromPart→parent.hurt（根state4拒绝）；另有hurtParts直接super但在取得的同版本源内未找到调用者。因此不能声称“真实部件绕过state4”，也不将未证实入口算作独立研究。',
 '需完整固定树调用者追踪；仅已取文件搜索无匹配不足以证明全仓库死代码。')
add('cat-generic-phase-copies','lender544/new1.20.1',['Ancient_Remnant_Entity.java'],'reviewed_zero_template_overlap',
 '完整hurt/isSleep/necklace getter已读：state7、非12箭矢、睡眠拒绝。当前与已有Boss阶段/来源门控语义重复，未按每个状态值和伤害种类扩增。',
 '状态生命周期未完整追踪；此文件全文已保存但不代表全类已研究。')
add('cat-revenant-shield-overlap','lender544/new1.20.1',['Ignited_Revenant_Entity.java'],'reviewed_zero_template_overlap',
 '完整hurt已读：斧暴击增加盾损并发音、方向盾排穿刺箭；与已计TF方向盾/破盾决策重合，不能仅四次盾损对比三次就加1。',
 '未宣称整个Boss动作/同步链已读；不计模板阈值差异。')
add('tf-health-sideeffects-not-immune','TeamTwilight/twilightforest',['Yeti.java','DeathTome.java','LichMinion.java','SnowQueen.java'],'excluded_wrong_semantics',
 '已读相关hurt覆写分别是生气、火伤翻倍/掉落、成功伤害后buff、beam受伤统计；没有所拟称的拒绝结果。不能凭关键词或Boss名计免疫实现。',
 'SnowQueen盾部件另有候选，父类beam统计不算同一拒绝实现；这些全文件引用是可审查上下文，不声称所有方法已研究。')
add('tf-naga-segment-wrapper','TeamTwilight/twilightforest',['NagaSegment.java'],'excluded_same_chain_wrapper',
 '全类已读；segment.hurtServer仅不可见时拒绝，否则父Naga.hurtServer的2/3伤害。父链已计，部件包装不加数。',
 '可补入父链上下文，不独立计数。')
add('tf-shield-true-not-hp','TeamTwilight/twilightforest',['SnowQueenIceShield.java','TFPart.java'],'reviewed_zero_pending_entry_chain',
 '两类全文已读：穿刺箭hurtServer直接true且不调用父伤害，其他来源播放碎冰声false。因此true不等于实际Boss扣血；原生入口/父部件组生命周期尚未全文串完。',
 '需补父SnowQueen构造/parts/tick与平台部件入口边界，再评估语义独立性。')
add('aoa-mixed-source-activation','Tslat/Advent-Of-Ascension',['TESIntegration.java','SkullPlateMultipart.java'],'reviewed_zero_version_provenance',
 '已读TESIntegration完整类与SkullPlateMultipart/父部件有关方法；档案同时含不同Minecraft API时代源码，取得的提交未确认各旧Boss的构建注册激活入口。TES桥调用旧接口不能与另一项目当前HEAD拼成已验兼容链。',
 '需要实际构建/注册映射及匹配TES版本，候选不计。')
add('goety-monolith-native-feedback-pending','Polarice3/Goety-2',['AbstractObsidianMonolith.java','AbstractMonolith.java','ObsidianMonolithRenderer.java','AbstractMonolithRenderer.java'],'reviewed_zero_pending_producer_activation',
 '完整hurt/handleEntityEvent/aiStep和盾层render已读：empowered拒绝→entity event6→shieldTime10→客户端tick递减→energySwirl绘制。渲染名alpha实际传给RGB，最终alpha仍1，不能称透明度渐隐。IS_EXPLOSION/IS_FIRE在回执前拒绝，无同一盾回执；Emerging走父isInvulnerableTo。尚未证实empowered原生赋值入口及renderer注册。',
 '补empowered赋值、实体/renderer激活注册和未读辅助；当前不能报成完整原生可运行链。')
(O/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
groups=[
 ('dnp-platforms','dnp-health-delta-worldtext','同一项目1.21.9/1.21.11变体合并；数字、颜色、TextGroup包装不拆。'),
 ('retro-family','retro-health-sync-active-text','选定有效Retro链1；未激活粒子和同源跨平台绘字不累计。'),
 ('tes-api-and-worldtext','tes-explicit-component-and-health-particle-chain','显式文本API、健康数字、文本风格/提交包装全合并；泛用库0。'),
 ('dummy-derived-renderers','dummy-authoritative-hit-number-particle','Dummy原生setHealth/源记录链1；Immersive另计本地攻击归因+shader回退完整语义链1，复用的35tick字粒子/pose本身0；后续Mmm Indicators同链不得再计。'),
 ('cat-shared-boss-base','cataclysm-range-damagebucket-authority','LLibrary/IABoss同构伤害桶与距离链合并；子类仅继承、配置覆盖、阈值不同不另计。'),
 ('cat-effect-tag','cataclysm-boss-effect-allowlist-refusal','两个同构基类、每个tag成员、Lazy标签包装合并1，不按36行资源拆。'),
 ('tf-shared-mounted-shield','tf-mounted-goblin-shared-shield-rejection','Upper/Lower delegate同一盾判定合并，动画字节包装0。'),
 ('mineandslash-nullified','mineandslash-native-nullified-receipt-particle','DODGE/RESIST、Default/Row、codec/通知器/RenderUtils合并1，旧不可达renderer0。'),
 ('simple-combat-gui','simplecombat-server-hit-to-projected-hud-text','服务端事件→按ID选择/按对象合并→投影GUI整链1，worldToScreen/颜色/动画各包装0。'),
 ('generic-libraries',None,'Anima、ImmersiveMessages、Library of Exile等仅链路辅助，不单独计研究；关联源码版本不自动证明实际依赖二进制兼容。')
]
(O/'semantic-dedup.json').write_text(json.dumps({'status':'ongoing_manual_semantic_review','key_uniqueness_is_not_semantic_proof':True,'groups':[{'family':a,'credited_chain':b,'rationale':c} for a,b,c in groups]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'zero_credit_records':len(rows),'dedup_groups':len(groups)}))
