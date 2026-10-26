from ledger import record,verify,attach_auxiliary,B
r='Ovear-Mitama/Damage-Engine';p='common/src/'
files=['main/java/damage/engine/util/DamageTrackerHelper.java','main/java/damage/engine/network/DamagePayload.java','client/java/damage/engine/hud/indicator/DamageIndicator.java','client/java/damage/engine/client/IndicatorPos.java','client/java/damage/engine/mixin/client/ClientTickMixin.java']
refs=[(p+f,1,len((B/'sources/Ovear-Mitama__Damage-Engine'/p/f).read_text().splitlines())) for f in files]
refs += [(f,1,len((B/'sources/Ovear-Mitama__Damage-Engine'/f).read_text().splitlines())) for f in ['neoforge/src/main/java/damage/engine/DamageEngine.java','neoforge/src/main/java/damage/engine/DamageEngineClient.java','neoforge/src/main/java/damage/engine/network/NetworkSetup.java']]
record('damageengine-level-source-merge-and-targeted-worldtext',r,refs,
 '已读完整NeoForge生产事件注册：LivingIncomingDamage捕获快照→LivingDamage.Post实损→pending按tick/ServerLevel对象/target/directSource合并→ServerTick.Post flush→同level玩家S2C→完整客户端receiver过滤→IndicatorPos完整512格射线锚定→addIndicator客户端合并/容量→完整renderWorld及其所属辅助函数链→Anima drawWorldText3D辅助→完整WorldText3D drawComponent→原版font.drawInBatch。两层合并、所有重载、颜色/出场/追踪模式均合1条，不拆包装计数。',
 'health+absorption损失大于0或killed才产包，immune零变化不发。服务端去重有level对象边界，只合连续pending同键，换键会flush；客户端可选按目标ID/无ID距离0.35合并，heal/kill分离，出场开始后不再合并。容量0=不限；时钟为wall clock，500ms清理，持续命中推迟出场。entity模式每帧current level按ID解析目标并插值，失去目标停最后点；crosshair模式固定前6格。实际调用先seeThrough再normal，减少动画时只穿透；不能照注释声称被方块遮挡。',
 '必须单独产生拒控语义事件；可借鉴服务端维度内去重和客户端有界队列，但目标身份/维度生命周期不能只用数字ID。显示模式必须核对实际render调用参数。',
 '研究固定源码的模组自有链；外部Anima辅助固定HEAD不保证与DE声明1.0.7二进制完全一致，不作为可直接粘贴/构建兼容证明。仅复核辅助绘制方法，动画基础库不逐个计数。NeoForge入口仅登录重置mod检测，未在所读路径找到清空所有飘字的登出/维度回调；跨维度遗留属于待验证风险，不直接定产品bug。无游戏/像素验收。')
p='common/src/client/java/anima/'
attach_auxiliary('damageengine-level-source-merge-and-targeted-worldtext','Ovear-Mitama/Anima',[(p+'api/AnimaApi.java',119,165),(p+'client/world/WorldText3D.java',198,293)],'通用库只补字体提交/深度模式边界，不单独计数；版本适配仍待确认')
r='txnimc/ImmersiveDamageIndicators';p='src/main/java/toni/immersivedamageindicators/'
files=['mixins/LivingEntityMixin.java','mixins/PlayerMixin.java','particle/DamageParticle.java','foundation/ParticleRegistry.java','foundation/IrisCompat.java','foundation/CaxtonRenderer.java','api/CreateDamageIndicator.java']
record('immersivedamage-local-attribution-shader-fallback-chain',r,[(p+f,1,len((B/'sources/txnimc__ImmersiveDamageIndicators'/p/f).read_text().splitlines())) for f in files],
 '完整tick HEAD血差缓存→TAIL要求getLastDamageSource.entity是LocalPlayer→一tick一个particle标志→factory→完整DamageParticle构造消息/回调/渲染/tick；shader检测动态选择vanilla字体回调或Caxton，ImmersiveMessage.render→manager.getRenderer→VanillaRenderer完整render→回调DamageParticle.renderMessage→两次NORMAL字体提交。平台注册、反射检测、原版/自定义字体回调、粒子生命周期均已读。',
 '同源说明明确来自TargetDummy：继承的35tick寿命/相机姿态不再单独计数。本条区别是客户端本地攻击归属过滤、tick血差聚合及替换消息渲染/着色器回退，不是另一个Dummy版本。零血差无immune生产点；5秒消息时钟与35tick粒子寿命各自存在；粒子出生世界点固定不持续跟随。shader启用临时forceVanillaRenderer，结束复位，没有try/finally；不据此静态认定运行故障。',
 '可读性需核对真实字体渲染分支；普通受伤飘字的本地攻击归属过滤不能冒充Boss拒控回执。自定义字体与着色器冲突不必靠新增贴图解决。',
 '同源视觉代码已合并去重；计数仅一个具有不同生产/归属/兼容语义的完整整合链。外部消息库为固定候选源码边界，未核对整包实际依赖Jar，没有编译/实机证明。LAST_ATTACK_SWING UUID缓存未在所读链找到清理，不断言泄漏。')
p='src/main/java/toni/immersivemessages/'
attach_auxiliary('immersivedamage-local-attribution-shader-fallback-chain','txnimc/ImmersiveMessages',[(p+'api/ImmersiveMessage.java',274,299),(p+'ImmersiveMessagesManager.java',18,104),(p+'renderers/VanillaRenderer.java',20,110)],'辅助消息渲染库0信用，只有使用它的战斗文字整合链计1；固定源码并非依赖Jar兼容保证')
verify()
