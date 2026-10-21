package com.dynasty.dungeon;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.elite.EliteContent;
import com.dynasty.blueprint.elite.HammerGuardian;
import com.dynasty.blueprint.elite.Jinwu;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import java.util.UUID;

/** Two authored elites, sharing the existing bounded tomb spawn scheduler and ledger. */
public final class ChenshaGarrisons {
    private static final String OWNER="ChenshaGarrison";
    private ChenshaGarrisons() {}

    // Use chamber landings, not the two-block clear bridge deck. These positions
    // fit the existing 5.6x3.4 and 5.0x4.3 bodies without rescaling either actor.
    public static BlockPos jinwuOffset(){return new BlockPos(32,25,42);}
    public static BlockPos hammerOffset(){return new BlockPos(19,1,15);}
    public static String key(UUID instance,boolean hammer){return "chensha@"+instance+(hammer?":elite_hammer":":elite_jinwu");}

    public static boolean maySpawn(boolean cleared,int produced,int members,long nextSpawn,long now){
        // A missing live lookup never releases an unloaded actor's UUID. A
        // produced-but-empty legacy record also cannot mint a second elite.
        return !cleared&&produced==0&&members==0&&nextSpawn<=now;
    }
    public static boolean inRoom(boolean hammer,int x,int y,int z){
        return hammer?x>=8&&x<=55&&y>=1&&y<=17&&z>=2&&z<=29&&ChenshaVaultLayout.moatRadius(x,z)<=1:
            x>=5&&x<=58&&y>=25&&y<=32&&z>=33&&z<=86;
    }

    /** Caller accounts a true result against BlueprintSpawns' two-actor budget. */
    public static boolean spawnOne(ServerLevel level,BlockPos origin,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL
                ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return false;
        int x=entrant.getX()-origin.getX(),y=entrant.getY()-origin.getY(),z=entrant.getZ()-origin.getZ();
        boolean hammer=inRoom(true,x,y,z);
        if(!hammer&&!inRoom(false,x,y,z))return false;
        String room=hammer?"imperial_vault":"mercury";
        BlockPos corePos=origin.offset(ChenshaPiece.core(room));
        if(level.getChunkSource().getChunkNow(corePos.getX()>>4,corePos.getZ()>>4)==null
                ||!(level.getBlockEntity(corePos) instanceof DungeonMechanismBlockEntity core)
                ||core.kind()!=DungeonMechanismBlock.Kind.CORE||!core.validBinding()||!room.equals(core.roomId())
                ||!core.instance().equals(ChenshaStructure.instanceId(level.getSeed(),origin)))return false;
        UUID instance=core.instance();
        var rooms=DungeonStateStore.get(level);
        if(!rooms.room(instance,"entrance").completed()||hammer&&!rooms.room(instance,"mercury").completed())return false;
        var feet=origin.offset(hammer?hammerOffset():jinwuOffset());
        if(feet.distSqr(entrant)<36||feet.distSqr(entrant)>48*48)return false;
        var state=BlueprintSpawnState.get(level);String key=key(instance,hammer);
        var marker=state.markers.get(key);
        if(marker!=null&&!maySpawn(marker.cleared,marker.produced,marker.members.size(),marker.nextSpawn,level.getGameTime()))return false;
        EntityType<? extends Mob> type=hammer?EliteContent.HAMMER.get():EliteContent.JINWU.get();
        AABB box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!loadedStandingSpace(level,feet,box)||!level.noCollision(null,box)
                ||!level.getEntitiesOfClass(Mob.class,box.inflate(16),e->e.isAlive()&&e.getType()==type).isEmpty())return false;
        Mob actor=type.create(level);if(actor==null)return false;
        actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,hammer?-90:180,0);
        actor.setPersistenceRequired();actor.restrictTo(feet,hammer?10:8);
        if(actor instanceof HammerGuardian guardian)guardian.bindEncounter(key);
        else if(actor instanceof Jinwu guard)guard.bindEncounter(key);
        else return false;
        bindOwner(actor,instance,hammer);
        actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);
        if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}
        marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();
        return true;
    }

    static void bindOwner(Mob actor,UUID instance,boolean hammer){
        var owner=new CompoundTag();owner.putUUID("Instance",instance);owner.putBoolean("Hammer",hammer);
        actor.getPersistentData().put(OWNER,owner);
    }

    static boolean loadedStandingSpace(ServerLevel level,BlockPos feet,AABB box){
        if(!level.getWorldBorder().isWithinBounds(box)||box.minY<level.getMinBuildHeight()||box.maxY>=level.getMaxBuildHeight())return false;
        int minX=(int)Math.floor(box.minX),maxX=(int)Math.floor(box.maxX-1.0e-6);
        int minZ=(int)Math.floor(box.minZ),maxZ=(int)Math.floor(box.maxZ-1.0e-6);
        for(int cx=minX>>4;cx<=maxX>>4;cx++)for(int cz=minZ>>4;cz<=maxZ>>4;cz++){
            var pos=new BlockPos(cx*16,feet.getY(),cz*16);
            if(level.getChunkSource().getChunkNow(cx,cz)==null||!level.isPositionEntityTicking(pos)
                    ||!level.areEntitiesLoaded(new ChunkPos(cx,cz).toLong()))return false;
        }
        // The whole footprint needs support, not merely the centre of a narrow bridge.
        for(int x=minX;x<=maxX;x++)for(int z=minZ;z<=maxZ;z++){
            var support=new BlockPos(x,feet.getY()-1,z);
            if(!level.getBlockState(support).isFaceSturdy(level,support,Direction.UP))return false;
            for(int y=feet.getY();y<Math.ceil(box.maxY);y++)
                if(!level.getFluidState(new BlockPos(x,y,z)).isEmpty())return false;
        }
        return true;
    }

    /** Always release in the owner dimension, including a death after portal travel. */
    public static void release(Entity actor){
        if(!(actor.level() instanceof ServerLevel level)||!(actor instanceof Jinwu||actor instanceof HammerGuardian))return;
        var tag=actor.getPersistentData().getCompound(OWNER);if(!tag.hasUUID("Instance"))return;
        var owner=level.getServer().overworld();var state=BlueprintSpawnState.get(owner);
        var marker=state.markers.get(key(tag.getUUID("Instance"),tag.getBoolean("Hammer")));
        if(marker==null||!marker.members.remove(actor.getUUID()))return;
        marker.cleared=true;marker.nextSpawn=owner.getGameTime()+12000;state.setDirty();
    }
}
