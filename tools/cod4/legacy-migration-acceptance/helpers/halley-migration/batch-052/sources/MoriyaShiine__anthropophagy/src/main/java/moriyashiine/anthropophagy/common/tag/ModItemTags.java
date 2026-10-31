/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.tag;

import moriyashiine.anthropophagy.common.Anthropophagy;
import net.minecraft.item.Item;
import net.minecraft.registry.RegistryKeys;
import net.minecraft.registry.tag.TagKey;
import net.minecraft.util.Identifier;

public class ModItemTags {
	public static final TagKey<Item> KNIVES = TagKey.of(RegistryKeys.ITEM, new Identifier("c", "knives"));

	public static final TagKey<Item> FLESH = TagKey.of(RegistryKeys.ITEM, Anthropophagy.id("flesh"));
}
