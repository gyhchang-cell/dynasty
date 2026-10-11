# Cod2 本地核验与补完记录 · 2026-10-10

**未全部完成。** 本报告来自真实服务端注册表、现有资源和实机局部 QA。框架、目录、注册 ID、单个场景通过均不代表整项成品完成。已验证基础任务从外部 `cod2.txt` 删除，原文备份及删除记录见 `DELETIONS_20261010.json`。

## 本轮实现与验证

修正事件服务器全局并发上限、死亡玩家参与/奖励/祝福判定、被取消死亡与实体类型不匹配的账本更新；真实压缩 `.dat` 文件测试验证离线奖励、清理预约及冷却恢复。沉沙玄宫驻军等待实际实体区块就绪。修正新合入 Cod1 物种的重复生态刷怪表登记，并扫描全部实际 Biome 刷怪表验证每种至多一条、至少保留一个有效入口。

服务端：68 项，通过，构建成功。单客户端：All ten world client stages passed。双客户端：host=All ten world client stages passed；peer=All ten world client stages passed。

客户端 10 阶段涵盖：真实奖励模型、阴兵队列与雾、资源重载、客机 TCP 断线重连、停止后清理、玄鸟祝福与武器耐久同步、冲锤三阶段实际 Renderer、再次天象及现有维度切换后清理。使用临时世界、静音，不改变系统音量；不等于地牢完整通关或30事件验收。

## 10 地下城世界落点表

下表保留原设计落点，只有沉沙玄宫已经注册实际结构。其8192格是候选网格间距，实际平均发现距离未测；其他行均是未实现的要求。

| 地下城 | 维度要求 | 地形/层级 | 原要求间距 | 最小出生点距离 | Boss要求 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 镇岳孤陵·沉沙玄宫 | 主世界 | 荒漠/恶地，地下三层 | 6000–9000 | 2500 | 昭明帝 | PARTIAL；缺Boss/精英/奖励/完整美术与探索验收 |
| 天工破晓·千机机关城 | 主世界 | 山地/喀斯特，四层圆坑 | 6000–9000 | 待落实 | 刑天遗卫 | 未实现 |
| 万骨枯寂·血海古战场 | 主世界 | 荒原/沙地，城防与堑壕 | 5000–8000 | 待落实 | 公孙无妄 | 未实现 |
| 断魂迷障·黑风阿兰若 | 主世界 | 高山绝壁，垂直寺院 | 6000–9000 | 待落实 | 黑风法王 | 未实现 |
| 千古幽咽·阴司枉死城 | 复用阴司；否则主世界地下 | 地下街区与血河 | 待落地 | 待落实 | 彼岸冥舟 | 未实现 |
| 万蛊盘虬·赤练古苗窟 | 主世界 | 湿热山地/丛林/沼泽，地下 | 5000–8000 | 待落实 | 蛇母娘娘 | 未实现 |
| 太清问道·冲霄隐仙观 | 复用神域；否则主世界高山上空 | 浮岛/云桥 | 8000–12000 | 待落实 | 九霄木鸢 | 未实现 |
| 玄冥极渊·万载冻龙窟 | 主世界 | 雪山/冰原/冻海，冰下洞窟 | 6000–10000 | 待落实 | 沉渊骨龙 | 未实现 |
| 极天剑绝·封魔万刃峰 | 主世界 | 极高山/孤峰，登峰路线 | 8000–12000 | 待落实 | 玄天剑煞 | 未实现 |
| 苍穹逆乱·四象封天枢 | 复用现有四象终局区域 | 固定唯一四岛区域 | 唯一，不随机刷 | 待落实 | 混元祖兽，保留现有最终Boss | 未实现 |

沉沙玄宫实际缺失：dynasty:zhaoming_di；cod1 startEncounter + world/player reward binding。披鳞执金吾、巨锤金甲力士亦未注册；其余九座没有成品结构，不能用现有 Boss 改名或空钩子充数。

## 地下城机关实现表

