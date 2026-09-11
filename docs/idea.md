# 在 IDEA 里运行 Dynasty（含常见报错处理）

> 工程目录：`~/Desktop/dynasty`（原 `newton's new mod` 已改名，**旧项目要关掉，重新打开这个新目录**）

## 🚀 先看这里：三条能跑起来的路（从易到难）

### 路线 A：完全不用 IDEA —— 双击脚本（最省事）
访达 → 桌面 → `dynasty` → **双击 `1-启动游戏.command`**
* 脚本自动使用 **JDK 17** 并执行 `./gradlew runClient`，出错会把报错留在窗口里。
* 另外还有 `2-构建模组.command`（出 jar）、`3-打包整合包.command`（出 `dist/` 上传包）。

### 路线 B：IDEA 的 Gradle 面板（不需要任何运行配置）
IDEA 打开 `~/Desktop/dynasty` 后：
**右侧 Gradle 工具窗 → `dynasty` → `Tasks` → `forgegradle runs` → 双击 `runClient`**

> 右侧没有 Gradle 面板 → 右键工程里的 `build.gradle` → **Link Gradle Project / Reload Gradle Project**；
> 或 `File | Open` 重新选 `~/Desktop/dynasty` 文件夹，弹窗选 **Import Gradle project**。

### 路线 C：IDEA 底部 Terminal
```bash
cd ~/Desktop/dynasty
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
./gradlew runClient
```

### 路线 D：右上角运行配置（工程里 `.run/` 已经建好三条）
IDEA 重新导入工程后会自动出现在右上角下拉框：

| 配置 | 做什么 | 用什么 |
| --- | --- | --- |
| **① Dynasty 模组（开发客户端）** | 跑**模组本体**的开发客户端（改代码调试用） | Gradle `runClient` |
| **② 导出 Dynasty 模组（jar）** | 构建并导出本体 jar → `~/Desktop/导出/Dynasty模组/dynasty-x.y.z.jar`，自动打开该文件夹 | Gradle `exportMod` |
| **③ 导出 Dynasty 整合包（CF/MR/手动 + 同步 HMCL）** | 出 `dist/` 三个上传包 → 复制到 `~/Desktop/导出/Dynasty整合包/`，并把 5 个模组同步进 HMCL 实例 `~/Public/.minecraft/versions/Dynasty 王朝 x.y.z/mods`，自动打开文件夹 | Gradle `exportModpack` |

> ③ 不是"在 IDEA 里把整合包开起来"（Curios / Puzzles Lib / Overflowing Bars 是 Mixin 模组，开发环境 official 映射下无法加载）。
> 它的定位是**一键产出可玩的整合包**：产物会直接同步进 HMCL，HMCL 里点 `Dynasty 王朝 x.y.z` 即可开玩。

**看不到这些配置？**
`Run | Edit Configurations…` → 若有旧的 `runClient`（报 `could not setcwd()`）选中按 **−** 删掉 → 关窗口；
`.run/` 里的配置会自动出现；仍没有就 `File | Reload All from Disk` 或重启 IDEA。
**注意**：只有工程根是 `~/Desktop/dynasty` 时这些配置才有效；如果工程根显示 Desktop，请用桌面上的 `打开Dynasty工程.command` 重开。

---

## ⚠️ 90% 的"IDEA 跑不起来"都是这两个原因

### 1) JDK 版本不对（本机装了 Java 25，很容易被 IDEA 默认选中）
本机 JDK：`temurin-17`、`liberica-jdk-17`、`liberica-jdk-25` —— **只能用 17**。
* `Settings | Build, Execution, Deployment | Build Tools | Gradle` → **Gradle JVM = 17（temurin-17 或 liberica-17）**
* `File | Project Structure | Project` → **SDK = 17**，Language level = 17
* `File | Project Structure | Modules` → `dynasty.main` → 依赖的 SDK 也是 17
* 工程里 `gradle.properties` 已写死 `org.gradle.java.home=.../temurin-17...`，所以 Gradle 任务本身一定用 17

### 2) 打开的目录不对 / 没导入 Gradle
* 要打开的是 **`~/Desktop/dynasty`（工程根，里面有 build.gradle）**
* ❌ 不要打开 `modpack/`（那只是整合包成品目录，不是编程工程）
* ❌ 不要运行 `Dynasty.java`（那是模组入口类，没有 main 方法）→ 请用 **runClient**

---

## 一、正确的打开步骤（照着做即可）

1. **关掉 IDEA 里旧的 `newton's new mod` 项目**（改过名，旧项目的路径已经失效）。
2. IDEA → `File | Open` → 选 **`~/Desktop/dynasty`** 这个**文件夹**（不是 `modpack`，也不是里面的 `src`）。
3. 弹窗选 **Trust Project**；如果问 "Import Gradle project?"，选 **Yes**。
4. 等右下角 **Gradle 同步** 跑完（第一次会下载依赖，可能 3–10 分钟；进度条消失即可）。
5. 右上角运行配置下拉框里会看到 **runClient / runServer / runData / runGameTestServer**（我已经生成好，在 `.idea/runConfigurations/`）。
   * 没看到？右侧 **Gradle** 工具窗 → `dynasty` → `Tasks` → `forgegradle runs` → 双击 **runClient** 也一样。
