"""Pinned world-zone refusal and partial fatal blood settlement; no candidates promoted."""
from ledger import B,O,record,verify
import json
r='Moriyashiine/bewitchment';p='src/main/java/moriyashiine/bewitchment/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def resource(s):
 rel='src/main/resources/'+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k1='bewitchment-native-glyph-ritual-world-zone-damage-nullification'
record(k1,r,[w('mixin/ritual/LivingEntityMixin.java'),w('common/block/GlyphBlock.java'),w('common/block/entity/GlyphBlockEntity.java'),w('common/registry/BWRitualFunctions.java'),w('api/registry/RitualFunction.java'),w('common/recipe/RitualRecipe.java'),f('common/misc/BWUtil.java',37,39),resource('data/bewitchment/recipes/rituals/immortality.json'),resource('bewitchment.mixins.json')],
 '实际启用ritual mixin→GOLDEN_GLYPH原生onUse服务端调用GlyphBlockEntity.onUse→匹配实际immortality recipe（普通内圈/eldritch外圈、3原料、600altar、12000运行）→扣资源且设置PREVENT_DAMAGE/timer=-100。原生LivingEntity.applyArmorToDamage HEAD检查服务端、非BYPASSES_INVULNERABILITY、受害者与找到glyph均在worldborder，BWUtil.iterateOutwards三轴16，glyph.function同一注册对象即amount0。Glyph原生ticker推进/清理，NBT保存function/timer/endTime。',
 '一个按真实场地装置及短期仪式生效的拒伤生产点1。不同于Cyclic缓存beacon区域拒绝效果，按每次hurt查真实BlockEntity；无Boss/阵营/玩家特例，不拒控。不是球半径16判距：传入原版iterateOutwards的三轴范围均16，未另判平方距离。消费者不检查timer>=0，所以启动-100预备期function已满足；超过endTime由服务端ticker清null，边界需看tick顺序。Waystone只改effectivePos，拒伤查询仍围绕受害者找glyph实际pos，不能宣称保护区迁移到effectivePos。目标pos越worldborder时ticker直接return、计时不前进；静态边界不宣称实测产品bug。仪式启动音/粒子是启动反馈，不是每次命中拒伤回执，不能拿来证明Boss灰字/嗡声。',
 'Boss回执应来自准确控制拒绝点，视觉定位目标与服务端判定域使用同一身份；阶段起止与场地迁移不可只由视觉或timer推断。维度与生命周期需明确。',
 '固定842cd9777b7bde2a0208099d5184baf88f24f63a；完整GlyphBlock/GlyphBlockEntity/recipe/function和拒伤方法全文已读，未审原版iterateOutwards内部/区块卸载/跨模组mixin组合。静态不证明实际图像、音响或TCP。注册/配方/持久化均为同链0，不再拆计。','native_world_zone_damage_refusal')
k2='bewitchment-native-vampire-fatal-edge-discrete-blood-partial-settlement'
record(k2,r,[w('common/registry/BWDamageSources.java'),f('mixin/LivingEntityMixin.java',95,100),f('api/BewitchmentAPI.java',191,199),f('api/BewitchmentAPI.java',211,223),w('api/component/BloodComponent.java'),w('api/event/BloodSetEvents.java'),w('common/registry/BWComponents.java'),w('common/registry/BWEntityTypes.java'),resource('fabric.mod.json'),resource('bewitchment.mixins.json')],
 '实际LivingEntity applyDamage/getHealth前modifyDamage0服务端→handleDamage先银弱点/狼人分支，else吸血鬼玩家转化（含人形）或实际注册VampireEntity→handleVampireDamage。非isEffective伤源且health-amount<1时，while health-amount<=0且blood>0：amount--，drainBlood(1,false)。实际living组件初始100，setBlood事件通知后写入并sync，NBT持久化，vampire不走本组件非吸血鬼随机回血。',
 '一个临死边缘按离散血液逐点扣减的原生结算点1；不是Vampirism既有大额伤害原子全额支付/全拒绝。允许支付部分后仍死，资源用尽即不再减；while是<=0，因此只需把剩余HP推到正数，非始终锁1HP，也可能因浮点amount留下0到1间生命。health-amount已经正但<1仅进入外if，实际while不执行。bypass、MAGIC_COPY/SUN、直接source的blacklist/吸血鬼/狼人/带Smite活体或silver均走有效例外，非所有hurt=false。没有灰字/免控reason/声音receipt，血液sync也不能证明战斗反馈。',
 '正式Boss控制免疫必须直接给出拒绝reason，不能把资源减伤、致命保护、伤害bool或组件同步当控制拒绝。无需给普通阴阳体质新增灰字。',
 '固定版本，完整handleDamage/isEffective/handleVampireDamage及血液组件/回调/注册全文；本项只审原生handler和组件契约，不计基础CCA同步为有效位置，不宣称重连或实际音画通过。无游戏/正式修改。','native_fatal_damage_resource_settlement')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'bewitchment-batch70-ritual-and-fatal-blood','credited_chains':[k1,k2],'rationale':'真实glyph阶段/空间拒伤与吸血鬼致死边缘离散资源结算为两个原生点。配方、区块、组件、回调、wrapper均0；barrier实际push_mobs不计。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
