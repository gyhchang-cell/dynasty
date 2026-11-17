# Sweep QA 02：独立审查修复与集中验收交接

2026-10-29。**本目录当前为02源码；旧reobf01不是当前版本。** 本岗未开游戏、未打SRG Jar、未改正式Java、共享Jar、专业资产或主清单。10份旧源码变为**11份源码/11个QA class**，新增核心 `com.dynasty.sweepqa.CaseLog`；仍为7个Mixin，配置包保留为 `.mixin`，CaseLog不在保留包里。正式FangtianSweep修复仍是已交付的6增3删，不在本次修改范围。

## 审查问题闭环（源码/离线，非原生已验收）

- **QA-01 P1**：SERVER和CLIENT使用独立CaseLog，即使在集成JVM也不共用case变量或事件缓冲。客户端完整40tick窗口落盘后close，本地可开始下一唯一case；新case会换capture/binding并清空自身缓冲。服务器dump/clear只管服务器，不再承担清远端client的职责。采集结束后的事件不进入已封存窗口。两个独立JDK进程各执行18个生命周期断言，包括连续case、旧快照保留、迟到事件不污染、新case无旧事件、服务端关闭不影响client和拒绝ID复用；不是Forge/TCP验证。
- **QA-02**：每个事件和frame携带case、mode、fixture绑定nonce、capture、role、进程session、QA构建标签及**实际装载QA Jar字节SHA256**。SHA从Forge ModList给出的mod文件路径计算，不靠手填预期值。未打包目录标成UNPACKAGED，分析拒绝。服务器必须有攻击后20个连续、成对END before/after观测，after队列为空；空集合不能通过。客户端每一帧须观察到真正进入FangtianSweep和Cod3Vfx的HEAD/RETURN回调，即使ACTIVE为空也有hook记录，覆盖采集早期至40tick。负控还必须关联同视角、同服务器/客户端进程session、同QA包且发生在它之前的真实成功age1正控；分析器重新读原始正控，不能仅信旧analysis绿灯。
- **QA-03**：客户端攻击前必须导入该case**原始服务器fixture文件**，核对case、QA Jar、nonce（集成服当前绑定）、玩家UUID、主靶UUID/id/维度及攻击距离/原生满冷却。分析逐条核对所有事件/frame的身份，不仅计数：client player和server actor必须是fixture actor，client/server攻击必须是fixture第一只靶，成功回执main也必须是它，取消伤害的owner/direct/target须匹配。无敌case核对fixture及最终无敌标记和两靶零生命下降。错打外部无敌实体不再能机械通过。
- 补强旧mesh关联：AfterImages.render的实际packet上下文关联到其weapon绘制入口，保存真实actor身份、sequence/entity/dimension/start/seed/template，分析要求与实际mesh_weapon收包匹配、处于相应生命期、与专用月牙同帧。**调用入口仍不是GPU可见性证明**，原帧人工审核保留。
- 每个case必须传入预期 `--view`，实际frame相机必须全部匹配。全矩阵的两视角/六负控合并仍由协调核对下表，不能把两个文件名当两个视角。

## 离线证据和旧记录

- 新Java编译：`docs/cod4/audit-20261022/sweep-native-acceptance/offline-compile02.json`，javac17真实冻结Forge47.4.10/Minecraft1.20.1依赖，11class。`compile.py`不执行Gradle或游戏，输出全在本目录.work；旧 `offline-compile.json`、原00:34失败目录、全部旧work和协调 `coordinator-reobf01.json` 不覆盖。
- `checks/verify_offline.py` 只加载JDK CaseLog及**明确标记SYNTHETIC-NOT-NATIVE**的合成JSON，验证空探针/单边或断档END、错玩家/错靶/错维度/旧case/旧绑定、错误相机/进程/QA包、断线/短窗口、错误取消来源、正控缺hook/重复cue/age0/错误mesh关联等反例均拒绝。见 `offline-checks02.json`。合成文件不是实际像素图片，不能作为正控或原生证据。
- 本轮增加反例时的一次失败保留在 `.work/checks02-20261029-011134-121029/`：原合成mesh对象被收包/绘制共用，修改start同时改了两侧；已拆开，并新增mesh实际frame生命期校验。此失败不隐去、不算游戏缺陷；最终结果见新收据。
- 完整源/class/资源/脚本哈希及逐问题闭环见 `review-closure02.json`。旧01 Jar SHA `e2bdbec6fea55c46da69823e7ea6f9237aa18eb1d6d87a3ae66f8ff627a5af32` 仅历史，不能给02背书。

## 协调私有02构建

在协调自己的**冻结Forge工程、独立GRADLE_USER_HOME和全新输出**使用本目录 `qa.init.gradle` 的 `reobfSweepNativeAcceptanceJar`，明确：

- `-Ddynasty.sweepqa.build=<全新私有输出>`
- `-Ddynasty.sweepqa.baseline=<已统一编译的正式class目录>`
- `-Ddynasty.sweepqa.sources=<本目录绝对路径>`

QA Jar版本2.0，只含11个QA类及本目录resources，不含正式class/资产；manifest为 `MixinConfigs: sweep-native-qa.mixins.json`。不得把旧01或开发映射class直接注入当前生产包。正式4个SRG修复类与当前整包的精确集成仍由协调处理。本岗没有生成/覆盖任何Jar。

**仍待02 SRG及Mixin运行验证**：javac -proc:none不验证Inject/Shadow，旧01 reobf也不验证新02；新增AfterImages.render的HEAD/RETURN也须实际装载验证。defaultRequire=1只在Mixin配置确实装载时生效，需保留启动错误日志、mods表、运行包及QA Jar SHA。runtime fixture中的artifact必须等于本次02 QA Jar字节SHA。

