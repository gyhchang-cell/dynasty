# 继续清理的验收记录

本轮仅执行用户追加授权的 Dynasty 内部存储清理。原制作任务继续暂停；没有运行游戏、编译或下载，没有操作垃圾桶及项目外文件。

## 已完成

- 删除1,088份可重新生成的 Gradle 任务输出缓存，逻辑大小2,037,403,538字节。依赖源码、冻结输入和原始证据保留。
- 删除5份经逐文件内容、路径、权限和链接核对的重复 Gradle 工具分发缓存，逻辑大小2,371,266,390字节。完整工具副本保留在 `tools/cod4/ecology-acceptance/.work/gradle-home/wrapper`，删除后再次核对。
- 整理 Git 对象存储，净减少2,287,599,922字节。两个新存储包均通过完整校验，覆盖全部原对象。191,141个对象、全部原引用及索引保留；没有清除未引用对象、过期历史或 reflog。旧包删除总量不能当净释放量：新包同时占用了17.22GB。

上述合计减少约6.70GB逻辑存储。APFS副本共享数据块，逻辑大小不等于物理释放；磁盘可用空间观测也可能受其他进程影响。具体观测和最终目录统计见 `summary.json`。

## 保护范围

`src`、`modpack`、`libs`、`dist` 共6,100个文件、1,713,096,603字节逐一SHA-256复核，无缺失和变更。存档、专业资产、有效参考和历史QA快照继续保留，清单没有因清理而删项。没有把无法确认无用的材料当垃圾删除。

已删除的只是派生或重复工具缓存。以后得到制作恢复授权时，先核查项目内保留的 Gradle home；不要盲目重跑旧 `cp -cR` 准备脚本，重新制造多份缓存。重新编译可能因派生缓存清空而变慢，现有整合包运行文件保持原样。

## 收据

- `derived-cache-deletion-report.json`
- `wrapper-cache-deletion-report.json`
- `git-compaction-report.json`、`git-final-delete-proof.json`：最终对象覆盖闭环；较早的 `new-pack-index-coverage.json` 是补齐5,150个对象前的中间结果。
- `verify-new-pack-result.json`、`verify-supplemental-pack-result.json`
- `runtime-source-assets-preservation.json`

上一轮55.24GB逻辑删除的独立记录保留在上级目录；本轮不重复计算它。
