"""Read-only native result/feedback counterexamples; no new immunity credit."""
from reference_evidence import Evidence,row
import json
e=Evidence(40)
U='Quek04__The-Undergarden';E='team-abnormals__endergetic'
def refs(repo,f,names):return [e.ref(repo,f,method=n) for n in names]
rows=[]
rows.append(row(40,1,'undergarden-gloomper-pre-native-hurt-cloud-is-not-refused-effect-receipt','support_only',
 refs(U,'Gloomper',['hurtServer','canBeAffected','getHurtSound']),
 'Full333-line Gloomper class read. Native hurtServer performs a50percent random branch BEFORE calling super.hurtServer: creates600tick radius3 cloud, sets shrinking radiusPerTick to -(7-3)/600, adds100tick VIRULENCE, plays fart sound and invokes addFreshEntity without checking result. It then returns parent hurt result unconditionally. canBeAffected independently rejects only VIRULENCE holder. Therefore cloud/sound can precede parent rejection and are not proof damage applied or effect immunity was invoked. Self immunity is a static own-cloud effect exclusion, not an explicit Boss refusal receipt. No amount>0 guard in override.',
 'Use as a negative control when assessing immunity sound/particle: observe final parent hurt or effect result separately; pre-settlement retaliation is not reliable accepted-hit feedback. Avoid counting the self-effect tag and cloud species as a new independent Boss immunity implementation.',
 'Support0 deliberately. Static effect exclusion is a constant-policy family; pre-parent side effect is already a broad reviewed counterexample family. No credit merely for different animal, cloud particle or effect ID. Main source-path search finds no prior Gloomper row, but unused source does not imply semantic novelty.',
 'NeoForge newer hurtServer conceptual reference only; parent Animal/LivingEntity damage implementation and AreaEffectCloud application not expanded. Full class read, no runtime/cloud spawn/effect success or networking claim. No new production mechanic.' ))
rows.append(row(40,2,'endergetic-nonliving-zero-amount-interaction-versus-invulnerability-return','support_only',
 refs(E,'AbstractBolloom',['isInvulnerableTo','skipAttackInteraction','hurt','onBroken','doParticles','displayFireAnimation']),
 'Complete303-line AbstractBolloom base read. Invulnerability returns own isInvulnerable && not FELL_OUT_OF_WORLD && not CRAMMING, without parent delegation. skipAttackInteraction for Player invokes hurt(playerAttack,0). hurt returnsfalse only at its invulnerability gate; otherwise if alive and server it discards, marks hurt, then invokes onBroken(!creative); even client or already not alive returns true without authoritative break. Base onBroken plays wet-grass break and invokes ServerLevel sendParticles; subclasses override and were not fully read here. Tick additionally clears fire, and independent height exit breaks/discards; neither is proof rejected damage. Amount is ignored, so zero attack is intentional interaction, not a successful HP-damage receipt.',
 'Keep native boolean, authoritative removal and actual hit point damage separate in feedback QA. Nonliving interactable zero-amount success must not be interpreted as successful Boss control or damage. Client true alone cannot establish server removal.',
 'Support0. Nonliving special handling/default invulnerability exclusions and object removal are not a new living Boss immune policy. Do not split out-of-world/cramming or fruit/balloon subclasses into countable variants. No guard research credit reused.',
 'Only full base class plus six complete methods frozen; subclass onBroken overrides, vanilla player attack call chain, removal S2C and sound consumers not expanded. No claim any instance is invulnerable by default or actual native interaction tested.' ))
rows.append(row(40,3,'endergetic-booflo-attempt-retarget-before-parent-success-only-hurt-animation','support_only',
 refs(E,'Booflo',['hurt','actuallyHurt']),
 'Both complete damage methods read in native Booflo context. hurt assigns attack target from living responsible entity before parent damage, unless vehicle; player creative/spectator excluded only from retarget. IN_WALL substitutes0.5, but responsible PuffBug overrides to2.5 with higher precedence. super.hurt boolean gates BOOFLO_HURT animation (only when no current endimation) and true return; false returnsfalse although retarget may already be changed. actuallyHurt repeats retarget and delegates. A target change is an attempt-side effect; actual animation is guarded by native result here, but absence of animation can also mean existing animation, not immunity.',
 'Cross-check feedback consumers against precise server branch: neither retarget observation nor missing hurt animation alone identifies rejection reason. Keep scalar substitution separate from complete refusal; no new immunity behavior proposed.',
 'Support0. Source-specific fixed damage is not a new immunity, and pre/post native result feedback distinction is existing family. This row is a concrete negative-control comparison, not new research credit or species-based counting.',
 'Only complete hurt/actuallyHurt read with neighbouring context, not entire1375-line class. NetworkUtil animation implementation, targeting AI and all parent damage not expanded. No runtime/visual/synchronization success claim.' ))
print(json.dumps(e.finish(rows,[
 'Malignant Aegis and Embers ExplosionCharm fully read again for source selection but already present in main58/other accepted rows; no new reference credit.',
 'SimplySwords full StormbringerParryManager read; exact timed parry/stack identity row already accepted. No rewrapped candidate.',
 'DivineRPG LadyLuna full class read but existing main source entry; excluded. Karos full class read: static explosion rejection and unrelated arena actions; excluded.',
 'MoC Werewolf incoming damage and form context read: fixed gold-tool damage amounts are scalar variation, not immune feedback. Remaining transformation chain not claimed complete.',
 'MineAndSlash DamageEvent ranges read; mana/shield dependencies absent cached source. No partial resource-chain candidate or new credit.'
]),ensure_ascii=False))
