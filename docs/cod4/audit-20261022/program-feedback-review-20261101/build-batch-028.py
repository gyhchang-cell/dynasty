#!/usr/bin/env python3
"""Save actual thermal review and exclusions; no semantic credit awarded."""
import hashlib
import json
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
B = R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-043'
sha = lambda b: hashlib.sha256(b).hexdigest()
mp = B/'source-manifest.json'
m = next(x for x in json.loads(mp.read_text()) if x['repo']=='Glitchfiend/ToughAsNails')
names = [
 'temperature/TemperatureData.java','temperature/TemperatureHandler.java','temperature/TemperatureHooksClient.java',
 'temperature/TemperatureOverlayRenderer.java','temperature/TemperatureHelperImpl.java','temperature/BuiltInTemperatureModifier.java',
 'mixin/MixinLivingEntity.java','mixin/MixinPlayer.java','mixin/MixinServerPlayer.java','mixin/MixinServerLevel.java',
 'mixin/client/MixinGui.java','network/UpdateTemperaturePacket.java','api/temperature/TemperatureHelper.java',
 'api/temperature/TemperatureLevel.java','init/ModApi.java','init/ModPackets.java','init/ModClient.java',
 'init/ModConfig.java','core/ToughAsNails.java','config/TemperatureConfig.java']
paths = ['common/src/main/java/toughasnails/'+f for f in names] + [
 'forge/src/main/java/toughasnails/forge/core/ToughAsNailsForge.java',
 'common/src/main/resources/toughasnails.mixins.json','forge/src/main/resources/toughasnails.forge.mixins.json',
 'fabric/src/main/resources/toughasnails.fabric.mixins.json','neoforge/src/main/resources/toughasnails.neoforge.mixins.json']
entries = {x['path']:x for x in m['files']}
refs = []
for up in paths:
 e=entries[up];raw=(R/e['source']).read_bytes()
 refs.append({'path':e['source'],'upstream_path':up,'lines':[1,len(raw.decode().splitlines())],
              'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
              'purpose':'Complete containing class/declaration actually read for temperature production, state writes, synchronization, display and exit limits; support0.',
              'reading_context':'Actually read during028 in bounded outputs; complete mod source files only, not native engine or every external dependency.'})
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
comp={
 'coldsweat-native-critical-temperature-source-denial-and-bound-hurt-sound':'Existing actual temperature/effect-qualified thermal hurt production refusal. TAN heat accumulation/decay and a different numerical threshold alone do not establish a new refusal family; no new credit merely for temperature HUD.',
 'coldsweat-native-thermal-qualified-voluntary-input-vector-replacement':'Existing final thermal voluntary-input substitution is genuinely a different write from TAN transient positive ADD_VALUE modifier; TAN names do not prove a slowing/control-refusal mechanism. Record positive write, do not count a supposed heat slow.',
 'coldsweat-native-frozen-health-healing-budget-and-independent-heart-overlay':'Existing health-budget denial plus independent heart feedback. TAN heart replacement reports hyperthermia state only, not denial/healing settlement; generic heart tint or texture variants cannot add credit.',
 'betweenlands-native-cleansed-exposure-reacquired-under-independent-immunity-deadline-and-unmasked-target-qualification':'Existing latent exposure masked by an independent immunity deadline. TAN clemency forces displayed/current temperature neutral while target/delay fields remain, but no new independent timed mask/reacquisition family is proved and clemency producer is already migration-owned.',
 'betweenlands-native-exposure-load-control-attenuated-by-server-observed-struggle-with-independent-hurt-cue-and-residual-damage-clock':'Existing exposure load, counteraction and residual damage clock with actual cue. TAN thermal buildup/decay alone is not a new general exposure family; no struggle or independent refusal receipt here.',
 'mekanism-native-scuba-oxygen-presence-preventable-magic-denial':'Existing explicit resource/equipment-qualified final damage cancellation. TAN resistance suppresses generation/decays exposure, not cancellation of every matching incoming source or paid defense; do not conflate these.'}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlraw=mlp.read_bytes();ml=[json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]
