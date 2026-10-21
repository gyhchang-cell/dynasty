package com.dynasty.client;

import com.google.gson.JsonObject;
import com.mojang.blaze3d.platform.NativeImage;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.model.*;
import net.minecraft.client.renderer.texture.SpriteContents;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.metadata.animation.AnimationMetadataSection;
import net.minecraft.client.resources.metadata.animation.FrameSize;
import net.minecraft.client.resources.model.*;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.client.model.geometry.IGeometryBakingContext;
import net.minecraftforge.client.model.geometry.IUnbakedGeometry;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Original PNGs use their own texture, avoiding the shared atlas's 16384px limit. */
@Mod.EventBusSubscriber(modid = "dynasty", bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class OriginalItemGeometry implements IUnbakedGeometry<OriginalItemGeometry> {
    private final ResourceLocation texture;
    private final int tintIndex;

    public OriginalItemGeometry(ResourceLocation texture) { this(texture, -1); }
    public OriginalItemGeometry(ResourceLocation texture, int tintIndex) {
        this.texture = texture;
        this.tintIndex = tintIndex;
    }

    @SubscribeEvent
    public static void register(ModelEvent.RegisterGeometryLoaders event) {
        event.register("original_item", (net.minecraftforge.client.model.geometry.IGeometryLoader<OriginalItemGeometry>) (JsonObject json, com.google.gson.JsonDeserializationContext context) ->
                new OriginalItemGeometry(new ResourceLocation(json.get("original_texture").getAsString()),
                        json.has("tint_index") ? json.get("tint_index").getAsInt() : -1));
    }

    @Override
    public BakedModel bake(IGeometryBakingContext context, ModelBaker baker,
            Function<Material, TextureAtlasSprite> sprites, ModelState state,
            ItemOverrides overrides, ResourceLocation location) {
        TextureAtlasSprite particle = sprites.apply(new Material(
                net.minecraft.world.inventory.InventoryMenu.BLOCK_ATLAS,
                new ResourceLocation("minecraft", "item/iron_nugget")));
        try (InputStream input = Minecraft.getInstance().getResourceManager().open(texture)) {
            return new OriginalModel(bakeQuads(input, texture, particle, state, location, tintIndex),
                    particle, context.getTransforms(), overrides, texture);
        } catch (IOException e) {
            throw new IllegalStateException("Cannot load original item texture " + texture, e);
        }
    }

    /** Vanilla extrusion and UV baking, with no resampling or texture retained in the atlas. */
    public static List<BakedQuad> bakeQuads(InputStream input, ResourceLocation texture,
            TextureAtlasSprite particle, ModelState state, ResourceLocation location) throws IOException {
        return bakeQuads(input, texture, particle, state, location, -1);
    }

    public static List<BakedQuad> bakeQuads(InputStream input, ResourceLocation texture,
            TextureAtlasSprite particle, ModelState state, ResourceLocation location, int tintIndex) throws IOException {
        NativeImage image = NativeImage.read(input);
        try (SpriteContents contents = new SpriteContents(texture,
                new FrameSize(image.getWidth(), image.getHeight()), image, AnimationMetadataSection.EMPTY, null)) {
            TextureAtlasSprite direct = new DirectSprite(texture, contents);
            FaceBakery bakery = new FaceBakery();
            List<BakedQuad> quads = new ArrayList<>();
            for (BlockElement element : new ItemModelGenerator().processFrames(tintIndex, "layer0", contents)) {
                for (var face : element.faces.entrySet()) {
                    BakedQuad quad = bakery.bakeQuad(element.from, element.to, face.getValue(), direct,
                            face.getKey(), state, element.rotation, element.shade, location);
                    // The UVs bind the original PNG; only the particle sprite belongs to the atlas.
                    quads.add(new BakedQuad(quad.getVertices(), quad.getTintIndex(), quad.getDirection(),
                            particle, quad.isShade()));
                }
            }
            return List.copyOf(quads);
        }
    }

    private static final class DirectSprite extends TextureAtlasSprite {
        DirectSprite(ResourceLocation texture, SpriteContents contents) {
            super(texture, contents, contents.width(), contents.height(), 0, 0);
        }
        @Override public float uvShrinkRatio() { return 0; }
    }

    private record OriginalModel(List<BakedQuad> quads, TextureAtlasSprite particle,
            ItemTransforms transforms, ItemOverrides overrides, ResourceLocation texture) implements BakedModel {
        @Override public List<BakedQuad> getQuads(BlockState state, Direction side, RandomSource random) {
            return side == null ? quads : List.of();
        }
        @Override public boolean useAmbientOcclusion() { return false; }
        @Override public boolean isGui3d() { return false; }
        @Override public boolean usesBlockLight() { return false; }
        @Override public boolean isCustomRenderer() { return false; }
        @Override public TextureAtlasSprite getParticleIcon() { return particle; }
        @Override public ItemTransforms getTransforms() { return transforms; }
        @Override public ItemOverrides getOverrides() { return overrides; }
        @Override public List<RenderType> getRenderTypes(ItemStack stack, boolean fabulous) {
            return List.of(RenderType.entityCutoutNoCull(texture));
        }
    }
}
