"""Explicitly excluded fixed-source and already-reviewed DivineRPG chains."""
from reference_evidence import Evidence,row,reader,SOURCES
import json
e=Evidence(27);R='DivineRPG__DivineRPG';S='support_only_not_effective'
refs=[e.ref(R,'EntityKaros',method=n) for n in ['hurt','manageAbilities','tick','getAmbientSound']]
p=next((SOURCES/R).rglob('EntityKingOfScorchers.java'));lines=p.read_text().splitlines(keepends=True)
assert 'boolean hurt(' in lines[49]
ref=e.ref(R,'EntityKingOfScorchers',span=[50,reader['end_method'](lines,50)]);ref['unit']='complete_method';ref['method']='hurt';refs.append(ref)
refs+=[e.ref(R,'EntityDivineBoss'),e.ref(R,'EntityDivineMonster')]
rows=[row(27,1,'divinerpg-karos-scorcher-identical-exact-explosion-denial-and-ambient-quip-support',S,refs,
 'Read full Karos/KingOfScorchers classes. Their native hurt both immediately false for source.is(DamageTypes.EXPLOSION), otherwise parent; no explosion tag test, per-hit receipt or stateful unique policy here. Karos manageAbilities ceiling choice emits explosion skill warning and voice before block effects, while getAmbientSound independently picks laugh/doom/try-your-best/you-cannot-kill-me dialogue then sends to AABB expanded towards positive30 each axis. These quips are ambient selections, not produced by refused explosion hit. Intro game/begin messages are sequential actionbar calls during initial block scan. Parent Boss native knockback is empty, ordinary health bossbar progress and player seen/unseen membership; generic wrappers not separate proposals.',
 'A boast that the target cannot be killed is not semantic evidence this hit was immune. Exact-source refusal cannot be broadened to all explosive-tagged damage. Keep actionbar/voice encounter cues separate from denied-hit receipt and verify asymmetric AABB rather than interpreting30 as radius.',
 'Support0: same exact-source constant refusal in two creature names is one trivial template, not two new independent game policies; adjacent source-only immune families already represented. Dialogue random variants and base Boss wrappers0. No claim every line is newly relevant merely because full class read.',
 'No runtime, generic engine hurt/ambient scheduling or LocalizeUtils internals proof. No world-space text/depth, receipt throttle or pixel/sound acceptance. World-altering Karos block skill helpers not researched as new immune implementations; no production changes.')]
print(json.dumps(e.finish(rows,['Ayeraco full class re-read against master divinerpg-native-spatial-companion-class-selective-immunity: native post-super hurt buffs/teleport ignoring result already explicitly observed there, so no new row/candidate/credit.','Luna rotating source gate remains accepted master; not repeated.']),ensure_ascii=False))
