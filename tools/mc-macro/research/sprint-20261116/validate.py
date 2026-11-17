"""Offline sprint candidate regression. Never starts an app or attaches to a game."""
from pathlib import Path
import importlib.util
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.build/candidates/sprint-20261116'
spec = importlib.util.spec_from_file_location('baseline', ROOT / 'research/native-right-1104/validate.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)
baseline.OUT = OUT / 'regression'
baseline.OUT.mkdir(exist_ok=True)
baseline.SWIFTC += ['-vfsoverlay', str(ROOT / '.build/sdk-overlay.json'), '-module-cache-path', str(ROOT / '.build/module-cache')]
baseline.main()
baseline.run('CombatAdaptation', baseline.COMMON + [ROOT / 'Tests/CombatAdaptation/main.swift'], [baseline.FIXTURE])
baseline.run('SprintTransport', [ROOT / 'Sources/SprintTelemetry.swift', ROOT / 'Tests/SprintTelemetry/main.swift'])
jdk = Path('/Users/a15356015027/Library/Java/JavaVirtualMachines/ms-21.0.12.1/Contents/Home/bin')
java_out = OUT / 'java'
java_out.mkdir(exist_ok=True)
subprocess.run([str(jdk / 'javac'), '--release', '8', '-d', str(java_out), str(ROOT / 'sprint-agent/src/local/mcmacro/SprintAgent.java'), str(ROOT / 'Tests/SprintAgent/SprintAgentTest.java')], check=True)
result = subprocess.run([str(jdk / 'java'), '-cp', str(java_out), 'local.mcmacro.SprintAgentTest'], text=True, capture_output=True, check=True)
(OUT / 'agent-tests.log').write_text(result.stdout)
print(result.stdout, end='')
