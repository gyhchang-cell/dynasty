package com.dynasty.cod3;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import static com.dynasty.structure.InteractionAcceptance.*;

@GameTestHolder("dynasty_interaction_qa") @PrefixGameTestTemplate(false)
public final class InteractionSceneAcceptance {
    static boolean choose(ServerPlayer p,String choice){var n=NpcDialogue.session(p.getUUID());return n!=null&&NpcDialogue.choose(p,n.token(),choice);}
    @GameTest(template="bow_ritual_test",batch="interaction_scene_rotations",timeoutTicks=500)
    public static void productionCourtyardSceneNpcsReachableForTwoOwnersInEveryOrientation(GameTestHelper h){
        record Case(int style,Direction facing,com.dynasty.structure.InteractionAcceptance.Piece piece){}
        var cases=new java.util.ArrayList<Case>();int rot=0;
        for(var facing:Direction.Plane.HORIZONTAL){for(int style=0;style<3;style++)cases.add(new Case(style,facing,build(h,style,facing,new BlockPos(3072+style*64,80,3072+rot*64))));rot++;}
        h.runAtTickTime(h.getTick()+80,()->{for(var item:cases){int style=item.style();var facing=item.facing();
            String id=style==0?"wayside_tea_stall":style==1?"mortuary_room":"ghost_market_boat";
            int x=style==2?13:17;var piece=item.piece();var at=piece.point(x,1,28);var approach=piece.point(x,1,27);
            var p=player(h,approach);var q=player(h,approach);p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));q.setItemInHand(InteractionHand.MAIN_HAND,offering(id));use(h,p,at);use(h,q,at);
            java.util.UUID uid=style==0?SmallInteractions.poisonTeaVendorId(h.getLevel(),at):style==1?SmallInteractions.mortuaryVictimId(h.getLevel(),at,p.getUUID()):SmallInteractions.ghostBoatId(h.getLevel(),at);
            var npc=(DynastyNpcEntity)h.getLevel().getEntity(uid);
            h.assertTrue(npc!=null&&h.getLevel().noCollision(npc,npc.getBoundingBox()),"Actual scene NPC fits production candidates "+id+" "+facing);
            var foot=npc.blockPosition().below();boolean ground=h.getLevel().getBlockState(foot).isFaceSturdy(h.getLevel(),foot,Direction.UP);
            h.assertTrue(ground&&p.distanceToSqr(npc)<=36,"NPC supported and reachable "+id);
            evidence("scene_spawn","id",id,"orientation",facing.toString(),"site_world",at.toShortString(),"approach_world",approach.toShortString(),"npc_world",npc.position().toString(),"native_no_collision",true,"ground_support",ground,"player_distance_squared",p.distanceToSqr(npc));
            if(style==1){
                var second=(DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.mortuaryVictimId(h.getLevel(),at,q.getUUID()));
                h.assertTrue(second!=null&&!second.getUUID().equals(npc.getUUID())&&second.getPersistentData().getUUID("cod4_mortuary_owner").equals(q.getUUID()),"Two actual patient identities own separate native entity NBT");second.discard();
            }else{
                boolean pc=style==0?SmallInteractions.poisonTeaContext(p,npc):SmallInteractions.ghostBoatContext(p,npc);
                boolean qc=style==0?SmallInteractions.poisonTeaContext(q,npc):SmallInteractions.ghostBoatContext(q,npc);
                h.assertTrue(pc&&qc,"Each paid/anchored owner gets existing shared merchant context");
                p.setPos(p.position().add(30,0,0));h.assertTrue(!(style==0?SmallInteractions.poisonTeaContext(p,npc):SmallInteractions.ghostBoatContext(p,npc)),"Remote actual scene context rejected");
            }
            npc.discard();NpcDialogue.logout(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));NpcDialogue.logout(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(q));p.discard();q.discard();
        }h.succeed();});
    }
    @GameTest(template="bow_ritual_test",batch="interaction_scene_real_clock",timeoutTicks=2700)
    public static void realTwoMinuteSceneDialogueDeliveryFlipAndHealingUseActualProductionPlacement(GameTestHelper h){
        var post=build(h,0,Direction.WEST,new BlockPos(3456,80,3072));var herb=build(h,1,Direction.SOUTH,new BlockPos(3520,80,3072));var desert=build(h,2,Direction.EAST,new BlockPos(3584,80,3072));
        var tea=post.point(17,1,28);var room=herb.point(17,1,28);var boat=desert.point(13,1,28);
        h.runAtTickTime(h.getTick()+80,()->{
        var t=player(h,post.point(17,1,27));var m=player(h,herb.point(17,1,27));var b=player(h,desert.point(13,1,27));var other=player(h,post.point(17,1,27));
        b.setItemInHand(InteractionHand.MAIN_HAND,offering("ghost_market_boat"));use(h,t,tea);use(h,m,room);use(h,b,boat);
        h.assertTrue(choose(t,"inspect")&&choose(b,"talk"),"Actual production scene nonce-protected choices");
        b.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar"),2));m.setItemInHand(InteractionHand.MAIN_HAND,PotionUtils.setPotion(new ItemStack(Items.POTION),Potions.HEALING));
        h.assertTrue(!choose(t,"flip")&&!SmallInteractions.deliverGhostBoat(b,(DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.ghostBoatId(h.getLevel(),boat))),"Early actual scene actions reject");
        long start=h.getLevel().getGameTime(),base=h.getTick();
        h.runAtTickTime(base+2400,()->{
            use(h,t,tea);var vendor=(DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.poisonTeaVendorId(h.getLevel(),tea));var sess=NpcDialogue.session(t.getUUID());boolean flip=choose(t,"flip");
            evidence("scene_tea_result","elapsed_world_ticks",h.getLevel().getGameTime()-start,"flip",flip,"claimed",SecretTracker.poisonTeaClaimed(t),"root",EquipmentBehaviors.saved(t).toString(),"npc",vendor==null?"null":vendor.saveWithoutId(new net.minecraft.nbt.CompoundTag()).toString(),"session",String.valueOf(sess),"game_mode",t.gameMode.getGameModeForPlayer().toString(),"site_state",h.getLevel().getBlockState(tea).toString());
            h.assertTrue(flip&&SecretTracker.poisonTeaClaimed(t),"Native table break/restore completes after real2400 ticks; diagnostic in scene_tea_result");
            use(h,b,boat);h.assertTrue(choose(b,"deliver")&&SecretTracker.ghostBoatClaimed(b)&&b.getMainHandItem().getCount()==1,"Native boat pays one actual cinnabar after real deadline");
            use(h,m,room);h.assertTrue(SecretTracker.mortuaryClaimed(m)&&m.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==1,"Native patient heals and awards one heirloom after real deadline");
            h.assertTrue(!SecretTracker.poisonTeaClaimed(other)&&!SecretTracker.ghostBoatClaimed(other)&&!SecretTracker.mortuaryClaimed(other),"Detached second ServerPlayer inherits no personal claim");
            int silk=t.getInventory().countItem(ExpansionContent.item("silk")),slip=b.getInventory().countItem(ExpansionContent.item("bamboo_slip"));use(h,t,tea);use(h,b,boat);use(h,m,room);
            h.assertTrue(t.getInventory().countItem(ExpansionContent.item("silk"))==silk&&b.getInventory().countItem(ExpansionContent.item("bamboo_slip"))==slip&&m.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==1,"Repeated native scene completion does not repay");
            evidence("real_clock_scenes","elapsed_world_ticks",h.getLevel().getGameTime()-start,"tea_native_break_restore",true,"ghost_actual_cinnabar",true,"mortuary_native_healing",true,"other_server_player_unclaimed",true,"repeat_no_reward",true);h.succeed();
        });
        });
    }
}
