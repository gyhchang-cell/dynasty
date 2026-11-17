# D86：北极毛皮甲两通道穿戴绑定与UV补核

继续已有arctic_fur_leather同套，不新增设计信用。实际关闭的是本次固定源码中穿戴路径与染色/固定层选择的静态问题，不是游戏外观、真实染色或用户模组二进制验收。1000已验适用总数和缺口仍未知，制作门槛未满足；未覆盖资源、共享Jar、主清单或session。

## 来源与范围

官方TeamTwilight/twilightforest，固定提交1bc3a4c21213bc443967e92125613cb9ef47891e；commit→真实根树→33份选取文件逐份Git blob/SHA256验证。MC1.20.1、mod_version4.3、NeoForge47.1.70：gradle.properties与build.gradle有明确声明。版本不是本批凭用户Jar名字推断出来的。12张原始PNG（8图标层、4活跃穿戴层）均与旧研究哈希一致；这只证明所比图片相同，不证明整个4.3.2508用户Jar与此源码二进制一致。

本批面向布/皮/海蚕丝及锦缎甲的材料区、图标/穿戴一致性和多层判断研究，不证明项目某ID未做过且简陋；优先70的28ID没有新增重画资格。已认可和精致稿全部保护。全程只研究本岗材质/UV，没有改生物身体或行为。

## 实际看图

已查看12张原图的整数最近邻页，以及两通道168个原始UV矩形。4基础图标和4覆层分别展示，不合成默认游戏外观。褐色短胸、直腿和横脚面属于皮革主面；白灰肩毛、锯齿下摆、裤腰毛沿和双靴毛筒来自第二图层。头盔有白灰内区、深脸口与帽边，不能把浅色主体删除成透明底。毛边靠阶梯缺口表达，不能改为柔光毛绒插画；皮甲大棕面配很少的深边即可，与毛口留出材料区别。

可染色穿戴层主要是白灰毛区：头壳、胸下摆/袖口、腰部尖下摆、靴筒。固定覆层主要是棕皮衣胸、长裤腿和脚尖；兜帽四条小立体边的24面只有固定覆层有像素，可染色层24面全透明。hat外层固定通道六面透明；染色通道NORTH原矩形只有2个极低Alpha像素（46,15为22；47,15为3），其余五面透明，不能把整层说成全透明。补充单面放大页核看这两个像素，但不据此判断游戏瑕疵。不能见一个图集的透明片就判漏贴，也不能将两图层分别当成两套。原生arcticarmor_1.png/_2.png不被此getArmorTexture分支引用，本批没有下载或看这两个非活跃候选。

## 实际消费者

完整阅读ArcticArmorItem、ArcticArmorModel、TFArmorModel。TFItems132–135注册四原生ID与实际类型，材料为TwilightArmorMaterial.ARMOR_ARCTIC；其58–63声明毛皮修复材料。initializeClient→ArmorRender.INSTANCE→按LEGS选择INNER，其余OUTER→new TFArmorModel(bakeLayer)。TFLayerDefinitions客户端MOD事件注册两层，均64×32，分别INNER .5和OUTER1膨胀。ArcticArmorModel继承HumanoidModel.createMesh并加4小hood条，不是HumanoidArmorModel.createBodyLayer，所以本次腿块没有错误套用-0.1膨胀修正。TFArmorModel普通实体走super.setupAnim，盔甲架有单独姿态设置；只读未运行。

getArmorTexture按LEGS→arcticarmor_2，其余→arcticarmor_1；layer参数null选择_dyed，非null选择_overlay。TwilightForestMod.ARMOR_DIR明确twilightforest:textures/armor/。getColor(stack)默认0xBDCFD9或NBT display.color；getColor(stack,type)在type0返回白，其他返回该染色值。ColorHandler401–405明确注册四物品颜色回调，因此物品layer0固定、layer1染色，和穿戴的基础染色通道/固定overlay语义要分开。

本批取到官方NeoForge47.1.70源码归档，服务器SHA1核对通过，读取HumanoidArmorLayer整份补丁：DyeableLeatherItem路径先以getColor颜色渲染null通道，再白色渲染overlay通道；ForgeHooksClient259–263调用物品getArmorTexture，320–338通过IClientItemExtensions并复制根姿态/可见性。精确版本源码的两通道调用链已经读通，但事件实际执行、已加载模型和着色结果未实测。无需把同名net.minecraftforge包误认为本批声明使用旧Forge版本。

四item JSON及4原生配方完整阅读。配方使用twilightforest:arctic_fur标签，材料本源/标签解析/实际付款合成未测。每件10个trim状态只读基础模型引用，不查看变体PNG、不计额外设计。

## 逐面UV与未验

14个分槽方块实例（HEAD6、CHEST3、LEGS3、FEET2），84个名义面分别在染色和固定两通道提取，共168个原图矩形，全部在64×32内。体块名义大小、原点、镜像、父局部位置、膨胀和有符号UP V保留。4hood分别1×4×1或4×1×1、独立0.5膨胀并接在头节点，不是另外4设计。UV算式/基础人体几何使用同MC1.20.1 Forge47.4.10映射源码作上下文，不冒充Neo47.1.70已加载Minecraft类。裁片未模拟最终顶点绕序、镜像朝向、接缝或动画。

实际读旧arctic_fur_leather观察、20261101层绑定与手动复核记录；本批不重复旧图标覆层遗漏的已解决结论，只将其穿戴源分支/UV问题收窄。12原PNG字节相同不等于新案例；当前已验信用0、待独立审查。真实五视角、黑剪影、默认色/自定义色运行、衣料接缝与动作仍待验，不删提示词。保护289与优先70哈希前后及当前一致，没有启动Java、游戏或改变声音亮度焦点。
