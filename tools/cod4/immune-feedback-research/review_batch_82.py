"""Native attacker-pose/weapon damage acceptance with world/entity side effects."""
from ledger import B,O,record,verify
import json
r='klikli-dev/occultism';p='src/main/java/com/klikli_dev/occultism/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='occultism-native-golem-attacker-pose-weapon-acceptance-before-shard-transition'
record(k,r,[w('common/entity/familiar/IesniumGolemEntity.java'),f('registry/OccultismEntities.java',402,407),f('registry/OccultismEntities.java',550,551),f('registry/OccultismItems.java',73,75),f('registry/OccultismTags.java',203,203),f('datagen/tags/OccultismItemTagProvider.java',270,271),f('Occultism.java',105,105)],
 '实际注册IesniumGolem extends IronGolem及实体工厂，原生isInvulnerableTo(ServerLevel,DamageSource)：void先teleport world spawn并向上直到4个block检测可容身；weapon item实际IESNIUM_KNIFE tag直接return false；否则来源entity缺失或不crouching直接true，有crouching才super。实际actuallyHurt再次调用该gate，允许时先createShard再super：备份原HP→set满HP/resetFall/removeAllEffects/discard自己→保存本体entityData进fragile soul gem→恢复原HP→spawn掉落item。tag实际填入已注册iesnium butcher knife。',
 '一个由攻击者当前姿态与来源携带的武器快照联合决定接受/拒伤并切换成保存物品的最终位点1，不是同源常量换壳。不把void恢复另外计数，归既有回场保护支持。knife直接false绕过本法super资格，不等于最终hurt必成功；非刀crouching也仍须super。void传送在最终拒绝前，且actuallyHurt重复查询还可再触发，故资格检查并非无副作用；while未显式y上界/步数上限，未运行验证极端地形。createShard发生在super真正扣血前，保存发生在discard后，不能据掉落已出现推断伤害/死亡成功；保存时刻移除态与后续真实载入行为未验。拒伤分支没有灰字/嗡鸣/专用回执。',
 'Boss免控reason应来自专门控制入口和权威策略，不从来源姿态不允许/刀具交互收取/保存实体的hurt结果推导。应避免带位置/卸载/掉落副作用的资格方法反复调用；反馈只有明确最终拒控才发送。',
 '固定版本，完整实体类及直接注册/tag填充已读；未审复制模型/资产，未启动游戏，未验证native玩家攻击、极端地形、物品载入或像素。非Boss普通实体策略仅作语义反例，不增项目灰字要求，不按刀名/void/4空间检查加数。','native_attacker_pose_damage_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'occultism-batch82-golem-attack-eligibility','credited_chains':[k],'rationale':'姿态/来源武器门与原生actuallyHurt转换保存物的完整资格位点1；回场保护/刀tag/注册包装0，区别于单来源filter、Boss阶段无敌和通用阵营判断。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
