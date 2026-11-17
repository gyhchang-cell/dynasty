/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.tag;

import moriyashiine.anthropophagy.common.Anthropophagy;
import net.minecraft.block.Block;
import net.minecraft.registry.RegistryKeys;
import net.minecraft.registry.tag.TagKey;

public class ModBlockTags {
	public static final TagKey<Block> PIGLUTTON_BREAKABLE = TagKey.of(RegistryKeys.BLOCK, Anthropophagy.id("piglutton_breakable"));
}
