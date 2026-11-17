package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;

/** Ceiling-anchored blade. Visual stroke and its only server contact share dimensions. */
public final class GuillotineTrap {
    public static final int CONTACT_TICK=2;
    public static final double WIDTH=2.75,THICKNESS=.375,HEIGHT=.75,RAISED=-.875,LOWERED=-3;
    private GuillotineTrap(){}

    public static double bladeY(int phase,double progress){
        double p=Math.max(0,Math.min(1,progress));
        if(phase==1)return RAISED+Math.sin(p*Math.PI*8)*.015;
        if(phase==2){double fall=Math.min(1,p*2);return RAISED+(LOWERED-RAISED)*fall*fall;}
        if(phase==3)return LOWERED+(RAISED-LOWERED)*p;
        return RAISED;
    }
    /** Full swept blade volume during the two-tick fall, not the entire corridor. */
    public static AABB sweep(BlockPos anchor,Direction facing){
        double halfX=facing.getAxis()==Direction.Axis.Z?WIDTH/2:THICKNESS/2;
        double halfZ=facing.getAxis()==Direction.Axis.Z?THICKNESS/2:WIDTH/2;
        return new AABB(anchor.getX()+.5-halfX,anchor.getY()+LOWERED,anchor.getZ()+.5-halfZ,
            anchor.getX()+.5+halfX,anchor.getY()+RAISED+HEIGHT,anchor.getZ()+.5+halfZ);
    }
    public static AABB renderBounds(BlockPos anchor){return new AABB(anchor).inflate(1,0,1).expandTowards(0,-3.1,0);}
    public static boolean clear(ServerLevel level,BlockPos anchor,Direction facing){
        AABB sweep=sweep(anchor,facing);
        if(!level.getWorldBorder().isWithinBounds(sweep)||sweep.minY<level.getMinBuildHeight())return false;
        for(int x=(int)Math.floor(sweep.minX)>>4;x<=(int)Math.floor(sweep.maxX)>>4;x++)
            for(int z=(int)Math.floor(sweep.minZ)>>4;z<=(int)Math.floor(sweep.maxZ)>>4;z++)
                if(level.getChunkSource().getChunkNow(x,z)==null)return false;
        // A newly placed obstruction stops the blade instead of damaging through blocks.
        return !level.getBlockCollisions(null,sweep).iterator().hasNext();
    }
    public static void warning(ServerLevel level,DungeonMechanismBlockEntity be,boolean first){
        var pos=be.getBlockPos();var facing=be.getBlockState().getValue(DungeonMechanismBlock.FACING);
        var area=sweep(pos,facing);double y=pos.getY()+LOWERED+.06;
        for(int i=0;i<7;i++){
            double along=-WIDTH/2+WIDTH*i/6;
            level.sendParticles(ParticleTypes.FLAME,pos.getX()+.5+(facing.getAxis()==Direction.Axis.Z?along:0),y,
                pos.getZ()+.5+(facing.getAxis()==Direction.Axis.X?along:0),1,0,0,0,0);
        }
        if(first){
            level.playSound(null,pos,SoundEvents.CHAIN_BREAK,SoundSource.BLOCKS,.6F,.6F);
            for(var p:level.getEntitiesOfClass(Player.class,area.inflate(3),p->p.isAlive()&&!p.isCreative()&&!p.isSpectator()))
                p.displayClientMessage(Component.translatable("message.dynasty.dungeon.guillotine_warning"),true);
        }
    }
    public static void contact(ServerLevel level,DungeonMechanismBlockEntity be){
        var pos=be.getBlockPos();var facing=be.getBlockState().getValue(DungeonMechanismBlock.FACING);
        if(!clear(level,pos,facing))return;
        for(var p:level.getEntitiesOfClass(Player.class,sweep(pos,facing),p->p.isAlive()&&!p.isCreative()&&!p.isSpectator()))
            p.hurt(level.damageSources().generic(),DungeonTrapProfile.GUILLOTINE.damage);
        level.playSound(null,pos.below(3),SoundEvents.ANVIL_LAND,SoundSource.BLOCKS,.7F,.65F);
        level.sendParticles(ParticleTypes.CRIT,pos.getX()+.5,pos.getY()+LOWERED+.1,pos.getZ()+.5,6,.6,.05,.1,0);
    }
}
