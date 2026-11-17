package net.tslat.aoa3.integration;

import it.unimi.dsi.fastutil.objects.Object2ObjectOpenHashMap;
import net.minecraft.Util;
import net.neoforged.fml.ModList;
import net.tslat.aoa3.advent.Logging;
import net.tslat.aoa3.integration.patchouli.PatchouliIntegration;
import net.tslat.aoa3.integration.tes.TESIntegration;

import java.util.Map;
import java.util.function.BooleanSupplier;
import java.util.function.Function;

public class IntegrationManager {
	public static final String JEI = "jei";
	public static final String PATCHOULI = "patchouli";
	public static final String TES = "tslatentitystatus";

	private static final Map<String, CallableIntegration> INTEGRATIONS = Util.make(new Object2ObjectOpenHashMap<>(), map -> {
		map.put(JEI, new CallableIntegration(JEI, () -> {}, () -> {}, () -> {}));
		map.put(PATCHOULI, new CallableIntegration(PATCHOULI, PatchouliIntegration::preInit, () -> {}, () -> {}));
		map.put(TES, new CallableIntegration(TES, () -> {}, () -> {}, TESIntegration::clientInit));
	});

	public static boolean isModPresent(String modId) {
		return ModList.get().isLoaded(modId);
	}

	public static boolean isJEIActive() {
		return INTEGRATIONS.get(JEI).enabled();
	}

	public static boolean isPatchouliActive() {
		return INTEGRATIONS.get(PATCHOULI).enabled();
	}

	public static boolean isTESActive() {
		return INTEGRATIONS.get(TES).enabled();
	}

	public static void init() {
		Logging.logStatusMessage("Checking for third-party integrations");

		callSetupStage(integration -> {
			Logging.logStatusMessage("Found '" + integration.modId() + "', integrating");

			return integration.init();
		});
	}

	public static void lateInit() {
		callSetupStage(CallableIntegration::postInit);
	}

	public static void clientInit() {
		callSetupStage(CallableIntegration::clientInit);
	}

	private static void callSetupStage(Function<CallableIntegration, Runnable> stageTask) {
		for (Map.Entry<String, CallableIntegration> entry : INTEGRATIONS.entrySet()) {
			if (entry.getValue().enabled()) {
				Logging.logStatusMessage("Found '" + entry.getKey() + "', integrating");

				stageTask.apply(entry.getValue()).run();
			}
		}
	}

	public record CallableIntegration(String modId, BooleanSupplier isActive, Runnable init, Runnable postInit, Runnable clientInit) {
		public CallableIntegration(String modId, Runnable init, Runnable postInit, Runnable clientInit) {
			this(modId, () -> isModPresent(modId), init, postInit, clientInit);
		}

		public boolean enabled() {
			return isActive.getAsBoolean();
		}
	}
}
