package local.mcmacro;
import com.sun.tools.attach.VirtualMachine;
/** Explicit attach entry point; never discovers or chooses a process itself. */
public final class Attach {
    public static void main(String[] args) throws Exception {
        if(args.length!=3)throw new IllegalArgumentException("pid agent-jar session");
        VirtualMachine vm=VirtualMachine.attach(args[0]);
        try {vm.loadAgent(args[1],args[2]);} finally {vm.detach();}
        System.out.println("Read-only telemetry attached.");
    }
}
