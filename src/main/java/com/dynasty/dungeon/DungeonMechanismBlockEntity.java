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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** One room core owns ticking; markers reconcile on load without loading other chunks. */
public final class DungeonMechanismBlockEntity extends BlockEntity {
    private UUID instance;
    private String roomId="probe",mechanismId="";
    private BlockPos controller=BlockPos.ZERO;
    private int symbol=-1;
    private final List<BlockPos> markers=new ArrayList<>();
    private boolean registered;
    public DungeonMechanismBlockEntity(BlockPos pos,BlockState state){super(DungeonContent.MECHANISM.get(),pos,state);}
    public void configure(UUID instance,String room,String mechanism,BlockPos core,int symbol,List<BlockPos> markerPositions){
        this.instance=instance;roomId=room;mechanismId=mechanism;controller=core.immutable();this.symbol=symbol>=0&&symbol<=5?symbol:-1;
        markers.clear();markers.addAll(markerPositions.stream().filter(p->p.closerThan(core,128)).limit(64).toList());
        registered=false;setChanged();
    }
    public UUID instance(){return instance;}
    public String roomId(){return roomId;}
    public boolean validBinding(){return instance!=null&&!roomId.isBlank()&&worldPosition.closerThan(controller,128);}
    private DungeonRoomController room(){return validBinding()&&level instanceof ServerLevel sl?DungeonStateStore.get(sl).room(instance,roomId):null;}
    private DungeonMechanismBlock.Kind kind(){return ((DungeonMechanismBlock)getBlockState().getBlock()).kind();}
    private void changed(){if(level instanceof ServerLevel sl)DungeonStateStore.get(sl).setDirty();setChanged();}
    public void interact(Player player){
        if(level==null||level.isClientSide||player.isSpectator()||player.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(worldPosition))>36)return;
        var state=room();if(state==null)return;
        if(kind()==DungeonMechanismBlock.Kind.SEAL){if(state.recordTarget(symbol)){changed();syncVisual(state);}}
        else if(kind()==DungeonMechanismBlock.Kind.CORE){player.displayClientMessage(net.minecraft.network.chat.Component.literal("试验房：破封 "+Integer.bitCount(state.progress()&7)+"/3，兽眼 "+Integer.bitCount((state.progress()>>3)&7)+"/3"),true);}
    }
    public void hitTarget(Player player){
        if(level==null||level.isClientSide||player.isSpectator()||player.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(worldPosition))>4096)return;
        var state=room();if(state!=null&&kind()==DungeonMechanismBlock.Kind.TARGET&&state.recordTarget(symbol)){changed();syncVisual(state);}
    }
    public void trigger(){var state=room();if(state!=null&&state.phase()==DungeonMechanism.Phase.IDLE){state.trigger(level.getGameTime());changed();}}
    public void syncVisual(DungeonRoomController room){
        if(level==null)return;
        var old=getBlockState();boolean solved=symbol>=0&&(room.progress()&(1<<symbol))!=0;
        boolean open=kind()==DungeonMechanismBlock.Kind.DOOR?room.completed():kind()==DungeonMechanismBlock.Kind.FLOOR&&room.phase()==DungeonMechanism.Phase.ACTIVE;
        var next=old.setValue(DungeonMechanismBlock.ACTIVE,solved||room.phase()==DungeonMechanism.Phase.WARNING||room.phase()==DungeonMechanism.Phase.ACTIVE)
            .setValue(DungeonMechanismBlock.OPEN,open).setValue(DungeonMechanismBlock.STAGE,room.phase().ordinal());
        if(next!=old){level.setBlock(worldPosition,next,3);level.sendBlockUpdated(worldPosition,old,next,3);}
    }
    public static void tick(Level level,BlockPos pos,BlockState block,DungeonMechanismBlockEntity be){
        if(!(level instanceof ServerLevel sl)||!be.validBinding())return;
        if(!be.registered){be.registered=true;be.syncVisual(be.room());}
        if(be.kind()!=DungeonMechanismBlock.Kind.CORE||level.getGameTime()%2!=0)return;
        var room=be.room();long time=level.getGameTime();
        boolean nearby=sl.players().stream().anyMatch(p->!p.isSpectator()&&p.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(pos))<96*96);
        if(!nearby){room.pause(time);return;}
        var before=room.phase();int beforeTicks=room.phaseTicks();room.tickActive(time);
        boolean contact=room.consumeContact();
        if(before!=room.phase()||beforeTicks!=room.phaseTicks())be.changed();
        for(BlockPos marker:be.markers){
            if(!sl.hasChunkAt(marker))continue;
            if(sl.getBlockEntity(marker) instanceof DungeonMechanismBlockEntity part&&be.instance.equals(part.instance)&&be.roomId.equals(part.roomId)){
                part.syncVisual(room);
                if(contact&&part.kind()==DungeonMechanismBlock.Kind.TRAP){
                    var area=new AABB(marker).inflate(2,1,2);
                    for(Player player:sl.getEntitiesOfClass(Player.class,area,p->!p.isSpectator()&&!p.isCreative())){
                        player.hurt(sl.damageSources().magic(),3);
                        player.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.POISON,60,0));
                    }
                }
            }
        }
        // Warnings are sparse and local. The same timer controls visual and hit.
        if(room.phase()==DungeonMechanism.Phase.WARNING&&time%4==0){
            for(BlockPos marker:be.markers)if(sl.hasChunkAt(marker)&&sl.getBlockState(marker).is(DungeonContent.TRAP.get()))
                sl.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE,marker.getX()+.5,marker.getY()+1.1,marker.getZ()+.5,3,.5,.05,.5,.01);
        }
    }
    @Override protected void saveAdditional(CompoundTag tag){
        super.saveAdditional(tag);
        if(instance!=null)tag.putUUID("DungeonInstance",instance);
        tag.putString("Room",roomId);tag.putString("Mechanism",mechanismId);tag.putLong("Controller",controller.asLong());tag.putInt("Symbol",symbol);
        tag.putLongArray("Markers",markers.stream().mapToLong(BlockPos::asLong).toArray());
    }
    @Override public void load(CompoundTag tag){
        super.load(tag);instance=tag.hasUUID("DungeonInstance")?tag.getUUID("DungeonInstance"):null;
        roomId=tag.getString("Room");mechanismId=tag.getString("Mechanism");controller=BlockPos.of(tag.getLong("Controller"));
        symbol=tag.contains("Symbol")?tag.getInt("Symbol"):-1;if(symbol<0||symbol>5)symbol=-1;
        markers.clear();for(long value:tag.getLongArray("Markers")){BlockPos p=BlockPos.of(value);if(p.closerThan(controller,128)&&markers.size()<64)markers.add(p);}
        registered=false;
    }
    @Override public CompoundTag getUpdateTag(){return saveWithoutMetadata();}
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket(){return ClientboundBlockEntityDataPacket.create(this);}
}