| 机关 | 方块/类 | 保存与同步 | 伤害/动画 | 本轮验收边界 |
| --- | --- | --- | --- | --- |
| 断龙石/三兽眼/封门 | 自定义 DungeonMechanismBlock/BlockEntity | 房间SavedData、实例UUID、目标位掩码、BE包 | 服务端解谜；封门碰撞/开门进度 | 既有服务端局部测试；本轮未跑整座地牢 |
| 毒箭/翻板 | 自定义 pressure_trap_emitter/resettable_floor | 房间时钟；BE阶段快照 | 接触帧生成限量毒箭/失碰撞/恢复 | 服务端回归；本轮未完整探索验收 |
| 返程吊篮/石碑 | 自定义 elevator/shortcut | SavedData永久解锁；目标楼层 | 已加载安全目标，有限楼层式传送 | 服务端回归；未把货物测试当实机地牢通关 |
| 水银闸/护城渠 | 房间控制器/受保护mercury_channel | 服务端计时、暂停卸载；专用不可挖块 | 预警、区域接触；幻想粒子液面 | 服务端回归；本轮未实机末室验收 |
| 冲锤/履带/蒸汽/地雷/箭雨/罡风 | 自定义六种TRAP + DungeonTrapProfile | 同一房间时钟，持久化阶段/剩余tick | 预警后有限伤害或速度；冲锤Renderer | 冲锤显示/同步通过单/双端局部QA；不等于对应地牢完成 |
| 其余设计机关 | 尚缺真实实现/结构绑定 | 待实现 | 待实现 | 未实机验证 |

| 地下城 | 机关要求 | 自定义/状态/动画/同步 | 实机边界 |
| --- | --- | --- | --- |
| 镇岳孤陵·沉沙玄宫 | 断龙石、兽眼、翻板、毒箭、水银闸、吊篮 | DungeonMechanismBlockEntity；房间/instance保存，阶段BE同步，接触帧服务器判定 | 既有结构局部回归；完整探索未实机验证 |
| 天工破晓·千机机关城 | 齿轮水闸、冲锤、履带、蒸汽、升降机 | 已有crusher/conveyor/steam/elevator独立块与时钟；水闸和结构绑定待做 | 冲锤单/双客户端局部QA；整座未实现 |
| 万骨枯寂·血海古战场 | 扎马坑、地雷、箭雨、炸墙捷径 | 已有mine/arrow_rain独立块；无真实爆炸；扎马坑和预设墙切换待做 | 独立伤害/掩体服务端测试；整座未实现 |
| 断魂迷障·黑风阿兰若 | 断木、幻镜、经幢、喷火、铁索捷径 | 已有resettable_floor/shortcut基础；mirror_altar/scripture_pillar/flame_vent及结构绑定待做 | 整座未实现；未实机验证 |
| 千古幽咽·阴司枉死城 | 鬼打墙、铡刀、封门、引魂灯、水闸 | 已有seal_door基础；loop_gate/guillotine/soul_lantern/gate待做 | 整座未实现；未实机验证 |
| 万蛊盘虬·赤练古苗窟 | 毒藤、落石、瘴气、栈道捷径 | poison_vine/rockfall_anchor/miasma_vent及结构绑定待做 | 整座未实现；未实机验证 |
| 太清问道·冲霄隐仙观 | 云砖、丹炉火、阴阳砖、上升气流 | fading_cloud_tile/flame_vent/yin_yang_tile/updraft_vent待做 | 整座未实现；未实机验证 |
| 玄冥极渊·万载冻龙窟 | 滑冰寒冷、冰锥、热源、融冰墙 | 自定义cold/heat/icicle/sealed_ice控制器待做；原版冰只提供材质与摩擦 | 整座未实现；未实机验证 |
| 极天剑绝·封魔万刃峰 | 飞剑阵、罡风、剑底座、倒剑桥 | 已有wind_field独立块；sword_array/pedestal/桥piece切换待做 | 罡风有限速度服务端测试；整座未实现 |
| 苍穹逆乱·四象封天枢 | 四象碑、重力、避难点、光桥、中央门 | 已有seal_door基础；四象/重力/避难/碰撞光桥及固定区域绑定待做 | 整座未实现；未实机验证 |

## 10 生态规则表

权重/group为EcologyRule定义值；使用已有Cod1刷怪器的物种保留其实际原生权重，并禁止二次登记。自然分布、所有原文协同/天气行为、缺失精英与神域角色均未整项验收。

