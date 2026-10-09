package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;

/** Three existing room cores own bounded fantasy hazards; no fluids, scans or tickets. */
public final class ChenshaEnvironment {
    public static boolean validCore(String room,BlockPos core,BlockPos origin) {
        return switch(room) {
            case "shendao","mercury","imperial_vault" -> origin.offset(ChenshaPiece.core(room)).equals(core);
            default -> false;
        };
    }
    private static boolean between(double value,double min,double max) {return value>=min&&value<max;}
    /** Only feet touching an authored surface are exposed. Platforms and the ladder stay safe. */
    public static String contactZone(ServerLevel level,BlockPos origin,String room,Player player) {
        if(!player.isAlive()||player.isCreative()||player.isSpectator())return "";
        double x=player.getX()-origin.getX(),y=player.getY()-origin.getY(),z=player.getZ()-origin.getZ();
        String zone="";
        if(room.equals("shendao")&&between(x,30,35)&&between(z,40,43)&&between(y,44,45.1))zone="poison_pit";
        else if(room.equals("mercury")&&between(x,5,59)&&between(z,33,89)&&between(y,19,19.75))zone="mercury_channel";
        else if(room.equals("mercury")&&between(x,50,54)&&between(z,85,87)&&between(y,25,25.75))zone="mercury_fall";
        else if(room.equals("imperial_vault")&&between(x,8,56)&&between(z,2,30)&&between(y,1,1.75))zone="mercury_moat";
        if(zone.isEmpty())return "";
        var floor=BlockPos.containing(player.getX(),player.getY()-.05,player.getZ());
        if(!level.hasChunkAt(floor))return "";
        var surface=level.getBlockState(floor);
        if(zone.equals("poison_pit"))return surface.is(Blocks.GREEN_STAINED_GLASS)?zone:"";
        return surface.is(Blocks.LIGHT_BLUE_STAINED_GLASS)?zone:"";
    }
    public static boolean tick(ServerLevel level,BlockPos origin,String room,DungeonRoomController state,long time) {
        // Only loaded players near this footprint; at most 64 records per room.
        var present=new java.util.HashSet<java.util.UUID>();boolean changed=false;
        for(var player:level.players()) {
            if(player.distanceToSqr(origin.getX()+32,origin.getY()+32,origin.getZ()+48)>96*96)continue;
            present.add(player.getUUID());
            changed|=contact(level,origin,room,state,player,time);
        }
        changed|=state.retainExposures(present);
        if(room.equals("mercury")&&time%10==0) {
            var fall=origin.offset(52,28,86);
            if(level.hasChunkAt(fall)&&level.players().stream().anyMatch(p->!p.isSpectator()&&p.distanceToSqr(fall.getX()+.5,fall.getY(),fall.getZ()+.5)<24*24)) {
                // A fixed particle ribbon hides the breakable wall; no spreading liquid blocks.
                level.sendParticles(ParticleTypes.END_ROD,fall.getX()+.5,fall.getY()+.5,fall.getZ()+.5,12,1.2,2,.12,.015);
                level.sendParticles(ParticleTypes.SOUL,fall.getX()+.5,origin.getY()+25.1,fall.getZ(),4,1.2,.1,.5,.01);
            }
        }
        return changed;
    }
    public static boolean contact(ServerLevel level,BlockPos origin,String room,DungeonRoomController state,Player player,long time) {
        String zone=contactZone(level,origin,room,player);
        if(zone.isEmpty())return state.clearExposure(player.getUUID());
        var exposure=state.exposure(player.getUUID(),true);
        if(exposure==null)return false;
        var action=exposure.tick(zone,time);
        if(action==DungeonExposure.Contact.WARNING) {
            player.displayClientMessage(Component.translatable(zone.equals("poison_pit")?
                "message.dynasty.dungeon.poison_warning":"message.dynasty.dungeon.mercury_warning"),true);
            level.playSound(null,player.blockPosition(),SoundEvents.SOUL_ESCAPE,SoundSource.BLOCKS,.6F,.65F);
        } else if(action==DungeonExposure.Contact.DAMAGE) {
            player.hurt(level.damageSources().magic(),2);
            if(zone.equals("poison_pit"))player.addEffect(new MobEffectInstance(MobEffects.POISON,40,0));
        }
        if(!zone.isEmpty()&&time%10==0)level.sendParticles(ParticleTypes.SOUL,player.getX(),player.getY()+.1,player.getZ(),3,.25,.1,.25,.01);
        return true;
    }
    private ChenshaEnvironment(){}
}
