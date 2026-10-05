package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Cores own room clocks. Markers use loaded-only bindings and authoritative visual snapshots. */
public final class DungeonMechanismBlockEntity extends BlockEntity {
    private UUID instance;
    private String roomId="probe",mechanismId="";
    private BlockPos controller=BlockPos.ZERO,areaMin,areaMax,destination;
    private int symbol=-1,requiredTargets=63;
    private boolean timedTrial;
    private final List<BlockPos> markers=new ArrayList<>();
    private boolean registered;
    private int visualPhase,visualTicks,visualDuration=1,doorTicks=12;
    private long visualTime;
    public DungeonMechanismBlockEntity(BlockPos pos,BlockState state){super(DungeonContent.MECHANISM.get(),pos,state);}
    public void configure(UUID instance,String room,String mechanism,BlockPos core,int symbol,List<BlockPos> markerPositions){
        this.instance=instance;roomId=room;mechanismId=mechanism;controller=core.immutable();this.symbol=symbol>=0&&symbol<=5?symbol:-1;
        markers.clear();markers.addAll(markerPositions.stream().filter(p->p.closerThan(core,128)).distinct().limit(64).toList());
        registered=false;setChanged();
    }
    public void configureRoom(int targets,boolean timed,BlockPos min,BlockPos max){
        requiredTargets=targets&63;timedTrial=timed;
        if(min.closerThan(controller,128)&&max.closerThan(controller,128)){areaMin=min.immutable();areaMax=max.immutable();}
        registered=false;setChanged();
    }
    public void setDestination(BlockPos dest){if(dest.closerThan(worldPosition,128)){destination=dest.immutable();setChanged();}}
    public UUID instance(){return instance;}
    public String roomId(){return roomId;}
    public String mechanismId(){return mechanismId;}
    public boolean validBinding(){return instance!=null&&!roomId.isBlank()&&worldPosition.closerThan(controller,128);}
    private DungeonRoomController room(){return validBinding()&&level instanceof ServerLevel sl?DungeonStateStore.get(sl).room(instance,roomId):null;}
    public DungeonMechanismBlock.Kind kind(){return ((DungeonMechanismBlock)getBlockState().getBlock()).kind();}
    private boolean hazard(){return kind()==DungeonMechanismBlock.Kind.FLOOR||kind()==DungeonMechanismBlock.Kind.TRAP;}
    private DungeonHazard clock(DungeonRoomController room){return room.hazard(mechanismId,kind()==DungeonMechanismBlock.Kind.FLOOR);}
    private void changed(){if(level instanceof ServerLevel sl)DungeonStateStore.get(sl).setDirty();setChanged();}
    public void interact(Player player){
        if(level==null||level.isClientSide||player.isSpectator()||player.distanceToSqr(Vec3.atCenterOf(worldPosition))>36)return;
        var state=room();if(state==null)return;
        if(kind()==DungeonMechanismBlock.Kind.SEAL){if(state.recordTarget(symbol)){changed();syncVisual(state);}}
        else if(kind()==DungeonMechanismBlock.Kind.ELEVATOR){
            if(state.unlockShortcut(mechanismId))changed();
            syncVisual(state);useElevator(player);
        }else if(kind()==DungeonMechanismBlock.Kind.CORE){player.displayClientMessage(net.minecraft.network.chat.Component.literal(
            "破封 "+Integer.bitCount(state.progress()&7)+"/3，兽眼 "+Integer.bitCount((state.progress()>>3)&7)+"/3"),true);}
    }
    private void useElevator(Player player){
        if(!(level instanceof ServerLevel sl)||destination==null||!sl.hasChunkAt(destination)){
            player.displayClientMessage(net.minecraft.network.chat.Component.literal("吊篮已解锁；出口区块尚未加载。"),true);return;
        }
        AABB landing=player.getBoundingBox().move(destination.getX()+.5-player.getX(),destination.getY()-player.getY(),destination.getZ()+.5-player.getZ());
        if(!sl.getWorldBorder().isWithinBounds(landing)||!sl.noCollision(player,landing)
                ||!sl.getBlockState(destination.below()).isFaceSturdy(sl,destination.below(),net.minecraft.core.Direction.UP)
                ||!sl.getBlockState(destination).getFluidState().isEmpty())return;
        player.teleportTo(destination.getX()+.5,destination.getY(),destination.getZ()+.5);
        player.setDeltaMovement(Vec3.ZERO);player.fallDistance=0;
        sl.playSound(null,worldPosition,net.minecraft.sounds.SoundEvents.CHAIN_PLACE,net.minecraft.sounds.SoundSource.BLOCKS,1,.6F);
    }
    public void hitTarget(Player player){
        if(level==null||level.isClientSide||player.isSpectator()||player.distanceToSqr(Vec3.atCenterOf(worldPosition))>4096)return;
        var state=room();if(state!=null&&kind()==DungeonMechanismBlock.Kind.TARGET&&state.recordTarget(symbol)){changed();syncVisual(state);}
    }
    public void trigger(){var state=room();if(state!=null&&hazard()){
        var clock=clock(state);if(clock.phase()==DungeonMechanism.Phase.IDLE){clock.trigger(level.getGameTime());changed();syncVisual(state);}
    }}
    public float visualProgress(float partial){
        long elapsed=level==null?0:Math.max(0,Math.min(10,level.getGameTime()-visualTime));
        return net.minecraft.util.Mth.clamp((visualTicks+elapsed+partial)/(float)Math.max(1,visualDuration),0,1);
    }
    public float doorProgress(float partial){
        if(getBlockState().getValue(DungeonMechanismBlock.OPEN))return 1;
        if(!getBlockState().getValue(DungeonMechanismBlock.ACTIVE))return 0;
        long elapsed=level==null?0:Math.max(0,Math.min(10,level.getGameTime()-visualTime));
        return net.minecraft.util.Mth.clamp((doorTicks+elapsed+partial)/12F,0,1);
    }
    public void syncVisual(DungeonRoomController room){
        if(level==null)return;
        var old=getBlockState();boolean solved=symbol>=0&&(room.progress()&(1<<symbol))!=0;
        var phase=hazard()?clock(room).phase():DungeonMechanism.Phase.IDLE;
        boolean open=kind()==DungeonMechanismBlock.Kind.DOOR?
            mechanismId.startsWith("trial_entry")?!room.trialRunning():room.doorOpen():kind()==DungeonMechanismBlock.Kind.FLOOR&&(phase==DungeonMechanism.Phase.ACTIVE||phase==DungeonMechanism.Phase.RECOVERY);
        boolean active=solved||phase==DungeonMechanism.Phase.WARNING||phase==DungeonMechanism.Phase.ACTIVE
            ||kind()==DungeonMechanismBlock.Kind.DOOR&&room.completed()||kind()==DungeonMechanismBlock.Kind.ELEVATOR&&room.shortcutOpen(mechanismId);
        var next=old.setValue(DungeonMechanismBlock.ACTIVE,active).setValue(DungeonMechanismBlock.OPEN,open).setValue(DungeonMechanismBlock.STAGE,phase.ordinal());
        int ticks=hazard()?clock(room).ticks():0,duration=hazard()?clock(room).duration():1;
        boolean snapshot=visualPhase!=phase.ordinal()||doorTicks!=room.openingTicks()
            ||visualTicks!=ticks&&level.getGameTime()-visualTime>=10;
        if(next!=old||snapshot){
            visualPhase=phase.ordinal();visualTicks=ticks;visualDuration=duration;doorTicks=room.openingTicks();visualTime=level.getGameTime();
            if(next!=old)level.setBlock(worldPosition,next,3);
            setChanged();level.sendBlockUpdated(worldPosition,old,next,3);
        }
    }
    public static void tick(Level level,BlockPos pos,BlockState block,DungeonMechanismBlockEntity be){
        if(!(level instanceof ServerLevel sl)||!be.validBinding())return;
        var room=be.room();
        if(!be.registered){be.registered=true;
            if(be.kind()==DungeonMechanismBlock.Kind.CORE)room.configureTargets(be.requiredTargets,be.timedTrial);
            be.syncVisual(room);
        }
        if(be.kind()!=DungeonMechanismBlock.Kind.CORE||level.getGameTime()%2!=0)return;
        long time=level.getGameTime();
        boolean nearby=sl.players().stream().anyMatch(p->!p.isSpectator()&&p.distanceToSqr(Vec3.atCenterOf(pos))<96*96);
        boolean changed=room.tickRoom(time,nearby);
        if(!nearby){room.pause(time);room.pauseHazards(time);if(changed)be.changed();return;}
        var loaded=new ArrayList<DungeonMechanismBlockEntity>();
        for(BlockPos marker:be.markers)if(sl.hasChunkAt(marker)&&sl.getBlockEntity(marker) instanceof DungeonMechanismBlockEntity part
                &&be.instance.equals(part.instance)&&be.roomId.equals(part.roomId))loaded.add(part);
        var handled=new java.util.HashSet<String>();
        for(var part:loaded)if(part.hazard()&&handled.add(part.mechanismId)){
            var clock=part.clock(room);boolean local=loaded.stream().filter(p->p.hazard()&&p.mechanismId.equals(part.mechanismId))
                .anyMatch(p->sl.players().stream().anyMatch(player->!player.isSpectator()&&player.distanceToSqr(Vec3.atCenterOf(p.worldPosition))<24*24));
            if(!local){clock.pause(time);continue;}
            var before=clock.phase();int beforeTicks=clock.ticks();clock.tickActive(time);
            changed|=before!=clock.phase()||beforeTicks!=clock.ticks();
            boolean contact=clock.consumeContact();
            if(contact)for(var emitter:loaded)if(emitter.kind()==DungeonMechanismBlock.Kind.TRAP&&emitter.mechanismId.equals(part.mechanismId))emitter.damageTrap(sl);
        }
        if(be.timedTrial&&be.areaMin!=null){
            var area=new AABB(be.areaMin,be.areaMax.offset(1,1,1));
            var entrants=sl.getEntitiesOfClass(Player.class,area,p->!p.isSpectator()&&!p.isCreative());
            if(entrants.isEmpty())changed|=room.allowRetry();
            if(!entrants.isEmpty()&&!room.trialFailed())changed|=room.startTrial(time);
            if(room.trialRunning()&&time%20==0){
                double liquidY=be.areaMin.getY()+Math.min(3,room.trialTicks()/400.0);
                sl.sendParticles(net.minecraft.core.particles.ParticleTypes.SOUL,area.getCenter().x,liquidY,area.getCenter().z,12,area.getXsize()/3,.05,area.getZsize()/3,0);
                if(room.trialTicks()>=20)for(Player player:entrants)if(player.getY()<liquidY)player.hurt(sl.damageSources().magic(),2);
            }
        }
        for(var part:loaded){part.syncVisual(room);
            if(part.hazard()&&part.clock(room).phase()==DungeonMechanism.Phase.WARNING&&time%4==0)
                sl.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE,part.worldPosition.getX()+.5,part.worldPosition.getY()+1.1,part.worldPosition.getZ()+.5,3,.5,.05,.5,.01);
        }
        if(changed)be.changed();
    }
    private void damageTrap(ServerLevel sl){
        var facing=getBlockState().getValue(DungeonMechanismBlock.FACING);
        Vec3 center=Vec3.atCenterOf(worldPosition).add(facing.getStepX()*2,.7,facing.getStepZ()*2);
        var area=new AABB(center,center).inflate(facing.getStepX()==0?1:2,1,facing.getStepZ()==0?1:2);
        for(Player player:sl.getEntitiesOfClass(Player.class,area,p->!p.isSpectator()&&!p.isCreative())){
            player.hurt(sl.damageSources().magic(),3);
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.POISON,60,0));
        }
        sl.sendParticles(net.minecraft.core.particles.ParticleTypes.CRIT,center.x,center.y,center.z,8,.5,.15,.5,.02);
        sl.playSound(null,worldPosition,net.minecraft.sounds.SoundEvents.DISPENSER_LAUNCH,net.minecraft.sounds.SoundSource.BLOCKS,1,1);
    }
    @Override protected void saveAdditional(CompoundTag tag){
        super.saveAdditional(tag);
        if(instance!=null)tag.putUUID("DungeonInstance",instance);
        tag.putString("Room",roomId);tag.putString("Mechanism",mechanismId);tag.putLong("Controller",controller.asLong());tag.putInt("Symbol",symbol);
        tag.putLongArray("Markers",markers.stream().mapToLong(BlockPos::asLong).toArray());
        tag.putInt("RequiredTargets",requiredTargets);tag.putBoolean("TimedTrial",timedTrial);
        if(areaMin!=null){tag.putLong("AreaMin",areaMin.asLong());tag.putLong("AreaMax",areaMax.asLong());}
        if(destination!=null)tag.putLong("Destination",destination.asLong());
        tag.putInt("VisualPhase",visualPhase);tag.putInt("VisualTicks",visualTicks);tag.putInt("VisualDuration",visualDuration);
        tag.putInt("DoorTicks",doorTicks);tag.putLong("VisualTime",visualTime);
    }
    @Override public void load(CompoundTag tag){
        super.load(tag);instance=tag.hasUUID("DungeonInstance")?tag.getUUID("DungeonInstance"):null;
        roomId=tag.getString("Room");mechanismId=tag.getString("Mechanism");controller=BlockPos.of(tag.getLong("Controller"));
        symbol=tag.contains("Symbol")?tag.getInt("Symbol"):-1;if(symbol<0||symbol>5)symbol=-1;
        markers.clear();for(long value:tag.getLongArray("Markers")){BlockPos p=BlockPos.of(value);if(p.closerThan(controller,128)&&markers.size()<64)markers.add(p);}
        requiredTargets=tag.contains("RequiredTargets")?tag.getInt("RequiredTargets")&63:63;timedTrial=tag.getBoolean("TimedTrial");
        areaMin=tag.contains("AreaMin")?BlockPos.of(tag.getLong("AreaMin")):null;areaMax=tag.contains("AreaMax")?BlockPos.of(tag.getLong("AreaMax")):null;
        if(areaMin==null||areaMax==null||!areaMin.closerThan(controller,128)||!areaMax.closerThan(controller,128)){areaMin=null;areaMax=null;}
        destination=tag.contains("Destination")?BlockPos.of(tag.getLong("Destination")):null;
        if(destination!=null&&!destination.closerThan(worldPosition,128))destination=null;
        visualPhase=Math.max(0,Math.min(3,tag.getInt("VisualPhase")));visualTicks=Math.max(0,tag.getInt("VisualTicks"));
        visualDuration=Math.max(1,tag.getInt("VisualDuration"));doorTicks=Math.max(0,Math.min(12,tag.getInt("DoorTicks")));visualTime=tag.getLong("VisualTime");registered=false;
    }
    @Override public CompoundTag getUpdateTag(){return saveWithoutMetadata();}
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket(){return ClientboundBlockEntityDataPacket.create(this);}
}
