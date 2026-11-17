# RockyRoller 继承碰撞与退出补读

本批沿既有饕餮 `dynasty:taoyan_zhishi` RAM501研究断点补缺。只用已存固定本地材料，无下载、Java、游戏或生产修改。父批收据保持不变。

## 固定来源与实际阅读范围

Alex’s Mobs固定提交09755dade2cfbdf14839e026d3af446f9d3ff843复用父批实体465行、模型173行、控制器96行、NoTeleport包装31行，不算新身份或新机制信用。

Citadel为该固定项目build.gradle实际声明的文件5633260，SHA256 549596de295d90a84ee70625076087a9724dabca1de0567ef6ef03435aab7d5d。ZIP静态读取，不加载JVM。`ICustomCollisions.json`包含全部三个静态方法（getAllowedMovementForEntity字节码0..354；collideBoundingBox2 0..109；collideWithShapes2 0..194）及抽象canPassThrough声明。`CustomCollisionsBlockCollisions.json`完整读取两构造、getChunk、computeNext及桥接方法，关键computeNext 0..312。

`PathingStuckHandler.json`实际读构造、createStuckHandler、checkStuck、resetGlobalStuckTimers、completeStuckAction、tryUnstuck、chanceStuckLevel、resetStuckTimers八方法。未读的建筑/破坏辅助不冒称完整类审阅。`navigation-constructors.json`读四构造；`navigation-selected.json`读tick(m_7638_)0..616、moveToXYZ0..173、tryMoveToBlockPos0..22、moveTo(double...)0..33、getDesiredPos、onPathFinish；stop复用旧已审0..38。AbstractAdvancedPathNavigate、PathResult取消、原版Goal/Selector/WrappedGoal/PathNavigation已有证据复用，不重新计数。字节码位置不是Java行号；映射证据保存在mapping-anchors.json。

原版底座只作本地Forge47.4.10上下文，Entity.move完整612..740及collide/辅助888..929已读；不证明与参考47.1.65所有补丁等价。Goal.canContinueToUse默认回调canUse，stop为空；WrappedGoal有running保护并委托；GoalSelector清理阶段不受isInterruptable保护，继续条件失败也会stop。AIRollIdle不可打断只阻止优先级替换，不阻止其canContinue=false被清理。AIMelee翻滚后canUse=false，因此下一次清理调用其stop只清rollTimeout，不关闭翻滚本身，不清rollFromPos或速度。不能断言每实际游戏tick都清理；Mob调度频率未在本批重审。

## 允许位移的计算与真实碰撞分开

getAllowedMovementForEntity先读当前AABB、扩展扫掠区的其他实体碰撞；零向量可直接返回，否则合并候选。collideBoundingBox2保留实体碰撞，必要时加入世界边界，再加入CustomCollisionsBlockCollisions迭代的方块形状。迭代器取得状态及原生形状后，若实体是ICustomCollisions且canPassThrough为真则跳过该方块；RockyRoller自己的实现针对PointedDripstoneBlock，不是无视全部墙体。空区块候选跳过也不能据此声称运行场景已加载完整。

collideWithShapes2先限Y；再依水平向量绝对值，必要时先Z，再X，再剩余Z，逐轴移动临时AABB。step逻辑仅在有台阶高度、接地或向下被裁剪、且水平被裁剪时比较候选，以水平位移平方择优，再修正下落量。该辅助返回Vec3，自己不setPos、不更新horizontalCollision、不清ROLLING。

原版Entity.move以collide返回值更新位置，再比较原请求与结果设置碰撞标记，并把受阻水平速度分量置0；结尾仍有速度地面系数、方块回调等。原生move不是只有一个运动调用即成功的承诺。

