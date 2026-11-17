# Dynasty 项目内部清理（2026-11-16）

本次仅执行用户明确授权的项目内部存储清理。原制作、研究、构建、游戏测试继续暂停；不进行独立模组归档，不触碰垃圾桶和项目外文件。

## 已永久删除

- Git 明确报告的26个废弃临时对象/临时包，约4.91GB；超过七天未改动，无打开句柄，仓库连通性前后通过。全部正常分支、索引和正常历史包保持。
- 四份相同的旧 `caches/minecraftforge` 缓存副本，约45.59GB。逐文件路径、内容SHA-256、模式及链接目标与项目内保留副本相同，删除后再次核对保留副本。
- 旧互动QA目录中的 `caches/forge_gradle` 副本，约4.39GB。不是整棵树相等：该副本是保留缓存的严格子集，其全部文件与对应原件相同；保留缓存还具有额外文件。删除前后核对完整保留树。
- 25份与保留版本完全一致的旧应用备份，约26.2MB；保留每个版本的原件与当前应用。
- 444个由系统SDK生成的Swift/Clang编译缓存，约324.4MB；源码、测试、SDK和兼容头文件保持。

合计删除逻辑字节 **55,237,994,794（55.24GB）**。目录du统计约从 **283.94GB降为228.65GB**，不是实际物理释放量。各次删除前后观测的可用空间增量合计约 **5.33GB**；共享APFS数据块使逻辑副本大小显著大于物理释放量，其他同时进行的磁盘操作也可能影响观测。期间其他项目清理导致的全盘空间增加未计入本次成果。

## 保护与核查

`src`、`modpack`、`libs`、`dist` 共6,100个文件（约1.71GB）已逐文件复核，未缺失、未改变。有效参考、固定来源、源码绑定JAR、存档、原稿、精致旧稿、当前断点和历史验收材料保留。旧模型包装快照中的重复JAR也保留；没有把整棵冻结快照当垃圾处理。清单和研究进度不因存储清理而改变。

六个现有专业对话均已咨询；没有确认安全的额外内容继续保留。除本轮清理记录外，不恢复原任务。

## 恢复工作前先读

历史 `prepare.py` 曾用 `cp -cR` 把整份全局Gradle缓存播种到每个隔离目录，这些是大量表观占用的来源。**不要自动重跑旧准备脚本或重新填充已删的多份缓存。** 用户明确恢复且确有构建需要时，先核查项目内保留依赖，再按当时隔离和输入核验要求处理，不自动下载或重造大副本。

保留的一份完整缓存位于：

- `/Users/a15356015027/Desktop/dynasty/tools/cod4/ecology-acceptance/.work/gradle-home/caches/minecraftforge`
- `/Users/a15356015027/Desktop/dynasty/tools/cod4/ecology-acceptance/.work/gradle-home/caches/forge_gradle`

源码研究直接引用的以下路径完整保留：

- `/Users/a15356015027/Desktop/dynasty/tools/cod4/interaction-acceptance/.work/gradle-home/caches/minecraftforge`
- mob-load QA缓存内的固定Forge源码JAR及原始资源JAR，详见 `pinned-source-preservation-check.json`。

详细删除路径、原件哈希、保留副本及空间观测见同目录 `summary.json` 与四份 `*-deletion*.json` 收据。
