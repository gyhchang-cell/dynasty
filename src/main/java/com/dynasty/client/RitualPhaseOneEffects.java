package com.dynasty.client;

import com.dynasty.ritual.ZhenyuanNodeBlockEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Local-only reversible cinema. Never changes saved options, player abilities or world time. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class RitualPhaseOneEffects {
    private static ZhenyuanNodeBlockEntity focus;
    private static float audio=1;
    public static void observe(ZhenyuanNodeBlockEntity node) {
        var mc=Minecraft.getInstance();
        if(mc.player==null||mc.level!=node.getLevel()||node.getSlot()!=4)return;
        if(focus==null||!valid()||distance(node)<distance(focus))focus=node;
    }
    private static double distance(ZhenyuanNodeBlockEntity n) { return Minecraft.getInstance().player.distanceToSqr(Vec3.atCenterOf(n.getBlockPos())); }
    private static boolean valid() {
        var mc=Minecraft.getInstance();
        return focus!=null&&mc.player!=null&&mc.player.isAlive()&&mc.level==focus.getLevel()&&!focus.isRemoved()&&focus.getStage()<2
                &&mc.level.hasChunkAt(focus.getBlockPos())&&distance(focus)<64*64;
    }
    private static String stage(){return valid()?focus.timeline().getString("Stage"):"";}
    private static double tick(){var mc=Minecraft.getInstance();return valid()?focus.timeline().getInt("Tick")+focus.timelineAge(mc.level.getGameTime()+mc.getFrameTime()):0;}
    private static boolean participant(){return valid()&&focus.timeline().hasUUID("Owner")&&focus.timeline().getUUID("Owner").equals(Minecraft.getInstance().player.getUUID());}
    @SubscribeEvent public static void clientTick(TickEvent.ClientTickEvent e) {
        if(e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance(); String s=stage();double t=tick();float desired=1;
        if(s.equals("THIRD_OMEN")&&t<10||s.equals("FOURTH_CONVERGENCE")&&t<20)desired=.015f;
        else if(s.equals("FINAL_RITUAL")&&participant())desired=(float)Math.max(.015,1-Math.max(0,t-145)/55);
        if(desired<1||Math.abs(desired-audio)>.002f) {
            audio=desired;
            // In 1.20.1 category volume updates ignore their argument; the listener's master gain does not.
            // Apply transient gain, never write Options. Restoring reads the user's current slider value.
            mc.getSoundManager().updateSourceVolume(SoundSource.MASTER,mc.options.getSoundSourceVolume(SoundSource.MASTER)*audio);
        }
        if(!valid())focus=null;
    }
    @SubscribeEvent public static void camera(ViewportEvent.ComputeCameraAngles e) {
        String s=stage();double t=tick();
        double strength=s.equals("THIRD_OMEN")&&t>=10&&t<32?.35*(1-(t-10)/22):s.equals("FINAL_RITUAL")&&participant()&&t>=170&&t<220?.65*(1-(t-170)/50):0;
        e.setRoll(e.getRoll()+(float)(Math.sin(t*1.9)*strength));
        e.setPitch(e.getPitch()+(float)(Math.sin(t*1.3)*strength*.55));
    }
    @SubscribeEvent public static void fov(ViewportEvent.ComputeFov e) {
        if(stage().equals("FINAL_RITUAL")&&participant()) {
            double a=Math.max(0,Math.min(1,(tick()-170)/40));e.setFOV(e.getFOV()*(1-a*.12));
        }
    }
    @SubscribeEvent public static void overlay(RenderGuiEvent.Post e) {
        if(!stage().equals("FINAL_RITUAL")||!participant())return;
        double t=tick();int alpha=0,rgb=0;
        if(t>=170&&t<180){alpha=(int)(110*(1-(t-170)/10));rgb=0xFFE9BC;}
        else if(t>=215)alpha=(int)(255*Math.min(1,(t-215)/20));
        if(alpha>0)e.getGuiGraphics().fill(0,0,e.getWindow().getGuiScaledWidth(),e.getWindow().getGuiScaledHeight(),alpha<<24|rgb);
    }
}