mids=['be6ccee3bf61205aedc6','5bd0c61ab6940e988afc','6bceaaffd17c9693b455']
mkeys=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
doc={
 'schema_version':1,'owner':'program-feedback-review-028','repo':m['repo'],'commit':m['commit'],'branch':m['branch'],
 'provenance':{'manifest_path':str(mp.relative_to(R)),'manifest_sha256':sha(mp.read_bytes()),'bare_git_path':str((B/'upstream.git').relative_to(R)),'git_tree':m['git_tree'],'acquisition':'Existing fixed local cache only; no download or upstream execution.'},
 'status':'uncredited_thermal_overlap_and_incomplete_native_freeze_lifecycle','research_credit':0,'maximum_proposed_credit':0,
 'production_changes':False,'runtime_executed':False,
 'semantic_family':'uncredited-toughasnails-thermal-state-control-and-freeze-ownership-triage',
 'source_refs':refs,
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),
   'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comp.items()],
   'reading_order':'All six accepted substantive decisions and all three migration substantive decisions read before candidate source. Initial combined output clipped Swarm limitations; exact full Swarm decision separately recovered before source read. No claim prior underlying source chains reread.',
   'limits':'No whole novel mechanism proposed. Actual source work is retained without credit; wrappers/metadata/line counts and incorrect names cannot establish novelty.'},
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlraw),'rows':len(ml),
   'comparisons':[{'accepted_id':x['candidate_id'],'complete_semantic_decision_read':{k:x[k] for k in mkeys},
      'distinction':'Retain this whole migration owner. No new credit for clemency grant history, survival-stat save/load or thermoregulator spatial fuel state. This turn actually reread specified current-session temperature code, not the complete old machine/acquisition source chain.'} for x in ml if x['candidate_id'] in mids]},
 'full_chain':[
  {'stage':'real bindings','observation':'Forge @Mod constructor calls ToughAsNails.init→config, registrars, event handlers, packets and API singleton. Common mixin list names Player/ServerPlayer/ServerLevel/LivingEntity and client Gui. Player.tick TAIL invokes temperature handler. Native mixin application and GlitchCore event/transport internals unexecuted; other-loader manifests are context, not port credits.'},
  {'stage':'temperature input and delayed state','observation':'Server enabled handler prunes thermoregulator positions, decreases positional delay and increments dry timer. Without clemency computes biome/night/altitude/rain/proximity then ordered player/held/armor/internal modifiers. On target change resets delay, optionally caps rebound delay. Movement test uses pre-update currentTargetLevel while increment direction reads updated target. With clemency writes level NEUTRAL but retains target/delay and does not execute modifiers. Default target delay500; armor50/held375/player125/internal20; configuration changes and enum values are not separate mechanisms.'},
  {'stage':'environment boundaries','observation':'Helper enum increment returns a new clamped enum. immersionModifier dry residual branch calls current.increment without assignment, so that branch leaves current unchanged despite wetTicks test. Armor branch caps newly reached extremes, positive thermal enchant sets NEUTRAL, internal warmth then chill apply before similar cap. Modifier ordering cache is initialized once; config validator compares sets so duplicates are not rejected by that predicate. Thermoregulator influence/AreaFill full producer lifecycle not reread and not new credit.'},
  {'stage':'heat production and release','observation':'Extremity delay decrements; lastLevel!=level and current extreme reassigns configured extremityDamageDelay. lastLevel is the synchronization cache, not a separate transition sample, so exact native tick/sync scheduling matters. Eligible noncreative/nonspectator HOT/no fire resistance/delay0 increases heat to140; otherwise decreases by2 to0. Every enabled tick removes existing speed_modifier then adds positive 0.015*heatPercent with ADD_VALUE when getOnPos block is non-air and heat>0. This is not a negative slow; grounded test is not onGround. Every tickCount%40==0 and heat>=140 requests1 hyperthermia hurt, ignores return. Other raw external out-of-range values can survive decay above140; no universal creative/fire-resistance damage-immunity guarantee from malformed/injected state.'},
  {'stage':'sync and real heat feedback','observation':'ServerPlayer.doTick TAIL sends to this player when level/heat/nearby set differs from last caches. sync updates lastLevel/lastHeat but calls setNearbyThermoregulators(current) rather than setLastNearbyThermoregulators, so a nonempty set can continue triggering sync; not an executed network-rate claim. Packet carries enum, heat int and BlockPos set; client context player receives writes, no target identity/session/sequence. Registered overlay reads heat to draw outline at fraction heat/140; heart HEAD mixin always cancels original after rendering replacement, overheated hearts only for NORMAL and fully hyperthermic, others original sprite. UI does not prove hurt accepted. Heat decay eventually removes heat-dependent drawing under ordinary enabled updates. Disabled server handler returns before speed removal/heat decay, while heart/outline methods lack their own enable gate; hot disable is not proved full cleanup.'},
  {'stage':'meter animation exit','observation':'Shared client updateCounter increments only unpaused END. Meter draw suppressed when temperature disabled; requires survival mode and actual FOOD event path. On changed visible level sets flash deadline+3 (despite comment16) and arrow deadline+15; arrow cleared on strict counter>deadline. Random movement seeded by counter, so pause freezes it. Static previous-level/counters have no world/player/session reset in this class; returning to UI can compare new player level with old remembered level. These presentation wrappers are support0.'},
  {'stage':'native freeze ownership incomplete','observation':'LivingEntity aiStep redirect suppresses all matched native setTicksFrozen calls only for Player, even with temperature disabled; nonplayers receive original requested setter. Injection before matched getTicksFrozen reads TAN level/extremity. Without ICE_RESISTANCE: icy noncreative/nonspectator with delay0 adds2 capped at native required+2; else powder-snow/canFreeze adds1 capped at native required. ICE_RESISTANCE writes0. If final count equals entry count, performs melt -2, including when a cap has prevented increase. This conditional can alternate capped count and cap-2 across repeated standalone hook invocations. No native aiStep callsite count/order, frozen-data sync, damage and overlay final lifecycle available/read here; do not claim once-per-tick oscillation or full native freezing control.'},
 ],
 'critical_boundaries':[
  'Heat/stat/clemency persistence families retain their existing whole owners; no split of migration chain into new credits just because reread from immunity role.',
  'Temperature disable exits before normal cleanup; source observations identify conditional risks, not reproduced bugs. No fixes below gate.',
  'Positive heat speed attribute is the actual sign in source; a method name HeatExhaustion is not evidence of movement denial.',
  'Native freeze final lifecycle is unclosed. ICE_RESISTANCE brewing/application and effect expiry are not expanded. No extra count for a wrapper that calls native freeze setters.',
  'All25 files are evidence only. Existing source names/assets were read as code references; no art inspection/design credit or assets changed.',
 ],
 'native_gaps':[
  {'missing':'Native Minecraft1.21 LivingEntity.aiStep matched call ordering, Entity frozen data replication, final freezing damage and render consumers; full actual ICE_RESISTANCE acquisition/expiry.', 'impact':'Freeze ownership remains incomplete0; no new fetch requested.'},
  {'missing':'GlitchCore dispatch/network internals and full thermoregulator/AreaFill/plugin modifier acquisition chains.', 'impact':'Heat producer, concrete state/attribute writes, packet receiver and HUD methods observed, but no universal environmental completeness, transport guarantee or runtime result.'},
 ],
 'static_examples_not_executed_tests':[
  {'case':'positive heat modifier','assumptions':'Heat70/threshold140, getOnPos block non-air, speed attribute exists.', 'derivation':'Remove old modifier; add +0.0075 ADD_VALUE. Calling this a speed penalty would contradict source.'},
  {'case':'freeze cap equality','assumptions':'One invocation of shown hook, icy/delay0/no resistance/noncreative/non-spectator, previous count required+2.', 'derivation':'Cap keeps same value; equality branch subtracts2. No assumption native aiStep invokes this only once.'},
  {'case':'disable retains runtime heat','assumptions':'Heat previously140 and speed modifier exists; enableTemperature becomes false while same player survives.', 'derivation':'TemperatureHandler returns before heat decrease or speed removal. Other external/native paths may intervene; this method alone is not full teardown.'},
 ],
 'application':'Record the actual final control write and independent state/render teardown. Configuration disable, immunity admission, positive movement modifiers and actual damage refusal must not be conflated. Research only; no Dynasty feature/UI additions.',
 'counting':{'formal_baseline_observed':len(rows),'current_credit':0,'whole_family_maximum':0,'helpers_variants_packets_migration_credit':0},
 'next_work':['Continue029 from another fixed local source after nearest complete decisions; do not retry026 nativeParticleCrit or count this freeze wrapper.', 'If exact native1.21 source and genuinely distinct whole policy become available later, review separately;028 remains0 without acceptance.'],
}
with (H/'immune-reference-batch-028.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(refs),'lines':sum(x['lines'][1] for x in refs),'comparisons':len(comp),'credit':0,'baseline':len(rows)}))
