package artifacts.client.item.property;

import artifacts.util.ItemDamageUtil;
import com.mojang.serialization.MapCodec;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.item.properties.conditional.ConditionalItemModelProperty;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * Same as minecraft:broken, but only for indestructible items
 */
public record NeedsRepair() implements ConditionalItemModelProperty {

    public static final MapCodec<NeedsRepair> MAP_CODEC = MapCodec.unit(new NeedsRepair());

    @Override
    public boolean get(ItemStack stack, @Nullable ClientLevel level, @Nullable LivingEntity owner, int seed, ItemDisplayContext displayContext) {
        return ItemDamageUtil.needsRepair(stack);
    }

    @Override
    public MapCodec<NeedsRepair> type() {
        return MAP_CODEC;
    }
}
