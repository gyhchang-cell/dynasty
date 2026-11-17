"""One actual client damage-number pipeline, not each particle/helper/loader."""
from ledger import B,O,record,verify
import json
r='luavixen/damagenumbers';p='common/src/main/java/dev/foxgirl/damagenumbers/'
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
key='luavixen-native-health-delta-limited-queue-physical-text-particle'
record(key,r,[w('fabric/src/main/resources/fabric.mod.json'),w('fabric/src/main/resources/damagenumbers.mixins.json'),w('mixins/damagenumbers.mixins.json'),w('fabric/src/main/java/dev/foxgirl/damagenumbers/DamageNumbersInitializer.java'),w('mixins/mixin/MixinLivingEntity.java'),w(p+'DamageNumbers.java'),w(p+'client/DamageNumbersHandler.java'),w(p+'client/DamageNumbersImpl.java'),w(p+'client/TextParticle.java'),w(p+'client/Config.java'),w(p+'client/Color.java')],
 '实际fabric.mod client entrypoint→DamageNumbers reflection handler初始化→声明client MixinLivingEntity在tick TAIL记录previousHealth差值→完整onEntityHealthChange过滤/队列/构建真实TextParticle→client.particleManager.addParticle→自定义buildGeometry朝向camera并TextLayerType.NORMAL提交。fabric资源Git mode symlink的blob是相对路径文本，已解析到固定仓库根mixins实际JSON，未把本地复制的文本文件冒称可运行Jar资源。',
 '世界浮字整链1，三个loader/所有颜色/大小/包装函数0额外。previousHealth初始0，首次正血是负damage被忽略；真实health下降才显示，零伤/控制拒绝完全不可见。排自身默认/需sameworld/48格距离，按原版particle setting256/64/16 FIFO markDead，Deque不移除自然到期项、仅新生时按容量淘汰，不是按目标/事件节流；未见换world清理Deque。出生在头顶+0.25一次快照，速度继承实体速度再相对camera前向偏移，非持续目标绑定，离世后仍由原生particle manager生命周期管而非持有target。maxAge32/重力.75/阻尼.99由原生Particle tick消费，源码没有自有tick，未读原生内部不能宣称实际运动/墙体遮挡观感。实际draw NORMAL非SEE_THROUGH、固定满亮、无阴影、立即flush共享buffer；不把模式名直接当遮挡已验。String.format默认Locale，仅剥endsWith(.0)，逗号小数Locale不剥；配置RGBA插值辅助0。未S2C无damage reason/UUID，不可用health delta推Boss Immune。',
 'Boss需要显式server拒控事件；文字采用可验证目标生命周期/世界隔离/固定tick寿命，并把总容量和每目标节流分别处理。不要复用任意伤害数字作为灰字语义。',
 '固定b77ee7071a54093849f4c6e0b72e055e0a9cf7f1及逐文件Git blob/SHA；所有本条自有完整方法已读。原生Particle/字体底层仅辅助未运行，未确认编译打包symlink处理/游戏画面；未改正式资产/源码/TODO，不启动客户端。','floating_combat_text')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'luavixen-batch48','credited_chains':[key],'rationale':'独立实际native health观察→FIFO运动文字链1，各loader/颜色/粒子渲染wrapper不拆；对比既有DNP/ToroHealth等，保留其独立生产+容量队列/物理快照策略，不按常量差异增加条数。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
