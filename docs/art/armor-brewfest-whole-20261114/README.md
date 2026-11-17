# D93：Brewfest 旧家族完整穿戴消费链核对

本轮仅参考研究，未制作或覆盖 Dynasty 贴图。保留289已认可资源与70优先路径，哈希前后一致。未启动游戏、未改变声音/亮度/屏幕、未触碰用户实例、共享Jar、主清单或主协调session。

固定本地 Brewery Fabric2.0.6 Jar，SHA256见 provenance.json。实际查看8张16×16图标、2张64×64服装图集、2张32×32帽图集；原图仅整数近邻放大展示。全部8图标与2服装图集和原记录逐字节一致，两张帽子穿戴图只补齐同一家族绑定，因此不增加参考设计数。

已核对实际物品注册bootstrap→工厂→纹理getter→Fabric四renderer→ArmorRegistry物品identity/cache/bake→四custom model层bootstrap。4个模型共17个Cuboid/平面声明（头4、胸8、腿3、脚2），不是普通layer1/layer2。详见 four-slot-binary-bindings.json、model-declarations.json 和 actual-review-scope.json。

实际查看原始腿部相对条与胸部前背候选矩形：lederhosen各腿条20/48不透明，dirndl40/48；body helper各124/384和256/384，不能沿用厨师服同矩形全透明的结论。裤子body helper不复制身体pose、帽檐负UV和零厚度平面、左右袖构成不对称均需单独看待。矩形检查不是已确认方向/镜像或实机穿戴验收。

原始图与消费链仍属于历史 functional_brewfest_clothing 家族；红帽换色、配方和模型子部件不计独立设计。总有效适用设计数与距1000的缺口尚未核实（null），gate=false；保留此前已认可参考，不清零。未删除任何待验提示词。

学习点：正面开口与背面连续格纹以硬边像素明确区分；吊带与腿片分别核对；避免用横短鞋、宽檐帽直接替代原版盔甲比例。下一步继续其他完整相关家族的实际原图与消费链证据。
