package artifacts.mixin.accessors.client;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.List;

@Mixin(LivingEntityRenderer.class)
public interface LivingEntityRendererAccessor<S extends EntityRenderState, M extends EntityModel<S>> extends RenderLayerParent<S, M> {

    @Accessor
    List<RenderLayer<S, M>> getLayers();
}
