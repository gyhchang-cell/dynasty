from review_batch import record
rows=[]
for i,other,note in [
('dfe352090bbdd9304231','0c0613ed6cfe098c73c0','完整DraculaFightData上下文与真实LevelTick/Chalice/Dracula.die消费者补读，实际owner已计；外层Serializer.read不是第二实现。'),
('2cc5dc257a6bed989b15','e411d08ca6ded4093aa8','完整AdvancedHunter与level派生属性、specialArrow实际射击已读；旧combatant族已含本reader及库存重建边界，不重复。'),
('53b7ac046a1c05d406b4','e411d08ca6ded4093aa8','完整AdvancedVampire reader/writer/level/mobGoal已读，与上述已计族同源近克隆，不因不同阵营加信用。'),
('27a4d93f5b774076812a','e9a2fd0f296b61c9527c','完整RemainsDefender reader/writer/tick/child damage/actual attack consumers补读；已计聚合方块owner的child attachment，不拆面朝向或LightTicks。'),
('d05824832528da0e0f8d','35131021fa6b2cf9da4a','完整CurableConvertedCreature接口上下文补读；计时器、支付、服务端扣减、startConverting调用已属已计原实体/治愈完整链，不把接口另算。')]:
 rows.append(dict(candidate_id=i,status='duplicate',duplicate_of=other,reason=note,supporting_candidates=[]))
rows.append(dict(candidate_id='80bedfa654647460591f',status='rejected',reason='完整ConvertedCreature接口：readAdditionalSaveDataC/write均空，客户端和平discard不是持久恢复实现；0信用。'))
record(192,rows,[
 'tools/cod4/legacy-migration-acceptance/.work/sources/TeamLapen__Vampirism/projects/vampirism/src/main/java/de/teamlapen/vampirism/common/world/LevelEventHandler.java',
 'tools/cod4/legacy-migration-acceptance/.work/sources/TeamLapen__Vampirism/projects/vampirism/src/main/java/de/teamlapen/vampirism/common/world/blocks/ChaliceBlock.java',
 'tools/cod4/legacy-migration-acceptance/.work/sources/TeamLapen__Vampirism/projects/vampirism/src/main/java/de/teamlapen/vampirism/common/world/entity/dracula/Dracula.java'])
