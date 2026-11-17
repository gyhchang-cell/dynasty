"""Package the coordinator's actual source reading; grants no research credit."""
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
SRC = ROOT / 'tools/cod4/immune-feedback-research/sources/AlexModGuy__AlexsCaves'
OUT = DOC / 'coordinator-ferrouslime-cohort-transfer-proposal-20261103.json'
assert not OUT.exists(), 'Immutable proposal already exists; do not rerun.'
sha = lambda b: hashlib.sha256(b).hexdigest()
meta = json.loads((SRC / 'source.json').read_text())
tree = json.loads((SRC / 'tree.json').read_text())
revision = '4718f4287c65b810aecb211789b45f54d405a94d'
assert meta['commit'] == tree['sha'] == revision and tree['truncated'] is False
files = {r['path']: r for r in meta['files']}
entries = {r['path']: r for r in tree['tree']}
refs = []

def mod(path, lo, hi, role):
    p = SRC / path
    raw = p.read_bytes()
    lines = raw.decode().splitlines()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert files[path]['sha256'] == sha(raw)
    assert files[path]['git_blob_sha1'] == entries[path]['sha'] == blob
    assert 1 <= lo <= hi <= len(lines)
    refs.append(dict(source_kind='fixed_mod_git', path=str(p.relative_to(ROOT)),
                     source_path=path, lines=[lo, hi], file_sha256=sha(raw),
                     git_blob_sha1=blob, revision=revision,
                     source_metadata=str((SRC / 'source.json').relative_to(ROOT)),
                     source_metadata_sha256=sha((SRC / 'source.json').read_bytes()),
                     tree_metadata=str((SRC / 'tree.json').relative_to(ROOT)),
                     tree_metadata_sha256=sha((SRC / 'tree.json').read_bytes()),
                     excerpt_sha256=sha(('\n'.join(lines[lo-1:hi])+'\n').encode()),
                     url=f'https://github.com/AlexModGuy/AlexsCaves/blob/{revision}/{path}#L{lo}-L{hi}',
                     coordinator_actually_read=True, role=role, research_credit=0))

base = 'src/main/java/com/github/alexmodguy/alexscaves/'
mod(base+'server/entity/living/FerrouslimeEntity.java', 1, 435,
    'Complete actual entity, both registered inner AI goals, merge/split/removal/constructor state and effects; one proposed cohort family.')
mod(base+'AlexsCaves.java', 92, 133, 'Complete constructor registry-bus binding; no whole mod setup claim.')
for lo, hi, role in [(20,25,'Deferred register declaration'), (34,34,'Actual MONSTER factory'),
                     (110,116,'Attribute subscriber header and actual Ferrouslime binding; bounded method prefix only'),
                     (165,165,'Actual ordinary spawn-placement binding, not deployed biome pool')]:
    mod(base+'server/entity/ACEntityRegistry.java', lo, hi, role)

