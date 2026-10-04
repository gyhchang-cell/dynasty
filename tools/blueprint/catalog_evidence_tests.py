#!/usr/bin/env python3
"""Small temporary-fixture regressions for the catalogue evidence parser; no game/build run."""
import importlib.util
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import uuid
import zlib

SPEC = importlib.util.spec_from_file_location("catalog", Path(__file__).with_name("catalog.py"))
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)
REAL_ROOT = catalog.ROOT
STAGES = catalog.client_stage_contract()["stageNames"]
IDS = ["zuwu_daoshou", "ludun_jiashi", "fufa_jijiu", "shanjing_shanxiao"]


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


PNG = (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 800, 600, 8, 0, 0, 0, 0))
       + png_chunk(b"IDAT", zlib.compress((b"\0" * 801) * 600)) + png_chunk(b"IEND", b""))


class ClientEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dynasty-catalog-evidence-")
        catalog.ROOT = Path(self.temporary.name).resolve()
        self.write("tools/blueprint/qa-src/com/dynasty/client/BlueprintClientQa.java",
                   "String[] NAMES = {" + ",".join(json.dumps(name) for name in STAGES) + "};")

    def tearDown(self):
        catalog.ROOT = REAL_ROOT
        self.temporary.cleanup()

    def write(self, relative, data):
        path = catalog.ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        return path

    def fixture(self, players=2):
        run = "fixture-solo" if players == 1 else "fixture-network"
        base = "evidence/" + run
        owners = [(0, 1, "attack"), (1, 2, "attack"), (2, 4, "buff"), (3, 5, "skill"),
                  (2, 3, "attack"), (3, 6, "rock"), (1, 0, "death"), (0, 0, "death"),
                  (0, 0, "death"), (2, 0, "death"), (2, 0, "death"), (3, 0, "death"), (3, 0, "death"),
                  (3, 0, "climb"), (3, 6, "rock")]
        final_mobs = []
        for role in (["host"] if players == 1 else ["host", "peer"]):
            lines = []
            for index, name in enumerate(STAGES):
                if index >= 7:
                    owner, active_skill, active_clip = owners[index - 7]
                    for entity_index, identity in enumerate(IDS):
                        entity_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{run}/{min(index,20)}/{identity}"))
                        skill = active_skill if entity_index == owner else 0
                        start = 100 + index if entity_index == owner and index != 20 else -1
                        clip = active_clip if entity_index == owner else "idle"
                        phase = "ACTIVE" if skill else "IDLE"
                        lines.append(f"{name} entity={identity} uuid={entity_uuid} skill={skill} phase={phase} start={start} clientTime=200 actionAge=20.0")
                        lines.append(f"Rendered {identity} requested=animation.{identity}.{clip} queued=animation.{identity}.{clip} controller=RUNNING root=rot(0,0,0)")
                        if index == 21 and role == "host":
                            final_mobs.append({"entityId": entity_index + 1, "id": identity, "uuid": entity_uuid, "skill": skill, "start": start})
                capture = f"Captured {name}; four exact UUIDs tracked; players={players}; FPS=60"
                lines.append(capture)
                self.write(f"{base}/{role}/{index:02d}-{name}.png", PNG)
                self.write(f"{base}/coord/ready-{index}-{role}.txt", run + f"\nAll four exact entity UUIDs tracked; players={players}")
                self.write(f"{base}/coord/captured-{index}-{role}.txt", run + "\n" + capture)
            observed = "\n".join(lines) + "\n"
            for index in (20,21):
                beast = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{run}/20/{IDS[3]}"))
                server = dict(run=run, uuid=beast, noAi=False, noGravity=False, climbing=index==20,
                              horizontalCollision=index==20, climbStart=190, climbFace="south", onGround=index==21,
                              position=[0,3,0], initialY=0, skill=0 if index==20 else 6, skillStart=121,
                              rocks=[dict(uuid="fixture-rock")])
                event = dict(run=run, role=role, stage=index, uuid=beast, server=server, clientTick=200,
                             serverTick=200, geometryValid=True, rootAwayDot=1, rootUpDot=1, stanceContacts=4,
                             contacts={str(i):dict(planeDistance=.03,projectsOntoSolidWall=True) for i in range(4)},
                             clientClimbStart=190, clientClimbFace="south", clientSkill=6, clientStart=121,
                             visibleRockUuids=["fixture-rock"])
                self.write(f"{base}/{role}/{index}-encounter.json",json.dumps(event))
            final = ("PASS: isolated single-client 22 stages, actual Gecko action/death clips, and screenshot harness. This is NOT a multiplayer or visual-quality pass."
                     if players == 1 else "PASS: real loopback TCP clients acknowledged all 22 stages with matching entity identity, action start, phase, actual Gecko action/death clips, possession effect and target. Screenshots still require visual review.")
            self.write(f"{base}/{role}/observations.txt", observed)
            self.write(f"{base}/{role}/PASS.txt", observed + final + "\n")
        self.write(f"{base}/coord/stage.json", json.dumps({"run": run, "index": 21, "phase": "ACTIVE", "published": 119, "mobs": final_mobs}))
        self.write(f"{base}/coord/complete.txt", run + " all stages acknowledged by " + ("host only" if players == 1 else "both TCP clients"))
        self.write(f"{base}/coord/listening.txt", run + " loopback 127.0.0.1:25587")
        return catalog.ROOT / base

    def edit_observations(self, run, role, before, after):
        for name in ("observations.txt", "PASS.txt"):
            path = run / role / name
            path.write_text(path.read_text().replace(before, after, 1))

    def artifact_manifest(self, run):
        class_root, resource_root, qa_root = "build/classes/java/main", "build/resources/main", "build/classes/java/blueprintQa"
        for name in ("TemplateMob.class", "combat/CenteredGroundNavigation.class"):
            self.write(class_root + "/com/dynasty/blueprint/" + name, b"synthetic class bytes")
        resources = [f"assets/dynasty/geo/blueprint/{identity}.geo.json" for identity in IDS]
        resources += [f"assets/dynasty/animations/blueprint/{identity}.animation.json" for identity in IDS]
        resources += [f"assets/dynasty/textures/entity/{atlas}.png" for atlas in ("royal_guard", "imperial_soldier", "nian_beast")]
        for name in resources:
            self.write(resource_root + "/" + name, b"synthetic resource bytes")
            self.write("src/main/resources/" + name, b"synthetic resource bytes")
        self.write(qa_root + "/Qa.class", b"synthetic QA")
        trees = []
        for root in (class_root, resource_root, qa_root):
            files = sorted((catalog.ROOT / root).rglob("*"))
            entries = [{"path": path.relative_to(catalog.ROOT / root).as_posix(), "bytes": path.stat().st_size,
                        "sha256": catalog.digest(path)} for path in files if path.is_file()]
            digest = hashlib.sha256("".join(e["path"] + "\0" + e["sha256"] + "\n" for e in entries).encode()).hexdigest()
            trees.append({"root": root, "fileCount": len(entries), "bytes": sum(e["bytes"] for e in entries),
                          "sha256": digest, "entries": entries})
        combined = hashlib.sha256("".join(t["root"] + "\0" + t["sha256"] + "\n" for t in trees[:2]).encode()).hexdigest()
        path = run / "artifact-manifest.json"
        path.write_text(json.dumps({"formatVersion": 1, "run": run.name, "createdAt": "synthetic fixture",
                                   "scope": "synthetic test only", "productionSha256": combined, "trees": trees}))
        return path

    def test_complete_solo_remains_quality_pending(self):
        result = catalog.client_run_evidence(self.fixture(1), 1)
        self.assertEqual(result["status"], "HARNESS_PASS_QUALITY_PENDING")
        self.assertEqual(len(result["screenshots"]), 22)
        self.assertEqual(result["artifactIdentity"]["status"], "PENDING_EXECUTED_CLASSPATH_SNAPSHOT")

    def test_complete_network_compares_52_printed_identities(self):
        result = catalog.client_run_evidence(self.fixture(), 2)
        self.assertEqual(len(result["screenshots"]), 44)
        self.assertEqual(result["crossClient"]["identityActionMatches"], 60)

    def test_old_fourteen_stage_run_is_rejected(self):
        run = self.fixture(1)
        path = run / "coord/stage.json"
        data = json.loads(path.read_text())
        data["index"] = 13
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, "incomplete run"):
            catalog.client_run_evidence(run, 1)

    def test_missing_screenshot_is_rejected(self):
        run = self.fixture()
        (run / "peer/19-shanxiao-death-curled-faded.png").unlink()
        with self.assertRaisesRegex(AssertionError, "screenshots"):
            catalog.client_run_evidence(run, 2)

    def test_mixed_run_ack_is_rejected(self):
        run = self.fixture()
        path = run / "coord/captured-17-peer.txt"
        path.write_text(path.read_text().replace("fixture-network", "other-run"))
        with self.assertRaisesRegex(AssertionError, "acknowledgement"):
            catalog.client_run_evidence(run, 2)

    def test_network_requires_two_players_on_every_capture(self):
        run = self.fixture()
        self.edit_observations(run, "peer", "players=2", "players=1")
        with self.assertRaisesRegex(AssertionError, "player count"):
            catalog.client_run_evidence(run, 2)

    def test_different_entity_uuid_across_clients_is_rejected(self):
        run = self.fixture()
        original = str(uuid.uuid5(uuid.NAMESPACE_DNS, "fixture-network/7/zuwu_daoshou"))
        self.edit_observations(run, "peer", original, str(uuid.uuid4()))
        with self.assertRaisesRegex(AssertionError, "Cross-client"):
            catalog.client_run_evidence(run, 2)

    def test_idle_clip_cannot_masquerade_as_attack(self):
        run = self.fixture()
        self.edit_observations(run, "peer", "queued=animation.zuwu_daoshou.attack", "queued=animation.zuwu_daoshou.idle")
        with self.assertRaisesRegex(AssertionError, "Gecko clip"):
            catalog.client_run_evidence(run, 2)

    def test_inactive_off_camera_fixture_may_have_stopped_controller(self):
        run = self.fixture(1)
        self.edit_observations(run, "host", "queued=animation.fufa_jijiu.idle controller=RUNNING", "queued=none controller=STOPPED")
        self.assertEqual(catalog.client_run_evidence(run, 1)["status"], "HARNESS_PASS_QUALITY_PENDING")

    def test_failure_marker_rejects_even_existing_pass(self):
        run = self.fixture()
        (run / "peer/FAIL.txt").write_text("FAIL: later error")
        with self.assertRaisesRegex(AssertionError, "Failure report"):
            catalog.client_run_evidence(run, 2)

    def test_full_classpath_snapshot_matches_without_claiming_loaded_jar(self):
        run = self.fixture(1)
        self.artifact_manifest(run)
        result = catalog.client_artifact_manifest(run, run.name)
        self.assertEqual(result["status"], "FROZEN_RUNCLIENT_CLASSPATH_SNAPSHOT_MATCHES_CURRENT_OUTPUTS")
        self.assertIn("not proof of loading the packaged release JAR", result["limits"])

    def test_changed_classpath_bytes_invalidate_frozen_manifest(self):
        run = self.fixture(1)
        self.artifact_manifest(run)
        self.write("build/classes/java/main/com/dynasty/blueprint/TemplateMob.class", b"changed class bytes")
        with self.assertRaisesRegex(AssertionError, "changed since snapshot"):
            catalog.client_artifact_manifest(run, run.name)

    def test_changed_source_resource_cannot_reuse_old_runtime_hash(self):
        run = self.fixture(1)
        self.artifact_manifest(run)
        self.write("src/main/resources/assets/dynasty/geo/blueprint/zuwu_daoshou.geo.json", b"changed source asset")
        with self.assertRaisesRegex(AssertionError, "Source asset differs"):
            catalog.client_artifact_manifest(run, run.name)

    def test_manifest_from_another_run_is_rejected(self):
        run = self.fixture(1)
        self.artifact_manifest(run)
        with self.assertRaisesRegex(AssertionError, "run/schema"):
            catalog.client_artifact_manifest(run, "different-run")


if __name__ == "__main__":
    unittest.main()
