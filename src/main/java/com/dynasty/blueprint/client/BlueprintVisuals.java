package com.dynasty.blueprint.client;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
import java.util.LinkedHashMap;
import java.util.UUID;
import java.util.ArrayList;

/** World-space particle hints only; never touches RenderSystem, camera, matrices or player controls. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BlueprintVisuals {
    private record Key(UUID caster, long started) {}
    private static final LinkedHashMap<Key, BlueprintVisualEvent> ACTIVE = new LinkedHashMap<>();
    private static ResourceLocation world;
    private static final ArrayList<Integer> SUPPORTS = new ArrayList<>();
    private static final ArrayList<Integer> SHIELDS = new ArrayList<>();
    private BlueprintVisuals() {}
    public static void accept(BlueprintVisualEvent p) {
        var mc=Minecraft.getInstance();
        if(mc.level==null || !mc.level.dimension().location().equals(p.dimension())) return;
        if(p.cancelled()) {ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()) && e.getKey().started<=p.started());return;}
        if(mc.level.getGameTime()-p.started()>p.duration()) return;
        var key=new Key(p.entityUuid(),p.started());
        if(ACTIVE.containsKey(key)) return;
        ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()));
        while(ACTIVE.size()>=64) ACTIVE.remove(ACTIVE.keySet().iterator().next());
        ACTIVE.put(key,p);
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e) { ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null; }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END) return;
        var mc=Minecraft.getInstance();
        if(mc.level==null) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null;return;}
        var dim=mc.level.dimension().location();
        if(world!=null && !world.equals(dim)) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();} world=dim;
        if(mc.isPaused()) return;
        long now=mc.level.getGameTime();
        int budget=mc.options.particles().get()==ParticleStatus.MINIMAL?8:mc.options.particles().get()==ParticleStatus.DECREASED?24:48;
        // Entity metadata survives tracking/rejoin; the possession beam outlives the brief casting event.
        if(now%10==0) {
            SUPPORTS.clear();SHIELDS.clear();
            for(var entity:mc.level.entitiesForRendering()) {
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.PRIEST && mob.isAlive()
                        && mob.buffTargetId()>=0 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=48*48)
                    if(SUPPORTS.size()<32) SUPPORTS.add(mob.getId());
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.SHIELD && mob.isAlive()
                        && SHIELDS.size()<24 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=24*24)
                    SHIELDS.add(mob.getId());
                if(SUPPORTS.size()>=32 && SHIELDS.size()>=24) break;
            }
        }
        for(int id:SUPPORTS) {
            if(budget<=0 || (now+id)%3!=0 || !(mc.level.getEntity(id) instanceof TemplateMob caster) || !caster.isAlive()) continue;
            if(!(mc.level.getEntity(caster.buffTargetId()) instanceof net.minecraft.world.entity.LivingEntity target)
                    || !target.isAlive() || !(target instanceof TemplateMob linked && linked.isPossessed())
                    || caster.distanceToSqr(target)>16*16) continue;
            int count=Math.min(6,budget);budget-=count;
            var dust=new DustParticleOptions(new Vector3f(.78F,.12F,.19F),.7F);
            for(int i=0;i<count;i++) {
                double u=(i+(now*.06)%1)/count;
                var at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
        for(int id:SHIELDS) {
            if(budget<=0 || (now+id)%10!=0 || !(mc.level.getEntity(id) instanceof TemplateMob mob)
                    || !mob.isAlive() || !mob.onGround() || mob.getDeltaMovement().horizontalDistanceSqr()<.0005) continue;
            var state=mc.level.getBlockState(mob.blockPosition().below());
            if(state.isAir())continue;
            var chips=new BlockParticleOption(ParticleTypes.BLOCK,state);
            for(int i=0;i<2 && budget>0;i++,budget--) {
                double side=i==0?-.24:.24;
                mc.level.addParticle(chips,mob.getX()+side,mob.getY()+.05,mob.getZ(),side*.05,.03,0);
            }
        }
        var iterator=ACTIVE.entrySet().iterator();
        while(iterator.hasNext()) {
            var p=iterator.next().getValue(); var caster=mc.level.getEntity(p.entityId()); long age=now-p.started();
            boolean death=p.key().startsWith("death_");
            if(!p.dimension().equals(dim) || age>p.duration()+4 || age< -20
                    || caster!=null && (!caster.getUUID().equals(p.entityUuid()) || !death && !caster.isAlive())) {iterator.remove();continue;}
            if(caster==null || age<0 || budget<=0 || (now+p.entityId())%3!=0 || mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(caster.position())>48*48)continue;
            if(death) {
                budget-=deathParticles(mc,p,age,budget);
                continue;
            }
            boolean buff=p.key().contains("buff")||p.key().contains("possession");
            var color=buff?new Vector3f(.78F,.12F,.19F):p.key().contains("talisman")?new Vector3f(.12F,.65F,.85F):new Vector3f(.70F,.50F,.24F);
            var dust=new DustParticleOptions(color,.7F);
            var target=mc.level.getEntity(p.targetId());
            int count=Math.min(budget,6); budget-=count;
            double offset=((p.seed()&1023)/1024.0 + age*.08)%1;
            for(int i=0;i<count;i++) {
                Vec3 at;
                if(buff && target!=null) {
                    double u=(i+offset)/count;
                    at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                } else if(age<p.windup()) {
                    double a=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*((i+offset)/count-.5);
                    at=p.origin().add(Math.cos(a)*p.range(),.10,Math.sin(a)*p.range());
                } else {
                    double a=(i+offset)/count*Math.PI*2;
                    at=caster.position().add(Math.cos(a)*.55,.6+age*.007,Math.sin(a)*.55);
                }
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
    }
    private static int deathParticles(Minecraft mc,BlueprintVisualEvent p,long age,int budget) {
        boolean priest=p.key().endsWith("fufa_jijiu"),shield=p.key().endsWith("ludun_jiashi"),sword=p.key().endsWith("zuwu_daoshou");
        if(!(priest && age<18 || shield && age>=188 || sword && age>=40))return 0;
        int count=Math.min(budget,priest?8:4);
        // No visual entities, frame packets or random state to replicate: seed + absolute age is deterministic.
        var random=net.minecraft.util.RandomSource.create(p.seed()^age*0x9e3779b97f4a7c15L);
        for(int i=0;i<count;i++) {
            double x=p.origin().x+(random.nextDouble()-.5)*.8,z=p.origin().z+(random.nextDouble()-.5)*.8;
            double y=p.origin().y+(priest?.6:shield?.4:.15)+random.nextDouble()*(priest?.6:shield?1.2:.25);
            if(priest) {
                if(i%3==0)mc.level.addParticle(ParticleTypes.SOUL_FIRE_FLAME,x,y,z,(x-p.origin().x)*.05,.025,(z-p.origin().z)*.05);
                else mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.PAPER)),x,y,z,(x-p.origin().x)*.2,.06,(z-p.origin().z)*.2);
            } else if(shield) {
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,(i%2==0?Blocks.IRON_BLOCK:Blocks.DARK_OAK_PLANKS).defaultBlockState()),x,y,z,(x-p.origin().x)*.05,.02,(z-p.origin().z)*.05);
            } else mc.level.addParticle(ParticleTypes.SMOKE,x,y,z,0,.012,0);
        }
        return count;
    }
    public static int activeCount() {return ACTIVE.size();}
}