| 区域 | 维度类型Tag | Biomes/结构Tag | Y | 时间/天气 | local cap | 物种/权重/group |
| --- | --- | --- | --- | --- | --- | --- |
| 深山茂林区 | #dynasty:ecology/overworld | dynasty:blueprint/shanxiao_habitat | -63–240 | ALL/ANY | 普通12/飞行3/精英0 | shanjing_shanxiao w=4 g=1–3 cap=3, kumu_shujing w=3 g=1–2 cap=2, baimu_mowu w=2 g=1–2 cap=2, chimu_zhuha w=4 g=1–2 cap=2 |
| 焦土古战场 | #dynasty:ecology/overworld | dynasty:blueprint/battlefields | -32–220 | NIGHT/ANY | 普通16/飞行2/精英1 | zuwu_daoshou w=8 g=1–3 cap=4, juma_changqiangbing w=2 g=1–2 cap=2, liannu_zhenzu w=2 g=1–3 cap=3, ludun_jiashi w=1 g=1–2 cap=2, zhenwang_zhangqiguan w=1 g=1–1 cap=1, kuijun_sishi w=1 g=1–3 cap=3, tiesuo_chihou w=2 g=1–2 cap=2, xianzhen_duantoujiang w=1 g=1–1 cap=1 |
| 废村荒镇区 | #dynasty:ecology/overworld | dynasty:ecology/ruined_villages | -63–220 | NIGHT/ANY | 普通8/飞行2/精英1 | zhiren_jianke w=3 g=1–3 cap=3, fuhun_baibu_tongzi w=1 g=1–1 cap=1, yinyang_zhijiao_youhun w=1 g=1–1 cap=1, shibian_lishi w=1 g=1–2 cap=2 |
| 古墓地宫区 | #dynasty:ecology/overworld | dynasty:ecology/tombs | -63–64 | ALL/ANY | 普通8/飞行3/精英1 | shibian_lishi w=1 g=1–2 cap=2, muxue_feilu w=2 g=1–1 cap=3, qingtong_shuangtoushekui w=1 g=1–2 cap=2, juli_bixi_kuilei w=1 g=1–1 cap=1, banshan_jiazhou_shikuang w=1 g=1–1 cap=1 |
| 河流湖泊与大沼泽 | #dynasty:ecology/overworld | dynasty:ecology/wetlands | -62–220 | ALL/ANY | 普通6/飞行0/精英1 | shashui_funigui w=2 g=1–3 cap=3, bishui_xuanjiao_youzi w=3 g=1–2 cap=2, chimu_zhuha w=4 g=1–2 cap=2, fubo_xunhai_yecha w=1 g=1–1 cap=1 |
| 地下溶洞与矿脉裂谷 | #dynasty:ecology/overworld | dynasty:ecology/caves | -63–40 | ALL/ANY | 普通8/飞行4/精英0 | mingsha_shixie w=4 g=1–3 cap=3, bazu_digongzhu w=2 g=1–2 cap=2, youdeng_guimianfu w=2 g=1–1 cap=3, xueju_mangguyu w=2 g=1–3 cap=3 |
| 万仞绝壁与积雪孤峰 | #dynasty:ecology/overworld | dynasty:ecology/snow_peaks | 140–319 | ALL/ANY | 普通5/飞行3/精英1 | hanshan_tongjia_juyuan w=1 g=1–1 cap=1, liefeng_jindiao_yushi w=1 g=1–1 cap=1, tongbi_feitian_yecha w=2 g=1–1 cap=2 |
| 云端虚空与天阶神域 | #dynasty:ecology/celestial | dynasty:ecology/celestial | -63–319 | ALL/ANY | 普通4/飞行3/精英1 | 无自然池；原角色待绑定 |
| 瘴气蛊毒妖域 | #dynasty:ecology/overworld | dynasty:ecology/toxic_miao | -63–220 | OUTSIDE_NOON/ANY | 普通8/飞行3/精英1 | gudu_tianzhunv w=1 g=1–1 cap=1, baimu_mowu w=2 g=1–2 cap=2, baimian_huxiangu w=1 g=1–1 cap=1 |
| 终极神魔古祭坛（四象维度边界） | #dynasty:ecology/final | 固定阵眼范围待绑定 | -63–319 | ALL/ANY | 普通0/飞行0/精英0 | 无自然池；原角色待绑定 |

