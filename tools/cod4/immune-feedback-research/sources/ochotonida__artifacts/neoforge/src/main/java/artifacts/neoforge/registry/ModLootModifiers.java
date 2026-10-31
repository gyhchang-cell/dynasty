package artifacts.neoforge.registry;

import artifacts.neoforge.loot.ReplaceWithTableLootModifier;
import artifacts.registry.Register;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.Holder;
import net.neoforged.neoforge.common.loot.IGlobalLootModifier;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

public class ModLootModifiers {

    public static final Register<MapCodec<? extends IGlobalLootModifier>> LOOT_MODIFIERS = Register.create(NeoForgeRegistries.Keys.GLOBAL_LOOT_MODIFIER_SERIALIZERS);

    public static final Holder<MapCodec<? extends IGlobalLootModifier>> REPLACE_WITH_TABLE = LOOT_MODIFIERS.register("replace_with_table", () -> ReplaceWithTableLootModifier.CODEC);

}
