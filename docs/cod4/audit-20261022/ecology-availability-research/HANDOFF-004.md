# 独立生态可达性研究：协议及首轮连续四批

研究仍未完成。已连续做四批，共9条已全文阅读并语义去重的实现链待独立审阅，正式认可0；另3条不完整候选明确0信用。不是9个物种/9个方法，也未继承横扫或其它1000信用。每条保留固定commit、完整方法excerpt/行范围、源文件SHA-256、Git blob及调用者/消费者、具体观察、借鉴范围、限制和去重理由。source-index-001.json汇集来源；文件数/支持方法数均不是参考数。下一编号EA-0010。

## 已审待评机制

| 批次 | 项目 | 单项机制与边界 |
| --- | --- | --- |
| 001 | EA-0001 | AlexsMobs雷暴时钟、失败概率、有限搜索到实际鲸实体加入；SPAWNER不是普通NATURAL。保存键大小写不一致、true/UUID不等于成功出生。 |
| 001 | EA-0002 | 同仓库种子选唯一栖地区块、噪声水柱与洞穴predicate、持久化搜索放弃；普通cap仍会先阻挡。 |
| 001 | EA-0003 | TwilightForest按valid start/组件索引/征服状态收集表，消费者仅在非空时替换；返回空不自动阻止biome默认表。 |
| 002 | EA-0004 | Ice_and_Fire自然巢穴的地形门/共享危险地点记录/实体植入；共享记录失败前写入、循环覆盖判断及static隔离限制。 |
| 002 | EA-0005 | 同仓库自然岛逐层寻支撑、空间条件植入有限群落；造地成功不保证出生。共享间距不重复计。 |
| 002 | EA-0006 | 同仓库双高度图的水下采样及实体副作用；feature最终false也不能反推无出生。 |
| 002 | EA-0007 | Mowzie共用自然predicate和biome条件交集；7物种/名单/参数合计1项。ServerLevelAccessor后cast ServerLevel等限制保留。 |
| 003 | EA-0008 | Cold Sweat带函数的SpawnerData→原生结果AND→偏移位置/真实piece条件；category schema被消费者固定CREATURE覆盖，不按声明推断实际类别。 |
| 004 | EA-0009 | Mowzie自然营地piece后处理有限植入、STRUCTURE provenance、home存档与自定义持久化；无一次性植入标记，不能称生命周期至多5–9个。 |

这些实现有些带缺陷，是借鉴及反例证据，不是推荐照抄，更不是本项目生态修复已获批准。不同Minecraft/Forge/NeoForge版本边界逐条注明；未编译、测试或运行上游。

## 已核对的当前项目事实

baseline-001.json与driver-readback-001.json直接核对runtime04冻结证据：850条gate日志组成283组完整scope，六个400tick周期全部global CREATURE关闭，数量67–83/原生cap10，local未评估。driver原始671行有43目标、61server attack guard、37death candidate；客户端69行有61原生攻击。这些不增加严格KILLED，原outcome严格确认为0。exit0与保存日志保留，但不改watchdog.native_save_verified=false，不冒称独立存档验收。

原24/30+9/10保持。空ruined_villages、ghost_sites只有ruined_battlefield保持，未认作荒村/义庄/鬼市。原static-creature-gaps是静态与历史运行基线，未把回调阳性改记自然出生，也未把在世实体/巢内NBT/普通category.persistent/实体requiresCustomPersistence混为同一计数。

## 可用于下一轮研究的判断，尚非修复方案

1. runtime04没有到达local/species选择，继续改变观察点或等待不能替代global门实际打开的证据；不再盲目清理/挂机。
2. 普通自然出生、独立遭遇spawner、结构植入是不同来源；不能借后两者给既有NATURAL验收加信用。
3. 栖地存在、自然场景存在、实体出生、严格死亡、原掉落UUID拾取是分开的链。解决共享cap也不会凭空补出缺少的专用场景。
4. 结构生态的来源、持久化、消失/回收和一次性植入边界值得继续查；不要为避开cap直接改类别/持久化、概率或原生cap。

## 精确断点及限制

candidates-001.json保留蚁丘生命周期、graveyard jigsaw入口、结构净空feature过滤三条0信用候选。分别还缺实际配置/绑定、Pool与资源、距离helper与真实placed feature消费。Quark的Zeta链与来源闭环尚未完成，不计；Frostmaw空marker方法不能证明模板有实体。下一轮从这些断点与新语义来源继续，不重复包装共享支持链。

仅一次固定GitHub页面请求返回restricted URL，错误已保留network-limit-001.json，无重试/替代下载；其余从既有固定缓存研究并比对Git tree，绝不写成本轮在线验证。全部新写入局限独立ecology-availability-research tools/docs目录；未改生产、QA、主台账、待办、Jar、资产，未建新对话/自动运行，不启动游戏/服务器/GUI或编译测试。
