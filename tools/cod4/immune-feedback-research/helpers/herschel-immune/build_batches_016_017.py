"""Serialize manual fixed-source observations; no upstream code is executed."""
from reference_evidence import Evidence,row,reader,SOURCES
import json,re
R='Infamous-Misadventures__Dungeons-Mobs'
P='pending_primary_semantic_review'
S='support_only_not_effective'
def refs(e,f,methods):
 return [e.ref(R,f,method=m) for m in methods]
def at(e,f,name,start):
 paths=list((SOURCES/R).rglob(f+'.java'));assert len(paths)==1
 lines=paths[0].read_text().splitlines(keepends=True)
 assert re.search(r'\b'+re.escape(name.split('.')[-1])+r'\s*\(',lines[start-1])
 end=reader['end_method'](lines,start)
 ref=e.ref(R,f,span=[start,end]);ref['unit']='complete_method';ref['method']=name
 ref['qualified_declaration']='Explicit lexical declaration at fixed line; end_method closes complete containing body.'
 return ref

e=Evidence(16)
w=refs(e,'WildfireEntity',['finalizeSpawn','defineSynchedData','getShields','setShields','getShieldHealth','setShieldHealth','hurt','breakShield','regenerateShield','baseTick','addAdditionalSaveData','readAdditionalSaveData','getHurtSound'])
w += refs(e,'WildfireModel',['setCustomAnimations'])
w += [e.ref(R,'WildfireRenderer',method='WildfireRenderer'),e.ref(R,'DungeonsMobs',method='DungeonsMobs'),e.ref(R,'ModEntityTypes',span=[397,404]),e.ref(R,'ModEntityTypes',method='registerEntity',signature='private static')]
rows=[row(16,1,'dungeonsmobs-wildfire-shared-shield-health-false-result-single-break-and-staged-rearm',P,w,
 'finalizeSpawn sets four shields and 60 shared shield HP. Native hurt with a shield except OUT_OF_WORLD/DROWN subtracts the entire amount, updates last attacker, breaks at most one shield at thresholds or plays hurt sound, then returns false. Thus false can consume defense without HP loss. baseTick separately breaks one remaining shield each tick when shared HP<=0. Each break resets 150-tick regeneration; regeneration restores one shield and 15 shared HP, not full health. Negative shared HP may immediately break a regenerated shield. Synced shield count drives four model bones in one consumer. NBT saves count/HP but not regeneration timer.',
 'Separate refused health damage, consumed defensive resource, and final control admission. A feedback reason must follow the actual branch; false alone cannot label absolute immunity. Review shield recovery across save/load rather than infer it from persisted shield count.',
 'Compared master tf-lich-shield-and-clone-rejection (magic hit removes a layer), tf-mounted-goblin-shared-shield-rejection (shared mounted shield with disable counter), and tf-snowqueen-multipart-shield-native-refusal-sound. Candidate distinction is shared numerical HP overflow, single break per hurt plus subsequent tick cascade and staged resource rearm. All four shields, sounds, sync, model and NBT are ONE proposal; Russell may merge if same semantic family.',
 'Static only. Renderer constructor binds model but no WildfireRenderer registration was found in fixed cached source; no claim of visible registered rendering. No server-only guard in the shown shield resource branch/baseTick, so do not infer authority exclusivity. Defaults before finalizeSpawn are zero. Timer-loss consequence is conditional static observation, not reproduced save/load bug.')]
sq=refs(e,'SquallGolemEntity',['hurt','registerGoals','getActivate','setActivate','defineSynchedData','setAttackID','handleEntityEvent'])
sq += [at(e,'SquallGolemEntity','SquallGolemEntity.tick',207),at(e,'SquallGolemEntity','Activate.start',513),at(e,'SquallGolemEntity','Deactivate.start',545),e.ref(R,'ModEntityTypes',span=[293,300])]
rows.append(row(16,2,'dungeonsmobs-squall-dormant-refusal-cue-selective-wake-and-raid-reactivation',P,sq,
 'Inactive native hurt except OUT_OF_WORLD always plays iron-door impact and returns false. This branch sets target only when the causing LivingEntity itself isInvulnerable; ordinary attackers do not satisfy that condition. Server tick reactivates from a nonnull target OR an active raid; after >200 targetless ticks active form returns dormant. Registered Activate/Deactivate goals broadcast negative attack IDs and distinct open/off sounds; client event resets attack timer. This is damage refusal state, not the existing stomp knockback-cancellation chain.',
 'Keep phase state, explicit refusal cue, and wake-up policy distinct. Do not translate every rejected hit into a target change, and do not claim a quiet inactive phase stays inactive while raid policy can activate it.',
 'Master same source full-file read already supports the separate stomp control path. No credit for reading that file again or for activation animations. Proposed difference is inactive damage gate plus independently authored wake policy/cue; if phase-refusal family already covers it, downgrade this entire row to support0.',
 'Static source proposal, not native AI run. The unusual attacker.isInvulnerable condition is recorded literally, not corrected or recommended. Target selector can independently acquire targets; no assertion that ordinary attacks can never wake it. No dedicated immune text or per-target rate limiter.'))
