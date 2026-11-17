# 鳄龟：低壳、伸颈与独立咬合

固定本地来源：AlexModGuy/AlexsMobs `09755dade2cfbdf14839e026d3af446f9d3ff843`。完整读取模型、431行实体、Renderer（含苔层内部类）及BottomFeederAIWander、SemiAquaticPathNavigator、AnimalAIFindWater；六份源码和两张原PNG逐字节核对既有固定Git树blob。不是下载标题研究，也没有执行上游Java。清单、原URL和读源范围见source-manifest.json。

## 身体整体如何成立

14节点、13父子边、13次box调用只用于结构复核。14×6×16低躯托住16×3×18壳体，四条扁而外展的肢体根部藏在壳缘之下；两条宽壳脊形成次轮廓，不是许多同等大小零件。颈→头→下颚逐级相连，头内另有同形内层，在render时缩到0.99；四肢没有膝肘链。

实际查看旧001构造器灰模卡，以及128×128主体PNG和苔层PNG。主体用大片深褐壳板与略浅的颈腹区区分材质，壳缝集中；苔图在透明底上选择性覆盖表面。灰模卡并非完整逐面贴图模型，更不是游戏画面。Renderer明确绑定主体图，内部MossLayer在同一parent model上以translucent苔图重画，alpha=min(1,0.15×clamp(Moss,0,10))。补足了旧卡仅按同名图匹配、未确认绑定的限制。

幼体整体0.25与头1.5来自模型render分支；Entity.getScale另返回幼体0.3，Renderer再读TurtleScale（小于0.01回退1）。这些并非一个统一倍率，不能把幼体、苔层和0.8～1出生变体分别算作参考，也不能据此臆定显示与碰撞尺寸严格相等。源模型的旧Blockbench/1.15导出注释不构成升级项目Forge的依据。

## 先张口，再前探；两个连续进度共同驱动

实体保存prevOpenMouthProgress/prevAttackProgress，各自每tick以1趋向0或5。LUNGE_FLAG驱动攻击进度；Waiting或“有攻击目标标志且未lunge”驱动张口进度。模型用Minecraft.getFrameTime插值，非本批飞鱼使用的ageInTicks-tickCount形式。

张口满值贡献颈-10°、头-35°、颚+65°与颚Y-1；前探满值把颈scale改为(0.75,0.75,3.5)，头Z再前移7.25，并叠头+10°/颚-10°。下颚原始-0.2182弧度仍存在。progressPositionPrev(neck,snap,0,0,0,5)请求的位移为零，实际伸颈来自scale与头部位移，不能把这个零偏移调用当成功能。

四肢以侧向swing和前后/左右相位变化行走，水内速度0.5、陆地1；尾部叠idle与步态，颈头另有小幅摆动。模型没有专门攻击或死亡分支关掉全部步态，也没有足底IK。因此可学习壳、颈、口的层级，不可宣称它已证明重型构装抬落时的四足接地。

命中语义必须单独看：doHurtTarget仅return true。实体tick在attackProgress==4、目标非空、自身活着、视线与距离<2.3时调用hurt，该段不包在后续server-only分支内，也无“只在上升沿”或LUNGE条件。进度上升、回落均可能经过4，说明有再次检查机会；原生伤害免疫、客户端目标可见性等尚未运行，不等于已证明两次成功扣血。达到5时反复设biteTick5并在同tick递减，服务器在biteTick非零时清标志，模型再逐渐恢复。不能移植为赑屃的伤害时钟。

Waiting由服务器等待/追击关系控制，负chaseTime会使getTarget等访问器返回null。BottomFeeder在canUse/canContinue检查shouldStopMoving；FindWater负责离水找水；SemiAquatic导航使用AmphibiousNodeEvaluator，而本实体匿名子类把稳定目的地条件改为流体为空。未重新读完原版MeleeAttack、AnimalAILeaveWater、NearestTarget和全部父类，不称为整个AI/停速链闭环。水内travel有真实move、0.4阻尼/下沉或jump上升，不是模型前探产生了真实冲刺。

自有NBT保存Waiting、MossLevel、TurtleScale、MossTime、WaitTime、WaitTime2；未保存lunge/target标志、两个进度、biteTick和chaseTime。不把字段存在等同于重载后攻击连续。剪苔和出生代码虽随完整实体读过，仅为上下文，不计新程序/物件参考，不制作对应物品。

## 赑屃现有输入与仍未闭合的检查

目标为cod1§27 `dynasty:juli_bixi_kuilei`。它已有认可美术与制作记录，cod1§0禁止重建现有30只。当前28骨骼，shell→neck_base→neck_tip→head→jaw关系完整；256×128声明和实际PNG一致。TemplateMobRenderer→TemplateMobModel与geo/animation/texture的blueprint/juli_bixi_kuilei路径核对一致。保持四足、负碑构装主题，不把生物苔层、幼体或另一套伸缩骨架搬进来。

完整读取BixiBehavior与BixiGameTests，复用已读TemplateMob、Renderer和动画绑定的相关段。18tick=0.9秒：颈根X8°，颈尖Z-3，颚闭合；32tick=1.6秒为重踏接触。这里的时间对应已确认，嘴部世界位置、实际接触扇区与伸颈连续性还没有通过矩阵回放/实机验证。源鳄龟的7.25像素伸颈或2.3距离不能拿来替换项目的现有范围和18tick接触。

stomp当前动画驱动shell、stele及四足位置，未在该clip给hip/piston独立通道。前足在1.6秒有补偿键，后足附近键位不同；需要按完整父子变换检验，不能凭“少通道”直接断言脱节。death则已有四hip反向折叠、足部抵消旋转和piston位置通道，并非上一批魔蜈只有root/head的情况。不能把两个目标的问题混为一谈。

本参考没有专属死亡跪伏clip，不能闭合赑屃四足承重/落地死亡门槛。BixiBehavior在32tick尝试既有场景残碑，该物件与结构保持原样，不在建模专岗制作；测试源码中的单次接触、阻墙和重载残碑只表示现有测试内容，本轮未运行，不能冒称当前通过。保留当前技能、碰撞、单实体、物件与时间轴。

## 记数与保护

旧v35与taoyan记录已接受同一物种的静态结构；本批加深整体动作/渲染/恢复覆盖，不当成另一只。一个整体候选，独立接受0、程序信用0，节点、进度、苔层、幼体与六份文件均不累加。全局适用1000的已接受总数/缺口仍null，交Main独立核实；四足死亡接地专项仍0/1000。10份目标输入只读保存并复核哈希；无生产修改、无Java/游戏、无清单/Jar/存档/声音/亮度/焦点操作。
