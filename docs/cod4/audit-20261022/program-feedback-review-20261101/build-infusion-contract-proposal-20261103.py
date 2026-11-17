"""Seal read-only findings; never import or run production/build/art scripts."""
import csv
import hashlib
import io
import json
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
OUT = ROOT / 'docs/cod4/audit-20261022/program-feedback-review-20261101'
DATA = 'src/main/resources/data/dynasty/infusion/materials.json'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def binding(path):
    raw = (ROOT / path).read_bytes()
    return {'path': path, 'sha256': digest(raw), 'bytes': len(raw)}

def seal(name, obj):
    p = OUT / name
    with p.open('x') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    return binding(str(p.relative_to(ROOT)))

commits = [
    'e3172263b5cdcd3736e2e919f6e795a4bfb2c10f',
    'e5947ef7e45d5d28bc8dcb8987fb617c5048125e',
    '2c8bcacec225f2227a03b8d1da4d8d0fbe43ec4f',
    'c3a13a6639cfe395679be79805ad9c4f0a79214f',
    '69bfa431405031ded80146e67818f964a4b94781',
]
history = []
previous = {}
catalogs = []
for commit in commits:
    raw = git('show', commit + ':' + DATA)
    rows = json.loads(raw)
    index = {r['itemId']: r for r in rows}
    catalogs.append(index)
    history.append({
        'commit': commit,
        'metadata': git('show', '-s', '--format=%H%n%aI%n%s', commit).decode().splitlines(),
        'blob': git('rev-parse', commit + ':' + DATA).decode().strip(),
        'sha256': digest(raw), 'rows': len(rows), 'unique_materials': len(index),
        'unique_effects': len({r['enhancementId'] for r in rows}),
        'added_ids': sorted(index.keys() - previous.keys()) if previous else [],
        'removed_ids': sorted(previous.keys() - index.keys()),
        'changed_existing_rows': {
            k: {'before': previous[k], 'after': index[k]}
            for k in previous.keys() & index.keys() if previous[k] != index[k]
        },
    })
    previous = index

current_raw = (ROOT / DATA).read_bytes()
current = json.loads(current_raw)
current_index = {r['itemId']: r for r in current}
expected = dict(catalogs[2])
added4 = ['fox_pelt', 'wolf_fang', 'crab_shell', 'kappa_scale']
added3 = ['cracked_alchemy_copper', 'alchemist_fire_ash', 'purified_mercury_bead']
for name in added4:
    expected['dynasty:' + name] = catalogs[3]['dynasty:' + name]
for name in added3:
    expected['dynasty:' + name] = catalogs[4]['dynasty:' + name]
assert current_index == expected and len(current) == len(current_index) == 102
assert len({r['enhancementId'] for r in current}) == 41
assert digest(current_raw) == '5005ad2ad656395febbf8b23647b60001f50e91455c29b3120c4cd3bba61fbe7'

full_files = [
    'src/main/java/com/dynasty/infusion/' + name for name in [
        'InfusionContent.java', 'InfusionTraits.java', 'InfusionMenu.java',
        'InfusionRequest.java', 'InfusionBlockEntity.java', 'InfusionCombat.java',
        'InfusionGameTests.java', 'InfusionScreen.java',
    ]
] + ['src/main/java/com/dynasty/MaterialFunctionGameTests.java',
     'tools/audit_infusion.py', 'tools/rebuild_infusion_definitions.py',
     'tools/generate_infusion_art.py', 'docs/maintenance/merge-pr15-2026-10-08.md']
loot_paths = ['src/main/resources/data/dynasty/loot_tables/entities/' + x + '.json'
              for x in ['red_fox', 'gray_wolf', 'crab_soldier', 'river_imp', 'yinyang_liandan_fangshi']]
full_files += loot_paths
partial = {
    'src/main/java/com/dynasty/expansion/ExpansionContent.java': [[1, 34]],
    'src/main/java/com/dynasty/blueprint/BlueprintSalvage.java': [[107, 109], [130, 154]],
}
sources = []
for p in full_files:
    item = binding(p)
    item['read_scope'] = 'whole file across this task and preceding continuation; clipped test slices recovered'
    item['lines'] = len((ROOT / p).read_text().splitlines())
    sources.append(item)
for p, ranges in partial.items():
    item = binding(p)
    item['read_scope'] = 'only specified ranges; enclosing file hash is provenance, not full-file semantic credit'
    item['ranges'] = ranges
    sources.append(item)

