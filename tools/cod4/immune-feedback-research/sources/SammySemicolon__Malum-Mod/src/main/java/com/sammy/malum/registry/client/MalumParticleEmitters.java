package com.sammy.malum.registry.client;

import com.sammy.malum.*;
import com.sammy.malum.common.recipe.*;
import com.sammy.malum.registry.common.recipe.*;
import net.minecraft.client.player.*;
import net.minecraft.world.item.*;
import net.neoforged.api.distmarker.*;
import net.neoforged.bus.api.*;
import net.neoforged.fml.common.*;
import net.neoforged.neoforge.event.entity.*;
import team.lodestar.lodestone.handlers.screenparticle.*;
import team.lodestar.lodestone.modules.toolkit.recipe.LodestoneInWorldRecipe;
import team.lodestar.lodestone.modules.toolkit.recipe.LodestoneRecipeSearch;

import java.util.*;

import static com.sammy.malum.visual_effects.ScreenParticleEffects.VoidTransmutableParticleEffect.*;

@EventBusSubscriber(modid= MalumMod.MALUM, value = Dist.CLIENT)
public class MalumParticleEmitters {

    public static boolean registeredVoidParticleEmitters = false;

    @SubscribeEvent
    public static void addParticleEmitters(EntityJoinLevelEvent event) {
        if (!registeredVoidParticleEmitters) {
            if (event.getEntity() instanceof AbstractClientPlayer player) {
                var search = LodestoneRecipeSearch.search(player.level(), MalumRecipeTypes.VOID_FAVOR);
                for (VoidFavorRecipe recipe : search.getAllRecipes()) {
                    for (ItemStack item : recipe.input.getItems()) {
                        ParticleEmitterHandler.registerItemParticleEmitter(item.getItem(), INSTANCE);
                    }
                }
            }
        }
    }
}