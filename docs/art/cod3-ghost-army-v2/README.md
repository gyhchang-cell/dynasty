# 巡猎兵俑：模型交付，贴图待接

秦汉兵俑，身体约2.6米；长兵总顶端约3.04米。scale=1、16单位/米、脚底Y0、朝前+Z。三档模型56/45/24个Cuboid、共同19骨骼；札甲、低盔、分段腰胯与屈曲肢体保持紧凑。

已查看并筛选100张作者画廊参考，来自16个项目，不是100种生物；每张来源与实际借鉴项见references/selected-100.json。未复制外部像素、模型或动画。只学习胸甲与内衬区分、关节连接、低盔和真实握持，不移植参考阵营造型。

步行4秒循环，animation.scenic.idle，无根位移。按每秒0.2米、每周期0.8米向+Z移动，落地阶段与平地世界速度匹配。地形适配属于运行接入，不能拿平地数学检查代替实机地形检查。

validation.json：三档各81姿态，连接、握持、地面接触、所列穿插、循环及UV检查通过。所有图都是软件预览；temporary-material-atlas.png仅材质分区，脸和甲面尚未完成正式绘制。

UV已冻结，正式贴图交接见TEXTURE_HANDOFF.json，模型清单见MODEL_READY.json。未写正式PNG、未启动Java，未更改任务清单。主线程仍需接入模型/编队/地形、正式PNG并进行原生烘焙与游戏检查。

朝向接入：源geo与GeoObjectRenderer无额外调用旋转时均朝+Z，不加Y180。调用方用atan2(direction.x,direction.z)绕Y转向，同时沿同一direction每tick前进0.01米。详见orientation-check.json。已做静态源代码核对，原生方向仍待主线实测。