实际缺失生态实体：dynasty:baimian_huxiangu；dynasty:banshan_jiazhou_shikuang；dynasty:fubo_xunhai_yecha；dynasty:gudu_tianzhunv；dynasty:hanshan_tongjia_juyuan；dynasty:liefeng_jindiao_yushi；dynasty:xianzhen_duantoujiang。未绑定原文角色：天机罗刹鸟、云中巡守仙吏虚影、蛇母麾下蛇群、玄冰异兽。阵营、捕食目标、world state说明详见同名JSON，字符串状态说明不等于相应行为已经实现。

## 30 随机事件触发表

3个基础控制器可运行，27个仍UNIMPLEMENTED；3个运行模板的完整原奖励分支、场景叙事和自然触发验收仍为PARTIAL。手动命令不会把UNIMPLEMENTED事件替换成通用事件。所有触发参数来自当前实际Definition。

| 事件 | 维度Tag | 区域Tag/Y | 时间/天气 | 冷却/稀有度 | 半径/时限tick | 控制器/状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 子夜军魂·阴兵借道 | dynasty:ecology/overworld | dynasty:ecology/event_plains / -63–319 | 17700–18300 / FOG | 72000 / 1:40 | 64 / 1800 | PROCESSION / PARTIAL; full source branches not accepted |
| 荒村诡市·纸扎迎亲 | dynasty:ecology/overworld | dynasty:ecology/ruined_villages / -63–319 | 11500–13500 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 深潭夜渡·落水冤索 | dynasty:ecology/overworld | dynasty:ecology/wetlands / -63–319 | 17000–19000 / NO_MOON | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 狭路相逢·山路伏兵 | dynasty:ecology/overworld | dynasty:ecology/snow_peaks / -63–319 | 0–12000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 官运劫杀·绝境镖车 | dynasty:ecology/overworld | dynasty:ecology/roads / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 4800 | BATTLE / PARTIAL; full source branches not accepted |
| 黑云压顶·天雷地火 | dynasty:ecology/overworld | dynasty:ecology/event_plains / -63–319 | 0–23999 / THUNDER | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 枯井啼婴·深井异象 | dynasty:ecology/overworld | dynasty:ecology/ruined_villages / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 古刹钟鸣·盲僧化魔 | dynasty:ecology/overworld | dynasty:ecology/temples / -63–319 | 11500–13500 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 沙暴过隙·楼兰幻城 | dynasty:ecology/overworld | dynasty:blueprint/scorpion_habitat / -63–319 | 0–23999 / SANDSTORM | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 江湖仇杀·双雄死斗 | dynasty:ecology/overworld | dynasty:ecology/roads / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 血月当空·百妖夜游 | dynasty:ecology/overworld | 维度范围 / -63–319 | 13000–23000 / ANY | 480000 / 1:200 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 地龙翻身·矿道塌方 | dynasty:ecology/overworld | dynasty:ecology/caves / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 义庄诈尸·七星续命灯 | dynasty:ecology/overworld | dynasty:ecology/ruined_villages / -63–319 | 17000–19000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 蜃气蔽日·水乡迷局 | dynasty:ecology/overworld | dynasty:ecology/wetlands / -63–319 | 0–2000 / FOG | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 异宝现世·古碑破土 | dynasty:ecology/overworld | dynasty:ecology/event_plains / -63–319 | 0–12000 / CLEAR | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 孤魂问路·荒野老妪 | dynasty:ecology/overworld | dynasty:blueprint/shanxiao_habitat / -63–319 | 11500–13500 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 天降陨铁·火流星坠 | dynasty:ecology/overworld | dynasty:ecology/event_plains / -63–319 | 13000–23000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 玄鸟止戈·吉兆天象 | dynasty:ecology/overworld | 维度范围 / -63–319 | 0–12000 / ANY | 72000 / 1:40 | 64 / 1800 | CELESTIAL / PARTIAL; full source branches not accepted |
| 天工失控·暴走木牛 | dynasty:ecology/overworld | dynasty:ecology/mechanism_cities / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 黑风卷地·恶风伏杀 | dynasty:ecology/overworld | dynasty:blueprint/scorpion_habitat / -63–319 | 11500–13500 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 古阵回光·星宿错乱 | dynasty:ecology/overworld | dynasty:blueprint/ritual_sites / -63–319 | 13000–23000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 盗墓同行·分赃不均 | dynasty:ecology/overworld | dynasty:ecology/tombs / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 天狗食日·诸神隐匿 | dynasty:ecology/overworld | 维度范围 / -63–319 | 5000–7000 / ANY | 480000 / 1:200 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 野渡无人·孤舟自横 | dynasty:ecology/overworld | dynasty:ecology/wetlands / -63–319 | 11500–13500 / FOG | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 百鸟朝凤·神木显圣 | dynasty:ecology/overworld | dynasty:ecology/sacred_trees / -63–319 | 0–2000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 雷劈古木·电精破壳 | dynasty:ecology/overworld | dynasty:blueprint/tree_habitat / -63–319 | 0–23999 / THUNDER | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 古战场擂台·斗将死斗 | dynasty:ecology/overworld | dynasty:blueprint/battlefields / -63–319 | 0–23999 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 深山鬼打墙·迷雾回廊 | dynasty:ecology/overworld | dynasty:blueprint/shanxiao_habitat / -63–319 | 13000–23000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 幽冥当铺·阴钱市易 | dynasty:ecology/overworld | dynasty:ecology/roads / -63–319 | 17000–19000 / ANY | 72000 / 1:40 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |
| 天河倒倾·神龙飞升 | dynasty:ecology/overworld | dynasty:ecology/snow_peaks / -63–319 | 11500–13500 / RAIN | 480000 / 1:200 | 64 / 1800 | UNIMPLEMENTED / UNIMPLEMENTED |

