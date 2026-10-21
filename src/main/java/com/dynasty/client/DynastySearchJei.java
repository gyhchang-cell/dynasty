package com.dynasty.client;

import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.registration.IIngredientAliasRegistration;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PotionItem;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraftforge.registries.ForgeRegistries;

@JeiPlugin
public final class DynastySearchJei implements IModPlugin {
    @Override public ResourceLocation getPluginUid(){return new ResourceLocation("dynasty","search_aliases");}
    @Override public void registerIngredientAliases(IIngredientAliasRegistration r) {
        for(var item:ForgeRegistries.ITEMS) {
            var stack=new ItemStack(item);
            if(!DynastySearchAliases.aliases(stack).isEmpty())r.addAliases(item,DynastySearchAliases.aliases(stack));
            if(item instanceof PotionItem)for(var potion:ForgeRegistries.POTIONS) {
                var variant=PotionUtils.setPotion(new ItemStack(item),potion);
                for(String alias:DynastySearchAliases.aliases(variant))r.addAlias(variant,alias);
            }
        }
    }
}
