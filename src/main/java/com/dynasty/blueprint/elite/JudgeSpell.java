package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
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

/** Three finite spells. The cage is one server object, four visual pillars, no pillar AIs. */
public final class JudgeSpell extends Entity implements GeoEntity {
    public static final String PEN_ID="judge_falling_pen",STROKE_ID="judge_ink_stroke",CAGE_ID="judge_chain_cage";
    private static final EntityDataAccessor<Float> LENGTH=SynchedEntityData.defineId(JudgeSpell.class,EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> STUCK=SynchedEntityData.defineId(JudgeSpell.class,EntityDataSerializers.BOOLEAN);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born=-1,lastTick=-1,epoch=-1;
    private Vec3 direction=new Vec3(0,0,1);
    private final Set<UUID> hit=new HashSet<>();
    private final LinkedHashMap<UUID,Vec3> trapped=new LinkedHashMap<>();
    public JudgeSpell(EntityType<? extends JudgeSpell> type,Level level){super(type,level);}
    public boolean cage(){return getType()==EliteContent.JUDGE_CAGE.get();}
    public boolean pen(){return getType()==EliteContent.JUDGE_PEN.get();}
    public String modelId(){return cage()?CAGE_ID:pen()?PEN_ID:STROKE_ID;}
    public float strokeLength(){return entityData.get(LENGTH);}
    public boolean stuck(){return entityData.get(STUCK);}
    public int trappedCount(){return trapped.size();}
    public boolean ownedBy(LampJudge judge){return judge.getUUID().equals(owner);}
    @Override protected void defineSynchedData(){entityData.define(LENGTH,5.5F);entityData.define(STUCK,false);}
    public void launch(LampJudge judge,Vec3 at,Vec3 forward){
        owner=judge.getUUID();born=level().getGameTime();lastTick=born;epoch=judge.attack().started();setPos(at);
        direction=forward.multiply(1,0,1).normalize();if(direction.lengthSqr()<.001)direction=new Vec3(0,0,1);
        setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));
        if(pen())setDeltaMovement(0,-.7,0);
        else if(!cage())refreshLength();
        else if(level() instanceof ServerLevel world)for(var player:world.players()){
            if(trapped.size()>=8)break;
            if(validPlayer(player)&&player.position().subtract(at).horizontalDistanceSqr()<=9&&Math.abs(player.getY()-at.y)<=3)trapped.put(player.getUUID(),player.position());
        }
    }
    private boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return level().getWorldBorder().isWithinBounds(box);}
    private boolean validPlayer(ServerPlayer p){return p.isAlive()&&!p.isSpectator()&&!p.isCreative()&&p.level()==level();}
    private void refreshLength(){
        var to=position().add(direction.scale(5.5));
        if(!loaded(new AABB(position(),to).inflate(.3))){discard();return;}
        var wall=level().clip(new ClipContext(position(),to,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));
        // Never regrow through a removed obstruction; a new wall may shorten the visible cut.
        float length=(float)(wall.getType()==HitResult.Type.MISS?5.5:Math.max(0,position().distanceTo(wall.getLocation())-.05));
        entityData.set(LENGTH,Math.min(strokeLength(),length));
    }
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||owner==null||!(world.getEntity(owner) instanceof LampJudge judge)||!judge.isAlive()){discard();return;}
        long now=world.getGameTime(),age=now-born;
        if(born<0||age<0||age>=(cage()?160:pen()?30:80)||now-lastTick>1||now<lastTick||distanceToSqr(judge)>68*68){discard();return;}if(now==lastTick)return;lastTick=now;
        if(cage()){
            if(judge.attack().current()!=LampJudge.CAGE||judge.attack().started()!=epoch||!loaded(new AABB(getX()-3.5,getY(),getZ()-3.5,getX()+3.5,getY()+3,getZ()+3))){discard();return;}
            confine(world,judge);return;
        }
        if(pen())fall(world,judge);else cut(world,judge);
    }
    private void fall(ServerLevel world,LampJudge judge){
        if(stuck()){if(!loaded(getBoundingBox()))discard();return;}
        var velocity=getDeltaMovement();if(!Double.isFinite(velocity.lengthSqr())||velocity.lengthSqr()>2){discard();return;}
        var next=position().add(velocity);var body=getBoundingBox().expandTowards(velocity);
        if(!loaded(body)){discard();return;}
        if(world.getBlockCollisions(this,body).iterator().hasNext()){
            var floor=world.clip(new ClipContext(position(),next,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));
            if(floor.getType()==HitResult.Type.BLOCK&&floor.getDirection()==net.minecraft.core.Direction.UP){setPos(floor.getLocation().add(0,.02,0));setDeltaMovement(Vec3.ZERO);entityData.set(STUCK,true);}else discard();
            return;
        }
        // Only the actual bottom nib deals damage, not the five-metre visual shaft.
        var sweep=new AABB(position(),next).inflate(.3);LivingEntity nearest=null;double best=Double.MAX_VALUE;
        for(var target:world.getEntitiesOfClass(LivingEntity.class,sweep,judge::enemy).stream().limit(16).toList()){
            var box=target.getBoundingBox().inflate(.3);var contact=box.contains(position())?Optional.of(position()):box.clip(position(),next);if(contact.isEmpty())continue;
            double distance=position().distanceToSqr(contact.get());
            if(distance<best&&world.clip(new ClipContext(position(),contact.get(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS){best=distance;nearest=target;}
        }
        if(nearest!=null){nearest.hurt(damageSources().indirectMagic(this,judge),(float)judge.getAttributeValue(Attributes.ATTACK_DAMAGE)*1.8F);discard();return;}
        setPos(next);
    }
    private void cut(ServerLevel world,LampJudge judge){
        refreshLength();if(isRemoved()||strokeLength()<.1||hit.size()>=16)return;
        var to=position().add(direction.scale(strokeLength()));var sweep=new AABB(position(),to).inflate(.25);
        for(var target:world.getEntitiesOfClass(LivingEntity.class,sweep,judge::enemy).stream().limit(16).toList()){
            if(hit.contains(target.getUUID()))continue;var box=target.getBoundingBox().inflate(.25);
            var contact=box.contains(position())?Optional.of(position()):box.clip(position(),to);if(contact.isEmpty())continue;
            if(world.clip(new ClipContext(position(),contact.get(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            hit.add(target.getUUID());target.hurt(damageSources().mobAttack(judge),(float)judge.getAttributeValue(Attributes.ATTACK_DAMAGE)*.75F);
            if(hit.size()>=16)break;
        }
    }
    private boolean legal(ServerPlayer player,Vec3 destination){
        var box=player.getBoundingBox().move(destination.subtract(player.position()));var foot=BlockPos.containing(destination);
        return loaded(box)&&level().noCollision(player,box)&&level().getFluidState(foot).isEmpty()
            &&level().getBlockState(foot.below()).isFaceSturdy(level(),foot.below(),net.minecraft.core.Direction.UP);
    }
    private void confine(ServerLevel world,LampJudge judge){
        var iterator=trapped.entrySet().iterator();
        while(iterator.hasNext()){
            var entry=iterator.next();var player=world.getPlayerByUUID(entry.getKey());
            if(!(player instanceof ServerPlayer p)||!validPlayer(p)){iterator.remove();continue;}
            var offset=p.position().subtract(position());
            if(offset.horizontalDistanceSqr()<=2.6*2.6&&Math.abs(offset.y)<=3){if(legal(p,p.position()))entry.setValue(p.position());continue;}
            var horizontal=offset.multiply(1,0,1);if(horizontal.lengthSqr()>.001)horizontal=horizontal.normalize().scale(2.6);
            var destination=position().add(horizontal);if(!legal(p,destination))destination=entry.getValue();
            if(!legal(p,destination)){judge.breakCage();return;}
            // Native authoritative correction keeps the player's current view and never changes dimension.
            if(p.connection!=null)p.connection.teleport(destination.x,destination.y,destination.z,p.getYRot(),p.getXRot());else p.moveTo(destination);
            p.setDeltaMovement(0,p.getDeltaMovement().y,0);p.fallDistance=0;
        }
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){
        if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putLong("Epoch",epoch);
        t.putDouble("DirectionX",direction.x);t.putDouble("DirectionZ",direction.z);t.putFloat("Length",strokeLength());t.putBoolean("Stuck",stuck());
        var hits=new ListTag();for(var id:hit.stream().limit(16).toList()){var tag=new CompoundTag();tag.putUUID("Id",id);hits.add(tag);}t.put("Hits",hits);
        // Player constraints are deliberately not resurrected after an unloaded cage.
    }
    @Override protected void readAdditionalSaveData(CompoundTag t){
        owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;epoch=t.contains("Epoch")?t.getLong("Epoch"):-1;
        direction=new Vec3(t.getDouble("DirectionX"),0,t.getDouble("DirectionZ"));float length=t.getFloat("Length");
        if(!Double.isFinite(direction.lengthSqr())||direction.lengthSqr()<.001||!Float.isFinite(length)||length<0||length>5.5){born=-1;direction=new Vec3(0,0,1);length=0;}else direction=direction.normalize();
        entityData.set(LENGTH,length);entityData.set(STUCK,t.getBoolean("Stuck"));hit.clear();trapped.clear();for(var item:t.getList("Hits",Tag.TAG_COMPOUND)){if(hit.size()>=16)break;var tag=(CompoundTag)item;if(tag.hasUUID("Id"))hit.add(tag.getUUID("Id"));}if(cage())born=-1;
    }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"spell",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+modelId()+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
