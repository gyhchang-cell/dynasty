# 86 Jar 双客户端实际战斗/自然地形探索兼容

状态：fail。0阶段，0通过。两端各86Jar（85生产+1私有QA），实际加载96个mod；固定0e1生产Jar。

四类代表生物：山贼喽啰、灰狼、纸钱鬼、蝠妖。双方原生attack、生产AI实际伤害、单次原生死亡与尸体不重复事件。自然生成地表三处各原生步行126客户端tick；起点与展示摆位为夹具，未铺平台或导入旧档。

## 校验

- complete_37_stages: False
- real_distinct_UUID_TCP: True
- host_all_85_production_jars_retained: True
- host_86_jars: True
- host_0e1_jar: True
- host_complete_exit0: True
- host_input_ack_all: True
- host_actual_world_frames: True
- peer_all_85_production_jars_retained: True
- peer_86_jars: True
- peer_0e1_jar: True
- peer_complete_exit0: True
- peer_input_ack_all: True
- peer_actual_world_frames: True
- three_real_walks_both_move_over5: False
- four_actual_AI_damage_samples: False
- four_single_native_deaths: False

## 实际探索位移

|场景|host移动距离|peer移动距离|生物群系|
|---|---:|---:|---|

## 证据与边界

- run-08/source-snapshot、双端manifest、connections、loaded-mods、input/ack/render/result、原始PNG与日志/退出码全部保留。
- fullpack-report.json记录逐项检查与探索原始坐标，fullpack-visual-review.json记录实际同框复核。
- 完整modpack85生产Jar+私有QA=86Jar，无删mod；仅私有Dynasty换已验0e1
- 普通生成地形新世界，不铺平台，不导入旧档；开始位置与场景镜头可传送摆位，步行阶段126客户端tick实际按keyUp/keyJump
- 生物/初始铁剑护甲/高生命/最后1血高伤击杀是声明夹具；不声称自然获得或自然生成这些测试生物
- dynamic_fps只在私有副本关闭后台限帧；30FPS与2区块渲染是QA运行配置，不代表高负载最坏表现
- 四类战斗、三处自然地表为代表兼容样本，不宣称全模组交叉组合、全30类独有技能、生态生成或自然取得闭合
- 两个自动控制真实客户端，独立UUID与TCP原生C2S，非FakePlayer；不是两名真人，不新增真人门槛

原30类已由主协调独立审计闭合，不以本样本替代其证据；本任务不改待办。
