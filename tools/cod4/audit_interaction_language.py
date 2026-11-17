"""Read-only coverage check, explicitly not client rendering/network acceptance."""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
sources = [ROOT / p for p in (
    'src/main/java/com/dynasty/expansion/SmallInteractions.java',
    'src/main/java/com/dynasty/cod3/SwordDance.java',
    'src/main/java/com/dynasty/cod3/DialogueGraph.java',
)]
language = ROOT / 'src/main/resources/assets/dynasty/lang/zh_cn.json'
duplicates = []

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            duplicates.append(key)
        result[key] = value
    return result

lang = json.loads(language.read_text(), object_pairs_hook=unique_pairs)
texts = {str(p.relative_to(ROOT)): p.read_text() for p in sources}
ids_match = re.search(r'IDS=List\.of\((.*?)\);', texts[str(sources[0].relative_to(ROOT))])
ids = re.findall(r'"([a-z_]+)"', ids_match[1])
assert len(ids) == len(set(ids)) == 15
keys = {f'interaction.dynasty.{site}' for site in ids}
keys |= {f'block.dynasty.{site}' for site in ids}
for text in texts.values():
    # Complete literal keys; dynamically composed suffixes are expanded below.
    keys |= {key for key in re.findall(r'"((?:message\.dynasty\.cod4\.|cod4\.dynasty\.(?:ghost_boat|poison_tea|sword_dance)\.)[a-z_0-9]+)"', text)
             if not key.endswith('_')}
keys |= {f'message.dynasty.cod4.puzzle_{suffix}' for suffix in ('north', 'east', 'south', 'west', 'stand', 'sneak')}
keys |= {f'cod4.dynasty.sword_dance.step_{step}' for step in range(3)}
missing = sorted(key for key in keys if not isinstance(lang.get(key), str) or not lang[key].strip())
without_chinese = sorted(key for key in keys if key in lang and not re.search(r'[\u3400-\u9fff]', lang[key]))
report = {
    'date': datetime.datetime.now().astimezone().isoformat(),
    'status': 'PASS_STATIC_ONLY' if not missing and not without_chinese and not duplicates else 'FAILED',
    'sites': [{'id': site, 'name': lang.get(f'block.dynasty.{site}'), 'clue': lang.get(f'interaction.dynasty.{site}')} for site in ids],
    'reviewed_keys': {key: lang.get(key) for key in sorted(keys)},
    'missing_or_empty': missing,
    'without_chinese': without_chinese,
    'duplicate_language_keys': duplicates,
    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources + [language]},
    'scope': 'Current literal and explicitly expanded dynamic interaction keys resolve to nonempty Chinese resource strings. No production changes.',
    'not_verified': ['client rendering, line wrap and occlusion', 'actual C2S clicks', 'two TCP clients and player progress isolation'],
    'new_research_credit': 0,
    'game_clients_started': 0,
    'servers_started': 0,
}
out = ROOT / 'docs/cod4/audit-20261022/interaction-natural-acceptance/chinese-resource-audit-20261026.json'
if out.exists():
    assert json.loads(out.read_text())['source_sha256'] == report['source_sha256'], 'Use a separate dated receipt after input changes'
else:
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in report.items() if key not in ('sites', 'reviewed_keys', 'source_sha256')}, ensure_ascii=False))
raise SystemExit(0 if report['status'] == 'PASS_STATIC_ONLY' else 1)
