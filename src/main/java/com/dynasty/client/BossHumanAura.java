package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Budgeted, depth-tested client atmosphere. No server actors, sounds, damage or lights. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BossHumanAura {
    private static boolean reviewSuppressed;
    private static int reviewEmissions;
    private static final boolean REVIEW=Boolean.getBoolean("dynasty.bossHumanPresenceQa");
    public static void setReviewSuppressed(boolean suppressed){if(REVIEW){reviewSuppressed=suppressed;reviewEmissions=0;}}
    public static int reviewEmissions(){return reviewEmissions;}
    static boolean suppressed(){return reviewSuppressed;}
    private static int kind(String id){return switch(id){case "nine_heaven_general"->0;case "dragon_king"->1;case "dragon_emperor"->2;default->-1;};}

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(event.phase!=TickEvent.Phase.END||reviewSuppressed)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.isPaused()||mc.level.getGameTime()%4!=0)return;
        int budget=16;
        for(var mob:mc.level.getEntitiesOfClass(Mob.class,mc.player.getBoundingBox().inflate(36),m->!m.isInvisible()&&!m.isDeadOrDying())){
            ResourceLocation key=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
            if(key==null||!key.getNamespace().equals("dynasty"))continue;
            int k=kind(key.getPath());if(k<0)continue;
            if(k==0){
                int emitted=TianjiangAura.emit(mob,budget);budget-=emitted;
                if(REVIEW)reviewEmissions+=emitted;
                if(budget<=0)break;
                continue;
            }
            int emitted=RoyalBossAura.emit(mob,budget,k==1);budget-=emitted;
            if(REVIEW)reviewEmissions+=emitted;
            if(budget<=0)break;
        }
    }

    static void draw(PoseStack pose,MultiBufferSource buffers,Mob mob,String id,float partial,boolean casting){
        int k=kind(id);if(k<0||reviewSuppressed||mob.isInvisible()||mob.isDeadOrDying())return;
        if(k==0){TianjiangAura.draw(pose,buffers,mob,partial,casting);return;}
        RoyalBossAura.draw(pose,buffers,mob,partial,casting,k==1);
    }
}