atlas_path = 'src/main/resources/assets/dynasty/textures/gui/infusion_crests.png'
atlas = (ROOT / atlas_path).read_bytes()
old_effects = sorted({r['enhancementId'] for r in catalogs[2].values()})
new_effects = sorted({r['enhancementId'] for r in current})
atlas_history = {c: digest(git('show', c + ':' + atlas_path)) for c in commits[1:]}
language = {}
for locale in ['zh_cn', 'en_us']:
    p = 'src/main/resources/assets/dynasty/lang/' + locale + '.json'
    lang = json.loads((ROOT / p).read_text())
    keys = {current_index['dynasty:' + n][k] for n in added4 + added3 for k in ['nameKey', 'descriptionKey']}
    language[locale] = {'binding': binding(p), 'read_scope': 'seven additions name/description key values only',
                        'values': {k: lang.get(k) for k in sorted(keys)}}

findings = [
    {'id': 'F1', 'severity': 'test precondition contradiction',
     'evidence': 'InfusionGameTests.java:27-34 asserts99, then loops ALL. Current reviewed catalog102; assertion prevents round-trip checks.',
     'limit': 'Static contradiction only; no GameTest executed. Retain round-trip invariants and fixed expected catalog; no >=, no len(current)==len(current).'},
    {'id': 'F2', 'severity': 'historical audit scope drift',
     'evidence': 'audit_infusion.py:10 asserts95/40; later enforces byte equality and global unchanged loot/recipes/assets against86c3d2a422a4413626d10bc6f1728bca5744e2b6.',
     'limit': '95→102 and40→41 alone does not make this a valid current audit. Historical44/44 or279 test claims cannot establish current pass.'},
    {'id': 'F3', 'severity': 'destructive current-use generator',
     'evidence': 'rebuild_infusion_definitions.py retains hardcoded95 rows and writes materials, both languages and TSV. It cannot preserve seven additions as written.',
     'limit': 'Not executed. A sourceReference-only correction to tianming_jade exists at e5947; preserve it rather than reconstruct metadata heuristically.'},
    {'id': 'F4', 'severity': 'static GUI atlas indexing mismatch',
     'evidence': 'InfusionScreen.java sorts41 effects, uses10 columns of16px and textureHeight64. zhuque_feather index40→UV(0,64), tile bottom80 outside actual160×64 atlas. cold_ward inserted at6 changes34 old indexes.',
     'limit': 'Atlas bytes unchanged at examined95/99/102 commits. This establishes coordinate/order mismatch, not a native screenshot or visual/art acceptance. Generator fixed64 height also rewrites infusion background; never run it for this repair.'},
    {'id': 'F5', 'severity': 'player-facing trigger mismatch',
     'evidence': 'zh_cn cracked_alchemy_copper description says hostile attack, but xuanwu_shell routes only ShieldBlockEvent with blockedDamage>0, hostile living source, useTicks<=8, player-owned200tick cooldown,60tick resistance.',
     'limit': 'Do not broaden combat to fit wording; correct localized wording after applicable gate. en_us wording is vague rather than an equivalent explicit false trigger.'},
    {'id': 'F6', 'severity': 'three alias regression coverage gap',
     'evidence': 'Three69bfa rows reuse xuanwu_shell/cinnabar/poison_ward; existing representative effect tests select earlier rows and do not establish new material-to-behavior/payment routing.',
     'limit': 'No claim of runtime failure of those behaviors. Dedicated four COD4 material tests already exist and should be retained.'},
]
plan = [
    {'step': 1, 'target': 'reviewed current catalog contract',
     'change': 'Approve fixed102 distinct material IDs /41 behavior IDs from pinned2c8bc95 + c3a13four +69bfathree, with complete expected row fields and explicit provenance. All95 existing rows unchanged across latter additions. Compare current IDs and tuples to this independent historical union; do not derive expected from runtime under test.',
     'validation': 'Fail on missing/extra/duplicate/replaced IDs, wrong effect/family/type/count/cost/tier/gate/name keys/source refs, even if total remains102. Verify registry names, actual applicable equipment and bilingual key resolution separately.'},
    {'step': 2, 'target': 'InfusionGameTests.java:27-34',
     'change': 'Once gated, change exact99 to102 with message95+4+3; keep legacy method name initially to preserve external selectors (search in tools/src/docs/infusion/build.gradle found only declaration; not proof no external callers). Keep registry, active trait, damage11, ForeignData, serialize and exact removal equality checks. Add explicit effect cardinality41 plus independent fixed-contract membership check.',
     'validation': 'Existing incompatible equipment, capacity/family conflicts, legacy4capacity preservation, shared table revision and transaction tests remain; no disabled test or swallowed assertion.'},
    {'step': 3, 'target': 'three69bfa material aliases through real InfusionMenu',
     'change': 'Targeted data cases: cracked_alchemy_copper→xuanwu_shell ARMOR guard; alchemist_fire_ash→cinnabar WEAPON fire; purified_mercury_bead→poison_ward ARMOR purify. Each count2 cost1 tier1 empty row gate, with common get_jade advancement still required.',
     'validation': 'Noncreative server player: valid container/current revision/in-range/table; exactly2 material and3 XP levels paid once, same gear identity/damage/foreign tags/progression preserved, first_infusion only successful apply. Stale duplicate packet or second viewer revision rejected without payment/mutation. Same-effect different material alias rejected9, including selected replacement slot; no duplicate effect layering. Removal selected occupied slot costs1 level, consumes no material, awards no new first_infusion, preserves unrelated NBT. Missing advancement/material/XP/incompatible gear refuses without payment. Creative bypass remains existing behavior.'},
    {'step': 4, 'target': 'alias-specific combat contracts; retain existing behavior',
     'change': 'Exercise each new material equipped through its actual effect, not findFirst(effect). Copper: positive hostile ShieldBlock in first8 use ticks grants60tick resistance at200tick cooldown; ordinary unblocked hurt and late block must not trigger. Ash: validated qualifying weapon hit ignites non-fire-immune target3sec at120tick cooldown; canceled/nonpositive/synthetic/invalid target cases keep no effect. Mercury: positive hostile damage while POISON present clears poison+slowness at200tick cooldown; slowness alone or no hostile source does not trigger.',
     'validation': 'Prove player/effect-owned cooldown cannot be reset by changing between old/new aliases or copied gear; unequipped inventory has no armor effect. Direct Forge callback tests establish callback behavior only; eventual permitted native C2S/combat/acquisition traces are a distinct acceptance step.'},
    {'step': 5, 'target': 'tools/audit_infusion.py and current validation entrypoint',
     'change': 'Preserve86c3 historical audit and clearly label its95/40 branch scope; add separately named current read-only validator bound to reviewed102/41 manifest and current-scope input hashes. Retain relevant invariants with per-scope authorized changes, not a blanket no-loot/no-recipe change since86c3. Do not weaken current checks merely to satisfy historical script.',
     'validation': 'Report static contract results independently from registry-loaded GameTests and native client/server evidence. Atlas capacity is its own contract, not simply uniqueEffectCount==imageCellCount without correct mappings.'},
    {'step': 6, 'target': 'rebuild_infusion_definitions.py and docs/infusion/material-mapping.tsv',
     'change': 'Quarantine historical95 writer behind explicit archival output path/preconditions before future use; prepare current read-only exporter from approved canonical102 catalog, preserving dedicated aliases, source refs and tianming_jade correction. Do not merge old generated defaults over current rows. Historical TSV95 must be labeled archival or replaced by approved current export, not treated as proof102 exists.',
     'validation': 'Future exporter operates to a new output directory and is diff-reviewed before installation; prove no writes to current materials/lang/art from historical mode. No generator executed during this task.'},
    {'step': 7, 'target': 'InfusionScreen.java and crest mapping contract',
     'change': 'Use explicit stable effect→cell map preserving40 legacy identities; allocate a reviewed cold_ward cell in fifth row of capacity50 (e.g.160×80), and derive/declare matching texture dimensions in renderer. Expand atlas only through texture-owner workflow and applicable reference gate; preserve existing40 cell pixels. Do not use modulo wrapping or map41 effects blindly onto40 cells. Do not run generate_infusion_art.py because it also rewrites background.',
     'validation': 'All41 effect IDs map to valid declared cells, every tile within actual PNG dimensions; legacy effect/cell identity retained under shuffled material input. New cell art and native GUI appearance need separate acceptance. Main menu/background and infusion background bytes must remain unchanged. No asset creation performed.'},
    {'step': 8, 'target': 'localized cracked_alchemy_copper description',
     'change': 'After gate, align Chinese and English with early hostile shield-block trigger,3sec resistance and10sec cooldown; keep original item/effect IDs and display names. Example Chinese: 装备后，举盾前8刻内成功格挡敌人攻击时获得3秒抗性提升；冷却10秒。',
     'validation': 'Localization review against native trigger and equipped-source rules; do not expand xuanwu_shell into ordinary hurt trigger or invent another effect.'},
]
tsv = 'docs/infusion/material-mapping.tsv'
tsv_rows = list(csv.DictReader(io.StringIO((ROOT / tsv).read_text()), delimiter='\t'))
proposal = {
    'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'READ_ONLY_HISTORY_CONFIRMED_PRECISE_REPAIR_PLAN_PENDING_APPLICABLE_GATE',
    'head_observed': git('rev-parse', 'HEAD').decode().strip(),
    'coordinator_request_receipt': binding('docs/cod4/audit-20261022/quest-integration-20261030/coordinator-infusion-current-contract-delta-20261103.json'),
    'scope': 'Independent post95/post99 source audit and proposed contract repair; no production/test/asset edits or runtime tests.',
    'sources': sources, 'materials': binding(DATA), 'material_history': history,
    'current_contract': {'rows': 102, 'unique_materials': 102, 'unique_effects': 41,
                         'matches_pinned95_plus4_plus3_all_fields': True,
                         'new_effects_after95': ['dynasty:cold_ward'],
                         'semantic_read_limit': 'Seven added rows examined in full plus transaction/combat methods; old95 structural equality is not95 independent new semantic credits.',
                         'seven_added_rows': [expected['dynasty:' + n] for n in added4 + added3]},
    'registrations': {'four': 'ExpansionContent.java:11-13,26-32 DeferredRegister and event bus',
                      'three': 'BlueprintSalvage.java:107-109,137-144 ComponentItem is ordinary Item; Use parameter ignored, NOT an infusion applicability definition.',
                      'three_introduction_commit': commits[4],
                      'loot': {p: json.loads((ROOT / p).read_text()) for p in loot_paths},
                      'limit': 'Source declarations and loot tables read; no actual registry boot, killed mob or acquired drop verified.'},
    'languages': language,
    'atlas': {'binding': binding(atlas_path), 'inspection': 'PNG header and immutable bytes only, no visual rendering',
              'size': list(struct.unpack('>II', atlas[16:24])), 'historical_sha256': atlas_history,
              'current_effect_index': dict(zip(new_effects, range(len(new_effects)))),
              'old_effect_index': dict(zip(old_effects, range(len(old_effects)))),
              'shifted_existing_effects': [e for e in old_effects if old_effects.index(e) != new_effects.index(e)]},
    'tsv': {'binding': binding(tsv), 'parsed_rows': len(tsv_rows), 'semantic_read_scope': 'row count and IDs; no claim all rows manually studied'},
    'findings': findings, 'repair_plan': plan,
    'gates': {'applicable_accepted1000_not_established': True,
              'immune_reference_observation': json.loads((ROOT / 'docs/cod4/audit-20261022/immune-feedback-research/progress.json').read_text()),
              'note': 'Immune476/1000 does not satisfy1000; unrelated completed migration research cannot silently authorize infusion repair. Coordinator must establish applicability. Until then source/test/art implementation stays pending; read-only research may continue.'},
    'validation': {'history_union_check': 'PASS_STATIC_ONLY', 'production_tests_executed': False,
                   'native_runtime_credit': 0, 'new_research_credit': 0,
                   'note': 'This builder checks historical/data bindings only. It never runs audit_infusion.py, rebuild script, art generator, Java, Gradle or game.'},
    'boundaries': {'production_changes': False, 'test_changes': False, 'art_changes': False,
                   'shared_jar_changes': False, 'game_starts': 0, 'network_requests': 0,
                   'master_ledger_changes': False, 'checklist_deletions': 0, 'hours_claimed': 0},
}
sealed = seal('infusion-current-contract-repair-proposal-20261103.json', proposal)
handoff = {
    'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'INFUSION_95_99_102_HISTORY_AND_PRECISE_REPAIR_PROPOSAL_READY_NO_IMPLEMENTATION',
    'worker_thread_id': '01a16392-312e-72f2-a4dd-56e184f9cb02',
    'prior_checkpoint': binding(str((OUT / 'direct-dispatch-program-handoff-033.json').relative_to(ROOT))),
    'proposal': sealed,
    'builder': binding(str(Path(__file__).relative_to(ROOT))),
    '045_evidence_pending_review': binding(str((OUT / 'immune-reference-batch-045.json').relative_to(ROOT))),
    '045_credit': 0, 'formal_count_observed': 476, 'gap_to1000': 524,
    'findings': ['95→99 adds4 and cold_ward;99→102 adds3 aliases, no extra effects',
                 'current ALL102 contradicts test99; historical audit95/40 is not current audit',
                 'historical writer would drop7 rows',
                 '41effect GUI indexes40cell unchanged atlas; last tile outside bounds;34 old indexes shifted',
                 'copper description omits early shield-block trigger'],
    'next_work': 'Coordinator reviews exact proposal and applicable accepted1000 evidence; specialist can continue original-program reference research. No gated code/test/art work or game run is authorized by this receipt alone.',
    'boundaries': proposal['boundaries'],
}
receipt = seal('direct-dispatch-program-handoff-034.json', handoff)
print(json.dumps({'proposal': sealed, 'handoff': receipt, 'status': 'SEALED_STATIC_PROPOSAL_ONLY'}, ensure_ascii=False))
