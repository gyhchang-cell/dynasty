package artifacts.fabric;

import artifacts.Artifacts;
import artifacts.ArtifactsClient;
import artifacts.client.item.ArtifactRenderers;
import artifacts.client.mimic.MimicRenderer;
import artifacts.event.ArtifactHooks;
import artifacts.fabric.network.FabricClientNetworkHandler;
import artifacts.registry.ModEntityTypes;
import artifacts.registry.ModKeyMappings;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientEntityEvents;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;
import net.fabricmc.fabric.api.resource.IdentifiableResourceReloadListener;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.minecraft.client.renderer.item.properties.conditional.ConditionalItemModelProperties;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;

public class ArtifactsFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ArtifactsClient.setup();
        ArtifactsClient.onClientStarted();
        FabricClientNetworkHandler.register();

        ClientPlayConnectionEvents.DISCONNECT.register((_, _) -> Artifacts.onClientDisconnect());

        ArtifactsClient.registerLayerDefinitions((location, layerDefinition) -> ModelLayerRegistry.registerModelLayer(location, layerDefinition::get));
        ClientTickEvents.END_CLIENT_TICK.register(ArtifactsClient::onClientTick);
        EntityRendererRegistry.register(ModEntityTypes.MIMIC.get(), MimicRenderer::new);
        ModKeyMappings.register(KeyMappingHelper::registerKeyMapping);

        ClientEntityEvents.ENTITY_LOAD.register((entity, _) -> ArtifactHooks.onEntityAdded(entity));
        ResourceManagerHelper.get(PackType.CLIENT_RESOURCES).registerReloadListener(new IdentifiableArtifactRendererReloadListener());

        ArtifactsClient.registerConditionalItemModelProperties(ConditionalItemModelProperties.ID_MAPPER::put);
    }

    private static class IdentifiableArtifactRendererReloadListener implements ResourceManagerReloadListener, IdentifiableResourceReloadListener {

        private static final Identifier ID = Artifacts.id("renderers");

        @Override
        public void onResourceManagerReload(ResourceManager resourceManager) {
            ArtifactRenderers.register();
        }

        @Override
        public Identifier getFabricId() {
            return ID;
        }
    }
}
