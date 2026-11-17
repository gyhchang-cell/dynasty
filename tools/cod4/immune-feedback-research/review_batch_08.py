from ledger import record,verify,B
r='lender544/new1.20.1';p='src/main/java/com/github/L_Ender/cataclysm/'
record('cataclysm-harbinger-rejection-after-emp-transition',r,[(p+'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java',190,200),(p+'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java',214,246),(p+'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java',275,437),(p+'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java',810,817),(p+'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java',836,838),(p+'entity/AnimationMonster/LLibrary_Monster.java',57,81),(p+'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',73,137)],
 '完整hurt：同类来源拒绝→idleHeadUpdates/destroyBlocksTick副作用→EMP可先sendAnimationMessage(STUN)→半血powered箭矢拒绝→deactivateProgress普通来源拒绝→共享Boss hurt。完整aiStep追踪激活标志造成40tick进度及递减、STUN15tick声音和客户端烟粒子；getter/synced字段及动画字段辅助已读。',
 '半血以health<=max/2定义，不是统一无敌态；EMP动作改变发生在后续箭矢/未激活拒绝前，所以hurt=false不能推出“没有动作/状态变化”。STUN音效由后续animationTick==15决定，客户端烟粒子是STUN态，不是专门免疫文本；本链无浮字和逐目标文本节流。',
 '专门研究“权威拒绝与已有副作用的顺序”：未来语义接入不能把任何false都翻译为Boss纹丝不动，也不能重复触发已有受控动作。普通玩家体质独立。',
 '不把每个伤害来源/半血阈值拆条；此条独立于已计共享伤害桶，新增的是EMP先变动作后拒绝的本体决策。动画网络由lionfishapi契约承担，未研究库内部，不计库，不声称像素/同步已验。','immunity_rejection_semantics')
q=p+'entity/AnimationMonster/BossMonsters/Ignis_Entity.java'
record('cataclysm-ignis-counterstrike-refusal-receipt',r,[(q,287,393),(q,396,408),(q,435,510),(q,2602,2626),(p+'entity/etc/Animation_Monsters.java',97,99),(p+'entity/AnimationMonster/LLibrary_Monster.java',57,81),(p+'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',73,137)],
 '完整Ignis.hurt/canBlockDamageSource及自有状态getter/Crackiness.byFraction：被攻击时可能进入COUNTER；已在反击有效窗口则广播STRIKE并播BLAZE_HURT后非bypass拒绝。反射深渊火球增加盾损；Boss阶段/自身火球/方向盾各有拒绝；半血阶段阈值另有减伤；最终super成功且裂度改变才播破甲音。',
 'COUNTER窗口>16<=46，破盾COUNTER>8<=38；动作与声音在bypass判断前发生，不能把声响当伤害已被拒绝证据。反射火球例外由directEntity类型与owner联合判断。方向盾源位置水平向量dot<0且!BYPASSES_SHIELD；反击分支不同于方向盾。阶段半伤不是免疫；外观裂度改变是成功受伤回执。无独立免疫浮字。',
 '专门研究带原生反击回执的拒绝：结果文字不得覆盖或重复已生产的反击/破甲语义；伤害owner、direct entity与绕盾标签要分别记录。与普通前盾模板重合部分不另计，只为整条counter/reflected-source权威链计1。',
 '父类原版hurtCurrentlyUsedShield/blockUsingShield以及外部动画分发止于平台/库接口；不声称Boss动画资产或画面合格。此链可发生动作，作为设计反例而非照搬COD4“纹丝不动”。','immunity_rejection_semantics')
repo='sam-makes-stuff/simple_combat_indicators';p='src/main/java/net/sam/simple_combat_indicators/'
root=B/'sources'/repo.replace('/','__')
rels=['SimpleCombatIndicators.java','networking/ModPackets.java','networking/packets/S2CAttackedPacket.java','networking/ClientPacketHandler.java','util/DamageHandler.java','util/DamageDealtIndicator.java','render/DamageIndicatorRenderer.java','render/CustomHudRenderer.java','util/ConfigUtils.java','config/ClientConfig.java']
record('simplecombat-server-hit-to-projected-hud-text',repo,[(p+x,1,len((root/(p+x)).read_text().splitlines())) for x in rels],
 '构造器注册Forge DamageHandler；LivingDamageEvent服务端且有source.entity→ModPackets按目标chunk追踪玩家发送attackerId/receiverId/damage→包enqueueWork→客户端仅当地玩家是攻击者时生成数字→同目标对象可替换旧记录并累加damage→DamageDealtIndicator出生点/动画→RenderGuiEvent.Post→worldToScreen相机投影→GuiGraphics.drawString。注册/codec/处理/构造/tick/完整投影绘制与config初始化方法均已读；包装和显示模式合并1条。',
 '这是原生服务端伤害事件而非HP差推断，但没有独立拒控结果；无source.entity环境伤害直接不发。发送范围为目标chunk追踪列表，接收端再按攻击者ID筛选；不是广播给所有旁观者的文字。对象身份合并只在旧记录仍存活时有效，无事件序号去重/硬cap。出生位置是目标半高快照，投影只剔除w<=0，没有射线遮挡；GUI文字不具有世界深度遮挡。age在每次GUI渲染用partialTick差增加，跨多个tick只见分数环绕，低帧率实际时长不能据配置30tick保证；GUI不渲染时也不在独立tick回收。未见显式world/epoch清空或空player保护。isKill以收到时damage>=client target.health推断，不能当权威击杀结论。',
 '同一场景可对比世界绘字和屏幕投影绘字；拒控字不能复用damage事件当唯一来源。目标关联、网络接收范围、时间与可见性应各自有可审查证据，不把配置tick和实际tick回收混为一谈。',
 '源码静态参考，不启动游戏、不证明低帧率故障或实际穿墙截图；伤害方向图标链只随全文阅读，未单独计数。与已有粒子链不同之处为服务器事件+攻击者筛选+目标对象合并+HUD投影/渲染时钟这一完整实现；不是绘字包装多计。','floating_combat_text')
verify()
