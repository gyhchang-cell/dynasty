/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.reloadlisteners;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonReader;
import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.util.FleshDropEntry;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.entity.EntityType;
import net.minecraft.item.Item;
import net.minecraft.registry.Registries;
import net.minecraft.resource.Resource;
import net.minecraft.resource.ResourceManager;
import net.minecraft.util.Identifier;
import net.minecraft.util.JsonHelper;

import java.io.InputStream;
import java.io.InputStreamReader;

public class FleshDropsReloadListener implements SimpleSynchronousResourceReloadListener {
	private static final Identifier ID = Anthropophagy.id("flesh_drops");

	@Override
	public Identifier getFabricId() {
		return ID;
	}

	@Override
	public void reload(ResourceManager manager) {
		FleshDropEntry.DROP_MAP.clear();
		manager.findAllResources("flesh_drops", path -> path.getNamespace().equals(Anthropophagy.MOD_ID) && path.getPath().endsWith(".json")).forEach((identifier, resources) -> {
			for (Resource resource : resources) {
				try (InputStream stream = resource.getInputStream()) {
					JsonObject object = JsonParser.parseReader(new JsonReader(new InputStreamReader(stream))).getAsJsonObject();
					Identifier entityId = new Identifier(identifier.getPath().substring(identifier.getPath().indexOf("/") + 1, identifier.getPath().length() - 5).replace("/", ":"));
					EntityType<?> entityType = Registries.ENTITY_TYPE.get(entityId);
					if (entityType == Registries.ENTITY_TYPE.get(Registries.ENTITY_TYPE.getDefaultId()) && !entityId.equals(Registries.ENTITY_TYPE.getDefaultId())) {
						continue;
					}
					Identifier rawDropId = new Identifier(JsonHelper.getString(object, "raw_drop"));
					Item rawDrop = Registries.ITEM.get(rawDropId);
					if (rawDrop == Registries.ITEM.get(Registries.ITEM.getDefaultId()) && !rawDropId.equals(Registries.ITEM.getDefaultId())) {
						Anthropophagy.LOGGER.error("Unknown item '{}' in file '{}'", rawDropId, identifier);
						continue;
					}
					Identifier cookedDropId = new Identifier(JsonHelper.getString(object, "raw_drop"));
					Item cookedDrop = Registries.ITEM.get(cookedDropId);
					if (cookedDrop == Registries.ITEM.get(Registries.ITEM.getDefaultId()) && !cookedDropId.equals(Registries.ITEM.getDefaultId())) {
						Anthropophagy.LOGGER.error("Unknown item '{}' in file '{}'", cookedDropId, identifier);
						continue;
					}
					FleshDropEntry.DROP_MAP.put(entityType, new FleshDropEntry(rawDrop, cookedDrop));
				} catch (Exception ignored) {
				}
			}
		});
	}
}