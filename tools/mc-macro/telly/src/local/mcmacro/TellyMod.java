package local.mcmacro;

import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import net.minecraftforge.fml.common.FMLCommonHandler;
import java.util.*;

@Mod(modid="mcmacro_telly", name="MC Telly Assistant (Experimental)", version="0.1.0",
     acceptedMinecraftVersions="[1.8.9]", clientSideOnly=true, acceptableRemoteVersions="*")
public final class TellyMod {
    private Object mc, player, world, settings;
    private Object[] bindings;
    private boolean running, blockedUntilRelease;
    private TellyPlan plan;
    private TellyPlan.Frame frame;
    private float heading, yaw, pitch, sensitivity;
    private double startX, startY, startZ, lastX, lastZ;
    private int floorY, failedPlacements;
    private String lastError = "";
    private static final String[] KEY_SRG = {"field_74351_w", "field_74368_y", "field_74370_x", "field_74366_z", "field_74314_A", "field_74311_E", "field_151444_V"};
    private static final String[] KEY_MCP = {"keyBindForward", "keyBindBack", "keyBindLeft", "keyBindRight", "keyBindJump", "keyBindSneak", "keyBindSprint"};

    @Mod.EventHandler public void init(FMLInitializationEvent event) {
        FMLCommonHandler.instance().bus().register(this);
    }

    @SubscribeEvent public void tick(TickEvent.ClientTickEvent event) {
        try {
            if (mc == null) mc = Reflect.call(Reflect.type("net.minecraft.client.Minecraft"), "func_71410_x", "getMinecraft");
            if (event.phase == TickEvent.Phase.START) beginTick();
            else if (running && frame != null && frame.place) place();
        } catch (Exception ex) {
            String detail = ex.toString();
            stop(); blockedUntilRelease = true;
            if (!detail.equals(lastError)) {
                lastError = detail;
                System.err.println("[MC Telly] Disabled after compatibility error: " + detail);
                message("MC Telly：兼容性检查失败，已停止。请查看游戏日志。");
            }
        }
    }

    private void beginTick() throws Exception {
        boolean held = key(47); // Physical V; never auto-repeat/start after focus loss.
        if (!held) { stop(); blockedUntilRelease = false; return; }
        Object currentPlayer = Reflect.get(mc,"field_71439_g","thePlayer");
        Object currentWorld = Reflect.get(mc,"field_71441_e","theWorld");
        if (currentPlayer == null || currentWorld == null || Reflect.get(mc,"field_71462_r","currentScreen") != null
            || !Reflect.flag(mc,"field_71415_G","inGameHasFocus")) {
            stop(); blockedUntilRelease = true; return;
        }
        if (running && (player != currentPlayer || world != currentWorld)) {
            stop(); blockedUntilRelease = true; return;
        }
        if (blockedUntilRelease) return;
        if (!running) {
            player = currentPlayer; world = currentWorld;
            settings = Reflect.get(mc,"field_71474_y","gameSettings");
            if (!start()) { blockedUntilRelease = true; return; }
        }
        if (Reflect.flag(player,"field_70128_L","isDead") || ((Number)Reflect.call(player,"func_110143_aJ","getHealth")).floatValue() <= 0
            || (Boolean)Reflect.call(player,"func_70090_H","isInWater") || (Boolean)Reflect.call(player,"func_180799_ab","isInLava")
            || (Boolean)Reflect.call(player,"func_70617_f_","isOnLadder") || (Boolean)Reflect.call(player,"func_70115_ae","isRiding")) {
            abort("MC Telly：角色状态变化，已停止。松开 V 后可重新开始。"); return;
        }
        Object stack = Reflect.call(player,"func_70694_bm","getHeldItem");
        if (!validBlock(stack)) { abort("MC Telly：请手持完整方块，已停止。"); return; }
        // User movement input always overrides the assistant.
        for (int i : new int[] {0,1,2,3,5}) {
            if (key(code(bindings[i]))) { abort("MC Telly：检测到手动移动，已停止。"); return; }
        }
        double x = Reflect.num(player,"field_70165_t","posX"), y = Reflect.num(player,"field_70163_u","posY"), z = Reflect.num(player,"field_70161_v","posZ");
        double r = Math.toRadians(heading), along = -(x-startX)*Math.sin(r)+(z-startZ)*Math.cos(r);
        double sideways = (x-startX)*Math.cos(r)+(z-startZ)*Math.sin(r);
        if (y < startY - 0.45 || y > startY + 1.7 || Math.abs(sideways) > 0.65 || along < -0.5
            || Math.hypot(x-lastX,z-lastZ) > 1.5) {
            abort("MC Telly：位置偏离或落空，已停止。松开 V 后重新站位。"); return;
        }
        lastX=x; lastZ=z;
        sensitivity = (float)Reflect.num(settings,"field_74341_c","mouseSensitivity");
        frame = plan.tick(Reflect.flag(player,"field_70122_E","onGround"));
        if (frame.stalled) { abort("MC Telly：起跳或落地超时，已停止。"); return; }
        yaw = TellyPlan.quantize(heading + (frame.forward ? 0 : 180), heading, sensitivity);
        pitch = TellyPlan.quantize(frame.forward ? 0 : 72, 0, sensitivity);
        rotate(yaw,pitch);
        for (int i=0;i<bindings.length;i++) {
            boolean down = i==0 ? frame.forward : i==1 ? !frame.forward : i==4 ? frame.jump : i==6 && frame.forward;
            Reflect.set(bindings[i],"field_74513_e","pressed",down);
        }
        Reflect.call(player,"func_70031_b","setSprinting",new Class<?>[]{boolean.class},frame.forward);
    }

