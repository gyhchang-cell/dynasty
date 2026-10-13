package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import java.util.*;

/** Server-owned use sessions. Requests never supply damage, a victim, a position or a clock. */
public interface ArtifactAbility {
    record AttackProfile(CombatGeometry.Shape shape,double range,double width,double angle,double height) {
        public List<net.minecraft.world.entity.LivingEntity> targets(ServerPlayer p,Vec3 origin,Vec3 facing) {
            if(!loaded(p.serverLevel(),new net.minecraft.world.phys.AABB(origin,origin).inflate(range+width*.5,height,range+width*.5)))return List.of();
            return CombatGeometry.query(p.serverLevel(),origin,facing,shape,range,width,angle,height,
                e->e!=p&&!e.isAlliedTo(p)&&!(e instanceof net.minecraft.world.entity.player.Player other&&(other.isCreative()||!p.canHarmPlayer(other)))).stream().limit(16).toList();
        }
    }
    boolean swing(ServerPlayer p,ItemStack actual);
    boolean release(ServerPlayer p,ItemStack actual,int elapsed);
    default void tickUse(ServerPlayer p,ItemStack actual,int elapsed){}
    default void startUse(ServerPlayer p,ItemStack actual){}
    default void stopUse(ServerPlayer p,ItemStack actual){}
    default double gripOffsetMetres(){return 0;}
    default net.minecraft.world.item.UseAnim useAnimation(){return net.minecraft.world.item.UseAnim.BOW;}
    record Session(ItemStack stack,long born,net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dimension,ArtifactAbility ability) {}
    Map<UUID,Session> USES=new HashMap<>();
    static boolean loaded(net.minecraft.server.level.ServerLevel w,net.minecraft.world.phys.AABB b){
        if(!Double.isFinite(b.minX+b.maxX+b.minY+b.maxY+b.minZ+b.maxZ)||b.getXsize()>64||b.getZsize()>64||b.minY<w.getMinBuildHeight()||b.maxY>=w.getMaxBuildHeight()||!w.getWorldBorder().isWithinBounds(b))return false;
        for(int x=net.minecraft.util.Mth.floor(b.minX)>>4;x<=net.minecraft.util.Mth.floor(b.maxX)>>4;x++)for(int z=net.minecraft.util.Mth.floor(b.minZ)>>4;z<=net.minecraft.util.Mth.floor(b.maxZ)>>4;z++)if(!w.hasChunkAt(new net.minecraft.core.BlockPos(x<<4,0,z<<4)))return false;return true;
    }
    static boolean valid(ServerPlayer p,ItemStack actual) {
        return p!=null&&p.isAlive()&&!p.isSpectator()&&!p.isSleeping()&&p.getMainHandItem()==actual
            &&actual.getItem() instanceof ArtifactItem&&!p.getCooldowns().isOnCooldown(actual.getItem());
    }
    static boolean begin(ServerPlayer p,ItemStack actual) {
        if(!valid(p,actual)||p.isUsingItem())return false;
        var ability=((ArtifactItem)actual.getItem()).ability();forget(p);p.getPersistentData().remove("DynastyZhanluGuardSpent");USES.put(p.getUUID(),new Session(actual,p.serverLevel().getGameTime(),p.level().dimension(),ability));ability.startUse(p,actual);return true;
    }
    static boolean finish(ServerPlayer p,ItemStack actual) {
        var session=USES.remove(p.getUUID());long now=p.serverLevel().getGameTime();
        if(session==null)return false;
        try{if(session.stack()!=actual||session.dimension()!=p.level().dimension()||now<session.born()||now-session.born()>72000||!valid(p,actual))return false;return session.ability().release(p,actual,(int)(now-session.born()));}finally{session.ability().stopUse(p,session.stack());}
    }
    static void forget(ServerPlayer p){var session=USES.remove(p.getUUID());if(session!=null)session.ability().stopUse(p,session.stack());}
    static void forget(UUID id){var session=USES.remove(id);if(session!=null&&session.stack().getTag()!=null)session.stack().getTag().remove("DynastyZhanluStanceAt");}
}