**仍未闭合的重要调用入口：** 本地Forge底座的Entity.collide(Vec3)为private；RockyRoller定义同名public方法并不凭源码名称自动证明覆盖。Citadel本地AT不包含该Entity方法，Citadel mixin配置也没有EntityMixin。Alex’s Mobs固定build.gradle声明自身AT文件，但目前固定本地树未保存其AT内容，故不能判断最终转换后可见性与真实dispatch。完整辅助计算已读，不冒称其已接管原生碰撞，也不指认模组存在bug。后续需要确切固定Alex’s Mobs AT/转换后类，不能随便拿另一个版本来补。

## 导航停止与卡住恢复

AdvancedPathNavigate普通五参构造默认createStuckHandler().withTeleportSteps(6).withTeleportOnFullStuck()。但是NoTeleport包装明确走六参构造并传入新的未设置处理器；六参构造保存调用者参数，不追加默认传送。默认处理器teleportRange=0、canTeleportGoal=false、破坏/架梯/搭桥/自伤开关均false，初始延迟1200。故“不传送”有实际构造依据，而不是按类名猜测。

checkStuck若desiredPos为空或ZERO直接返回；距离目标<3重置计时。目标不变累积globalTimeout，超过max(2400,timePerBlockDistance*max(10,distance))执行completeStuckAction。路径空/完成、同一节点或缺乏进展可走tryUnstuck。默认行为先停止路径，再可能停路并请求向外退10格；传送、搭建、破坏分支有各自开关，不能看见这些方法就说当前实体会传送。level递增存在1/6回退2级，不能给它承诺固定几秒必脱困。

completeStuckAction末尾停止导航并重置计时；默认关闭其额外传送、自伤、破坏。stop取消PathResult、设CANCELLED并置null、清destination、调用父stop清path；**未在已读stop中清desiredPos、MoveControl旧操作或deltaMovement**。tick在路径计算未完成时可能提前返回，普通路径则会向MoveControl写wanted位置；在末尾才检查stuck，且坐下驯兽/stopTickingPathing有跳过条件。RockyRoller本身不是驯兽，也未实现IAdvancedPathingMob，但路径计算分支仍是条件。路径任务和地形求解内部未全读，不宣称能走到目标。

## 翻滚动作退出的最终条件表

- 正常超时：服务器关闭ROLLING、设置10..19冷却、counter=0、delta=ZERO；同tick尾部会再减冷却。
- 低速/死亡分支：counter>2且delta.lengthSqr<=0.02，或!alive，只关闭ROLLING，不走同一清速/冷却块。
- handleRoll先写本次rollDelta后才测试isMoving；因此即使某次引擎移动曾把受阻速度分量清0，本次handleRoll也可能重写水平速度，不能凭“有碰墙”断言低速退出必触发。super.tick内具体引擎顺序与真实碰墙结果未跑，保留条件观察。
- 地震与目标接触不是统一退出。目标接触把maxRollTime刷新为counter+10；地震独立冷却。
- 下一次非翻滚分支才重置counter与台阶；模型独立把rollProgress降到0，并用clientRoll收敛姿态。姿态恢复不是导航/世界位移已清理证明。尸体接地不在该机制范围，死亡参考新增0。

## 对已有饕餮动作的适用点与边界

RAM501服务端20..31tick逐步move并检查实际水平位移<0.98或非法地面后stop(45)。已有模型siege_piston在20tick收蓄、21tick冲出、32tick保持后回稳，服务器窗口与视觉进度必须分别核对。本批只留“受阻停止后，主体、支撑足和活塞是否回稳”检查点，不把RockyRoller整体翻滚移植过来，不改攻击/比例/武器。当前停止同步与模型重选已有父批材料；完整游戏回放未做，不能宣布运动中穿插或受力已通过。

## 去重与交付状态

继承帮助类和源码数量不增加生物参考数量；旧herschel025已覆盖实体链支持0，旧静态身份仍归原账。本批新增有效已验收=0、主岗验收=false、全局适用1000总数未知保留null。原始父批收据未覆盖，待办/主清单不动。新研究价值是补清辅助算法、默认导航开关和Goal清理语义，同时明确暴露原生碰撞挂接缺口，不是已完成新模型。
