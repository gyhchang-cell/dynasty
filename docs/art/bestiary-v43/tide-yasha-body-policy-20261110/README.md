# 伏波巡海夜叉：身体动作政策

原任务：cod1.txt 第9节；保持PARTIAL，未删除提示词。

**trigger_and_selection**：Server only startSkill validates alive/registered skill/enemy/sight/horizontal range, plus real surface for DIVE and no existing owned vortex for WAVE. TimedAttack tryStart is the same unchanged idle/cooldown/finite-input contract already reviewed. AI tries combo at squared distance<=20.25, then dive when>16, then wave; actual skill min/max range gates still apply.

**combo_whole_action**：Skill393 total84ticks: WINDUP0..9, ACTIVE10..43, RECOVERY44..83. Three movement windows10..19,22..31,34..43 inclusive, each10steps*.2=2blocks if unobstructed. Step is collision move before impact19/31/43; unloaded next cell or displacement squared<.005 cancels to30tick stun. Third window at34 adds vertical.38 only onGround. This is a conditional intended distance, not actual path/contact acceptance.

**combo_body**：carapace->fork_hinge->fork_foresegment->fork_clamp->trident. Local hinge yaw -35at10/+18at19, -30at22/+18at31, -35at34/+15at43; returns0at50. Foresegment roll -10at10/+15at19, -10at22/+15at31, -20at34/+30at39/+5at43, return0at54. Carapace and tail-tip provide smaller counter-motion. Tip attack query is body-position plus fixed right/forward offset, not sampled from rendered bone; matching fork tip to query is unverified.

**dive_whole_action**：Skill392 total71ticks:30windup/1active/40recovery; impact30. Pool follows valid target surface through age<=20, then locks. Renderer root+children hidden iff392 and age>=9 and<30 and notdead. Authored root Y scale1->.08at8, holds through30, restores1at34. At30 emergence seeks one loaded unobstructed nearby location with height/home/distance/sight checks; failed emergence cancels30tick stun; valid emergence teleports once, faces pool and adds vertical.3. Animation alone is not server teleport/hit source.

**wave_context**：Skill391 total82ticks; impact18; hinge windup yaw-12at12 then+10at18, vent scales peak1.25at17 and return18. Existing trident rotation channel is read as attachment transform only; no weapon object modifications.

**body_priority**：death wins, then active skill391/392/393, then hurtTime hurt, horizontal motion walk, idle. Incoming ordinary hurt does not visually replace an active skill. No separate STUN clip branch. Gameplay stun may outlast hurt clip and display idle/walk.

**interrupt_exit**：Accepted server damage while alive with actual health loss>=8 and WINDUP stuns20 and immediately syncs. ACTIVE/RECOVERY do not use this custom interrupt. Death cancels attack, clears owned effects, navigation/target, syncs deathStart and chooses death; getDeathMaxRotation0 avoids additional whole-model death roll. Server removes at80ticks. No sound/game operation executed.

**visibility_death**：Renderer recomputes root/children hidden every custom animation call, so current skill cancellation or dead state clears dive hiding on next invocation. Reef shell+children hidden while alive, visible flag while dead; death scale then fades reef0 through24 to1at32. Live carapace scales1 through24 to0at32. Six root-parented legs remain until54 and scale0at76. Death effect fragments inherit reef_shell; not new server entities. Planted weapon/normal weapon visibility is an interface read only, not item production.

**clock_and_load**：Same0-transition controller as giant ape: reset on START change, loop idle/walk, hold-last others, RUNNING age from gameTime-START+partial except initial reset pass. Source save/load stores EliteAttack, pool, LastCombatTick, deathStart, loot flag/home. Invalid distant saved pool cancels DIVE; time gap>1 or reversal cancels active action on next combat. TimedAttack retains consumed frames/cooldowns, does not dump delayed hits. Not a seamless controller phase/blend persistence claim.

**external_whole_comparison**：Pinned Alex Lobster ticks target proximity<=1 and cooldown0 -> doHurtTarget writes ATTACK_TICK5 and calls super.doHurtTarget immediately; same class later applies target hurt2 when count2 and distance<1.3. Counter decrements and attackProgress ramps0..5 then decays; model interpolates prev/current progress, yaws paired arms+/-45 and hands-/+30, layered with idle/locomotion. Counter/damage tick block lacks its own explicit side guard; inherited damage behavior is not proved here. Do not transplant this double-path hit logic or treat visual peak as authoritative hit. Own custom NBT only variant/fromBucket, not counter/progress/cooldown; no own hurt/death cancel override. Inherited death/network/math helpers unreviewed, no complete engine/runtime claim.

**comparison_boundary**：Lobster is relevant low aquatic shell with linked claw articulation; it is not an underwater teleport/combo boss and supplies no proof for Yasha dive timing or balance. Transfer only connected parent-child body articulation and explicit attack-progress/return assessment. Existing Yasha body is six-foot shell, not Steve and not being converted.

复用范围：不重读原300卡；保留旧1000结构与3项100账。适用完整累计及缺口为null。所有模型、动作、物件和UV保持。
