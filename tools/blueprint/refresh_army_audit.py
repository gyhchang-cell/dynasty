#!/usr/bin/env python3
"""Extract the implemented army batch and preserve honest, run-owned QA evidence.

Generated reports only. This does not register content or certify visual quality.
"""
import argparse
import collections
import json
import re
from pathlib import Path
import catalog as audit

BASE = "src/main/java/com/dynasty/blueprint/"
KINDS = {
    "SPEAR": ("archer", ["THRUST", "BRACE"]),
    "CROSSBOW": ("rebel_soldier", ["VOLLEY", "ROLL"]),
    "SCOUT": ("assassin", ["CUT", "GRAPPLE", "KNEE"]),
    "POWDER": ("rebel_soldier", ["STAB", "DETONATE"]),
    "FLAG": ("royal_guard", ["SLAM"]),
}


def refresh(catalog, test_log, solo=None, network=None):
    read = lambda name: (audit.ROOT / (BASE + name)).read_text()
    entities, definitions, skills_source = map(read, ("BlueprintEntities.java", "TemplateContentDefinitions.java", "ArmySkills.java"))
    number = lambda s: float(s.strip().removesuffix("F"))
    registered = {row[1]: (row[0], row[2], number(row[3]), number(row[4])) for row in re.findall(
        r'(\w+) = mob\("([^"]+)", TemplateMob.Kind.(\w+), ([\d.F]+), ([\d.F]+)\)', entities) if row[2] in KINDS}
    stats = {row[0]: list(map(number, row[1].split(","))) for row in re.findall(
        r'event.put\((\w+).get\(\), attributes\(([^)]+)\)\)', entities)}
    rows = re.findall(r'new Spawn\("([^"]+)",Level.OVERWORLD,List.of\((.*?)\),List.of\((.*?)\),\s*'
        r'(-?\d+),(-?\d+),(\d+),(\d+),"([^"]+)","([^"]+)",(\d+),(\d+),(\d+),(\d+),"([^"]+)",\s*'
        r'"([^"]+)","([^"]+)"\)', definitions, re.S)
    rows = [row for row in rows if row[0] in registered]
    assert len(rows) == len(registered) == 5, "Army registration or location format changed"
    constants = dict(re.findall(r'(\w+)=(\d+)', skills_source))
    names = "windupTicks activeTicks recoveryTicks cooldownTicks minRange maxRange angleDegrees definitionDamageMultiplier definitionKnockback interruptible".split()
    skills = {}
    for constant, key, arguments in re.findall(r'skill\((\w+),"([^"]+)",([^)]*)\)', skills_source):
        values = arguments.split(",")
        assert len(values) > len(names)
        parsed = [v.strip() == "true" if v.strip() in ("true", "false") else number(v) for v in values[:len(names)]]
        record = dict(zip(names, parsed), id=int(constants[constant]), key=key,
            impactTicks=[int(v) for v in values[len(names):]], requiresSight=True, source=BASE + "ArmySkills.java")
        for name in names[:4]: record[name] = int(record[name])
        record["totalTicks"] = sum(record[n] for n in names[:3])
        skills[constant] = record
    assert len(skills) == 10, "Army action contract changed"
    tests = audit.game_test_evidence(test_log, ("dynasty", "dynasty_army", "dynasty_cod2"))
    runs = [audit.client_run_evidence(path, count, army=True) for path, count in ((solo, 1), (network, 2)) if path]
    hashes = [run["artifactIdentity"].get("productionSha256") for run in runs]
    if runs:
        assert all(hashes) and len(set(hashes)) == 1, "Army acceptance needs matching frozen solo/network resources"
    loot = {row["id"]: row for row in json.loads((audit.OUT / "template-loot-status.json").read_text())["templates"]}
    inventory = []
    for row in rows:
        identity = "dynasty:" + row[0]
        entry = next(e for e in catalog["entries"] if e["id"] == identity)
        constant, kind, width, height = registered[row[0]]
        atlas, actions = KINDS[kind]
        health, damage, speed, armor, resistance = stats[constant]
        if entry["definitionStatus"] != "ACTIVE_RUNTIME": entry["pendingWorldPlacement"] = entry["spawn"]
        entry.update(implementationStatus="PARTIAL", exactExistingId=identity, definitionStatus="ACTIVE_RUNTIME",
                     naturalSpawnActive=kind == "SCOUT", acquisitionActive=False)
        entry["attributes"].update(status="REGISTERED_BASE_ATTRIBUTES", MAX_HEALTH=health, ATTACK_DAMAGE=damage,
            MOVEMENT_SPEED=speed, ARMOR=armor, ARMOR_TOUGHNESS=0, FOLLOW_RANGE=28, KNOCKBACK_RESISTANCE=resistance,
            ATTACK_SPEED=1, ATTACK_KNOCKBACK=0, FLYING_SPEED=None, XP_REWARD=5,
            entityDimensions={"width":width,"height":height}, immunities={"fire":False,"water":False,"fall":False})
        resources = {"implementationClass":[audit.probe(BASE + name) for name in ("BlueprintEntities.java", "TemplateMob.java", "ArmyBehaviors.java")],
            "skillClasses":[audit.probe(BASE + name) for name in ("ArmySkills.java", "ArmyAuraEffect.java", "ArmyCaltrop.java", "TemplateProjectile.java", "combat/TimedAttack.java")],
            "renderer":[audit.probe(BASE + "client/" + name) for name in ("TemplateMobModel.java", "TemplateMobRenderer.java", "TemplateSecondaryMotion.java", "BlueprintVisuals.java")],
            "geo":[audit.probe(f"src/main/resources/assets/dynasty/geo/blueprint/{row[0]}.geo.json")],
            "animation":[audit.probe(f"src/main/resources/assets/dynasty/animations/blueprint/{row[0]}.animation.json")],
            "texture":[audit.probe(f"src/main/resources/assets/dynasty/textures/entity/{atlas}.png")],
            "loot":[audit.probe(f"src/main/resources/data/dynasty/loot_tables/entities/{row[0]}.json")],
            "spawn":[audit.probe(BASE + name) for name in ("TemplateContentDefinitions.java", "BlueprintSpawns.java", "BlueprintSpawnState.java")]}
        entry["resources"] = resources
        tags = lambda raw, category: [dict(audit.tagref(tag, category), status="ACTIVE_RUNTIME", activeForThisEntry=True)
            for tag in re.findall(r'tag\("([^"]+)"\)', raw)]
        pending = "PENDING" in row[13]
        spawn = dict(status="PENDING_BATTLEFIELD_ENCOUNTER" if pending else "ACTIVE_RUNTIME", dimension="minecraft:overworld",
            biomeTags=tags(row[1], "biome"), structureTags=tags(row[2], "structure"),
            heightRange={"min":int(row[3]),"max":int(row[4])}, lightRange=[int(row[5]),int(row[6])],
            timeWindow=row[7], weatherCondition=row[8], spawnWeight={"active":int(row[9]),"status":"DISABLED_PENDING_ENCOUNTER" if pending else "ACTIVE_RUNTIME"},
            minGroup=int(row[10]), maxGroup=int(row[11]), localCap=int(row[12]), spawnReason=row[13],
            specialCondition=row[14], despawnPolicy=row[15], worldEntryActive=not pending)
        if kind == "SCOUT":
            path = "src/main/resources/data/dynasty/forge/biome_modifier/blueprint_scout.json"
            modifier = json.loads((audit.ROOT / path).read_text())
            assert modifier["spawners"]["type"] == identity and modifier["spawners"]["weight"] == int(row[9])
            resources["spawn"].append(audit.probe(path))
            spawn.update(localCapScope="2 same-type loaded mobs within32; night; light0..7; solid standing space", biomeModifier=path)
        elif not pending:
            spawn.update(squadComposition={"ludun_jiashi":1,"liannu_zhenzu":2,"juma_changqiangbing":1},
                respawnRule="12000 ticks after membership empty; unload is not death; persistent UUID membership", localCapScope="PER_PERSISTENT_STRUCTURE_MARKER")
        entry["spawn"] = spawn
        entry["runtimeSkills"] = dict(timingUnit="SERVER_TICK_20_PER_SECOND", baseTimeline=[skills[action] for action in actions],
            source=BASE + "ArmyBehaviors.java", balanceStatus="BASELINE_GAMEPLAY_ACCEPTANCE_PENDING")
        entry["dropsReward"].update(status=loot[identity]["status"], implemented=loot[identity]["implemented"], pending=loot[identity]["pending"])
        entry["verification"] = dict(singlePlayer=runs[0]["status"] if solo else "PENDING", twoPlayer=runs[-1]["status"] if network else "PENDING",
            serverGameTests="PASS_LOGGED_REQUIRED_TESTS", evidence="docs/blueprint-cod1/army-verification.json",
            screenshots=[p["path"] for run in runs for p in run["screenshots"]], note="Harness pass is not full art, player-discovery, active-combat rejoin, server restart or balance acceptance. Optional idle rejoin/resource reload is recorded separately. No DONE claim.")
        entry["implementationEvidence"] = dict(kind=kind, texturePolicy="REUSE_UNMODIFIED_OWN_ATLAS_NATIVE_UV", remaining=[
            "Final visual quality, locomotion/narrow terrain and normal gameplay matrix", "Active-combat multiplayer rejoin/late tracking and server disk restart",
            *([] if runs and all(r.get("lifecycle",{}).get("status","").startswith("PASS") for r in runs)
              else ["Actual resource reload and idle multiplayer rejoin"]),
            "Original location/quest integration and pending decorative material use"] + (["Battlefield encounter source"] if pending else []))
        bones = json.loads((audit.ROOT / resources["geo"][0]["path"]).read_text())["minecraft:geometry"][0]["bones"]
        clips = json.loads((audit.ROOT / resources["animation"][0]["path"]).read_text())["animations"]
        inventory.append(dict(id=identity, bones=len(bones), cuboids=sum(len(b.get("cubes", [])) for b in bones), clips=len(clips)))
    return dict(status="PARTIAL", server=tests, clientRuns=runs, modelInventory=inventory,
        totals={key:sum(row[key] for row in inventory) for key in ("bones","cuboids","clips")},
        productionSha256=hashes[0] if hashes else None, qualityAcceptance="PENDING", allTasksComplete=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-log", type=Path, required=True)
    parser.add_argument("--solo", type=Path)
    parser.add_argument("--network", type=Path)
    parser.add_argument("--template-solo", type=Path)
    parser.add_argument("--template-network", type=Path)
    args = parser.parse_args()
    catalog = audit.make_catalog(audit.DEFAULT_SOURCE)
    first = audit.refresh_templates(catalog, args.server_log, args.template_solo, args.template_network,
                                   ("dynasty", "dynasty_army", "dynasty_cod2"))
    army = refresh(catalog, args.server_log, args.solo, args.network)
    validation = audit.validate(catalog, audit.DEFAULT_SOURCE)
    assert validation["valid"] and not validation["resourceEvidenceChanges"], validation
    for name, data in (("content-definitions",catalog),("template-verification",first),("army-verification",army),("catalog-validation",validation)):
        (audit.OUT / (name + ".json")).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    (audit.OUT / "world-placement.tsv").write_text(audit.world_tsv(catalog))
    print("Source-backed implementation counts:", dict(collections.Counter(e["implementationStatus"] for e in catalog["entries"])))
    print("Army model counts:", army["totals"], "required server tests:",army["server"]["suite"])


if __name__ == "__main__": main()
