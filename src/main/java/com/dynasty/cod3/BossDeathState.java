package com.dynasty.cod3;

import com.dynasty.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Capture the existing death pipeline, delay loot/XP, persist a journal until cleanup. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class BossDeathState extends SavedData {
    public static final String KEY="dynasty_cod3_death";
    private final Map<UUID,CompoundTag> entries=new LinkedHashMap<>();
    private final Set<UUID> pending=new LinkedHashSet<>();
    public static BossDeathState get(ServerLevel l){return l.getDataStorage().computeIfAbsent(BossDeathState::load,BossDeathState::new,"dynasty_cod3_deaths");}
    private static BossDeathState load(CompoundTag n){var s=new BossDeathState();for(var t:n.getList("Entries",10)){var c=(CompoundTag)t;s.entries.put(c.getUUID("Boss"),c);if(!c.getBoolean("Cleaned"))s.pending.add(c.getUUID("Boss"));}return s;}
    @Override public CompoundTag save(CompoundTag n){var list=new ListTag();entries.values().forEach(list::add);n.put("Entries",list);return n;}
    public static boolean managed(LivingEntity boss){return boss.getPersistentData().getBoolean(KEY);}
    @SubscribeEvent(priority=EventPriority.HIGHEST)
    public static void death(LivingDeathEvent e){
        if(!(e.getEntity() instanceof Mob boss)||!(boss.level() instanceof ServerLevel l))return;
        var id=ForgeRegistries.ENTITY_TYPES.getKey(boss.getType());var def=Cod3Catalog.sequence("deaths",id.toString());if(def==null)return;
        var data=get(l);if(data.entries.containsKey(boss.getUUID()))return;
        var n=new CompoundTag();n.putBoolean("PreviousNoAi",boss.isNoAi());n.putBoolean("PreviousInvulnerable",boss.isInvulnerable());n.putUUID("Boss",boss.getUUID());n.putString("Sequence",def.id());n.putString("Type",id.toString());n.putLong("Start",l.getGameTime());n.putInt("Duration",def.totalTicks());n.putLong("Position",boss.blockPosition().asLong());n.put("Loot",new ListTag());n.putInt("XP",0);
        if(boss.getKillCredit()!=null)n.putUUID("Killer",boss.getKillCredit().getUUID());
        data.entries.put(boss.getUUID(),n);data.pending.add(boss.getUUID());data.setDirty();boss.getPersistentData().putBoolean(KEY,true);boss.setNoAi(true);boss.setInvulnerable(true);boss.setTarget(null);
        if(boss instanceof DynastyBossCombat.BarHolder holder)holder.dynastyBossBar().setVisible(false);
        // Do not cancel death: advancement/kill credit and other mod death hooks still run.
    }
    @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true)
    public static void canceledDeath(LivingDeathEvent e){
        if(e.isCanceled()&&e.getEntity() instanceof Mob boss&&boss.level() instanceof ServerLevel l)rollback(l,boss);
    }
    private static void rollback(ServerLevel level,Mob boss){
        var data=get(level);var previous=data.entries.remove(boss.getUUID());data.pending.remove(boss.getUUID());
        if(previous==null)return;
        boss.getPersistentData().remove(KEY);boss.setNoAi(previous.getBoolean("PreviousNoAi"));boss.setInvulnerable(previous.getBoolean("PreviousInvulnerable"));
        if(boss instanceof DynastyBossCombat.BarHolder holder)holder.dynastyBossBar().setVisible(true);
        data.setDirty();
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void drops(LivingDropsEvent e){
        if(!managed(e.getEntity())||!(e.getEntity().level() instanceof ServerLevel l))return;
        var d=get(l);var n=d.entries.get(e.getEntity().getUUID());if(n==null)return;
        if(!n.getBoolean("Captured")){var list=new ListTag();for(var drop:e.getDrops())list.add(drop.getItem().save(new CompoundTag()));n.put("Loot",list);n.putBoolean("Captured",true);d.setDirty();}
        e.getDrops().clear();
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void xp(LivingExperienceDropEvent e){
        if(!managed(e.getEntity())||!(e.getEntity().level() instanceof ServerLevel l))return;
        var d=get(l);var n=d.entries.get(e.getEntity().getUUID());if(n!=null&&!n.getBoolean("XPCaptured")){n.putInt("XP",e.getDroppedExperience());n.putBoolean("XPCaptured",true);d.setDirty();}e.setDroppedExperience(0);
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST)
    public static void tickCorpse(LivingEvent.LivingTickEvent e){
        if(!managed(e.getEntity())||e.getEntity().level().isClientSide)return;
        // Prevent vanilla's 20-tick removal. State progression is independent of a loaded corpse.
        e.setCanceled(true);
    }
    @SubscribeEvent public static void server(TickEvent.LevelTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel l))return;
        var data=get(l);var iterator=data.pending.iterator();
        while(iterator.hasNext()){
            var uuid=iterator.next();var n=data.entries.get(uuid);long age=l.getGameTime()-n.getLong("Start");
            Entity entity=l.getEntity(uuid);
            if(entity instanceof Mob revived&&revived.isAlive()){
                // Resurrection may happen after LivingDeathEvent. Never freeze a revived mob.
                iterator.remove();data.entries.remove(uuid);revived.getPersistentData().remove(KEY);
                revived.setNoAi(n.getBoolean("PreviousNoAi"));revived.setInvulnerable(n.getBoolean("PreviousInvulnerable"));
                if(revived instanceof DynastyBossCombat.BarHolder holder)holder.dynastyBossBar().setVisible(true);
                data.setDirty();continue;
            }
            if(entity instanceof Mob boss&&age>=0&&age<n.getInt("Duration")){
                var def=Cod3Catalog.sequence("deaths",n.getString("Type"));
                if(def!=null)for(var step:def.steps())if(age==step.startTick())try{if(step.type()==BossSequenceDefinition.Type.SPAWN_CLIENT_VFX)Cod3Vfx.sequence(boss,def.id(),(int)age,step);else BossSequenceRunner.play(boss,step);}catch(RuntimeException ex){Dynasty.LOGGER.warn("cod3 death effect skipped",ex);}
            }
            if(age<n.getInt("Duration")&&!n.getBoolean("RewardGranted"))continue;
            BlockPos pos=BlockPos.of(n.getLong("Position"));if(!l.hasChunkAt(pos))continue;
            try {
                if(!n.getBoolean("RewardGranted")){
                    reward(l,pos,n);n.putBoolean("RewardGranted",true);data.setDirty();
                    if(entity instanceof Mob boss)boss.getPersistentData().putBoolean("dynasty_reward_granted",true);
                    if(n.hasUUID("Killer")){var player=l.getServer().getPlayerList().getPlayer(n.getUUID("Killer"));if(player!=null){DynastyBossCombat.grantFirstKill(player,new net.minecraft.resources.ResourceLocation(n.getString("Type")).getPath());n.putBoolean("FirstKillGranted",true);}}
                    Cod3WorldState.bossDefeated(l,n.getString("Type"));
                }
                if(entity!=null)entity.remove(Entity.RemovalReason.KILLED);
                // Keep completion tombstones so a stale saved corpse cannot generate another reward.
                n.putBoolean("Cleaned",true);iterator.remove();data.setDirty();
            }catch(RuntimeException ex){Dynasty.LOGGER.error("cod3 reward remains pending boss={}",uuid,ex);}
        }
    }
    @SubscribeEvent public static void login(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent event){
        if(!(event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player))return;
        for(var level:player.server.getAllLevels()){
            var data=get(level);
            for(var n:data.entries.values())if(n.getBoolean("RewardGranted")&&!n.getBoolean("FirstKillGranted")&&n.hasUUID("Killer")&&n.getUUID("Killer").equals(player.getUUID())){
                DynastyBossCombat.grantFirstKill(player,new net.minecraft.resources.ResourceLocation(n.getString("Type")).getPath());n.putBoolean("FirstKillGranted",true);data.setDirty();
            }
        }
    }
    @SubscribeEvent public static void join(net.minecraftforge.event.entity.EntityJoinLevelEvent e){
        if(!(e.getEntity() instanceof Mob boss)||!(e.getLevel() instanceof ServerLevel l)||!managed(boss))return;
        var n=get(l).entries.get(boss.getUUID());
        if(n!=null&&n.getBoolean("Cleaned"))e.setCanceled(true);
        else if(n==null){boss.getPersistentData().remove(KEY);boss.setNoAi(false);boss.setInvulnerable(false);}
    }
    @SubscribeEvent public static void tracking(net.minecraftforge.event.entity.player.PlayerEvent.StartTracking e){
        if(e.getEntity() instanceof net.minecraft.server.level.ServerPlayer p&&e.getTarget() instanceof Mob boss&&managed(boss)&&boss.level() instanceof ServerLevel level){
            var state=get(level).entries.get(boss.getUUID());if(state!=null&&!state.getBoolean("Cleaned"))Cod3Vfx.sync(p,boss,state.getString("Sequence"),(int)(level.getGameTime()-state.getLong("Start")),state.getInt("Duration"));
        }
    }
    private static void reward(ServerLevel l,BlockPos pos,CompoundTag n){
        if(n.getBoolean("LootPlaced")&&n.getBoolean("XPAwarded"))return;
        BlockPos place=null;
        for(int dy=0;dy<4&&place==null;dy++)for(int dx=-2;dx<=2&&place==null;dx++)for(int dz=-2;dz<=2;dz++){
            var p=pos.offset(dx,dy,dz);if(l.getBlockState(p).isAir()&&l.getBlockState(p.below()).isSolidRender(l,p.below())){place=p;break;}
        }
        var stacks=new ArrayList<ItemStack>();for(var tag:n.getList("Loot",10))stacks.add(ItemStack.of((CompoundTag)tag));
        if(!n.getBoolean("LootPlaced")){
            // Phase receipts prevent a later XP/world-feedback failure from re-placing loot.
            // SavedData and chunks still use Minecraft's normal save boundary.
            if(place!=null&&l.setBlock(place,LootableRemains.BLOCK.get().defaultBlockState(),3)&&l.getBlockEntity(place) instanceof LootableRemains.Remains remains){
                int i=0;for(var s:stacks){if(i<54)remains.setItem(i++,s);else net.minecraft.world.level.block.Block.popResource(l,place,s);}remains.setChanged();
            }else for(var s:stacks)net.minecraft.world.level.block.Block.popResource(l,pos,s);
            n.putBoolean("LootPlaced",true);get(l).setDirty();
        }
        if(!n.getBoolean("XPAwarded")){ExperienceOrb.award(l,net.minecraft.world.phys.Vec3.atCenterOf(pos),n.getInt("XP"));n.putBoolean("XPAwarded",true);get(l).setDirty();}
    }
}
