package com.dynasty.blueprint.artifact;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Persisted reward for real Taiqing temple trials and their registered sword cases. No recipe, command or packet. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ZhanluTrialRewards extends SavedData {
    private record Case(String dimension,long position){}
    private record Trial(Case swordCase,int next,long born){}
    private static final Map<ServerPlayer,Trial> TRIALS=new WeakHashMap<>();
    private final Set<Case> cases=new HashSet<>();
    private final Map<UUID,Case> eligible=new HashMap<>();
    private final Set<UUID> claimed=new HashSet<>();
    public static ZhanluTrialRewards get(ServerLevel w){return w.getServer().overworld().getDataStorage().computeIfAbsent(ZhanluTrialRewards::load,ZhanluTrialRewards::new,"dynasty_cod1_zhanlu_trials_v1");}
    /** Actual structure discovery verifies the generated temple and real case before registration. */
    public static void registerSwordCase(ServerLevel w,BlockPos p){var s=get(w);if(w.hasChunkAt(p)&&w.getBlockState(p).is(TaiqingContent.SWORD_CASE.get())&&s.cases.add(new Case(w.dimension().location().toString(),p.asLong())))s.setDirty();}
    private static boolean valid(ServerPlayer p,Case c,int distance){var at=BlockPos.of(c.position());return p.isAlive()&&!p.isSpectator()&&!p.isCreative()&&!p.isSleeping()&&c.dimension().equals(p.level().dimension().location().toString())&&p.serverLevel().hasChunkAt(at)&&p.serverLevel().getWorldBorder().isWithinBounds(at)&&p.serverLevel().getBlockState(at).is(TaiqingContent.SWORD_CASE.get())&&p.position().distanceToSqr(Vec3.atCenterOf(at))<=distance*distance;}
    public static boolean begin(ServerPlayer p,BlockPos swordCase){var s=get(p.serverLevel());var c=new Case(p.level().dimension().location().toString(),swordCase.asLong());if(s.claimed.contains(p.getUUID())||s.eligible.containsKey(p.getUUID())||!s.cases.contains(c)||!valid(p,c,16))return false;TRIALS.put(p,new Trial(c,1,p.serverLevel().getGameTime()));return true;}
    public static void cancel(ServerPlayer p){TRIALS.remove(p);}
    public static boolean active(ServerPlayer p,BlockPos at){var t=TRIALS.get(p);long now=p.serverLevel().getGameTime();return t!=null&&t.swordCase().position()==at.asLong()&&valid(p,t.swordCase(),16)&&now>=t.born()&&now-t.born()<=1800;}
    public static boolean claimed(ServerPlayer p){return get(p.serverLevel()).claimed.contains(p.getUUID());}
    public static boolean eligible(ServerPlayer p,BlockPos at){var c=get(p.serverLevel()).eligible.get(p.getUUID());return c!=null&&c.position()==at.asLong()&&valid(p,c,16);}
    /** Native meditation, ordered floor path and four-ring pulses call this after actual success. */
    public static boolean completeStage(ServerPlayer p,BlockPos swordCase,int stage){var t=TRIALS.get(p);long now=p.serverLevel().getGameTime();if(t==null||t.next()!=stage||stage<1||stage>3||t.swordCase().position()!=swordCase.asLong()||!valid(p,t.swordCase(),16)||now<t.born()||now-t.born()>1800)return false;if(stage<3)TRIALS.put(p,new Trial(t.swordCase(),stage+1,t.born()));else{TRIALS.remove(p);var s=get(p.serverLevel());s.eligible.put(p.getUUID(),t.swordCase());s.setDirty();}return true;}
    public static boolean claim(ServerPlayer p,BlockPos swordCase,InteractionHand hand){var s=get(p.serverLevel());var c=s.eligible.get(p.getUUID());if(hand!=InteractionHand.MAIN_HAND||!p.getMainHandItem().isEmpty()||s.claimed.contains(p.getUUID())||c==null||c.position()!=swordCase.asLong()||!s.cases.contains(c)||!valid(p,c,4)||p.getInventory().getFreeSlot()<0)return false;var sword=new ItemStack(ArtifactContent.ZHANLU.get());if(!p.getInventory().add(sword))return false;s.claimed.add(p.getUUID());s.eligible.remove(p.getUUID());s.setDirty();return true;}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void damage(LivingDamageEvent e){if(e.getAmount()>0&&e.getEntity() instanceof ServerPlayer p)TRIALS.remove(p);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)TRIALS.remove(p);}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){if(e.getEntity() instanceof ServerPlayer p)TRIALS.remove(p);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p){var t=TRIALS.get(p);long now=p.serverLevel().getGameTime();if(t!=null&&(!valid(p,t.swordCase(),16)||now<t.born()||now-t.born()>1800))TRIALS.remove(p);}}
    public static ZhanluTrialRewards load(CompoundTag n){var s=new ZhanluTrialRewards();for(var row:n.getList("Cases",10)){var c=(CompoundTag)row;if(!c.getString("Dimension").isEmpty())s.cases.add(new Case(c.getString("Dimension"),c.getLong("Position")));}for(var row:n.getList("Eligible",10)){var c=(CompoundTag)row;if(c.hasUUID("Id")){var at=new Case(c.getString("Dimension"),c.getLong("Position"));if(s.cases.contains(at))s.eligible.put(c.getUUID("Id"),at);}}for(var row:n.getList("Claimed",10)){var c=(CompoundTag)row;if(c.hasUUID("Id"))s.claimed.add(c.getUUID("Id"));}return s;}
    @Override public CompoundTag save(CompoundTag n){n.putInt("Version",1);var registered=new ListTag();for(var c:cases){var row=new CompoundTag();row.putString("Dimension",c.dimension());row.putLong("Position",c.position());registered.add(row);}n.put("Cases",registered);var ready=new ListTag();for(var e:eligible.entrySet()){var row=new CompoundTag();row.putUUID("Id",e.getKey());row.putString("Dimension",e.getValue().dimension());row.putLong("Position",e.getValue().position());ready.add(row);}n.put("Eligible",ready);var done=new ListTag();for(var id:claimed){var row=new CompoundTag();row.putUUID("Id",id);done.add(row);}n.put("Claimed",done);return n;}
}
