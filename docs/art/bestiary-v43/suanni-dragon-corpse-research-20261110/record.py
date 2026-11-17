"""Seal selected source research; never modify production or main task lists."""
from pathlib import Path
import hashlib
import json

O = Path(__file__).resolve().parent
R = O.parents[3]
C = R / 'build/creature-reference-1000/AlexModGuy__Ice_and_Fire'
J = C / 'src/main/java/com/github/alexthe666/iceandfire'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n, data): (O/n).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

baseline = R/'docs/art/bestiary-v43/suanni-death-intent-review-20261110/review.json'
production = json.loads(baseline.read_text())['production_hashes']
for p, h in production.items():
    assert sha(Path(p)) == h, 'Production asset changed: '+p
downloads = json.loads((O/'source-verification.json').read_text())
assert sum(x.get('cached_byte_match') is True for x in downloads) == 8
assert sum(x['exit'] == 0 for x in downloads) == 10

study = {
 'identity':'IceAndFire:shared_dragon_model_dead_policy',
 'revision':'02b2922003cbce3c67dad55dfea79acf1721e0db',
 'scope':'选定死亡/姿态转换/支撑/渲染/保存链的实际源码阅读；不是所有攻击、所有全局补丁或完整Tabula运行重建。',
 'read_scopes':{
  'DragonTabulaModelAnimator.java':'1–250完整setRotationAngles和setRotationsLoop；251–287辅助与性别方法；animate仅入口及首段，不声称全部攻击已读。',
  'IceAndFireTabulaModelAnimator.java':'完整文件：default相等判定、角度最短差、位置与旋转转换。',
  'FireDragonTabulaModelAnimator.java':'完整文件：四walk/六fly及swim复用walk，模型枚举绑定。',
  'DragonAnimationsLibrary.java':'完整文件：模型资源路径、注册、共享引用；实际ClientProxy注册调用点未在当前缓存找到。',
  'EntityDragonBase.java':'535–630死亡与noAI，740–765/790–810保存读取，975–1002同步，1048–1085 customPose，1120–1202尸体采集，1705–1835 tick/aiStep，2548–2573眼层，2700–2772头部位置。非全实体。',
  'IafDragonLogic.java':'285–435客户端/公共进度方法所选范围；不声称全部服务端攻击逻辑已读。',
  'RenderDragonBase.java':'完整文件：scale/纹理缓存/层注册；未读全部护甲/乘客/旗层。',
  'LegArticulator.java':'完整文件。',
  'LegSolver.java':'完整文件。',
  'LegSolverQuadruped.java':'完整文件。',
  'LayerDragonEyes.java':'完整文件。',
  'TabulaModelHandlerHelper.java':'完整文件。',
  'EnumDragonPoses.java':'完整文件。',
  'EnumDragonModelTypes.java':'完整文件。',
  'firedragon_Ground.tbl / firedragon_Dead.tbl':'官方固定提交资源ZIP中model.json；实际提取并阅读18个相关身体/颈/头颚/四肢局部变换和父子关系，非游戏画面。'
 },
 'findings':[
  'tickDeath每次把deathTime置0、同步ModelDead并卸客；尸体按采集DeathStage与年龄阈值移除，不是普通20tick或duration-20定时消失。交互采集还可直接移除尸体。',
  '公共逻辑在ModelDead时以0.5增长到20：从0起40次更新。不可称每个加载案例都是40tick，因为保存读取与customPose会改变起点。',
  'tick仍调用公共逻辑，但ModelDead分支跳过updateDragonClient；LegSolver.update位于客户端活体路径，死亡后不继续更新采样。模型末尾articulateQuadruped无死亡排除，满足宽度>=2且fly/hoverProgress为0仍可能消费残留高度。',
  '每帧reset默认、执行animate、逐cube转换死亡等进度，之后活体idle/look由isNoAi排除；isNoAi包含ModelDead。缓存摆动缓冲应用也排除ModelDead。死亡不自动等于清除已有其他进度。',
  '死亡转换用插值进度/20；大腿使用直接角差，其他骨用最短角差。位置也在transitionTo内转换；但外层仅在isRotationEqual为false时调用，只有位置变化而默认旋转相同的cube不能假定会被转换。',
  '火龙资源BodyUpper局部Y由11.6到20.6，X旋转5.22到13.04；颈三级+Head形成偏转、头roll49.57；Jaw松开并偏转。后腿不对称外翻，前翼臂分级松落。它不是只平移一个头。具体值只作阅读证据，不移植到Dynasty。',
  '冰龙专用分支为BodyUpper增加0.35*插值死亡进度，最大7个局部模型单位，源码明确为尸体贴地补偿；不是世界地面求解器，也不能外推到所有龙或狻猊。冰龙Dead资源TLS下载失败，未检视其真实终姿。',
  '实体tick尸体遇脚下空块时向下移动0.2，另将dragonPitch恢复0；这是实体层下落/朝向，不等同模型头颚接地。正pitch分支Math.min(0,pitch-5)可能直接归零，不笼统描述为所有情况匀速衰减。',
  '渲染scale先绕X施加dragonPitch再按renderSize/3缩放；本类无setupRotations或getFlipDegrees覆盖。deathTime持续置0使常规死亡计时侧翻不积累，但不声称未读父类/全局环境已原生验证。',
  'getHeadPosition的deadProg=-0.02*进度用于实体头位置近似，不是从Tabula Head/Jaw最终顶点算出。不能把该点直接当嘴部落地证明。',
  'NBT写读ModelDead、DeadProg、DeathStage；随后readAdditionalSaveData会调用setCustomPose，而该setter无条件把modelDeadProgress设20。不能据保存DeadProg就宣称瞬时死亡进度可精确恢复。',
  '眼层仅在shouldRenderEyes时绘制；该条件排除ModelDead、睡眠、眨眼和石化。保留头部祖先链并复制变换是对齐方法，不是额外身体/独立参考。'
 ],
 'comparison_to_prior':{
  'Suanni':'已测最终几何头颚距地约7.9cm，旧生成器补偿在后续精修前计算。新研究支持按最终父链与渲染完整变换检查接触；不支持直接把世界差值减到局部Y。原90tick与已认可外形保持。',
  'EnderGolem/Monstrosity':'根部、上身与头、四肢协同改变；原动画死亡时长与实体实际移除必须分别核对。龙为持续可采集尸体，与它们不是同一移除策略。',
  'Frostmaw':'也有地形腿部调节，但龙死亡后客户端地形采样路径停止；不能以存在LegSolver当成尸体接触认证。',
  'Wroughtnaut/Foliaath':'共享动画器/分阶段下落不自动保证头部贴地；仍须完整模型父链和渲染层检查。'
 },
 'limitations':[
  '没有运行Java、游戏或Tabula；没有世界空间头颚/前肢接触数值认证。',
  '模型资源仅查火龙Ground/Dead选定部位；冰龙Dead TLS失败保留原失败，不换证书/不关闭TLS验证。',
  '实际ClientProxy注册和Citadel Tabula模型容器到AdvancedModelBox的转换未闭合；火/冰/雷不能分别计为完整独立死亡实现。',
  'LegSolver/眼层/枚举/解压辅助为本地实际阅读、哈希绑定；未全部逐字远端验证。',
  '该固定源使用旧版Quaternion/Vector3f与旧DamageSource接口，仅研究方法，不升级/拷入项目。'
 ],
 'qualification':'RELATED_SHARED_DRAGON_CORPSE_CHAIN_PARTIAL; NOT_WORLD_CONTACT_ACCEPTED',
 'new_accepted_semantic_credit':0,
 'new_production_ready_credit':0,
 'dedup':'火/冰/雷模型枚举、姿态数、四肢和骨骼数量都不算独立实现；历史1000静态与旧有效100要求不清零。'
}
put('study.json', study)
put('local-source-bindings.json', [{
 'path':str(J/p), 'sha256':sha(J/p)
} for p in [
 'client/model/util/LegSolver.java','client/model/util/LegSolverQuadruped.java',
 'client/render/entity/layer/LayerDragonEyes.java','client/model/util/TabulaModelHandlerHelper.java',
 'client/model/util/EnumDragonPoses.java','client/model/util/EnumDragonModelTypes.java'
]])
put('progress.json', {
 'status':'SOURCE_RESEARCH_CONTINUES; PRODUCTION_GATE_NOT_MET',
 'new_related_partial_chain':1, 'new_accepted_semantic_credit':0,
 'prior_custom_death_source_study_candidates_retained':5,
 'partial_dragon_not_added_to_complete_count':True,
 'production_hashes_unchanged':production,
 'production_modified':False,'java_or_game_started':False,'master_lists_modified':False,
 'tasks_deleted':False,
 'next':'补读实际龙类注册与Citadel容器变换，或查另一个未覆盖的四足头颚/前肢贴地机制；不重复481walk/103stomp/165death采样，不将源码哈希和重复骨链计为1000语义参考。'
})
files=[p for p in O.iterdir() if p.is_file() and p.name!='handoff-metadata.json']
files += [p for p in (O/'sources').iterdir() if p.is_file()]
put('handoff-metadata.json', {str(p.relative_to(O)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)})
print(json.dumps({'receipt':str(O/'handoff-metadata.json'),'sha256':sha(O/'handoff-metadata.json'),'production_unchanged':True}, ensure_ascii=False))
