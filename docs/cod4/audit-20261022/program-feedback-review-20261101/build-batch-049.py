"""Seal a fixed-local Storm Cloud overlap review; no proposed semantic credit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def binding(p):
    return {'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())}
def load(p):
    return json.loads(p.read_text())

old_path = H / 'immune-reference-batch-048.json'
assert binding(old_path)['sha256'] == 'b1dec92f9b924ee5ebcbb40becffbf2c2e89eaccaa04edfad2d219abd2044efd'
old = load(old_path)
v = old['provenances'][0]
manifest_raw = (R / v['manifest_path']).read_bytes()
assert sha(manifest_raw) == v['manifest_sha256']
m = next(x for x in json.loads(manifest_raw) if x['repo'] == v['repo'])
entries = {e['path']: e for e in m['files']}
prefix = 'src/main/java/epicsquid/roots/'

def source(name, start=1, end=None, context='actual_read049'):
    e = entries[prefix + name]
    b = (R / e['source']).read_bytes()
    lines = b.decode().splitlines()
    end = end or len(lines)
    assert sha(b) == e['sourceSha256']
    assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == e['source_blob']
    return {'repo': m['repo'], 'commit': m['commit'], 'path': e['source'],
            'upstream_path': e['path'], 'lines': [start, end], 'file_sha256': sha(b),
            'git_blob_sha1': e['source_blob'],
            'range_text_sha256': sha('\n'.join(lines[start-1:end]).encode()),
            'reading_context': context}

new_names = ['spell/SpellStormCloud.java', 'potion/PotionStormCloud.java',
             'network/fx/MessageStormCloudGasFX.java', 'network/fx/MessageStormCloudStormFX.java',
             'network/fx/ModifierPacket.java', 'entity/spell/EntityIcicle.java']
refs = [source(n) for n in new_names]
refs.append(source('config/GeneralConfig.java', 151, 182))
new_refs = [x for x in refs if not x['upstream_path'].endswith('/ModifierPacket.java')]
refs[4]['reading_context'] = 'actual_reread049_previously_read043_support0'
refs.append(source('init/ModEntities.java', context='actual_reread049_previously_read041_support0'))
excluded = {'spell/SpellAquaBubble.java', 'potion/PotionAquaBubble.java', 'network/fx/MessageAquaBubbleFX.java'}
for x in old['source_refs']:
    if x['upstream_path'].removeprefix(prefix) in excluded:
        continue
    assert sha((R / x['path']).read_bytes()) == x['file_sha256']
    refs.append(dict(x, reading_context='exact048_shared_support_reused0'))

fields = ['id', 'status', 'repo', 'commit', 'category', 'semantic_dedup_key', 'count_unit',
          'full_chain_observation', 'concrete_observation', 'application_to_boss_immune',
          'limitations', 'research_credit', 'reviewed_utc']
ledger = A / 'immune-feedback-research/reviewed.json'
raw = ledger.read_bytes()
rows = json.loads(raw)
index = {r['id']: r for r in rows}
comparisons = {
    'goety-enderkeeper-distance-refusal-counterteleport-not-success-gated':
        'Already owns refusal independent of counter-teleport success. Storm relocates the true attacker to the holder instead of relocating the defender toward the attacker, and does not itself refuse damage. Changed actor/direction alone is insufficient new policy credit here.',
    'wizardry-shadowward-retaliatory-split-and-recursion-exclusion':
        'Already owns damage redistribution/retaliation and explicit recursion exclusion, with continuous decoration independent of outcome. Storm uses causeMobDamage without a shown local retaliation marker; native reentry is unexpanded. Missing guard is a caution, not another accepted mechanism.',
    'roots-native-effect-qualified-true-attacker-punishment-zeroes-victim-damage-with-target-suppression-and-type-dispatched-removal-aftermath':
        'Geas owns true-attacker punishment and target suppression/release. Storm reads victim state, attempts true-source jolt and direct relocation but has no original-damage zero/cancel operation of its own. Same event owner/support is not re-awarded; direction and modifier changes do not alone establish semantic independence.',
    'dungeonsmobs-native-stomp-knockback-cancellation-leaves-independent-vertical-control':
        'Already owns complete-control cancellation boundaries: a rejected damage/knockback operation does not stop another physical component. Storm direct relocation after unchecked jolt is useful confirmation, but no new owned control receipt or rejection lifecycle has been established.',
    'create-native-cardboard-cancels-attack-but-retains-dismount-and-directed-client-knockback':
        'Already owns cancelled damage with retained dismount/motion and client-directed control. Storm periodic state messages do not acknowledge relocation; replacing movement with setPositionAndUpdate and decorative cloud packets is not counted as independent here.'}
cmps = [{'accepted_id': key, 'complete_semantic_decision_read': {k: index[key][k] for k in fields},
         'overlap_judgment': judgment} for key, judgment in comparisons.items()]

mig = old['migration_overlap_screen']
migration_raw = (R / mig['path']).read_bytes()
mi = {x['candidate_id']: x for x in map(json.loads, migration_raw.decode().splitlines())}
for c in mig['comparisons']:
    assert all(mi[c['accepted_id']][k] == val for k, val in c['complete_semantic_decision_read'].items())
progress_path = A / 'immune-feedback-research/progress.json'
progress = load(progress_path)
assert len(rows) == progress['reviewed_effective_semantic_dedup']

observations = [
    'Previously read Roots lifecycle, concrete SpellRegistry insertion/disable/sound setting, ModPotions and client message registrations are reused with unchanged file hashes. ModEntities explicitly submits EntityIcicle and its renderer to external LibRegistry. These are registration requests, not runtime availability proof.',
    'Native ItemStaff selects the spell, checks cooldown/material availability and dispatches through SpellBase. Instantaneous SpellStormCloud.cast attempts the potion server-side, then overwrites the modifier snapshot under its cached name, and returns true on both sides. Default duration600/cooldown100/cloud_berry0.250 plus modifier costs are declared; actual configuration is unknown. Payment/cast sound follow success, not verified potion admission. Deep pouch/staff migration remains existing ownership0.',
    'Potion readiness always returns true. Every performEffect reads the current entity snapshot. Server tick scans the fixed3x3 footprint one block below: exact FIRE→AIR, exact LAVA plus OBSIDIAN→OBSIDIAN, configured water-block member plus LEVEL property0 and ICE→ICE. Water config builds a lazy registry-derived set; no successful mutation receipt or reload invalidation is shown. These terrain modes are support0, not buildings or new art.',
    'Server aura search radius is base2 plus optional2 through external MysticalLib Util. Friendly entities or self receive optional holder-tick healing, an attempted native FIRE_RESISTANCE effect with the full configured storm duration, and extinguish. Only self or PEACEFUL skips subsequent harmful modes: friendly status alone permits lightning/poison/icicles afterward. Native potion admission/heal/weather/block results are not used as final success proofs.',
    'Harmful aura uses each target ticksExisted for lightning and icicle intervals with random admission; poison has no additional interval. Icicle constructor receives holder and target-minus-holder-eye acceleration, snapshots modifiers and requests spawn. Native entity impact on server submits physical shooter-owned damage, ignores hurt result, then discards for any impact. Modifiers do not change dam in its ternary. Type is assigned in the parameterized constructor, while world-only constructor leaves null; native persistence/spawn reconstruction is unexpanded and no runtime null crash is asserted. Wildfire branch is context0, not separately studied.',
    'HIGHEST LivingHurt obtains trueSource before branches. Victim Storm potion and nonnull trueSource qualify: JOLT first submits causeMobDamage(holder) with configured amount, ignores boolean; MAGNETISM then calls trueSource.setPositionAndUpdate(holder coordinates). There is no local amount>0, living-only, team, boss, line-of-sight, destination safety, hurt-success, cooldown or explicit side guard in this arm. It can qualify after earlier Aqua reduced amount to0. It does not itself cancel or lower original damage. Later TimeStop/Resistance/Petal/Geas may change that event; no rollback of already submitted control is shown.',
    'The object relocated is the actual DamageSource true source, not necessarily the immediate projectile, current AI target or a Living entity. The shown branch never calls Forge teleport cancellation directly. Native Entity.setPositionAndUpdate, virtual overrides, event dispatch and packet synchronization are not expanded: cannot conclude universal Boss-immune bypass, safe relocation or successful client motion. JOLT has no local recursion tag, but engine hurt windows and other handlers prevent any static claim of infinite recursion.',
    'On removal, PotionStormCloud calls parent then conditionally submits end sound. It does not clear the modifier snapshot, reverse terrain, restore relocated actors or explicitly remove FIRE_RESISTANCE given to nearby entities. Therefore aura lifetime and granted effect lifetimes are different native owners; native cure/expiry/replacement rules are unexpanded. End sound is callback activity, not a rollback receipt.',
    'Gas feedback is submitted server-side every4 holder ticks if ICE or OBSIDIAN is enabled, even without an actual terrain change. Storm feedback is submitted every2 ticks outside the server-side block. External PacketHandler side enforcement is unexpanded; no guaranteed client exception or duplicate delivery is asserted. Both are holder-state decoration and do not depend on a jolt, teleport, damage refusal, potion acceptance or successful block mutation.',
    'Gas packet encodes xyz doubles. Storm packet extends ModifierPacket and passes snapshot into its sending constructor but overrides both codecs to write/read xyz only, omitting super calls. Its normal no-arg constructor leaves inherited modifiers null; after the shown fromBytes path it stays null, so hasRand(POISON,4) is false. Thus the attempted poison palette selection is unsupported by this codec path. This static protocol observation is support0, not a separate credit or a reproduction; external packet construction was not executed.',
    'Both concrete CLIENT message handlers use current Minecraft.world and submit randomized smoke through the previously read queue/END dispatcher and ParticleUtil settings/counter gate. No target identity, dimension, generation, cause, accepted delta or expiry in these payloads. Angular step can0, so no deterministic iteration bound established. Gas lifetime90 and storm80 are requested particle inputs, not measured visual duration. Renderer/transport internals remain external.',
    'Reviewed five complete saved accepted judgments, not their old original source chains, plus the complete048 proposal observation/boundaries and two exact unchanged migration judgments reused from046/048. Whole-family comparison is conservative: independent physical control after unchecked damage and state-only feedback are already covered. Shared timed snapshot and reactive effects overlap pending048. Do not promote a new credit from direction, modifier, packet bug, missing guard, method count or multiple files.'
]
doc = {
    'schema_version': 1, 'owner': 'program-feedback-review-049',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'STORM_CLOUD_WHOLE_POLICY_OVERLAP_HOLD_ZERO',
    'research_credit': 0, 'maximum_proposed_credit': 0,
    'repo': m['repo'], 'commit': m['commit'], 'provenances': [v], 'source_refs': refs,
    'prior_read_reuse': {'evidence': binding(old_path), 'new_ranges': len(new_refs),
        'new_cited_lines': sum(x['lines'][1]-x['lines'][0]+1 for x in new_refs),
        'new_whole_files': 5,
        'other_reuse_evidence': [binding(H/'immune-reference-batch-043-screen.json'), binding(H/'immune-reference-batch-041.json')],
        'scope': 'Five new concrete files fully read049. GeneralConfig151-182 includes complete water declarations/cache/getter. ModifierPacket42 (043), ModEntities77 (041) and EventManager1-249 reread but remain prior support. Other exact048 shared ranges reused, not new reading credit. Prior clipped storm output recovered with separate complete reads. Incidental ParticleUtil21-96/109-125 and config142-150/183 are not cited as complete methods.'},
    'baseline': {'progress': binding(progress_path), 'formal_count_observed': len(rows),
        'gap_to1000': 1000-len(rows), 'old_verifier_or_ledger_rerun': False},
    'dedup_snapshot': {'path': str(ledger.relative_to(R)), 'sha256': sha(raw),
        'rows': len(rows), 'comparisons': cmps,
        'scope': 'Five entire saved semantic decisions actually read; ledger keyword screen is not a whole-ledger source review.'},
    'migration_overlap_screen': {'path': mig['path'], 'sha256': sha(migration_raw),
        'comparisons': mig['comparisons'], 'reading_scope': 'Unchanged complete nine-field Roots migration judgments reused; no new migration review/credit.'},
    'pending_overlap': {'evidence': binding(old_path), 'status': '048 pending at last specialist handoff; no self-acceptance',
        'scope': 'Shared timed holder snapshot, pre-final reactive effects and state-only FX overlap048. Shared absorption grant/release remains048 subject; Storm does not provide a new owned resource policy.'},
    'whole_chain_observation': observations,
    'decision': 'Hold whole Storm Cloud review at0. It supplies useful original-program boundary evidence but no sufficiently distinct full control/immunity/receipt policy relative to accepted owners and pending048. No proposed credit for missed super codec or changed control vector. Coordinator may independently revisit semantics; this worker does not award or request automatic credit.',
    'application': '原Boss免控必须覆盖实际的传送/全部运动写入，并与反击伤害返回值分开；先确定真实目标与拒绝原因，再产生一次反馈。云雾、施法声、结束声不能充当控制成功/恢复成功回执。普通阴阳体质不新增灰字。此处仅研究。',
    'limitations': ['Fixed Roots1.12.2 snapshot, not Dynasty runtime. External MysticalLib/native Forge/MC internals remain explicit API boundaries.',
        'No game, Java, Gradle, upstream executable, network, fresh download, production/test/art/sharedJar/instance or master ledger changes.',
        'No control safety, final damage, native admission, packet delivery, visual/audio or task-completion claim. New evidence verifier only checks bindings; it cannot award semantic credit.'],
    'next_work': 'Leave048 to coordinator. Select a different complete owner, starting with the fixed Astral charge-paid dodge path only if comparison shows distinct resource/settlement lifecycle; no count for candidate scans.',
    'production_changes': False, 'runtime_executed': False, 'network_requests': 0,
    'master_changes': False, 'checklist_deletions': 0, 'hours_claimed': 0}
covered = {}
for x in refs:
    a, z = x['lines']
    incoming = set(range(a, z+1))
    previous = covered.setdefault(x['path'], set())
    assert not previous.intersection(incoming)
    previous.update(incoming)
doc.update(source_ranges=len(refs), unique_files=len(covered),
           full_files=sum(len(s) == len((R/p).read_text().splitlines()) for p, s in covered.items()),
           cited_lines=sum(map(len, covered.values())))
out = H / 'immune-reference-batch-049-screen.json'
with out.open('x') as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'evidence': binding(out), 'ranges': len(refs), 'files': doc['unique_files'],
                  'lines': doc['cited_lines'], 'credit': 0}, ensure_ascii=False))
