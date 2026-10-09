"""Run prepared Forge clients without keeping a Gradle cache lock for the whole session.

Requires Java 17 and a working graphical display (ordinary macOS desktop or Xvfb on Linux).
Only launches/terminates its own processes; worlds are created under build/cod2-client.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("launch", type=Path)
parser.add_argument("run_id")
parser.add_argument("--solo", action="store_true")
args = parser.parse_args()
if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for c in args.run_id) or args.run_id in (".", ".."):
    parser.error("Use a fresh alphanumeric run id")
repo = Path(__file__).resolve().parents[2]
launch = json.loads(args.launch.read_text())
out = repo / "build/cod2-client" / args.run_id
out.mkdir(parents=True, exist_ok=False)
java = launch["executable"] or shutil.which("java")
if java is None:
    raise RuntimeError("Java 17 is required")
children, logs = [], []
try:
    roles = ["host"] if args.solo else ["host", "peer"]
    for role in roles:
        work = out / role
        work.mkdir()
        jvm = list(launch["jvmArgs"])
        for key, value in {"dynasty.cod2Qa.role": role, "dynasty.cod2Qa.output": str(out / "results"),
                           "dynasty.cod2Qa.solo": str(args.solo).lower()}.items():
            jvm = [v for v in jvm if not v.startswith("-D" + key + "=")]
            jvm.append("-D" + key + "=" + value)
        game = list(launch["args"])
        game[game.index("--username") + 1] = "Dungeon" + role.title()
        env = dict(os.environ, **launch["environment"])
        log = (out / (role + ".log")).open("w")
        logs.append(log)
        children.append(subprocess.Popen([java, *jvm, "-cp", launch["classpath"], launch["main"], *game],
                                          cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT))
    for role, process in zip(roles, children):
        # Forge can remain on its loading-error screen without exiting the JVM.
        # Surface that failure immediately instead of waiting eleven minutes.
        import time
        deadline = time.monotonic() + 660
        while True:
            try:
                code = process.wait(timeout=1)
                break
            except subprocess.TimeoutExpired:
                with (out / (role + '.log')).open('rb') as current:
                    current.seek(max(0, current.seek(0, 2) - 16384))
                    tail = current.read().decode(errors='replace')
                if any(message in tail for message in ('Failed to create mod instance.',
                        'Failed to complete lifecycle event', 'LoadingFailedException')):
                    raise RuntimeError(f'{role} failed during Forge loading; inspect {out / (role + ".log")}')
                if time.monotonic() >= deadline:
                    raise RuntimeError(f'{role} timed out; inspect {out / (role + ".log")}')
        passed = out / "results" / (role + "-PASS.txt")
        if code != 0 or not passed.is_file():
            raise RuntimeError(f"{role} did not pass (exit={code}); inspect {out / (role + '.log')}")
        print(role, passed.read_text().strip(), flush=True)
finally:
    for process in reversed(children):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    for log in logs:
        log.close()