rows.append(row(16,3,'dungeonsmobs-wildfire-independent-shockwave-side-effects-support',S,refs(e,'WildfireEntity',['shockwave','strongKnockback','causeFallDamage']),
 'Shockwave loops living entities excluding blaze/wildfire by predicate; hurt return ignored, fire and strongKnockback still execute. Fall damage returns false.',
 'Additional negative example that HP refusal does not prove fire/motion refusal.',
 'Generic hurt-then-independent motion/fire and constant fall gate already covered in other helper/master families; zero independent proposal.',
 'No extra native trigger or runtime proof claimed.'))
print(json.dumps(e.finish(rows,['No layer/bone/sound/registration/constant-threshold credit. Clone allied gates and vine wrappers remain screened material, not new independent candidates.']),ensure_ascii=False))

e=Evidence(17)
n=refs(e,'StraightMovingProjectileEntity',['tryToDealDamage','baseTick','tick','canHitEntity','onHitEntity','playImpactSound','vanishesAfterTime','vanishAfterTime'])
n += refs(e,'NecromancerOrbEntity',['baseTick','tickDownAnimTimers','startForming','handleEntityEvent','predicate','registerControllers','defineSynchedData','hasDelayedForm','setDelayedForm','getVanishAnimationLength','getImpactSound'])
n += [e.ref(R,'NecromancerOrbEntity',method='onHitEntity',signature='Entity entity'),e.ref(R,'NecromancerOrbEntity',method='onHitEntity',signature='EntityHitResult'),e.ref(R,'NecromancerEntity',method='registerGoals'),at(e,'NecromancerEntity','ShootAttackGoal.canUse',405),at(e,'NecromancerEntity','ShootAttackGoal.start',416),at(e,'NecromancerEntity','ShootAttackGoal.tick',422),e.ref(R,'ModEntityTypes',span=[492,498]),e.ref(R,'DungeonsMobs',method='DungeonsMobs')]
rows=[row(17,1,'dungeonsmobs-necromancer-orb-native-overlap-impact-outside-ray-cancel-and-root-dismount',P,n,
 'Registered Necromancer ShootAttackGoal spawns delayed-form orb at animation action point. StraightMovingProjectile baseTick calls a server AABB entity overlap loop into onHitEntity(Entity); unlike tick ray path it contains no Forge onProjectileImpact check. Necromancer custom Entity overload skips undead Mob, otherwise sounds via parent, attempts magic hurt, gates only enchant effects on true/alive, then unconditionally ejects all passengers of the target root vehicle, adds projectile delta*2, sounds again, sets vanish40 and broadcasts event1. Hence hurtfalse does not guard root-vehicle topology changes; cancellation of the separate ray path is not evidence the explicit overlap path was canceled. Orb baseTick invokes parent damage BEFORE its own animation timers/motion freeze. canHitEntity does not exclude forming/vanishing, so qualifying repeated overlap can reset vanish timer; parent 200+40 lifetime is still a cap, not immortality. Client event1 sets vanish animation consumed by predicate; this cue is impact lifecycle, not proof HP/control succeeded.',
 'Audit every actual collision ingress and all physical/topological side effects, not only ray impact events or HP result. Record refused damage, dismount rejection, applied motion and attempted-impact animation as separate outcomes; root eject can affect other riders. Animation phase alone is not a control gate.',
 'One complete proposal merges overlap ingress, root-passenger side effect, repeated vanish reset and feedback lifecycle. Different from master dungeonsmobs-native-paired-impact-zones-share-attempt-history-not-health-success (two connected carriers consume shared attempts) and dungeonsmobs-native-stomp-knockback-cancellation-leaves-independent-vertical-control (event helper only guards XZ). Generic hurtfalse-followed-by-motion alone is support0; semantic adoption hinges on actual alternate native ingress plus root topology.',
 'No game/server/Forge event implementation executed. Native parent Projectile internal onHit dispatch not verified here; claim is limited to explicit AABB→Entity overload and separately shown ray branch, not universal event cancellation bypass. Feedback is not gray immune text, and duplicate impact sound remains two static calls without audibility proof. No claim that all contacts pass inherited canHitEntity or that late join reconstructs animation.')]
rows.append(row(17,2,'dungeonsmobs-orb-unpickable-constant-hurt-refusal-and-parent-reflection-support',S,refs(e,'NecromancerOrbEntity',['hurt','isPickable'])+refs(e,'StraightMovingProjectileEntity',['hurt','addAdditionalSaveData','readAdditionalSaveData']),
 'Orb overrides hurt false and unpickable false; parent projectile can reflect by attacker look and replace owner after invulnerability test, but that parent hurt body is overridden for this orb. Parent NBT saves acceleration power only in its own methods.',
 'Do not cite an inherited deflection implementation as reachable when the actual subtype refuses it. Parent persistence excerpt is not proof complete entity persistence.',
 'Constant bool refusal and vanilla-style reflection template are support only; no extra credit or independent candidate.',
 'No reflected-orb claim; no parent engine save implementation read.'))
print(json.dumps(e.finish(rows,['Drowned sibling and constant projectile variants not repackaged. No credit for duplicate sounds, event byte, accessor or registration wrappers.']),ensure_ascii=False))
