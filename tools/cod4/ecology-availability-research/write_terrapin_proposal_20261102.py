"""Save the coordinator's actual Terrapin reading, without granting credit.

One-shot, immutable evidence writer. Source hashes verify the stated reading;
they are not additional semantic research and this does not alter a ledger.
"""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/cod4/audit-20261022/ecology-availability-research"
LEGACY = ROOT / "tools/cod4/legacy-migration-acceptance/.work/sources"
MOD = LEGACY / "AlexModGuy__AlexsMobs"
PIN = ROOT / "tools/cod4/ecology-availability-research/sources/AlexModGuy__AlexsMobs"
NATIVE = LEGACY / "minecraft-forge-1.20.1-47.4.10"
JAVA = "src/main/java/com/github/alexthe666/alexsmobs/"
COMMIT = "09755dade2cfbdf14839e026d3af446f9d3ff843"
OUT = AUDIT / "coordinator-terrapin-parent-payload-proposal-20261102.json"
OLD = json.loads((AUDIT / "coordinator-skreecher-alarm-latch-proposal-20261102.json").read_text())
ARTIFACT = OLD["native_artifact"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


assert not OUT.exists(), "Immutable proposal already exists; do not rewrite"
meta_bytes, tree_bytes = (PIN / "source.json").read_bytes(), (PIN / "tree.json").read_bytes()
assert sha(meta_bytes) == "503e8b933d51581f2949312697f14f503a3af77ba1b92589f443f6dfd7196084"
assert sha(tree_bytes) == "8e36c9680713d8ff86cab4cdb9c2c404089532dadeca22b2aaa7cc0d6102e8c3"
assert json.loads(meta_bytes)["sha"] == COMMIT
tree = json.loads(tree_bytes)
assert not tree["truncated"]
blobs = {x["path"]: x["sha"] for x in tree["tree"] if x["type"] == "blob"}
archive = Path(ARTIFACT["source_archive"])
assert sha(archive.read_bytes()) == ARTIFACT["sha"]
ranges = []


def add(path, source_path, bounds, role, native=False, reused=False):
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    if native:
        with zipfile.ZipFile(archive) as z:
            assert z.read(source_path) == data, source_path
    else:
        assert blobs[source_path] == blob(data), source_path
        for other in (MOD / source_path, PIN / source_path):
            if other.exists():
                assert other.read_bytes() == data, str(other)
    for start, end in bounds:
        assert 1 <= start <= end <= len(lines), (source_path, start, end, len(lines))
        row = {
            "path": relative(path), "source_path": source_path,
            "lines": [start, end], "file_sha256": sha(data),
            "excerpt_sha256": sha(b"".join(lines[start - 1:end])),
            "role": role, "support_credit": 0, "actually_read": True,
            "reading_reused_at_identical_bytes_from_earlier_same_turn": reused,
            "source_kind": "native_forge_archive" if native else "fixed_mod_git",
        }
        if native:
            row.update(source_archive_sha256=ARTIFACT["sha"], archive_entry_exact=True)
        else:
            row.update(repo="AlexModGuy/AlexsMobs", commit=COMMIT,
                       git_blob_sha1=blobs[source_path],
                       url=f"https://github.com/AlexModGuy/AlexsMobs/blob/{COMMIT}/{source_path}#L{start}-L{end}")
        ranges.append(row)


def mod(name, bounds, role, reused=False):
    p = JAVA + name
    local = PIN / p if (PIN / p).exists() else MOD / p
    add(local, p, bounds, role, reused=reused)


def native(name, bounds, role, reused=False):
    add(NATIVE / name, name, bounds, role, native=True, reused=reused)


mod("entity/EntityTerrapin.java", [(1, 675)], "Complete entity: goals, pregnancy, parent capture, phenotype, NBT/bucket and persistence methods")
mod("block/BlockTerrapinEgg.java", [(1, 242)], "Complete egg block: habitat/random incubation, stacking, silk transfer, removal and hatch sink")
mod("tileentity/TileEntityTerrapinEgg.java", [(1, 117)], "Complete parent payload, serialization, application and canMerge implementation; no canMerge caller inferred")
mod("entity/ai/AnimalAILeaveWater.java", [(1, 80)], "Complete selected leave-water goal and bounded random target search")
mod("entity/util/TerrapinTypes.java", [(1, 56)], "Complete enum, variant weights and phenotype palettes; variants/colors are zero separate credit")
mod("tileentity/AMTileEntityRegistry.java", [(1, 29)], "Complete egg block-entity registration binding")
mod("item/AMBlockItem.java", [(1, 79)], "Complete item subclass: no Terrapin placement/NBT override; Triops-only special useOn is separate")
mod("item/ItemModFishBucket.java", [(1, 98)], "Complete fish bucket spawn/restore dispatch and extra-attribute methods; no successful spawn assumed")
mod("entity/AMEntityRegistry.java", [(118, 118), (220, 220), (313, 313)], "Actually read Terrapin type/placement/attribute declarations only; not entire registry")
mod("block/AMBlockRegistry.java", [(37, 37), (67, 75)], "Egg registration declaration and complete registerBlockAndItem helper")
mod("item/AMItemRegistry.java", [(170, 170), (284, 284), (397, 397)], "Bucket/spawn-egg/dispenser declarations only; dispenser implementation not expanded")
mod("misc/AMTagRegistry.java", [(166, 166), (206, 206), (239, 245)], "Exact breedable/habitat declarations and complete item/block tag-key helpers")
mod("AlexsMobs.java", [(75, 114)], "Complete constructor already actually read for Triops/Skreecher at same bytes, reused registration context only", reused=True)
for source_path in [
    "src/main/resources/data/alexsmobs/tags/blocks/crocodile_spawns.json",
    "src/main/resources/data/alexsmobs/tags/items/terrapin_breedables.json",
]:
    p = ROOT / "tools/cod4/ecology-availability-research/.work/terrapin-20261102" / source_path
    add(p, source_path, [(1, len(p.read_bytes().splitlines()))], "Complete tiny fixed-commit resource actually read; nested habitat tag and runtime loaded tags not expanded")

native("net/minecraft/world/entity/ai/goal/BreedGoal.java", [(1, 80)], "Complete native pair admission/continuation/tick; overridden breed method is not native child spawning")
native("net/minecraft/world/entity/ai/goal/MoveToBlockGoal.java", [(1, 123)], "Complete native target search, restriction, path request, distance gate and retry bookkeeping")
native("net/minecraft/world/entity/animal/Bucketable.java", [(1, 110)], "Complete native bucket pickup and default save/load helpers")
native("net/minecraft/world/entity/animal/Animal.java", [(127, 205)], "Complete food mobInteract, usePlayerItem, love state and compatibility methods only")
native("net/minecraft/world/level/Level.java", [(195, 269), (274, 277), (556, 562)], "Complete setBlock overloads/markAndNotifyBlock/removeBlock/getBlockEntity; external callbacks not expanded")
native("net/minecraft/world/level/chunk/LevelChunk.java", [(213, 278), (286, 294), (297, 323), (340, 342), (394, 409)], "Complete setBlockState/create/get/remove block-entity and loaded-state methods; pending promotion/external callbacks not expanded")
native("net/minecraft/world/level/block/state/BlockBehaviour.java", [(163, 168), (753, 755)], "Complete default onRemove and BlockStateBase dispatch only")
native("net/minecraft/world/item/BlockItem.java", [(45, 96), (113, 115), (162, 192), (236, 248)], "Complete useOn/place, NBT wrapper, placement write, custom BE merge and BE-tag get/set methods")
native("net/minecraft/world/entity/EntityType.java", [(349, 383), (387, 440), (442, 455), (524, 526)], "Complete stack-config/spawn/create/offset/custom-entity-tag paths used by fish bucket; inner collision/factory implementations not expanded")
native("net/minecraft/world/level/ServerLevelAccessor.java", [(1, 12)], "Complete default passenger spawn dispatcher ignores per-entity boolean results")
native("net/minecraft/server/level/ServerLevel.java", [(814, 840), (842, 867), (869, 875)], "Complete shown add wrappers/player helper/addEntity/tryAdd helper; entityManager internal/event sink not expanded")
native("net/minecraft/world/entity/Mob.java", [(699, 740), (1077, 1079), (1105, 1107)], "Actual earlier same-turn native despawn and persistence accessors reused at same bytes; not all removal causes", reused=True)

def reference(name):
    p = AUDIT / name
    return {"path": relative(p), "sha256": sha(p.read_bytes())}


doc = {
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "status": "ACTUAL_COMPLETE_LOCAL_CHAIN_READ_PENDING_INDEPENDENT_DEDUP_REVIEW_ZERO_CREDIT",
    "author_thread_id": "01a16364-cac0-7ca2-a042-a5312781ca34",
    "draft_association": "EA-0015 mentioned in unexecuted build_tenth.py only; not a formal accepted item or candidate id",
    "new_accepted_identifier_assigned": False,
    "semantic_key": "phenotypic-parent-payload-across-pregnancy-egg-block-stack-silk-and-bucket-boundaries",
    "proposed_maximum_credit": 1, "accepted_credit": 0,
    "source_commit": COMMIT, "source_metadata_sha256": sha(meta_bytes),
    "source_tree_sha256": sha(tree_bytes), "actual_read_ranges": ranges,
    "native_artifact": ARTIFACT,
    "observations": [
        "Native BreedGoal admission needs own love and a compatible same-class partner; continuation is partner alive/inLove and loveTime<60, and the distance/adjustedTickDelay gate calls overridden breed. Terrapin breed records partner phenotype in ordinary partnerData memory, marks only this parent HasEgg, resets both love, ages both6000, and awards stats/XP. It does not create a child at mating; scheduled evaluations are not guaranteed world-tick counts.",
        "Own additional NBT and bucket TerrapinData preserve phenotype and HasEgg, but do not serialize partnerData. A reconstructed pregnant carrier can therefore use its own phenotype for both egg parents at lay time. Parent payload contains phenotype, not parent UUID/ownership. No general rollback/transaction or per-egg genealogical identity is implemented in the read chain.",
        "Actual resource declares minecraft:seagrass as breedable. Own food interaction marks persistence before native Animal logic; native adult server age0/not-in-love consumes actual food unless instabuild and sets love600. Bucketable.bucketMobPickup(...).orElse(super.mobInteract(...)) evaluates the superclass interaction eagerly even when the Optional is nonempty. This is Java call ordering, not a reproduced duplicate-consumption bug; the parent reads the then-current hand stack.",
        "HasEgg drives leaving water. The complete leave-water goal makes at most8 local random dry-target samples after its admission gate; a requested navigation path does not prove arrival. LayEgg uses native MoveToBlock target search/restriction/distance bookkeeping and an empty position above SAND or CROCODILE_SPAWNS. The direct SAND branch is known; nested #alexsmobs:am_spawns contents and loaded tags are not read/proven. No dig-delay is implemented in the complete egg-laying body.",
        "Lay placement uses random.nextInt(1)+3, exactly3 requested eggs. Sound/game event precede setBlock, whose boolean is ignored. It then assigns the egg BE's two parent fields if a BE is obtainable; parent2 falls back to parent1 when partnerData is null. Those direct assignments do not call setChanged in this shown path. HasEgg is cleared and love set600 regardless of successful placement/BE assignment. Save completeness or parent retention is not guaranteed.",
        "Random incubation checks habitat and either timeOfDay in (0.65,0.69) or a1/15 draw, advancing HATCH until the hatch branch. That branch requests removeBlock before attempting EGGS child creations; creation is not null-guarded, addFreshEntity result is ignored, and there is no finalizeSpawn/checkSpawnRules call at this sink. Egg disappearance, requested count and sounds cannot prove actual offspring.",
        "The egg's onRemove delegates to the default only when old EGGS<=1. The read Forge server LevelChunk path calls old-state onRemove and has no separate unconditional BE removal for a replacement without BE; its client path differs. Native getBlockEntity can return an unremoved stored BE without rechecking the current block state. Thus for EGGS>1 the shown server path can retain the old BE for the post-removal parent lookup. This is conditional on no reentrant/external removal or other failure, not proof all hatch paths retain data. For EGGS<=1 default removal and loaded-state conditions matter. Do not claim all hatch parents are lost or all are durable.",
        "Egg BE parent application runs only when both parents exist. It selects parent type/shell/skin, averages packed color integers (not per-channel RGB), and may mutate the overlay. The nextInt(2) mutation switch can select only0/1, not case2. Seven enum variants, colors, child loop entries and mutations are parts of one algorithm, never separate semantic credit. canMerge has an implementation but no caller is shown in the complete placement chain.",
        "Egg stacking increments a shared block-state count, not a per-egg parent list. Registration uses ordinary AMBlockItem, whose complete class has no Terrapin NBT-placement override. Native BlockItem after successful placement merges BlockEntityTag into the existing BE snapshot then load/setChanged if different, with its permission checks; this is a shared-payload boundary, not evidence two phenotype pairs can be merged safely. CompoundTag/ItemStack storage internals and actual cross-stack behavior are not expanded/reproduced.",
        "Silk drops require the shown enchantment and egg BE, returning one egg item irrespective of EGGS, with Parent1/Parent2 compounds when either exists. A missing parent's empty compound is still loaded through ParentData defaults rather than preserved as absent. Non-silk returns an empty list in this override. Actual break callback order, drops, inventory/payment, silk availability and world save/reopen remain unverified.",
        "Hatched child gets age-24000, optional BE phenotype, FromBucket=true and a fixed per-index position offset before unchecked add. The reused native Mob despawn/accessor read supports only the shown persistence/distance/event guards; FromBucket is not immunity to every removal reason. The hatch code creates new entities, not preservation of parent/egg identity or a strict kill event.",
        "Complete ItemModFishBucket calls EntityType.spawn first, then restores Bucketable NBT and FromBucket when the returned entity implements Bucketable. The expanded native spawn finalizes/configures a created mob, calls the void addFreshEntityWithPassengers dispatcher and returns the entity without propagating per-add success. A nonnull return can still fail actual admission. The subsequent bucket load occurs after that add attempt; no successful world admission, complete event ordering or exact-once delivery is inferred.",
        "Terrapin is registered WATER_AMBIENT, with native water placement and a separate normal-spawn random phenotype initializer. Bucket/reproduction/hatch are different initiation paths. Category names, local searches, phenotype reads and propagation attempts are not natural ecology opportunities or a remedy for Dynasty's observed closed CREATURE cap. No loaded biome/mod compatibility/runtime or shared production change is made.",
    ],
    "semantic_comparisons": [
        {"id": "EA-0017", "decision": reference("batch-011.json"),
         "actual_read_scope": "EA17 full chain read/authored earlier this same turn; observation/application reread now, source byte binding reused, not a new full reread of all limits",
         "comparison": "Both are fed-pair pregnancy to habitat egg offspring and that common skeleton cannot earn credit twice. The only proposed distinct unit is the complete two-parent phenotype payload ownership/serialization/stack/silk/bucket handoff with failure boundaries, absent from EA17's asymmetric reservation and scheduled water-surface egg. Reviewer may reject as insufficient semantic difference; species/colors alone are explicitly zero."},
        {"id": "EA-0013", "decision": reference("batch-008.json"),
         "actual_read_scope": "Full observation/application fields reread, earlier accepted limits remain authoritative; no complete new reread claimed",
         "comparison": "EA13 seed/food plateau adult replacement has no paired phenotype payload crossing entity, BE, item and bucket representations. Generic growth/new-child attempts are shared support, not extra credit."},
        {"id": "EA-0014", "decision": reference("batch-009.json"),
         "actual_read_scope": "Full observation/application fields reread, earlier complete chain reading reused; no complete new reread of all source ranges claimed",
         "comparison": "EA14 delayed parasitic effect/host retention is not paired phenotype handoff. Its discard/expiry and unchecked offspring lesson is reused support, not new credit."},
    ],
    "application": [
        "For later Dynasty quest/ecology design keep mating, carried pregnancy, successful egg placement, actual BE parent payload, item/bucket transfer and actual admitted child as distinct receipts. Never award a reproduction quest from hearts, sound, a cleared HasEgg flag, a nonnull spawn return or a vanished egg.",
        "Review a single stable parent-payload ownership model and its merge/reload/failure behavior before implementing it. Do not copy this upstream code/assets; no spawning, cap/category/probability or production breeding changes below1000 accepted relevant mechanisms.",
    ],
    "limitations": [
        "Zero formal research credit until an independent complete-source and semantic-dedup review and the appropriate strict aggregation receipt; original unexecuted draft does not assign acceptance or a candidate id.",
        "Actual reading ranges, files, palette entries, resources, hashes, supporting native helpers and acquisition are not separate implementations. At most one whole mechanism is proposed, potentially zero if duplicate.",
        "No runtime, source mod execution, native reproduction/offspring UUID, real drop/pickup/payment, loaded-tag, save/reopen or current-pack acceptance. Original Dynasty ecology24/30 births+9/10 same-UUID pickup and all failed native assertions remain unchanged.",
        "Native GoalSelector scheduling, navigation/collision internals, entityManager/event bus internals, full NBT merge/storage, all parent/packet/engine lifecycle paths, block break callbacks, nested habitat resource, dispenser implementation, Client rendering/model/texture and all external modifications are not expanded. Path requests and source arithmetic are not observed gameplay.",
        "Reentrant callbacks or cancellation can change post-remove/post-place conditions; shown source ordering is conditional. No atomicity, complete safety, guaranteed parent transfer, exact child count or universal persistence is established.",
        "Hashes and metadata verification bind the actual earlier and current reading, not a new reread of every existing accepted source or a production repair approval.",
    ],
    "network_requests": {"current_terrapin_reading": 2, "bounded_once_each": True, "automatic_retry": False,
                         "acquisition": relative(ROOT / "tools/cod4/ecology-availability-research/.work/terrapin-20261102/acquisition.json")},
    "game_starts": 0, "production_changes": 0, "checklist_deletions": 0,
    "duration_hours_claimed": 0,
}
with OUT.open("x") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(json.dumps({"path": relative(OUT), "sha256": sha(OUT.read_bytes()),
                  "ranges": len(ranges), "files": len({x['path'] for x in ranges}),
                  "native_ranges": sum(x['source_kind'] == 'native_forge_archive' for x in ranges),
                  "accepted_credit": 0, "ledger_changes": 0}, ensure_ascii=False))
