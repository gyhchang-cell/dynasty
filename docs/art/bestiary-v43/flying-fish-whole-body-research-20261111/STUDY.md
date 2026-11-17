# FlyingFish：窄躯、展鳍与环境状态过渡

这是与Tusklin四足支撑、Straddler发射姿态不同的完整身体实现研究。固定来源AlexModGuy/AlexsMobs `09755dade2cfbdf14839e026d3af446f9d3ff843`，完整阅读ModelFlyingFish、EntityFlyingFish、RenderFlyingFish及三份移动辅助源码。六份源码与三张原始PNG均按既有固定Git树的blob内容核对，未联网补取、未执行外部代码。实际阅读范围、URL、摘要及树依据见source-manifest.json和pin-evidence.json。

## 完整身体与真实原图

模型8节点、7父子边、9次addBox；只表示拓扑，不作参考数量。3×4×8窄躯加前方3×3×1口鼻，后接2×3×8尾段；尾鳍和腹鳍跟随尾段，胸鳍接躯干。头不是一个独立方头，也没有人为加上人类脖子。胸鳍每侧13×0×5，尾鳍0×8×9，借大面积薄片与透明像素建立轮廓，不靠排列许多细碎方块。

已看原始64×64 RGBA的flying_fish_0、1、2.png：共用浅腹、蓝色鳍区与整体像素组织，背部局部色相有区别；只记录原尺寸下可辨认的大区关系，不冒称逐个像素手工研究。三个配色变体不算三只生物。另看了旧AlexsMobs灰模卡；它明确是bind pose、没有纹理遮罩或动作，不能把灰色矩形鳍误认为最终有贴图的轮廓。没有查看同名betteranimalsplus模型，不混淆项目。

RenderFlyingFish明确variant0/1/2分别绑定三张PNG，异常值回退0；同一模型整体scale0.8，shadow0.2。没有不同变体的第二副骨架。未研究桶物品、靴子或任何手持资产。

## 连续状态，不是五段攻击的另一版

ModelFlyingFish没有ModelAnimator或攻击关键帧。每次setupAnim重置默认姿态，再按实体插值状态展开胸鳍、腹鳍；flyProgress为0～5，swimProgress=max(0,5-flyProgress)×0.2。两种尾摆权重随过渡反向变化，而非突然停掉旧摆尾。body→tail→tail_fin链同时有轻微idle、游动与较弱滑翔chainSwing；四鳍保留不同强度的flap。

onLandProgress独立由“离开水/气泡且onGround”趋向0或5；模型在该进度下绕Z侧转到-90°并调整胸鳍。它与flyProgress可在过渡期间重叠，不是互斥枚举。不能把这个活鱼离水侧躺当死亡动画，也不能拿它证明八段脊柱的柔性求解。

EntityFlyingFish每个自身tick先保存prev进度，再改变当前进度。滑翔离水下降时把Y速度减半；姿态目标由Y速度生成，滑翔状态反转其符号，rotlerp单次最大9°。模型再把headPitch施加到body；它没有独立头骨。因此身体俯仰来自实体方向、模型局部旋转和摆尾叠加，不能只截图默认灰模解释运动。

水内travel执行真实move和阻尼(0.9,0.6,0.9)，无目标追加微小下沉；其余情况走父类travel。活鱼离水着地有概率flop。isFlying恒true只是接口返回，不能据此声称恒定滑翔或悬浮。死亡声、伤害声不是死亡动作；本体没有专属死亡收束clip。

## 起跳、落水与退出限制

Entity内部GlideGoal完整阅读：TryFindWater优先级1、Glide2、Panic3、随机游动4。寻找水面与下一水面上方目标后缓存surface/glide。canContinue依赖两个缓存与“未着地或在水/气泡”，不以GLIDING为条件。start为空；stop清两个点，设150～224tick冷却并置GLIDINGfalse，未明确清导航或delta。

本批不复制其实现，下列字面边界必须保留：

