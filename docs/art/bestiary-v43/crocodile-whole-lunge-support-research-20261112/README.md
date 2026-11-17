# 鳄鱼：突咬、最终颌部与低伏支撑

**identity**：AlexModGuy/AlexsMobs:Crocodile@09755dade2cfbdf14839e026d3af446f9d3ff843

**read_scope**：Full ModelCrocodile/EntityCrocodile/RenderCrocodile including renderer nestedCrownLayer; whole CrocodileAIMelee/AquaticMoveController/GroundPathNavigatorWide. Inherited native navigation/target lifecycle not fully read here. SemiAquaticPathNavigator reused previous snapping-turtle evidence only, no new credit.

**support**：Basking bodyY+3/Z-3, all four limbY-3; limbroll±30 countered by child hand/foot∓30. Full10progress required, interpolated from actual sit state. Translation cancellation alone does not cancel rotated endpoints. Swimming addsY+2 limb, X75/Z±90 then foot/hand local offsets; no terrain sampler/IK. Actual feet/hand are0-thickness texturedplanes, not thick plates.

**lunge**：23ticks total:2anticipation(bodyZ+2/headX-55/jaw+60),1hold,5forward(bodyZ-14/head-15/jaw+20/alllimbX45),5return(bodyZ+3/head-10/jaw15),10reset. Real contact branch ticks6,7,8 while model forward phase3..8; not a single biteframe. Entity forward velocity adds.02 eacheligibleframe, distance<3.5/LOS andshield/grab conditions separate from mesh mouth.

**final_jaw**：setupAnim final if baskProgress>0 assigns jawX=-headX AFTER grab/bask/animator offsets and idleheadwalk. Thus final jawpitch relative to neck cancels headpitch; earlier jawtargets do not survive, but combined head/neck yaw/roll still apply. During baskProgress0 this assignment absent: animated jawtargets remain. Read both branches, not one frame.

**grab**：Passenger is placed at actor-radius2,actorY+.1 with yBodyRot=wrap(yRot-180); not solved from mouth bone. It can therefore differ from interpolated upper/lowerjaw positions. Passenger damageevery40 and deathroll targetdamageevery10 are distinct consumers, not new creature references.

**deathroll**：ANIMATION_DEATHROLL is a LIVE water attack after victim mounts. Model rotates bodyZ-1080 through30ticks, entitydeclares40; exact sharedModelAnimator has no authored offset during30..40 (equivalent fullturn orientation approaches identity), procedural swim/grab layers continue. No death clip/reset sequence or death-ground-contact example.

**movement**：Entity stops navigation during roll; shouldStopMoving trueforroll/sitting; AquaticMoveController adds buoyancy.005 BEFORE speed0+return, so stopped speed is not zerovelocity. Travel in water moves currentdelta then damps.9. No claim stationary/footplant. CrocodileAIMelee blocks passenger cases atcanUse/continue and invokesdoHurtTarget basedreach; entitysetter onlyassignsanimation.

**state**：ground/swim/bask/grab each0..10 plusprev interpolation; sourceconstructor random.nextInt(1) yields onlystyle0, althoughNBTstyle1 and mirrored branch exist. Hurt clears sitting; flags/timers/stun persist, exact transient animation/progress/passengertimer not savedbythisclass. No diedeath/tickDeathoverride; inherited deathroll not conflated.

**bixi_application**：['Inspect final jaw assignment after all authored/procedural transforms before judging bite closure', 'Use independent support compensation and check actual vertices; matching counterrotation is not plantedfoot guarantee', 'Keep server actor-based sector and visualmouth markers separate', 'Bixi is mechanical hip/piston/foot; Crocodile small planar feet offer no piston continuity solution']

**limits**：No copied geometry/UV/PNG, native replay, target contact/terrain validation or production repair. Same previouslyseenCrocodile identity; extended wholeconsumer reading only.
