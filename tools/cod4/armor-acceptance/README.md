# COD4-4 盔甲代码验收

2026-10-23：隔离 Forge GameTest 已实际运行结束，63/63 通过，Gradle 退出码 0。最近一次为 `evidence/final-current.log`、`evidence/final-current-receipt.json`；保留先前 `evidence/final.log`。完整修复、源哈希、测试分类和剩余验收在仓库 `docs/cod4/audit-20261022/armor-acceptance.json`。本轮补报告和研究，没有追加正式 Java 改动。

本套件不启动 GUI、不加载真实用户存档，也不等同于两名真实玩家联机。28 个套装用例真实调用 ServerPlayer/LivingEntity 的装备检测，穿戴序列为 2→3→4→3→2→0；检查七种属性重复刷新不叠加、卸装回退、外部夜视药水保留，以及另一名断开网络的服务端测试角色不受影响。它们没有逐一触发全部 84 个条件行为，不能写成“28 套 2/3/4 件实机验收完成”。

额外复用 20 个现有装备/格挡/蓄势/召唤/冷却测试，其中 11 个原有用例使用 FakePlayer；复用 4 个体质测试（仅变更私有发现命名空间）。11 个本次专项回归包含原生输入、原生 NBT 读写及明确构造的事件级断言。合计 52 个普通 ServerPlayer 夹具测试、11 个 FakePlayer 夹具测试，不能将 63 项全部描述为真人原生输入验收。最近冻结树包含主代理反馈修复，但本分工没有重复其 LAUNCH 专项测试。

修复前，排除测试角色出生保护影响后的同一核心 60 项中有 7 项失败；修复后 60/60 通过，再加入三个针对新来源判断的正反向用例，最终 63/63 通过。`initial-fixture.log` 中四个出生保护造成的失败不作为产品缺陷证据。正式修改仅 `EquipmentBehaviors.java`：四种三件临时窗口失去资格时撤销、青铜/凤羽开窗核来源、反击标记来源并在换装/换手时复核、北斗伤害入口读取实时四件。`QiConstitution.java` 没有由本分工修改。

**专属研究已补足（事后补读），当前核验检查点：1000/1000，仍缺0。** 原 `status-reference-1000.json` 的固定版本、哈希、摘录、行号核验，只证明宽泛 status/immune/removal 语料存在；静态 `fireImmune` 等不计为本次换装窗口、反击归属和持久冷却研究。最初五段只是相关补读，不是补齐1000的证据，也不按五个独立实现直接相加。既有修复发生在专属门槛满足之前，此次补读不能追溯冒称制作前已完成。

原593个候选（其中原先340处未审）已经全部逐段结案，接受301处、排除292处。之后扩大到事件、能力、属性和冷却辅助方法，补取完整固定版本Java源码。最新扫描涉及29035个Java物理文件路径（跨缓存可重复）；4085个归一化候选不是有效参考数。目前逐段接受1000处、排除845处、尚未计入2240处。未声称穷尽所有外部源码。

方法内多个分支只计一处，重复模板、纯setter、客户端动画和无关生物AI不填数。详见 `evidence/armor-references.json`（已核验接受片段、来源、观察）、`evidence/armor-reference-ledger.json`（全部候选状态）、`research/reviewed-sites.json`（人工结论）、`evidence/discovery-rounds.json`（扩展检索）与 `evidence/expanded-source-downloads.json`（新源码固定提交及下载哈希）。外部实现含风险反例，不作正确性背书。新来源只读取Java与许可证，没有执行上游代码。

后续独立队列：已按用户要求联系 Kepler，迁移研究另存 `migration-research/`，优先 Clone 死亡字段白名单、持续冷却跨生死和旧物品ID替代。读取其已选段去重后贡献单独账本，不写其生产新类。盔甲1000不会自动计入迁移1000。研究总结在 `evidence/armor-research-summary.json`；真实双客户端和长冷却由 Herschel 继续。

证据核验（不运行游戏）：

```sh
python3 tools/cod4/armor-acceptance/verify_references.py
python3 tools/cod4/armor-acceptance/publish_research.py
python3 tools/cod4/armor-acceptance/index_tests.py
python3 tools/cod4/armor-acceptance/write_report.py
```

`publish_research.py` 核对接受片段的本地文件字节、行号、归一化去重和不重叠范围，并校验固定提交的 Git tree blob；无 tree 的文件使用已保存的固定提交原始文件哈希回执。需要重新联网验证该部分时加 `--verify-missing-pins`。Python 默认证书链初次失败记录已保留，随后使用开启 TLS 校验的系统 curl 获取；不是额度失败，也不影响已完成的 GameTest 证据。

重跑测试（macOS、已有本仓库依赖缓存；本轮无需重复）：

```sh
python3 tools/cod4/armor-acceptance/prepare.py --refresh-source
python3 tools/cod4/armor-acceptance/run_verified.py --label rerun --world rerun
```

`--label` 必须未被使用，回执和日志不会覆盖既有证据。`prepare.py` 使用 APFS copy-on-write 克隆依赖缓存，不创建共享硬链接。首次准备无需 `--refresh-source`；已有快照会在刷新时保留到私有历史目录。运行时不要刷新快照。JDK 路径在 `run.sh` 中。初始化脚本沿用 `tools/cod4/qi-qa.init.gradle` 的隔离方法，未修改该共享脚本。冻结源码、Gradle缓存、项目缓存、构建输出和服务器运行目录均在本工具的 `.work/` 中；该目录被局部 `.gitignore` 排除。

仍保留客户端/真人验收：28套各档全部84项实际条件行为与卸装、视觉/音效、真实双人归属和同步、召唤物在真实水域与维度切换时的表现、Boss实战完整长冷却计时、真实死亡重生/退出重进/服务器重启后的冷却。主代理负责 GUI。本分工没有改待办原文、共享build输出、模型、贴图、建筑或主代理的通用反馈修复。
