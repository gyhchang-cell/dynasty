"""JDK-only schedule/import checks plus static boundary assertions. Never loads a Minecraft runtime."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[3];O=R/'docs/cod4/audit-20261022/sweep-native-acceptance/driver'
compile_receipt=json.loads((O/'compile01.json').read_text());W=B/'.work'/('checks-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));W.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/compile_receipt['source'];assert sha(source)==compile_receipt['source_sha256']
classes=R/compile_receipt['work']/'classes';target=W/'check-classes';target.mkdir();bin=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
commands=[]
def run(cmd):
    commands.append(cmd);r=subprocess.run(cmd,capture_output=True,text=True);(W/(str(len(commands))+'-output.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==0,(cmd,r.stdout,r.stderr)
    return r.stdout
run([str(bin/'javac'),'-J-Djava.awt.headless=true','--release','17','-proc:none','-cp',str(classes),'-d',str(target),str(B/'checks/DriverProtocolCheck.java')])
log=W/'classload.log'
result=run([str(bin/'java'),'-Djava.awt.headless=true','-Xlog:class+load=info:file='+str(log),'-cp',str(classes)+':'+str(target),'DriverProtocolCheck',str(W/'raw-import')])
loaded=log.read_text();assert 'net.minecraft.' not in loaded and 'net.minecraftforge.' not in loaded
checks={}
checks['nested_schedule_and_import_execute_without_Minecraft_Forge']=True
s=source.read_text()
for forbidden in ['createFreshLevel(','.setScreen(','.glfwFocusWindow(','.glfwShowWindow(','.hurt(','.setGameTime(','.setDayTime(','ProcessBuilder','Runtime.getRuntime','performPrefixedCommand(','FangtianSweep.begin(','FangtianSweep.finish(']:
    checks['absent '+forbidden]=forbidden not in s
checks['default_off']= 'static final boolean ENABLED=Boolean.getBoolean("dynasty.sweepdriver.enabled")' in s and 'if(!ENABLED||done||e.phase!=TickEvent.Phase.END)return;' in s
checks['native_chat_entry']='mc.player.connection.sendCommand(command)' in s
checks['no_direct_attack_or_private_command_dispatch']='.gameMode.attack(' not in s and 'SweepClient.start(' not in s and 'ClientCommandHandler.runCommand(' not in s
checks['native_ready_message_event']='ClientChatReceivedEvent.System' in s and 'sendSystemMessage(Component.literal("[COD4_SWEEP_READY_' in s
checks['own_instance_hash_and_hidden_checks']='"Wrong driver artifact"' in s and '"Wrong private production artifact"' in s and 'GLFW.GLFW_VISIBLE' in s and 'GLFW.GLFW_FOCUSED' in s
checks['bounded_normal_exit']='900_000_000_000L' in s and '240_000_000_000L' in s and '60_000_000_000L' in s and 'mc.stop()' in s
checks['no_acceptance_PASS_marker']='server-PASS' not in s and 'd.put("overall_acceptance",false)' in s
checks['separate_ADDON_pack_format_15']=json.loads((B/'resources/pack.mcmeta').read_text())['pack']['pack_format']==15
assert all(checks.values()),checks
(W/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
r=dict(status='PASS_OFFLINE_PROTOCOL_ONLY',jdk_output=result.strip(),assertions=int(re.search(r'checks=(\d+)',result).group(1)),schedule_combinations=36,checks=checks,work=str(W.relative_to(R)),Minecraft_or_Forge_runtime_loaded=False,game_started=False,native_chat_C2S_or_graphics_verified=False,source_sha256=sha(source),check_source_sha256={str(p.relative_to(R)):sha(p) for p in [B/'checks/DriverProtocolCheck.java',Path(__file__)]})
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');(O/'offline-checks01.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
