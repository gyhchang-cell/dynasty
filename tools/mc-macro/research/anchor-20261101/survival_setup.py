from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parents[2];game=root/'.build/anchor-singleplayer';pid=(game/'pid').read_text().strip()
assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
commands=['/gamemode survival','/difficulty normal','/time set day','/item replace entity @s weapon.offhand with minecraft:totem_of_undying','/effect give @s minecraft:instant_health 1 10 true']
for cmd in commands:
 r=subprocess.run([str(game/'probe'),'command',cmd],env={**os.environ,'MC_TEST_PID':pid},capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