仅协调计划的私有进程可装。每个服务器/集成服或客户端使用自身真实目录及独立output：

`-Ddynasty.sweepqa.enabled=true -Ddynasty.sweepqa.instance=<该进程私有实例绝对目录> -Ddynasty.sweepqa.output=<该进程独立绝对证据目录>`

服务器世界根必须在该instance下；客户端gameDirectory完全匹配。不要与旧dynastyweaponqa自动驱动一起装载。此工具无自动建世界/连接/退出/抢焦点/screen/GLFW操作；只在显式命令后放工具靶/换测试主手/发动原生攻击。

## 一次集中会话阶段

1. 协调确认私有整合包含精确正式修复和02 QA，场地平坦无遮挡、没有其他战斗。真实操作者为生存、具备原生武器使用条件；记录原能力/衣甲/副手。工具不修改玩家生命/原生伤害系数/冷却/时间，也不直接调hurt、begin/finish/tick或伪造cue。
2. 服务端OP `/sweepqa arm <唯一case> <mode>`，mode为 `success|cancel-attack|cancel-damage|invulnerable`。仅创建本工具两只无AI中立牛，前方2.1格、侧向1.1格；提高**靶**生命上限并给操作者方天主手。负控只取消本actor对这两靶的对应事件，或只使这两靶无敌。旧case须先dump/clear，不能直接覆盖。
3. **远端新增必需步骤**：把服务器原始 `<case>-fixture.json` 逐字节复制到攻击客户端output（已有观察客户端也复制）。不重排/改写JSON。集成服若同output已存在不必复制。它含服务器身份和新nonce；每次新case都重新复制，不能复用上次fixture。客户端必须等实体追踪/属性同步/满原生冷却。
4. 攻击客户端 `/sweepqa-client <同case> <主靶ID> first|third`。检查fixture后仅调用真实 `MultiPlayerGameMode.attack` + MAIN_HAND swing；40客户端tick收集实际收包/几何/原帧对，恢复原相机、落盘并close。服务器和客户端事件现在分别为 `-server-events.json`、`-client-events.json`，不会混写缓冲。之后服务端dump、clear；只discard本工具靶，不能操作用户实例。
5. 第一、第三人称各取得真实age=1成功case。要求produced=n、consumer now=n+1，captured level/actor/main匹配，实际生命下降、一次专用S2C且start=consumer now，END后queue为空，后续20连续服务端周期观测仍完整；专用几何与旧方天mesh同帧。**不把age0成功当4991→4992覆盖**。不改gameTime/回执去造边界。每视角自然重试最多6次，新case、新fixture、等待原生冷却；不额外开实例。到上限未覆盖就报告未覆盖，不能放宽。
6. 再做三种负控各first/third。须有真实C2S/server攻击且身份正确，取消模式实际取消、无敌模式实际无敌、最终两靶HP不降，专用cue/几何为零，探针/周期覆盖完整，并引用该视角的前序成功校准。其他原生反馈是否出现逐项解释，不能要求所有视觉归零。
7. 在每个case完成、server clear后，将**服务器原始fixture/server-events**复制到对应攻击者分析目录；保留原始SHA。只读分析（写新analysis02收据）示例：

   `python3 tools/cod4/sweep-native-acceptance/analyze.py <攻击者output> sweep-first-ok --mode success --view first`

   `python3 tools/cod4/sweep-native-acceptance/analyze.py <同output> sweep-first-cancel --mode cancel-attack --view first --calibration sweep-first-ok`

   第三人称必须引用第三人称正控。负控不传校准、校准原始证据缺失/不合格、进程session/QA包不同或正控晚于负控，均失败。正控和负控需在**同一02装载会话**中完成；重启客户端或服务器后重新正控。不能用本目录合成数据或旧01记录当校准。输出 `MECHANICAL_PASS_VISUAL_PENDING` 也固定 `overall_acceptance=false`。
8. 协调核对矩阵，每格不同case且对应实际相机：

| mode | FIRST_PERSON | THIRD_PERSON_BACK |
|---|---|---|
| success，真实age1 | 待验/正控ID | 待验/正控ID |
| cancel-attack | 待验/first校准ID | 待验/third校准ID |
| cancel-damage | 待验/first校准ID | 待验/third校准ID |
| invulnerable | 待验/first校准ID | 待验/third校准ID |

9. 原始PNG、renderer实际draw前后帧对、投影/模型矩阵、深度混合状态及全部实际sequence保留。人工检查月牙弧形/朝向、第一人称近裁剪、第三人称尺寸、遮挡深度、旧残影可见及其他原生VFX组合没有被替换/遮挡/大白块；写具体帧号和理由。wire HEAD只是handler入口，weapon HEAD只是绘制入口；非零像素、method call或同帧调用都不自动证明可见构图正确。
10. 可用**已安排的真实第二客户端** `/sweepqa-watch <case> first|third`，先复制fixture、先启动watch、再攻击。watch不攻击，不能冒充攻击者运行上述分析（它缺actor攻击记录）；须由协调将实际packet/actor/dim/start与攻击者证据关联并人工审帧。无需新增实例；不以FakePlayer充数。客户端每次40tick后本地close可接下一case，不受服务器clear影响。

最后只清本工具靶和私有QA装载，保留全部结果。最多18条case（12次成功探索上限+6负控），关键证据足额即可停。任何采集失败或probe-error保留，先修工具再继续；禁止把未验完条目删掉。本岗不运行该会话，不碰共享Jar/用户存档，不重跑套装护卫。
