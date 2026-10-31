package com.dynasty.armorqa;

import com.dynasty.expansion.EquipmentBehaviors;
import com.dynasty.cod3.SecretTracker;
import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;
import static com.dynasty.armorqa.InteractionNetworkQa.*;

/** Uses the game's saved deadlines as read-only scheduling inputs. No accelerated clocks or direct use(). */
final class TimedInteractionWorkflow {
    static final Set<String> SUPPORTED=Set.of("battlefield_remnant","sword_scar_wall","wayside_shrine","nameless_tomb","old_weapon_rack","herb_spot","abandoned_armory","broken_stele","old_bellows","broken_waterwheel","mortuary_room","ghost_market_boat","wayside_tea_stall","ancient_well","puzzle_box");
    static final Set<Integer> complete=new HashSet<>(),replayed=new HashSet<>();
    static final List<Map<String,Object>> results=new ArrayList<>();
    static boolean waiting;
    static long started;
    static List<Map<String,Object>> battlefields;
    static boolean observerAck;
    static JsonObject site(int index,String phase)throws Exception{
        var original=SITES.get(index).getAsJsonObject();
        if(!id(index).equals("battlefield_remnant")||phase.equals("entry"))return original;
        if(battlefields==null){battlefields=NaturalBattlefieldSites.find(server.overworld(),pos(original.get("pos").getAsString()));write("additional-natural-battlefields.json",battlefields);}
        int count=EquipmentBehaviors.saved(players(server).get(1)).getInt("site_battlefield_remnant_count");
        return count==0?original:JSON.toJsonTree(battlefields.get(Math.min(1,count-1))).getAsJsonObject();
    }
    static String inventorySnapshot(ServerPlayer player){
        var all=new net.minecraft.nbt.CompoundTag();all.put("vanilla",player.getInventory().save(new net.minecraft.nbt.ListTag()));
        var curios=new net.minecraft.nbt.CompoundTag();
        top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(player).ifPresent(h->{
            for(var entry:new TreeMap<>(h.getCurios()).entrySet()){
                var slots=new net.minecraft.nbt.ListTag();var stacks=entry.getValue().getStacks();
                for(int i=0;i<stacks.getSlots();i++){var slot=new net.minecraft.nbt.CompoundTag();slot.putInt("slot",i);slot.put("stack",stacks.getStackInSlot(i).save(new net.minecraft.nbt.CompoundTag()));slots.add(slot);}curios.put(entry.getKey(),slots);
            }
        });all.put("curios",curios);return all.toString();
    }
    static Map<String,Integer> inventory(ServerPlayer player){
        var counts=new TreeMap<String,Integer>();
        for(var stack:player.getInventory().items)if(!stack.isEmpty())counts.merge(net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem()).toString(),stack.getCount(),Integer::sum);
        return counts;
    }
    static String id(int index){return SITES.get(index).getAsJsonObject().get("id").getAsString();}
    static String key(int index){return "site_"+id(index);}
    static float yaw(String id,String phase,ServerPlayer actor){
        if(!id.equals("puzzle_box")||phase.equals("entry"))return 180;
        return new float[]{180,-90,0,90}[Math.min(3,SecretTracker.puzzleCount(actor))];
    }
    static boolean sneak(String id,String phase,ServerPlayer actor){return id.equals("puzzle_box")&&!phase.equals("entry")&&SecretTracker.puzzleCount(actor)%2==1;}
    static void assertEntry(JsonObject command,ServerPlayer actor){
        String id=command.get("id").getAsString(),key="site_"+id;
        var root=EquipmentBehaviors.saved(actor);
        require(root.contains(key+"_start")&&root.contains(key+"_next"),"Real entry must establish original timers: "+id);
        require(!root.getBoolean(key+"_done"),"Entry alone must not count as completion: "+id);
        if(id.equals("ghost_market_boat"))require(root.getBoolean(key+"_talked"),"Real received dialogue talk choice must reach server");
        if(id.equals("wayside_tea_stall"))require(root.getBoolean(key+"_inspected")&&root.contains(key+"_drink_at"),"Real inspect/drink choices must reach server");
    }
    static void begin()throws Exception{started=server.overworld().getGameTime();waiting=true;schedule();}
    static void supplyNaturalFurnace(BlockPos site)throws Exception {
        var level=server.overworld();
        for(var at:BlockPos.betweenClosed(site.offset(-3,-1,-3),site.offset(3,2,3))){
            if(level.getBlockEntity(at) instanceof AbstractFurnaceBlockEntity furnace){
                // Supply an input to an existing naturally generated furnace; do not create a furnace or output.
                furnace.setItem(0,new ItemStack(Items.RAW_IRON));furnace.setChanged();
                write("natural-furnace-input-fixture.json",obj("site",site.toShortString(),"furnace",at.toShortString(),"input","minecraft:raw_iron","blocksPlaced",false));return;
            }
        }
        throw new AssertionError("No existing natural furnace near bellows");
    }
    static void schedule()throws Exception{
        var actor=players(server).get(1);var root=EquipmentBehaviors.saved(actor);long now=server.overworld().getGameTime();
        require(now-started<10000,"Bounded timed workflow exhausted");
        for(int n=0;n<15;n++)if(SUPPORTED.contains(id(n))&&!complete.contains(n)&&now>=root.getLong(key(n)+"_next")){
            waiting=false;prepare(n,"complete");return;
        }
        for(int n=0;n<15;n++)if(complete.contains(n)&&!replayed.contains(n)){
            waiting=false;prepare(n,"repeat");return;
        }
        if(complete.size()==SUPPORTED.size()&&replayed.size()==SUPPORTED.size()&&!observerAck){waiting=false;prepare(9,"observer_ack");}

    }
    static void assertRewards(JsonObject command,ServerPlayer actor,String id,boolean done){
        var expected=new TreeMap<String,Integer>();command.getAsJsonObject("actorInventoryBefore").entrySet().forEach(e->expected.put(e.getKey(),e.getValue().getAsInt()));
        if(id.equals("ancient_well")){expected.merge("minecraft:water_bucket",-1,Integer::sum);expected.merge("minecraft:bucket",1,Integer::sum);}
        if(done){
            String payment=switch(id){case "wayside_shrine"->"dynasty:soul_incense";case "nameless_tomb"->"minecraft:poppy";case "broken_stele"->"minecraft:paper";case "old_bellows"->"minecraft:charcoal";case "broken_waterwheel"->"dynasty:qimen_cable";case "ghost_market_boat"->"dynasty:cinnabar";case "mortuary_room"->"minecraft:potion";default->"";};
            if(!payment.isEmpty())expected.merge(payment,-1,Integer::sum);
            switch(id){
                case "old_weapon_rack"->expected.merge("dynasty:tie_jian",1,Integer::sum);
                case "herb_spot"->expected.merge("dynasty:tea",2,Integer::sum);
                case "abandoned_armory"->expected.merge("dynasty:qimen_gear",1,Integer::sum);
                case "old_bellows"->expected.merge("minecraft:iron_nugget",3,Integer::sum);
                case "broken_stele","broken_waterwheel","battlefield_remnant"->expected.merge("dynasty:copper_coin",2,Integer::sum);
                case "sword_scar_wall"->{expected.merge("dynasty:jade",1,Integer::sum);expected.merge("dynasty:copper_coin",2,Integer::sum);}
                case "ghost_market_boat"->{expected.merge("dynasty:bamboo_slip",1,Integer::sum);expected.merge("dynasty:copper_coin",2,Integer::sum);}
                case "puzzle_box"->{expected.merge("dynasty:blueprint",1,Integer::sum);expected.merge("dynasty:copper_coin",2,Integer::sum);}
                case "ancient_well"->expected.merge("dynasty:jade",1,Integer::sum);
                case "wayside_tea_stall"->expected.merge("dynasty:silk",1,Integer::sum);
                case "mortuary_room"->{expected.merge("dynasty:longyuan_sword",1,Integer::sum);expected.merge("minecraft:glass_bottle",1,Integer::sum);}
            }
        }
        expected.values().removeIf(v->v==0);require(expected.equals(inventory(actor)),"Exact native payment/reward inventory delta required: "+id+" expected="+expected+" actual="+inventory(actor));
    }
    static void accept(JsonObject command,ServerPlayer actor)throws Exception{
        String id=id(current),key=key(current);var root=EquipmentBehaviors.saved(actor);
        var before=net.minecraft.nbt.TagParser.parseTag(command.get("actorBefore").getAsString());
        require(root.getLong(key+"_start")==before.getLong(key+"_start"),"Native start deadline must survive revisit: "+id);
        int oldCount=before.getInt(key+"_count"),count=root.getInt(key+"_count");
        if(InteractionNetworkQa.phase.equals("observer_ack")){
            require(id.equals("broken_waterwheel")&&!before.getBoolean(key+"_done")&&root.getBoolean(key+"_done"),"Other player own native click acknowledges shared physical repair");
            require(command.getAsJsonObject("actorInventoryBefore").equals(JSON.toJsonTree(inventory(actor))),"Acknowledging already repaired shared wheel must neither charge nor reward player");
            require(command.get("actorStacksBefore").getAsString().equals(inventorySnapshot(actor)),"Shared acknowledgment must preserve every stack including equipment/offhand/Curios data");
            observerAck=true;write("shared-waterwheel-ack.json",obj("sequence",sequence,"player",actor.getUUID().toString(),"done",true,"inventoryUnchanged",true,"ownNativeClick",true));
            write("interaction-scope.json",obj("entryCases",15,"timedRoutes",complete.size(),"repeatedRoutes",replayed.size(),"sharedWaterwheelOtherPlayerAck",true,"wholeStoryCompletion",true,"elapsedTimersNotModified",true,"sceneBlocksManuallyPlaced",false,"independentVerificationRequired",true));
            mark("server-PASS");mark("server-COMPLETE");finished=true;return;
        }
        if(InteractionNetworkQa.phase.equals("repeat")){
            require(root.getBoolean(key+"_done")&&count==oldCount,"Repeat cannot increment completed progress: "+id);
            require(root.getLong(key+"_next")==before.getLong(key+"_next"),"Repeat cannot reset original next deadline: "+id);
            require(command.getAsJsonObject("actorInventoryBefore").equals(new com.google.gson.Gson().toJsonTree(inventory(actor))),"Repeat must not pay or reward any inventory item: "+id);
            require(command.get("actorStacksBefore").getAsString().equals(inventorySnapshot(actor)),"Repeat must preserve all slots and full item data: "+id);
            replayed.add(current);
        }else{
            if(id.equals("ancient_well"))require(count==oldCount+1&&actor.getMainHandItem().is(Items.BUCKET),"Each actual water delivery must consume exactly its supplied bucket");
            else if(id.equals("battlefield_remnant"))require(count==oldCount+1&&root.getBoolean(key+"_done")== (count==3),"Each actual distinct battlefield anchor advances once; exactly three required");
            else if(id.equals("puzzle_box"))require(SecretTracker.puzzleCount(actor)==oldCount+1||SecretTracker.puzzleClaimed(actor),"Native yaw/sneak puzzle step must advance");
            else require(root.getBoolean(key+"_done"),"Actual timed native use/dialogue must finish "+id);
            assertRewards(command,actor,id,root.getBoolean(key+"_done"));
            if(root.getBoolean(key+"_done"))complete.add(current);
        }
        results.add(obj("sequence",sequence,"site",id,"phase",InteractionNetworkQa.phase,"countBefore",oldCount,"countAfter",count,"done",root.getBoolean(key+"_done"),"worldTick",server.overworld().getGameTime(),"start",root.getLong(key+"_start"),"deadlineBefore",before.getLong(key+"_next"),"deadlineAfter",root.getLong(key+"_next"),"actorInventoryBefore",command.getAsJsonObject("actorInventoryBefore"),"actorInventoryAfter",inventory(actor),"actorStacksBefore",command.get("actorStacksBefore").getAsString(),"actorStacksAfter",inventorySnapshot(actor),"originalStartPreserved",true));
        write("interaction-timed-results.json",results);waiting=true;schedule();
    }
}