实例seed、参与UUID、actor UUID、临时方块原状态及奖励托管有保存接口；取消死亡与类型不匹配不能写入击杀，已卸载UUID不算死亡。成功/失败、奖励与清理框架仅验证已运行模板，未实现事件不能声称已拥有原文分支。

## 已有返工人形模型清单

本轮未重绘模型。以下记录实际已有资源，替代过时的“模型全部未启动”报告。头身比为主颅面首个网格到脚部最低网格的静态测量；肩腰比为肩轴距离/腰部首个网格宽，不含甲片外轮廓。空值需要专门视觉测量；测量和骨骼存在不等于握持/穿模/剪影验收通过。

| 实体/职业 | 基础头身比 | 肩轴/腰比 | 骨骼数 | geo / texture | 握持/LOD |
| --- | --- | --- | --- | --- | --- |
| dynasty:zhiren_jianke / PAPER | 7.2 | 1.725 | 33 | src/main/resources/assets/dynasty/geo/blueprint/zhiren_jianke.geo.json / src/main/resources/assets/dynasty/textures/entity/imperial_soldier.png | 5个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:fuhun_baibu_tongzi / CHILD | — | — | 77 | src/main/resources/assets/dynasty/geo/blueprint/fuhun_baibu_tongzi.geo.json / src/main/resources/assets/dynasty/textures/entity/imperial_soldier.png | 9个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:zuwu_daoshou / SWORD | 6.95 | 1.725 | 43 | src/main/resources/assets/dynasty/geo/blueprint/zuwu_daoshou.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 5个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:ludun_jiashi / SHIELD | 7.7 | 2.549 | 45 | src/main/resources/assets/dynasty/geo/blueprint/ludun_jiashi.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 7个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:fufa_jijiu / PRIEST | — | — | 90 | src/main/resources/assets/dynasty/geo/blueprint/fufa_jijiu.geo.json / src/main/resources/assets/dynasty/textures/entity/imperial_soldier.png | 8个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:juma_changqiangbing / SPEAR | 7.4 | 1.627 | 49 | src/main/resources/assets/dynasty/geo/blueprint/juma_changqiangbing.geo.json / src/main/resources/assets/dynasty/textures/entity/archer.png | 6个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:liannu_zhenzu / CROSSBOW | 6.75 | 1.804 | 43 | src/main/resources/assets/dynasty/geo/blueprint/liannu_zhenzu.geo.json / src/main/resources/assets/dynasty/textures/entity/rebel_soldier.png | 6个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:tiesuo_chihou / SCOUT | 7.025 | 1.294 | 56 | src/main/resources/assets/dynasty/geo/blueprint/tiesuo_chihou.geo.json / src/main/resources/assets/dynasty/textures/entity/assassin.png | 6个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:kuijun_sishi / POWDER | 7.2 | 1.686 | 39 | src/main/resources/assets/dynasty/geo/blueprint/kuijun_sishi.geo.json / src/main/resources/assets/dynasty/textures/entity/rebel_soldier.png | 6个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:zhenwang_zhangqiguan / FLAG | — | — | 77 | src/main/resources/assets/dynasty/geo/blueprint/zhenwang_zhangqiguan.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 8个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:pijia_panjiang_huwei / AXE_GUARD | 8.2 | 2.745 | 43 | src/main/resources/assets/dynasty/geo/blueprint/pijia_panjiang_huwei.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 6个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:yinbing_guizu / GHOST | — | — | 24 | src/main/resources/assets/dynasty/geo/blueprint/yinbing_guizu.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 5个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:shibian_lishi / CORPSE | 8.45 | 2.745 | 66 | src/main/resources/assets/dynasty/geo/blueprint/shibian_lishi.geo.json / src/main/resources/assets/dynasty/textures/entity/nian_beast.png | 4个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:jubi_shigandang / STONE_GUARD | — | — | 13 | src/main/resources/assets/dynasty/geo/blueprint/jubi_shigandang.geo.json / src/main/resources/assets/dynasty/textures/entity/royal_guard.png | 0个腕/掌/握点；二级动画24格外停更，网格LOD待验 |
| dynasty:shashui_funigui / DROWNER | — | — | 23 | src/main/resources/assets/dynasty/geo/blueprint/shashui_funigui.geo.json / src/main/resources/assets/dynasty/textures/entity/imperial_soldier.png | 0个腕/掌/握点；二级动画32格外停更，网格LOD待验 |
| dynasty:tongbi_feitian_yecha / YECHA | — | — | 26 | src/main/resources/assets/dynasty/geo/blueprint/tongbi_feitian_yecha.geo.json / src/main/resources/assets/dynasty/textures/entity/nian_beast.png | 0个腕/掌/握点；二级动画24格外停更，网格LOD待验 |

