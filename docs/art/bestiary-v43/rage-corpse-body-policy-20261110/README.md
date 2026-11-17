# 搬山甲胄尸狂：完整身体策略

原任务cod1.txt第10节，保持PARTIAL。

**start_priority**：startSkill server/alive/enemy/sight/vertical delta<=3 and configured horizontal range checks, leap landing safety/home checks, then unchanged TimedAttack idle/cooldown/finite-input gate. AI tries LEAP when squared distance>25, SPIN when<25, otherwise BLOOD; range==25 falls to BLOOD. Actual min/max gates still apply.

**spin_strategy**：Skill40122windup+80active+40recovery=142ticks. Server requests .03 forward/tick for ages22..101 (2.4blocks only if all moves succeed), keeps entity facing original attack direction. Authored ROOT yaw0at22->2160at102, holds to142 (six visual turns). All child body/supports inherit this rendered rotation; server circular damage is not animated root geometry. Hits22,32,42,52,62,72,82,92. Logical facing stays fixed while mesh spins. No claim rotating AABB or skeletal collision.

**spin_body**：coffin_shell windup rocks pitch+3/-3/+3 then returns0at22; recovery rolls+4at112/-4at122/0at142. Foreknuckle roll has sampled windup left+50/right-50at10, returns0at22 and remains baseline. Chain root local yaw reaches-180at22 against authored default180; this interface change is not object asset modification or verified chain collision.

**blood_strategy**：Skill40316windup+25active+40recovery=81ticks, hits16/26/36. Facing locked from attack direction each combat tick. Existing front-knuckle windup rolls reach +/-90 and local Y up to11.03 then return0at16. Blood gates open from +/-8at14 to +/-70at16, hold to36 and close by50; viscera scales1.08at14 and1at16. Gates and viscera are children of coffin_shell, front supports independently root-parented. Server emission origin is bodyposition+direction*1.2+(0,1.5,0), not a bone ticket. Gate/stream alignment requires runtime/world-space validation, no fake completed contact.

**leap_context**：Skill40214windup+20active+50recovery=84ticks, hit33. Physical server clipped parabola age14..33 uses u=(age-13)/20 and vertical8*u*(1-u), maximum2blocks above interpolated baseline. travel suppresses its extra integrator only during this server skill interval, never enables NoGravity. Authored supports lift at14..33 and shell pitches at contact; actual ground contact remains unverified.

**interrupt_exit**：Accepted actual health loss>=12 while server/alive/WINDUP -> stop30stun; movement notloaded/border/obstruction or bad landing -> stop40stun. ACTIVE/RECOVERY ordinary hurt does not use that custom interrupt. stop cancels current action but cooldown remains through reused TimedAttack. At total end current/start clear; missed elapsed frames never dump late damage.

**visual_priority**：death > active401spin/402leap/403blood > hurtTime hurt > horizontal movement walk > idle. Same zero-transition controller/start-reset/world-clock RUNNING adjustment as unchanged giant ape; reusing it adds no reference credit. Gameplay STUN has no dedicated clip; no assumption that hurt is shown throughout recovery/stun.

**death_exit**：die cancels attack/navigation/target, syncs deathStart;80tick removal and4secdeathclip align numerically. Renderer death maxrotation0, death_mud visible flag only while dead; channel keeps mudscale0through16 then1at24, hold60 and0at80. RootY compresses to.45at12, then full-root scale0by78. Blood gates open+/-90by8; back-blade interface transforms depart8..30. No new object/server-entity work. Mud inherits root scale, not an independent floor effect.

**reload**：Custom NBT keeps EliteAttack, landing+finite bounded offsets, LastCombatTick/deathStart/loot/home. Invalid saved leap landing cancels leap. Next combat cancels active on gap>1 or clock reversal; cannot claim seamless unloaded animation. Same consumed-frame/cooldown protections reused; exact client interpolation/network/load ordering not executed.

**complete_comparison**：Closest already fully reviewed local strategy is BronzeGorilla SMASH: both four-support bodies with fixed server clock and strong windup; ape strikes alternate forearm motion with .125step and24/64/42 phases. Corpse401 instead rotates whole root during80active and rocks recovery while moving. Corpse403 instead exposes paired abdominal gates on a fixed direction. These are whole body strategies, not new helpers or new Gorilla species. Do not transplant ape geometry/keyframes or count this comparison as a new external family.

**limits**：This batch completes the selected local static actor policy trace, not native playback, texture acceptance, full continuous curve visual examination or framework internals. No production/model/animation/PNG/UV edits. No Java/game/QA/new instance/sharedJar changes.
