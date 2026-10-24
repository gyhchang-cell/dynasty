"""Verify every inherited site against its pinned local source; record armor-specific follow-up reading."""
from pathlib import Path
import collections, hashlib, json, re
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'evidence' / 'references.json'
CORPUS = ROOT / 'build/creature-reference-1000'
source = ROOT / 'docs/cod4/audit-20261022/status-reference-1000.json'
refs = json.loads(source.read_text())['sites']
repos = {}
for p in CORPUS.glob('*/source.json'):
    meta = json.loads(p.read_text())
    repos[meta.get('repo'), meta.get('sha')] = p.parent
checks = []
for s in refs:
    p = repos[s['repo'], s['revision']] / s['path']
    raw = p.read_bytes()
    text = p.read_text()  # universal newlines, as in the original study
    assert hashlib.sha256(raw).hexdigest() == s['source_sha256'], p
    assert s['operation'] in text.splitlines()[s['line'] - 1], p
    assert s['excerpt'] in text, p
    assert hashlib.sha256(re.sub(r'\s+', '', s['excerpt']).encode()).hexdigest() == s['excerpt_sha256'], p
    checks.append({'url': s['url'], 'source_sha256': s['source_sha256'], 'excerpt_sha256': s['excerpt_sha256'], 'verified': True})
assert len(checks) == len({s['excerpt_sha256'] for s in refs}) == 1000
# Additional actual source ranges read for the precise failure modes; NOT counted as another 1000.
repo = 'Polarice3/Goety-2'
revision = next(s['revision'] for s in refs if s['repo'] == repo)
followup = []
for file, start, end, observation, application in [
    ('PotionEvents.java', 129, 146, 'Armor modifier is revoked when either its effect or equipment condition fails.', 'Revoke temporary armor windows at threshold loss before they can be reactivated by re-equipping.'),
    ('PotionEvents.java', 716, 770, 'Amplifier transitions remove obsolete charged modifiers; absence removes charge benefits.', 'Test threshold downgrades and temporary states separately from idempotent UUID refresh.'),
    ('ItemEvents.java', 143, 157, 'Weapon benefit reads both main hand and offhand and removes its modifier when the predicate fails.', 'A paired-axe counter requires both original hands; Xuanwu counter source must not masquerade as an axe grant.'),
    ('ModEvents.java', 278, 284, 'Player clone handling copies the player-owned cooldown capability.', 'Retain persisted lastStand cooldown through gear changes and native player save/read; do not clear it with transient windows.'),
    ('SoulEnergyEvents.java', 75, 95, 'Movement state and airborne cooldown are checked on the actual player at the end of the tick.', 'Read the current four-piece requirement at damage acceptance as well as removing stale stride state on equipment refresh.'),
]:
    rel = 'src/main/java/com/Polarice3/Goety/common/events/' + file
    p = repos[repo, revision] / rel
    excerpt = '\n'.join(p.read_text().splitlines()[start-1:end])
    followup.append({'url': f'https://github.com/{repo}/blob/{revision}/{rel}#L{start}-L{end}',
        'source_sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'excerpt': excerpt,
        'observation': observation, 'application': application})
report = {'inherited_source': str(source.relative_to(ROOT)), 'inherited_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'verified_sites': len(checks), 'deduplication': 'whitespace-normalized excerpt SHA256; sites, not independent mods or playtests',
    'scope_limit': 'The 1000 status/immune/removal excerpts include static fireImmune registrations and provide only broad lifecycle context. Hash/line verification does not satisfy the armor window/owner/cooldown gate. The five follow-up ranges are partial reading, overlap whole methods, and do NOT close the 1000-site research gap.',
    'armor_gate_credit_from_inherited_count': 0, 'five_ranges_complete_gate': False,
    'timing_boundary': 'Existing fixes preceded satisfaction of the armor-specific gate. Later research must not be represented as completed before implementation.',
    'operations': dict(collections.Counter(s['operation'] for s in refs)), 'checks': checks, 'armor_specific_followup': followup}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Verified 1000 inherited excerpt locations only; armor-specific gate is NOT satisfied by that corpus or five follow-up ranges.')
