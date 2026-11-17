"""Zero-credit static ownership investigation. Not a completed migration review."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';base=R/'tools/cod4/legacy-migration-acceptance/.work/sources/TeamWizardry__Wizardry';src=next(r for r in json.loads((O/'sources.json').read_text()) if r['repo']=='TeamWizardry/Wizardry')
paths=['api/capability/world/StandardWizardryWorld.java','api/capability/world/WizardryWorldStorage.java','api/capability/world/WizardryWorldCapability.java','api/SpellObjectManager.java','api/lifetimeobject/LifetimeObjectManager.java','common/core/nemez/NemezTracker.java','common/core/nemez/NemezManager.java']
files=[]
for f in paths:
 rel='src/main/java/com/teamwizardry/wizardry/'+f;p=base/rel;raw=p.read_bytes();files.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(raw).hexdigest(),source_url=f'https://github.com/TeamWizardry/Wizardry/blob/{src["sha"]}/{rel}',full_source=raw.decode(),credit=0))
data=dict(status='partial_context_review_no_credit',credit=0,candidates=['b236c080e9dc6c503dbf','a87cca0835c682b32707'],observations=[
 'Capability.init new WizardryWorldStorage resolves private nested class, not same-named top-level class. Actual attach provider StandardWizardryWorld implements its own INBTSerializable path. A top-level source file is not proof its UUID backup map reader is registered.',
 'Standard writer emits only spell_object_manager and block drives. entityNemezDrives and zombieBackupTracker omitted. Therefore cannot claim backup count survives disk just because unregistered top-level storage serializes it.',
 'Standard reader recreates manager only when key present and appends/replaces matching positions in blockNemezDrives without clearing absent old positions.',
 'LifetimeObjectManager saves active entries+remaining ticks, not pending adds queue. Read clears entries but not pending adds and does not call start; restored countdown invokes tick/stop through later manager ticks.',
 'NemezManager serializes pushed moments only, not transient currentMoment. NemezTracker trackedEntities live set is not serialized. Moment.fromNBT and full snapshot graph not yet reviewed, no claim complete time snapshot restoration.',
 'Scope relevance to old item/permanent player repair and full lifecycle remain unresolved. All source/AST candidates and helper contexts here count0, not completed study count.'
],files=files)
(O/'wizardry-world-owner-boundary-pending.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('7 exact sources captured,0 credit')
