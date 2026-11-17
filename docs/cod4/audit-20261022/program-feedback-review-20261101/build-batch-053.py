"""Fixed-local attunement protection/camera/settlement lifecycle; pending0/max1."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_text())
p50=H/'immune-reference-batch-050.json';p51=H/'immune-reference-batch-051.json';p52=H/'immune-reference-batch-052.json'
d50=load(p50);d51=load(p51)
assert ref(p50)['sha256']=='59958fbe55e28774eee1642642401e7da4539601b103d37b8bafa8450051ef6e'
assert ref(p51)['sha256']=='176f6f8226778744ed87ea66d0d5a0c42a5000e0063454985401f5a86b0c48c7'
assert ref(p52)['sha256']=='e34aab50309ff2dd5513a83552446023f7c4d4f9d620dcdc614f8ea1cb3ba0f8'
v=d50['provenances'][0];mr=(R/v['manifest_path']).read_bytes();assert sha(mr)==v['manifest_sha256']
m=next(x for x in json.loads(mr) if x['repo']==v['repo']);es={x['path']:x for x in m['files']}
prefix='src/main/java/hellfirepvp/astralsorcery/'
refs=[]
def source(n,a=1,z=None):
 e=es[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines();z=z or len(lines)
 assert 1<=a<=z<=len(lines) and sha(b)==e['sourceSha256']
 refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
  'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],
  'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),'reading_context':'actual_read053'})
full=[
 'common/event/helper/EventHelperInvulnerability.java',
 'common/crafting/nojson/attunement/active/ActivePlayerAttunementRecipe.java',
 'common/crafting/nojson/attunement/AttunePlayerRecipe.java',
 'common/crafting/nojson/attunement/AttunementRecipe.java',
 'common/crafting/nojson/CustomRecipe.java','common/crafting/nojson/CustomRecipeRegistry.java',
 'common/crafting/nojson/AttunementCraftingRegistry.java','common/registry/RegistryRecipeTypes.java',
 'common/network/play/client/PktAttunePlayerConstellation.java',
 'common/tile/TileAttunementAltar.java','common/tile/base/TileEntityTick.java','common/tile/base/TileEntitySynchronized.java',
 'client/util/camera/ClientCameraManager.java','client/util/camera/path/CameraPathBuilder.java',
 'client/util/camera/path/CameraPath.java','client/util/camera/CameraTransformerPlayerFocus.java',
 'client/util/camera/CameraTransformerSettingsCache.java','client/util/camera/ClientCameraUtil.java',
 'client/util/camera/EntityClientReplacement.java','client/util/camera/EntityCameraRenderView.java',
 'client/util/camera/CameraEventHelper.java','client/util/camera/ICameraTransformer.java',
 'client/util/camera/ICameraPersistencyFunction.java','client/util/camera/ICameraTickListener.java',
 'client/util/camera/ICameraStopListener.java','client/util/sound/FadeSound.java',
 'common/data/research/ProgressionTier.java','common/block/tile/BlockAttunementAltar.java']
for n in full:source(n)
for n,a,z in [
 ('common/data/research/ResearchManager.java',190,212),
 ('common/data/research/PlayerProgress.java',224,263),('common/data/research/PlayerProgress.java',309,315),
 ('common/util/entity/EntityUtils.java',290,304),
 ('common/util/MiscUtils.java',69,81),('common/util/MiscUtils.java',645,677),
 ('common/util/data/ByteBufUtils.java',152,192),('common/util/data/ByteBufUtils.java',233,244),
 ('common/util/sound/SoundHelper.java',83,93),
 ('common/registry/RegistryBlocks.java',102,102),('common/registry/RegistryTileEntities.java',41,41),
 ('common/registry/RegistryTileEntities.java',83,98),
 ('common/registry/internal/PrimerEventHandler.java',133,147)]:source(n,a,z)
reuse={'common/constellation/world/DayTimeHelper.java','common/data/research/ResearchHelper.java',
 'common/data/research/ResearchManager.java','common/event/handler/EventHandlerCache.java',
 'AstralSorcery.java','common/CommonProxy.java','client/ClientProxy.java',
 'common/registry/internal/PrimerEventHandler.java','common/registry/internal/InternalRegistryPrimer.java',
 'common/network/PacketChannel.java','common/network/base/ASPacket.java',
 'common/network/channel/SimpleSendChannel.java','common/network/channel/BufferedReplyChannel.java'}
for x in d50['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if x['repo']=='HellFirePvP/ObserverLib' or n in reuse:
  if n=='common/registry/internal/PrimerEventHandler.java' and x['lines']==[195,197]:continue
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  refs.append(dict(x,reading_context='exact050_bootstrap_transport_research_boundary_support_reused0'))
for x in d51['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if n in {'common/util/tick/TimeoutList.java','common/util/NameUtil.java'} or (n=='common/util/MiscUtils.java' and x['lines']==[219,228]):
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  refs.append(dict(x,reading_context='exact051_timeout_and_registration_support_reused0'))

ledger=A/'immune-feedback-research/reviewed.json';lb=ledger.read_bytes();rows=json.loads(lb);idx={r['id']:r for r in rows}
policy='astralsorcery-native-attunement-split-membership-protection-and-camera-completion-with-asymmetric-exit'
assert policy not in {x['semantic_dedup_key'] for x in rows}
dist={
 'astralsorcery-native-vortex-renews-object-timeout-with-dimension-id-freeze-membership-and-change-only-server-receipts':
 'Same TimeoutList helper is not novelty. Vortex refreshes one timeout and separate dimension/intID control membership; attunement appends independent player entries and unconditionally clears native invulnerable on each expiry while membership can still veto hurt/target. Protection admission/settlement is coupled to an altar and independent client camera lifetime. Only entire ownership and asymmetric exits are proposed, never add versus setOrAdd by itself.',
 'relics-native-use-bound-rewind-incoming-immunity-and-dimension-exit':
 'Relics reads current actual use stack/ability at damage and releases by stopUsingItem. Attunement retains server player-object membership outside recipe/camera lifetime; repeated entries and native flag restoration diverge. Client camera completion can request authoritative settlement but server duration also finishes independently. Not a second travel animation or duration constant.',
 'alexscaves-native-quorum-ritual-windup-versus-victim-owned-committed-capture-lifecycle':
 'AlexsCaves separates NPC quorum windup from armed victim conversion timer. Attunement repeatedly grants protected membership while server recipe runs, and separately locks local camera with an alternate client-request completion route. No quorum/committed conversion owner; final progression setter result is ignored, and both protection residue and client teardown have independent exits. Ritual theme alone earns0.',
 'cat-scripted-animation-phase-invulnerability-family':
 'Cataclysm directly rejects damage from live scripted boss phase with bypass policy. Astral recipe absence does not immediately revoke membership, native invulnerability flag can disagree with event cancellation, and client presentation is independently driven. Not an additional numeric scripted phase.',
 'goety-vizier-native-intro-and-post-hit-window-final-refusal':
 'Vizier maintains actor intro/post-hit countdown and native hurt gate; attunement uses repeated external object-list grants and three independent consumers (native flag, hurt, targeting), plus client completion/restore. Intro effects/particles and timer length are support0.',
 'playerrevive-native-helper-membership-pauses-terminal-bleed-clock-and-integrates-authoritative-release-with-asymmetric-helper-feedback-exit':
 'PlayerRevive is sampled helper membership integrating recovery while pausing terminal bleed. Attunement has no helper count or competing terminal clock: closest-candidate eligibility admits a server recipe and repeated protection entries, while server age or authenticated client finish may end it. Shared principle of asymmetric feedback exits alone is not new credit.'}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
cmps=[{'accepted_id':k,'complete_semantic_decision_read':{f:idx[k][f] for f in fields},'distinction':v} for k,v in dist.items()]
mig=d50['migration_overlap_screen'];mb=(R/mig['path']).read_bytes();mi={r['candidate_id']:r for r in map(json.loads,mb.decode().splitlines())}
mc=[]
for c in mig['comparisons']:
 assert all(mi[c['accepted_id']][k]==v for k,v in c['complete_semantic_decision_read'].items())
 mc.append({'accepted_id':c['accepted_id'],'complete_semantic_decision_read':c['complete_semantic_decision_read'],
 'distinction':'Existing player-research UUID persistence/allocation/clone owner retained. Attuned progression setter and prior source-dispatch support close the final API boundary here; no second progression/migration credit or deeper disk reliability claim. Candidate is transient protected ceremony/control and its three independent exits.'})
progress_path=A/'immune-feedback-research/progress.json';progress=load(progress_path);assert len(rows)==progress['reviewed_effective_semantic_dedup']
observations=[
 'Concrete registration: RegistryRecipeTypes.init calls AttunementCraftingRegistry.init from prior primer startup, registering AttunePlayerRecipe plus crystal recipe in a HashMap. Altar first matching values iteration has no sorted priority guarantee. Registered BlockAttunementAltar creates actual TileAttunementAltar, and tile registry builds its reflected factory. CommonProxy registers invulnerability listeners and SERVER timeout; ClientProxy registers camera manager with Observer tick and camera render listener. Native block placement/Observer structure engine/runtime registry success unexecuted; no building design credit.',
 'Admission requires cached sky visibility and observed multiblock, active constellation search and night. Altar sky checks are cached up to20ticks; constellation scan every20. Recipe requires IMajor active constellation and chooses closest ServerPlayer in unit box at altar.up grown1 BEFORE eligibility, so an ineligible closest player prevents trying another candidate. Eligibility is alive/nonfake/nonsneaking, valid progress, unattuned, tier>=ATTUNEMENT and discovered current constellation. Fake helper rejects Forge FakePlayer/unapproved subclass/missing connection/address errors; external Mods class lookup unexpanded. No ingredient/payment exists in this player recipe.',
 'createRecipe repeats closest lookup, captures that player UUID and current major constellation; start positions that player at altar offset twice. Active.matches first reruns recipe.canStartCrafting (some closest eligible player), then separately requires captured UUID player present/alive in altar world; it does not require these two player identities equal or captured constellation equal current altar constellation. Server tick calls active.tick (grant then increments age) BEFORE matches, so an invalidated current recipe can grant one last pass. Sky/multiblock early failure instead nulls recipe before grant; neither invalidation branch calls stopCrafting. stopCrafting itself is empty for this recipe.',
 'Every server doTick with captured player present invokes EventHelperInvulnerability.makeInvulnerable: unconditionally setInvulnerable(true), append a new timeout10 entry containing PlayerEntity object. TimeoutList.add does not deduplicate or renew. contains compares value.equals across entries. A repeated grant is not a source-owned lease/refcount or one refreshed deadline. No snapshot of prior invulnerable flag is saved; no UUID/dimension/generation metadata is stored in this helper. Only this active-player recipe is a native producer in the fixed Java call-site scan.',
 'Three effective protection paths differ. Native invulnerable flag is set at grant; LOW LivingHurt cancels any player with list membership without local amount/source/bypass/side predicate; LivingSetAttackTarget requires live player target and membership, then clears revenge target and Mob attack target. It changes targeting, not every AI memory or all direct control. No success-specific packet, gray text, sound or result is produced by these hooks; exact Forge/native damage/target recursion and other listeners remain external.',
 'SERVER END timeout decrements each entry and unconditionally calls player.setInvulnerable(false) before removing each expired entry. It does not inspect remaining entries. Thus older expiries can clear native flag while newer membership still cancels Hurt/target assignment; relative tile/END order is not a runtime guarantee. Stopping recipe stops new grants but existing entries retain residue until their remaining dispatched ticks expire. Ordinary recipe completion/stopEffects does not immediately clear list or flag. Never infer complete invulnerability from camera presence or from one of these states alone.',
 'Logout removes ALL equal player entries through removeIf without the expiry delegate, so this handler does not restore/clear the native flag. Server cache cleanup invokes clearServer, whose TimeoutList.clear calls delegate for every remaining entry then clears. No prior-flag restoration in either path, and duplicate clears are possible. Clone/dimension transfer/object replacement/native entity destruction are not modeled here: list keys are retained player objects, not UUIDs, and no survival across real process restart is claimed.',
 'Authoritative default finish: Active age>=800 after server tick and matches permits Tile.finishActiveRecipe. It invokes recipe.finishRecipe then empty stopCrafting, nulls currentRecipe, marks block update and submits two ambient flares. finishRecipe calls ResearchManager.setAttunedConstellation using CAPTURED constellation. Setter rejects invalid progress/undiscovered constellation, otherwise removes allocated perks, zeroes experience, sets attuned state, optionally applies root, requests advancement, progress sync and save; it returns bool. Active ignores that bool, so tile teardown/flares are not proof progression settled. Existing migration owner owns persistence/research; this is API-boundary support0 and no transaction/disk success claim.',
 'Tile synchronization uses writeNetNBT for current constellation and recipe key/tick/playerUUID/captured constellation; getUpdatePacket includes it. Chunk write and getUpdateTag omit writeNetNBT, so this class does not persist active ceremony or include it in normal initial tag. readNetNBT replaces same recipe instance via deserialize while reusing previous cameraHack only; startedPlayerSound resets with new instance. Invalid/missing recipe calls previous stopEffects then nulls. External native update delivery, chunk bootstrap and rendering are unexecuted; no continuous timer sync or resume-across-save guarantee.',
 'Local camera starts only for matching UUID. Builder creates400 path points*2ticks and player-focus transformer, placed in priority-only TreeSet; equal priority can reject another transformer without a result checked by caller. Render START chooses highest, starts/stops on changes, renders and removes expired; CLIENT START while unpaused advances camera age. CameraPath expires when ticksExisted>total800, unlike server recipe>=800. No shared authoritative clock. Tick delegate locks REPLACEMENT position/orientation, hides its custom name and zeroes velocity; rendering helper also writes actual local player pose/position to camera location. EntityCameraRenderView ignores rotation input; no full server control/input-ban assertion.',
 'Camera settings snapshot GUI/view-bobbing/viewpoint/flying and start pose, sets GUI hidden/third-person/flying during rendering. PlayerFocus creates a local replacement from player NBT; stop restores cached settings/pose first, then overwrites actual local pose with replacement final pose, removes replacement, resets render camera and may close current screen, and invokes path stop delegate if world nonnull. Thus return is not simply original pose. These are source reads only: no actual UI/focus/sound/brightness/game action performed.',
 'Normal camera stop delegate sends PktAttunePlayerConstellation only if cameraHack exists, persistency expired and !forciblyStopped. Payload contains submitted constellation registry entry, world key and altar position. Server enqueue requires nonnull submitted cst, existing world, loaded correctly typed altar, active player recipe, sender UUID equal captured UUID, and sender currently eligible against ALTAR CURRENT constellation. It does not compare submitted cst with current/captured constellation, require sender same world/distance, check recipe age or rerun sky/multiblock/matches. Submitted cst is only nonnull gate; actual reward uses captured cst. finishActiveRecipe then clears current object, so ordinary subsequent queued request finds none; no per-generation nonce means stale request for a new same-player recipe is not excluded. These are static trust-boundary differences, not exercised exploit or proof of accessible crafted packet.',
 'Presentation stop is asymmetric: stopEffects only removes transformer from set, without forceStop or immediate onStop. Next render may clean lastTransformer. On normal expiry manager calls onStop but leaves lastTransformer set; next no-active render can call onStop again. Base settings active flag guards only its own restoration; PlayerFocus cleanup/path callback has no equivalent once guard. removeAllAndCleanup stops active and clears set but retains lastTransformer; reused EventHandlerCache invokes it on client disconnect. Nullable player/replacement preconditions and native render/disconnect order mean no universal crash, exactly-once completion request or immediate restoration guarantee. No native forceStop caller found in this fixed camera/event scope; unrelated external callers not ruled out.',
 'Sound/particles are ceremony state feedback, not protection or reward ACK. Active recipe starts FadeSound on client regardless whether local UUID owns camera; stop predicate checks altar active-effects or currentRecipe identity. Deserialize preserves camera but creates new recipe, so old sound predicate can retire while new instance starts another. FadeSound updates hasStoppedPlaying in isDonePlaying predicate check, accumulates stopTick in tick and ends only stopTick>fadeOut80; engine calling order/output unverified. Numerous particle submissions follow local age/constellation, independent of actual Hurt cancellation and ResearchManager result. Native audio/particle engine/render assets remain boundary0.',
 'Six complete nearest saved semantic decisions and existing Astral migration owner read. Vortex shares timer helper but refreshes one entry with separate dimension membership; this policy has append-only overlapping grants/native flag disagreement, independent client presentation with alternate completion authority, and different logout/normal/world exits. Relics use-bound rewind and scripted intro immunity also compared. Pending051 paid death-token and052 one-use fall-source ownership are separate exact overlap checks; neither helper/packet/constant nor each failure branch earns credit. One complete protected-ceremony lifecycle max1 pending0; coordinator may merge/hold.'
]
doc={'schema_version':1,'owner':'program-feedback-review-053','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_PROTECTED_CEREMONY_SPLIT_EXIT_POLICY_PENDING_INDEPENDENT_REVIEW',
 'research_credit':0,'maximum_proposed_credit':1,'repo':m['repo'],'commit':m['commit'],'semantic_dedup_key':policy,
 'provenances':d50['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':[ref(p50),ref(p51),ref(p52)],'scope':'28 whole files newly cited053, selected complete helpers/methods and bounded declarations. Full ActivePlayerAttunementRecipe421 now read in two bounded outputs, closing excluded partial052 exploration. TimeoutList202 reread, retained exact prior binding0. Prior bootstrap/transport/research-boundary/Observer support reused0, no old verifier rerun.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),'comparisons':cmps,
 'scope':'Six full saved substantive judgments, not original source chains. Combined output clipped AlexsCaves observation/concrete fields; both recovered explicitly. Broad concept search is not full481-chain rereading.'},
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mb),'comparisons':mc},
 'existing_work_overlap':[
 {'evidence':ref(p50),'distinction':'Accepted paid dodge owns charge arithmetic/attribute membership/reconciliation.053 neither spends charge nor reuses a paid-dodge gate; transient ceremony protection not another chance/resource variant.'},
 {'evidence':ref(p51),'distinction':'051 prepaid death potion token and independent later consumption/cooldown.053 repeats external temporary player memberships and coordinates server recipe/client camera exit, not another death effect or retained charge.'},
 {'evidence':ref(p52),'distinction':'052 source-qualified coalesced one-use token consumed on matching hurt or grounded tick.053 overlapping timed entries cancel repeated hurt and clear targeting, with non-refcounted native flag and ceremony/camera completion. Source constant/time parameter alone not counted.'}],
 'excluded_index_screen':[{'evidence':ref(p),'status':load(p).get('status'),'scope':'Existing held/excluded index status only; no old full source reread'} for p in sorted(H.glob('*screen*.json'))],
 'whole_chain_observation':observations,
 'application':'原程序應分開保存服務端保護資格、原生旗標、客戶端控制與完成回執；退出要按各自所有者清理，不能靠演出完畢或特效存在判定拒控/結算成功。Boss免控反饋仍需最終拒控原因；不新增儀式玩法、普通體質灰字或鏡頭干預。僅研究。',
 'critical_boundaries':[
 'Fixed historical source, not installed Dynasty binary/config/runtime equivalence. Research only; no actual game, input, camera, rendering, sound, network or registry dispatch.',
 'Native Forge cancellation/target recursion/damage bypass, tile/END/render scheduling, cloned player object semantics and block update delivery unexpanded. No guaranteed immunity, full control suppression, exactly-once feedback, reproducible crash or exploit.',
 'Observer structure/sky/constellation engine, Mods subclass adapter, native packet registry decoding security and engine sound/render lifecycle unexpanded. Partial registry lines are declarations/calls only, not whole file reads.',
 'Progression setter is full mod-owned completion boundary; save/root-effect dispatch belongs existing migration ownership. Ignored returned bool prevents claiming reward success from teardown. No deeper disk transaction/recovery credit.',
 'Source declaration lookup and bounded original reads are evidence, not counts. Six whole decisions plus one migration owner; pending051/052 compared; max1 only after independent coordinator decision.',
 'No production/test/art/background/sharedJar/user-game/master ledger/session/checklist edits, no network/upstream code/Java/Gradle/game/display/audio action, no hours claim.'
 ],
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'runtime_credit':0},
 'next_work':'Finish new053 binding verification and immutable handoff; then bounded fixed-local source inventory for another whole original-program owner. No global Astral exhaustion claim and no duplicate timer/charge/camera variant credits.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered={}
for x in refs:
 a,z=x['lines'];new=set(range(a,z+1));old=covered.setdefault(x['path'],set());assert not old.intersection(new);old.update(new)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-053.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0,'maximum_pending':1}))
