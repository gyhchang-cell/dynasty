package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.DynastyWeapons;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraftforge.registries.ForgeRegistries;

/** Read native active use only. No timer, saved flag, input, projectile or packet of its own. */
public final class BowDrawProgress {
    public record Draw(int ticks, int required) {
        public boolean full() { return ticks >= required; }
        public float fraction() { return Math.min(1, Math.max(0, ticks / (float)required)); }
    }
    public static Draw read(Player player) {
        if(player==null || !player.isAlive() || player.isSpectator() || !player.isUsingItem()) return null;
        var stack=player.getUseItem();
        if(stack.isEmpty() || !(stack.getItem() instanceof BowItem)
                || stack!=player.getItemInHand(player.getUsedItemHand())) return null;
        var id=ForgeRegistries.ITEMS.getKey(stack.getItem());
        if(id==null || !id.getNamespace().equals(Dynasty.MODID)) return null;
        int required=stack.getItem() instanceof DynastyWeapons.HuntingBowItem bow ? bow.fullDrawTicks() : 20;
        return new Draw(Math.max(0,player.getTicksUsingItem()),required);
    }
    private BowDrawProgress() {}
}
