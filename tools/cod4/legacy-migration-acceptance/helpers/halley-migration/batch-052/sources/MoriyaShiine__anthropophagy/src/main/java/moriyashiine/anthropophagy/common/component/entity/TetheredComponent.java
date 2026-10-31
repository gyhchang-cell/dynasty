/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.component.entity;

import net.minecraft.nbt.NbtCompound;
import net.minecraft.registry.RegistryWrapper;
import org.ladysnake.cca.api.v3.component.sync.AutoSyncedComponent;

public class TetheredComponent implements AutoSyncedComponent {
	private boolean tethered = false;

	@Override
	public void readFromNbt(NbtCompound tag, RegistryWrapper.WrapperLookup registryLookup) {
		tethered = tag.getBoolean("Tethered");
	}

	@Override
	public void writeToNbt(NbtCompound tag, RegistryWrapper.WrapperLookup registryLookup) {
		tag.putBoolean("Tethered", tethered);
	}

	public boolean isTethered() {
		return tethered;
	}

	public void setTethered(boolean tethered) {
		this.tethered = tethered;
	}
}
