package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.core.*;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
import java.util.*;

/** Three actual server objectives, each player's own clock. No packet, force-loaded chunk or enemy puppet. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class TaiqingTrials {
    public static final int[][] PATH={{6,-6},{6,-3},{3,-3},{3,0},{3,3}};
    private static final Map<ServerPlayer,Session> SESSIONS=new WeakHashMap<>();
    static int stage(ServerPlayer p){var s=SESSIONS.get(p);return s==null?0:s.stage;}
    public static void cancel(ServerPlayer p){SESSIONS.remove(p);ZhanluTrialRewards.cancel(p);}
    private static final class Session {
        final BlockPos swordCase;
        long last=-1,ringBorn=-1;
        int stage=1,hold,waypoint,spent;
        Vec3 previous;
        Session(BlockPos p){swordCase=p.immutable();}
    }
    public static boolean begin(ServerPlayer p,BlockPos swordCase){
        if(SESSIONS.containsKey(p)||SESSIONS.size()>=16||!loaded(p,swordCase)||!p.serverLevel().getBlockState(swordCase).is(TaiqingContent.SWORD_CASE.get())||!ZhanluTrialRewards.begin(p,swordCase))return false;
        SESSIONS.put(p,new Session(swordCase));return true;
    }
    private static boolean loaded(ServerPlayer p,BlockPos c){return ArtifactAbility.loaded(p.serverLevel(),new AABB(c).inflate(12,2,12));}
    public static void discover(ServerPlayer p){
        var w=p.serverLevel();if(w.dimension()!=Level.OVERWORLD||p.isSpectator())return;
        var registry=w.registryAccess().registryOrThrow(Registries.STRUCTURE);var id=new ResourceLocation("dynasty","taiqing_hidden_temple");
        var starts=new LinkedHashSet<net.minecraft.world.level.levelgen.structure.StructureStart>();var origin=p.chunkPosition();int budget=64;
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
            var at=new ChunkPos(origin.x+dx,origin.z+dz);if(!w.hasChunk(at.x,at.z))continue;
            var c=w.getChunkSource().getChunk(at.x,at.z,net.minecraft.world.level.chunk.ChunkStatus.STRUCTURE_REFERENCES,false);if(c==null)continue;
            c.getAllStarts().forEach((type,start)->{if(id.equals(registry.getKey(type)))starts.add(start);});
            for(var refs:c.getAllReferences().entrySet())if(id.equals(registry.getKey(refs.getKey())))for(long packed:refs.getValue()){
                if(budget--<=0)break;var owner=new ChunkPos(packed);if(!w.hasChunk(owner.x,owner.z))continue;
                var source=w.getChunkSource().getChunk(owner.x,owner.z,net.minecraft.world.level.chunk.ChunkStatus.STRUCTURE_STARTS,false);
                if(source!=null){var start=source.getStartForStructure(refs.getKey());if(start!=null)starts.add(start);}
            }
        }
        for(var start:starts)if(start.isValid()&&start.getBoundingBox().isInside(p.blockPosition()))for(var piece:start.getPieces())if(piece instanceof TaiqingTemplePiece temple){
            var at=temple.swordCase();if(w.hasChunkAt(at)&&w.getBlockState(at).is(TaiqingContent.SWORD_CASE.get()))ZhanluTrialRewards.registerSwordCase(w,at);
        }
    }
    private static Vec3 point(Session s,int x,int z){return Vec3.atBottomCenterOf(s.swordCase.offset(x,0,z));}
    private static boolean pad(ServerPlayer p,Vec3 centre,double radius){return p.position().subtract(centre).multiply(1,0,1).lengthSqr()<=radius*radius&&p.getY()>=centre.y-.06&&p.getY()<=centre.y+1.5;}
    private static void fail(ServerPlayer p){if(SESSIONS.remove(p)!=null){ZhanluTrialRewards.cancel(p);p.displayClientMessage(Component.translatable("message.dynasty.taiqing_failed"),false);}}
    private static void advance(ServerPlayer p,Session s){
        if(!ZhanluTrialRewards.completeStage(p,s.swordCase,s.stage)){fail(p);return;}
        s.stage++;s.hold=0;s.previous=null;s.ringBorn=-1;s.spent=0;
        if(s.stage==4){SESSIONS.remove(p);var state=p.serverLevel().getBlockState(s.swordCase);if(state.is(TaiqingContent.SWORD_CASE.get()))p.serverLevel().setBlock(s.swordCase,state.setValue(TaiqingSwordCase.STAGE,1),3);p.displayClientMessage(Component.translatable("message.dynasty.taiqing_ready"),false);}
        else p.displayClientMessage(Component.translatable("message.dynasty.taiqing_stage"+s.stage),false);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        if(p.serverLevel().getGameTime()%80==Math.floorMod(p.getId()+47,80))discover(p);
        var s=SESSIONS.get(p);if(s==null)return;long now=p.serverLevel().getGameTime();
        if(s.last==now)return;
        if(!ZhanluTrialRewards.active(p,s.swordCase)||!loaded(p,s.swordCase)||!p.serverLevel().getBlockState(s.swordCase).is(TaiqingContent.SWORD_CASE.get())
                ||s.last>=0&&(now<s.last||now-s.last!=1)||s.previous!=null&&p.position().distanceToSqr(s.previous)>2.25){fail(p);return;}
        s.last=now;
        if(s.stage==1){
            var centre=point(s,-6,-6);boolean stationary=s.previous==null||p.position().distanceToSqr(s.previous)<.001;
            if(p.onGround()&&pad(p,centre,.7)&&stationary)s.hold++;else s.hold=0;
            if(s.hold>=40){advance(p,s);return;}
        }else if(s.stage==2){
            if(s.waypoint>0&&(!p.onGround()||!p.serverLevel().getBlockState(p.blockPosition().below()).is(Blocks.CALCITE))){fail(p);return;}
            var next=PATH[s.waypoint];if(p.onGround()&&pad(p,point(s,next[0],next[1]),.65)){s.waypoint++;if(s.waypoint==PATH.length){advance(p,s);return;}}
        }else if(s.stage==3){
            var centre=point(s,-6,6);
            if(!pad(p,centre,3)||!p.getMainHandItem().isEmpty()||!p.getOffhandItem().isEmpty()){s.ringBorn=-1;s.spent=0;}
            else{
                if(s.ringBorn<0)s.ringBorn=now;long age=now-s.ringBorn;int pulse=(int)Math.min(3,age/30);var f=new Vec3(Math.sin(pulse*Math.PI/2),0,Math.cos(pulse*Math.PI/2));
                //20-tick tell and one actual pulse per sector; later packets/ticks never replay it.
                if(age%30<20&&age%5==0)for(int i=0;i<6;i++){
                    double a=pulse*Math.PI/2+Math.toRadians(-45+90D*i/5);var at=centre.add(Math.sin(a)*3.2,.12,Math.cos(a)*3.2);
                    p.serverLevel().sendParticles(new DustParticleOptions(new Vector3f(.78F,.28F,.22F),.8F),at.x,at.y,at.z,1,0,0,0,0);
                }
                if(age%30==20&&(s.spent&(1<<pulse))==0){s.spent|=1<<pulse;
                    if(p.getBoundingBox().minY<centre.y+.5&&CombatGeometry.contains(centre,f,CombatGeometry.Shape.SECTOR,3.2,0,90,1,p.getBoundingBox())
                            &&p.serverLevel().clip(new ClipContext(centre.add(0,.3,0),p.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p)).getType()==HitResult.Type.MISS)p.hurt(p.damageSources().magic(),1);
                    if(!ZhanluTrialRewards.active(p,s.swordCase)){fail(p);return;}
                }
                if(age>=120&&s.spent==15){advance(p,s);return;}
            }
        }
        s.previous=p.position();
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void damage(LivingDamageEvent e){if(e.getAmount()>0&&e.getEntity() instanceof ServerPlayer p)fail(p);}
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void attack(AttackEntityEvent e){if(e.getEntity() instanceof ServerPlayer p&&SESSIONS.containsKey(p)){e.setCanceled(true);fail(p);}}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void offensiveDamage(LivingHurtEvent e){if(e.getAmount()>0&&!e.getSource().is(net.minecraft.world.damagesource.DamageTypes.THORNS)&&e.getSource().getEntity() instanceof ServerPlayer p&&SESSIONS.containsKey(p))fail(p);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)SESSIONS.remove(p);}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){if(e.getEntity() instanceof ServerPlayer p)SESSIONS.remove(p);}
    private TaiqingTrials(){}
}
