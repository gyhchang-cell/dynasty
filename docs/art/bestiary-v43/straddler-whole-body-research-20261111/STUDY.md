# Straddler 完整身体设计补读

只用现存固定本地源。模型、实体、AI、Renderer四份全文已读，哈希分别核对旧固定提交09755dade2cfbdf14839e026d3af446f9d3ff843的模型记录、chain-source-pins及immune sources清单；无重新下载。源全文与完整行范围见sources、source-manifest.json、line-anchors.json。实体/AI程序链已有sweep062，复读只补身体上下文，信用仍0。

## 完整体块、层级与枢轴

9节点、8父子连接、8个box调用，128×128图集。root(0,24,0)→body(0,-14,0)。主体28×11×14，双腿枢轴(±7,-0.5,0)，腿6×15×6；上方两结构枢轴(±9.5,-12,-4)，各6×18×10，独立带末端薄片。body还带中央薄片，三个薄片为零厚度、依赖图集透明轮廓。完整几何及枢轴原文保存在body-graph.json。

这是一只双足、宽主体、没有普通头手胸腰骨盆的非人形生物，不是普通Steve，也不是四足。旧卡片底栏“Quadruped”描述不对，本批已纠正观察但未改原卡片/旧收据。旧“上躯开口”不能泛化为主体有空腔：主身明确是实心大Cuboid，开口在上方两结构之间。不能用灰图宣布透明边缘最终外观成立。

## 从入口到回稳

射击Goal检查target非空和shouldShoot；shouldShoot在此实现恒true，不是实际查持弓。连续可见且距离够近20次检查后停导航并横移，其他情况追踪目标；看见目标且当前不是LAUNCH就setAnimation。attackTime只赋值，未见递减/触发读取；animationCooldown只递减无实际设置；不能按字段名宣称冷却有效。

动画长度30，与5蓄势+5保持+10加载+5反冲+5恢复一致。body蓄势X=-5°，双腿各+5°；两侧结构向外展10°并牵动末端片。10..20tick加载再向后俯30°。20..25tick躯干前俯25°、腿-25°，两侧结构俯20°且Y偏移2.4，薄片大幅回甩；25..30tick reset到空增量。所有角度是默认姿态上的增量，不能当世界角度；腿反向补偿只是局部X抵消，不是足底固定IK。

实体自身tick在动画20且活着、当前目标非空时建立发射物，生成位置为实体X/eyeY/Z；后调用公共AnimationHandler推进计时。接触事件位于加载段结束、反冲段开始附近；实际帧采样还受客户端与partial tick影响。没有游戏回放，不宣称发射与模型绝对同步。

每帧先resetToDefaultPose，ModelAnimator生成增量，再叠加毛片呼吸、腿步态、主体摇动和俯仰。这里没有“发射时关闭所有走路叠加”分支。若无乘客，以0.5*headPitch加到body，再从两腿减去；netHeadYaw未在自身setupAnim中使用，不可说头部独立追踪。全身关注方向靠主体俯仰与实体朝向构成。Renderer整体再乘1.2。

## 恢复、打断与保存限制

正常结束复用已审Citadel5633260 equality结束分支，30tick回NO_ANIMATION；resetKeyframe恢复增量，不清服务器目标、导航或动作flags。Straddler.setAnimation只赋currentAnimation，不重置animationTick。AI stop清aggressive、seeTime、attackTime并stopUsingItem，不撤LAUNCH，不明确停导航，也不清横移方向/strafingTime。目标消失后动画可能继续至结束；20tick无目标则不发射，但目标重新存在可能在事件帧使用当前目标，不保存最初目标身份。没有私有伤害打断分支，不编造被打必撤动作。

NBT只保存StradpoleCount，没有保存本次动画及tick。自身没有专用死亡动画、倒地侧卧或尸体接地恢复；普通落地/熔岩浮起不算死亡接触。floatStrider及travel已读：有效AI在水/熔岩moveRelative并move，速度有0.9阻尼、发射减速、熔岩额外减速；浅熔岩和表面条件可设onGround，深处可改竖速。这里只是自身运动条件，不是身体脚底已通过地形验收。原版父tick/伤害/导航全部状态及新载入后瞬态未实机验证。

## 身体挂点接口

Renderer附加展示层只在LAUNCH整数tick7..19出现，先root.translateAndRotate再body.translateAndRotate，再加局部offset。back在tick7..15按(t-6)*0.05，16..19固定0.25，有分段变化，不能描成无缝单调轨迹。20tick该层消失，服务端发射事件由Entity独立计算。身体展示层与真实发射原点没有共享骨骼socket计算，不能凭画面接近声称永不脱节。

本批只读root/body变换接口，不读/改子体模型、物品、武器或挂件物件，留贴图专岗。没有把其他模组资产接入Dynasty。

## 对现有待办的具体适用点

对应现有饕餮之蚀OIL503的“宽主体蓄力→释放→回稳”，不是把它改成双足Straddler。现有oil4.8秒，两形态war_cauldron在1.2秒俯15°、1.8秒保持、2.8秒归0；下颚与油面有独立通道。既有支撑骨有密集补偿关键帧，不能因为主体俯仰就宣称腿未补偿；本批仅抽样身体/足/口通道，不冒称完整回放。服务器OIL24tick起作用，在地面前方创建油池，不是从骨骼口部发射；该玩法保持。可借鉴的是主体/足部受力和视觉释放阶段对齐检查，不复制骨架/投射玩法。

本体模型38/63骨、原ID、比例、已认可形态、动作时间轴及战斗逻辑均未改。target-readset记录只读输入，非生产验收。

## 门槛与差额

本批是同一旧静态Straddler身份的完整身体动作补读：whole设计候选1，新增独立已验收0，主岗尚未验收。不能把9节点、4文件、5阶段或20tick事件算多只参考。

适用身体设计门槛required=1000；历史适用whole-body去重已验收总数当前没有权威核定值，因此accepted_total=null、global_gap=null，不能编造1000已满或把旧静态参考总数当动画/身体全设计总数，也不能擅自把旧有效数量归零。四足死亡接触单独旧账accepted0/required1000/gap1000仍保留；本只双足发射设计对该窄门槛新增0。详见progress.json。全局差额仍需要主岗对既有适用收据核定，这不是模型完成。

固定源哈希和收据可验证，离线骨架/动作组织已读；没有原生贴图动画回放、游戏、Java、构建、碰撞验收或生产修改。既有专业资产和主清单未触碰。
