#!/usr/bin/env python3
"""Save bounded fixed-source ring/stand study; incomplete native lifecycle earns zero."""
import hashlib
import json
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
B = R / 'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-023'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
mp = B / 'source-manifest.json'
m = next(x for x in json.loads(mp.read_text()) if x['repo'] == 'Ellpeck/ActuallyAdditions')
entries = {x['path']: x for x in m['files']}
refs = []
pre = 'src/main/java/de/ellpeck/actuallyadditions/mod/'

def ref(up, start=1, end=None):
    e = entries[up]
    raw = (R / e['source']).read_bytes()
    end = end or len(raw.decode().splitlines())
    refs.append({'path': e['source'], 'upstream_path': up, 'lines': [start, end],
                 'file_sha256': sha(raw), 'git_blob_sha1': e['source_blob'],
                 'purpose': 'Read concrete registration, effect selection, funding, tile synchronization or exit context; support files earn no separate credit.',
                 'reading_context': 'Full file unless explicit bounds. InitItems/InitBlocks cite complete init methods; StackUtil cites only validity helpers. Native engine dependencies not inferred as read.'})

for name in ['items/ItemPotionRing.java', 'items/metalists/ThePotionRings.java',
             'crafting/RecipePotionRingCharging.java', 'tile/TileEntityDisplayStand.java',
             'blocks/BlockDisplayStand.java', 'tile/TileEntityBase.java',
             'tile/TileEntityInventoryBase.java', 'tile/CustomEnergyStorage.java',
             'items/base/ItemBase.java', 'RegistryHandler.java',
             'util/VanillaPacketDispatcher.java', 'util/ItemUtil.java',
             'blocks/base/BlockContainerBase.java', 'crafting/InitCrafting.java',
             'util/crafting/RecipeHelper.java', 'ActuallyAdditions.java',
             'util/ItemStackHandlerAA.java', 'config/values/ConfigIntValues.java']:
    ref(pre + name)
ref('src/main/java/de/ellpeck/actuallyadditions/api/misc/IDisplayStandItem.java')
ref(pre + 'util/StackUtil.java', 1, 45)
ref(pre + 'items/InitItems.java', 205, 377)
ref(pre + 'blocks/InitBlocks.java', 119, 217)

