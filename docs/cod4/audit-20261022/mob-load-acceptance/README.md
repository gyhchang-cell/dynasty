# COD4-1第二项：只读验收证据

最新只读补充：[原11项类预算与候选范围](class-budget-review.md)（6项全部候选满足、1项部分满足、2项超出全部候选、2项无可比；均非强制一对一）；[30类原始CSV独立复核](load30-independent.md)列出全部实体计数、粒子峰值、tick p95与帧p95。对应CSV/JSON及复现脚本均已保存。

**30/30类已完成各20只的原生cohort采样；整条产品验收仍保留未决项。**

最新逐类负载、基线、采样协议、截图路径和边界见 [30类覆盖报告](remaining-load-report.md)，结构化数据见 [remaining-load-results.json](remaining-load-results.json)。run-04补齐26类，100 tick预热、200 tick采样；原run-02四类为200/400，开放平台与本轮围护配置不同。

30类均保留实际渲染提交计数、AI/路径、粒子、服务端tick和帧时间。新增26类全程20只存活、NoAI=0；四个类别各有1个阶段末端0提交帧，未隐藏。渲染事件代表实际renderer提交，不是GPU可见像素或20个轮廓保证。

COD1基础怪作为产品比较口径：19个有依据的形态/用途对应候选均在面数预算内，另外11类未定义。详见 [对应表与选择理由](cod1-comparison.json)、[30类几何计数](geometry-counts.csv) 和 [原生COD1烘焙结果](run-03/native-cod1-geometry.json)。vanilla及旧自身模型仅作参考，不据此认定产品缺陷。

并行Java任务环境有原始CPU/load记录，不能从微小差异断言因果。未覆盖全技能、复杂地形、混合群、多人、长时间或完整整合包；原蟹兵持续全潜水边界仍保留未覆盖。蝗虫真实玩家接触补测与主30类分母分开，run-06在1112个采样帧全部记录20只提交，采样期成功对玩家伤害1次；粒子实测0，不代表粒子最坏情况。失败的run-04/05观察相机记录保留，详见最新报告。

原4类历史详表完整保存在 [historical-four-cohorts.md](historical-four-cohorts.md)。本任务仅写指定QA工具与审计目录，未修改正式代码、模型、贴图、TODO或游戏内容，QAhelper未入正式Jar。69份测量源码/模型与当前文件一致，见 [源文件核对](run-04-source-integrity.json)。
