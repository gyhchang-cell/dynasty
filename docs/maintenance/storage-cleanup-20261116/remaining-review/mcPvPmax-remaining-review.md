# mcPvPmax：剩余大文件与缓存深入核查（2026-11-16）

本轮只进行存储清理。原制作、研究、下载、构建和游戏测试继续暂停；未触及 .git、其他岗缓存、项目外文件或垃圾桶。按已安装 find-skills 的适用性判断，本次标准库审计不需要安装或联网。

## 本轮实际删除

- 永久删除 **1630 份可再生 CPython 字节码缓存**；逻辑 18,348,213 字节（17.50 MiB），删除文件原已分配 21,712,896 字节（20.71 MiB）。
- 删除前：`du -sk` 12197208	/Users/a15356015027/Desktop/dynasty/tools/mc-macro。删除后：12176004	/Users/a15356015027/Desktop/dynasty/tools/mc-macro。两者相差21,204 KiB，约20.71 MiB。
- 卷可用空间观测：326,125,404,160 → 326,147,923,968 字节；系统及其他聊天同时活动，不能把卷差值全算成本轮。
- 绝大多数缓存位于 `.build/video-venv/lib/`，少量在研究脚本、Tests/Live及旧源码备份的 `__pycache__`。逐文件完整路径、缓存SHA-256、保留源码SHA-256、inode/mtime/size和操作结果详见 `mcPvPmax-remaining-review-deletion.json`。
- 每一份删除前均有普通 `.py` 源文件；PYC头中的时间戳/大小与该源文件吻合。删除前再次核对双方SHA、文件身份和打开句柄，删除后再次核对全部保留源文件SHA。没有删除整个 Python 环境、依赖源码、可执行工具或配置。
- 查阅54,209份文本文件的固定路径引用，未发现这些PYC被验收或源码固定引用。lsof查到的项目内打开文件仅为8份源码/AGENTS/build脚本，全部保留；删除目标无打开句柄。
- 上轮25份app备份与编译模块缓存目前已不存在；不重建、不再次计入本轮成果。

## 大体量材料为何仍需保留

- `tools/mc-macro/.build/video-study` 约8.58 GiB。实际核查201份 `.mov`/`.mp4`，其中192份在现存研究/试验文本有文件名引用；每份最多保存5条文件/行号/上下文证据到 `mcPvPmax-remaining-review-plan.json`。
- 191份MOV总量约6.27 GiB，属于不同起点、视角、候选、失败和应用入口录屏；未找到≥16MiB完全重复原视频。不能把失败实验录像视作无用，它们仍用于定位回归与比较旧成功效果。
- 141组字节相同的媒体并非141份无用材料。`research/xiaocai-study-20261026.json` 的144/155、264/276行分别绑定 everyone-cycle/continuous 与 imagine-cycle/continuous；相同图片分别承担概览、时间序列或片段定位。未删除任一帧，也未改变序列或历史验收路径。
- `research/frame-observations.json:142` 固定引用 app-east-182-turn/sheet.png；`research/camera-smoothing-184-progress.json:60` 固定引用 app-release-mixed-south-184-frames/sheet.png。没有删除看似可重新拼接的接触表，以保护当时实际查看过的证据。
- `.build/state-live` 约756.6MiB，包含被研究progress引用的原始读数/动作日志；与原始测试录像不是相同数据，不能当重复品清理。
- 7份完全相同的旧ZIP备份已核对SHA及候选目录保留件，但有历史备份目录/回滚用途绑定，本轮全部保留。具体每份路径、对应原件与引用证据见 plan 的 `hold_duplicate_zip`。
- combat-lan服务器JAR及其依赖、世界存档保留；应用源码、各候选独有逻辑、当前1.10.7未完成成果与不同版本回滚包均未动。

## 两份可能包含旧逻辑的PYC：明确不删

- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/combat-20261102/__pycache__/duel.cpython-314.pyc`：头部与现有源码不吻合，保留缓存及对应源码；缓存SHA `4d276a369ba2a684b9a808596287838ae84831ad5aec9b57c7b4315015a2da2e`。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/experiments-190/__pycache__/summarize_trials.cpython-314.pyc`：头部与现有源码不吻合，保留缓存及对应源码；缓存SHA `60efdf068a287c7eb7120fee48d44f0f3a563f287ed8be05d0c5b335cfa1326e`。

## 9份未发现文字引用的录像：明确保留

缺少文字引用不足以证明无用；保留其独有内容和恢复研究用途。

- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/doogile.mp4`（6,358,262 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/dribbly.mp4`（1,943,048 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/game-diagonal-before.mov`（17,872,822 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/game-diagonal-holdface.mov`（14,950,486 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/game-diagonal-retry.mov`（22,453,876 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/game-window-check.mov`（608,001 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/iinavy.mp4`（8,205,880 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/sweep-camera-1025.mov`（15,754,699 字节）。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/video-study/xiaocai190-app-diag192-openingfollow-nw.mov`（30,989,225 字节）。

## 报告与边界

- `mcPvPmax-remaining-review-plan.json`：删除前校验、保留原件、引用/句柄证据及录像保留清单。
- `mcPvPmax-remaining-review-deletion.json`：本轮实际删除路径与校验回执，完整保留源码清单。
- 仅上述PYC被永久unlink，清除其已空的__pycache__目录；未改任务清单、进度、源码、应用、权限或运行中的游戏。
- 深入核查后没有新增可证实安全删除的GiB级素材。不能为了空间数字而删除唯一录像、有效研究证据或当前断点。
