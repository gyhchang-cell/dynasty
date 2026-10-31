package floffy.toffys_hooks;

import floffy.toffys_hooks.register.*;
import floffy.toffys_hooks.register.ModLootTableModifiers;
import net.fabricmc.api.ModInitializer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ToffysHooks implements ModInitializer {
	public static final String MOD_ID = "toffys_hooks";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
	@Override
	public void onInitialize() {
		ModEntities.register();
		ModItems.register();
		ModLootTableModifiers.modifyLootTables();
		ModSoundEvents.register();
	}
}