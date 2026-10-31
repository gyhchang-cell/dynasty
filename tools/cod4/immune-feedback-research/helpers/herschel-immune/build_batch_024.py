"""Owner-qualified native tame/control mutation; horse and animal adapters merged."""
from reference_evidence import Evidence,row
import json
e=Evidence(24);R='TeamPneumatic__pnc-repressurized'
def m(f,names):return [e.ref(R,f,method=n) for n in names]
refs=m('AbstractTameableHack',['canHack','getHackTime','addHackInfo','addPostHackInfo'])
refs+=m('HackableTameable',['getHackableClass','onHackFinished'])+m('HackableHorse',['getHackableClass','onHackFinished'])
refs+=m('HackManager',['getHackableForEntity'])+[e.ref(R,'CommonArmorRegistry',method='getHackable',signature='Entity entity, Player player')]
refs+=m('IHackableEntity',['canHack','_getHackTime','_onHackFinished'])
refs+=m('HackHandler',['tickEntityHack','setHackedEntity'])+m('PacketHackingEntityStart',['handle'])+m('PacketHackingEntityFinish',['handle'])
refs+=m('EntityTrackEntryHackable',['addInfo'])
refs+=[e.ref(R,'HackManager',span=[112,112]),e.ref(R,'HackManager',span=[121,121]),e.ref(R,'NetworkHandler',span=[176,181])]
rows=[row(24,1,'pnc-native-hack-owner-difference-admission-and-direct-retame-control','pending_primary_semantic_review',refs,
 'Native registered TamableAnimal and Horse hacks share AbstractTameableHack.canHack: returns (TamableAnimal && playerUUID!=ownerUUID) OR (Horse && playerUUID!=ownerUUID). It does not call IHackableEntity.super.canHack, does not require untamed status, empty owner or player-is-original-owner; null owner differs and another owner also differs. Thus same-owner is the explicit qualification refusal, not universal refusal of already-tamed animals. Default class+alive predicate is not inherited here; server tickEntityHack still separately checks alive when committing. Common registry picks a matching canHack implementation; entity cache can return a prior object between periodic prunes without per-call rechecking ownership. Final server onHackFinished does not repeat ownership guard: stop navigation, clear target, setHealth20, setOwnerUUID(requesting player), broadcast success7, then setTame(true,true) / Horse.setTamed(true). Existing owner is overwritten on the shown path. Animal cat variant branch is same action context, not an additional control policy. Both client finish bodies call handleEntityEvent7; server also broadcasts native7. Finish packet/HUD carries only shared operation entityID/time information, not old/new owner or confirmation the intended owner change was admitted.',
 'An ownership-changing control needs qualification at final mutation, with a result separate from predicted/local success particles. A check that refuses one owner identity is not protection for other owners. For Boss immunity design, explicit source/target qualification must precede target clearing and persistent ownership mutation; never infer immunity or accepted control from generic tame hearts. This is a research counterexample, not an instruction to add taming/PVP mechanics.',
 'One candidate for owner-identity-qualified direct control/re-tame policy; TamableAnimal/Horse/cat variants and all success7 emitters merge. Shared native hacking ingress/cache/tick/finish/HUD already documented in023 and master PNC families; zero extra for wrappers. Not the guard-ownership ledger and no credit transfer. Russell must assess whether this ownership-control example is sufficiently relevant/independent; helper suggested/research credit0.',
 'Static source93d04cc52714742c4ef747eed82528d0fdbde581 only. Do not assert actual theft, double hearts, owner AI alliance after transfer, engine setHealth clamp, native TamableAnimal event mediation, failed tame outcome or network correctness without engine/runtime evidence. No claimant/source distance/LOS exploit demonstrated. No per-target immune text throttle or Boss refusal asserted. No changes to production, assets or TODO.')]
print(json.dumps(e.finish(rows,[
 'Merge two native tame adapters and cat appearance into one owner qualification family. Existing framework context earns no count.',
 'Creeper onHackFinished only calls ignite; no full native fuse/explosion admission consumer examined, so not proposed as an immunity/control implementation.',
 'Native same-owner refusal is documented literally; do not rewrite it as already-tamed refusal. Local source only, no runtime/game/GUI/compile.'
]),ensure_ascii=False))
