package com.dynasty;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.effect.MobEffects;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_bugfix")
@PrefixGameTestTemplate(false)
public final class ReportedBugGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void medicineHealsConsumesAndRetainsCreativeStack(GameTestHelper h) {
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"medicine-qa"));
        player.setHealth(4);
        var salve=new ItemStack(DynastyItems.HEALING_SALVE.get(),2);
        h.assertTrue(salve.getUseAnimation()==UseAnim.EAT,"Medicine must display a use animation");
        salve.finishUsingItem(h.getLevel(),player);
        h.assertTrue(player.getHealth()==12,"One completed salve dose heals exactly 8 immediately");
        h.assertTrue(salve.getCount()==1,"Survival consumes exactly one dose");
        player.getAbilities().instabuild=true;player.setHealth(4);
        salve.finishUsingItem(h.getLevel(),player);
        h.assertTrue(player.getHealth()==12&&salve.getCount()==1,"Creative heals without consuming dose");
        player.getAbilities().instabuild=false;
        var pill=new ItemStack(DynastyItems.PILL_LONGEVITY.get(),2);
        pill.finishUsingItem(h.getLevel(),player);
        var effect=player.getEffect(MobEffects.REGENERATION);
        h.assertTrue(effect!=null&&effect.getAmplifier()==1&&effect.getDuration()==600,"Longevity retains real Regeneration II for 30 seconds");
        h.assertTrue(pill.getCount()==1,"Regeneration dose consumed once");
        h.succeed();
    }
}