## 11 类 AnimationProfile 完成表

共享枚举/语义已经完成；各物种有独立动画资源，但全部职业覆盖、动作质量、所有击中帧、变TPS、移速与远距LOD仍未整项实机验收。逐clip循环/时长、实际移速属性、二级距离及geo摘要在同名JSON；服务端伤害关键帧直接导出自SkillDefinition，不从画面或同名attack剪辑推断。

| Profile | 适用已注册实体 | 资源/循环/时长 | 二级距离 | 状态 |
| --- | --- | --- | --- | --- |
| LIGHT_HUMANOID | zhiren_jianke, tiesuo_chihou, kuijun_sishi, shashui_funigui | 独立动画；29个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| HEAVY_HUMANOID | ludun_jiashi, pijia_panjiang_huwei, shibian_lishi | 独立动画；20个clip，明细见JSON | 24 | 枚举/映射已验；完整动画质量PARTIAL |
| ARCHER | liannu_zhenzu | 独立动画；7个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| BLADE | zuwu_daoshou | 独立动画；7个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| SPEAR | juma_changqiangbing | 独立动画；7个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| CASTER | fufa_jijiu, zhenwang_zhangqiguan | 独立动画；14个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| QUADRUPED | chimu_zhuha, shanjing_shanxiao, xunshan_mujiaquan | 独立动画；24个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| MULTILEG | mingsha_shixie, bazu_digongzhu, baimu_mowu | 独立动画；23个clip，明细见JSON | 24 | 枚举/映射已验；完整动画质量PARTIAL |
| SERPENT | bishui_xuanjiao_youzi, qingtong_shuangtoushekui | 独立动画；17个clip，明细见JSON | 32 | 枚举/映射已验；完整动画质量PARTIAL |
| FLOATING | muxue_feilu, fuhun_baibu_tongzi, yinbing_guizu, youdeng_guimianfu, xueju_mangguyu, tongbi_feitian_yecha, yinyang_zhijiao_youhun | 独立动画；49个clip，明细见JSON | 24 | 枚举/映射已验；完整动画质量PARTIAL |
| GIANT_CONSTRUCT | kumu_shujing, jubi_shigandang, juli_bixi_kuilei | 独立动画；23个clip，明细见JSON | 24 | 枚举/映射已验；完整动画质量PARTIAL |

