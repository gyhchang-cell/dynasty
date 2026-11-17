# RockyRoller 身体动作组织补读（支持材料，未晋级）

目标仅为已有 `dynasty:taoyan_zhishi` RAM501 的身体受力与退出检查。固定 Alex’s Mobs 09755dade2cfbdf14839e026d3af446f9d3ff843；5份源码经 TLS curl 重新获取并保存哈希。参考目录不是独立 Git 工作树，不能把向上找到的 Dynasty HEAD 当参考提交。Renderer 原先本地缺失，本次补得固定版本。

## 实际阅读

完整 EntityRockyRoller 465行、ModelRockyRoller 173行、RenderRockyRoller 26行、MovementControllerCustomCollisions 96行、AdvancedPathNavigateNoTeleport 31行。重新查看旧卡片 `build/bestiary-v43/taoyan-reference-more/004-AlexModGuy__AlexsMobs-RockyRoller.png`：左侧灰色源码体块，右侧原图集，不能当完整逐面贴图预览或游戏截图。

## 身体与动作

14节点、13父子连接，19次addBox。主体18×16×20，头小、四肢短，尖刺大量通过带透明贴图的零厚度平面实现。不能把灰卡片上的大片矩形当成游戏里的真实刺轮廓。所有四肢、头尾附着body，body旋转同时改变全身方向。

入口：AIMelee仅目标活且未翻滚时可用；寻找可见起步位置，最多累积40次准备分支，然后朝目标调用rollFor(30..69)。AIRollIdle在地面、无活目标、无冷却、前下方为空时调用rollFor(30..59)，本身不持续执行。rollFor只设置时长、地震冷却、ROLLING，不主动重置rollCounter。

每tick先插值进度0..5，再处理翻滚。handleRoll首tick记录方向与水平速度并加0.27竖直速度；以后锁朝向并维持水平速度。目标接触可把maxRollTime刷新为当前counter+10，不应把它记成绝对固定持续时间。地震由水平碰撞、愤怒和冷却共同触发，不等于翻滚停止。

模型每帧resetToDefaultPose。rollProgress改变body高度，翻滚时body X旋转并保存clientRoll；退出时wrapDegrees保存角度后按剩余进度退回。这里并没有专门把四肢逐节卷入壳内的关键帧，不能称已读到“完整蜷曲骨架”。前肢步行姿态有walkProgress衰减，后腿walk/bob仍直接用limbSwingAmount；不能声称所有步态都在翻滚时关闭。头部视线仍叠加。Renderer优先ROLLING贴图，其次ANGRY，再普通贴图，视觉状态可比姿态进度更快切换。

## 退出和缺口

正常超时：ROLLING=false、冷却10..19、counter=0、速度ZERO。当前tick尾部还会递减冷却一次，不能笼统承诺完整10..19后续tick。受阻/死亡分支：counter>2且速度平方<=0.02，或已死亡，只关闭ROLLING；并不走相同清速度与冷却块。isMoving是速度判定，不是实际位移或明确碰墙证据。下一次非翻滚分支才重置counter和台阶高度。AIMelee.stop仅清rollTimeout，未清rollFromPos，也未显式navigation.stop或清速度。

自身collide委托Citadel ICustomCollisions；Navigator继承AdvancedPathNavigate，包含stuck handler。上述Citadel碰撞与导航父实现、原版Goal默认canContinue/stop调度尚未在本批完整核对，故不宣称原生完整退出闭环或实机行为。causeFallDamage的两参数方法是否原生调用未验证。这里没有尸体落地接触依据，不计死亡参考。

## 与现有待办的关系

饕餮RAM501：20..31tick移动，受阻或非法地面stop(45)，既有动画4.4秒。两形态模型分别38/63骨，118/153方块；RAM动画26/51骨通道，均无缺失目标骨。siege_piston在1.0秒位置14、1.05秒-4、1.6秒保持、2.6秒回0，主体war_cauldron当前RAM通道零变换。参考只用于后续检查“世界位移、主体受力、恢复”是否独立，不能由静态零通道断言整体战斗动画错误。未回放、未修改。现有注册、几何、比例、技能、伤害、碰撞和时间轴保持。

Renderer实际绑定_body PNG而非同名不带_body贴图，第二阶段前32tick沿用第一阶段_body。只核对路径，不绘制贴图或替贴图岗改物件。武器/挂件不在本批制作范围。

## 去重结论

旧creature-mc-v35及taoyan参考已经覆盖同一RockyRoller静态模型/图集，不新增身份。immune-feedback helpers/herschel-immune/batch-025已有整份实体、原生tick/roll/伤害支持0，本批服务器机制沿用支持0，不能借新目录加信用。新增阅读仅模型setupAnim、Renderer与模型/实体组织关联；仍是既有身份补充，不申请新的独立实现信用。

本批dedup-screen只实际扫描docs/art/bestiary-v43与docs/cod4的JSON/MD，并参照已有v35身份；不是全仓库所有账本已穷尽的证明。主岗全语义验收待进行。5文件数、骨骼数、姿态与帧均不是参考数。新增独立已验收=0；全局适用1000门槛总数未核定，保留null，不据此提前制作。

## 验证边界

源码和目标JSON静态检查，未启动Java/Gradle/游戏，未改共享Jar、提示词、主清单或生产资产；没有实机截图。不能把本批标记成完成模型或完成适用1000参考。
