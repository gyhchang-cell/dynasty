package com.dynasty.structure;

import com.dynasty.expansion.*;
import com.dynasty.cod3.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.*;
import static com.dynasty.structure.InteractionAcceptance.*;

/** Real world ticks; no rewriting *_start, *_next, native Last or completion fields. */
@GameTestHolder("dynasty_interaction_qa") @PrefixGameTestTemplate(false)
public final class InteractionTimedAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_real_clock",timeoutTicks=3700)
    public static void realElapsedTicksCompleteNineGenericSitesWithoutRepeatedRewardsOrPersonalLeakage(GameTestHelper h){
        var positions=new HashMap<String,BlockPos>();
        for(int s=0;s<3;s++){
            var piece=build(h,s,Direction.NORTH,new BlockPos(2048+s*64,80,2048));
            for(int i=0;i<5;i++)positions.put(IDS[s][i],piece.point(5+i*4,1,28));
        }
        // Three genuinely different production battlefield anchors, not copied coordinates.
        var extraA=build(h,2,Direction.WEST,new BlockPos(2240,80,2048));var extraB=build(h,2,Direction.EAST,new BlockPos(2304,80,2048));
        var battle=List.of(positions.get("battlefield_remnant"),extraA.point(9,1,28),extraB.point(9,1,28));
        var durations=new LinkedHashMap<String,Integer>();for(String id:List.of("wayside_shrine","old_weapon_rack","broken_stele","old_bellows"))durations.put(id,600);
        for(String id:List.of("nameless_tomb","herb_spot","broken_waterwheel","battlefield_remnant"))durations.put(id,1200);durations.put("abandoned_armory",3600);
        long start=h.getLevel().getGameTime();long base=h.getTick();int[] completed={0};
        for(var entry:durations.entrySet()){
            String id=entry.getKey();int duration=entry.getValue();var at=positions.get(id);var p=player(h,at.north());var q=player(h,at.north());p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));
            if(id.equals("old_bellows")){
                // Existing real furnace placed by style2's production postProcess.
                var piece=new Piece(new BlockPos(2176,80,2048),2,Direction.NORTH);var furnaceAt=piece.point(17,1,26);
                var furnace=(net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity)h.getLevel().getBlockEntity(furnaceAt);
                h.assertTrue(furnace!=null,"Production furnace exists within native assist search");furnace.setItem(0,new ItemStack(Items.RAW_IRON));
            }
            use(h,p,at);String key="site_"+id;
            h.assertTrue(!EquipmentBehaviors.saved(p).getBoolean(key+"_done")&&!EquipmentBehaviors.saved(q).contains(key+"_start"),"Start belongs only to active ServerPlayer "+id);
            use(h,p,at);h.assertTrue(EquipmentBehaviors.saved(p).getInt(key+"_count")==0,"Early real repeated use has no progress "+id);
            int needed=id.equals("battlefield_remnant")?3:1;
            for(int step=1;step<=needed;step++){final int n=step;
                h.runAtTickTime(base+(long)duration*step/needed,()->{
                    var actual=id.equals("battlefield_remnant")?battle.get(n-1):at;p.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(actual.north()));
                    use(h,p,actual);var root=EquipmentBehaviors.saved(p);
                    h.assertTrue(root.getInt(key+"_count")==n,"Native elapsed interval advances exactly one "+id+" step "+n);
                    if(id.equals("battlefield_remnant")){use(h,p,actual);h.assertTrue(root.getInt(key+"_count")==n,"Same physical battlefield never counts twice");}
                    if(n==needed){
                        h.assertTrue(root.getBoolean(key+"_done")&&!EquipmentBehaviors.saved(q).getBoolean(key+"_done"),"Personal completion isolated "+id);
                        String inventory=p.getInventory().save(new net.minecraft.nbt.ListTag()).toString();use(h,p,actual);
                        h.assertTrue(inventory.equals(p.getInventory().save(new net.minecraft.nbt.ListTag()).toString()),"Repeat completed use never repays "+id);
                        var data=p.saveWithoutId(new CompoundTag());var restored=player(h,actual.north());restored.load(data);
                        h.assertTrue(EquipmentBehaviors.saved(restored).getBoolean(key+"_done"),"Native player NBT save/load retains receipt "+id);
                        use(h,restored,actual);h.assertTrue(inventory.equals(restored.getInventory().save(new net.minecraft.nbt.ListTag()).toString()),"Reloaded receipt never repays "+id);
                        evidence("real_clock_generic","id",id,"elapsed_world_ticks",h.getLevel().getGameTime()-start,"expected_duration",duration,"native_nbt_reload",true,"repeat_no_reward",true,"other_server_player_unclaimed",true,"player",p.getUUID().toString(),"other_player",q.getUUID().toString());
                        completed[0]++;p.discard();q.discard();restored.discard();if(completed[0]==durations.size())h.succeed();
                    }
                });
            }
        }
    }
    @GameTest(template="bow_ritual_test",batch="interaction_real_special_clock",timeoutTicks=3700)
    public static void actualProductionWellAndPuzzleHonorAllIntervalsWithNoSeededClock(GameTestHelper h){
        var post=build(h,0,Direction.SOUTH,new BlockPos(2560,80,2048));var desert=build(h,2,Direction.EAST,new BlockPos(2624,80,2048));
        var well=desert.point(21,1,28);var box=post.point(13,1,28);var w=player(h,desert.point(21,1,27));var p=player(h,post.point(13,1,27));var other=player(h,post.point(13,1,27));
        w.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));p.setYRot(180);p.setShiftKeyDown(false);
        use(h,w,well);use(h,p,box);long start=h.getLevel().getGameTime(),base=h.getTick();
        h.assertTrue(EquipmentBehaviors.saved(w).getLong("site_ancient_well_next")==start+515&&EquipmentBehaviors.saved(p).getLong("site_puzzle_box_next")==start+800,"Native original timers from actual uses");
        for(int i=0;i<7;i++){final int step=i;h.runAtTickTime(base+(i+1)*515,()->{
            w.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));use(h,w,well);
            h.assertTrue(EquipmentBehaviors.saved(w).getInt("site_ancient_well_count")==step+1&&w.getMainHandItem().is(Items.BUCKET),"Actual elapsed well delivery "+step);
            if(step==6){h.assertTrue(SecretTracker.wellClaimed(w)&&!SecretTracker.wellClaimed(other),"Seven paid waters isolate two ServerPlayer native receipts");
                int jade=w.getInventory().countItem(ExpansionContent.item("jade"));w.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));use(h,w,well);h.assertTrue(w.getMainHandItem().is(Items.WATER_BUCKET)&&w.getInventory().countItem(ExpansionContent.item("jade"))==jade,"Eighth water/reward cannot repeat");
                evidence("real_clock_well","elapsed_world_ticks",h.getLevel().getGameTime()-start,"deliveries",7,"duplicate_reward",false,"other_server_player_unclaimed",true);h.succeed();}
        });}
        long[] times={800,1600,2400,2410};float[] yaw={180,-90,0,90};
        for(int i=0;i<4;i++){final int step=i;h.runAtTickTime(base+times[i],()->{
            p.setYRot(yaw[step]);p.setShiftKeyDown(step%2==1);use(h,p,box);
            h.assertTrue(SecretTracker.puzzleCount(p)==step+1,"Real elapsed cardinal/posture pin "+step);
            if(step==3){h.assertTrue(SecretTracker.puzzleClaimed(p)&&!SecretTracker.puzzleClaimed(other),"Native puzzle personal receipt");int reward=p.getInventory().countItem(ExpansionContent.item("blueprint"));use(h,p,box);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("blueprint"))==reward,"Puzzle repeat no reward");evidence("real_clock_puzzle","elapsed_world_ticks",h.getLevel().getGameTime()-start,"pins",4,"other_server_player_unclaimed",true);}
        });}
    }
}
