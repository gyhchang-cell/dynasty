"""Native damage-qualified reputation transition receipt and AI retaliation eligibility, one policy."""
from ledger import B,O,record,verify
import json
p='src/main/java/com/github/alexmodguy/alexscaves/'
refs=[(p+'AlexsCaves.java',91,133),(p+'server/entity/ACEntityRegistry.java',68,68),(p+'server/entity/living/DeepOneEntity.java',35,53),(p+'server/entity/living/DeepOneBaseEntity.java',455,496),(p+'server/entity/living/DeepOneBaseEntity.java',537,548),(p+'server/entity/living/DeepOneBaseEntity.java',645,710),(p+'server/level/storage/ACWorldData.java',26,92),(p+'server/misc/ACTagRegistry.java',94,94),(p+'server/misc/ACTagRegistry.java',121,123),('src/main/resources/data/alexscaves/tags/damage_type/deep_one_ignores.json',1,6)]
for f in ['server/entity/util/DeepOneReaction.java','server/entity/ai/DeepOneTargetHostilePlayersGoal.java','server/entity/ai/DeepOneReactToPlayerGoal.java']:
 refs.append((p+f,1,len((B/'sources/AlexModGuy__AlexsCaves'/p/f).read_text().splitlines())))
k='alexscaves-native-damage-qualified-reputation-band-receipt-and-retaliation-refusal'
record(k,'AlexModGuy/AlexsCaves',refs,
 '原生DeepOne entity/goals真实注册；完整hurt先取super结果，只sup=true、来源Player、server且非DEEP_ONE_IGNORES才活体-5/死后-15。addReputation读UUID旧值→按未clamp新值算reaction→overworld共享SavedData写clamp[-100,100]；仅跨reaction档并找到当前world玩家才displayClientMessage(translatable reaction,true)。getReactionTo正常读声望，召唤者另HELPFUL。原生目标goal只选AGGRESSIVE非creative，HurtByHostileTargetGoal.canAttack对HELPFUL玩家直接false；React goal按reaction执行跟随/追逐/帮助。',
 '一个战斗结果限定的持久身份档位反馈与最终AI报复拒绝政策1，非普通按常量列表不许hurt。无需每次伤害刷屏，只有状态跨档才发文字，目标是来源玩家而非受害者头顶。sup=false不扣声望也不发此回执，但没有由false推出免疫；hurt=true也不在这里证实最终HP。区间<=-10攻击、<=10跟踪、<=30中立、其余帮助；原生免声望伤害tag默认荆棘。UUID声望由主世界保存跨维共用，提示只当前level.getPlayerByUUID命中；没找到仍先保存状态，无补播已错过提示证据。',
 'Boss灰字应按明确拒控事件和目标节流；状态档位文字与每次拒控文字不同语义，不能移用玩家actionbar作为Boss锚定证据。来源身份/伤害是否被接受须在最终生产点区分；普通阴阳不新增文字。',
 '全文读包含hurt/声望get-set-add/两类目标goal/copyTarget/反应goal和SavedData get/load/save方法。ACWorldData只具名保存与声望方法，不称完整地图/原始Boss工作器已读；初始正声望barter生产不在本项覆盖，不声称完整自然全部四档进度。只有HELPFUL报复canAttack分支拒绝，群体alertOthers/已有目标不在同法重新判reaction，不可泛称所有AI不会攻击朋友；newReaction预clamp与持久值可能不同，在正常阈值附近不凭静态推断玩家实际错误提示。vanilla原生文本收包/字体绘制不另展开，不称本地化/像素/声音/TCP验收；提示无专用灰字微光，未动正式代码或启动。','native_combat_state_transition_feedback')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch152-damage-qualified-reputation-state-feedback','credited_chains':[k],'rationale':'One damage-result/source-tag-qualified reputation transition receipt and native AI retaliation eligibility policy. All species, reputation thresholds, goal adapters, messages and save wrappers merged; not boss immune inferred from false hurt.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
verify()