archive = ROOT / ('tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/'
    'minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/'
    'forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
assert sha(archive.read_bytes()) == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'
native = []
with zipfile.ZipFile(archive) as z:
    for path, ranges in [
        ('net/minecraft/world/entity/Entity.java', [(353,356),(3348,3368)]),
        ('net/minecraft/world/entity/LivingEntity.java', [(546,553),(1054,1056),(1303,1336)]),
        ('net/minecraft/world/entity/ai/goal/Goal.java', [(1,59)]),
    ]:
        raw = z.read(path)
        lines = raw.decode().splitlines()
        for lo, hi in ranges:
            assert hi <= len(lines)
            native.append(dict(source_kind='native_archive_entry', archive=str(archive.relative_to(ROOT)),
                archive_sha256=sha(archive.read_bytes()), entry=path, lines=[lo,hi],
                entry_sha256=sha(raw), excerpt_sha256=sha(('\n'.join(lines[lo-1:hi])+'\n').encode()),
                coordinator_actually_read=True, research_credit=0))

comparisons = []
for p in sorted(DOC.glob('batch-*.json')):
    for r in json.loads(p.read_text())['records']:
        if r['id'] in {'EA-0010','EA-0013','EA-0014','EA-0017'}:
            comparisons.append(dict(id=r['id'], batch=str(p.relative_to(ROOT)), batch_sha256=sha(p.read_bytes()),
                semantic_key=r['semantic_key'], actually_read_fields=['semantic_key','observation','application','limits'],
                old_source_chain_reread=False, research_credit=0))
assert len(comparisons) == 4

report = dict(recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    status='ACTUAL_COMPLETE_BOUNDED_SOURCE_READING_PENDING_INDEPENDENT_SEMANTIC_REVIEW_ZERO_CREDIT',
    author_thread_id='01a16364-cac0-7ca2-a042-a5312781ca34',
    proposed_semantic_key='live-cohort-head-aggregation-and-stall-or-death-triggered-bisection-with-uncommitted-adds',
    maximum_proposed_whole_family_credit=1, accepted_credit=0, candidate_identifier_invented=False,
    source_refs=refs, native_source_refs=native, selected_existing_decisions= comparisons,
    observations=[
        'Actual registered MONSTER factory/attributes and constructor bus binding exist. Complete registerGoals installs MeleeGoal priority1 and FormGoal priority2, sharing MOVE. No loaded natural biome pool, native cap opportunity, actual goal scheduling or spawn success is established.',
        'FormGoal canUse requires own alive and mergeCooldown<=0. It tests executionCooldown--<0, resets to100 with no target or20 with a target, then chooses nearest other alive/cooldown-ready slime in an inflated30 cube. Starting0 fails first test and decrements; these are local evaluations, not exact world-tick intervals. Query/admission is not a lock, fairness guarantee or spherical/global census.',
        'Continuation rechecks both canForm and distance<32; tick requests navigation, then at distance<=.5+(both widths)/2 and other.canForm sums head counts onto THIS actor before removing the other as DISCARDED. It requests combine sound, clears its reference and sets own cooldown600. No child add occurs in merge and no HP transfer is copied directly; FormGoal tick does not itself recheck own canForm. Scheduler/concurrency/native removal effects remain external.',
        'Head count is synced but not clamped in setter. onSyncedDataUpdated refreshes dimensions and resets mergeProgress. Tick notices difference from prevHeadCount, refreshes dimensions, advances progress toward5, then clamps MAX_HEALTH to10..100 and ATTACK_DAMAGE to2..10 and requests heal toward maximum. This is not numerical conservation of HP or head-count-backed global entity count. Exact native data-callback scheduling, healing result and malformed head arithmetic are unverified.',
        'Server-side non-client tick branch with a live combat target counts own deltaMovement length<.1; movement>=.1 resets noMoveTime. At >40 and cooldown<=0 it calls split(1200). Missing/dead targets do not explicitly reset this stored counter. It is sampled velocity, not proof of path failure or physical immobility, and exact wall-clock delay is not established.',
        'split has no explicit side/alive/removal guard and requires heads>=2. It computes integer halves whose arithmetic sum equals the positive original count, assigns own cooldown1200, requests two child adds, then calls own remove(DISCARDED) and returns true. The parameter named cooldown is ignored; literal1200 is used. No null guards, add-result checks, placement/finalizeSpawn or retry/refund. Returntrue is not successful replacement or two live offspring.',
        'makeSlime creates the registered factory, copies position/name/noAI/invulnerable/yaw/body-yaw, assigns requested heads and merge cooldown. It does not copy parent UUID, all NBT, current HP/target or persistence flag in this method; defaults and inherited state remain external. Factory null leads to dereference, not a checked failure path.',
        'The own remove override first requests cache clearing, and whenever heads>=2 AND isDeadOrDying it requests the same two additions BEFORE super.remove, independent of requested reason and without an explicit server or already-removed guard. Native isDeadOrDying reads health<=0. Calling split on a dead actor can enter both own split and this removal branch by source composition; this is a conditional static possibility, not a reproduced four-child outcome or exploit.',
        'Native tickDeath increments deathTime and only on server at>=20 and !isRemoved broadcasts60 then dynamically calls remove(KILLED). Native die first respects Forge death hook and guards removed/dead, records death/loot in ServerLevel, and sets DYING. These normal-path gates do not retroactively guard every external call to the subclass remove override. Entity.remove delegates setRemoved then invalidates capabilities; setRemoved keeps first reason but still has callback/riding operations. Complete dispatcher/Forge join and entity-manager behavior not expanded.',
        'Own dropFromLootTable delegates only heads<=1; this covers that loot-table hook, not every equipment/XP/death or external reward path. Native dropAllDeathLoot internals, actual carried items and drops are unexpanded. A merge donor DISCARDED is not a player kill, and no strict kill/material pickup credit follows from either replacement.',
        'Complete class adds no own additional NBT writer/reader for heads, mergeCooldown, noMoveTime, progress or head offsets. Defaults/own transient fields alone do not certify full inherited save/reload state, attribute reconstruction or cross-mod persistence. Do not claim whole state survives or is completely lost without engine save/read chain.',
        'Single MAGNETIZING rejection delegates super first; no new immunity implementation credit. Attack staging, client particles/sound, head offsets and dimensions are supporting context, not extra ecological families, successful damage, asset production or visual/native acceptance.'
    ],
    proposed_distinction=[
        'EA10 stores complete entity NBT in a block queue and removes a stored item only after checked add success; this chain merges live actors by summed head state and requests uncommitted bisection without a stored queue.',
        'EA13 feeding/hunger growth replaces a planted infant at a maturity threshold; this has no food/pregnancy/world egg and transfers existing live cohort state through merge/stall/death paths. Generic remove/create/add alone would not qualify as a second mechanism.',
        'EA14 host-effect expiry emits offspring; EA17 paired feeding reserves mates and commits pregnancy to an egg block/scheduler. This proposed unit is live cohort aggregation with actor-owned transient head/merge state and alternative stall/death bisection. Independent reviewer may merge or reject; head thresholds, two paths, registry and native helpers each support0.'
    ],
    limitations=[
        'This immutable source-reading proposal is not a formal batch, accepted EA identifier or independent acceptance. No existing candidate id is fabricated and no master/progress/validation policy is edited.',
        'Actual text read: complete435-line entity, complete constructor92..133, four bounded registry ranges, and six native archive ranges. Hash/tree/archive replay proves source identity, not semantic independence, deployed mod compatibility or runtime success.',
        'No loaded natural spawning JSON, NaturalSpawner/cap/local-density path, complete GoalSelector/navigation/Citadel engine, EntityType factory internals, complete entity manager/Forge join callback, save/reload/attributes/death-loot or client sound/particle implementation was executed or fully expanded.',
        'Both merger arithmetic and split child requests are nontransactional source operations; no global population/head conservation, exactly-once death split, safe floor, survival material flow or natural species gap closure is asserted.',
        'Four selected old substantive decision fields actually read; their original source chains and all other accepted families were not reread. All methods/paths/species/render states remain one proposed related implementation at most.',
        'No upstream code execution/Java/Gradle/game, new network/process/display queries, production/assets/sharedJar/userworld/TODO mutations, new schedule or active-hours claim.'
    ],
    supporting_ranges_credit=0, native_gameplay_credit=0, production_changes=0,
    checklist_deletions=0, duration_hours_claimed=0)
with OUT.open('x') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'path':str(OUT.relative_to(ROOT)), 'sha256':sha(OUT.read_bytes()),
                  'mod_ranges':len(refs),'native_ranges':len(native),'accepted_credit':0}))
