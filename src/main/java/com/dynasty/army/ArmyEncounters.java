package com.dynasty.army;

import com.dynasty.*;
import com.dynasty.entity.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.*;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.*;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Solo commander instances in empty, checked cells of the existing Jiuxiao dimension.
 * No terrain removal. The roster and its encounter receipt share the player's save transaction.
 * Interrupted/restarted encounters evacuate without victory rewards, preserving recorded casualties.
 */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ArmyEncounters {
    public static final String[] BOSSES={"rebel_general","eunuch_mastermind","undead_first_emperor","nine_heaven_general","dragon_king","dragon_emperor"};
    public static final String[] NAMES={"叛将·破阵","宦官·咒台","亡帝·棺阵","天将·雷楔","龙王·潮道","龙帝·御军"};
    public static final ResourceKey<Level> DIM=com.dynasty.block.DynastyPortalBlock.JIUXIAO;
    private static final String KEY="Encounter";
    public static CompoundTag session(ServerPlayer p){return ArmyRoster.data(p).getCompound(KEY);}
    public static boolean active(ServerPlayer p){return session(p).getString("Phase").equals("ACTIVE");}
    public static boolean inside(ServerPlayer p){String phase=session(p).getString("Phase");return phase.equals("ACTIVE")||phase.equals("PREPARE");}
    private static void message(ServerPlayer p,String text){p.displayClientMessage(Component.literal("军阵 · "+text),false);}
    private static boolean completed(ServerPlayer p,String id){var a=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));return a!=null&&p.getAdvancements().getOrStartProgress(a).isDone();}
    public static boolean prepare(ServerPlayer p,int stage) {
        if(stage<0||stage>=BOSSES.length||inside(p)||!ArmyRoster.hasTally(p))return false;
        if(!completed(p,"exam_passed")&&!p.isCreative()){message(p,"科举中第后开放军阵关卡");return false;}
        for(var row:ArmyRoster.soldiers(p))if(((CompoundTag)row).getString("State").equals("DEPLOYED")){message(p,"先收回野外部队再入场");return false;}
        if(stage>0&&!p.getPersistentData().getBoolean("dynasty_firstkill_"+BOSSES[stage-1])&&!completed(p,"army_clear_"+BOSSES[stage-1])&&!p.isCreative()) {message(p,"先完成前一场首领战");return false;}
        var level=p.server.getLevel(DIM);if(level==null)return false;
        var allocator=p.server.overworld().getDataStorage().computeIfAbsent(Allocation::load,Allocation::new,"dynasty_army_cells");
        BlockPos center=null;
        for(int attempt=0;attempt<8;attempt++) {
            int index=allocator.next++;allocator.setDirty();if(index>=200000)return false;
            var candidate=new BlockPos(-2048-(index%512)*128,level.getMaxBuildHeight()-22,2048+(index/512)*128);
            boolean empty=true;
            outer:for(int x=-25;x<=25;x++)for(int z=-25;z<=25;z++)for(int y=-1;y<=8;y++)
                if(!level.isEmptyBlock(candidate.offset(x,y,z))){empty=false;break outer;}
            if(empty){center=candidate;break;}
        }
        if(center==null){message(p,"附近预留场地被占用，未改动地形");return false;}
        var c=center;
        for(int x=-25;x<=25;x++)for(int z=-25;z<=25;z++) {
            level.setBlock(c.offset(x,-1,z),(stage==4?Blocks.PRISMARINE_BRICKS:stage==2?Blocks.POLISHED_BLACKSTONE_BRICKS:Blocks.STONE_BRICKS).defaultBlockState(),2);
            if(Math.abs(x)==25||Math.abs(z)==25)for(int y=0;y<7;y++)level.setBlock(c.offset(x,y,z),Blocks.BARRIER.defaultBlockState(),2);
            if(x%8==0&&z%8==0)level.setBlock(c.offset(x,-1,z),Blocks.SEA_LANTERN.defaultBlockState(),2);
        }
        // Two cover lanes; the center remains wide enough for all five formation presets.
        for(int side:new int[]{-1,1})for(int z=-8;z<=8;z+=8)for(int y=0;y<3;y++)
            level.setBlock(c.offset(side*15,y,z),(stage==1?Blocks.CHISELED_QUARTZ_BLOCK:Blocks.CHISELED_STONE_BRICKS).defaultBlockState(),2);
        var s=new CompoundTag();s.putUUID("Id",UUID.randomUUID());s.putInt("Stage",stage);s.putString("Phase","PREPARE");s.putLong("Center",c.asLong());
        s.putString("ReturnDimension",p.level().dimension().location().toString());s.putDouble("ReturnX",p.getX());s.putDouble("ReturnY",p.getY());s.putDouble("ReturnZ",p.getZ());
        s.putFloat("ReturnYaw",p.getYRot());s.putLong("Created",p.server.overworld().getGameTime());
        ArmyRoster.data(p).put(KEY,s);p.closeContainer();p.teleportTo(level,c.getX()+.5,c.getY(),c.getZ()-17.5,0,0);
        message(p,"已进入"+NAMES[stage]+"；编队出阵后，在虎符中点击开战");return true;
    }
    public static boolean start(ServerPlayer p) {
        var s=session(p);if(!s.getString("Phase").equals("PREPARE")||p.level().dimension()!=DIM)return false;
        var troops=troops(p);if(troops.isEmpty()){message(p,"至少部署一名已购买的士兵");return false;}
        int stage=s.getInt("Stage");var c=BlockPos.of(s.getLong("Center"));var level=p.serverLevel();
        var type=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",BOSSES[stage]));
        if(type==null||!(type.create(level) instanceof Mob boss))return false;
        boss.moveTo(c.getX()+.5,c.getY(),c.getZ()+12.5,180,0);boss.setPersistenceRequired();
        boss.getPersistentData().putUUID("ArmyEncounter",s.getUUID("Id"));boss.getPersistentData().putUUID("ArmyCommander",p.getUUID());
        if(!level.addFreshEntity(boss))return false;
        s.putUUID("Boss",boss.getUUID());s.putString("Phase","ACTIVE");s.putLong("Started",p.server.overworld().getGameTime());
        // Freeze the owner's existing accessory bonuses once for this fight.
        ArmySupport.snapshot(p,troops);
        var locked=new ListTag();
        for(var soldier:troops) {
            var row=new CompoundTag();row.putUUID("Id",soldier.getPersistentData().getUUID("ArmySoldier"));
            row.putInt("Slot",soldier.getPersistentData().getInt("ArmySlot"));
            row.putInt("Role",soldier.getPersistentData().getInt("ArmyRole"));
            row.putLong("Generation",soldier.getPersistentData().getLong("ArmyGeneration"));locked.add(row);
        }
        s.put("LockedRoster",locked);ArmyRoster.changed(p);
        String guard=new String[]{"ludun_jiashi","fufa_jijiu","yinbing_guizu","liannu_zhenzu","bishui_xuanjiao_youzi","jade_guard"}[stage];
        var guardType=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",guard));
        if(guardType!=null)for(int side:new int[]{-1,1})if(guardType.create(level) instanceof Mob mob) {
            mob.moveTo(c.getX()+side*7+.5,c.getY(),c.getZ()+7.5,180,0);mob.setPersistenceRequired();
            mob.getPersistentData().putUUID("ArmyEncounter",s.getUUID("Id"));mob.getPersistentData().putUUID("ArmyCommander",p.getUUID());
            mob.setTarget(troops.get(0));level.addFreshEntity(mob);
        }
        boss.setTarget(troops.get(0));message(p,"开战：全军覆没、阵亡或离场即判败；战中不能调换兵册");return true;
    }
    private static List<ImperialSoldier> troops(ServerPlayer p) {
        return p.serverLevel().getEntitiesOfClass(ImperialSoldier.class,p.getBoundingBox().inflate(64),s->ArmyRoster.valid(s,p)&&s.isAlive());
    }
    public static void finish(ServerPlayer p,boolean victory,String reason) {
        if(!inside(p))return;var s=session(p);var level=p.server.getLevel(DIM);s.putString("Phase",victory?"WON":"LOST");
        if(level!=null&&s.hasUUID("Boss")&&level.getEntity(s.getUUID("Boss")) instanceof Mob boss) {
            if(!victory)boss.discard();
        }
        if(level!=null) {
            var center=Vec3.atCenterOf(BlockPos.of(s.getLong("Center")));
            for(var mob:level.getEntitiesOfClass(Mob.class,new AABB(center,center).inflate(32),m->m.getPersistentData().hasUUID("ArmyEncounter")&&m.getPersistentData().getUUID("ArmyEncounter").equals(s.getUUID("Id"))))
                if(mob.isAlive())mob.discard();
        }
        ArmyRoster.recallNow(p,true);
        // On crash recovery, an unconfirmed unloaded carrier is invalidated, never duplicated/refilled.
        for(var value:ArmyRoster.soldiers(p)) {var row=(CompoundTag)value;
            if(row.getString("State").equals("DEPLOYED")){row.putString("State","WOUNDED");row.putFloat("Health",0);row.remove("Entity");row.remove("RecallRequested");row.remove("RecallAt");row.remove("RecallForced");}}
        ArmyRoster.changed(p);

        if(victory) {
            String id=BOSSES[s.getInt("Stage")];
            DynastyBossCombat.grantFirstKill(p,id);
            DynastyWorldEvents.creditKill(p,net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",id)));
            for(var value:s.getList("Loot",10))deliver(p,net.minecraft.world.item.ItemStack.of((CompoundTag)value));
            s.remove("Loot");
            var a=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","army_clear_"+id));
            if(a!=null)p.getAdvancements().award(a,"code");
            for(String name:new String[]{"slay_"+id,id.equals("undead_first_emperor")?"slay_emperor":"slay_"+id}) {
                var adv=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",name));
                if(adv!=null)for(String criterion:p.getAdvancements().getOrStartProgress(adv).getRemainingCriteria())p.getAdvancements().award(adv,criterion);
            }
        }
        message(p,(victory?"胜利":"撤离")+" · "+reason);
        evacuate(p,s);
    }
    private static void evacuate(ServerPlayer p,CompoundTag s) {
        if(!p.isAlive())return;
        var key=ResourceKey.create(Registries.DIMENSION,new ResourceLocation(s.getString("ReturnDimension")));var home=p.server.getLevel(key);
        if(home==null)home=p.server.overworld();
        p.teleportTo(home,s.getDouble("ReturnX"),s.getDouble("ReturnY"),s.getDouble("ReturnZ"),s.getFloat("ReturnYaw"),0);
        s.putBoolean("Returned",true);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%10!=0||!inside(p))return;
        var s=session(p);var c=Vec3.atCenterOf(BlockPos.of(s.getLong("Center")));
        if(p.level().dimension()!=DIM||Math.abs(p.getX()-c.x)>24||Math.abs(p.getZ()-c.z)>24||p.getY()<c.y-4){finish(p,false,"离开战区");return;}
        long now=p.server.overworld().getGameTime();
        if(!active(p)){if(now-s.getLong("Created")>2400)finish(p,false,"备战超时");return;}
        var troops=troops(p); // Win/wipe decisions use one server END-tick snapshot below.
        if(now-s.getLong("Started")>18000){finish(p,false,"战斗超时");return;}
        if(p.serverLevel().getEntity(s.getUUID("Boss")) instanceof Mob boss) {
            var nearest=troops.stream().min(Comparator.comparingDouble(boss::distanceToSqr)).orElse(null);
            if(nearest!=null&&boss.distanceToSqr(nearest)<24*24)boss.setTarget(nearest);
            // Keep summons inside this encounter's bounds and tie credit to its commander.
            for(var minion:p.serverLevel().getEntitiesOfClass(Mob.class,new AABB(c,c).inflate(24),m->m!=boss&&m instanceof net.minecraft.world.entity.monster.Enemy)) {
                minion.getPersistentData().putUUID("ArmyEncounter",s.getUUID("Id"));minion.getPersistentData().putUUID("ArmyCommander",p.getUUID());
                if(nearest!=null)minion.setTarget(nearest);
            }
        }
    }
    /** One outcome after all living entities have ticked, independent of death-event order. */
    static void settleOutcome(ServerPlayer p) {
        if(!active(p))return;
        var s=session(p);
        if(s.getBoolean("BossDefeated")) {finish(p,true,"首领倒下（保留全部战损）");return;}
        if(s.getBoolean("CommanderDefeated")||!p.isAlive()) {finish(p,false,"主将阵亡");return;}
        if(troops(p).isEmpty())finish(p,false,"全军覆没");
    }
    @SubscribeEvent public static void settle(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END)return;
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server==null)return;
        var players=new HashSet<ServerPlayer>();
        for(var level:server.getAllLevels())players.addAll(level.players());
        for(var player:players)settleOutcome(player);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void death(LivingDeathEvent e) {
        if(e.getEntity() instanceof ServerPlayer p) {
            if(active(p))session(p).putBoolean("CommanderDefeated",true);
            else if(inside(p))finish(p,false,"主将阵亡");
            return;
        }
        var n=e.getEntity().getPersistentData();
        if(!n.hasUUID("ArmyCommander")||!n.hasUUID("ArmyEncounter")||!(e.getEntity().level() instanceof ServerLevel l))return;
        var p=commander(l,n.getUUID("ArmyCommander"));
        if(p!=null&&active(p)&&session(p).hasUUID("Boss")&&session(p).getUUID("Boss").equals(e.getEntity().getUUID())
                &&session(p).getUUID("Id").equals(n.getUUID("ArmyEncounter"))) {
            session(p).putBoolean("BossDefeated",true);
            session(p).putLong("BossDefeatedTick",p.server.overworld().getGameTime());ArmyRoster.changed(p);
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p&&inside(p)){settleOutcome(p);if(inside(p))finish(p,false,"主将离线，保留战损");}}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(e.getEntity() instanceof ServerPlayer p){if(inside(p))finish(p,false,"服务器中断，保留战损安全撤出");else if(session(p).contains("Id")&&!session(p).getBoolean("Returned"))evacuate(p,session(p));}}
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent e){if(e.getEntity() instanceof ServerPlayer p&&session(p).contains("Id")&&!session(p).getBoolean("Returned"))evacuate(p,session(p));}
    @SubscribeEvent public static void breakBlock(BlockEvent.BreakEvent e){if(e.getPlayer() instanceof ServerPlayer p&&inside(p))e.setCanceled(true);}
    @SubscribeEvent public static void placeBlock(BlockEvent.EntityPlaceEvent e){if(e.getEntity() instanceof ServerPlayer p&&inside(p))e.setCanceled(true);}
    private static ServerPlayer commander(ServerLevel level,UUID id) {
        var player=level.getServer().getPlayerList().getPlayer(id);if(player!=null)return player;
        for(var world:level.getServer().getAllLevels())if(world.getPlayerByUUID(id) instanceof ServerPlayer p)return p;
        return null;
    }
    private static void deliver(ServerPlayer p,net.minecraft.world.item.ItemStack stack) {
        if(!p.getInventory().add(stack))p.drop(stack,false);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void loot(LivingDropsEvent e) {
        var tag=e.getEntity().getPersistentData();if(!(e.getEntity().level() instanceof ServerLevel l)||!tag.hasUUID("ArmyCommander"))return;
        var p=commander(l,tag.getUUID("ArmyCommander"));
        if(p!=null&&session(p).hasUUID("Id")&&session(p).getUUID("Id").equals(tag.getUUID("ArmyEncounter"))) {
            var s=session(p);var receipts=s.getCompound("LootReceipts");String id=e.getEntity().getUUID().toString();
            if(!receipts.getBoolean(id)) {
                receipts.putBoolean(id,true);s.put("LootReceipts",receipts);
                if(s.getString("Phase").equals("WON"))for(var drop:e.getDrops())deliver(p,drop.getItem().copy());
                else if(active(p)){var bank=s.getList("Loot",10);for(var drop:e.getDrops())if(bank.size()<128)bank.add(drop.getItem().save(new CompoundTag()));s.put("Loot",bank);}
            }
        }
        e.getDrops().clear();
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void outsiderDamage(LivingHurtEvent e) {
        var tag=e.getEntity().getPersistentData();
        if(!tag.hasUUID("ArmyCommander")||!(e.getEntity().level() instanceof ServerLevel))return;
        var credited=ArmySupport.owner(e.getSource());
        if(credited!=null&&!credited.getUUID().equals(tag.getUUID("ArmyCommander")))e.setCanceled(true);
    }
    @SubscribeEvent public static void explosions(net.minecraftforge.event.level.ExplosionEvent.Detonate e) {
        if(e.getLevel().isClientSide)return;
        for(var player:e.getLevel().players())if(player instanceof ServerPlayer p&&inside(p)) {
            var c=BlockPos.of(session(p).getLong("Center"));e.getAffectedBlocks().removeIf(b->Math.abs(b.getX()-c.getX())<=25&&Math.abs(b.getZ()-c.getZ())<=25&&Math.abs(b.getY()-c.getY())<10);
        }
    }
    @SubscribeEvent public static void restored(net.minecraftforge.event.entity.EntityJoinLevelEvent e) {
        var tag=e.getEntity().getPersistentData();
        if(e.getLevel().isClientSide||!tag.hasUUID("ArmyCommander")||!tag.hasUUID("ArmyEncounter"))return;
        var p=commander((ServerLevel)e.getLevel(),tag.getUUID("ArmyCommander"));
        if(p==null||!inside(p)||!session(p).getUUID("Id").equals(tag.getUUID("ArmyEncounter")))e.setCanceled(true);
    }
    private static final class Allocation extends SavedData {
        int next;static Allocation load(CompoundTag n){var a=new Allocation();a.next=n.getInt("Next");return a;}
        @Override public CompoundTag save(CompoundTag n){n.putInt("Next",next);return n;}
    }
    private ArmyEncounters(){}
}