6. 点 ▶ **runClient** 启动游戏。

**验收标准**（日志里应该看到）：
```
[Dynasty] Curios not present - trinkets use the built-in pouch
[Dynasty] baked 15 entity model layers
[Dynasty] quests validated: 24 quests, 0 problems
```
命令行实测已通过（`BUILD SUCCESSFUL`），所以只要 IDEA 配置对了就能跑。

## 二、常见报错 → 处理办法

| IDEA 里的现象 | 原因 | 解决 |
| --- | --- | --- |
| `Could not set process working directory to '/Users/.../newton's new mod': could not setcwd() (errno 2)` | **IDEA 里还开着旧工程**：文件夹已改名 `newton's new mod` → `dynasty`，旧路径不存在 | ① 立刻可用：作者已建兼容链接 `~/Desktop/newton's new mod → dynasty`，直接再点一次运行即可；② 正确做法：`File | Open` 打开 `~/Desktop/dynasty`，并到 `Run | Edit Configurations` 里**删掉旧的 runClient**（它记着旧路径），改用右侧 Gradle 面板运行；③ 或者干脆双击 `1-启动游戏.command` |
| 打开后代码全红 / 没有 Gradle 面板 | 只打开了文件夹，没导入 Gradle 工程 | 右侧 Gradle 面板点 **↻ Reload/Rebuild**；或 `File | Open` 重选 `~/Desktop/dynasty` 并在弹窗选 "Import Gradle project" |
| `Directory '/Users/..../Desktop' does not contain a Gradle build` | **IDEA 的工程根是 `Desktop`**（把整个桌面当工程打开了）。它从 `Desktop/dynasty/.run/` 扫到这两个配置，但 `$PROJECT_DIR$` 解析成 Desktop → Gradle 去桌面找 `build.gradle` | **一键修**：双击桌面上的 **`打开Dynasty工程.command`**（或工程里的 `打开IDEA工程.command`），它会用 IDEA 打开正确目录；也可 `File | Open` 后**双击进入 `dynasty` 文件夹**再 Open。打开后校验：左侧项目树最顶层必须叫 **dynasty** |
| 运行按钮是灰的 / 下拉框里没有 runClient | 没同步完 或 没生成运行配置 | Gradle 面板 → `Tasks → forgegradle runs → runClient` 直接双击（或执行一次 `./gradlew genIntellijRuns`） |
| `Unsupported class file major version` / `Toolchain 17 not found` / `无效的源发行版: 17` | **JDK 不是 17** | 我已在 `gradle.properties` 里写死 `org.gradle.java.home=...temurin-17...`；若你的 JDK 位置不同就改成你的路径。另外 `File | Project Structure | Project SDK` 选 **17**，`Settings | Build Tools | Gradle | Gradle JVM` 也选 **17** |
| `Could not find top.theillusivec4.curios:...` | 有人删了 `libs/repo` 或不在工程根目录构建 | 确认 `libs/repo/top/theillusivec4/...` 存在（整合包依赖的本地仓库）；重新 `./gradlew build` |
| 运行后 `Mixin apply failed ... f_19803_` | 你把 Curios / Puzzles Lib / Overflowing Bars 的 jar 手动丢进了 `run/mods/` | **删掉 `run/mods/` 里的第三方 jar**：开发环境不支持 Mixin 模组（SRG vs official 映射），第三方模组只在整合包（启动器）里生效 |
| `Main method not found` / 绿色 ▶ 直接跑 `Dynasty.java` | 点错了入口 | 不要运行 `Dynasty` 类；请用 **runClient** 配置 |
| 客户端窗口一闪而过 | `run/` 里已有同名进程占用，或上一次没退干净 | `pkill -f runClient` 后重试；或在 IDEA 里 Stop 再 Run |
| 首次同步卡在下载 | 网络 | 挂代理/VPN 重试；依赖已在 `~/.gradle/caches`，第二次会快很多 |

## 三、IDEA 里能做什么 / 不能做什么

* ✅ 改代码、跑 `runClient`/`runServer` 调试本体、看日志、加物品。
* ❌ 不要在 IDEA 里期待 Curios 饰品槽或美化血条生效 —— 那三个是 Mixin 模组，开发环境（official 映射）无法应用它们的 Mixin。
  想连带它们一起玩，请用**启动器 + `modpack/mods/`（5 个 jar）**。

## 四、兜底：命令行永远可用

```bash
cd ~/Desktop/dynasty
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
./gradlew runClient      # 启动客户端
./gradlew runServer      # 启动服务端
./gradlew build          # 只构建 jar → build/libs/dynasty-1.4.0.jar
```
