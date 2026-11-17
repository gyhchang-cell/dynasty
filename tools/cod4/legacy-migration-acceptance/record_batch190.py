from review_batch import record,O
import json
idx=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()))
notes={
'V4648':('rejected','Empty register with entity comments only; no implementation to credit.'),
'V4649':('rejected','Whole source: consumable animation spear->trident only, absent compound no-op, all other payload retained. Single renamed literal repeated mapping shape, no distinct custody/Clone/format preservation algorithm. Do not count key-only aliases.'),
'V4651':('rejected','Whole options-only source: split graphicsMode into four string settings with fancy default plus force graphicsPreset custom; overwrites existing values without guard. Client graphics configuration, outside actual game item/player progression scope; generic formatting0.'),
'V4656':('rejected','Empty register with camel_husk/parched comments only; registration comments are not actual implementation.'),
'V4533':('rejected','Whole source installs common Items-list walker for shelf, no independently studied owner or migration semantic; generic traversal registration0. No additional library study claimed.'),
'V4535':('pending','Whole entity converter examined: copper_golem weather_state integer1/2/3 -> exposed/weathered/oxidized, default including wrong type ->unaffected. Relevant state format conversion candidate; not automatically accepted without semantic dedup against existing weather/state migration families and actual gameplay-owner context. No count, no requirement for full roundtrip+fallback imposed.'),
'V4537':('rejected','Whole source only delegates V3451.removeLight for CHUNK; common support plus lighting cache invalidation is outside item/durable-player state migration,0. Delegated method not newly studied here.'),
'V4541':('rejected','Whole source static one-entry chain->iron_chain rename map reused block and item converters; user excluded key-only repeated tables from credit. Not independent new mechanism.'),
'V4544':('rejected','Whole level converter: world border fields moved to fresh world_border with fixed numeric defaults then old keys removed; overwrites existing child; generic world boundary configuration outside assigned item/permanent-player study. Observations retained0, no claim valid restoration in new consumer.'),
'V4548':('duplicate','Whole source reread; PLAYER respawn angle->yaw/pitch0/missing dimension overworld already accepted d39596e37b5b959cfecc. Register wrapper cannot earn second credit. LEVEL world spawn group likewise not new separate owner study here.')}
rows=[];files=[]
for name,(status,reason) in notes.items():
 r=next(x for x in idx if x['repo']=='PaperMC/DataConverter' and x['path'].endswith('/'+name+'.java') and x['method']=='register')
 rows.append(dict(candidate_id=r['candidate_id'],status=status,reason=reason,supporting_candidates=[]));files.append(r['private_file'])
record(190,rows,files)
