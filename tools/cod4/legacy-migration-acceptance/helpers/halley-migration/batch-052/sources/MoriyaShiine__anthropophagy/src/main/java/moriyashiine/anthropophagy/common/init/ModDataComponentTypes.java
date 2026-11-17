/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.init;

import com.mojang.serialization.Codec;
import moriyashiine.anthropophagy.common.Anthropophagy;
import net.minecraft.component.DataComponentType;
import net.minecraft.network.codec.PacketCodecs;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;

public class ModDataComponentTypes {
	public static final DataComponentType<Boolean> FROM_PLAYER = new DataComponentType.Builder<Boolean>().codec(Codec.BOOL).packetCodec(PacketCodecs.BOOL).build();
	public static final DataComponentType<String> OWNER_NAME = new DataComponentType.Builder<String>().codec(Codec.STRING).packetCodec(PacketCodecs.STRING).build();

	public static void init() {
		Registry.register(Registries.DATA_COMPONENT_TYPE, Anthropophagy.id("from_player"), FROM_PLAYER);
		Registry.register(Registries.DATA_COMPONENT_TYPE, Anthropophagy.id("owner_name"), OWNER_NAME);
	}
}