* 移动末尾给Z分量加的是target.y，不是target.z。两个水面点通常同Y，不能把这段直接当作可靠水平指向算法。未实机重现轨迹，不声称已验证上游缺陷。
* 已滑翔且入水的最终else分支会调用stop，随后仍写velocity、角度并无条件setGliding(true)。直接调用Goal.stop不等于调度器当即退出；共享原版Goal生命周期沿用此前阅读。下次何时被调度清理未执行验证。
* 接近水面前的另一个分支也可直接stop；不能把一次flag变化描述成完整物理恢复。

AquaticMoveController完整阅读：MOVE_TO且导航未结束才设速度、修正朝向与垂直速度；水中另加微小浮力。没有“停导航就速度归零”的保证。AnimalAIRandomSwimming完整阅读：选点、限制区返回、水面尝试与submerged调整负责目的地，不是骨骼驱动；目标筛选也不等于已经到达。SwimmerJumpPathNavigator完整阅读：SwimNodeEvaluator允许跳出水，路径推进、前向直达剪枝和超时检查负责导航；stop沿用父类，不能宣称完整清零运动。三者均为本生物的支撑阅读，不拆成三项参考。原版TryFindWater/Panic与完整父类水生生物未在本批展开，保留边界。

实体NBT与桶标签保存FromBucket/Variant及原版桶基础数据；GLIDING、flyProgress、onLandProgress和glideIn不在自有保存字段中。这里只确认自有读写范围，不声称重载完整恢复滑翔，也不另算迁移参考。

## 绑定现有未完验收，不制造新制作目标

cod1§25为`dynasty:xueju_mangguyu`。cod1§0已明确30只基础怪不重新建模；registered-art-continuation记录也确认其美术已有制作。本批没有把“整项待验”说成“模型没做”，只为尚未独立闭环的运动/身体验收补参考。

当前注册包围盒1.2×1.3，TemplateMobRenderer→TemplateMobModel→blueprint/xueju_mangguyu的geo、animation、PNG三者路径一致；声明图集256×64与实际RGB PNG一致。模型已有spine_0～7串联、独立左右鳍尖和尾尖，共28骨骼。TemplateMob为其设置FlyingPathNavigation、FlyingMoveControl及无重力；这是一只空气浮游灵鱼，不是上游会干涸的水生飞鱼。

可借鉴“薄鳍根部跟随主体、鳍尖另有延迟、摆尾强度与实际运动匹配”，不可导入上游干涸、出水跳跃、桶物品或突然侧躺逻辑。当前secondary gear列表对BLIND_FISH返回NO_GEAR；这不等于没有既有鳍动画，也不能冒称已有布料动力学。保留现有主体结构。

选读现有动作：attack在0.8秒尾鳍yaw35°、spine_7 yaw29°，与FISH_TAIL16tick相同时间；resonance在1.5秒下颚42°、头段-10°，与FISH_RESONANCE30tick相同时间。它们仅在时间上对应，不代表已核验尾部空间、攻击方向与真实受击点。death为2.2秒，已有侧转与密集位移；Renderer按44tick衰减alpha，die恢复重力。普通发光鳍与半透明渲染需与默认光照分开判断；未执行死亡全过程、矩阵接触求值或双人观察者重连。

BlindFishGameTests现有源码包含甩尾一次接触、共鸣有限区域、重载/墙体取消及真实飞行阻墙等测试。本批只读，未运行，不能把测试存在或历史记录说成当前通过。原规范“无视地形碰撞”与当前物理阻墙测试有不同方向，维持当前实现，不借研究擅改noPhysics或AI。

## 数量与交付边界

旧reference-ledger已记AlexsMobs:FlyingFish静态结构。本批补足身体状态、原始贴图绑定与动作关系，不新增物种信用；独立接受0、程序信用0。全局适用完整参考总数及缺口仍null，等待Main核实；死亡地面接触专项仍0/1000。没有修改生产资产、Java、共享Jar、外部提示词或主清单，没有启动Java/游戏，没有改声音、亮度、焦点或用户存档。
