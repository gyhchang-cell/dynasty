package com.dynasty;
import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class DragonPearlNativeGameTests {
    @GameTest(template="bow_ritual_test",batch="cod4_dragon_pearl_native",setupTicks=20,timeoutTicks=420)
    public static void actualFiveChargedPrimaryInputsReleaseOneOriginalSharedDragonWaveAndSixthCannotDoubleProc(GameTestHelper h){
        var ps=new ArrayList<ServerPlayer>();var targets=new ArrayList<Cow>();float[][] lost=new float[2][6];long[] until=new long[2];
        for(int i=0;i<2;i++){
            var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"pearl-native"));
            p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
            p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6+i*5,52,6))));p.setNoGravity(true);p.getFoodData().setFoodLevel(17);
            p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.setHealth(5000);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));
            if(i==1){for(var slot:new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS})p.setItemSlot(slot,new ItemStack(ExpansionContent.item("qinglong_"+switch(slot){case HEAD->"helmet";case CHEST->"chestplate";default->"leggings";})));}
            SchoolCombatGameTests.equip(p,"charm",new ItemStack(DynastyTrinkets.DRAGON_PEARL.get()));h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});ps.add(p);
            var z=new Cow(EntityType.COW,h.getLevel());z.setPos(p.position().add(1,0,0));z.setNoAi(true);z.setNoGravity(true);z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);z.setHealth(5000);z.getAttribute(Attributes.ARMOR).setBaseValue(0);z.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);for(var cell:BlockPos.betweenClosed(p.blockPosition().offset(-1,0,-1),p.blockPosition().offset(2,3,1)))h.getLevel().setBlock(cell,net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(),2);h.assertTrue(h.getLevel().noCollision(p,p.getBoundingBox())&&h.getLevel().noCollision(z,z.getBoundingBox()),"Real stationary primary calibration pair has clear standing volumes");h.getLevel().addFreshEntity(z);targets.add(z);
        }
        Runnable cleanup=()->{for(var t:targets)t.discard();for(var p:ps){net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}};
        int[] input={0};Runnable hit=new Runnable(){public void run(){try{
            int at=input[0]++;
            for(int i=0;i<2;i++){
                var p=ps.get(i);var z=targets.get(i);h.assertTrue(z.tickCount>=2&&h.getLevel().getEntity(z.getUUID())==z,"Actual world-ticked visible primary target");
                h.assertTrue(p.getAttackStrengthScale(.5F)>.9F,"Real world/native player ticks charge actual primary input");float hp=z.getHealth();p.setSprinting(false);p.attack(z);lost[i][at]=hp-z.getHealth();
                h.assertTrue(lost[i][at]>0&&p.getAttackStrengthScale(.5F)<.2F,"Actual primary input changes target health and resets cooldown");
                h.assertTrue(DynastyTrinketOnHit.comboStacks(p,z)==at+1,"One shared combo layer per actual charged input, pearl and Qinglong cannot both advance it: "+(at+1));
                if(at<4)h.assertTrue(!EquipmentBehaviors.saved(p).contains("comboWave"),"First four actual inputs do not emit the fifth-hit wave");
                if(at==4){until[i]=EquipmentBehaviors.saved(p).getLong("comboWave");h.assertTrue(until[i]==h.getLevel().getGameTime()+60,"Fifth hit uses original shared60tick wave cooldown");}
                if(at==5)h.assertTrue(EquipmentBehaviors.saved(p).getLong("comboWave")==until[i],"Pearl plus suit does not start a second cooldown or wave on sixth input");
            }
            if(at<5){h.runAfterDelay(22,()->this.run());return;}
            h.assertTrue(Math.abs(lost[0][4]/lost[0][3]-1.12F)<.01&&Math.abs(lost[0][5]-lost[0][3])<.02,"Pearl alone original fifth-hit12percent damage bonus occurs once, sixth stays baseline: damage="+java.util.Arrays.deepToString(lost)+", until="+java.util.Arrays.toString(until));
            h.assertTrue(lost[1][4]>lost[1][3]&&Math.abs(lost[1][5]-lost[1][3])<.05,"With existing three-piece Qinglong the same fifth wave is single and sixth retains only capped original combo benefit: "+java.util.Arrays.deepToString(lost));
            h.succeed();cleanup.run();
        }catch(Throwable failure){cleanup.run();throw failure;}}};h.startSequence().thenWaitUntil(()->{for(var p:ps)h.assertTrue(p.getAttributeValue(Attributes.ATTACK_DAMAGE)>=7.49,"Native Curios/player refresh has actually applied original25percent pearl attack modifier before measuring the combo");}).thenExecute(()->h.runAfterDelay(22,hit));
    }
}
