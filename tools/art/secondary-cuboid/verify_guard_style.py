"""Verify the immutable production build and two explicitly scoped native segments.

Run in the isolated art worktree; no Java client is started by this verifier.
Segment 02 intentionally has a recorded QA camera failure AFTER its 19 valid
stages. Segment 03 resumes at 19 with the SAME production/resources/classes.
This does not promote the first segment's entire failed run to a whole-run pass.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/art/guard-style-v2"
BASE = Path("/Users/a15356015027/Desktop/dynasty/build/maintenance-artifacts/art-secondary20/dynasty-1.4.0.jar")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def owner_xyz(sample):
    return tuple(float(v) for v in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", sample["owner"]))


def main():
    a = OUT / "native/guard-style-final-02"
    b = OUT / "native/guard-style-final-03"
    assert "NullPointerException" in (a / "FAIL.txt").read_text()
    assert len(list(a.glob("*-state.json"))) == 19 and not (a / "PASS.txt").exists()
    assert "PASS: native stages 19 through 28" in (b / "PASS.txt").read_text()
    assert not (b / "FAIL.txt").exists() and len(list(b.glob("*-state.json"))) == 10
    manifests = [read(p / "runtime-manifest.json") for p in [a, b]]
    assert manifests[0]["production"] == manifests[1]["production"]
    prod = manifests[0]["production"]
    jar = ROOT / "build/libs/dynasty-1.4.0.jar"
    assert sha(jar) == prod["jarSha256"] and jar.read_bytes() == (ROOT / "build/reobfJar/output.jar").read_bytes()
    for path, digest in prod["sources"].items():
        assert sha(ROOT / path) == digest, path
    checked = 0
    for manifest in manifests:
        for tree in manifest["trees"]:
            snapshot = Path(tree["snapshot"])
            assert {str(f.relative_to(snapshot)) for f in snapshot.rglob("*") if f.is_file()} == {r["path"] for r in tree["files"]}
            for row in tree["files"]:
                assert sha(snapshot / row["path"]) == row["sha256"], row["path"]
                checked += 1
    # Only QA classes differ between the segments, never game classes/resources.
    for i in [0, 1, 2]:
        assert manifests[0]["trees"][i]["files"] == manifests[1]["trees"][i]["files"]
        for row in manifests[1]["trees"][i]["files"]:
            assert sha(Path(manifests[1]["trees"][i]["source"]) / row["path"]) == row["sha256"]
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(jar) as new:
        assert set(old.namelist()) == set(new.namelist())
        changed = sorted(n for n in old.namelist() if old.read(n) != new.read(n))
        assert changed == ["META-INF/MANIFEST.MF", "com/dynasty/client/character/DynastyCharacterModel.class", "com/dynasty/client/character/DynastyCharacterRenderer$1.class"], changed
        assert not any(any(q in n for q in ["GuardStyleClientQa", "GuardStyleProof", "LegacyGuardModel", "QuietWindowAgent"]) for n in new.namelist())
    proof = read(OUT / "headless/rig-clearance-proof.json")
    assert proof["modelDevClassSha256"] == sha(ROOT / "build/classes/java/main/com/dynasty/client/character/DynastyCharacterModel.class")
    assert proof["actualJavaPoseSamples"] == 13545 and proof["obbPairs"] == 4740750
    assert proof["finalOverlappingPairs"] == 0 and proof["baselineOverlappingPairs"] > 0
    assert proof["beforeCuboids"] == 153 and proof["afterCuboids"] == 166 and proof["addedJoints"] == 2
    assert proof["allOldJointsRetained"] and proof["rootOffsetsUnchanged"] and proof["otherRolesExactPoseSamples"] == 96
    for p in [a, b]:
        assert read(p / "rig-clearance-proof.json") == proof
        grip = read(p / "grip-sweep.json")
        assert grip["samples"] == 128 and grip["worstSeparationErrorBlocks"] < .0001
    states = [read((a if i < 19 else b) / f"{i:02d}-state.json") for i in range(29)]
    assert all(s["stage"] == i and s["viewport"] == [2800, 1800] for i, s in enumerate(states))
    for i, s in enumerate(states[:16]):
        assert s["entities"] == s["renderedCountMax"] == 1 and s["boxes"] == 166
        assert len(s["joints"]) == 72 and s["joints"] == states[0]["joints"]
        assert s["boltCaseVisible"] == (4 <= i <= 7) and s["spearVisible"] == (12 <= i <= 15)
        assert s["nativeClearanceSamples"] > 0 and s["nativeWorstOverlapBlocks"] == 0
        if 4 <= i <= 7:
            assert abs(s["supportGripSeparationBlocks"] - .175) < .0001
        if 12 <= i <= 15:
            assert "chang_qiang" in s["mainHand"]
    loads = states[16:19]
    assert loads[0]["entities"] == 0
    for s in loads[1:]:
        assert s["entities"] == 18 and s["frames"] >= 120
        assert s["renderedCountMin"] == s["renderedCountMax"] == 18 and s["all18RenderedFraction"] >= .8
        assert s["medianFrameMs"] < 50 and s["p95FrameMs"] < 100
        assert s["nativeGripSamples"] > 120 and s["nativeGripMaxSeparationErrorBlocks"] < .0001
        assert s["nativeClearanceSamples"] > 0 and s["nativeWorstOverlapBlocks"] == 0
    live = states[18]
    assert live["guardsMovedOver1Block"] >= 12 and live["guardsWithKneeMotion"] >= 12 and live["guardsNavigatingAtFirstSample"] >= 1
    for sample in live["movementSamples"]:
        assert len(sample["entities"]) == 18 and all(not m["noAi"] for m in sample["entities"])
    delta = math.dist(owner_xyz(live["movementSamples"][0]), owner_xyz(live["movementSamples"][1]))
    assert delta > 1, "Real input did not send changed owner positions to the server"
    for s in states[19:23]:
        assert s["entities"] == 1 and not s["noAi"] and s["boltCaseVisible"] and not s["spearVisible"]
        assert s["nativeClearanceSamples"] > 0 and s["nativeWorstOverlapBlocks"] == 0
        assert s["nativeGripSamples"] > 1 and s["nativeGripMaxSeparationErrorBlocks"] < .0001
        assert abs(s["supportGripSeparationBlocks"] - .175) < .0001
        assert len(s["actualKneeRange"]) == 1 and all(v[1] - v[0] > .02 for v in s["actualKneeRange"].values())
        sample = s["serverMovement"][0]
        assert not sample["entities"][0]["noAi"]
        assert math.dist(sample["entities"][0]["position"], [0, -60, 0]) > 1
    for s in states[23:]:
        assert s["entities"] == 1 and s["boxes"] != 166 and not s["boltCaseVisible"] and not s["spearVisible"]
        assert "RebelGeneral" in s["scope"]
    evidence = []
    for p in [a, b]:
        for f in sorted(p.iterdir()):
            if f.suffix in [".json", ".png"] or f.name in ["PASS.txt", "FAIL.txt"]:
                evidence.append({"path": str(f.relative_to(ROOT)), "sha256": sha(f)})
    result = {"production": prod, "changedJarEntries": changed, "checkedFrozenFiles": checked,
              "nativeSegments": [{"run": a.name, "acceptedStages": [0, 18], "wholeRun": "FAILED: camera attempted to read entity before spawn packet"}, {"run": b.name, "acceptedStages": [19, 28], "wholeRun": "PASS"}],
              "actualJavaClearance": proof, "equipmentViews": 16, "liveCloseViews": 4, "unchangedGeneralViews": 6,
              "load": [{k: s[k] for k in ["stage", "medianFrameMs", "p95FrameMs", "serverAverageTickMs", "renderedCountMin", "renderedCountMax", "frames"]} for s in loads],
              "following": {k: live[k] for k in ["guardsMovedOver1Block", "guardsNavigatingAtFirstSample", "guardsWithKneeMotion"]},
              "realInputOwnerMovementBlocks": delta, "evidence": evidence,
              "limitations": ["Automatic client, no human gameplay or paid formation acceptance", "Standing static art is distinct from natural shooting/reload and skill timing", "Frozen isolated sources exclude other developers' newer primary WIP", "Other clients can run concurrently; load figures describe this run only"]}
    (OUT / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: 29 native stages in 2 immutable segments, {checked} frozen files, 13545 poses / zero skirt-leg intersections; JAR {prod['jarSha256']}")


if __name__ == "__main__":
    main()
