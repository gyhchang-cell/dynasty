# COD4 食品客户端验收工具

QA-only：使用真实生产Minecraft客户端和同UUID连接的集成服务端玩家。正式JAR来自已验证的language-repair产物；只在独立`.work/run-NN`实例复制包、加QA helper和提供测试物品/状态/靶怪。不得覆盖既有run、其他代理实例或用户整合包。

最终证据在`docs/cod4/audit-20261022/food-client-acceptance/REPORT.md`。原请求分母15：8食品+7既有瞬发符；run02为26例，run03为16例相机补充。run01遮挡图保留为历史，不用于最终视觉证明。

离线复核现有证据（不启动游戏）：

```sh
python3 tools/cod4/food-client-acceptance/verify.py
```

该脚本重算run02/run03原生事件、时钟、消耗、收益、相机身份、人工看图文件SHA与旧服务端证据实现绑定，写回本目录对应的final-acceptance/native-verification/denominator。933个检查是42个实际用例的断言数，不是933次游戏。visual-review是实际打开图片后逐项记录，不能自动凭PNG存在生成“看图通过”。

后续需要新运行时，从仓库根目录构建QA helper（仅本任务输出和缓存；需Java17与ForgeGradle依赖）：

```sh
JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home \
./gradlew --no-daemon --max-workers=2 \
  --gradle-user-home tools/cod4/food-client-acceptance/.work/gradle-user-home \
  --project-cache-dir tools/cod4/food-client-acceptance/.work/project-cache \
  -I tools/cod4/food-client-acceptance/qa.init.gradle reobfFoodClientQaJar
```

`qa.init.gradle`将buildDirectory指向`.work/gradle`，只编译独立foodClientQa源集，不编译/替换正式Java。未初始化的私有Gradle缓存需要下载依赖。当前归档build-04.log是已成功的run03 helper构建，不能将上述复现命令未执行的缓存配置冒称既有构建环境。

选择新的未存在run编号，启动与驱动分开终端执行；启动器保持运行直到自身客户端退出：

```sh
python3 tools/cod4/food-client-acceptance/launch.py run-04 zh_cn
```

```sh
python3 tools/cod4/food-client-acceptance/drive.py run-04
```

完整计划26例。需要16例食品前后相机身份补充时，在另一个全新run上给drive.py追加`camera-audit`，不能对已用run重复覆盖结果。新增run后须显式复核并更新verifier的归档选择，当前verifier固定run02/run03。

驱动完成后客户端保留供看图。确认本run结果已写完，用以下原子命令只结束自己的实例；不要终止其他Java PID：

```sh
python3 - <<'PY'
from pathlib import Path
import json, os
out=Path('docs/cod4/audit-20261022/food-client-acceptance/run-04')
command={'id':'finish-owned-client','op':'finish'}
(out/'finish-owned-client-command.json').write_text(json.dumps(command))
(out/'command.pending').write_text(json.dumps(command))
os.replace(out/'command.pending',out/'command.json')
PY
```

核对FINISHED.json和exit-code.txt后再交付，DRIVER-COMPLETE不等于最终验收。原生时钟和扣料来自result/ticks；部分framebuffer PNG可能停帧，不得仅根据文件名或采集状态推断像素精确时序。长期效果/Build收益复用routes-05的8项服务端运行，并对6份实现SHA验证一致；不得把detached服务端玩家称客户端。

QA提供物品与条件，没有自然获取或六阶段2–3小时生存节奏结论。自动化真实客户端是有效客户端证据，不额外要求真人。无生产Java/资产修改，无自设NBT或瞬发符32刻契约。
