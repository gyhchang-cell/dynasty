from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import record_source_methods as M
def rec(repo,p,n,i=0):
 r=M.record(repo,p,n,i,'CONTEXT_ONLY_NO_COUNT','完整读取的方法正文；不计新的独立美术机制。');r['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';return r
repo='Antikythera-Studios/epicfight';p='src/main/java/yesman/epicfight/api/client/animation/property/TrailInfo.java';q='src/main/java/yesman/epicfight/client/particle/AnimationTrailParticle.java'
r=rec(repo,p,'overwrite');r.update(targetScope='EXCLUDED',reviewMode='READ_SOURCE_EXCLUDED_NO_COUNT',countsTowardReferenceGate=False)
r['observation']='完整读取TrailInfo全类及AnimationTrailParticle.Provider.createParticle的实际合并入口（含前置entity/patch/animation校验及后续构造），并读实际构造器的0/.5/1姿态端点初始化。实际优先级：渲染物品trailInfo作receiver，动画result作overwrite参数；参数字段非null/非负或有效时间才覆盖receiver，再交EntityDecorations修改和playable过滤。start/end_time要求成对有效才整组覆盖，RGB要求三值均>=0才整组覆盖，block/sky取max不允许较暗覆盖。关键限制：overwrite新建Builder却没有复制任一updateInterval，输出回到默认1；unpackAsBuilder确实复制updateInterval，两种路径不能混淆。JSON deserialize未读update_interval而NBT版读；isValidTime排NaN/负数却允许正Infinity，playable也没校验end>=start、不同端点非零距离或颜色上界。createParticle对idx直接get、jointId查回null后镜像路径会解引用，playable不验证真实joint存在；缺idx/joint边界不能由配置合法性代替。这里只补完整配置/调用契约，不把每个字段、两个格式或已审拖尾生产端再计为新学校纹样实现；源码问题不是Dynasty问题，未改外部项目，也未启动Java验证。'
r['callContext']=[rec(repo,p,n,i) for n,i in [('unpackAsBuilder',0),('isValidTime',0),('playable',0),('deserialize',0),('deserialize',1),('updateInterval',0),('create',0),('TrailInfo',0)]]+[rec(repo,q,'createParticle'),rec(repo,q,'AnimationTrailParticle',0)]
repo='SammySemicolon/Malum-Mod';p='src/main/java/com/sammy/malum/visual_effects/ScreenParticleEffects.java'
s=rec(repo,p,'spawnRuneParticles');s.update(targetScope='EXCLUDED',reviewMode='READ_SOURCE_EXCLUDED_NO_COUNT',countsTowardReferenceGate=False)
s['observation']='完整读取spawnRuneParticles正文（至结尾）。方法名含Rune但实际只生成标准SPARKLE和WISP屏幕粒子，颜色来自SpiritLike；随机寿命/偏移/运动及透明度/尺度/旋转easing后spawnOnStack，没有加载任何字形图集、符文字形身份或武器表面UV。第二个WISP builder先spawn一次，再修改参数spawn第二次；不能把两个粒子或每种easing算独立符纹。直接Minecraft.level.getRandom未判null，也未读外部ScreenParticleBuilder语义，不声称菜单无世界也安全或复制builder调用可正确构图。范围排除：GUI物品装饰不等于学院实景残影/皇权纹章。没有把后面未完整阅读的其余ScreenParticleEffects函数记作本次已研究。'
(D/'batch-011.json').write_text(json.dumps({'reviewed':0,'rows':[],'excluded':[r,s],'parentReview':{'status':'TWO_FRESH_SOURCE_CONTRACTS_REVIEWED_NO_CREDIT','newImplementations':0,'newExclusions':2,'mainLedgerUpdated':False,'productionChanges':False,'networkRequests':0}},ensure_ascii=False,indent=2)+'\n');print('batch011: two semantic exclusions; source contract notes retained')
