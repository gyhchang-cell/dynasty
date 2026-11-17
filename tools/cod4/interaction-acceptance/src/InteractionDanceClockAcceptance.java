package com.dynasty.cod3;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import static com.dynasty.structure.InteractionAcceptance.*;
/** Separate namespace/run keeps historical tests' global day/weather mutations away. */
@GameTestHolder("dynasty_interaction_extra_qa") @PrefixGameTestTemplate(false)
public final class InteractionDanceClockAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_sword_real_clock",timeoutTicks=2700)
    public static void productionMoonlitWallThreeNativeAirSwingsAfterActualEightHundredTickStages(GameTestHelper h){
        h.getLevel().setDayTime(14000);h.getLevel().updateSkyBrightness();h.getLevel().setWeatherParameters(10000,0,false,false);h.getLevel().setRainLevel(0);h.getLevel().setThunderLevel(0);
        var piece=build(h,1,Direction.NORTH,new BlockPos(4096,80,3072));var at=piece.point(13,1,28);var p=player(h,piece.point(15,1,27));var q=player(h,piece.point(15,1,27));p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));
        h.startSequence().thenWaitUntil(()->h.assertTrue(SwordDance.context(p,at),"Actual production outdoor moonlight readiness")).thenExecute(()->{
            use(h,p,at);h.assertTrue(SwordDance.state(p).getBoolean("DanceFocused"),"Actual block use focuses native dance");evidence("sword_clear_start","site_world",at.toShortString(),"start_world",p.position().toString(),"reason","Two local cells to side of wall; direct-front candidate auto-steps onto 13/16 collision during third north cut (run7).");long start=h.getLevel().getGameTime(),base=h.getTick();
            for(int i=0;i<3;i++){final int stage=i;h.runAtTickTime(base+(i+1)*800,()->{
                for(int j=0;j<8;j++){p.tick();p.doTick();}p.setYRot(stage<2?180:-90);
                p.move(MoverType.SELF,stage==0?new Vec3(.6,0,0):stage==1?new Vec3(-.6,0,0):new Vec3(0,0,-.6));
                for(int j=0;j<8&&!p.onGround();j++){p.tick();p.doTick();}
                p.swing(InteractionHand.MAIN_HAND);p.tick();p.doTick();
                h.assertTrue(SwordDance.state(p).getInt("Count")==stage+1,"Native grounded step + swing after actual interval; stage="+stage+", state="+SwordDance.state(p));
                evidence("real_clock_sword_step","elapsed_world_ticks",h.getLevel().getGameTime()-start,"count",stage+1,"on_ground",p.onGround(),"player_world",p.position().toString());
                if(stage==2){h.assertTrue(SecretTracker.swordDanceClaimed(p)&&!SecretTracker.swordDanceClaimed(q)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Original rewards and independent second ServerPlayer receipt");
                    use(h,p,at);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Completed dance repeat never repays");h.succeed();}
            });}
        });
    }
}
