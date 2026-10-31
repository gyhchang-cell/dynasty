package artifacts.client.mimic;

import artifacts.Artifacts;
import artifacts.entity.MimicEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;

public class MimicRenderer extends MobRenderer<MimicEntity, MimicRenderState, MimicModel> {

    private static final Identifier TEXTURE = Artifacts.id("textures/entity/mimic.png");

    private final MimicChestMaterials chestMaterials;

    public MimicRenderer(EntityRendererProvider.Context context) {
        super(context, new MimicModel(context.bakeLayer(MimicModel.LAYER_LOCATION)), 0.45F);
        this.chestMaterials = new MimicChestMaterials();
        addLayer(new MimicChestLayer(this, context.getModelSet(), context.getSprites()));
    }

    @Override
    public MimicRenderState createRenderState() {
        return new MimicRenderState();
    }

    @Override
    public void extractRenderState(MimicEntity mimic, MimicRenderState renderState, float partialTicks) {
        super.extractRenderState(mimic, renderState, partialTicks);
        renderState.ticksInAir = mimic.ticksInAir > 0 ? mimic.ticksInAir - 1 + partialTicks : 0;
        renderState.chestMaterial = chestMaterials.getChestSprite(mimic);
    }

    @Override
    public Identifier getTextureLocation(MimicRenderState entity) {
        return TEXTURE;
    }
}
