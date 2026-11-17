# mc-macro 存储只读审计（2026-11-16）

仅审计，未删除、未改清单；制作/研究/构建/游戏测试继续暂停。使用已安装 find-skills 的判断流程，本次标准文件系统审计不需额外安装或联网。

- 项目 du：12,540,828 KiB，约 11.96 GiB；其中 video-study 为 8,994,952 KiB（约8.58 GiB）。
- 建议由主协调核实的安全候选：25 个完全重复旧 app 副本 + 1 个编译模块缓存；文件已分配块合计 351,866,880 字节（335.57 MiB），逻辑字节 350,608,414。不等同 APFS 实际立即释放量。
- 缓存 444 文件、逻辑 324,407,124 字节（309.38 MiB）；lsof返回1且无打开文件输出。执行前再次检查占用。
- 141 组≥64KiB的逐字节重复媒体，额外副本逻辑量 140,639,422 字节；**暂不建议删**，有连续帧和固定来源引用风险。
- 未找到可确定安全释放的多GiB整目录。所有≥16MiB文件大小均不重复，没有找到对应级别的完全重复视频。

## 精确删除候选（主协调执行，本聊天不删）

|可删副本路径|保留副本路径|逻辑字节|
|---|---|---:|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/root-dist-before-ui-193.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/192-release-manual/dist/mcPvPmax.app`|765,104|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/mcPvPmax-1.9.0-before-ui-193.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/192-release-manual/dist/mcPvPmax.app`|765,104|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-1102-20261104-185630/mcPvPmax-1.10.1.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/cline-audit-20261104/app/mcPvPmax.app`|1,355,803|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/anchor-197/dist-1.9.6.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/sword-only-196/mcPvPmax.app`|985,723|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/anchor-197/desktop-1.9.6.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/sword-only-196/mcPvPmax.app`|985,723|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-196/dist-mcPvPmax-1.9.3.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/195-inventory/dist/mcPvPmax.app`|979,186|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-196/desktop-mcPvPmax-1.9.3.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/195-inventory/dist/mcPvPmax.app`|979,186|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/anchor-range-199/mcPvPmax-1.9.8.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/sprint-198/mcPvPmax.app`|1,198,231|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/sword-only-196/dist.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/left-only-195/mcPvPmax.app`|962,683|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/sword-only-196/desktop.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/left-only-195/mcPvPmax.app`|962,683|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-1103-20261105-155622/mcPvPmax-1.10.2.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/held-item-1102/app/mcPvPmax.app`|1,378,379|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/combat-1910/mcPvPmax-1.9.9.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/anchor-range-199/mcPvPmax.app`|1,218,871|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-1100/dist.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/anchor-range-199/mcPvPmax.app`|1,218,871|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-1100/desktop.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/anchor-range-199/mcPvPmax.app`|1,218,871|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/left-only-195/dist/mcPvPmax.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/196-held-tools/dist/mcPvPmax.app`|962,683|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/left-only-195/desktop/mcPvPmax.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/196-held-tools/dist/mcPvPmax.app`|962,683|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/sprint-198/mcPvPmax-1.9.7.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/anchor-197/mcPvPmax.app`|1,181,277|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-1104-20261105-161258/mcPvPmax-1.10.3-withdrawn.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/attack-priority-1103/app/mcPvPmax.app`|1,385,147|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/mcPvPmax-1.9.1-before-glass-194.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/193-ui/dist/mcPvPmax.app`|827,712|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-195/dist-mcPvPmax-1.9.2.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/194-bridge-art/dist/mcPvPmax.app`|863,200|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/release-195/desktop-mcPvPmax-1.9.2.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/194-bridge-art/dist/mcPvPmax.app`|863,200|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-sync-1101-20261104-110951/mcPvPmax-1.10.0.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/dist/mcPvPmax.app`|1,352,060|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/sword-toggle-1101/mcPvPmax.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/dist/mcPvPmax.app`|1,352,060|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/root-dist-before-manual-20261030.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/mcPvPmax-1.8.9-before-190.app`|738,425|
|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/mcPvPmax-1.8.9-before-manual-20261030.app`|`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/mcPvPmax-1.8.9-before-190.app`|738,425|

编译缓存候选：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/module-cache`。用途为 SDK 导入派生模块；保留源码/SDK/.build/sdk-compat，不能扩大成删除整个 .build。

应用副本逐文件路径、SHA-256、大小、权限和符号链接目标完全一致，详细 manifest 见同目录 `mc-macro-audit.json`。只删表中的 app，不删父目录中的日志、回退源码或收据。保留版本1.8.9基线在 `.build/backups/mcPvPmax-1.8.9-before-190.app`；现有 dist 与本轮1.10.7候选均保留。

## 明确保留

- `.build/video-study` 的8.58GiB资料包括主播ikun是小菜参考、连续逐帧、用户原始失败录像；不是已确认废弃缓存。
- `.build/state-live` 约756.6MiB，历史 progress 中明确引用原始测试日志，保留。
- 全部 research 来源/验收材料、世界/服务器存档、当前断点、不同版本唯一产物和未完成候选保留。
- `.build/video-venv` 约95.8MiB，不是已确认重复依赖；不为少量空间冒险删除。

原始大文件与其他应用不挪动、不更名、不重建。主协调若接受候选，执行前须复核 SHA、保留路径和占用状态。
