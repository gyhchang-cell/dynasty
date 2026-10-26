package de.njlent.damagenumbers;

import com.mojang.logging.LogUtils;
import de.njlent.damagenumbers.modules.combat.DamageNumbersModule;
import meteordevelopment.meteorclient.addons.GithubRepo;
import meteordevelopment.meteorclient.addons.MeteorAddon;
import meteordevelopment.meteorclient.systems.modules.Modules;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderEvents;
import org.slf4j.Logger;

public class DamageNumbersMeteorAddon extends MeteorAddon {
    public static final Logger LOG = LogUtils.getLogger();

    @Override
    public void onInitialize() {
        LOG.info("Initializing Damage Numbers Meteor addon");

        DamageNumbersModule module = new DamageNumbersModule();
        Modules.get().add(module);

        LevelRenderEvents.COLLECT_SUBMITS.register(DamageNumbersModule::renderParticles);
    }

    @Override
    public String getPackage() {
        return "de.njlent.damagenumbers";
    }

    @Override
    public GithubRepo getRepo() {
        return new GithubRepo("njlent", "Damagenumbers-Meteor-client-addon");
    }
}
