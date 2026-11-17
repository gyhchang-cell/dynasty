# 生态可达性研究协议 v1

本岗只研究，不制作。目标是实际阅读、核实并语义去重 1000 个相关 Minecraft 模组玩法实现。横扫等既有研究信用不继承；本地固定 corpus 仅复用来源。未满门槛不得修改生产、cap、概率、类别、资产、共享 Jar 或待办；不启动游戏、服务器、图形程序，不编译/测试，不执行上游代码。不依赖协调继续随机挂机，不安排自动运行。

## 计数

- 单位是独立玩法机制的完整实现链，包括入口、条件/状态、实际调用与结果边界。注册、调用者、被调用方法、序列化、客户端镜像组成一项，不拆开计数。
- 同一机制的物种 ID、参数、标签成员、模板/颜色、版本移植均合并。跨仓库相同语义也需比较，不以仓库名代替去重。
- 相关范围：自然出生入口与可达性交集、稀有被动生物和共享 cap 的共存、种群生命周期、结构/地形自然生成及场景门槛。通用缓存/网络库、仅视觉、建筑造型、纯战斗不计。
- `candidate` 未审查或调用链不完整，信用 0；`reviewed_proposed` 表示作者已全文阅读列明方法、核实来源并给出去重理由，仍为待审数；`accepted` 需独立审阅决定及证据。不得把候选量、方法量或 corpus 文件量写成完成量。
- 每项必有 repo/revision/path/source_local/source_sha256/line/end_line/excerpt/observation/application/limits/url；另带完整方法证据、固定 Git blob 校验、语义键、与近似项的差别。完整 excerpt 必须与原字节按行一致。局部注册字段注明是支持证据，不伪称完整方法。
- 来源须固定 40 位 commit；优先官方仓库已固定本地源码。保留原 metadata、Git tree 与 blob SHA-1 和文件 SHA-256。缓存核验不得写成本轮在线核验。无缓存/下载失败只记录缺口，不反复重试、不虚构。

## 本项目证据门槛（均为零参考信用）

分开记录 registry → 实际 biome 注入/category → 有效玩家/区块/400tick 机会 → global cap → local cap → species 抽取 → placement/position/obstruction → 非取消的自然实体加入 → 同 UUID 存活 → 玩家有效伤害/死亡/removal → 原掉落 UUID 拾取。前置门关闭，下游记 `not_evaluated`，不能记通过或失败。实际原生 gate、回调阳性、出生、死亡 candidate、严格 KILLED、掉落、拾取不可互相替代。

结构须区分注册、非空标签、structure_set/biome/placement 交集、valid start/pieces 与实际场景。古战场标签不能替代荒村/义庄/鬼市。已有来源的静态可达性不等于本世界已自然生成，也不证明等待足够久必出。

runtime04 基线冻结为 24/30 出生、9/10 材料；283 个完整原生 scope / 六周期 global CREATURE 全关闭，local 未评估；43 目标、61 攻击、37 死亡 candidate、0 严格 KILLED。1200tick 后停止清理，独立古战场 800tick 油窗口没有新灯笼鬼/原灯油拾取。保存日志与 exit0 不能替代玩法验收。保留既有失败，不回填成功。

## 输出和接续

仅写 tools/cod4/ecology-availability-research/ 与本 docs 目录。每批单独 JSON、完整来源索引、去重说明和未解决边界；研究计数与游戏验收计数分开。首批交付后接下一机制，不等待主协调挂机、不为凑数降低标准。没有审完的机制保留候选及精确断点。1000 前只归纳待验证设计原则，不实施新修复。
