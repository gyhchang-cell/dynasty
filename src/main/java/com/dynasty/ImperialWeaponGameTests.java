package com.dynasty;

import com.dynasty.network.WeaponImpactPacket;
import io.netty.buffer.Unpooled;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class ImperialWeaponGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void visualOnlyAndWeaponWhitelist(GameTestHelper helper) {
        helper.assertTrue(ImperialWeaponEffects.style(new ItemStack(DynastyWeapons.TIANZI_SWORD.get()))==1,"Tianzi style");
        helper.assertTrue(ImperialWeaponEffects.style(new ItemStack(DynastyWeapons.QINGLONG_DAO.get()))==2,"Qinglong style");
        helper.assertTrue(ImperialWeaponEffects.style(new ItemStack(DynastyWeapons.LONGYUAN_SWORD.get()))==0,"Longyuan must remain effect-free");
        helper.assertTrue(ImperialWeaponEffects.style(ItemStack.EMPTY)==0,"Empty hand must have no effects");
        var attacker=helper.spawn(EntityType.ZOMBIE,3,2,3);
        var target=helper.spawn(EntityType.SHEEP,5,2,3);
        attacker.setNoAi(true); target.setNoAi(true);
        float health=target.getHealth();
        for(var weapon:new net.minecraft.world.item.Item[]{DynastyWeapons.TIANZI_SWORD.get(),DynastyWeapons.QINGLONG_DAO.get()}) {
            attacker.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(weapon));
            var event=new LivingDamageEvent(target,helper.getLevel().damageSources().mobAttack(attacker),3);
            ImperialWeaponEffects.hit(event);
            helper.assertTrue(event.getAmount()==3 && !event.isCanceled(),"Effects must not change damage");
            helper.assertTrue(target.getHealth()==health,"Effects must not cause extra damage");
            event.setCanceled(true);
            ImperialWeaponEffects.hit(event);
            helper.assertTrue(event.isCanceled(),"Canceled damage must stay canceled");
        }
        helper.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void impactPacketRoundTrip(GameTestHelper helper) {
        FriendlyByteBuf buffer=new FriendlyByteBuf(Unpooled.buffer());
        try {
            for(int style=1;style<=2;style++) {
                buffer.clear();
                var packet=new WeaponImpactPacket(style,-203.25,82.75,439.125,-173.5f);
                WeaponImpactPacket.encode(packet,buffer);
                helper.assertTrue(packet.equals(WeaponImpactPacket.decode(buffer)),"Impact packet must retain style, position and orientation");
                helper.assertTrue(buffer.readableBytes()==0,"Packet must consume exactly its payload");
            }
        } finally { buffer.release(); }
        helper.succeed();
    }
}
