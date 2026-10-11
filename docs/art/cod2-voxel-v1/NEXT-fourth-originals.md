# 下一批原件审核（未修改资源）

2026-10-11 02:02 保存并实际检查下列原件五视图。开始写资源前必须重新比较 source/*/baseline.manifest.json 的当前 SHA，发现不同不得覆盖。

- 百目魔蜈 baimu_mowu：68 骨骼 / 133 Cuboid。当前平直长箱列、左右细杆腿缺少膝/足连续体块，主要灰嘴没有读得清的颚/眼。应使用逐节专用骨架、粗阶梯弯腿和厚背甲，收敛细碎装饰，保留眼 eye_* 发光条件与吊顶挂点。7 个 clip：idle/walk/run/attack/gaze/hurt/death。
- 碧水玄蛟幼子 bishui_xuanjiao_youzi：47 骨骼 / 69 Cuboid。当前细长矩形蛇列、鼻面没有眼/颚身份、UV 白点接缝；须使龙首/颈/胸腹/鳍/尾专用树、弯曲粗阶梯体块，保留水中 coil 名称与原接触时钟。7 clips。
- 赤目朱蛤 chimu_zhuha：34 骨骼 / 57 Cuboid。已有蛤蟆紧凑轮廓和粗后腿，可保留物种识别；目前暗灰方箱头、黄色钉点和灰白舌，红眼与朱色不突出，UV 接缝串色。重做原生 16×16 四色色岛和实际表面，强化宽口、粗下颚、后腿/足与清晰毒囊；必须保留 tongue_reach identity wrapper（生产按范围缩放）、venom_gland_*/eye_* 发光名称，以及 attack/leap/burst 三个特殊动作。8 clips。
- 符法祭酒 fufa_jijiu：90 骨骼 / 123 Cuboid。已有帽、宽袍、袍袖、法杖和符条职业身份，不按 Steve 模板改造。保存胸/腰/骨盆分层与程序 IK/惯性 identity 骨骼，减少细碎重复甲边与窄侧厚度问题；使用四色色岛 UV、夸张阶梯法冠、握杖手和厚袖/袍体。8 clips：walk/run/idle/buff/attack/skill/hurt/death。务必检查实际握点和袖/符惯性，不能把可用结构全丢掉。

制作之前另写主要比例、骨骼及动作计划；本页只是实际原件的问题记录。所有 png 白底一像素边距、16×16、四色含白、色区≥2×2，无模糊和抗锯齿。遵守 AGENTS.md；保持战斗、任务、AI、碰撞尺寸和他人 dirty 成果。依次通过静态/五方向/动作/构建/JAR 哈希/真实 Forge 静音隔离客户端后才能标 completed。已有前十模型不得由旧生成器覆盖，新增 id 要加入 owned-models.json 并仅增加对应贴图路径。
