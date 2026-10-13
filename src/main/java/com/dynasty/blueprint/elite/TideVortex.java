package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Two diverging native water columns; each target can be lifted only once per column. */
public final class TideVortex extends Entity implements GeoEntity {
    public static final String ID="yasha_tidal_vortex";
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born=-1,lastTick=-1,epoch=-1;
    private Vec3 origin=Vec3.ZERO,forward=new Vec3(0,0,1);
    private final Set<UUID> hit=new HashSet<>();
    public TideVortex(EntityType<? extends TideVortex> type,Level level){super(type,level);}
    public boolean ownedBy(TideYasha caster){return caster.getUUID().equals(owner);}
    public void launch(TideYasha caster,Vec3 from,Vec3 direction,int side){
        owner=caster.getUUID();born=level().getGameTime();lastTick=born;epoch=caster.attack().started();var right=new Vec3(-direction.z,0,direction.x);double turn=Math.toRadians(10);
        forward=direction.scale(Math.cos(turn)).add(right.scale(side*Math.sin(turn))).normalize();origin=from.add(right.scale(side*.8));setPos(origin);
    }
    @Override protected void defineSynchedData(){}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||born<0||owner==null||!(world.getEntity(owner) instanceof TideYasha caster)||!caster.isAlive()||caster.attack().current()!=TideYasha.WAVE||caster.attack().started()!=epoch){discard();return;}
        long now=world.getGameTime(),age=now-born;if(age<0||age>40||now-lastTick>1||now<lastTick||distanceToSqr(caster)>32*32){discard();return;}if(now==lastTick)return;lastTick=now;
        var next=origin.add(forward.scale(age*.32));var swept=getBoundingBox().expandTowards(next.subtract(position()));
        if(!world.hasChunkAt(BlockPos.containing(swept.minX,swept.minY,swept.minZ))||!world.hasChunkAt(BlockPos.containing(swept.maxX,swept.minY,swept.minZ))||!world.hasChunkAt(BlockPos.containing(swept.minX,swept.minY,swept.maxZ))||!world.hasChunkAt(BlockPos.containing(swept.maxX,swept.minY,swept.maxZ))||!world.getWorldBorder().isWithinBounds(swept)||world.getBlockCollisions(this,swept).iterator().hasNext()){discard();return;}
        if(world.clip(new ClipContext(position().add(0,.8,0),next.add(0,.8,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS){discard();return;}
        var segment=new AABB(position(),next).inflate(.4,0,.4).expandTowards(0,3,0);
        for(var target:world.getEntitiesOfClass(LivingEntity.class,segment,caster::enemy).stream().limit(16).toList()){
            var targetBox=target.getBoundingBox();double contactY=Math.max(next.y+.01,Math.min(next.y+2.99,(targetBox.minY+targetBox.maxY)*.5));
            var contactBox=targetBox.inflate(.4,0,.4);var from=position().add(0,contactY-position().y,0);var to=next.add(0,contactY-next.y,0);
            if(hit.contains(target.getUUID())||hit.size()>=16||!contactBox.contains(from)&&!contactBox.contains(to)&&contactBox.clip(from,to).isEmpty())continue;
            if(world.clip(new ClipContext(next.add(0,.8,0),target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            hit.add(target.getUUID());if(target.hurt(damageSources().indirectMagic(this,caster),(float)caster.getAttributeValue(Attributes.ATTACK_DAMAGE))){target.push(forward.x*.22,.55,forward.z*.22);target.hurtMarked=true;}
            if(!caster.isAlive()){discard();return;}
        }
        setPos(next);if(age==40)discard();
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putLong("Epoch",epoch);t.putDouble("X",origin.x);t.putDouble("Y",origin.y);t.putDouble("Z",origin.z);t.putDouble("DX",forward.x);t.putDouble("DY",forward.y);t.putDouble("DZ",forward.z);var list=new net.minecraft.nbt.ListTag();hit.stream().limit(16).forEach(id->{var item=new CompoundTag();item.putUUID("Target",id);list.add(item);});t.put("Hit",list);}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;epoch=t.contains("Epoch")?t.getLong("Epoch"):-1;origin=new Vec3(t.getDouble("X"),t.getDouble("Y"),t.getDouble("Z"));forward=new Vec3(t.getDouble("DX"),t.getDouble("DY"),t.getDouble("DZ"));hit.clear();var list=t.getList("Hit",net.minecraft.nbt.Tag.TAG_COMPOUND);for(int i=0;i<Math.min(16,list.size());i++)if(list.getCompound(i).hasUUID("Target"))hit.add(list.getCompound(i).getUUID("Target"));if(!Double.isFinite(origin.lengthSqr()+forward.lengthSqr())||Math.abs(forward.lengthSqr()-1)>.01||origin.distanceToSqr(position())>16*16)born=-1;}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"spin",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+ID+".spin"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
