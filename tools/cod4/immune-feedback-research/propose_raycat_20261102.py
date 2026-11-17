"""Freeze one actually read cross-entity status transfer and feedback proposal; credit0."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[3]
B = R / 'tools/cod4/immune-feedback-research'
O = R / 'docs/cod4/audit-20261022/immune-feedback-research'
S = B / 'sources/AlexModGuy__AlexsCaves'
P = 'src/main/java/com/github/alexmodguy/alexscaves/'
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    out = O / 'coordinator-raycat-status-transfer-proposal-20261102.json'
    assert not out.exists()
    meta = json.loads((S / 'source.json').read_text())
    tree = json.loads((S / 'tree.json').read_text())
    assert meta['commit'] == tree['sha'] == '4718f4287c65b810aecb211789b45f54d405a94d'
    assert not tree['truncated']
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    full = ['server/entity/living/RaycatEntity.java', 'client/render/entity/RaycatRenderer.java', 'client/model/RaycatModel.java']
    refs = [(P + n, 1, len((S / (P + n)).read_text().splitlines())) for n in full]
    refs += [(P + n, a, b) for n, a, b in [
        ('server/event/CommonEvents.java', 154, 160),
        ('server/entity/ACEntityRegistry.java', 19, 25), ('server/entity/ACEntityRegistry.java', 59, 59),
        ('server/entity/ACEntityRegistry.java', 127, 132), ('client/ClientProxy.java', 197, 198),
        ('server/potion/ACEffectRegistry.java', 15, 36), ('server/misc/ACTagRegistry.java', 74, 74),
        ('server/misc/ACTagRegistry.java', 97, 99),
        ('client/render/ACRenderTypes.java', 77, 80), ('client/render/ACRenderTypes.java', 93, 102),
        ('client/render/ACRenderTypes.java', 145, 154), ('AlexsCaves.java', 91, 133),
    ]]
    evidence = []
    for rel, lo, hi in refs:
        p = S / rel; raw = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == manifest[rel]['sha256'] and blob == manifest[rel]['git_blob_sha1'] == blobs[rel]
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        evidence.append(dict(path=str(p.relative_to(R)), source_path=rel, lines=[lo, hi],
            file_sha256=sha(raw), git_blob_sha1=blob, excerpt_sha256=sha(''.join(lines[lo - 1:hi]).encode()),
            url=f'https://github.com/AlexModGuy/AlexsCaves/blob/{tree["sha"]}/{rel}#L{lo}-L{hi}'))
    supplemental = [P + 'server/potion/IrradiatedEffect.java',
                    'src/main/resources/data/alexscaves/tags/entity_types/resists_radiation.json']
    for rel in supplemental:
        p = B / '.work/raycat-20261102' / rel; raw = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == blobs[rel]
        evidence.append(dict(path=str(p.relative_to(R)), source_path=rel, lines=[1, len(raw.decode().splitlines())],
            file_sha256=sha(raw), git_blob_sha1=blob, excerpt_sha256=sha(raw),
            supplemental_fixed_raw_source_not_original_manifest=True,
            url=f'https://github.com/AlexModGuy/AlexsCaves/blob/{tree["sha"]}/{rel}',
            acquisition='One bounded system-curl verified-HTTPS request; fixed commit raw Git blob verified; no API rate-limit retry or insecure TLS'))
    rows = json.loads((O / 'reviewed.json').read_text())
    keys = ['bewitchment-native-purity-budget-decrements-harmful-and-own-amplifiers',
            'mekanism-native-purification-paid-effect-duration-advance-and-hidden-rollover',
            'artifacts-native-antidote-finite-status-cap-with-shared-item-cooldown',
            'ars-soaked-observer-effect-sync-with-local-player-exclusion-and-lossy-amplifier',
            'goety-native-stored-effect-type-denial-before-independent-prehit-effect-theft']
    comparisons = []
    for key in keys:
        row = next(x for x in rows if x['semantic_dedup_key'] == key)
        comparisons.append(dict(key=key, full_record_sha256=sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
            substantive_decision_fields_actually_read=True, old_source_chain_reread_claimed=False, extra_credit=0))
    proposal = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        status='PENDING_INDEPENDENT_SEMANTIC_REVIEW_ZERO_CREDIT', accepted_credit=0, proposed_maximum_credit=1,
        semantic_key='alexscaves-native-delayed-live-target-amplifier-transfer-with-independent-recipient-gain-and-state-beam',
        repo='AlexModGuy/AlexsCaves', commit=tree['sha'], source_manifest_sha256=sha((S / 'source.json').read_bytes()),
        source_tree_sha256=sha((S / 'tree.json').read_bytes()), actual_source_ranges=evidence,
        semantic_comparisons=comparisons, ledger_sha256_before_proposal=sha((O / 'reviewed.json').read_bytes()),
        full_chain_observation=[
            'Actual Raycat registration/attributes/client renderer and IRRADIATED registration bound. Entity defines target integerID, absorb float, command/lay fields; random absorbCooldown300..599 is not synced. Complete native tick selects only on server after cooldown expires, preferring irradiated owner within20, else closest qualifying Living in inflated9 box, excluding Raycat and untamed selection of Player. Selection immediately resets cooldown, so selected target can be retained during another full wait.',
            'After cooldown reaches0 with an id-resolved target, amount<=0 starts at1 and requests absorb sound; subsequent ticks subtract.05. Completion first calls heal10 and addEffect IRRADIATED200 with self current amplifier+1 (or0 if absent), then lookAt target; only then reads current target effect, removes it, and if amplifier>0 recreates with same remaining duration and one lower amplifier. Target-id cleared; only server resets cooldown. Results of heal/add/remove ignored.',
            'No target alive/range/LOS/same-effect/still-owner revalidation at completion. getAbsorbTarget accepts any id-resolved Entity. Recipient heal/self-status can occur even if target effect disappeared or target is not Living. Transfer is not atomic and not a successful removal ACK. If target resolution becomes null mid-progress, selection resets cooldown but does not reset absorb amount, so later target can inherit partial progress.',
            'Native IrradiatedEffect explicitly skips its radiation-hurt call for Raycat; this is effect-tick damage production exclusion, not blanket damage-source immunity or canBeAffected denial. Own effect remains present and Raycat tick calls heal1 every10 entityticks. Registered CommonEvents cancels healing for irradiated entity unless RESISTS_RADIATION; fixed actual entity-type tag includes raycat. This tag only bypasses that listener, not final healing success. Damage helper and hazmat internals unexpanded.',
            'Renderer reads interpolated absorb amount and live id target, emits fullbright green triangular beam only amount>0/alive/nonnull. Radiation post shader is requested independently of current transfer; regular body/eye layers are not outcome-specific flashes. Body/eyes rendering and model sit/lay pose consume state, not a rejection reason. Renderer depth/helper boundaries read but no pixels or backend transport tested.',
            'Own NBT persists only Command and LayTime. Target id, absorb amount and cooldown have no own NBT keys, so this is not a durable transfer transaction. MobInteract owner command text describes follow/sit command, not transfer/refusal success; no gray immunity text or per-hit notification key exists in this chain.',
        ],
        distinctness_argument=('At most one complete two-entity delayed live-target status-amplifier transfer with recipient gain preceding target reduction and state-driven beam. '
            'Purity spends own amplifier to cleanse categories on the same entity, Mekanism advances durations with paid hidden-layer handling, Antidote caps finite durations, Soaked is observer-sync reconstruction, Wartling carried type becomes final admission predicate and prehit effect theft. '
            'Here delayed source capture can be stale, recipient progression and source reduction settle independently, and rendered transfer state is not an ACK. Do not separately count raycat species, IRRADIATED constants, damage skip, resist tag, healing callback, shader, model or effect methods.'),
        application_to_boss_immune=('For Dynasty control/immunity feedback separate selection, actual effect admission/removal, recipient mutation and cue completion. '
            'At final authority revalidate target identity/qualification and report exact rejection cause; a beam ending or healing call does not prove successful transfer or refused control. '
            'Do not copy forced lookAt into Dynasty camera/AI behavior, and do not introduce gray text for ordinary constitutions.'),
        limitations=[
            'Coordinator actually read complete Raycat311lines, renderer123lines and model159lines as gameplay/feedback consumers; use actual evidence lengths if source line counts differ. No art-asset creation or design reference credit. Large registry/proxy/common classes only listed bounded ranges, not whole methods/classes beyond livingHeal and explicitly complete helpers.',
            'Tick has explicit server guard around target selection only; cooldown decrement, progress, heal, add/remove, lookAt and amount/id writes lack a surrounding server-only guard in the completion branch. Client cooldown random phase can differ. No claim this is server-authoritative settlement or two-client convergence.',
            'Fixed tag source contains raycat and maps to TagKey entity_types/resists_radiation; resource existence is not an observed loaded runtime tag. Other datapacks/listeners can alter result. Raycat owns IRRADIATED but producer skips damage; no universal hurt/canBeAffected immunity inferred.',
            'Integer id target has no UUID/dimension/session/attempt field. Missing target does not clear old amount; id reuse or target replacement not exercised. No explicit live/range/LOS/faction revalidation once latched. Search inflated9 is box membership and distance comparator, not a spherical hard9 guarantee.',
            'Source effect is read at completion, not snapshotted initially. Removal/addition return values ignored; recipient heal/status precede source mutation. Recreated source uses three-argument MobEffectInstance, not a copy preserving ambient/visibility/icon/hidden chain. Native constructor defaults/update-combine rules not newly expanded; no lossless-state or guaranteed amplifier increment claim.',
            'Normal completion clears id and consumes server cooldown even if transfer did not change source. Because recipient effect may already exist with different strength/duration, addEffect call is not proof exactly200 or a stronger resulting status. Healing may be capped/canceled by independent rules.',
            'Radiation own tick uses effect amplifier as second apply argument, period200/level when positive; level0 does not schedule its damage callback. Hazmat damageScale/causeRadiationDamage and native hurt handling remain external here; no per-source zero-damage success conclusion.',
            'Beam fullbright240 and LEQUAL helper are static draw calls, not visible cue correctness/occlusion/performance/nativeS2C proof. Sepia mode still can reach amount-target beam branch, while shader request is separately disabled. Eye layer exists without transfer/outcome check. PostEffectRegistry/low-level state and texture PNG pixels not inspected.',
            'Five full prior semantic decision fields actually read in bounded outputs, canonical complete record hashes bind them; their old source chains not reread. New source file count/hash/download adds0; independent acceptance still required. No production/TODO/world/Java/game/claimed hours.',
        ], production_changes=0, art_changes=0, game_starts=0, checklist_deletions=0, duration_hours_claimed=0)
    # Derive factual lengths from actual bytes; prose never inflates containing-source coverage.
    proposal['limitations'][0] = ('Coordinator actually read complete Raycat/entity, renderer and model files, respectively ' +
        ','.join(str(len((S / (P + n)).read_text().splitlines())) for n in full) +
        'lines, as gameplay/feedback consumers only. No art creation/design reference credit. Large registry/proxy/common classes only specified bounded ranges, not whole classes.')
    with out.open('x') as f:
        json.dump(proposal, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(dict(proposal=str(out.relative_to(R)), sha256=sha(out.read_bytes()), source_ranges=len(evidence), accepted_credit=0)))


if __name__ == '__main__':
    main()
