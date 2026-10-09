package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.DynastyAdvancements;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Native air swings and grounded steps reuse secret 28 and the original Site clock. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class SwordDance {
    private static final String KEY="site_sword_scar_wall";
    private static final Direction[] FACING={Direction.NORTH,Direction.NORTH,Direction.EAST};
    private static final Vec3[] STEPS={new Vec3(.6,0,0),new Vec3(-.6,0,0),new Vec3(0,0,-.6)};
    static CompoundTag state(ServerPlayer p){
        String key="cod3_progress_28";if(!p.getPersistentData().contains(key))p.getPersistentData().put(key,new CompoundTag());return p.getPersistentData().getCompound(key);
    }
    public static boolean context(ServerPlayer p,BlockPos at){
        var level=p.serverLevel();return p.isAlive()&&!p.isSpectator()&&level.hasChunkAt(at)&&p.distanceToSqr(Vec3.atCenterOf(at))<=36
                &&level.getBlockState(at).is(SmallInteractions.ENTRIES.get("sword_scar_wall").get())&&p.getMainHandItem().getItem() instanceof SwordItem
                &&level.dimensionType().hasSkyLight()&&level.isNight()&&level.canSeeSky(p.blockPosition().above())
                &&level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING,p.blockPosition()).getY()<=p.blockPosition().above().getY()&&!level.isRainingAt(p.blockPosition());
    }
    public static boolean open(ServerPlayer p,BlockPos at){
        if(!context(p,at)){p.displayClientMessage(Component.translatable("interaction.dynasty.sword_scar_wall"),false);return false;}
        var root=EquipmentBehaviors.saved(p);var n=state(p);long now=p.level().getGameTime();
        if(SecretTracker.swordDanceClaimed(p)){root.putBoolean(KEY+"_done",true);n.putBoolean("DanceFocused",false);DynastyAdvancements.award(p,"cod4_sword_scar_wall");p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_done"),true);return true;}
        String dimension=p.level().dimension().location().toString();
        if(n.contains("Anchor")&&n.getLong("Anchor")!=at.asLong()||n.contains("DanceDimension")&&!n.getString("DanceDimension").equals(dimension)){
            n.putInt("Count",0);n.remove("DanceReadyAt");n.putBoolean("DanceFocused",false);
        }
        n.putLong("Anchor",at.asLong());n.putString("DanceDimension",dimension);
        if(!n.getBoolean("DanceFocused")){
            n.putBoolean("DanceFocused",true);n.putBoolean("DanceSwinging",p.swinging);base(p,n);
        }
        if(!root.contains(KEY+"_start")){root.putLong(KEY+"_start",now);root.putLong(KEY+"_next",now+800);}
        clue(p,n,false);cue(p,n,true);return true;
    }
    private static void base(ServerPlayer p,CompoundTag n){n.putDouble("DanceBaseX",p.getX());n.putDouble("DanceBaseY",p.getY());n.putDouble("DanceBaseZ",p.getZ());}
    private static int step(CompoundTag n){return Math.max(0,Math.min(2,n.getInt("Count")));}
    private static void clue(ServerPlayer p,CompoundTag n,boolean wrong){
        if(wrong)p.displayClientMessage(Component.translatable("cod4.dynasty.sword_dance.reset"),false);
        p.displayClientMessage(Component.translatable("cod4.dynasty.sword_dance.step_"+step(n)),false);
    }
    private static void cue(ServerPlayer p,CompoundTag n,boolean force){
        long now=p.level().getGameTime();if(!force&&n.contains("DanceCueAt")&&now-n.getLong("DanceCueAt")<40)return;n.putLong("DanceCueAt",now);
        int step=step(n);var target=new Vec3(n.getDouble("DanceBaseX"),n.getDouble("DanceBaseY"),n.getDouble("DanceBaseZ")).add(STEPS[step]);
        var direction=Vec3.atLowerCornerOf(FACING[step].getNormal());
        var packet=new Cod3VisualPacket(p.level().dimension().location().toString(),3,-1,p.getUUID().getLeastSignificantBits(),now,40,.7,target,direction,"site_sword_shadow",step,0xb8cde5);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(target.x,target.y,target.z,32,p.level().dimension())),packet);
    }
    public static void tick(ServerPlayer p){
        if(!p.getPersistentData().contains("cod3_progress_28"))return;
        var n=p.getPersistentData().getCompound("cod3_progress_28");if(!n.getBoolean("DanceFocused"))return;
        var at=BlockPos.of(n.getLong("Anchor"));
        if(!context(p,at)||!n.getString("DanceDimension").equals(p.level().dimension().location().toString())){n.putBoolean("DanceFocused",false);n.putBoolean("DanceSwinging",false);return;}
        boolean swinging=p.swinging&&p.swingingArm==InteractionHand.MAIN_HAND,edge=swinging&&!n.getBoolean("DanceSwinging");n.putBoolean("DanceSwinging",swinging);cue(p,n,false);
        if(!edge)return;var root=EquipmentBehaviors.saved(p);long now=p.level().getGameTime();boolean oldDone=root.getBoolean(KEY+"_done");
        if((!oldDone&&now<root.getLong(KEY+"_next"))||n.contains("DanceLastCut")&&now-n.getLong("DanceLastCut")<10)return;
        int step=step(n);double dx=p.getX()-n.getDouble("DanceBaseX"),dy=p.getY()-n.getDouble("DanceBaseY"),dz=p.getZ()-n.getDouble("DanceBaseZ");
        double along=step==0?dx:step==1?-dx:-dz,across=step<2?Math.abs(dz):Math.abs(dx);
        if(!p.onGround()||p.getDirection()!=FACING[step]||along<.35||along>1.5||across>.35||Math.abs(dy)>.4){
            n.putInt("Count",0);n.remove("DanceReadyAt");base(p,n);clue(p,n,true);cue(p,n,true);return;
        }
        if(step==2&&now-root.getLong(KEY+"_start")<2400){p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",Math.max(1,(2400-(now-root.getLong(KEY+"_start"))+19)/20)),true);return;}
        int count=step+1;n.putInt("Count",count);n.putLong("DanceLastCut",now);base(p,n);root.putInt(KEY+"_count",Math.max(root.getInt(KEY+"_count"),count));root.putLong(KEY+"_next",now+(oldDone?10:800));
        if(count<3){clue(p,n,false);cue(p,n,true);return;}
        n.putLong("DanceReadyAt",now);
        if(!SecretTracker.finishSwordDance(p,at))return;
        root.putBoolean(KEY+"_done",true);n.putBoolean("DanceFocused",false);
        if(!oldDone){var coins=new ItemStack(ExpansionContent.item("copper_coin"),2);if(!p.getInventory().add(coins))p.drop(coins,false);}
        DynastyAdvancements.award(p,"cod4_sword_scar_wall");p.displayClientMessage(Component.translatable("cod4.dynasty.sword_dance.found"),false);
    }
    private static void unfocus(Player p){var n=p.getPersistentData().getCompound("cod3_progress_28");n.putBoolean("DanceFocused",false);n.putBoolean("DanceSwinging",false);n.remove("DanceReadyAt");}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){unfocus(e.getEntity());}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){unfocus(e.getEntity());}
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent e){unfocus(e.getEntity());}
    private SwordDance(){}
}
