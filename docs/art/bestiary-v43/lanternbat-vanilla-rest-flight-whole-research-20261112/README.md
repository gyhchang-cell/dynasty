# 幽灯鬼面蝠：原版蝙蝠倒挂/飞行整机制研究（待核收）

固定Minecraft1.20.1 / Forge47.4.10映射来源归档，SHA核验后只按ZIP读取三个完整类：Bat、BatModel、BatRenderer。模型与实体状态/移动、渲染抬升分开研究。

关键结论：原版两级翼根/翼尖锁相，头与身体是同级节点；倒挂切到飞行没有重新赋值翼根X，不能以单帧冒充所有轴均复位。模型拍翼频率与flapping事件频率也不能混为一谈。

目标实际注册为dynasty:youdeng_guimianfu，保留现有四翼指、灯笼和爪挂点。完整只读LanternBatBehavior，锁定已有18/32/40tick俯冲消费者与碰撞中断，不修改技能时序。不把原版随机飞行当作俯冲参考，不代做灯笼物件。

实际read范围、源哈希、整族应用和限制见source-manifest.json、exact-task-scope.json、whole-study.json。新候选待Main独立核收，正式新增0；适用1000总数及缺口未知。未改认可资产、主清单或共享Jar，未运行游戏/Java/声音/亮度/焦点操作。
