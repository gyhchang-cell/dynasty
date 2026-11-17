package artifacts.component.ability;

import artifacts.Artifacts;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import artifacts.registry.ModTags;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;

public record ToolTierUpgrade(Value<Tier> tier, Value<Integer> itemDamage) implements EquipmentAbility {

    public static final Codec<ToolTierUpgrade> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.TOOL_TIER.codec().fieldOf("tier").forGetter(ToolTierUpgrade::tier),
            ValueTypes.itemDamageField().forGetter(ToolTierUpgrade::itemDamage)
    ).apply(instance, ToolTierUpgrade::new));

    public static final StreamCodec<ByteBuf, ToolTierUpgrade> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.TOOL_TIER.streamCodec(),
            ToolTierUpgrade::tier,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            ToolTierUpgrade::itemDamage,
            ToolTierUpgrade::new
    );

    public static boolean canHarvestWithTier(LivingEntity entity, BlockState state) {
        if (state.is(ModTags.MINEABLE_WITH_DIGGING_CLAWS)) {
            int level = ModDataComponents.TOOL_TIER_UPGRADE.on(entity)
                    .maxInt(ability -> ability.tier().get().getLevel());
            return isCorrectTierForDrops(Tier.fromLevel(level), state);
        }
        return false;
    }

    // TODO: fix with incorrect_for_<tier>_tool tags
    public static boolean isCorrectTierForDrops(Tier tier, BlockState state) {
        if (!state.requiresCorrectToolForDrops()) {
            return true;
        }
        int i = tier.getLevel();
        if (state.is(BlockTags.NEEDS_DIAMOND_TOOL)) {
            return i >= 4;
        } else if (state.is(BlockTags.NEEDS_IRON_TOOL)) {
            return i >= 3;
        } else if (state.is(BlockTags.NEEDS_STONE_TOOL)) {
            return i >= 2;
        } else {
            return i >= 1;
        }
    }

    public static void onBlockBroken(LivingEntity entity, BlockState state) {
        if (entity instanceof Player player
                && state.requiresCorrectToolForDrops()
                && !player.getInventory().getSelectedItem().isCorrectToolForDrops(state)
        ) {
            ModDataComponents.TOOL_TIER_UPGRADE.on(player)
                    .filter(ability -> isCorrectTierForDrops(ability.tier.get(), state))
                    .iterate((ability, slot) -> slot.hurtAndBreak(ability.itemDamage.get()));
        }
    }

    @Override
    public boolean isNonCosmetic() {
        return tier().get() != Tier.NONE;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        writer.addDefaultTooltipKey(getTierName(tier.get()));
    }

    public static Component getTierName(Tier tier) {
        return Component.translatable("%s.tooltip.tool_tier.%s".formatted(Artifacts.MOD_ID, tier.getSerializedName()));
    }

    public enum Tier implements StringRepresentable {
        NONE(0),
        WOOD(1),
        STONE(2),
        IRON(3),
        DIAMOND(4),
        NETHERITE(5);

        private final int level;

        Tier(int level) {
            this.level = level;
        }

        public static Tier fromLevel(int level) {
            return switch (level) {
                case 0 -> NONE;
                case 1 -> WOOD;
                case 2 -> STONE;
                case 3 -> IRON;
                case 4 -> DIAMOND;
                default -> NETHERITE;
            };
        }

        public int getLevel() {
            return level;
        }

        @Override
        public String getSerializedName() {
            return toString().toLowerCase();
        }
    }
}
