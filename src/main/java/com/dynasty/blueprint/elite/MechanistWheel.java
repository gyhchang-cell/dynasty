package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import com.dynasty.blueprint.combat.CombatGeometry;
import java.util.*;

/** Two physical, locked arcs; finite owner-bound entities, one hit per target per leg. */
public final class MechanistWheel extends Entity {
    public static final double RANGE=9,INNER_GAP=.9,CURVE_WIDTH=2;
    public static final int LIFETIME=40;
    private UUID owner;
    private Vec3 origin=Vec3.ZERO,forward=new Vec3(0,0,1);
    private long born=-1;
    private long lastTick=-1;
    private int side=1;
    private final Set<UUID> outgoing=new HashSet<>(),returning=new HashSet<>();
    public MechanistWheel(EntityType<? extends MechanistWheel> type,Level level){super(type,level);}
    public void launch(Mechanist caster,Vec3 direction,int flank){owner=caster.getUUID();born=level().getGameTime();lastTick=born;origin=caster.position().add(0,.2,0);forward=direction.multiply(1,0,1).normalize();side=flank<0?-1:1;
        setPos(point(0));}
    public boolean ownedBy(Mechanist caster){return caster.getUUID().equals(owner);}
    public UUID ownerId(){return owner;}
    public long born(){return born;}
    private Vec3 point(double t){double wave=Math.sin(Math.PI*t),offset=side*(INNER_GAP+CURVE_WIDTH*wave);return origin.add(forward.scale(RANGE*wave)).add(-forward.z*offset,0,forward.x*offset);}
    @Override protected void defineSynchedData(){}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||born<0||owner==null){discard();return;}
        long age=world.getGameTime()-born;
        if(age<0||age>LIFETIME||!(world.getEntity(owner) instanceof Mechanist caster)||!caster.isAlive()||caster.distanceToSqr(this)>32*32){discard();return;}
        if(world.getGameTime()<lastTick||world.getGameTime()-lastTick>1){discard();return;}
        if(world.getGameTime()==lastTick)return;
        lastTick=world.getGameTime();
        var destination=point(Math.min(1,age/(double)LIFETIME));if(!world.hasChunkAt(BlockPos.containing(destination))){discard();return;}
        var from=position();
        if(world.clip(new ClipContext(from,destination,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS){discard();return;}
        move(MoverType.SELF,destination.subtract(from));if(horizontalCollision||verticalCollision){discard();return;}
        var spent=age<=LIFETIME/2?outgoing:returning;
        for(var hit:world.getEntitiesOfClass(LivingEntity.class,new AABB(from,position()).inflate(.42),e->caster.enemy(e)&&!spent.contains(e.getUUID()))){
            if(hit.getBoundingBox().inflate(.4).clip(from,position()).isEmpty()
                    ||world.clip(new ClipContext(position(),hit.getBoundingBox().getCenter(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(spent.size()>=16)break;spent.add(hit.getUUID());
            if(hit instanceof Player player&&player.isBlocking()&&CombatGeometry.inFront(player.position(),player.getLookAngle(),position(),180)){
                player.hurt(damageSources().mobProjectile(this,caster),5);player.playSound(SoundEvents.SHIELD_BLOCK,1,1.1F);discard();return;
            }
            hit.hurt(damageSources().mobProjectile(this,caster),5);
        }
        if(age%8==0)playSound(SoundEvents.GRINDSTONE_USE,.5F,1.8F);
        if(age>=LIFETIME)discard();
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putInt("Side",side);t.putDouble("X",origin.x);t.putDouble("Y",origin.y);t.putDouble("Z",origin.z);t.putDouble("DX",forward.x);t.putDouble("DZ",forward.z);
        t.putInt("Version",1);saveHits(t,"Outgoing",outgoing);saveHits(t,"Returning",returning);}
    private static void saveHits(CompoundTag t,String key,Set<UUID> hits){var list=new net.minecraft.nbt.ListTag();for(var id:hits)list.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));t.put(key,list);}
    private static void loadHits(CompoundTag t,String key,Set<UUID> hits){hits.clear();var list=t.getList(key,8);for(int i=0;i<Math.min(16,list.size());i++)try{hits.add(UUID.fromString(list.getString(i)));}catch(IllegalArgumentException ignored){}}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;side=t.getInt("Side")<0?-1:1;origin=new Vec3(t.getDouble("X"),t.getDouble("Y"),t.getDouble("Z"));forward=new Vec3(t.getDouble("DX"),0,t.getDouble("DZ")).normalize();loadHits(t,"Outgoing",outgoing);loadHits(t,"Returning",returning);
        if(!Double.isFinite(origin.lengthSqr())||origin.distanceToSqr(position())>32*32||forward.lengthSqr()<.9)born=-1;}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
}