    private boolean start() throws Exception {
        if (!Reflect.flag(player,"field_70122_E","onGround")) { message("MC Telly：先站在完整方块上，再按住 V。"); return false; }
        Object held = Reflect.call(player,"func_70694_bm","getHeldItem");
        if (!validBlock(held)) { message("MC Telly：先手持完整方块，再按住 V。"); return false; }
        startX=lastX=Reflect.num(player,"field_70165_t","posX");
        startY=Reflect.num(player,"field_70163_u","posY");
        startZ=lastZ=Reflect.num(player,"field_70161_v","posZ");
        if (Math.abs(startY-Math.rint(startY))>0.05) { message("MC Telly：不支持台阶或半砖起步。"); return false; }
        floorY=(int)Math.floor(startY)-1;
        float currentYaw=(float)Reflect.num(player,"field_70177_z","rotationYaw");
        heading=TellyPlan.cardinal(currentYaw);
        if (Math.abs(currentYaw-heading)>8) { message("MC Telly：请朝正东、南、西或北，站在起跳边缘再按住 V。"); return false; }
        bindings=new Object[KEY_SRG.length];
        for(int i=0;i<bindings.length;i++) bindings[i]=Reflect.get(settings,KEY_SRG[i],KEY_MCP[i]);
        for(Object binding:bindings) if(code(binding)==47) { message("MC Telly：V 与移动键冲突，请先在控制设置解除冲突。"); return false; }
        plan=new TellyPlan(); frame=null; failedPlacements=0; running=true;
        message("MC Telly 实验模式：松开 V 停止；当前灵敏度 " + Math.round(Reflect.num(settings,"field_74341_c","mouseSensitivity")*200) + "%");
        return true;
    }

    private boolean validBlock(Object stack) throws Exception {
        if (stack==null || Reflect.num(stack,"field_77994_a","stackSize")<=0) return false;
        Object item=Reflect.call(stack,"func_77973_b","getItem");
        if(!Reflect.type("net.minecraft.item.ItemBlock").isInstance(item)) return false;
        Object block=Reflect.call(item,"func_179223_d","getBlock");
        return (Boolean)Reflect.call(block,"func_149686_d","isFullCube");
    }

