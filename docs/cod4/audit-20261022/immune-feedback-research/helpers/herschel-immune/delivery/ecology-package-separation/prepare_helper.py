"""Snapshot read-only observers into an isolated helper namespace; no game/world/production writes."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'tools/cod4/ecology-acceptance/bounded-src/EcologyOpportunityObserver.java';before=sha(source);original=source.read_text();new=original.replace('package com.dynasty.expansion;','package com.dynasty.ecologyqa.observer;').replace('@Mod.EventBusSubscriber(modid = "dynasty")\n','');assert new!=original and new.replace('package com.dynasty.ecologyqa.observer;','package com.dynasty.expansion;').replace('public final class EcologyOpportunityObserver','@Mod.EventBusSubscriber(modid = "dynasty")\npublic final class EcologyOpportunityObserver')==original
out=B/'src/com/dynasty/ecologyqa/observer/EcologyOpportunityObserver.java';out.parent.mkdir(exist_ok=True);out.write_text(new)
gate=R/'tools/cod4/ecology-acceptance/native-gate-src/NativeCreatureGateObserver.java';shutil.copy2(gate,B/'src/com/dynasty/ecologyqa/NativeCreatureGateObserver.java')
for mixin in (gate.parent/'mixin').glob('*.java'):
 dest=B/'src/com/dynasty/ecologyqa/mixin'/mixin.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(mixin,dest)
quiet=R/'tools/cod4/mob-network-acceptance/src/com/dynasty/mobnetworkqa/mixin/QuietWindowMixin.java';dest=B/'src/com/dynasty/ecologyqa/mixin/QuietWindowMixin.java';dest.parent.mkdir(exist_ok=True);dest.write_text(quiet.read_text().replace('com.dynasty.mobnetworkqa.mixin','com.dynasty.ecologyqa.mixin'))
assert sha(source)==before
manifest={'passive_source':str(source.relative_to(R)),'passive_original_sha256':before,'passive_private_copy_sha256':sha(out),'passive_copy_edits':['namespace changed to prevent split package with production expansion','removed automatic subscriber annotation; explicit registration exactly once by private bootstrap'],'gate_source':str(gate.relative_to(R)),'gate_source_sha256':sha(gate),'gate_copy_sha256':sha(B/'src/com/dynasty/ecologyqa/NativeCreatureGateObserver.java'),'quiet_window_source':str(quiet.relative_to(R)),'quiet_window_source_sha256':sha(quiet),'quiet_window_edit':'namespace only; already actual fullpack hidden/unfocused verified hook retained','game_started':False,'original_observer_written':False,'production_written':False}
(B/'helper-source-bindings.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('Isolated helper source snapshot prepared; no original source/world writes')
