package com.dynasty;

import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.WeaponImpactPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;

@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class ImperialWeaponEffects {
    public static int style(ItemStack stack) {
        if (stack.is(DynastyWeapons.TIANZI_SWORD.get())) return 1;
        if (stack.is(DynastyWeapons.QINGLONG_DAO.get())) return 2;
        return 0;
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void hit(LivingDamageEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity().level() instanceof ServerLevel level)
                || !(event.getSource().getEntity() instanceof LivingEntity attacker)
                || event.getSource().getDirectEntity() != attacker) return;
        int style = style(attacker.getMainHandItem());
        if (style != 1 || QinglongDescent.isDragonDamage(event.getSource())) return;
        var position = event.getEntity().position().add(0, event.getEntity().getBbHeight() * .55, 0);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(() -> new PacketDistributor.TargetPoint(
                position.x, position.y, position.z, 48, level.dimension())),
                new WeaponImpactPacket(style, position.x, position.y, position.z, attacker.getYRot()));
    }
    private ImperialWeaponEffects() {}
}
