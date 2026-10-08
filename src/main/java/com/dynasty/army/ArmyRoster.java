package com.dynasty.army;

import com.dynasty.*;
import com.dynasty.entity.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Server-owned roster stored with its owner's inventory, so one player save contains both sides of a purchase. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ArmyRoster {
    public static final int CAPACITY=36, DEPLOY_LIMIT=9, RECALL_TICKS=40;
    public static final String KEY="DynastyArmyV1";
    public static final String[] ROLES={"刀卫","弩卫","盾卫"};
    public static final int[] PRICE={12,16,20}; // Existing silver_coin currency, not a new token.
    public static final float[] HEALTH={1800,1300,2600};
    public static CompoundTag data(Player p) {
        var root=p.getPersistentData();
        if(!root.contains(KEY,10)) {var n=new CompoundTag();n.put("Soldiers",new ListTag());root.put(KEY,n);}
        return root.getCompound(KEY);
    }
    public static ListTag soldiers(Player p){return data(p).getList("Soldiers",10);}
    public static CompoundTag find(Player p,UUID id) {
        for(var n:soldiers(p))if(((CompoundTag)n).hasUUID("Id")&&((CompoundTag)n).getUUID("Id").equals(id))return (CompoundTag)n;
        return null;
    }
    public static boolean hasTally(Player p){return p.getMainHandItem().is(DynastyItems.TIGER_TALLY.get())||p.getOffhandItem().is(DynastyItems.TIGER_TALLY.get());}
    public static int coins(Player p) {
        int count=0;for(var stack:p.getInventory().items)if(stack.is(DynastyItems.SILVER_COIN.get()))count+=stack.getCount();return count;
    }
    private static boolean pay(Player p,int price) {
        if(coins(p)<price)return false;
        for(var stack:p.getInventory().items)if(stack.is(DynastyItems.SILVER_COIN.get())) {
            int n=Math.min(price,stack.getCount());stack.shrink(n);price-=n;if(price==0)break;
        }
        p.getInventory().setChanged();return true;
    }
    public static boolean recruit(ServerPlayer p,int role) {
        if(ArmyEncounters.active(p)||role<0||role>=ROLES.length||soldiers(p).size()>=CAPACITY||!pay(p,PRICE[role]))return false;
        var n=new CompoundTag();n.putUUID("Id",UUID.randomUUID());n.putInt("Role",role);n.putFloat("Health",HEALTH[role]);
        n.putString("State","RESERVE");n.putInt("Slot",-1);soldiers(p).add(n);changed(p);return true;
    }
    public static boolean repair(ServerPlayer p,int index) {
        var list=soldiers(p);if(index<0||index>=list.size())return false;var n=list.getCompound(index);
        int role=n.getInt("Role");
        if(ArmyEncounters.active(p)||role<0||role>=ROLES.length||!n.getString("State").equals("WOUNDED")
                ||!pay(p,Math.max(1,PRICE[role]/4-(DynastyTrinkets.activeIds(p).contains("imperial_seal_charm")?1:0))))return false;
        n.putFloat("Health",HEALTH[role]);n.putString("State","RESERVE");
        // Keep the paid soldier's equipment and attack cooldown through treatment.
        if(n.contains("EntityData",10)) {
            var saved=n.getCompound("EntityData");saved.putFloat("Health",HEALTH[role]);
            saved.putShort("DeathTime",(short)0);saved.putShort("HurtTime",(short)0);
        }
        clearRecall(n);changed(p);return true;
    }
    public static void changed(ServerPlayer p) { data(p).putInt("Revision",data(p).getInt("Revision")+1); }
    public static Vec3 slot(Vec3 center,float yaw,int index,int formation) {
        double x=(index%3-1)*2.5,z=2.5+(index/3)*2.5;
        if(formation==1){x*=1.5;z+=Math.abs(x)*.45;}
        if(formation==2){x*=1.7;z*=1.3;}
        if(formation==3){x=(index-4)*2.3;z=3;}
        if(formation==4){double a=index*Math.PI*2/9;x=Math.cos(a)*5;z=Math.sin(a)*5;}
        double a=Math.toRadians(yaw);return center.add(x*Math.cos(a)-z*Math.sin(a),0,x*Math.sin(a)+z*Math.cos(a));
    }
    public static int deploy(ServerPlayer p,int formation,int count) {
        if(ArmyEncounters.active(p)||!hasTally(p)||formation<0||formation>=5||count<1||count>DEPLOY_LIMIT)return 0;
        for(var v:soldiers(p))if(((CompoundTag)v).getString("State").equals("DEPLOYED"))return 0;
        var chosen=new ArrayList<CompoundTag>();
        var usedSlots=new HashSet<Integer>();var usedIds=new HashSet<UUID>();
        for(var v:soldiers(p)) {
            var row=(CompoundTag)v;
            if(!row.getString("State").equals("RESERVE")||row.getInt("Slot")<0)continue;
            int slot=row.getInt("Slot"),role=row.getInt("Role");float hp=row.getFloat("Health");
            if(slot>=DEPLOY_LIMIT||!row.hasUUID("Id")||!usedSlots.add(slot)||!usedIds.add(row.getUUID("Id"))
                    ||role<0||role>=ROLES.length||!Float.isFinite(hp)||hp<=0)return 0;
            chosen.add(row);
        }
        // Never silently deploy just the first part of a saved formation.
        if(chosen.isEmpty()||chosen.size()>count)return 0;
        var made=new ArrayList<ImperialSoldier>();var level=p.serverLevel();
        for(int i=0;i<chosen.size();i++) {
            var record=chosen.get(i);var soldier=DynastyEntities.IMPERIAL_SOLDIER.get().create(level);
            if(soldier==null)return 0;
            if(record.contains("EntityData",10)) {var n=record.getCompound("EntityData").copy();n.remove("UUID");soldier.load(n);}
            soldier.setOwner(p);soldier.getPersistentData().putUUID("ArmySoldier",record.getUUID("Id"));
            soldier.getPersistentData().putLong("ArmyGeneration",record.getLong("Generation")+1);
            soldier.getPersistentData().putInt("ArmyRole",record.getInt("Role"));soldier.getPersistentData().putInt("ArmySlot",record.getInt("Slot"));
            soldier.getPersistentData().putFloat("ArmyYaw",p.getYRot());soldier.getPersistentData().putInt("ArmyFormation",formation);
            soldier.setPersistenceRequired();soldier.setCanPickUpLoot(false);
            if(!record.contains("EntityData",10))equip(soldier,record.getInt("Role"));
            soldier.setHealth(Math.min(record.getFloat("Health"),soldier.getMaxHealth()));
            Vec3 target=slot(p.position(),p.getYRot(),record.getInt("Slot"),formation);
            var floor=net.minecraft.core.BlockPos.containing(target).below();
            if(!level.hasChunkAt(floor)||!level.getBlockState(floor).isFaceSturdy(level,floor,net.minecraft.core.Direction.UP))return 0;
            soldier.moveTo(target.x,target.y,target.z,p.getYRot(),0);
            if(!level.noCollision(soldier)||!level.getFluidState(soldier.blockPosition()).isEmpty())return 0;
            made.add(soldier);
        }
        for(var soldier:made)if(!level.addFreshEntity(soldier)) {made.forEach(Entity::discard);return 0;}
        for(int i=0;i<made.size();i++) {
            var r=chosen.get(i);clearRecall(r);r.putLong("Generation",made.get(i).getPersistentData().getLong("ArmyGeneration"));r.putString("State","DEPLOYED");r.putUUID("Entity",made.get(i).getUUID());
            r.putString("Dimension",level.dimension().location().toString());r.putInt("Slot",made.get(i).getPersistentData().getInt("ArmySlot"));
        }
        changed(p);
        var advancement=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","army_led"));
        if(advancement!=null)for(String criterion:p.getAdvancements().getOrStartProgress(advancement).getRemainingCriteria())p.getAdvancements().award(advancement,criterion);
        return made.size();
    }
    private static void equip(ImperialSoldier s,int role) {
        s.getAttribute(Attributes.MAX_HEALTH).setBaseValue(HEALTH[role]);
        s.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(role==1?170:role==2?140:260);
        s.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(role==1?Items.CROSSBOW:Items.IRON_SWORD));
        if(role==2)s.setItemSlot(EquipmentSlot.OFFHAND,new ItemStack(Items.SHIELD));
        s.setItemSlot(EquipmentSlot.HEAD,new ItemStack(Items.IRON_HELMET));
        s.setItemSlot(EquipmentSlot.CHEST,new ItemStack(Items.IRON_CHESTPLATE));
        for(var slot:EquipmentSlot.values())s.setDropChance(slot,0);
    }
    public static int recall(ServerPlayer p) {
        if(ArmyEncounters.active(p))return 0;
        return recallNow(p,false);
    }
    private static long clock(ServerPlayer p){return p.server.overworld().getGameTime();}
    private static void clearRecall(CompoundTag r) {
        r.remove("RecallRequested");r.remove("RecallAt");r.remove("RecallForced");
    }
    static int recallNow(ServerPlayer p,boolean forced) {
        int count=0;
        for(var v:soldiers(p)) {
            var r=(CompoundTag)v;if(!r.getString("State").equals("DEPLOYED")||!r.hasUUID("Entity"))continue;
            // A repeated click must not restart or shorten the channel.
            if(!r.getBoolean("RecallRequested"))r.putLong("RecallAt",clock(p)+RECALL_TICKS);
            r.putBoolean("RecallRequested",true);
            if(forced){r.putBoolean("RecallForced",true);r.putLong("RecallAt",clock(p));}
            count++;
            for(var level:p.server.getAllLevels())if(level.getEntity(r.getUUID("Entity")) instanceof ImperialSoldier soldier) {
                completeRecall(p,soldier);break;
            }
        }
        if(count>0)changed(p);return count;
    }
    /** Called by the carrier after reload too; no chunk loads or missing-entity replacement. */
    public static boolean completeRecall(ServerPlayer p,ImperialSoldier soldier) {
        if(!valid(soldier,p)||ArmyEncounters.active(p))return false;
        var r=find(p,soldier.getPersistentData().getUUID("ArmySoldier"));
        if(!r.getBoolean("RecallRequested"))return false;
        // Legacy pending recalls receive a full channel once instead of skipping it.
        if(!r.contains("RecallAt",99))r.putLong("RecallAt",clock(p)+RECALL_TICKS);
        if(!r.getBoolean("RecallForced")&&clock(p)<r.getLong("RecallAt"))return false;
        snapshot(r,soldier);r.putString("State",soldier.isAlive()?"RESERVE":"WOUNDED");
        r.remove("Entity");clearRecall(r);changed(p);soldier.discard();return true;
    }
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST) public static void damaged(net.minecraftforge.event.entity.living.LivingDamageEvent event) {
        if(event.getAmount()<=0||!(event.getEntity() instanceof ImperialSoldier s)
                ||!(s.getOwner() instanceof ServerPlayer p)||!valid(s,p))return;
        var r=find(p,s.getPersistentData().getUUID("ArmySoldier"));
        if(r.getBoolean("RecallRequested")&&!r.getBoolean("RecallForced")) {
            r.putLong("RecallAt",clock(p)+RECALL_TICKS);changed(p);
        }
    }
    public static void snapshot(CompoundTag r,ImperialSoldier s) {r.putFloat("Health",s.getHealth());r.put("EntityData",s.saveWithoutId(new CompoundTag()));}
    public static boolean valid(ImperialSoldier s,ServerPlayer owner) {
        if(!s.getPersistentData().hasUUID("ArmySoldier"))return false;
        var r=find(owner,s.getPersistentData().getUUID("ArmySoldier"));
        return s.getOwner()!=null&&s.getOwner().getUUID().equals(owner.getUUID())
                &&r!=null&&r.getString("State").equals("DEPLOYED")&&r.hasUUID("Entity")&&r.getUUID("Entity").equals(s.getUUID())
                &&r.getLong("Generation")==s.getPersistentData().getLong("ArmyGeneration")
                &&(!r.contains("Dimension",8)||r.getString("Dimension").equals(s.level().dimension().location().toString()));
    }
    @SubscribeEvent public static void death(LivingDeathEvent event) {
        if(event.getEntity() instanceof ServerPlayer owner&&!ArmyEncounters.inside(owner))recallNow(owner,true);
        if(event.getEntity() instanceof ImperialSoldier s&&s.getOwner() instanceof ServerPlayer p&&valid(s,p)) {
            var r=find(p,s.getPersistentData().getUUID("ArmySoldier"));snapshot(r,s);r.putString("State","WOUNDED");r.remove("Entity");clearRecall(r);changed(p);
            s.setDropChance(EquipmentSlot.MAINHAND,0);s.setDropChance(EquipmentSlot.OFFHAND,0);
        }
    }
    @SubscribeEvent public static void clone(PlayerEvent.Clone e) {if(e.getOriginal().getPersistentData().contains(KEY))e.getEntity().getPersistentData().put(KEY,data(e.getOriginal()).copy());}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e) {if(e.getEntity() instanceof ServerPlayer p&&!ArmyEncounters.inside(p))recallNow(p,true);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e) {if(e.getEntity() instanceof ServerPlayer p&&!ArmyEncounters.inside(p))recallNow(p,true);}
    private ArmyRoster(){}
}
