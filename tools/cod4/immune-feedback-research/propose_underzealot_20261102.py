"""Freeze one actually read ritual/capture lifecycle proposal, with zero automatic credit."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[3]
B = R / 'tools/cod4/immune-feedback-research'
O = R / 'docs/cod4/audit-20261022/immune-feedback-research'
S = B / 'sources/AlexModGuy__AlexsCaves'
PREFIX = 'src/main/java/com/github/alexmodguy/alexscaves/'
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    out = O / 'coordinator-underzealot-ritual-lifecycle-proposal-20261102.json'
    assert not out.exists()
    meta = json.loads((S / 'source.json').read_text())
    tree = json.loads((S / 'tree.json').read_text())
    assert meta['commit'] == tree['sha'] == '4718f4287c65b810aecb211789b45f54d405a94d'
    assert not tree['truncated']
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    refs = [
        ('server/entity/living/UnderzealotEntity.java', 1, 521),
        ('server/entity/ai/UnderzealotSacrificeGoal.java', 1, 245),
        ('server/entity/ai/UnderzealotCaptureSacrificeGoal.java', 1, 97),
        ('server/entity/ai/UnderzealotHurtByTargetGoal.java', 1, 33),
        ('server/entity/util/PackAnimal.java', 1, 72),
        ('server/entity/util/UnderzealotSacrifice.java', 1, 9),
        ('client/render/entity/UnderzealotRenderer.java', 1, 48),
        ('client/model/UnderzealotModel.java', 1, 197),
        ('client/ClientProxy.java', 111, 112),
        ('client/ClientProxy.java', 222, 231),
        ('client/ClientProxy.java', 580, 890),
        ('client/ClientProxy.java', 941, 947),
        ('server/entity/living/GloomothEntity.java', 45, 94),
        ('server/entity/living/GloomothEntity.java', 96, 182),
        ('server/entity/living/GloomothEntity.java', 313, 322),
        ('server/entity/living/VesperEntity.java', 44, 235),
        ('server/entity/living/VesperEntity.java', 404, 413),
        ('server/entity/ACEntityRegistry.java', 19, 25),
        ('server/entity/ACEntityRegistry.java', 80, 84),
        ('server/entity/ACEntityRegistry.java', 134, 147),
        ('AlexsCaves.java', 91, 133),
    ]
    evidence = []
    for rel, lo, hi in refs:
        rel = PREFIX + rel
        p = S / rel
        raw = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == manifest[rel]['sha256']
        assert blob == manifest[rel]['git_blob_sha1'] == blobs[rel]
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        evidence.append(dict(path=str(p.relative_to(R)), source_path=rel, lines=[lo, hi],
                file_sha256=sha(raw), git_blob_sha1=blob,
                excerpt_sha256=sha(''.join(lines[lo - 1:hi]).encode()),
                url=f'https://github.com/AlexModGuy/AlexsCaves/blob/{tree["sha"]}/{rel}#L{lo}-L{hi}'))
    rel = PREFIX + 'client/sound/UnderzealotSound.java'
    sound = B / '.work/underzealot-20261102' / rel
    raw = sound.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == blobs[rel] == '06229c4522a43c40a75fe31013c834b3400449fb'
    evidence.append(dict(path=str(sound.relative_to(R)), source_path=rel, lines=[1, len(raw.decode().splitlines())],
                file_sha256=sha(raw), git_blob_sha1=blob, excerpt_sha256=sha(raw),
                supplemental_fixed_raw_source_not_original_manifest=True,
                url=f'https://github.com/AlexModGuy/AlexsCaves/blob/{tree["sha"]}/{rel}',
                acquisition='Python verified HTTPS failed local CA; system curl verified HTTPS succeeded, then same fixed bytes saved and Git-blob verified; no insecure TLS or rate-limit bypass'))
    rows = json.loads((O / 'reviewed.json').read_text())
    assert len(rows) == 458
    keys = [
        'upgradeaquatic-native-prehurt-stun-budget-releases-captive-without-health-success',
        'endergetic-native-health-loss-grounding-release-and-target-wide-recapture-denial',
        'lycanites-native-weight-heavy-pickup-refusal-and-safe-release-control-lease',
        'domestication-native-bubble-break-source-denial-and-dismount-lock-lifecycle',
        'tf-hostilemount-native-escape-policy-and-release-window',
        'betweenlands-native-first-qualified-dismount-refusal-per-rider-worldtick-and-mount-callback-progress',
        'alexscaves-native-successful-hurt-and-unmarked-attacker-qualified-persisted-counter-spray',
        'cataclysm-crab-burrow-window-rejection-sound',
        'ars-bubble-pop-tick-lifecycle-not-unified-rejection',
    ]
    comparisons = []
    for key in keys:
        row = next(x for x in rows if x['semantic_dedup_key'] == key)
        comparisons.append(dict(key=key, full_record_sha256=sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                substantive_decision_fields_actually_read=True, old_source_chain_reread_claimed=False, extra_credit=0))
    proposal = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        status='PENDING_INDEPENDENT_SEMANTIC_REVIEW_ZERO_CREDIT', proposed_maximum_credit=1, accepted_credit=0,
        semantic_key='alexscaves-native-quorum-ritual-windup-versus-victim-owned-committed-capture-lifecycle',
        repo='AlexModGuy/AlexsCaves', commit=tree['sha'], source_manifest_sha256=sha((S / 'source.json').read_bytes()),
        source_tree_sha256=sha((S / 'tree.json').read_bytes()), actual_source_ranges=evidence,
        semantic_comparisons=comparisons, ledger_sha256_before_proposal=sha((O / 'reviewed.json').read_bytes()),
        full_chain_observation=[
            'Registered Underzealot goals capture a valid ground-near sacrifice and startRiding without checking returned success. Target selection/hurt-alert suppressed while carrying/leader carrying/praying. Actual carrying sync flag is updated from passenger presence in server tick after super.tick.',
            'Complete ritual goal separates follower and carrier eligibility. Followers seek ring positions, pray near altar and increment shared-looking but per-entity synced worship time; carrier >200 worship ticks plus >=3 praying followers triggers passenger.triggerSacrificeIn(300), then consumes local cloudCooldown400 and publishes event62. Validity/altar/position/digging and stop logic differ from later victim countdown.',
            'Native hurt calls super first; only true plus isVehicle plus random<.65 ejects passengers. It does not itself clear victim isBeingSacrificed/sacrificeTime or immediately set carrying false. Goal stop resets worship/praying/particle position, ejects and conditionally sets carrier cooldown100. No rollback callback to committed victim timer.',
            'Actual Gloomoth tick decrements armed sacrificeTime on server regardless of still being a passenger, then attempts Watcher conversion below0. Carrier postSacrifice/cooldown/advancement requires current Underzealot vehicle, but conversion does not. Vesper tick additionally requires isPassenger, so dismount pauses its timer without clearing the armed flag; later any passenger relation resumes, and conversion still does not require an Underzealot vehicle. Both trigger methods simply arm and replace timer.',
            'Client events61/62 create particles/cloud,77 requests chant. ClientProxy type5 reuses sound by integer entity id and isSameEntity/alive; queues only if absent from queued/ticking lists and canPlaySound. UnderzealotSound canPlay requires !silent/praying/worship<MAX; running tick checks alive/praying, updates position/volume/pitch and stops otherwise. It does not itself stop when worship crosses MAX or silent changes. Removal clears map entry; no sound-manager stop call in that removal helper.',
            'Native render burrow gate can suppress body; model carrying/praying interpolation reshapes pose, and armFreedom suppresses ordinary swing while carrying. These are state cues, not damage rejection text or verified visual feedback. Buried targetability/push/pick filters differ from hurt: own isInvulnerableTo only adds IN_WALL and super, not blanket buried invulnerability.',
        ],
        distinctness_argument=('At most one complete multi-actor windup/quorum-to-victim-owned-committed timer family with damage-qualified unseating and divergent interruption semantics. '
            'Not Thrasher attempted-hit stun budget, Glider actual-HP accumulated grounding/target regrab lease, weight pickup lease, bubble release-source/dismount veto, TF global release gate, Betweenlands per-rider worldtick callback budget or Gammaroach attacker-mark cooldown spray. '
            'Registration, burial, sound cache, pose, random constant, two victim species and each goal/tick are support0, never separate credits. No universal damage immunity implementation is claimed.'),
        application_to_boss_immune=('Authority must distinguish application admission, windup interruption, committed future effect and feedback lifetime. A damage-success dismount cue is not proof an armed effect was canceled; a chanted/visible state is not immunity denial. '
            'Boss feedback should follow exact authoritative reason and target, with explicit cleanup at each phase; do not add ordinary-constitution gray text or copy this ritual/gameplay.'),
        limitations=[
            'Coordinator actually read all listed source ranges. Full Underzealot/three goals/PackAnimal/interface/renderer/model/sound; large proxy and victim files only specified methods/ranges, not entire files. Earlier combined output clipped registry lines, recovered80..84 and renderer call explicitly; no extra credit for recovery.',
            'Vanilla hurt/forced eject/startRiding/AI scheduler/convertTo and Forge final listeners are not expanded or run. super.hurt true is API result, not independently measured HP loss; ejection attempted, not a runtime release guarantee. No double-side or exact tick-order proof.',
            'Carrier pose/carrying sync can lag actual removal until server tick. Quorum sampled at trigger, not maintained throughout victim countdown. No method cancels victim armed timer here. Vesper only requires any passenger after armed, not still same carrier/altar/quorum; Gloomoth does not even require passenger. Do not claim interruptible channel after commitment.',
            'Carrier own NBT saves sacrifice cooldown/buried/remerge/altar coordinates. Worship/praying/cloudCooldown and victim own armed/timer fields are not saved by these classes; inherited passenger/native save semantics not verified. No save/reopen or clone credit.',
            'Goal altar test nested loops both start and end-2, so not a complete5x5 floor test. Mutable position movement in altar search retained as source; no geometry guarantee. Malformed buried save without remerge position can reach null uses; not fixed or reproduced.',
            'Sound cache id equality is not UUID/dimension/session identity. A stopped matching sound object can be reused because type5 lacks isStopped recreation guard; do not assert restart success or sound-engine behavior. Clearing cache alone does not prove active sound stopped. No gray text, per-refusal nonce, damage ACK or measured sound/pixels/TCP.',
            'The model/renderer were read as feedback consumers only, no specialist art design credit or modification. ACSoundRegistry individual entries/particle classes, engine transport and native transformation outcome not expanded. Distinct transformations/thresholds/sounds are not extra semantic implementations. Reference version API not asserted drop-in compatible with Dynasty Forge1.20.',
            'One failed local Python CA request followed by bounded normal system-curl fixed-commit acquisition; raw blob verified. No SSL verification disabling, account/model/provider bypass, retry loop or download-time credit.',
            'Semantic search only selected nine actual prior decision records; broad initial output was truncated and was not counted as reading. All nine decision fields were then explicitly recovered in bounded outputs. No claim to have reread their old source chains.',
        ], production_changes=0, art_changes=0, game_starts=0, checklist_deletions=0, duration_hours_claimed=0)
    with out.open('x') as f:
        json.dump(proposal, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(dict(proposal=str(out.relative_to(R)), sha256=sha(out.read_bytes()),
                         source_ranges=len(evidence), accepted_credit=0)))


if __name__ == '__main__':
    main()
