"""Actual Aether Boss HUD identity/visibility policy; not generic GUI library credit."""
from ledger import B,O,record,verify
import json
r='The-Aether-Team/The-Aether';p='src/main/java/com/aetherteam/aether/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
config='src/main/resources/aether.mixins.json'
k='aether-native-boss-event-uuid-to-entity-id-visual-lifetime-and-conditional-vanilla-suppression'
record(k,r,[f('Aether.java',131,135),f('Aether.java',216,269),f('entity/AetherEntityTypes.java',93,96),
    f('entity/monster/dungeon/boss/Slider.java',97,106),f('entity/monster/dungeon/boss/Slider.java',430,452),
    f('entity/monster/dungeon/boss/Slider.java',499,507),f('entity/monster/dungeon/boss/Slider.java',591,621),
    w('entity/AetherBossMob.java'),w('network/packet/clientbound/BossInfoPacket.java'),
    f('client/AetherClient.java',44,50),f('client/AetherClient.java',111,136),
    f('client/event/listeners/GuiListener.java',25,31),f('client/event/listeners/GuiListener.java',92,101),
    f('client/event/hooks/GuiHooks.java',52,52),f('client/event/hooks/GuiHooks.java',303,339),
    w('mixin/mixins/client/BossHealthOverlayMixin.java'),
    (config,1,len((B/'sources'/r.replace('/','__')/config).read_text().splitlines()))],
    '真实Slider注册/构造ServerBossEvent→startSeenByPlayer先发Display(eventUUID,entityID)，只在无dungeon或玩家被dungeon跟踪时bossFight.addPlayer；stopSeen先发Remove再removePlayer。真实playToClient注册→Display.execute写静态Map<eventUUID,int>，Remove仅按eventUUID删。clientInit/eventSetup注册GuiListener，真实BossEventProgress监听按Map成员绘制；drawBossHealthBar每帧从当前world按ID重取AetherBossMob、动态取该实体Component/texture。声明的BossHealthOverlayMixin在原生render事件STORE后仅对能解析为AetherBossMob的映射cancel原版条。',
    '计1：真实Boss战斗反馈的双身份映射、可见性和自定义/原版替换生命周期策略。不是免疫生产，不因三Boss/两个packet/字体或sprite包装另计。Display map到达不等于vanilla boss event已入可见集合；事件UUID不是实体UUID，当前世界ID重用成另一AetherBossMob仍能过class检查。目标未加载时draw不画，但GuiListener仍increment+13；Mixin也不取消原版，这两个条件不同。Remove未比较entityID或代次，所读显示/移除路径无TTL/维度/实体UUID校验；同key重复Display覆盖不新增对象，但不是逐目标时间节流。所读client eventSetup的logout仅reset工具状态，不能据此断言整个mod所有未缓存文件没有清理。',
    'Boss灰字应携带实体UUID与维度/有限生命周期，不能把BossEvent UUID混成目标UUID；目标丢失应明确丢弃或短期等待，显示与抑制替代反馈使用相同资格。原版/自定义回执并存不能仅凭发送或Map非空判显示通过。',
    '实际tracking生产/移除、packet全文、render消费完整方法和声明mixin已读；generic平台BossEvent进度插值/字体绘制0额外。MixinPlugin/Optifine条件及平台字节码局部变量布局未审，声明不是加载成功证据。未启客户端，不证明文字可读、遮挡、热重载或两TCP画面；本例HUD屏幕定位不能当世界头顶锚定实现。',
    'native_boss_visual_identity_visibility_and_lifetime_policy')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch117-aether-actual-boss-visual-map-and-fallback-lifetime','credited_chains':[k],'rationale':'One native gameplay Boss HUD identity/lifecycle policy with actual tracking producer, consumer and conditional vanilla replacement. Different from Slider refusal reason cooldown; packet/render wrappers and other boss skins merge.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
