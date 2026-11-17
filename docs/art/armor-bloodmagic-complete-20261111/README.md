# D41 已固定本地源：Living完整套装补齐

继续既有本地 Blood Magic 1.20.1-3.3.7-49.jar，归档SHA256 `e88af6d512e522a47286fc87015ed290c5d41be7a51c3ef59a391e85bc1fd4a0` 与D9历史收据吻合。历史只看头裤靴，此批补齐胸甲、L1/L2图集及四个实际注册名、supplier/bootstrap、ArmorItem.Type与纹理选择。13个原生entry逐字节核对，六张原图实际查看，旧三图相同像素不计新图信用。

完整物品名：bloodmagic:livinghelmet、livingplate、livingleggings、livingboots。Bootstrap97..100对应supplier93..96，四Type为HELMET/CHESTPLATE/LEGGINGS/BOOTS；ItemLivingArmor.getArmorTexture按Item身份选头胸靴L1、裤L2，否则null。只是只读javap反汇编，没有加载或执行模组类，没有启动游戏。

观察：深红短宽胸片、金色短横带、头盔金面框、裤腰红带及金护胫构成材料连续性；L1大块暗红与有限金边，L2暗棕腿面和连续红横带。保持MC部位轮廓，少量强调材料。只学组织方法，不复制像素。

该套旧名称完整性升级，不新增名称或保守组，不增加有效独立设计信用。旧sentient残留纹理不等于当前注册/可获取套装，本批不认定其有效整套，也不声称它是游戏故障。累计仍654名称、640盔甲名称、215学习组；1000门槛未达。

本轮本地候选排查记录见 ../armor-local-continuation-20261111/ 。2861是按文件名和大小粗去重的归档元数据扫描数量，不是内容独立归档数、设计数或人工阅读量。86候选包含本项目资产和旧注册名别名，均没有新设计信用；不能宣称全部本地参考已经穷尽。

289保护文件无变化，无生产修改、共享Jar覆盖、游戏启动或清单删除。完整穿戴/外部渲染/独立图审仍待验。Main回传的PNC来源root桥与透明层消费者缺口已另存，不重复旧辅助验证。
