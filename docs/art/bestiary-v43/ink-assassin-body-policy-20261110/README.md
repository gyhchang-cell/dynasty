# 墨家绝影刺客：完整身体动作政策

原任务cod1.txt第11节保持PARTIAL，原待办正文不复制。

**trigger**：startSkill validates server, alive, enemy, sight, heightdelta<=2 and configured range; FIELD additionally validates same-height four floor anchors and clear rays before tryStart. Same unchanged TimedAttack clock/cooldown gate reused. AI tries stealth at distanceSquared>16, field at<36, then mist; conditions still pass skill min/max gates. Partial field creation failure cancels rather than leave a body action running.

**conceal_whole_policy**：411 total111ticks=70windup+11active+30recovery, hit80. concealed() uses skill411 and age1..79 and notdead. combat sets Invisible by same age; renderer independently hides ROOT and children from concealed(), not transparency alone. Start clears target references on at most16 nearby mobs currently targeting this entity, not universal aggro immunity or collision removal.

**mark_and_backstab**：For age<70 follows target-derived behind point with floor validation; at70 stops tracking for last10ticks. At80 clears invisibility, tries one blink to saved mark with distance<=8, height<=2, home/loaded/full-body clearance/ground/ray gates. Faces target, requires rangeSquared<=4 and clear ray, then compares current target view dot offset<-.5 for3x versus1x damage. Turning cancels bonus, not necessarily the ordinary hit. Failed blink stops30stun.

**conceal_body_channels**：rootY scale1->.25by4, holds78, restores1at80; fold wings reach-/+20by4, hold78 and recover80. Most fold compression is under root hidden state, so authored scale alone is not a visible dissolve proof. Daggers/carriages are read only as attachment interfaces: local carriage X-/+5 and dagger yaw+/-180at80..86, return94. No dagger assets edited.

**field_whole_policy**：412 total92ticks=10windup+46active+36recovery, impacts15/27/39/51. Current cast must have four owned matching-start anchors during age10..55; target loss/out-of-home cancels. Four diagonal route stages begin10/22/34/46, each ten collision-step requests toward opposite corner. At begin tries bounded blink to route start; step verifies loaded/success displacement. Stage gaps20..21/32..33/44..45 do not run a step for next stage. Damage uses current body circle1.1, not mesh dagger tip. Four routes/hits are one strategy, no new reference credits.

**field_body_and_break**：Wings-/+15 at10 through56, recover64; carriage translation+/-5 and dagger turn held through56; carriage yaw alternates at attack ticks15/27/39/51. InkSpike accepted hurt or die invokes breakField; caster only stops30stun if current FIELD and owned spike castStart equals current attack.started. Anchor expiry56, missing/wrong/dead owner, cast mismatch or time gap discards anchor. Prior cast spikes cannot intentionally break a later cast. No native sweep or packet acceptance claimed.

**mist_context**：413 total59ticks=8windup+21active+30recovery, emits8. Real .16backward step at ages1..6, intended .96distance only if unobstructed. Wings flare-/+35at3, recover by8; heart scale1.15at6, reset8. Cloud cap/pellet renderer declarations were seen in actor context, but whole cloud effect lifetime/texture/native blind acceptance not reviewed here.

**state_priority_and_interrupt**：death > skills411/412/413 > hurtTime hurt > horizontal movement walk > idle. Accepted actual healthloss>=6 on alive server while WINDUP stops25stun. Missing/invalid target or out-of-home target stops20; blocked route/broken field/blink failure usually30. stop cancels attack retaining cooldowns, clears invisibility and field, stops navigation, cancels visual event, syncs immediately. No distinct STUN body clip; gameplay stun can display idle/walk after hurtTime ends.

**death_visibility**：die cancels attack, fields/clouds, invisibility/navigation/target; syncs deathStart and chooses3sec death. ROOT hidden calculation becomes false because concealed requires notdead. death_wash visible flag only while dead; scale0through14 then1at20,1.3XZat46 and0at60. Root Y compresses.18by12, XZgrow1.2by40, entire scale0by58. Death renderer adds no whole-body roll; server removes when max(deathTime,gameTime-deathStart)>=60. Root-child wash inherits compression, not independent world mesh.

**reload**：NBT stores EliteAttack, mark+finite bounded offsets, LastCombatTick/deathStart/loot/home. Invalid mark cancels action; alive reload syncs and derives Invisible from concealed(), dead reload explicitly clears it. Next combat gap>1 or clock reversal cancels active, clears field/invisibility. Shared TimedAttack fired/cooldown safeguards retained, no phase-continuity claim. Exact client scale reset when switching to clip without root scale, network visibility ordering and death/load rendering remain native acceptance gaps.

**dedup_comparison**：Closest completed local whole body is TideYasha: both use actor-dependent root hiding, but Yasha dive hides9..29 and emerges once30; this stealth has moving mark->10tick lock->back-angle check80 plus matching-cast breakable field. Shared controller/clock and hide helpers are reused, not counted as another reference. Existing body is folded ink ray, not a human conversion.

**limits**：Complete selected actor static body policy, not whole runtime/client engine or object effects acceptance. No model/PNG/UV/animation/logic edits, no Java/game/QA/instance/sharedJar/main list changes.
