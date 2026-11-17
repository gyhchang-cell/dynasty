"""Preserve exclusions and complete native context; no research credit added."""
from reference_evidence import Evidence,row
import json
R='Infamous-Misadventures__Dungeons-Mobs';A='Tslat__Advent-Of-Ascension';S='support_only_not_effective'
e=Evidence(18)
def m(f,methods):return [e.ref(R,f,method=x) for x in methods]
refs=m('SnarelingEntity',['baseTick','performRangedAttack','registerGoals','defineSynchedData','getShootTime','setShootTime'])
refs+=m('SnarelingGlobEntity',['onHitEntity','onHit','handleEntityEvent','getParticle'])
refs+=m('EnsnaredEffect',['applyEffectTick','isDurationEffectTick'])
refs+=[e.ref(R,'ClientEntityEvents'),e.ref(R,'EntityEvents'),e.ref(R,'ModEffects'),e.ref(R,'ModEntityTypes',span=[387,394]),e.ref(R,'ModEntityTypes',span=[573,579]),e.ref(R,'DungeonsMobs',method='DungeonsMobs')]
rows=[row(18,1,'dungeonsmobs-ensnared-native-source-to-server-motion-and-input-control-support',S,refs,
 'Native Snareling baseTick starts shootTime80 for unsnared visible target and server fires at15; performRangedAttack creates glob. Glob onHitEntity excludes AbstractEnderling ONLY from 3damage, then independently attempts ENSNARED100 on any Living server target and ignores addEffect result. onHit broadcasts slime event3/removes onserver and plays land sound independently of admission. Effect server tick zeros XZ but preserves Y, sets speed0; registry adds -5 MULTIPLY_TOTAL speed modifier. Subscriber cancels knockback while effect present, and conditionally cancels attack/item/block/bucket actions. Client subscriber calls getMoveVector().scale(0) without assigning its return and explicitly clears jumping; dependency vector API not in this fixed cache, so no claim that first call mutates stored input. No raw client xxa/zza assignment shown.',
 'Useful native counterexample: damage type immunity/absence of health hit does not imply status refusal; land particles/sound do not certify effect admission. Trace vertical and horizontal control plus client input separately. Input return-value concern needs dependency source before treating as a defect.',
 'Zero proposal: compare master spellengine-final-input-and-active-item-control-gates and goety-native-stun-applicability-denial-versus-explosion-push, plus earlier Wizardry paralysis. Event wrappers, effect constant, slime FX, and differently named status do not establish a new independent family. Full chain retained for Russell support only.',
 'No dependency Vec2/Input implementation or runtime validation. Effect immunity/applicable hook remains inherited. Do not infer every event is cancelable: code checks isCancelable for most wrappers; right/left empty may remain noncancelable. No server/client synchronization receipt verified.')]
rows.append(row(18,2,'dungeonsmobs-windcaller-root-eject-before-native-knockback-support',S,[e.ref(R,'WindcallerBlastProjectileEntity')],
 'Complete projectile file: server impact first rootVehicle.ejectPassengers; Living then native knockback2, nonLiving direct motion1.5 plus0.5Y; hurtMarked true. It never attempts HP damage. canHit excludes owner and shared-vehicle owner relations. Therefore knockback resistance or event cancellation cannot retroactively guard an already executed root eject.',
 'Root topology control must have its own admission before mutation, not inferred from HP/knockback outcomes.',
 'Same root-eject control family as pending017; preserve semantic comparison, not another independent implementation credit. Native producer Windcaller attack goal not included, so cannot promote anyway.',
 'No native knockback internals or attack-goal producer read; parent AbstractHurtingProjectile impact dispatch not validated. No game claim.'))
rows.append(row(18,3,'dungeonsmobs-drowned-orb-sibling-overlap-and-root-eject-support',S,[e.ref(R,'DrownedNecromancerOrbEntity')],
 'Complete sibling projectile: inherits same AABB base path, skips undead Mob, hurt bool gates enchant only, root eject/motion/impact cue then immediate discard. Its own baseTick first calls parent damage and only afterward removes when not in water/rain/bubble. Water-only lifetime guard therefore is not a pre-hit gate in this body.',
 'Ordering support for environmental destruction versus already performed collision, and distinction from Necromancer visual vanish timer.',
 'Merged with017 overlap/root topology family. Different damage number/water lifetime/immediate disposal do not earn separate credit here.',
 'Actual drowned producer not traced; no runtime claim or assertion all dry spawning hits targets.'))
rows.append(row(18,4,'aoa-commented-crystocore-and-proshield-not-native-implementations',S,[e.ref(A,'CrystocoreEntity'),e.ref(A,'CrystocoreRenderer'),e.ref(A,'ProshieldEntity')],
 'Read complete fixed files: each entire Java package/class body is enclosed in /* ... */. Crystocore legacy phase/texture and Proshield legacy melee reflect/startRiding refusal are text inside a block comment at this commit, not active Java implementations.',
 'Reject attractive archived mechanics as present native evidence. Hash-valid source is not sufficient for actual game reachability.',
 'Zero credit and zero candidate; no rebranding commented methods or splitting phase textures. Does not question separately active AoA master entries.',
 'Comment status is confined to these three pinned files; no claim about all AoA classes or older releases.'))
print(json.dumps(e.finish(rows,['Aether ShieldOfRepulsion read: already covered stationary-defense/vignette family; no row or duplicate proposal. Swet class absent in selected local cache; no claimed read.']),ensure_ascii=False))
