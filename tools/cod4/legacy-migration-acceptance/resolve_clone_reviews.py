"""Resolve previously pending Clone chains after reading actual lifetime/ownership bodies."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';p=O/'reviews/batch-001.json';a=json.loads(p.read_text());idx={r['candidate_id']:r for r in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
for n in a:
 if n['candidate_id']=='0d68f4864ec09ce33745':
  n.update(status='accepted',family='irons-death-filtered-learned-spells-owner-transfer',trigger='ServerPlayerEvents.onPlayerCloned requires ServerPlayer target and wasDeath',input='old SummonTimer effects, SyncedSpellData learned spells/selection and spell cooldown map',output='copies only SummonTimer active effects; new synced object from getPersistentData uses old identity then binds newServerPlayer; learned set addAll; selection reference assigned; cooldown entries put into new map',preservation='getPersistentData full body now verified: fresh synced object does NOT copy isCasting/heartStopDamage/evasion hits. Owner reference updated while retaining original entity identity until clone identity initialized.',application_limit='Selection and cooldown values shallow shared, not deep copies. Upstream deliberately preserves selected summon timers/cooldowns; Dynasty should use audited permanent fields and exclude temporary immunity/counterattack rather than importing that policy.',supporting_candidates=['9bf1513f0d649069a5ec'])
 if n['candidate_id']=='d070215afd88b945e347':
  n.update(status='accepted',family='aether-copy-on-death-attachment-post-copy-reset',trigger='Aether Clone listener -> CapabilityHooks.AetherPlayerHooks.clone(newPlayer,wasDeath) -> attachment.handleRespawn',input='new player attachment declared .serialize(CODEC).copyOnDeath(); wasDeath distinguishes death versus End portal clone',output='on death resets remedyStartDuration0; all clone paths set shouldSyncAfterJoin true',preservation='AetherPlayerAttachment.CODEC full declaration includes life_shard_count and seen_sun_spirit permanent history alongside saved_health/remedy duration and optional mount UUID/NBT. Registration declares copyOnDeath; handler then explicitly resets timed remedy on death.',application_limit='NeoForge framework copy implementation not traced here; claim covers actual post-copy filter and source registration contract, not proven deep-copy of all codec fields. Handler count only once with listener/hook/constructor as support. Borrow preserve achievements while clearing timed effects.',supporting_candidates=['2ccaf826c400444c698a','75904f1ff320e74cd7a0','32f8f6d0143401bb71c6'])
p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
extras=[]
for i,relative in [('d070215afd88b945e347','attachment/AetherDataAttachments.java'),('d070215afd88b945e347','attachment/AetherPlayerAttachment.java')]:
 e=idx[i];root=(R/e['private_file'])
 while root.name!='aether':root=root.parent
 f=root/relative;raw=f.read_bytes();extras.append(dict(primary_candidate_id=i,revision=e['revision'],file=str(f.relative_to(R)),sha256=hashlib.sha256(raw).hexdigest(),full_source=raw.decode(),credit=0))
e=idx['0d68f4864ec09ce33745'];f=R/e['private_file'];root=f
while root.name!='ironsspellbooks':root=root.parent
f=root/'api/magic/MagicData.java';raw=f.read_bytes();extras.append(dict(primary_candidate_id=e['candidate_id'],revision=e['revision'],file=str(f.relative_to(R)),sha256=hashlib.sha256(raw).hexdigest(),full_source=raw.decode(),credit=0,observation='Disk load/save inspected for clone comparison; provider wrapper no independent credit. Disk loads current mana/cooldowns/recasts then synced data; actual Clone uses selected subset instead.'))
(O/'clone-chain-support-evidence.json').write_text(json.dumps(extras,ensure_ascii=False,indent=2)+'\n')
print('resolved2 prior pending; extra source context credit0')
