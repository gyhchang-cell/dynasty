package com.dynasty.ritual.client;

import com.dynasty.ritual.ZhenyuanSovereign;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;

/** Bounded client particles and reversible camera/audio; no gameplay authority on the client. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class ZhenyuanArrivalEffects {
    private static ZhenyuanSovereign focus;
    private static SoundInstance music;
    private static int last=-1;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        ZhenyuanSovereign next=null;
        if(mc.level!=null&&mc.player!=null&&mc.player.isAlive())
            for(var entity:mc.level.entitiesForRendering()) if(entity instanceof ZhenyuanSovereign b&&b.isAlive()&&b.distanceToSqr(mc.player)<88*88
                    &&(next==null||b.distanceToSqr(mc.player)<next.distanceToSqr(mc.player)))next=b;
        if(focus!=next) { stopMusic();focus=next;last=-1; }
        if(focus==null)return;
        if(focus.combatReady()) {
            if(focus.isNoAi()) {stopMusic();return;}
            if(music==null) {
                mc.getMusicManager().stopPlaying();
                music=new SimpleSoundInstance(new net.minecraft.resources.ResourceLocation("dynasty","zhenyuan_battle"),SoundSource.MUSIC,.65F,1,
                        SoundInstance.createUnseededRandom(),true,0,SoundInstance.Attenuation.NONE,0,0,0,true);
                mc.getSoundManager().play(music);
            }
            return;
        }
        mc.getMusicManager().stopPlaying();
        int t=focus.introTick();if(!focus.introRunning()||t==last)return;int previous=last;last=t;
        double x=focus.getX(),y=focus.getY(),z=focus.getZ();
        var gold=new DustParticleOptions(new Vector3f(.78F,.49F,.13F),1.8F);
        var dark=new DustParticleOptions(new Vector3f(.035F,.025F,.025F),2.6F);
        var red=new DustParticleOptions(new Vector3f(.28F,.025F,.025F),1.8F);
        if(t<60) {
            for(int i=0;i<5;i++) {
                double a=t*.09+i*Math.PI*.4;
                mc.level.addParticle(gold,x+Math.cos(a)*1.8,y+1.6+Math.sin(a*2)*.6,z+Math.sin(a)*1.8,0,.01,0);
            }
            // Portal residue remains behind the safe arrival point, not on the boss.
            for(int i=0;i<Math.max(1,(60-t)/8);i++)mc.level.addParticle(ParticleTypes.REVERSE_PORTAL,x+(mc.level.random.nextDouble()-.5)*3,y+mc.level.random.nextDouble()*3,z+30,0,.03,0);
        }
        if(t>=60&&t<145) for(int i=0;i<14;i++) {
            double a=t*.13+i*Math.PI*2/14,r=3.5+(i%3)*.8;
            mc.level.addParticle(i%3==0?gold:i%3==1?dark:red,x+Math.cos(a)*r,y+.3+(i%6)*.5,z+Math.sin(a)*r,-Math.cos(a)*.14,.04,-Math.sin(a)*.14);
        }
        for(int key:new int[]{54,230}) if(t>=key&&t<key+24) {
            double r=(t-key)*.65+.8;
            for(int i=0;i<48;i++) {
                double a=i*Math.PI/24;
                mc.level.addParticle(gold,x+Math.cos(a)*r,y+.12,z+Math.sin(a)*r,Math.cos(a)*.08,.015,Math.sin(a)*.08);
                if(key==230&&i%3==0)mc.level.addParticle(ParticleTypes.POOF,x+Math.cos(a)*r,y+.15,z+Math.sin(a)*r,0,.03,0);
            }
        }
        if(previous>=0&&previous<190&&t>=190&&t<200) mc.level.playLocalSound(x,y+4,z,net.minecraft.sounds.SoundEvent.createVariableRangeEvent(new net.minecraft.resources.ResourceLocation("dynasty","zhenyuan_voice")),SoundSource.HOSTILE,2,1,false);
    }
    private static void stopMusic() {if(music!=null)Minecraft.getInstance().getSoundManager().stop(music);music=null;}
    @SubscribeEvent public static void camera(ViewportEvent.ComputeCameraAngles event) {
        var mc=Minecraft.getInstance();if(focus==null||mc.level!=focus.level()||!focus.introRunning())return;
        float t=focus.introTick()+mc.getFrameTime(),strength=0;
        for(int key:new int[]{12,32,54,190,230})if(t>=key&&t<key+12)strength=Math.max(strength,(1-(t-key)/12)*(key==230?.85F:key==54?.55F:.25F));
        event.setPitch(event.getPitch()+(float)Math.sin(t*1.7)*strength);
        event.setRoll(event.getRoll()+(float)Math.sin(t*2.1)*strength*.6F);
    }
}
