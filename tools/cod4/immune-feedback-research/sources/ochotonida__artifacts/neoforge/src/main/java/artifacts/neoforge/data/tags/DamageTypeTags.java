package artifacts.neoforge.data.tags;

import artifacts.Artifacts;
import artifacts.registry.ModTags;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.DamageTypeTagsProvider;
import net.minecraft.world.damagesource.DamageTypes;

import java.util.List;
import java.util.concurrent.CompletableFuture;

public class DamageTypeTags extends DamageTypeTagsProvider {

    public DamageTypeTags(PackOutput packOutput, CompletableFuture<HolderLookup.Provider> lookupProvider) {
        super(packOutput, lookupProvider, Artifacts.MOD_ID);
    }

    @SuppressWarnings("unchecked")
    @Override
    protected void addTags(HolderLookup.Provider arg) {
        tag(ModTags.IS_MELEE).addAll(List.of(
                DamageTypes.MOB_ATTACK,
                DamageTypes.MOB_ATTACK_NO_AGGRO,
                DamageTypes.SPEAR
        )).addTags(
                net.minecraft.tags.DamageTypeTags.IS_PLAYER_ATTACK,
                net.minecraft.tags.DamageTypeTags.IS_MACE_SMASH
        );
    }
}
