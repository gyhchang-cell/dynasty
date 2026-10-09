package com.dynasty;

import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class AccessoryConditionGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"trinket-dual"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(500);p.setHealth(500);return p;
    }
    private static void phase(GameTestHelper h,ServerPlayer p,boolean day){h.getLevel().setDayTime(day?6000:18000);h.getLevel().updateSkyBrightness();h.assertTrue(h.getLevel().isDay()==day,"Native level uses the actual requested daylight phase");DynastyTrinkets.tick(p);}
    private static void near(GameTestHelper h,double actual,double expected,String message){h.assertTrue(Math.abs(actual-expected)<.00001,message+" actual="+actual+" expected="+expected);}
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_duality",setupTicks=20)
    public static void sixOppositeDayNightRulesWorkOnActualCuriosAndRollBackWithoutStacking(GameTestHelper h){
        var p=player(h);long time=h.getLevel().getDayTime();
        String[] ids={"dawn_blade_charm","dusk_veil_charm","noon_pendant","moonlit_mirror","twilight_cicada","eclipse_bead"};
        Attribute[] main={Attributes.ATTACK_DAMAGE,Attributes.ATTACK_DAMAGE,Attributes.MAX_HEALTH,Attributes.ATTACK_SPEED,Attributes.KNOCKBACK_RESISTANCE,Attributes.ATTACK_DAMAGE};
        Attribute[] third={Attributes.MOVEMENT_SPEED,Attributes.MAX_HEALTH,Attributes.MAX_HEALTH,Attributes.LUCK,net.minecraftforge.common.ForgeMod.ENTITY_REACH.get(),Attributes.ARMOR};
        double[] mv={.22,.26,240,.14,.4,.3},tv={.1,-.2,-160,2,1,-6};boolean[] mainDay={true,false,true,false,true,false};
        try{
            for(int i=0;i<ids.length;i++){
                String slot=java.util.Set.of("noon_pendant","eclipse_bead").contains(ids[i])?"necklace":ids[i].equals("moonlit_mirror")?"body":"charm";
                double mb=p.getAttributeValue(main[i]),tb=p.getAttributeValue(third[i]);SchoolCombatGameTests.equip(p,slot,new ItemStack(ExpansionContent.item(ids[i])));
                phase(h,p,mainDay[i]);near(h,p.getAttributeValue(main[i]),i==2||i==4?mb+mv[i]:mb*(1+mv[i]),ids[i]+" retains its original main-phase benefit");
                phase(h,p,!mainDay[i]);double expected=i==0||i==1?tb*(1+tv[i]):Math.max(i==5?0:Double.NEGATIVE_INFINITY,tb+tv[i]);
                near(h,p.getAttributeValue(third[i]),expected,ids[i]+" independently applies its opposite-phase third rule");
                if(main[i]!=third[i])near(h,p.getAttributeValue(main[i]),mb,ids[i]+" clears inactive main rule");
                int count=p.getAttribute(third[i]).getModifiers().size();DynastyTrinkets.tick(p);near(h,p.getAttributeValue(third[i]),expected,ids[i]+" repeated refresh does not add another modifier");h.assertTrue(p.getAttribute(third[i]).getModifiers().size()==count,"Original stable UUID deduplicates repeated third-rule refresh");
                phase(h,p,mainDay[i]);near(h,p.getAttributeValue(main[i]),i==2||i==4?mb+mv[i]:mb*(1+mv[i]),ids[i]+" returns to original main rule after dawn/dusk");
                SchoolCombatGameTests.equip(p,slot,ItemStack.EMPTY);DynastyTrinkets.tick(p);near(h,p.getAttributeValue(main[i]),mb,ids[i]+" unequip clears main modifier");near(h,p.getAttributeValue(third[i]),tb,ids[i]+" unequip clears third modifier");
            }
        }finally{h.getLevel().setDayTime(time);h.getLevel().updateSkyBrightness();DynastyTrinkets.forget(p);}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_duality",setupTicks=20)
    public static void conditionalThirdRuleDoesNotRequireMainStatAndKeepsLowHealthPredicate(GameTestHelper h){
        var p=player(h);double base=p.getAttributeValue(Attributes.ATTACK_DAMAGE);SchoolCombatGameTests.equip(p,"charm",new ItemStack(ExpansionContent.item("flesh_gamble_dice")));
        DynastyTrinkets.tick(p);near(h,p.getAttributeValue(Attributes.ATTACK_DAMAGE),base*1.2,"Full-health original always-active benefit remains");
        p.setHealth(100);DynastyTrinkets.tick(p);near(h,p.getAttributeValue(Attributes.ATTACK_DAMAGE),base*1.2*1.4,"Low-health third slot retains its independent original UUID and multiplicative behavior");
        p.setHealth(500);DynastyTrinkets.tick(p);near(h,p.getAttributeValue(Attributes.ATTACK_DAMAGE),base*1.2,"Recovering clears only the inactive third slot");
        SchoolCombatGameTests.equip(p,"charm",ItemStack.EMPTY);DynastyTrinkets.tick(p);near(h,p.getAttributeValue(Attributes.ATTACK_DAMAGE),base,"Unequip removes both original slots");DynastyTrinkets.forget(p);h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_duality",setupTicks=20)
    public static void auditUsesAllCanonicalAccessoriesAndTheNativeUnseenGiftPool(GameTestHelper h){
        var p=player(h);h.assertTrue(DynastyTrinkets.IDS.size()==201&&java.util.Set.copyOf(DynastyTrinkets.IDS).size()==201,"Audit includes all 201 canonical unique IDs, including the separately registered bronze mirror");
        var obtained=new java.util.HashSet<String>();for(int i=0;i<DynastyTrinkets.IDS.size();i++){var gift=com.dynasty.expansion.ContentProgress.gift(p);String id=DynastyTrinkets.idOf(gift);h.assertTrue(DynastyTrinkets.IDS.contains(id)&&obtained.add(id),"Native box unseen pool actually reaches every registered accessory without duplicates before exhaustion");}
        h.assertTrue(obtained.equals(java.util.Set.copyOf(DynastyTrinkets.IDS)),"Canonical gift source truly covers every audited ID");h.assertTrue(h.getLevel().getRecipeManager().byKey(new net.minecraft.resources.ResourceLocation("dynasty","trinket_box")).isPresent(),"Actual native box survival recipe exists");h.succeed();
    }
}