    private void place() throws Exception {
        // Select only an actually visible horizontal face, on this bridge's level.
        // The vanilla right-click path performs reach, collision and server checks.
        double reach=((Number)Reflect.call(Reflect.get(mc,"field_71442_b","playerController"),"func_78757_d","getBlockReachDistance")).doubleValue();
        for(float offset:new float[]{0,4,-4,8,-8,12,-12}) {
            for(float aim:new float[]{62,68,74,80,56,50,84}) {
                float candidateYaw=TellyPlan.quantize(heading+180+offset,heading,sensitivity);
                float candidatePitch=TellyPlan.quantize(aim,0,sensitivity);
                rotate(candidateYaw,candidatePitch);
                Object hit=Reflect.call(player,"func_174822_a","rayTrace",new Class<?>[]{double.class,float.class},reach,1F);
                if(hit==null || !"BLOCK".equals(Reflect.get(hit,"field_72313_a","typeOfHit").toString())) continue;
                Object side=Reflect.get(hit,"field_178784_b","sideHit");
                if(side==null || "UP".equals(side.toString().toUpperCase(Locale.ROOT)) || "DOWN".equals(side.toString().toUpperCase(Locale.ROOT))) continue;
                Object support=Reflect.call(hit,"func_178782_a","getBlockPos");
                Object target=Reflect.call(support,"func_177972_a","offset",new Class<?>[]{Reflect.type("net.minecraft.util.EnumFacing")},side);
                int x=((Number)Reflect.call(target,"func_177958_n","getX")).intValue();
                int y=((Number)Reflect.call(target,"func_177956_o","getY")).intValue();
                int z=((Number)Reflect.call(target,"func_177952_p","getZ")).intValue();
                if(y!=floorY) continue;
                double r=Math.toRadians(heading), cross=(x+0.5-startX)*Math.cos(r)+(z+0.5-startZ)*Math.sin(r);
                double forward=-(x+0.5-startX)*Math.sin(r)+(z+0.5-startZ)*Math.cos(r);
                if(Math.abs(cross)>0.55 || forward<0) continue;
                if(!(Boolean)Reflect.call(world,"func_175623_d","isAirBlock",new Class<?>[]{Reflect.type("net.minecraft.util.BlockPos")},target)) continue;
                yaw=candidateYaw; pitch=candidatePitch;
                Reflect.set(mc,"field_71476_x","objectMouseOver",hit);
                Reflect.set(mc,"field_71467_ac","rightClickDelayTimer",0);
                Reflect.call(mc,"func_147121_ag","rightClickMouse");
                if(!(Boolean)Reflect.call(world,"func_175623_d","isAirBlock",new Class<?>[]{Reflect.type("net.minecraft.util.BlockPos")},target)) failedPlacements=0;
                else if(++failedPlacements>=4) abort("MC Telly：放置未成功，已停止。");
                return;
            }
        }
        rotate(yaw,pitch);
    }

    private void rotate(float y,float p) throws Exception {
        Reflect.set(player,"field_70177_z","rotationYaw",y);
        Reflect.set(player,"field_70125_A","rotationPitch",Math.min(85,Math.max(-85,p)));
    }
    private int code(Object binding) throws Exception { return ((Number)Reflect.call(binding,"func_151463_i","getKeyCode")).intValue(); }
    private boolean key(int code) throws Exception {
        if(code<0) return (Boolean)Reflect.call(Reflect.type("org.lwjgl.input.Mouse"),"isButtonDown","isButtonDown",new Class<?>[]{int.class},code+100);
        if(code==0) return false;
        return (Boolean)Reflect.call(Reflect.type("org.lwjgl.input.Keyboard"),"isKeyDown","isKeyDown",new Class<?>[]{int.class},code);
    }
    private void abort(String reason) { stop(); blockedUntilRelease=true; message(reason); }
    private void stop() {
        if(!running) return;
        running=false; frame=null;
        if(bindings!=null) for(Object binding:bindings) {
            try { Reflect.set(binding,"field_74513_e","pressed",key(code(binding))); } catch(Exception ignored) { }
        }
    }
    private void message(String text) {
        try {
            Object p=Reflect.get(mc,"field_71439_g","thePlayer");
            if(p==null)return;
            Object msg=Reflect.type("net.minecraft.util.ChatComponentText").getConstructor(String.class).newInstance(text);
            // Local HUD message, never transmitted to server chat.
            Reflect.call(p,"func_145747_a","addChatMessage",new Class<?>[]{Reflect.type("net.minecraft.util.IChatComponent")},msg);
        } catch(Exception ignored) { }
    }
}