lp = A / 'immune-feedback-research/reviewed.json'
lr = lp.read_bytes()
rows = json.loads(lr)
by = {x['id']: x for x in rows}
comparisons = {
    'mekanism-native-purification-paid-effect-duration-advance-and-hidden-rollover': 'Existing paid duration advancement/hidden rollover, not granting or retargeting renewal. Ring stand selection is different code, but payment plus external effect call alone cannot justify a complete new lifecycle.',
    'tconstruct-native-milk-resistance-item-type-curative-key-and-equipment-replacement-release': 'Existing finite Resistance with item-type curative and qualified equipment-replacement release. Stand stores no effect owner/curative/recipient identity; stopping renewal does not establish explicit release.',
    'tconstruct-native-equipped-effect-immunity-multiset-threshold': 'Existing equipment sum compared with incoming amplifier refuses new effects and does not clear existing ones. Ring addPotionEffect call has no acceptance receipt; not proof of immunity bypass or successful renewal.',
    'betweenlands-native-collision-derived-phasing-suffocation-refusal-and-equipment-time-budget-exit-request': 'Existing continuously qualified state plus timer/durability and explicit exit requests. Ring empty/unequipped/redstone exit only stops future requests; native expiry not read. Do not repackage an equipment gate as another whole mechanism.',
    'spellengine-stashed-combat-charge-consumed-on-attempt-with-deferred-effect-replacement': 'Existing attempt-based spending and delayed type-based replacement without generation identity. Stand likewise can spend despite no fresh effect request or admission; generic attempt spending is not a new semantic credit.',
    'occultism-native-target-uuid-support-success-gated-receipt-cooldown': 'Existing per-goal victim UUID map, actual addEffect-success receipt and cooldown. Stand uses current same-effect occupancy instead of UUID memory and ignores effectEntity result. This distinction is recorded but does not close missing native feedback/expiry.',
    'simplyswords-native-gloam-shared-target-grasp-immunity-aftercare': 'Existing world/target-UUID shared regrasp lock established before addstatus outcome. Ring has no UUID lock or aftercare; any existing same-potion carrier can become the implicit recipient and have that whole potion removed. No new owner-scoped immunity claimed.',
}
mlp = A / 'legacy-migration-acceptance/reviewed.jsonl'
mlr = mlp.read_bytes()
ml = [json.loads(line) for line in mlr.decode().splitlines() if line.strip()]
mby = {x['candidate_id']: x for x in ml}
mkeys = ['candidate_id', 'status', 'family', 'trigger', 'input', 'output', 'preservation', 'application_limit', 'credit']
mcomparisons = {
    '93ba95eb0609044d7b71': 'Keep accepted full laser-network restoration/delivery owner. Shared storage/capability/update helpers provide context only, not a new graph, network or migration family.',
    '61a0405d2c891e7fae58': 'Keep accepted UUID-bound player-interface/probe/live charging owner. Same CustomEnergyStorage and tile sync infrastructure have existing credit; ring does not add an identity-restoration mechanism. Native energy and save caveats remain.',
}
doc = {
    'schema_version': 1, 'owner': 'program-feedback-review-030',
    'repo': m['repo'], 'commit': m['commit'], 'branch': m['branch'],
    'provenance': {'manifest_path': str(mp.relative_to(R)), 'manifest_sha256': sha(mp.read_bytes()),
                   'commit_metadata_path': str((B / 'provenance/Ellpeck__ActuallyAdditions/commit.json').relative_to(R)),
                   'tree_metadata_path': str((B / 'provenance/Ellpeck__ActuallyAdditions/tree.json').relative_to(R)),
                   'git_tree': m['git_tree'],
                   'acquisition': 'Existing fixed local source and cached GitHub commit/tree metadata only; no bare Git repository, network or upstream execution.',
                   'verification_correction': 'Initial verifier assumed upstream.git, which is absent. It failed before passing any provenance checks. Corrected to actual cached metadata and file Git blob hashes; no Git object database or fresh origin verification claimed.'},
    'status': 'held_native_effect_admission_sync_expiry_unclosed_and_shared_attempt_payment_not_new_credit',
    'research_credit': 0, 'maximum_proposed_credit': 0,
    'production_changes': False, 'runtime_executed': False,
    'semantic_family': 'held-actuallyadditions-effect-occupancy-selected-display-stand-renewal-and-exit',
    'source_refs': refs,
    'dedup_snapshot': {'path': str(lp.relative_to(R)), 'sha256': sha(lr), 'rows': len(rows),
                      'comparisons': [{'accepted_id': k, 'full_semantic_decision_read': {a: b for a, b in by[k].items() if a not in ['source_refs', 'auxiliary_refs']}, 'distinction': v} for k, v in comparisons.items()],
                      'reading_order': 'First five full substantive accepted decisions read before ItemPotionRing; last two full target-policy decisions read after ring revealed stand selection and before stand/base chain. Two migration decisions read once shared storage/sync became relevant. Old underlying source reread not claimed.',
                      'limits': 'Occupancy-based selection is an observed local distinction, not an accepted whole refusal/recovery/feedback reference. Shared gating, attempt spending and persistence do not earn additional credit.'},
    'migration_overlap_screen': {'path': str(mlp.relative_to(R)), 'sha256': sha(mlr), 'rows': len(ml),
                                 'comparisons': [{'accepted_id': k, 'complete_semantic_decision_read': {key: mby[k][key] for key in mkeys}, 'distinction': v} for k, v in mcomparisons.items()]},
    'full_chain': [
        {'stage': 'actual mod registration and gameplay entry', 'observation': 'ActuallyAdditions.preInit registers RegistryHandler; block/item events call InitBlocks/InitItems and register constructed queued entries. init registers TileEntityBase displayStand. ItemPotionRing constructor creates basic and advanced rings and creative subitems include empty/full Blaze values for concrete metadata. BlockDisplayStand creates actual tile; server activation copies one held item into empty slot and shrinks held stack unless creative. Returning current stack or empty-hand extraction clears/reduces slot. Native item handler inherited mutation details are external, not assumed fully read.'},
        {'stage': 'funding contexts are distinct', 'observation': 'Inventory onUpdate checks server, player, metadata upper bound and positive Blaze. Basic requires exact held-main/offhand stack identity; advanced accepts inventory update. effectEntity true means an addPotionEffect request was made, not native acceptance. Only that true branch and worldTotalTime modulo10==0 decrements one Blaze. RecipePotionRingCharging is constructed by InitCrafting, queued by RecipeHelper and registered by RegistryHandler: one ring plus Blaze powder slots, each occupied powder slot contributes20, output is ring copy only when added>0 and total<=800. matches itself allows zero powder although result then empty. Stand path never reads/debits Blaze and instead uses its own energy.'},
        {'stage': 'stand eligibility and target selection', 'observation': 'Tile tick calls super first then server-only checks valid slot, no redstone power, actual IDisplayStandItem and stored energy>=325. Ring builds integer-position-centered AABB radius16 basic/48 advanced and queries EntityLivingBase, with no explicit owner/team/line-of-sight filter in ring code. Advanced visits all returned living entities. Basic scans returned order for first entity with same potion active: 99% renews that carrier and returns; 1% removes its whole potion then breaks to shuffle the entire list and request effect on element0. No active carrier also shuffles. The removed carrier can be selected again; existing external carriers are not globally cleared and multiple affected entities can remain. No stored selected UUID or source token.'},
        {'stage': 'effect request and payment boundary', 'observation': 'effectEntity checks wait flag, existing null or existing duration<=1. Regeneration uses wait gate and50-tick requests; normal short buffs10 and night vision300. Requests set ambient=true/showParticles=false; native merge, immunity and visual outcome not proven. Stand update returns true for any nonempty entity list even if every effectEntity returns false because waiting. Tile then extracts325 after callback; return from extraction ignored. CustomEnergyStorage internal extraction temporarily raises maxExtract, calls own extraction and restores; raw setter/NBT reader do not clamp. Basic and advanced have same fixed cost, not per recipient. This is not an effect-admission-success transaction.'},
        {'stage': 'real tile sync, not potion feedback', 'observation': 'Stand energy delta triggers sendUpdateWithInterval using ticksElapsed modulo configured interval (enum default5; currentValue supplied by config outside this study). TileBase sends via VanillaPacketDispatcher to watching players for current server chunk entry; absent entry yields no recipients. getUpdatePacket serializes SYNC to SPacketUpdateTileEntity. onDataPacket and handleUpdateTag read SYNC; stand readSyncableNBT restores energy and inherited inventory reader restores Items when shouldSyncSlots=true. Inventory contents-change override marks dirty and requests sendUpdate. Actual energy/slot state consumer identified; this packet is not the effect application/removal packet and carries no target, effect-admission receipt or ownership token. No claim of rendered HUD or client acknowledgement.'},
        {'stage': 'exit and cleanup limits', 'observation': 'BlockContainerBase server redstone update stores power flag. With power, insufficient energy, no valid item or no targets, future renewal/payment paths are skipped as applicable. Removing ring empties slot; block break drops inventory then superclass removal, with no target list or potion cleanup. Inventory ring without Blaze/qualifying hand similarly stops requesting. No explicit native-effect revocation on stand loss, range exit, unequip, death or unload in these classes. Native duration expiry and removePotionEffect callbacks/sync are unresolved; cannot turn stopping renewal into verified complete cleanup. Chance-driven removePotionEffect can target externally sourced effect of same type; exact engine removal result not read.'},
    ],
    'critical_boundaries': [
        'No new immunity rejection or explicit denial feedback is established; this is an actual support mechanism with native lifecycle gaps, held at0.',
        'Basic is one request target per tick, not guaranteed one affected entity, nearest entity, owner-only or source-isolated target.',
        'A true stand callback means nonempty candidates, not fresh request or successful native effect application;325 can be paid during regeneration wait.',
        'World-time modulo inventory Blaze debit is not a per-ring ten-tick cooldown; regeneration wait may skip debit opportunities. No runtime free-effect exploit claimed.',
        'Tile energy/inventory synchronization is complete mod-side context; it cannot substitute for native entity effect synchronization or final UI rendering.',
        'The display-stand path lacks even the inventory onUpdate metadata upper-bound guard before direct enum index; negative/invalid metadata behavior not exercised.',
        'Shared tile/storage/registry support and eight potion variants/basic/advanced remain0 extra; no migration or per-file credit.',
        'No native1.12.2 effect admission/merge/tick/removal/network source was read. No substitution with unrelated1.20 cached source, download retry or runtime test.',
    ],
    'native_gaps': [
        {'missing': 'Same-version EntityLivingBase addPotionEffect, removePotionEffect, duration update and effect synchronization through actual client consumer.', 'impact': 'Cannot conclude effect accepted, exact expiration/removal, client icon/particles cleared or full recovery lifecycle.'},
        {'missing': 'Forge inherited ItemStackHandler mutation and native capability/save lifecycle.', 'impact': 'Only actual mod calls/overrides verified. No transactional custody, guaranteed persistence or save-loss conclusion.'},
        {'missing': 'Concrete native damage/resistance consumer and refusal receipt for this ring.', 'impact': 'Resistance enum grant request does not establish final Boss immunity behavior. Remain0, no production repair.'},
    ],
    'static_examples_not_executed_tests': [
        {'case': 'regeneration waiting still costs energy', 'assumptions': 'Eligible stand with>=325 energy; nonempty list; chosen same-potion carrier duration>1; random branch does not switch.', 'derivation': 'effectEntity false; basic update stilltrue; tile calls extractEnergyInternal(325,false).'},
        {'case': 'external effect selected and removal requested', 'assumptions': 'First same-potion carrier bears external effect and random nextInt100 is0.', 'derivation': 'No source check before removePotionEffect; shuffle may choose same entity again. Native acceptance/removal/sync not asserted.'},
        {'case': 'disabled stand leaves no explicit target cleanup', 'assumptions': 'Previously requested effect; next tick redstone is active.', 'derivation': 'Item.update branch skipped. Tile still may send energy change update but issues no potion removal. Expiration is an external engine dependency.'},
    ],
    'application': 'Distinguish selecting by present status from tracking ownership; distinguish nonempty target/update attempt from effect admission; require native teardown and real client consumer before declaring recovery/feedback closed.',
    'counting': {'formal_baseline_observed': len(rows), 'current_credit': 0, 'whole_family_maximum': 0, 'helpers_variants_migration_credit': 0},
    'next_work': ['Continue another unread fixed local original-program mechanism after comparing complete prior semantic owners; retain this study as0.', 'Only revisit native effect lifecycle with genuine same-version local evidence; do not manufacture a receipt from tile sync or count helpers.'],
}
with (H / 'immune-reference-batch-030.json').open('x') as out:
    json.dump(doc, out, ensure_ascii=False, indent=2)
    out.write('\n')
print(json.dumps({'files': len(refs), 'lines': sum(x['lines'][1]-x['lines'][0]+1 for x in refs), 'credit': 0, 'baseline': len(rows)}))
