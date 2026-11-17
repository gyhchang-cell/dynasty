"""Record bounded body-animation research. No runtime asset writes."""
from pathlib import Path
import hashlib
import json
import zipfile

O = Path(__file__).resolve().parent
R = O.parents[3]
J = R/'build/creature-reference-1000/lender544__new1.20.1/src/main/java/com/github/L_Ender/cataclysm'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d): (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

base=json.loads((R/'docs/art/bestiary-v43/suanni-death-intent-review-20261110/review.json').read_text())['production_hashes']
for p,h in base.items(): assert sha(Path(p)) == h, 'Production changed: '+p
v=json.loads((O/'source-byte-verification.json').read_text())
assert len(v)==4 and all(x['exit']==0 for x in v)
assert sum(x['cached_match'] is True for x in v)==3
anim=O/'sources/Ancient_Remnant_Animation.java'
assert sha(anim)==json.loads((O/'animation-download.json').read_text())['sha256']

put('study.json',{
 'identity':'Cataclysm:Ancient_Remnant:death_body_disarticulation',
 'revision':'819937203e22b4fa72fdeccc6c56ad415d65eeef',
 'read_scope':{
  'Ancient_Remnant_Rework_Model.java':'1–180字段/完整构造父链；175–265所选主根/躯干/头颚几何，中间输出少量被截断不称全createBodyLayer；385–末尾完整setupAnim与articulateLegs。',
  'Ancient_Remnant_Animation.java':'1952–2137完整DEATH；首次输出中desert_eye约百余token被截断，2066–2090和2088–2137补读。未读全部其他动画。',
  'Ancient_Remnant_Entity.java':'78–101声明/求解器；308–355睡眠与保存；385–435浮水/动画状态查找；454–620同步/死亡/tick；1510–1575死亡回调、清理后的重生器与bossbar所选方法。非整实体战斗研究。',
  'Ancient_Remnant_Renderer.java':'完整文件；getFlipDegrees0。',
  'Ancient_Remnant_Layer.java':'固定提交补取完整文件阅读；仅生存且Power时重绘眼层。',
  'Internal_Animation_Monster.java':'1–108所选ATTACK_STATE、事件、tick与tickDeath，复用已有父链研究；不重复信用。',
  'Animation_Monsters.java':'105–170所选onDeathUpdate/die，复用父链研究；不重复信用。',
  'IABoss_monster.java':'声明与65–108保存/读取；继承Internal_Animation_Monster。'
 },
 'body_chain':'root→roots→mid_pivot；其下pelvis→spine1→spine2→neck1→neck2→head→jaw，双臂分属spine2；legs与pelvis同级，双腿各自分段。不是普通四足支撑，实体仅两条腿求解采样。',
 'state_chain':'die调用super后setAttackState(3)，同步回调先stopAllAnimationStates再启动death；父setAttackState重置attackTicks并广播负状态事件，父tick递增状态计时。idle在客户端按state!=3启停。',
 'clip_seconds':2.375,
 'clip_nominal_ticks':47.5,
 'removal_threshold_ticks':70,
 'selected_phases':[
  {'time_seconds':'0–0.5','reading':'头部摇摆/抬颈/张颚，双臂先收紧；不是一开始就下移头。'},
  {'time_seconds':'0.5–0.875','reading':'roots降低10源posVec单位并偏航20度；pelvis前后俯仰、腿/小腿/踝分段折叠，颈与头以不同角度接住下沉。'},
  {'time_seconds':'0.875–1.125','reading':'主要根部/腿部保持；尚未进入颈臂大幅错移。'},
  {'time_seconds':'1.125–1.875','reading':'双臂先后局部位置大幅错开；neck1在1.375–1.625位移至源(0,-70,40)，neck2随后偏转/平移；jaw在1.5833–1.875错移。推断为残骸散落/脱节式终态，不能说仍为连贯承重四足。'},
  {'time_seconds':'1.875–2.375及其后','reading':'已列通道均到终值；非loop动画框架在最后关键帧后保持，不会因clip声明长度自行移除。服务端70tick阈值另行清理。'}
 ],
 'support_and_overlays':[
  'setup先reset再加头部look；walk仅排除状态10/11/12和sleep，未排除死亡3。因此死亡时若limbSwingAmount非0仍可叠walk，不能声称死亡天然独占所有姿态。',
  'death与其他AnimationState逐次叠加，状态回调停止旧技能，idle客户端按3关闭；head look不受death状态排除。',
  '地形LegSolver在实体tick内无死亡排除地update；模型articulateLegs在!isSleep时加roots高度并分别补左右腿。状态3且项链在时仍满足此条件。与上批龙死亡后不再更新采样不同。',
  '睡眠定义含无项链；无项链时模型末尾applyStatic(SLEEP)，会在death之后再叠静态睡姿。这一条件不能忽略。',
  '狻猊是四足、保持已认可几何的头颚接地；本例两后腿求解和后半段局部脱节不能拿来证明狻猊前肢支撑，不能照搬neck1大平移。'
 ],
 'cleanup':'Internal_Animation_Monster.tickDeath→Animation_Monsters.onDeathUpdate(70)：先onDeathAIUpdate，再deathTime++，服务器达到70广播60并KILLED移除。本实体死亡AI回调仅super。AfterDefeatBoss在父die路径服务端掉落后调用，可按配置放重生器；不是动画终点回调，不擅自移植游戏机制。',
 'render':'完整renderer无额外scale覆盖，getFlipDegrees=0；Power眼层还要求isAlive，死亡后不应以该层发光掩盖终态。未读取原始PNG，不声称完成模型+贴图或游戏画面参考。',
 'save_boundary':'本类仅显式存项链/Rage/Power，父IABoss存LifeRemain/Home；当前选定链未见保存AnimationState/attackTicks的承诺，不能宣称世界重载死亡姿态连续。',
 'native_math':'沿用本地Forge1.20.1固定源码档，实际阅读KeyframeAnimations全文件与HierarchicalModel动画入口：posVec反转Y，非loop elapsed不取模；最后帧索引夹紧、插值施加在默认+其他层上。不是把源posVec的负Y直接解释为世界向下。',
 'limitations':[
  'LionfishAPI LegSolver实现当前缓存未找到，只有本模型调用和实体采样定义可读；不声称地形求解全链闭合或头颚贴地。',
  '未运行游戏/Java，也未做软件全父链顶点求地；CATMULLROM不能用先前线性采样器冒充原生。',
  '没有查看完整动态参考画面，脱节散落是源码位移与层级支持的推断；不是作者画面实证。',
  '父类和原版框架复用，不拆开当新参考；一段clip、若干通道/帧/骨骼不计多个实现。'
 ],
 'qualification':'RELATED_STAGED_COLLAPSE_AND_CLEANUP_STUDY; SUPPORT_DEPENDENCY_PARTIAL; EXCLUDED_AS_QUADRUPED_HEAD_CONTACT_PROOF',
 'new_accepted_semantic_credit':0,
 'not_copied_to_runtime':True
})

archive=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
with zipfile.ZipFile(archive) as z:
 put('native-math-bindings.json',{'archive':str(archive),'sha256':sha(archive),'entries':{n:hashlib.sha256(z.read(n)).hexdigest() for n in ['net/minecraft/client/animation/KeyframeAnimations.java','net/minecraft/client/model/HierarchicalModel.java']},'new_reference_credit':0})
parents=['entity/InternalAnimationMonster/Internal_Animation_Monster.java','entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java','entity/etc/Animation_Monsters.java']
put('parent-source-bindings.json',[{'path':str(J/p),'sha256':sha(J/p),'scope':'选定方法阅读，父链复用0信用，未重新远端校验'} for p in parents])
put('progress.json',{
 'status':'CONTINUING_RESEARCH_NOT_PRODUCTION_READY',
 'this_batch_related_chain_studies':1,
 'this_batch_verified_direct_sources':5,
 'this_batch_accepted_semantic_credit':0,
 'prior_complete_selected_death_source_candidates_retained':5,
 'prior_dragon_partial_chain_retained':1,
 'this_chain_support_dependency_partial':True,
 'current_mapped_accepted':0,'mapped_register_gap':1000,'global_final_gap':None,
 'production_unchanged':base,
 'game_or_java_started':False,'shared_jar_modified':False,'main_lists_modified':False,'task_deleted':False,
 'next':'继续找四足身体完整折叠且头颚与前肢保持连贯支撑的实际来源；排除残骸散落案例充作直接接地信用。补旧参考语义映射，不重新清零。'
})
files=[p for p in O.rglob('*') if p.is_file() and p.name!='handoff-metadata.json']
put('handoff-metadata.json',{str(p.relative_to(O)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)})
print(json.dumps({'files':len(files),'receipt_sha256':sha(O/'handoff-metadata.json'),'production_unchanged':True}))