## 性能、清理与剩余范围

服务器事件全局最多3个，单维度最多保存256个实例；每20tick事件生成预算为2个，触发每200–400tick分批6个候选。生态空闲行为按UUID错峰32tick、12格查询；地牢只访问已加载marker，不为创建实体新增区块票。现有候选网格间距和上述预算不是生成距离/TPS测量；完整自然结构生成性能、同屏压力及长期多人负载仍未验证。

仍需完成：第一座缺失Boss/精英/最终奖励/美术与完整通关；其余九座地牢与机关；七个缺失生态精英和四个未绑定角色，以及十区原文特殊行为；27个事件的控制器和全部30个的具体原文分支；人形全方位/纯黑剪影/握持穿模验收；11类完整动画同步与LOD验收；旧世界、真实服务器重启及双人完整自然探索测试。以上仍保留在提示词，不标DONE。

## 本轮修改/新增文件

| 文件 | 用途 |
| --- | --- |
| src/main/java/com/dynasty/worldevent/DynastyWorldEventManager.java | 全服务器并发、存活参与/发奖、取消死亡与实体类型校验 |
| src/main/java/com/dynasty/worldevent/WorldEventGameTests.java | 四项新增生命周期回归；异步实体加载测试修复 |
| src/main/java/com/dynasty/blueprint/BlueprintSpawns.java | 已加载实体区块就绪检查；保留其他聊天的独立修改 |
| src/main/java/com/dynasty/dungeon/DungeonFrameworkGameTests.java | 真实驻军测试区隔离，保留实体和持久化断言 |
| src/main/java/com/dynasty/dungeon/DungeonTrapGameTests.java | 冲锤测试区隔离，避免其他房间核心干扰 |
| src/main/java/com/dynasty/blueprint/EcologyRules.java | 复用五种已存在的Cod1原生刷怪器，禁止重复登记 |
| src/main/java/com/dynasty/blueprint/EcologyGameTests.java | 扫描实际Biome刷怪表的重复与入口保留断言 |
| src/main/java/com/dynasty/dungeon/Cod2AuditGameTests.java | 新增：真实注册表、依赖、资源及服务器攻击时间轴导出 |
| tools/blueprint/cod2-test.init.gradle | 可选原生快照导出参数 |
| tools/blueprint/run_cod2_clients.py | 临时QA客户端默认静音 |
| tools/blueprint/report_cod2.py | 新增：以真实证据生成报告，不修改提示词 |
| docs/blueprint-cod2/README.md | 指向最新核验；保留历史记录 |
| docs/blueprint-cod2/IMPLEMENTATION_MAP.json | 校正陈旧状态，保留原始需求和未完成项 |
| docs/blueprint-cod2/DELETIONS_20261010.json | 新增：五段纯删除的原文、行号、备份和哈希 |
| docs/blueprint-cod2/LOCAL_AUDIT_20261010.md | 新增：核验报告；同名JSON保留快照与资源元数据 |

外部 `cod2.txt` 删除三段已验证基础要求，以及本轮完成的实施映射审核和基线构建要求；其他需求原样保留。证据目录仅存文本结果、日志与截图，不包含测试世界或玩家存档。

## 证据

原生快照：`docs/blueprint-cod2/evidence/local-20261010/runtime.json`，SHA-256 `cf1c7d34c3f4195fb49a1e432436c062cd813784a5c2f4cc91e992641a0d7e25`。服务端日志：`docs/blueprint-cod2/evidence/local-20261010/server-integrated2.log`，SHA-256 `9d060f3f62fee6ab909463cd97354618af90ed9639063193ca83708a39aefdf1`。单端：`docs/blueprint-cod2/evidence/local-20261010/solo`；双端：`docs/blueprint-cod2/evidence/local-20261010/pair`。同名JSON保留30事件缺失依赖、10生态阵营/捕食状态、30已注册实体资源与完整服务端技能时间轴。
