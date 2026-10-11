"""Verify the final guard proportions and all29 actual native stages; no Java launch."""
import hashlib
import json
import math
from pathlib import Path
import zipfile
from verify_guard_style import owner_xyz

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/art/guard-proportion-v3"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    native = OUT / "native/guard-proportion-final-02"
    assert "PASS: native stages 0 through 28" in (native / "PASS.txt").read_text() and not (native / "FAIL.txt").exists()
    assert len(list(native.glob("*-state.json"))) == 29
    manifest = read(native / "runtime-manifest.json")
    prod = manifest["production"]
    jar = ROOT / "build/libs/dynasty-1.4.0.jar"
    assert sha(jar) == prod["jarSha256"] and jar.read_bytes() == (ROOT / "build/reobfJar/output.jar").read_bytes()
    for p, digest in prod["sources"].items():
        assert sha(ROOT / p) == digest, p
    checked = 0
    for tree in manifest["trees"]:
        snapshot = Path(tree["snapshot"])
        assert {str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()} == {f["path"] for f in tree["files"]}
        for f in tree["files"]:
            assert sha(snapshot / f["path"]) == f["sha256"]
            if tree["source"] is not None:
                assert sha(Path(tree["source"]) / f["path"]) == f["sha256"]
            checked += 1
    baseline = Path("/Users/a15356015027/Desktop/dynasty/build/maintenance-artifacts/art-guard-style-v2/dynasty-1.4.0.jar")
    with zipfile.ZipFile(baseline) as before, zipfile.ZipFile(jar) as after:
        assert set(before.namelist()) == set(after.namelist())
        changed = sorted(p for p in before.namelist() if before.read(p) != after.read(p))
        assert changed == ["META-INF/MANIFEST.MF", "com/dynasty/client/character/DynastyCharacterModel.class"], changed
        assert not any(any(q in p for q in ["GuardProportion", "LegacyGuard", "GuardStyleProof", "GuardStyleClientQa", "QuietWindowAgent"]) for p in after.namelist())
    proof = read(OUT / "headless/rig-clearance-proof.json")
    assert read(native / "rig-clearance-proof.json") == proof
    assert proof["modelDevClassSha256"] == sha(ROOT / "build/classes/java/main/com/dynasty/client/character/DynastyCharacterModel.class")
    assert proof["actualJavaPoseSamples"] == 13545 and proof["obbPairs"] == 4740750 and proof["finalOverlappingPairs"] == 0
    assert proof["beforeCuboids"] == proof["afterCuboids"] == 166 and proof["joints"] == 72 and proof["addedJoints"] == 0
    assert proof["rootOffsetsUnchanged"] and proof["skirtLegFootVerticesUnchanged"] and proof["otherRolesExactPoseSamples"] == 96
    assert proof["neckJawContactVerifiedPoseSamples"] == 32 and proof["minNeckJawContactBlocks"] > 0
    assert proof["headScale"] == .94 and proof["headScaledAxesVerifiedPoseSamples"] == 32
    assert proof["shoulderWidthAfter"] / proof["shoulderWidthBefore"] == 1.05
    assert math.isclose(proof["waistWidthAfter"] / proof["waistWidthBefore"], 4.95 / 5.05)
    states = [read(native / f"{i:02d}-state.json") for i in range(29)]
    previous_native = ROOT / "docs/art/guard-style-v2/native/guard-style-final-02"
    previous = read(previous_native / "00-state.json")
    for i, s in enumerate(states):
        assert s["stage"] == i and s["viewport"] == [2800, 1800]
        if i != 16 and i < 23:
            assert s["nativeClearanceSamples"] > 0 and s["nativeWorstOverlapBlocks"] == 0
        if i < 16 or 19 <= i <= 22:
            assert s["boxes"] == 166 and s["joints"] == previous["joints"]
            assert s["entities"] == s["renderedCountMax"] == 1
            assert s["boltCaseVisible"] == (4 <= i <= 7 or 19 <= i <= 22)
            assert s["spearVisible"] == (12 <= i <= 15)
        if 4 <= i <= 7 or 19 <= i <= 22:
            assert abs(s["supportGripSeparationBlocks"] - .175) < .0001
            assert s["nativeGripSamples"] > 0 and s["nativeGripMaxSeparationErrorBlocks"] < .0001
        if 12 <= i <= 15:
            assert "chang_qiang" in s["mainHand"]
    for s in states[17:19]:
        assert s["entities"] == 18 and s["frames"] >= 120 and s["all18RenderedFraction"] >= .8
        assert s["renderedCountMin"] == s["renderedCountMax"] == 18
        assert s["medianFrameMs"] < 50 and s["p95FrameMs"] < 100
        assert s["nativeGripSamples"] > 120 and s["nativeGripMaxSeparationErrorBlocks"] < .0001
    live = states[18]
    assert live["guardsMovedOver1Block"] >= 12 and live["guardsWithKneeMotion"] >= 12 and live["guardsNavigatingAtFirstSample"] >= 1
    for sample in live["movementSamples"]:
        assert len(sample["entities"]) == 18 and all(not m["noAi"] for m in sample["entities"])
    delta = math.dist(owner_xyz(live["movementSamples"][0]), owner_xyz(live["movementSamples"][1]))
    assert delta > 1
    for s in states[19:23]:
        assert not s["noAi"] and len(s["actualKneeRange"]) == 1 and all(v[1] - v[0] > .02 for v in s["actualKneeRange"].values())
        assert math.dist(s["serverMovement"][0]["entities"][0]["position"], [0, -60, 0]) > 1
    for s in states[23:]:
        assert s["entities"] == 1 and s["boxes"] != 166 and not s["boltCaseVisible"] and not s["spearVisible"] and "RebelGeneral" in s["scope"]
    grip = read(native / "grip-sweep.json")
    assert grip["samples"] == 128 and grip["worstSeparationErrorBlocks"] < .0001
    report = {"production": prod, "nativeRun": native.name, "nativeStages": 29, "checkedFrozenFiles": checked,
              "changedJarEntries": changed, "proportionsAndGeometry": proof, "gripSweep": grip,
              "following": {k: live[k] for k in ["guardsMovedOver1Block", "guardsNavigatingAtFirstSample", "guardsWithKneeMotion"]},
              "realOwnerInputMovementBlocks": delta,
              "load": [{k: s[k] for k in ["stage", "frames", "medianFrameMs", "p95FrameMs", "renderedCountMin", "renderedCountMax", "serverAverageTickMs"]} for s in states[16:19]],
              "evidence": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in sorted(native.iterdir()) if p.suffix in [".png", ".json"] or p.name == "PASS.txt"],
              "limitations": ["Automatic real native client; not humans or paid roster formation", "Natural shooting/reload/skill timing and other owners' latest primary WIP remain untested"]}
    (OUT / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: guard proportions/head ensemble axes, unchanged166 cubes/72 names, 13545 clearance poses and all29 native stages; JAR {prod['jarSha256']}")


if __name__ == "__main__":
    main()
