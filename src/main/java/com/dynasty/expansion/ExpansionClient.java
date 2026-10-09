package com.dynasty.expansion;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ExpansionClient {
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers event) {
        SecondaryMobs.TYPES.values().forEach(t->event.registerEntityRenderer(t.get(),Renderer::new));
    }
    @SubscribeEvent public static void setup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(()-> {
            for(var item:java.util.List.of(ExpansionContent.REPEATING,ExpansionContent.SIEGE)) {
                net.minecraft.client.renderer.item.ItemProperties.register(item.get(),new ResourceLocation("pull"),(s,l,e,seed)->e!=null && e.getUseItem()==s && !net.minecraft.world.item.CrossbowItem.isCharged(s)?Math.min(1F,(s.getUseDuration()-e.getUseItemRemainingTicks())/(float)net.minecraft.world.item.CrossbowItem.getChargeDuration(s)):0F);
                net.minecraft.client.renderer.item.ItemProperties.register(item.get(),new ResourceLocation("pulling"),(s,l,e,seed)->e!=null && e.getUseItem()==s && e.isUsingItem() && !net.minecraft.world.item.CrossbowItem.isCharged(s)?1F:0F);
                net.minecraft.client.renderer.item.ItemProperties.register(item.get(),new ResourceLocation("charged"),(s,l,e,seed)->net.minecraft.world.item.CrossbowItem.isCharged(s)?1:0);
            }
        });
    }
    private static final class Model extends GeoModel<SecondaryMob> {
        @Override public ResourceLocation getModelResource(SecondaryMob m) {return new ResourceLocation("dynasty","geo/secondary/"+m.spec.id()+".geo.json");}
        @Override public ResourceLocation getAnimationResource(SecondaryMob m) {return new ResourceLocation("dynasty","animations/secondary/"+m.spec.id()+".animation.json");}
        @Override public ResourceLocation getTextureResource(SecondaryMob m) {
            String atlas=switch(m.spec.family()) {case "human"->m.spec.id().equals("bandit_thug")?"assassin":"minister";case "water"->"merfolk";case "fly"->m.spec.id().equals("wooden_magpie")?"terracotta_warrior":"phoenix";case "ghost"->"soul_soldier";default->m.spec.id().equals("red_fox")?"nine_tailed_fox":"nian_beast";};
            return new ResourceLocation("dynasty","textures/entity/"+atlas+".png");
        }
    }
    private static final class Renderer extends GeoEntityRenderer<SecondaryMob> {
        Renderer(EntityRendererProvider.Context ctx) {super(ctx,new Model());shadowRadius=.45F;}
    }
    private static long budgetTick=-1;private static int emitted;
    public static void feedback(CombatFeedback p) {
        var level=Minecraft.getInstance().level;if(level==null)return;
        if(level.getGameTime()!=budgetTick){budgetTick=level.getGameTime();emitted=0;}
        if(emitted>=128)return;
        if(p.type()==14) {
            int count=Math.min(32,128-emitted);emitted+=count;
            for(int i=0;i<count;i++){double f=(double)i/Math.max(1,count-1);level.addParticle(ParticleTypes.CRIT,p.sx()+(p.x()-p.sx())*f,p.sy()+(p.y()-p.sy())*f,p.sz()+(p.z()-p.sz())*f,0,0,0);}
            return;
        }
        if(p.type()==CombatFeedback.FIRE_RING || p.type()==CombatFeedback.CINNABAR || p.type()==CombatFeedback.SMALL_THUNDER) {
            int count=Math.min(40,128-emitted);emitted+=count;
            for(int i=0;i<count;i++) {
                double a=i*Math.PI*2/Math.max(1,count);
                if(p.type()==CombatFeedback.SMALL_THUNDER) {
                    double t=i/(double)Math.max(1,count-1),jitter=Math.sin(i*2.4)*.16;
                    level.addParticle(ParticleTypes.ELECTRIC_SPARK,p.x()+jitter,p.y()+2.5-t*2.5,p.z()-jitter,0,-.08,0);
                } else {
                    boolean fire=p.type()==CombatFeedback.FIRE_RING;
                    net.minecraft.core.particles.ParticleOptions particle=fire?ParticleTypes.FLAME:
                        new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.85F,.1F,.06F),1.3F);
                    double radius=fire?2.8:1.5;
                    level.addParticle(particle,p.x()+Math.cos(a)*radius,p.y()-.4,p.z()+Math.sin(a)*radius,Math.cos(a)*.12,.08,Math.sin(a)*.12);
                }
            }
            level.playLocalSound(p.x(),p.y(),p.z(),p.type()==CombatFeedback.SMALL_THUNDER?SoundEvents.LIGHTNING_BOLT_IMPACT:SoundEvents.FIRECHARGE_USE,SoundSource.PLAYERS,.35F,1.4F,false);
            return;
        }
        var type=switch(p.type()) {case CombatFeedback.THUNDER->ParticleTypes.ELECTRIC_SPARK;case CombatFeedback.WATER->ParticleTypes.BUBBLE;case CombatFeedback.HEAL->ParticleTypes.HAPPY_VILLAGER;case CombatFeedback.CRITICAL,CombatFeedback.STAR,CombatFeedback.PERFECT->ParticleTypes.CRIT;case CombatFeedback.ARMOR->ParticleTypes.ASH;default->ParticleTypes.ENCHANTED_HIT;};
        int count=p.type()==CombatFeedback.STAR?7:p.type()==CombatFeedback.NORMAL?4:12;
        count=Math.min(count,128-emitted);emitted+=count;
        for(int i=0;i<count;i++){double a=i*Math.PI*2/count;double r=p.type()==CombatFeedback.HEAVY?1.3:.55;level.addParticle(type,p.x()+Math.cos(a)*r,p.y(),p.z()+Math.sin(a)*r,Math.cos(a)*.03,.025,Math.sin(a)*.03);}
        level.playLocalSound(p.x(),p.y(),p.z(),p.type()==CombatFeedback.BLOCK||p.type()==CombatFeedback.PERFECT?SoundEvents.SHIELD_BLOCK:p.type()==CombatFeedback.HEAVY?SoundEvents.PLAYER_ATTACK_STRONG:SoundEvents.PLAYER_ATTACK_CRIT,SoundSource.PLAYERS,.25F,p.type()==CombatFeedback.PERFECT?1.5F:1F,false);
    }
    @Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
    public static final class Trails {
        @SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.ClientTickEvent e) {
            var level=Minecraft.getInstance().level;var player=Minecraft.getInstance().player;
            if(e.phase!=net.minecraftforge.event.TickEvent.Phase.END || level==null || player==null || level.getGameTime()%2!=0)return;
            int count=0;for(var entity:level.entitiesForRendering()) {
                if(count>=32)break;
                if(entity instanceof net.minecraft.world.entity.projectile.AbstractArrow arrow && arrow.getOwner() instanceof net.minecraft.world.entity.LivingEntity owner && arrow.distanceToSqr(player)<1024 && arrow.getDeltaMovement().lengthSqr()>.01) {
                    String id=EquipmentBehaviors.id(owner.getMainHandItem());
                    if(id.contains("bow") || id.contains("gong")) {level.addParticle(ParticleTypes.END_ROD,arrow.getX(),arrow.getY(),arrow.getZ(),0,0,0);count++;}
                }
            }
        }
    }
    private ExpansionClient() { }
}
